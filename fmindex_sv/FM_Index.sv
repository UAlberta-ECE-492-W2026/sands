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
    input logic [$clog2(`PAT_LEN+1)-1:0] pat_len_in,

    input logic [`IDX_WIDTH-1:0] ram_data,
    output logic [32:0] ram_addr,

    output logic done,
    output logic fail,

    output logic [`IDX_WIDTH-1:0] l_out,
    output logic [`IDX_WIDTH-1:0] r_out
);

localparam int PAT_IDX_W = $clog2(`PAT_LEN);
localparam int LOOP_COUNT_W = $clog2(`PAT_LEN + 1);

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

typedef struct packed {
    logic [`IDX_WIDTH-1:0] l;
    logic [`IDX_WIDTH-1:0] r;
    logic [`IDX_WIDTH-1:0] rank_l;
    logic [`IDX_WIDTH-1:0] rank_r;
    logic [PAT_IDX_W-1:0] pat_idx;
    logic [LOOP_COUNT_W-1:0] loop_count;
} search_t;

function automatic logic [32:0] occ_addr(
    input logic [`CHAR_WIDTH-1:0] char,
    input logic [`IDX_WIDTH-1:0] row
);
    begin
        // Read from occ array in RAM (NOTE: char is 1-based index, row and RAM is 0-based)
        // &Occ[c][r] = OCC_OFFSET + ROW_WIDTH * row + (char - 1)
        //            = 4          + 4         * row + (char - 1)
        occ_addr = row * 4 + ({29'd0, column} - 33'd1) + 33'd4;
    end
endfunction

function automatic logic [32:0] c_arr_addr(
    input logic [`CHAR_WIDTH-1:0] char
);
    begin
        // Read from count array in RAM (char is 1-based index, RAM is 0-based)
        // &Count[char] = char - 1
        c_arr_addr = {30'd0, char} - 33'd1;
    end
endfunction

state_t state, next_state;
search_t cur, nxt;

// Logging
`ifdef VERILATOR
always_ff @(negedge clk) begin
    case (state)
    INIT: $display("INIT");
    READ_CHAR: $display("READ_CHAR c=%d", c);
    RANK_L_S: $display("RANK_L_S");
    RANK_L_S_LOAD: $display("RANK_L_S_LOAD");
    RANK_R_S: $display("RANK_R_S");
    RANK_R_S_LOAD: $display("RANK_R_S_LOAD");
    UPDATE: $display("UPDATE");
    UPDATE_LOAD: $display("UPDATE_LOAD");
    CHECK: $display("CHECK");
    DONE_S: $display("DONE_S");
    FAIL_S: $display("FAIL_S");
    default: ;
    endcase
end
`endif

always_ff @(posedge clk) begin
    if (reset) state <= IDLE;
    else state <= next_state;
end

logic [`CHAR_WIDTH-1:0] char;
assign char = pattern[cur.pat_idx*`CHAR_WIDTH +: `CHAR_WIDTH];

// Next state
always_comb begin
    case (state)
    IDLE: begin
        if (start == 1)
            next_state = INIT;
        else
            next_state = IDLE;
    end

    INIT: next_state = READ_CHAR;

    READ_CHAR: begin
        if (char == 0)
            // Skip '$' chars (should be end of input)
            next_state = CHECK;
        else
            next_state = RANK_L_S;
    end

    RANK_L_S: next_state = RANK_L_S_LOAD;
    RANK_L_S_LOAD: next_state = RANK_R_S;
    RANK_R_S: next_state = RANK_R_S_LOAD;
    RANK_R_S_LOAD: next_state = UPDATE;
    UPDATE: next_state = UPDATE_LOAD;
    UPDATE_LOAD: next_state = CHECK;

    CHECK: begin
        if (cur.l >= cur.r) begin
            next_state = FAIL_S;
        end else if (cur.loop_count == 0) begin
            next_state = DONE_S;
        end else begin
            next_state = READ_CHAR;
        end
    end
    
    DONE_S: next_state = IDLE;
    FAIL_S: next_state = IDLE;

    default: next_state = IDLE;
    endcase
end

// Outputs
assign l_out = cur.l;
assign r_out = cur.r;
assign done = state == DONE_S;
assign fail = state == FAIL_S;
always_comb begin
    case (state)
    RANK_L_S: ram_addr = occ_addr(char, cur.l);
    RANK_R_S: ram_addr = occ_addr(char, cur.r);
    UPDATE: ram_addr = c_arr_addr(char);
    default: ram_addr = 0;
    endcase
end

always_ff @(posedge clk) begin
    if (reset) begin
        cur <= '0;
    end else begin
        cur <= nxt;
    end
end

always_comb begin
    nxt = cur;

    case (state)
    INIT: begin
        nxt.l = `IDX_WIDTH'd0;
        nxt.r = `IDX_WIDTH'd`N;
        nxt.loop_count = pat_len_in;
        nxt.pat_idx = PAT_IDX_W'(`PAT_LEN - 1);
    end

    READ_CHAR: begin
        nxt.loop_count = cur.loop_count - 1'b1;
    end

    RANK_L_S_LOAD: begin
        nxt.rank_l = ram_data; // Occ[char][l];
    end

    RANK_R_S_LOAD: begin
        nxt.rank_r = ram_data; // Occ[char][r];
    end

    UPDATE_LOAD: begin
        nxt.l = ram_data + cur.rank_l; // C_arr[char] + rank_l;
        nxt.r = ram_data + cur.rank_r; // C_arr[char] + rank_r;
    end

    CHECK: begin
        if (!(cur.l >= cur.r) && !(cur.loop_count == 0)) begin
            nxt.pat_idx = cur.pat_idx - 1'b1;
        end
    end

    default: ;
    endcase
end

endmodule
