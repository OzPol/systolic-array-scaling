-- P x P output-stationary grid built from one PE design.
-- A enters PE(r,0) from the left, B enters PE(0,c) from the top. Skewing is done
-- by the controller (A[r][k] on boundary step k+r, B[k][c] on step k+c), so matching
-- operands meet at PE(r,c) on step k+r+c.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.sys_pkg.all;

entity systolic_array is
  generic (P : positive := 2);
  port (
    clk, rst, clr, en : in  std_logic;
    a_in : in  word_array_t(0 to P-1);
    a_v  : in  std_logic_vector(0 to P-1);
    b_in : in  word_array_t(0 to P-1);
    b_v  : in  std_logic_vector(0 to P-1);
    acc  : out acc_2d_t(0 to P-1, 0 to P-1);
    fire : out bit_2d_t(0 to P-1, 0 to P-1)
  );
end entity systolic_array;

architecture rtl of systolic_array is
  signal a_link : word_2d_t(0 to P-1, 0 to P);
  signal a_vl   : bit_2d_t (0 to P-1, 0 to P);
  signal b_link : word_2d_t(0 to P, 0 to P-1);
  signal b_vl   : bit_2d_t (0 to P, 0 to P-1);
begin
  edge_in : for i in 0 to P-1 generate
    a_link(i, 0) <= a_in(i);
    a_vl(i, 0)   <= a_v(i);
    b_link(0, i) <= b_in(i);
    b_vl(0, i)   <= b_v(i);
  end generate;

  gen_r : for r in 0 to P-1 generate
    gen_c : for c in 0 to P-1 generate
      u_pe : entity work.pe
        port map (
          clk => clk, rst => rst, clr => clr, en => en,
          a_in    => a_link(r, c),
          a_v_in  => a_vl(r, c),
          a_out   => a_link(r, c+1),
          a_v_out => a_vl(r, c+1),
          b_in    => b_link(r, c),
          b_v_in  => b_vl(r, c),
          b_out   => b_link(r+1, c),
          b_v_out => b_vl(r+1, c),
          acc     => acc(r, c),
          fire    => fire(r, c)
        );
    end generate;
  end generate;
end architecture rtl;
