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

    input logic [`IDX_WIDTH-1:0] ram_data,
    output logic [32:0] ram_addr,

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
    RANK_L_S_LOAD,
    RANK_R_S,
    RANK_R_S_LOAD,
    UPDATE,
    UPDATE_LOAD,
    CHECK,
    DONE_S,
    FAIL_S
} state_t;

function automatic logic [32:0] occ_addr(
    input logic [`CHAR_WIDTH-1:0] column,
    input logic [`IDX_WIDTH-1:0] row
);
    begin
        occ_addr = row * 4 + ({29'd0, column} - 33'd1) + 33'd4;
    end
endfunction

function automatic logic [32:0] c_arr_addr(
    input logic [`CHAR_WIDTH-1:0] idx
);
    begin
        c_arr_addr = {30'd0, idx} - 33'd1;
    end
endfunction

state_t state;
state_t next_state;
always_ff @(posedge clk) begin
    if (reset) state <= IDLE;
    else state <= next_state;
end

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

logic [`CHAR_WIDTH-1:0] c;
assign c = pattern[pat_idx*`CHAR_WIDTH +: `CHAR_WIDTH];

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
        if (c == 0)
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
        if (l >= r) begin
            next_state = FAIL_S;
        end else if (loop_count == 0) begin
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
assign l_out = l;
assign r_out = r;
assign done = state == DONE_S;
assign fail = state == FAIL_S;
always_comb begin
    case (state)
    RANK_L_S: ram_addr = occ_addr(c, l);
    RANK_R_S: ram_addr = occ_addr(c, r);
    UPDATE: ram_addr = c_arr_addr(c);
    default: ram_addr = 0;
    endcase
end

// Register Updates
logic [`IDX_WIDTH-1:0] l, next_l;
logic [`IDX_WIDTH-1:0] r, next_r;
logic [`IDX_WIDTH-1:0] rank_l, next_rank_l;
logic [`IDX_WIDTH-1:0] rank_r, next_rank_r;
int pat_idx, next_pat_idx;
int loop_count, next_loop_count;

always_ff @(posedge clk) begin
    if (reset) begin
        l <= 0;
        r <= 0;
        rank_l <= 0;
        rank_r <= 0;
        pat_idx <= 0;
        loop_count <= 0;
    end else begin
        l <= next_l;
        r <= next_r;
        rank_l <= next_rank_l;
        rank_r <= next_rank_r;
        pat_idx <= next_pat_idx;
        loop_count <= next_loop_count;
    end
end

always_comb begin
    next_l = l;
    next_r = r;
    next_rank_l = rank_l;
    next_rank_r = rank_r;
    next_pat_idx = pat_idx;
    next_loop_count = loop_count;

    case (state)
    INIT: begin
        next_l = `IDX_WIDTH'd0;
        next_r = `IDX_WIDTH'd`N;
        next_loop_count = pat_len_in;
        next_pat_idx = `PAT_LEN - 1;
    end

    READ_CHAR: begin
        next_loop_count = loop_count - 1;
    end

    RANK_L_S_LOAD: begin
        next_rank_l = ram_data; // Occ[c][l];
    end

    RANK_R_S_LOAD: begin
        next_rank_r = ram_data; // Occ[c][r];
    end

    UPDATE_LOAD: begin
        next_l = ram_data + rank_l; // C_arr[c] + rank_l;
        next_r = ram_data + rank_r; // C_arr[c] + rank_r;
    end

    CHECK: begin
        if (!(l >= r) && !(loop_count == 0)) begin
            next_pat_idx = pat_idx - 1;
        end
    end

    default: ;
    endcase
end

endmodule
