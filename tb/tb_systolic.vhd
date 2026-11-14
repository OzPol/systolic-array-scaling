-- Self-checking testbench. One run = one (P, N, B) configuration over every case in VEC_FILE.
-- Checks per case:
--   * every serial output word equals the independent software reference (full 36 bits)
--   * words arrive in order, exactly N*N of them
--   * useful MAC events (observed on mac_fire) == N^3
--   * DUT cycle counters match closed-form expectations derived from P, N, B
-- Operands not yet accepted by the stager are driven correctly; words already accepted
-- (stage_got) and words not needed are driven with garbage, so lost/duplicated operands
-- or missing valid gating produce wrong results.
library ieee, std;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_textio.all;
use std.textio.all;
use std.env.all;
use work.sys_pkg.all;

entity tb_systolic is
  generic (
    P           : positive := 2;
    N           : positive := 8;
    B           : positive := 4;
    VEC_FILE    : string   := "tb/vectors/vec_n08.txt";
    RESULT_FILE : string   := "results/raw/sim_results.csv"
  );
end entity tb_systolic;

architecture sim of tb_systolic is
  constant T_STEPS : integer := N + 2*P - 2;
  constant NT      : integer := N / P;

  type int_arr_t is array (0 to N*N-1) of integer;
  type acc_arr_t is array (0 to N*N-1) of acc_t;

  signal clk   : std_logic := '0';
  signal rst   : std_logic := '1';
  signal start : std_logic := '0';

  signal budget    : unsigned(4 downto 0) := to_unsigned(B, 5);
  signal step_t    : unsigned(5 downto 0);
  signal tile_row, tile_col : unsigned(3 downto 0);
  signal a_need, b_need     : std_logic_vector(0 to P-1);
  signal stage_got          : std_logic_vector(0 to 2*P-1);
  signal a_data, b_data     : word_array_t(0 to P-1) := (others => (others => '0'));
  signal out_valid, done    : std_logic;
  signal out_idx            : unsigned(8 downto 0);
  signal out_data           : acc_t;
  signal cnt_compute, cnt_total, cnt_stall, cnt_adv, cnt_cap : unsigned(31 downto 0);
  signal mac_fire           : std_logic_vector(0 to P*P-1);

  signal mat_a, mat_b : int_arr_t := (others => 0);
  signal mat_c        : acc_arr_t := (others => (others => '0'));

  -- monitor results
  signal macs, out_words, out_errs, idx_errs : integer := 0;

  -- Functions below compute the EXPECTED cycle counts from P, N, B, so the testbench
  -- can check the DUT's counters against an independent formula.

  -- Words in boundary step t (A words + B words)
  function step_words(t : integer) return integer is
    variable cnt : integer := 0;
  begin
    for r in 0 to P-1 loop
      if t >= r and t < N + r then cnt := cnt + 1; end if;
    end loop;
    return 2 * cnt;
  end function;

  -- Expected budget-stall cycles for the whole product
  function exp_stalls return integer is
    variable s : integer := 0;
    variable w : integer;
  begin
    for t in 0 to T_STEPS - 1 loop
      w := step_words(t);
      if w > B then s := s + (w + B - 1) / B - 1; end if;
    end loop;
    return s * NT * NT;
  end function;

  constant EXP_STALL   : integer := exp_stalls;                    -- cycles lost waiting on the input budget
  constant EXP_ADV     : integer := NT * NT * T_STEPS;             -- every tile takes T_STEPS advancing cycles
  constant EXP_CAP     : integer := NT * NT;                       -- one capture cycle per tile
  constant EXP_COMPUTE : integer := EXP_ADV + EXP_STALL + EXP_CAP;
  constant EXP_TOTAL   : integer := EXP_COMPUTE + N * N;           -- plus serial readout of N*N words
begin
  clk <= not clk after 5 ns;  -- 10 ns period (simulation-only: generates the clock)

  -- Device under test: the whole design.
  u_dut : entity work.systolic_top
    generic map (P => P, N => N, INSTR => true)
    port map (
      clk => clk, rst => rst, start => start, budget => budget,
      step_t => step_t, tile_row => tile_row, tile_col => tile_col,
      a_need => a_need, b_need => b_need, stage_got => stage_got,
      a_data => a_data, b_data => b_data,
      out_valid => out_valid, out_idx => out_idx, out_data => out_data, done => done,
      cnt_compute => cnt_compute, cnt_total => cnt_total, cnt_stall => cnt_stall,
      cnt_adv => cnt_adv, cnt_cap => cnt_cap, mac_fire => mac_fire);

  -- Operand driver (combinational on DUT step/tile outputs)
  drive : process (all)
    variable k, addr : integer;
  begin
    for r in 0 to P-1 loop
      a_data(r) <= to_signed(16#5A5A#, DATA_W);   -- garbage by default
      b_data(r) <= to_signed(-21846, DATA_W);
      -- A[tile_row*P + r][t - r]
      k := to_integer(step_t) - r;
      if a_need(r) = '1' and stage_got(r) = '0' and k >= 0 and k < N then
        addr := (to_integer(tile_row) * P + r) * N + k;
        a_data(r) <= to_signed(mat_a(addr), DATA_W);
      end if;
      -- B[t - c][tile_col*P + c]
      k := to_integer(step_t) - r;
      if b_need(r) = '1' and stage_got(P + r) = '0' and k >= 0 and k < N then
        addr := k * N + to_integer(tile_col) * P + r;
        b_data(r) <= to_signed(mat_b(addr), DATA_W);
      end if;
    end loop;
  end process;

  -- Event monitor: independent MAC count and serial-output checking
  monitor : process (clk)
    variable inc : integer;
  begin
    if rising_edge(clk) then
      if start = '1' then
        macs <= 0; out_words <= 0; out_errs <= 0; idx_errs <= 0;
      else
        inc := 0;
        for i in 0 to P*P-1 loop
          if mac_fire(i) = '1' then inc := inc + 1; end if;
        end loop;
        macs <= macs + inc;
        if out_valid = '1' then
          if to_integer(out_idx) /= out_words then idx_errs <= idx_errs + 1; end if;
          if out_data /= mat_c(to_integer(out_idx)) then out_errs <= out_errs + 1; end if;
          out_words <= out_words + 1;
        end if;
      end if;
    end if;
  end process;

  -- Main sequencer: reads test vectors from file, runs each case, checks results, logs a CSV row.
  -- Unlike the RTL, this process runs top-to-bottom like software ("wait" statements are
  -- simulation-only and can't be synthesized).
  main : process
    file     f  : text;
    file     rf : text;
    variable l  : line;
    variable ncases : integer;
    variable w16 : std_logic_vector(15 downto 0);
    variable w36 : std_logic_vector(35 downto 0);
    variable va, vb : int_arr_t;
    variable vc : acc_arr_t;
    variable case_errs, total_errs : integer := 0;
    variable ok : boolean;

    procedure rd_vec(file ff : text; variable v : out std_logic_vector) is
      variable ll : line;
    begin
      readline(ff, ll);
      hread(ll, v);
    end procedure;

    procedure check(cond : boolean; msg : string) is
    begin
      if not cond then
        report msg severity error;
        case_errs := case_errs + 1;
      end if;
    end procedure;
  begin
    -- First line of the vector file = number of test cases.
    file_open(f, VEC_FILE, read_mode);
    readline(f, l);
    read(l, ncases);

    -- Hold reset for 4 clocks to put the DUT in a known state.
    rst <= '1';
    for i in 1 to 4 loop wait until rising_edge(clk); end loop;
    rst <= '0';
    wait until rising_edge(clk);

    for cs in 0 to ncases - 1 loop
      -- Load matrices A, B and the expected result C (from the software reference) for this case.
      for i in 0 to N*N-1 loop rd_vec(f, w16); va(i) := to_integer(signed(w16)); end loop;
      for i in 0 to N*N-1 loop rd_vec(f, w16); vb(i) := to_integer(signed(w16)); end loop;
      for i in 0 to N*N-1 loop rd_vec(f, w36); vc(i) := signed(w36); end loop;
      mat_a <= va; mat_b <= vb; mat_c <= vc;
      wait until rising_edge(clk);
      wait until rising_edge(clk);

      -- Pulse start for one clock, then wait for the DUT to finish (1 ms timeout).
      start <= '1';
      wait until rising_edge(clk);
      start <= '0';
      wait until done = '1' for 1 ms;
      wait until rising_edge(clk);
      wait until rising_edge(clk);

      -- Check everything for this case.
      case_errs := 0;
      check(done = '1', "case " & integer'image(cs) & ": timeout waiting for done");
      check(out_words = N*N, "case " & integer'image(cs) & ": wrong output word count " & integer'image(out_words));
      check(out_errs = 0,    "case " & integer'image(cs) & ": output mismatches = " & integer'image(out_errs));
      check(idx_errs = 0,    "case " & integer'image(cs) & ": output order errors = " & integer'image(idx_errs));
      check(macs = N*N*N,    "case " & integer'image(cs) & ": useful MACs " & integer'image(macs) & " /= N^3");
      check(to_integer(cnt_stall)   = EXP_STALL,   "case " & integer'image(cs) & ": stall cycles " & integer'image(to_integer(cnt_stall)) & " expected " & integer'image(EXP_STALL));
      check(to_integer(cnt_adv)     = EXP_ADV,     "case " & integer'image(cs) & ": advance cycles " & integer'image(to_integer(cnt_adv)) & " expected " & integer'image(EXP_ADV));
      check(to_integer(cnt_cap)     = EXP_CAP,     "case " & integer'image(cs) & ": capture cycles " & integer'image(to_integer(cnt_cap)) & " expected " & integer'image(EXP_CAP));
      check(to_integer(cnt_compute) = EXP_COMPUTE, "case " & integer'image(cs) & ": compute cycles " & integer'image(to_integer(cnt_compute)) & " expected " & integer'image(EXP_COMPUTE));
      check(to_integer(cnt_total)   = EXP_TOTAL,   "case " & integer'image(cs) & ": total cycles " & integer'image(to_integer(cnt_total)) & " expected " & integer'image(EXP_TOTAL));
      total_errs := total_errs + case_errs;

      -- CSV: P,N,B,case,pass,compute,total,stall,adv,cap,macs
      file_open(rf, RESULT_FILE, append_mode);
      write(l, integer'image(P) & "," & integer'image(N) & "," & integer'image(B) & "," &
               integer'image(cs) & "," & integer'image(boolean'pos(case_errs = 0)) & "," &
               integer'image(to_integer(cnt_compute)) & "," & integer'image(to_integer(cnt_total)) & "," &
               integer'image(to_integer(cnt_stall)) & "," & integer'image(to_integer(cnt_adv)) & "," &
               integer'image(to_integer(cnt_cap)) & "," & integer'image(macs));
      writeline(rf, l);
      file_close(rf);
    end loop;

    file_close(f);
    if total_errs = 0 then
      report "TB PASS P=" & integer'image(P) & " N=" & integer'image(N) & " B=" & integer'image(B) &
             " cases=" & integer'image(ncases) & " compute=" & integer'image(EXP_COMPUTE) severity note;
    else
      report "TB FAIL P=" & integer'image(P) & " N=" & integer'image(N) & " B=" & integer'image(B) &
             " errors=" & integer'image(total_errs) severity error;
    end if;
    finish;
  end process;
end architecture sim;
