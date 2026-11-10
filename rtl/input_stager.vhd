-- Input staging with a modeled input budget.
-- Each clock the stager accepts at most `budget` combined A/B words of the current
-- boundary step (lowest index first). Accepted words are held in staging registers.
-- The step is `complete` (grid may advance) in the first cycle in which every needed
-- word has been accepted, including words accepted that same cycle. So when
-- budget >= words-in-step the grid advances with no extra staging cycle.
-- While incomplete, complete='0' and the grid holds (stall).
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.sys_pkg.all;

entity input_stager is
  generic (P : positive := 2);
  port (
    clk, rst : in  std_logic;
    run      : in  std_logic;
    budget   : in  unsigned(4 downto 0);
    need_a   : in  std_logic_vector(0 to P-1);
    need_b   : in  std_logic_vector(0 to P-1);
    a_data   : in  word_array_t(0 to P-1);
    b_data   : in  word_array_t(0 to P-1);
    a_out    : out word_array_t(0 to P-1);
    b_out    : out word_array_t(0 to P-1);
    complete : out std_logic;
    stall    : out std_logic;
    got      : out std_logic_vector(0 to 2*P-1)
  );
end entity input_stager;

architecture rtl of input_stager is
  signal got_q    : std_logic_vector(0 to 2*P-1) := (others => '0');
  signal take     : std_logic_vector(0 to 2*P-1);
  signal ok_i     : std_logic;
  signal stage_a  : word_array_t(0 to P-1) := (others => (others => '0'));
  signal stage_b  : word_array_t(0 to P-1) := (others => (others => '0'));
begin
  -- Choose which pending words are accepted this cycle (up to `budget`).
  process (all)
    variable need : std_logic_vector(0 to 2*P-1);
    variable left : integer range 0 to 31;
    variable tk   : std_logic_vector(0 to 2*P-1);
    variable ok   : std_logic;
  begin
    need := need_a & need_b;
    left := to_integer(budget);
    tk   := (others => '0');
    ok   := '1';
    for i in 0 to 2*P-1 loop
      if need(i) = '1' and got_q(i) = '0' then
        if left > 0 then
          tk(i) := '1';
          left  := left - 1;
        else
          ok := '0';
        end if;
      end if;
    end loop;
    take <= tk;
    ok_i <= ok;
  end process;

  complete <= ok_i and run;
  stall    <= (not ok_i) and run;
  got      <= got_q;

  -- Words accepted earlier come from the staging registers; the rest bypass.
  gen_mux : for i in 0 to P-1 generate
    a_out(i) <= stage_a(i) when got_q(i)     = '1' else a_data(i);
    b_out(i) <= stage_b(i) when got_q(P + i) = '1' else b_data(i);
  end generate;

  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        got_q <= (others => '0');
      elsif run = '1' then
        if ok_i = '1' then
          got_q <= (others => '0');          -- step done; next step starts empty
        else
          got_q <= got_q or take;
        end if;
        for i in 0 to P-1 loop
          if take(i)     = '1' then stage_a(i) <= a_data(i); end if;
          if take(P + i) = '1' then stage_b(i) <= b_data(i); end if;
        end loop;
      end if;
    end if;
  end process;
end architecture rtl;
