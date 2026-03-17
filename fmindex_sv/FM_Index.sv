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

    output logic done,
    output logic fail,

    output logic [`IDX_WIDTH-1:0] l_out,
    output logic [`IDX_WIDTH-1:0] r_out
);

typedef enum logic [3:0] {
    IDLE,
    INIT,
    READ_CHAR,
    RANK_L_S,
    RANK_R_S,
    UPDATE,
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

// C table
logic [`IDX_WIDTH-1:0] C_arr [0:`SIGMA-1] = {`IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd4, `IDX_WIDTH'd5, `IDX_WIDTH'd6};

// Occ table
logic [`IDX_WIDTH-1:0] Occ [0:`SIGMA-1][0:`N] = {
    {`IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0},
    {`IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd2, `IDX_WIDTH'd2, `IDX_WIDTH'd2, `IDX_WIDTH'd3}, // A
    {`IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1}, // C
    {`IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1}, // G
    {`IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd2, `IDX_WIDTH'd2}  // T
};

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
            end

            READ_CHAR: begin
                c <= pattern[pat_idx*`CHAR_WIDTH +: `CHAR_WIDTH];
                loop_count <= loop_count - 1;
                state <= RANK_L_S;
            end

            RANK_L_S: begin
                rank_l <= Occ[c][l];
                state <= RANK_R_S;
            end

            RANK_R_S: begin
                rank_r <= Occ[c][r];
                state <= UPDATE;
            end

            UPDATE: begin
                l <= C_arr[c] + rank_l;
                r <= C_arr[c] + rank_r;
                state <= CHECK;
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
            end
            
            DONE_S: begin
                done <= 1;
                state <= IDLE;
            end

            FAIL_S: begin
                fail <= 1;
                state <= IDLE;
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
