----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 02/02/2026 04:16:17 PM
-- Design Name: 
-- Module Name: FM_Index - Behavioral
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

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity FM_Index is
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
        pattern :       in  unsigned(CHAR_WIDTH*PAT_LEN-1 downto 0);
        pat_len_in :    in integer range 1 to PAT_LEN;

        done    : out std_logic;
        fail    : out std_logic;

        l_out   : out unsigned(IDX_WIDTH-1 downto 0);
        r_out   : out unsigned(IDX_WIDTH-1 downto 0)
    );
end entity;

architecture rtl of FM_Index is

    -- FSM states
    type state_t is (
        IDLE,
        INIT,
        READ_CHAR,
        RANK_L_S,
        RANK_R_S,
        UPDATE,
        CHECK,
        DONE_S,
        FAIL_S
    );

    signal state : state_t := IDLE;

    -- Registers
    signal l, r       : unsigned(IDX_WIDTH-1 downto 0);
    signal rank_l     : unsigned(IDX_WIDTH-1 downto 0);
    signal rank_r     : unsigned(IDX_WIDTH-1 downto 0);

    signal pat_idx    : integer range 0 to PAT_LEN-1;
    signal c          : unsigned(CHAR_WIDTH-1 downto 0);
    
    signal loop_count : integer range 0 to PAT_LEN-1;

    -- ===== FM-index tables =====

    -- data assumes:
    -- text = "GATTACA$"
    -- bwt  = "ACTGA$TA"
    -- $ → 0
    -- A → 1
    -- C → 2
    -- G → 3
    -- T → 4

    -- C table
    type C_array is array (0 to SIGMA-1) of unsigned(IDX_WIDTH-1 downto 0);
    signal C_arr : C_array := (
        0 => to_unsigned(0, IDX_WIDTH),
        1 => to_unsigned(1, IDX_WIDTH),
        2 => to_unsigned(4, IDX_WIDTH),
        3 => to_unsigned(5, IDX_WIDTH),
        4 => to_unsigned(6, IDX_WIDTH)
    );

    -- Occ table (full version)
    type Occ_array is array (0 to SIGMA-1, 0 to N) of unsigned(IDX_WIDTH-1 downto 0);
    signal Occ : Occ_array := (
        0 => (others => TO_UNSIGNED(0, IDX_WIDTH)),
        1 => ( -- A
            0 => to_unsigned(0, IDX_WIDTH),
            1 => to_unsigned(1, IDX_WIDTH),
            2 => to_unsigned(1, IDX_WIDTH),
            3 => to_unsigned(1, IDX_WIDTH),
            4 => to_unsigned(1, IDX_WIDTH),
            5 => to_unsigned(2, IDX_WIDTH),
            6 => to_unsigned(2, IDX_WIDTH),
            7 => to_unsigned(2, IDX_WIDTH),
            8 => to_unsigned(3, IDX_WIDTH)
        ),
        2 => ( -- C
            0 => to_unsigned(0, IDX_WIDTH),
            1 => to_unsigned(0, IDX_WIDTH),
            2 => to_unsigned(1, IDX_WIDTH),
            3 => to_unsigned(1, IDX_WIDTH),
            4 => to_unsigned(1, IDX_WIDTH),
            5 => to_unsigned(1, IDX_WIDTH),
            6 => to_unsigned(1, IDX_WIDTH),
            7 => to_unsigned(1, IDX_WIDTH),
            8 => to_unsigned(1, IDX_WIDTH)
        ),
        3 => ( -- G
            0 => to_unsigned(0, IDX_WIDTH),
            1 => to_unsigned(0, IDX_WIDTH),
            2 => to_unsigned(0, IDX_WIDTH),
            3 => to_unsigned(0, IDX_WIDTH),
            4 => to_unsigned(1, IDX_WIDTH),
            5 => to_unsigned(1, IDX_WIDTH),
            6 => to_unsigned(1, IDX_WIDTH),
            7 => to_unsigned(1, IDX_WIDTH),
            8 => to_unsigned(1, IDX_WIDTH)
        ),
        4 => ( -- T
            0 => to_unsigned(0, IDX_WIDTH),
            1 => to_unsigned(0, IDX_WIDTH),
            2 => to_unsigned(0, IDX_WIDTH),
            3 => to_unsigned(1, IDX_WIDTH),
            4 => to_unsigned(1, IDX_WIDTH),
            5 => to_unsigned(1, IDX_WIDTH),
            6 => to_unsigned(1, IDX_WIDTH),
            7 => to_unsigned(2, IDX_WIDTH),
            8 => to_unsigned(2, IDX_WIDTH)
        )
    );


begin

    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                state <= IDLE;
                done  <= '0';
                fail  <= '0';
                loop_count <= pat_len_in;

            else
                case state is

                    when IDLE =>
                        done <= '0';
                        fail <= '0';
                        if start = '1' then
                            state <= INIT;
                        end if;

                    when INIT =>
                        l <= (others => '0');
                        r <= to_unsigned(N, IDX_WIDTH);
                        pat_idx <= PAT_LEN - 1;
                        state <= READ_CHAR;

                    when READ_CHAR =>
                        c <= pattern(
                            (pat_idx+1)*CHAR_WIDTH-1 downto pat_idx*CHAR_WIDTH
                        );
                        loop_count <= loop_count - 1;
                        state <= RANK_L_S;

                    when RANK_L_S =>
                        rank_l <= Occ(to_integer(c), to_integer(l));
                        state <= RANK_R_S;


                    when RANK_R_S =>
                        rank_r <= Occ(to_integer(c), to_integer(r));
                        state <= UPDATE;

                    when UPDATE =>
                        l <= C_arr(to_integer(c)) + rank_l;
                        r <= C_arr(to_integer(c)) + rank_r;
                        state <= CHECK;

                    when CHECK =>
                        if l >= r then -- doesn't happen here, test later
                            state <= FAIL_S;
                        elsif loop_count = 0 then
                            state <= DONE_S;
                        else
                            pat_idx <= pat_idx - 1;
                            state <= READ_CHAR;
                        end if;

                    when DONE_S =>
                        done <= '1';
                        state <= IDLE;

                    when FAIL_S =>
                        fail <= '1';
                        state <= IDLE;

                    when others =>
                        state <= IDLE;

                end case;
            end if;
        end if;
    end process;

    l_out <= l;
    r_out <= r;

end architecture;

