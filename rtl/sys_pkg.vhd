-- Shared types and constants for the output-stationary systolic array.
-- A package is like a header file: every other file pulls these in with
-- "use work.sys_pkg.all;" so they all agree on bit widths and array shapes.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package sys_pkg is
  constant DATA_W : positive := 16;  -- signed operand width
  constant ACC_W  : positive := 36;  -- exact for a 16-term dot product of signed 16-bit operands
                                     -- (16-bit * 16-bit = 32-bit product, +4 bits so summing 16 of them can't overflow)

  -- One input value (a matrix element) and one accumulated result (a running sum).
  subtype word_t is signed(DATA_W-1 downto 0);
  subtype acc_t  is signed(ACC_W-1 downto 0);

  -- Arrays of the above. "natural range <>" means the size is chosen where the type is used
  -- (e.g. word_array_t(0 to P-1)), so the same type works for any array size P.
  type word_array_t is array (natural range <>) of word_t;                       -- 1-D list of inputs
  type word_2d_t    is array (natural range <>, natural range <>) of word_t;     -- 2-D grid of inputs (wires between PEs)
  type acc_2d_t     is array (natural range <>, natural range <>) of acc_t;      -- 2-D grid of results (one per PE)
  type bit_2d_t     is array (natural range <>, natural range <>) of std_logic;  -- 2-D grid of single bits (valid / fire flags)
end package sys_pkg;
