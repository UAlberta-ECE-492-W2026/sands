`define CHAR_WIDTH 3
`define IDX_WIDTH 32
`define HEADER_WORDS 3

localparam logic [31:0] INDEX_MAGIC = 32'h3144_4946; // "FID1" in little-endian bytes

module FM_Index #(
    parameter int PAT_MAX_LEN = 150,
    parameter int RAM_DELAY_CYCLES = 8
) (
    input logic clk,
    input logic reset,
    input logic start,

    input logic [`CHAR_WIDTH*PAT_MAX_LEN-1:0] pattern,
    input logic [$clog2(PAT_MAX_LEN+1)-1:0] pat_len_in,

    output logic ram_req,
    input logic [`IDX_WIDTH-1:0] ram_data,
    output logic [31:0] ram_addr,

    output logic done,
    output logic fail,

    output logic [`IDX_WIDTH-1:0] l_out,
    output logic [`IDX_WIDTH-1:0] r_out
);

localparam int PAT_IDX_W = $clog2(PAT_MAX_LEN);
localparam int LOOP_COUNT_W = $clog2(PAT_MAX_LEN + 1);
localparam int RAM_WAIT_CYCLES = (RAM_DELAY_CYCLES < 1) ? 1 : RAM_DELAY_CYCLES;
localparam int RAM_WAIT_W = $clog2(RAM_WAIT_CYCLES + 1);

typedef enum logic [2:0] {
    IDLE,
    INIT,
    READ_CHAR,
    MEM_WAIT,
    CHECK,
    DONE_S,
    FAIL_S
} state_t;

typedef enum logic [2:0] {
    OP_INIT_MAGIC,
    OP_INIT_LEN,
    OP_INIT_ALPHA,
    OP_RANK_L,
    OP_RANK_R,
    OP_UPDATE
} mem_op_t;

typedef struct packed {
    logic [31:0] magic;
    logic [31:0] seq_len;
    logic [31:0] sigma_m1;
    logic [`IDX_WIDTH-1:0] l;
    logic [`IDX_WIDTH-1:0] r;
    logic [`IDX_WIDTH-1:0] rank_l;
    logic [`IDX_WIDTH-1:0] rank_r;
    logic [PAT_IDX_W-1:0] pat_idx;
    logic [LOOP_COUNT_W-1:0] loop_count;
    mem_op_t mem_op;
    logic [RAM_WAIT_W-1:0] mem_wait;
} search_t;

function automatic logic [31:0] occ_addr(
    input logic [`CHAR_WIDTH-1:0] char,
    input logic [31:0] row,
    input logic [31:0] sigma_m1
);
    begin
        // Read from occ array in RAM (NOTE: char is 1-based index, row and RAM is 0-based)
        // File layout:
        //   header[0..2], counts[0..sigma_m1-1], occ[row * sigma_m1 + col]
        occ_addr = `HEADER_WORDS + sigma_m1 + (row * sigma_m1) + ({29'd0, char} - 32'd1);
    end
endfunction

function automatic logic [31:0] c_arr_addr(
    input logic [`CHAR_WIDTH-1:0] char
);
    begin
        // Read from count array in RAM (char is 1-based index, RAM is 0-based)
        // header[0..2] are reserved, counts start immediately after the header
        c_arr_addr = `HEADER_WORDS + ({29'd0, char} - 32'd1);
    end
endfunction

state_t state, next_state;
search_t cur, nxt;

// Logging
`ifdef VERILATOR
always_ff @(negedge clk) begin
    case (state)
    INIT: $display("INIT");
    READ_CHAR: $display("READ_CHAR c=%d", char);
    MEM_WAIT: $display("MEM_WAIT wait=%0d op=%0d", cur.mem_wait, cur.mem_op);
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

    INIT: next_state = MEM_WAIT;

    READ_CHAR: begin
        if (char == 0) begin
            if (cur.loop_count == 0)
                // End of input: the remaining padding is all zeros.
                next_state = CHECK;
            else
                // Unexpected zero before the pattern is fully consumed.
                next_state = FAIL_S;
        end else begin
            next_state = MEM_WAIT;
        end
    end

    MEM_WAIT: begin
        if (cur.mem_wait != 0) begin
            next_state = MEM_WAIT;
        end else begin
            case (cur.mem_op)
            OP_INIT_MAGIC: begin
                if (ram_data != INDEX_MAGIC)
                    next_state = FAIL_S;
                else
                    next_state = MEM_WAIT;
            end

            OP_INIT_LEN: next_state = MEM_WAIT;
            OP_INIT_ALPHA: next_state = READ_CHAR;
            OP_RANK_L: next_state = MEM_WAIT;
            OP_RANK_R: next_state = MEM_WAIT;
            OP_UPDATE: next_state = CHECK;
            default: next_state = IDLE;
            endcase
        end
    end

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
    ram_req = 1'b0;
    case (state)
    INIT: begin
        ram_req = 1'b1;
        ram_addr = 32'd0;
    end

    READ_CHAR: begin
        if (char != 0) begin
            ram_req = 1'b1;
            ram_addr = occ_addr(char, cur.l, cur.sigma_m1);
        end
    end

    MEM_WAIT: begin
        if (cur.mem_wait == 0) begin
            case (cur.mem_op)
            OP_INIT_MAGIC: begin
                if (ram_data != INDEX_MAGIC) begin
                    ram_req = 1'b0;
                    ram_addr = 32'd0;
                end else begin
                    ram_req = 1'b1;
                    ram_addr = 32'd1;
                end
            end

            OP_INIT_LEN: begin
                ram_req = 1'b1;
                ram_addr = 32'd2;
            end

            OP_RANK_L: begin
                ram_req = 1'b1;
                ram_addr = occ_addr(char, cur.r, cur.sigma_m1);
            end

            OP_RANK_R: begin
                ram_req = 1'b1;
                ram_addr = c_arr_addr(char);
            end

            default: begin
                ram_req = 1'b0;
                ram_addr = 32'd0;
            end
            endcase
        end
    end

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
        nxt = cur;
        nxt.mem_op = OP_INIT_MAGIC;
        nxt.mem_wait = RAM_WAIT_W'(RAM_WAIT_CYCLES);
    end

    READ_CHAR: begin
        if (char != 0) begin
            nxt.loop_count = cur.loop_count - 1'b1;
            nxt.mem_op = OP_RANK_L;
            nxt.mem_wait = RAM_WAIT_W'(RAM_WAIT_CYCLES);
        end
    end

    MEM_WAIT: begin
        if (cur.mem_wait != 0) begin
            nxt.mem_wait = cur.mem_wait - 1'b1;
        end else begin
            case (cur.mem_op)
            OP_INIT_MAGIC: begin
                if (ram_data != INDEX_MAGIC) begin
                    nxt = cur;
                end else begin
                    nxt.mem_op = OP_INIT_LEN;
                    nxt.mem_wait = RAM_WAIT_W'(RAM_WAIT_CYCLES);
                end
            end

            OP_INIT_LEN: begin
                nxt.seq_len = ram_data;
                nxt.mem_op = OP_INIT_ALPHA;
                nxt.mem_wait = RAM_WAIT_W'(RAM_WAIT_CYCLES);
            end

            OP_INIT_ALPHA: begin
                nxt.sigma_m1 = ram_data;
                nxt.l = `IDX_WIDTH'd0;
                nxt.r = cur.seq_len;
                nxt.loop_count = pat_len_in;
                nxt.pat_idx = PAT_IDX_W'(PAT_MAX_LEN - 1);
                nxt.mem_op = OP_INIT_MAGIC;
            end

            OP_RANK_L: begin
                nxt.rank_l = ram_data; // Occ[char][l];
                nxt.mem_op = OP_RANK_R;
                nxt.mem_wait = RAM_WAIT_W'(RAM_WAIT_CYCLES);
            end

            OP_RANK_R: begin
                nxt.rank_r = ram_data; // Occ[char][r];
                nxt.mem_op = OP_UPDATE;
                nxt.mem_wait = RAM_WAIT_W'(RAM_WAIT_CYCLES);
            end

            OP_UPDATE: begin
                nxt.l = ram_data + cur.rank_l; // C_arr[char] + rank_l;
                nxt.r = ram_data + cur.rank_r; // C_arr[char] + rank_r;
                nxt.mem_op = OP_INIT_MAGIC;
            end

            default: nxt = cur;
            endcase
        end
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
