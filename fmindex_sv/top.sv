`define CHAR_WIDTH 3
`define PAT_LEN 8 
`define IDX_WIDTH 4
`define SIGMA 5
`define N 8

module top(
    input logic clk,

    input logic reset,
    input logic start,

    input logic [`CHAR_WIDTH*`PAT_LEN-1:0] pattern,
    input int pat_len_in,
    input logic we
);

logic done;
logic fail;

logic [`IDX_WIDTH-1:0] l_out;
logic [`IDX_WIDTH-1:0] r_out;

logic [32:0] addr;
logic [32:0] data;

FM_Index dut (
    .clk(clk),
    .reset(reset),
    .start(start),
    .pattern(pattern),
    .pat_len_in(pat_len_in),
    .we(we),
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
