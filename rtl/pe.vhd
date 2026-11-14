-- Processing element: forwards A to the right and B downward (registered), and
-- accumulates A*B into a local output-stationary accumulator when both operands
-- are valid.
--   clr : synchronous clear of accumulator and forwarded valids (tile boundary); overrides en
--   en  : advance enable; when '0' every register holds (grid stall)
--   fire: combinational, high when this PE performs a useful MAC this cycle
--
-- "Output-stationary" = the result (acc) stays inside this PE while the inputs
-- A and B stream through it. Each PE ends up holding one element of the output matrix C.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.sys_pkg.all;

-- The entity is the PE's "pin list": what goes in and out, nothing about the insides.
entity pe is
  port (
    clk, rst, clr, en : in  std_logic;  -- clock, reset, clear (new tile), enable (advance)
    a_in    : in  word_t;               -- A value arriving from the left neighbor (or the grid edge)
    a_v_in  : in  std_logic;            -- '1' if a_in holds real data this cycle
    b_in    : in  word_t;               -- B value arriving from the top neighbor (or the grid edge)
    b_v_in  : in  std_logic;            -- '1' if b_in holds real data this cycle
    a_out   : out word_t;               -- A value passed on to the right neighbor (1 cycle later)
    a_v_out : out std_logic;            -- valid bit that goes with a_out
    b_out   : out word_t;               -- B value passed on to the bottom neighbor (1 cycle later)
    b_v_out : out std_logic;            -- valid bit that goes with b_out
    acc     : out acc_t;                -- running sum = this PE's output element
    fire    : out std_logic             -- '1' when a multiply-accumulate happens this cycle (for counting MACs)
  );
end entity pe;

-- The architecture is what's inside the PE.
architecture rtl of pe is
  -- "_q" signals are registers (flip-flops): they only change on a clock edge.
  signal a_q, b_q       : word_t := (others => '0');      -- registered copies of A and B to forward
  signal a_v_q, b_v_q   : std_logic := '0';               -- registered valid bits to forward
  signal acc_q          : acc_t := (others => '0');       -- the accumulator
begin
  -- Plain wires from the registers to the output pins (no logic, just connections).
  a_out   <= a_q;
  b_out   <= b_q;
  a_v_out <= a_v_q;
  b_v_out <= b_v_q;
  acc     <= acc_q;
  -- Combinational (no clock): an AND gate. A MAC happens only if enabled and both inputs are valid.
  -- Reset/clear take priority over en in the register process; no MAC occurs then.
  fire    <= en and a_v_in and b_v_in and not rst and not clr;

  -- Clocked process: describes the registers. Everything inside happens on the rising clock edge.
  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' or clr = '1' then
        -- Reset / start of a new tile: zero the sum and drop the forwarded valids.
        acc_q <= (others => '0');
        a_v_q <= '0';
        b_v_q <= '0';
      elsif en = '1' then
        -- Advance: latch inputs so the neighbors see them next cycle (this is the "systolic" data movement).
        a_q   <= a_in;
        b_q   <= b_in;
        a_v_q <= a_v_in;
        b_v_q <= b_v_in;
        -- Multiply-accumulate, only when both operands are real data.
        -- resize() widens the 32-bit product to the 36-bit accumulator width before adding.
        if a_v_in = '1' and b_v_in = '1' then
          acc_q <= acc_q + resize(a_in * b_in, ACC_W);
        end if;
      end if;
      -- If en = '0' nothing is assigned, so every register keeps its value (the PE is stalled).
    end if;
  end process;
end architecture rtl;
