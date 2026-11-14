-- Compare the instrumented simulation configuration with INSTR=false used by Vivado.
library ieee, std;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.env.all;
use work.sys_pkg.all;
entity tb_synthesis_mode is end;
architecture sim of tb_synthesis_mode is
  constant P : positive := 8;
  constant N : positive := 16;
  signal clk : std_logic := '0';
  signal rst : std_logic := '1';
  signal start : std_logic := '0';
  type steps_t is array(0 to 1) of unsigned(5 downto 0);
  type tiles_t is array(0 to 1) of unsigned(3 downto 0);
  type masks_t is array(0 to 1) of std_logic_vector(0 to P-1);
  type indices_t is array(0 to 1) of unsigned(8 downto 0);
  type outputs_t is array(0 to 1) of acc_t;
  type counter_t is array(0 to 1) of unsigned(31 downto 0);
  signal steps : steps_t;
  signal tr, tc : tiles_t;
  signal na, nb : masks_t;
  signal idx : indices_t;
  signal data : outputs_t;
  signal valid, done : std_logic_vector(0 to 1);
  signal compute, total, stall_c, advance_c, capture_c : counter_t;
  signal a, b : word_array_t(0 to P-1);
begin
  clk <= not clk after 5 ns;
  versions : for mode in 0 to 1 generate
    dut : entity work.systolic_top generic map(P=>P,N=>N,INSTR=>(mode=0))
      port map(clk=>clk,rst=>rst,start=>start,budget=>to_unsigned(4,5),
        step_t=>steps(mode),tile_row=>tr(mode),tile_col=>tc(mode),
        a_need=>na(mode),b_need=>nb(mode),stage_got=>open,a_data=>a,b_data=>b,
        out_valid=>valid(mode),out_idx=>idx(mode),out_data=>data(mode),done=>done(mode),
        cnt_compute=>compute(mode),cnt_total=>total(mode),cnt_stall=>stall_c(mode),
        cnt_adv=>advance_c(mode),cnt_cap=>capture_c(mode),mac_fire=>open);
  end generate;
  drive : process(all)
  begin
    for i in 0 to P-1 loop
      a(i) <= to_signed((to_integer(tr(0))*P+i)*37-to_integer(steps(0))*13,DATA_W);
      b(i) <= to_signed((to_integer(tc(0))*P+i)*(-19)+to_integer(steps(0))*7,DATA_W);
    end loop;
  end process;
  monitor : process(clk)
  begin
    if rising_edge(clk) and rst='0' then
      assert steps(0)=steps(1) and tr(0)=tr(1) and tc(0)=tc(1) and na(0)=na(1) and nb(0)=nb(1)
        report "instrumentation changes request schedule" severity failure;
      assert valid(0)=valid(1) and done(0)=done(1) report "instrumentation changes result timing" severity failure;
      if valid(0)='1' then
        assert idx(0)=idx(1) and data(0)=data(1) report "instrumentation changes result data" severity failure;
      end if;
      assert compute(1)=0 and total(1)=0 and stall_c(1)=0 and advance_c(1)=0 and capture_c(1)=0
        report "disabled counters are not constant zero" severity failure;
    end if;
  end process;
  process
  begin
    for i in 1 to 4 loop wait until rising_edge(clk); end loop;
    rst<='0'; wait until falling_edge(clk); start<='1';
    wait until falling_edge(clk); start<='0';
    wait until done(0)='1' for 1 ms;
    assert done(0)='1' and done(1)='1' report "synthesis-mode comparison timeout" severity failure;
    wait until falling_edge(clk);
    report "TB PASS tb_synthesis_mode" severity note;
    finish;
  end process;
end;
