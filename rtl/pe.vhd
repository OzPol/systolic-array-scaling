-- Processing element: forwards A to the right and B downward (registered), and
-- accumulates A*B into a local output-stationary accumulator when both operands
-- are valid.
--   clr : synchronous clear of accumulator and forwarded valids (tile boundary); overrides en
--   en  : advance enable; when '0' every register holds (grid stall)
--   fire: combinational, high when this PE performs a useful MAC this cycle
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.sys_pkg.all;

entity pe is
  port (
    clk, rst, clr, en : in  std_logic;
    a_in    : in  word_t;
    a_v_in  : in  std_logic;
    b_in    : in  word_t;
    b_v_in  : in  std_logic;
    a_out   : out word_t;
    a_v_out : out std_logic;
    b_out   : out word_t;
    b_v_out : out std_logic;
    acc     : out acc_t;
    fire    : out std_logic
  );
end entity pe;

architecture rtl of pe is
  signal a_q, b_q       : word_t := (others => '0');
  signal a_v_q, b_v_q   : std_logic := '0';
  signal acc_q          : acc_t := (others => '0');
begin
  a_out   <= a_q;
  b_out   <= b_q;
  a_v_out <= a_v_q;
  b_v_out <= b_v_q;
  acc     <= acc_q;
  fire    <= en and a_v_in and b_v_in;

  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' or clr = '1' then
        acc_q <= (others => '0');
        a_v_q <= '0';
        b_v_q <= '0';
      elsif en = '1' then
        a_q   <= a_in;
        b_q   <= b_in;
        a_v_q <= a_v_in;
        b_v_q <= b_v_in;
        if a_v_in = '1' and b_v_in = '1' then
          acc_q <= acc_q + resize(a_in * b_in, ACC_W);
        end if;
      end if;
    end if;
  end process;
end architecture rtl;
