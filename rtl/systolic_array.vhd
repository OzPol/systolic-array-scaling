-- P x P output-stationary grid built from one PE design.
-- A enters PE(r,0) from the left, B enters PE(0,c) from the top. Skewing is done
-- by the controller (A[r][k] on boundary step k+r, B[k][c] on step k+c), so matching
-- operands meet at PE(r,c) on step k+r+c.
--
-- This file only wires PEs together; it has no logic of its own.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.sys_pkg.all;

entity systolic_array is
  generic (P : positive := 2);  -- grid size: P x P PEs (a generic is a compile-time parameter)
  port (
    clk, rst, clr, en : in  std_logic;           -- shared by every PE
    a_in : in  word_array_t(0 to P-1);           -- one A value per row, entering from the left edge
    a_v  : in  std_logic_vector(0 to P-1);       -- valid bit for each A input
    b_in : in  word_array_t(0 to P-1);           -- one B value per column, entering from the top edge
    b_v  : in  std_logic_vector(0 to P-1);       -- valid bit for each B input
    acc  : out acc_2d_t(0 to P-1, 0 to P-1);     -- every PE's accumulator (the P x P result tile)
    fire : out bit_2d_t(0 to P-1, 0 to P-1)      -- every PE's "did a MAC" flag
  );
end entity systolic_array;

architecture rtl of systolic_array is
  -- Wires between neighboring PEs. They have one extra column/row so each PE can
  -- have an input link on one side and an output link on the other:
  --   a_link(r, c)   = A value going INTO PE(r,c) from the left;  a_link(r, c+1) = going OUT to the right.
  --   b_link(r, c)   = B value going INTO PE(r,c) from the top;   b_link(r+1, c) = going OUT downward.
  -- The *_vl signals are the matching valid bits.
  signal a_link : word_2d_t(0 to P-1, 0 to P);
  signal a_vl   : bit_2d_t (0 to P-1, 0 to P);
  signal b_link : word_2d_t(0 to P, 0 to P-1);
  signal b_vl   : bit_2d_t (0 to P, 0 to P-1);
begin
  -- Connect the grid's external inputs to the left column (A) and top row (B) of links.
  edge_in : for i in 0 to P-1 generate
    a_link(i, 0) <= a_in(i);
    a_vl(i, 0)   <= a_v(i);
    b_link(0, i) <= b_in(i);
    b_vl(0, i)   <= b_v(i);
  end generate;

  -- "generate" loops build hardware: this creates P*P separate PE copies, one per (r, c).
  -- Each PE's outputs are wired to the inputs of the PE to its right (A) and below (B).
  gen_r : for r in 0 to P-1 generate
    gen_c : for c in 0 to P-1 generate
      u_pe : entity work.pe
        port map (
          clk => clk, rst => rst, clr => clr, en => en,
          a_in    => a_link(r, c),        -- from left neighbor
          a_v_in  => a_vl(r, c),
          a_out   => a_link(r, c+1),      -- to right neighbor
          a_v_out => a_vl(r, c+1),
          b_in    => b_link(r, c),        -- from top neighbor
          b_v_in  => b_vl(r, c),
          b_out   => b_link(r+1, c),      -- to bottom neighbor
          b_v_out => b_vl(r+1, c),
          acc     => acc(r, c),           -- this PE's result goes straight to the output
          fire    => fire(r, c)
        );
    end generate;
  end generate;
end architecture rtl;
