-- Top level: tile controller + input stager + PE grid + result storage + serial readout.
--
-- Operand interface: the controller publishes the current boundary step
-- (step_t, tile_row, tile_col) and which A/B boundary words are needed
-- (a_need/b_need). The environment drives a_data/b_data for needed words; the
-- stager accepts at most `budget` words per clock.
--
-- Per tile: T = N + 2P - 2 boundary steps (fill/steady/drain), then 1 CAPTURE cycle
-- (copy accumulators to result storage and clear the grid). After the last tile the
-- full NxN result is read out serially, one word per clock.
--
-- Compute latency = cycles in RUN + CAPTURE (first RUN cycle through last CAPTURE).
-- Total latency   = compute latency + N*N readout cycles.
--
-- INSTR=false removes the counters/debug outputs (use for Vivado synthesis).
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.sys_pkg.all;

entity systolic_top is
  generic (
    P     : positive := 2;
    N     : positive := 8;
    INSTR : boolean  := true
  );
  port (
    clk, rst, start : in  std_logic;
    budget          : in  unsigned(4 downto 0);   -- combined A/B words per clock (>= 1)
    -- operand interface
    step_t     : out unsigned(5 downto 0);
    tile_row   : out unsigned(3 downto 0);
    tile_col   : out unsigned(3 downto 0);
    a_need     : out std_logic_vector(0 to P-1);
    b_need     : out std_logic_vector(0 to P-1);
    stage_got  : out std_logic_vector(0 to 2*P-1);
    a_data     : in  word_array_t(0 to P-1);
    b_data     : in  word_array_t(0 to P-1);
    -- serial readout
    out_valid  : out std_logic;
    out_idx    : out unsigned(8 downto 0);
    out_data   : out acc_t;
    done       : out std_logic;
    -- instrumentation
    cnt_compute, cnt_total, cnt_stall, cnt_adv, cnt_cap : out unsigned(31 downto 0);
    mac_fire   : out std_logic_vector(0 to P*P-1)
  );
end entity systolic_top;

architecture rtl of systolic_top is
  -- The PxP grid can only compute a PxP piece (tile) of the NxN result at a time,
  -- so the full multiply is done as NT x NT tiles, one after another.
  constant NT      : positive := N / P;          -- tiles per row/column of the result
  constant T_STEPS : positive := N + 2*P - 2;    -- boundary steps per tile (N to stream the data + 2P-2 to fill/drain the grid)

  -- Controller state machine:
  --   IDLE -> RUN (stream one tile through the grid) -> CAPTURE (save tile, clear grid)
  --        -> back to RUN for the next tile ... -> READOUT (send results out) -> DONE
  type state_t is (S_IDLE, S_RUN, S_CAPTURE, S_READOUT, S_DONE);
  signal state : state_t := S_IDLE;

  signal t      : unsigned(5 downto 0) := (others => '0');  -- current boundary step within the tile
  signal tr, tc : unsigned(3 downto 0) := (others => '0');  -- current tile row / tile column
  signal rd_idx : unsigned(8 downto 0) := (others => '0');  -- which result word is being read out

  -- Storage for the whole NxN result matrix (becomes registers or block RAM).
  type res_t is array (0 to N*N-1) of acc_t;
  signal result : res_t;

  signal need_a_i, need_b_i : std_logic_vector(0 to P-1);  -- internal copies of a_need / b_need
  signal run, clr           : std_logic;                   -- state decoded into single-bit controls
  signal complete, stall    : std_logic;                   -- from the stager: step ready / waiting
  signal got                : std_logic_vector(0 to 2*P-1);
  signal a_grid, b_grid     : word_array_t(0 to P-1);      -- operands going from stager into the grid
  signal acc                : acc_2d_t(0 to P-1, 0 to P-1);  -- accumulators coming out of the grid
  signal fire               : bit_2d_t(0 to P-1, 0 to P-1);  -- MAC flags coming out of the grid

  -- Performance counters (only used when INSTR = true)
  signal c_compute, c_total, c_stall, c_adv, c_cap : unsigned(31 downto 0) := (others => '0');
begin
  -- Checked at elaboration (before simulation/synthesis): reject bad parameter choices.
  assert N mod P = 0 report "N must be divisible by P" severity failure;
  assert N <= 16 report "N > 16 would overflow the 36-bit accumulator" severity failure;

  -- Decode the state machine into control signals.
  run <= '1' when state = S_RUN     else '0';  -- streaming operands
  clr <= '1' when state = S_CAPTURE else '0';  -- clear the grid after saving the tile

  -- Boundary word i of A (row i) is needed on step t when 0 <= t-i < N; same for B.
  gen_need : for i in 0 to P-1 generate
    need_a_i(i) <= '1' when run = '1' and to_integer(t) >= i and to_integer(t) < N + i else '0';
    need_b_i(i) <= '1' when run = '1' and to_integer(t) >= i and to_integer(t) < N + i else '0';
  end generate;

  -- Input stager: accepts operands (limited by budget) and says when the grid may advance.
  u_stager : entity work.input_stager
    generic map (P => P)
    port map (
      clk => clk, rst => rst, run => run, budget => budget,
      need_a => need_a_i, need_b => need_b_i,
      a_data => a_data, b_data => b_data,
      a_out => a_grid, b_out => b_grid,
      complete => complete, stall => stall, got => got);

  -- The PE grid. It advances only when the stager says the step is complete (en => complete).
  -- The "need" bits double as the valid bits: data is real exactly when it was needed.
  u_grid : entity work.systolic_array
    generic map (P => P)
    port map (
      clk => clk, rst => rst, clr => clr, en => complete,
      a_in => a_grid, a_v => need_a_i,
      b_in => b_grid, b_v => need_b_i,
      acc => acc, fire => fire);

  -- Tile controller / result capture / readout
  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        state  <= S_IDLE;
        t      <= (others => '0');
        tr     <= (others => '0');
        tc     <= (others => '0');
        rd_idx <= (others => '0');
      else
        case state is
          -- Wait for start; then begin at tile (0,0), step 0.
          when S_IDLE | S_DONE =>
            if start = '1' then
              state  <= S_RUN;
              t      <= (others => '0');
              tr     <= (others => '0');
              tc     <= (others => '0');
              rd_idx <= (others => '0');
            end if;

          -- Step through the tile. Only move to the next step when the stager is complete
          -- (otherwise stall). After the last step, go save the tile.
          when S_RUN =>
            if complete = '1' then
              if to_integer(t) = T_STEPS - 1 then
                state <= S_CAPTURE;
              else
                t <= t + 1;
              end if;
            end if;

          -- Copy this tile's accumulators into the right spot in the result matrix
          -- (clr is high this cycle, so the grid zeroes itself for the next tile).
          -- Then move to the next tile (left to right, then down), or readout if that was the last.
          when S_CAPTURE =>
            for r in 0 to P-1 loop
              for c in 0 to P-1 loop
                result((to_integer(tr) * P + r) * N + to_integer(tc) * P + c) <= acc(r, c);
              end loop;
            end loop;
            t <= (others => '0');
            if to_integer(tc) = NT - 1 then
              tc <= (others => '0');
              if to_integer(tr) = NT - 1 then
                tr    <= (others => '0');
                state <= S_READOUT;
              else
                tr    <= tr + 1;
                state <= S_RUN;
              end if;
            else
              tc    <= tc + 1;
              state <= S_RUN;
            end if;

          -- Send out one result word per clock, in order, until all N*N are sent.
          when S_READOUT =>
            if to_integer(rd_idx) = N*N - 1 then
              state <= S_DONE;
            else
              rd_idx <= rd_idx + 1;
            end if;
        end case;
      end if;
    end if;
  end process;

  -- Output pins driven from the state machine / result storage.
  out_valid <= '1' when state = S_READOUT else '0';
  out_idx   <= rd_idx;
  out_data  <= result(to_integer(rd_idx)) when state = S_READOUT else (others => '0');
  done      <= '1' when state = S_DONE else '0';

  step_t   <= t;
  tile_row <= tr;
  tile_col <= tc;
  a_need   <= need_a_i;
  b_need   <= need_b_i;

  -- Instrumentation (generate-if: this hardware only exists when INSTR = true).
  gen_instr : if INSTR generate
    stage_got <= got;
    gen_fire_r : for r in 0 to P-1 generate
      gen_fire_c : for c in 0 to P-1 generate
        mac_fire(r*P + c) <= fire(r, c);
      end generate;
    end generate;

    process (clk)
    begin
      if rising_edge(clk) then
        if rst = '1' or ((state = S_IDLE or state = S_DONE) and start = '1') then
          c_compute <= (others => '0');
          c_total   <= (others => '0');
          c_stall   <= (others => '0');
          c_adv     <= (others => '0');
          c_cap     <= (others => '0');
        else
          -- c_compute: cycles in RUN + CAPTURE.  c_total: those plus READOUT.
          -- c_adv: cycles the grid advanced.  c_stall: cycles waiting on the stager.  c_cap: CAPTURE cycles.
          if state = S_RUN or state = S_CAPTURE then c_compute <= c_compute + 1; end if;
          if state = S_RUN or state = S_CAPTURE or state = S_READOUT then
            c_total <= c_total + 1;
          end if;
          if state = S_RUN and complete = '1' then c_adv <= c_adv + 1; end if;
          if stall = '1' then c_stall <= c_stall + 1; end if;
          if state = S_CAPTURE then c_cap <= c_cap + 1; end if;
        end if;
      end if;
    end process;
  end generate;

  -- With INSTR = false, tie debug outputs to 0 so synthesis removes the counters.
  gen_no_instr : if not INSTR generate
    stage_got <= (others => '0');
    mac_fire  <= (others => '0');
  end generate;

  cnt_compute <= c_compute;
  cnt_total   <= c_total;
  cnt_stall   <= c_stall;
  cnt_adv     <= c_adv;
  cnt_cap     <= c_cap;
end architecture rtl;
