-- Shared types and constants for the output-stationary systolic array.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package sys_pkg is
  constant DATA_W : positive := 16;  -- signed operand width
  constant ACC_W  : positive := 36;  -- exact for a 16-term dot product of signed 16-bit operands

  subtype word_t is signed(DATA_W-1 downto 0);
  subtype acc_t  is signed(ACC_W-1 downto 0);

  type word_array_t is array (natural range <>) of word_t;
  type word_2d_t    is array (natural range <>, natural range <>) of word_t;
  type acc_2d_t     is array (natural range <>, natural range <>) of acc_t;
  type bit_2d_t     is array (natural range <>, natural range <>) of std_logic;
end package sys_pkg;
