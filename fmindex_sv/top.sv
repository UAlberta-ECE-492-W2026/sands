`define CHAR_WIDTH 3
`define PAT_LEN 8 
`define IDX_WIDTH 32
`define SIGMA 5
`define N 15

module top(
    input logic clk,

    input logic reset,
    input logic start,

    input logic [`CHAR_WIDTH*`PAT_LEN-1:0] pattern,
    input logic [$clog2(`PAT_LEN+1)-1:0] pat_len_in,

    output logic [`IDX_WIDTH-1:0] l_out,
    output logic [`IDX_WIDTH-1:0] r_out,

    output logic done,
    output logic fail
);

logic [31:0] addr;
logic [`IDX_WIDTH-1:0] data;

FM_Index dut (
    .clk(clk),
    .reset(reset),
    .start(start),
    .pattern(pattern),
    .pat_len_in(pat_len_in),
    .ram_addr(addr),
    .ram_data(data),
    .done(done),
    .fail(fail),
    .l_out(l_out),
    .r_out(r_out)
);

ram dram (
    .clk(clk),
    .address(addr),
    .data(data)
);

endmodule
