`define CHAR_WIDTH 3
`define PAT_LEN 8 
`define IDX_WIDTH 4
`define SIGMA 5
`define N 8

module FM_Index (
    input logic clk,
    input logic reset,
    input logic start,

    input logic [`CHAR_WIDTH*`PAT_LEN-1:0] pattern,
    input int pat_len_in,
    input logic we,

    input logic [32:0] ram_data,
    output logic [32:0] ram_addr,

    output logic done,
    output logic fail,

    output logic [`IDX_WIDTH-1:0] l_out,
    output logic [`IDX_WIDTH-1:0] r_out
);

logic [`CHAR_WIDTH*`PAT_LEN-1:0] mem;

typedef enum logic [3:0] {
    IDLE,
    INIT,
    READ_CHAR,
    RANK_L_S,
    RANK_L_S_LOAD,
    RANK_R_S,
    RANK_R_S_LOAD,
    UPDATE,
    UPDATE_LOAD,
    CHECK,
    DONE_S,
    FAIL_S
} state_t;

state_t state;

logic [`IDX_WIDTH-1:0] l;
logic [`IDX_WIDTH-1:0] r;
logic [`IDX_WIDTH-1:0] rank_l;
logic [`IDX_WIDTH-1:0] rank_r;

logic [`CHAR_WIDTH-1:0] c;

function logic [32:0] occ_addr(
    input logic [32:0] column,
    input logic [32:0] row
);
    begin
        occ_addr = row * 5 + column + 5;
    end
endfunction

function logic [32:0] c_arr_addr(
    input logic [32:0] idx
);
    begin
        c_arr_addr = idx;
    end
endfunction

int pat_idx;

int loop_count;

/*
    -- data assumes:
    -- text = "GATTACA$"
    -- bwt  = "ACTGA$TA"
    -- $ → 0
    -- A → 1
    -- C → 2
    -- G → 3
    -- T → 4
*/

always_ff @(posedge clk) begin
    if (we)
        mem <= pattern;
end

always_ff @(posedge clk) begin
    if (reset) begin
        state <= IDLE;
        done <= 0;
        fail <= 0;
    end else begin
        case (state)

            IDLE: begin
                done <= 0;
                fail <= 0;
                loop_count <= pat_len_in;
                if (start == 1) begin
                    state <= INIT;
                end
            end

            INIT: begin
                l <= `IDX_WIDTH'd0;
                r <= `IDX_WIDTH'd`N;
                pat_idx <= `PAT_LEN - 1;
                state <= READ_CHAR;
                $display("INIT\n");
            end

            READ_CHAR: begin
                c <= pattern[pat_idx*`CHAR_WIDTH +: `CHAR_WIDTH];
                loop_count <= loop_count - 1;
                state <= RANK_L_S;
                $display("READ_CHAR\n");
            end

            RANK_L_S: begin
                ram_addr <= occ_addr(c, l);
                state <= RANK_L_S_LOAD;
                $display("RANK_L_S\n");
            end

            RANK_L_S_LOAD: begin
                rank_l <= ram_data; // Occ[c][l];
                state <= RANK_R_S;
                $display("RANK_L_S_LOAD\n");

                $display("ram[%d] => %d", ram_addr, ram_data);
            end

            RANK_R_S: begin
                ram_addr <= occ_addr(c, r);
                state <= RANK_R_S_LOAD;
                $display("RANK_R_S\n");
            end

            RANK_R_S_LOAD: begin
                rank_r <= ram_data; // Occ[c][r];
                state <= UPDATE;
                $display("RANK_R_S_LOAD\n");

                $display("ram[%d] => %d", ram_addr, ram_data);
            end

            UPDATE: begin
                ram_addr <= c_arr_addr(c);
                state <= UPDATE_LOAD;
                $display("UPDATE\n");
            end

            UPDATE_LOAD: begin
                l <= ram_data + rank_l; // C_arr[c] + rank_l;
                r <= ram_data + rank_r; // C_arr[c] + rank_r;
                state <= CHECK;
                $display("UPDATE_LOAD\n");

                $display("ram[%d] => %d", ram_addr, ram_data);
            end

            CHECK: begin
                if (l >= r) begin
                    state <= FAIL_S;
                end else if (loop_count == 0) begin
                    state <= DONE_S;
                end else begin
                    pat_idx <= pat_idx - 1;
                    state <= READ_CHAR;
                end
                $display("CHECK\n");
            end
            
            DONE_S: begin
                done <= 1;
                state <= IDLE;
                $display("DONE_S\n");
                $display("l_out: %0d\n", l);
                $display("r_out: %0d\n", r);
            end

            FAIL_S: begin
                fail <= 1;
                state <= IDLE;
                $display("FAIL_S\n");
            end

            default: begin
                state <= IDLE;
            end
        endcase
    end
end

assign l_out = l;
assign r_out = r;

endmodule
