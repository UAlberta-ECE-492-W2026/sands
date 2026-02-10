----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 02/03/2026 10:45:12 AM
-- Design Name: 
-- Module Name: FM_Index_tb - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity FM_Index_tb is
    generic (
        SIGMA      : integer := 5;     -- alphabet size
        N          : integer := 8;  -- text length
        PAT_LEN    : integer := 8;    -- max pattern length
        IDX_WIDTH  : integer := 4;    -- index width
        CHAR_WIDTH : integer := 3      -- bits per character
    );
    port (
        clk     : in  std_logic;
        reset   : in  std_logic;
        start   : in  std_logic;

        -- pattern buffer (loaded externally)
        pattern :        in  unsigned(CHAR_WIDTH*PAT_LEN-1 downto 0);
        pat_len_in :     in integer range 1 to PAT_LEN;

        done    : out std_logic;
        fail    : out std_logic;

        l_out   : out unsigned(IDX_WIDTH-1 downto 0);
        r_out   : out unsigned(IDX_WIDTH-1 downto 0)
    );
end entity;

architecture Behavioral of FM_Index_tb is

component FM_Index is
     generic (
        SIGMA      : integer := 5;     -- alphabet size
        N          : integer := 8;  -- text length
        PAT_LEN    : integer := 8;    -- max pattern length
        IDX_WIDTH  : integer := 4;    -- index width
        CHAR_WIDTH : integer := 3      -- bits per character
    );
    port (
        clk     : in  std_logic;
        reset   : in  std_logic;
        start   : in  std_logic;

        -- pattern buffer (loaded externally)
        pattern :        in  unsigned(CHAR_WIDTH*PAT_LEN-1 downto 0);
        pat_len_in :     in integer range 1 to PAT_LEN;

        done    : out std_logic;
        fail    : out std_logic;

        l_out   : out unsigned(IDX_WIDTH-1 downto 0);
        r_out   : out unsigned(IDX_WIDTH-1 downto 0)
    );
end component;

constant TIME_DELTA : time := 10ns;

-- tb signals here
signal clk_tb:      std_logic;
signal reset_tb:    std_logic;
signal start_tb:    std_logic;

signal pattern_tb:      unsigned(CHAR_WIDTH*PAT_LEN-1 downto 0);
signal pat_len_in_tb:   integer range 1 to PAT_LEN;

signal done_tb:     std_logic;
signal fail_tb:     std_logic;

signal l_out_tb:    unsigned(IDX_WIDTH-1 downto 0);
signal r_out_tb:    unsigned(IDX_WIDTH-1 downto 0);

begin

    dut : FM_Index
        port map(
            clk => clk_tb,
            reset => reset_tb,
            start => start_tb,
            pattern => pattern_tb,
            done => done_tb,
            fail => fail_tb,
            l_out => l_out_tb,
            r_out => r_out_tb,
            pat_len_in => pat_len_in_tb
        );
        
    -- Clock generator
    clk_process : process
    begin
        while true loop
            clk_tb <= '0';
            wait for TIME_DELTA;
            clk_tb <= '1';
            wait for TIME_DELTA;
        end loop;
    end process;
    
    
    -- main simulation
    simulation: process
    begin
    
    -- run testbench here
    reset_tb <= '1';
    start_tb <= '0';
    pat_len_in_tb <= 2;
    pattern_tb <= (others => '0');
    -- pattern = [x,x,x,x,x,x,1,4]
    pattern_tb(7*CHAR_WIDTH-1 downto 6*CHAR_WIDTH) <= to_unsigned(1, CHAR_WIDTH);
    pattern_tb(8*CHAR_WIDTH-1 downto 7*CHAR_WIDTH) <= to_unsigned(4, CHAR_WIDTH);
    
    wait for 2*TIME_DELTA;
    
    reset_tb <= '0';
    start_tb <= '1';
    
    wait for 2*TIME_DELTA;
    
    start_tb <= '0';
    
    wait;
    
    end process simulation;

end Behavioral;
