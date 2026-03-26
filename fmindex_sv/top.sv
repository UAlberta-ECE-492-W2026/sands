`define CHAR_WIDTH 3
`define IDX_WIDTH 32
`define SIGMA 5
`define N 15

module top #(
    parameter int PAT_MAX_LEN = 150,
    parameter int RAM_FIFO_DEPTH = 4,
    parameter int RAM_DELAY_CYCLES = 8
) (
    input logic clk,

    input logic reset,
    input logic query_valid,
    input logic [31:0] query_id,

    input logic [`CHAR_WIDTH*PAT_MAX_LEN-1:0] query_pattern,
    input logic [$clog2(PAT_MAX_LEN+1)-1:0] query_pat_len,

    output logic query_ready,

    output logic result_valid,
    output logic result_done,
    output logic result_fail,
    output logic [31:0] result_query_id,
    output logic [`IDX_WIDTH-1:0] l_out,
    output logic [`IDX_WIDTH-1:0] r_out,

    output logic done,
    output logic fail
);

logic [31:0] addr;
logic [`IDX_WIDTH-1:0] data;
logic ram_req;

FM_Index #(
    .PAT_MAX_LEN(PAT_MAX_LEN),
    .NUM_SLOTS(RAM_FIFO_DEPTH),
    .RAM_FIFO_DEPTH(RAM_FIFO_DEPTH),
    .RAM_DELAY_CYCLES(RAM_DELAY_CYCLES)
) dut (
    .clk(clk),
    .reset(reset),
    .query_valid(query_valid),
    .query_id(query_id),
    .query_pattern(query_pattern),
    .query_pat_len(query_pat_len),
    .query_ready(query_ready),
    .ram_req(ram_req),
    .ram_addr(addr),
    .ram_data(data),
    .result_valid(result_valid),
    .result_done(result_done),
    .result_fail(result_fail),
    .result_query_id(result_query_id),
    .done(done),
    .fail(fail),
    .l_out(l_out),
    .r_out(r_out)
);

ram #(
    .RAM_FIFO_DEPTH(RAM_FIFO_DEPTH),
    .RAM_DELAY_CYCLES(RAM_DELAY_CYCLES)
) dram (
    .clk(clk),
    .request(ram_req),
    .address(addr),
    .data(data)
);

endmodule
