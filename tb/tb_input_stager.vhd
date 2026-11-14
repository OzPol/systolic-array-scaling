library ieee, std;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.env.all;
use work.sys_pkg.all;

entity tb_input_stager is end;
architecture sim of tb_input_stager is
  constant P : positive := 8;
  signal clk : std_logic := '0';
  signal rst, run_s : std_logic := '0';
  signal budget : unsigned(4 downto 0) := (others => '0');
  signal na, nb : std_logic_vector(0 to P-1) := (others => '0');
  signal a, b, ao, bo : word_array_t(0 to P-1) := (others => (others => '0'));
  signal complete, stall : std_logic;
  signal got : std_logic_vector(0 to 2*P-1);
begin
  clk <= not clk after 5 ns;
  dut : entity work.input_stager generic map(P)
    port map(clk, rst, run_s, budget, na, nb, a, b, ao, bo, complete, stall, got);
  process
    type budgets_t is array(natural range <>) of positive;
    constant budgets : budgets_t := (1, 2, 4, 8, 16);
    variable pending, remaining, taken, cycles, expected_cycles : integer;
    variable done_now : boolean;
    variable mask : std_logic_vector(0 to 2*P-1);
    procedure tick is begin wait until rising_edge(clk); wait for 1 ns; end;
  begin
    rst <= '1'; tick; rst <= '0';
    -- Vary masks as well as budget; poison accepted inputs on later clocks.
    for pattern in 0 to 2 loop
      for bi in budgets'range loop
        mask := (others => '0'); pending := 0;
        for i in 0 to 2*P-1 loop
          if pattern = 0 or (pattern = 1 and i mod 3 = 0) then
            mask(i) := '1'; pending := pending + 1;
          end if;
        end loop;
        na <= mask(0 to P-1); nb <= mask(P to 2*P-1);
        budget <= to_unsigned(budgets(bi), 5); run_s <= '1';
        remaining := pending; cycles := 0;
        loop
          for i in 0 to P-1 loop
            a(i) <= to_signed(100+i, DATA_W);
            b(i) <= to_signed(-100-i, DATA_W);
            if got(i) = '1' then a(i) <= to_signed(30000, DATA_W); end if;
            if got(P+i) = '1' then b(i) <= to_signed(-30000, DATA_W); end if;
          end loop;
          wait for 1 ns;
          done_now := remaining <= budgets(bi);
          assert (complete = '1') = done_now and (stall = '0') = done_now
            report "completion/bypass latency disagrees with accepted word budget" severity failure;
          if done_now then
            for i in 0 to P-1 loop
              if mask(i) = '1' then
                assert ao(i) = to_signed(100+i, DATA_W) report "lost staged A word" severity failure;
              end if;
              if mask(P+i) = '1' then
                assert bo(i) = to_signed(-100-i, DATA_W) report "lost staged B word" severity failure;
              end if;
            end loop;
          end if;
          tick; cycles := cycles + 1;
          exit when done_now;
          remaining := remaining - budgets(bi);
          taken := 0;
          for i in 0 to 2*P-1 loop
            if got(i) = '1' then
              assert mask(i) = '1' report "accepted an unneeded operand" severity failure;
              taken := taken + 1;
            end if;
          end loop;
          assert taken = pending - remaining report "wrong number of accepted words" severity failure;
        end loop;
        expected_cycles := (pending + budgets(bi) - 1) / budgets(bi);
        if pending = 0 then expected_cycles := 1; end if;
        assert cycles = expected_cycles and got = (got'range => '0')
          report "step failed to clear accepted mask" severity failure;
        run_s <= '0'; tick;
        assert complete = '0' and stall = '0' report "idle exposed completion or stall" severity failure;
      end loop;
    end loop;
    -- Reset halfway through a staged step discards all partial acceptance.
    na <= (others => '1'); nb <= (others => '1'); budget <= to_unsigned(4, 5);
    run_s <= '1'; tick;
    assert got /= (got'range => '0') severity failure;
    rst <= '1'; tick;
    assert got = (got'range => '0') report "reset retained a partial step" severity failure;
    report "TB PASS tb_input_stager" severity note;
    finish;
  end process;
end;
