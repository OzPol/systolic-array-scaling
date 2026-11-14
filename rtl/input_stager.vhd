-- Input staging with a modeled input budget.
-- Each clock the stager accepts at most `budget` combined A/B words of the current
-- boundary step (lowest index first). Accepted words are held in staging registers.
-- The step is `complete` (grid may advance) in the first cycle in which every needed
-- word has been accepted, including words accepted that same cycle. So when
-- budget >= words-in-step the grid advances with no extra staging cycle.
-- While incomplete, complete='0' and the grid holds (stall).
--
-- Why this exists: it models limited input bandwidth (e.g. a memory that can only
-- deliver `budget` words per clock). If a step needs more words than that, the
-- grid waits (stalls) until they have all arrived.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.sys_pkg.all;

entity input_stager is
  generic (P : positive := 2);
  port (
    clk, rst : in  std_logic;
    run      : in  std_logic;                     -- '1' while the controller is in the RUN state
    budget   : in  unsigned(4 downto 0);          -- max words accepted per clock
    need_a   : in  std_logic_vector(0 to P-1);    -- which A words this step requires
    need_b   : in  std_logic_vector(0 to P-1);    -- which B words this step requires
    a_data   : in  word_array_t(0 to P-1);        -- A values offered by the environment
    b_data   : in  word_array_t(0 to P-1);        -- B values offered by the environment
    a_out    : out word_array_t(0 to P-1);        -- A values handed to the grid
    b_out    : out word_array_t(0 to P-1);        -- B values handed to the grid
    complete : out std_logic;                     -- '1' = all words for this step are in; grid may advance
    stall    : out std_logic;                     -- '1' = still waiting on words; grid holds
    got      : out std_logic_vector(0 to 2*P-1)   -- which words have already been accepted (A bits then B bits)
  );
end entity input_stager;

architecture rtl of input_stager is
  signal got_q    : std_logic_vector(0 to 2*P-1) := (others => '0');  -- register: words accepted on earlier cycles
  signal take     : std_logic_vector(0 to 2*P-1);                     -- wires: words accepted THIS cycle
  signal ok_i     : std_logic;                                        -- wire: every needed word is covered
  signal stage_a  : word_array_t(0 to P-1) := (others => (others => '0'));  -- registers holding accepted A words
  signal stage_b  : word_array_t(0 to P-1) := (others => (others => '0'));  -- registers holding accepted B words
begin
  -- Choose which pending words are accepted this cycle (up to `budget`).
  -- Combinational process (process (all)): pure logic, no registers. The loop is
  -- unrolled into hardware; it's not run one iteration at a time.
  process (all)
    variable need : std_logic_vector(0 to 2*P-1);  -- A needs followed by B needs
    variable left : integer range 0 to 31;         -- budget remaining this cycle
    variable tk   : std_logic_vector(0 to 2*P-1);
    variable ok   : std_logic;
  begin
    need := need_a & need_b;
    left := to_integer(budget);
    tk   := (others => '0');
    ok   := '1';
    for i in 0 to 2*P-1 loop
      -- A word is pending if it's needed and we haven't accepted it yet.
      if need(i) = '1' and got_q(i) = '0' then
        if left > 0 then
          tk(i) := '1';         -- accept it, spend one unit of budget
          left  := left - 1;
        else
          ok := '0';            -- out of budget: step can't finish this cycle
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
  -- (A mux per word: use the stored copy if we already took it, else pass the live input straight through.)
  gen_mux : for i in 0 to P-1 generate
    a_out(i) <= stage_a(i) when got_q(i)     = '1' else a_data(i);
    b_out(i) <= stage_b(i) when got_q(P + i) = '1' else b_data(i);
  end generate;

  -- Clocked process: remembers which words were accepted and stores their values.
  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        got_q <= (others => '0');
      elsif run = '1' then
        if ok_i = '1' then
          got_q <= (others => '0');          -- step done; next step starts empty
        else
          got_q <= got_q or take;            -- remember what we've accepted so far
        end if;
        -- Save the value of each word accepted this cycle.
        for i in 0 to P-1 loop
          if take(i)     = '1' then stage_a(i) <= a_data(i); end if;
          if take(P + i) = '1' then stage_b(i) <= b_data(i); end if;
        end loop;
      end if;
    end if;
  end process;
end architecture rtl;
