library ieee, std;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.env.all;
use work.sys_pkg.all;

entity tb_pe is end;
architecture sim of tb_pe is
  signal clk : std_logic := '0';
  signal rst, clr, en, av, bv : std_logic := '0';
  signal a, b, ao, bo : word_t := (others => '0');
  signal avo, bvo, fire : std_logic;
  signal acc : acc_t;
begin
  clk <= not clk after 5 ns;
  dut : entity work.pe port map(clk, rst, clr, en, a, av, b, bv, ao, avo, bo, bvo, acc, fire);
  process
    procedure tick is begin wait until rising_edge(clk); wait for 1 ns; end;
  begin
    rst <= '1'; en <= '1'; av <= '1'; bv <= '1';
    a <= to_signed(-32768, DATA_W); b <= to_signed(-32768, DATA_W);
    wait for 1 ns;
    assert fire = '0' report "reset must suppress useful MAC event" severity failure;
    tick;
    assert acc = to_signed(0, ACC_W) and avo = '0' and bvo = '0' severity failure;
    rst <= '0';
    for i in 1 to 16 loop tick; end loop;
    assert acc = signed'(x"400000000") report "full-width 16-term extreme dot product" severity failure;
    en <= '0'; a <= to_signed(7, DATA_W); b <= to_signed(-3, DATA_W);
    tick;
    assert acc = signed'(x"400000000") and ao = to_signed(-32768, DATA_W)
      and bo = to_signed(-32768, DATA_W) and fire = '0'
      report "stall changed PE state" severity failure;
    clr <= '1'; en <= '1'; wait for 1 ns;
    assert fire = '0' report "clear must suppress useful MAC event" severity failure;
    tick;
    assert acc = to_signed(0, ACC_W) and avo = '0' and bvo = '0' severity failure;
    clr <= '0'; tick;
    assert acc = to_signed(-21, ACC_W) and ao = to_signed(7, DATA_W)
      and bo = to_signed(-3, DATA_W) and avo = '1' and bvo = '1' severity failure;
    av <= '0'; tick;
    assert acc = to_signed(-21, ACC_W) and avo = '0' and bvo = '1'
      report "unpaired operands must forward but not accumulate" severity failure;
    clr <= '1'; en <= '0'; tick;
    assert acc = to_signed(0, ACC_W) report "clear must override stall" severity failure;
    report "TB PASS tb_pe" severity note;
    finish;
  end process;
end;
