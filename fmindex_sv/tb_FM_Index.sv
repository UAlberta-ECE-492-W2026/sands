`define CHAR_WIDTH 3
`define PAT_LEN 8 
`define IDX_WIDTH 4
`define SIGMA 5
`define N 8

module tb_FM_Index(
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

FM_Index dut (
    .clk(clk),
    .reset(reset),
    .start(start),
    .pattern(pattern),
    .pat_len_in(pat_len_in),
    .done(done),
    .fail(fail),
    .l_out(l_out),
    .r_out(r_out)
);

// OLD SIMULATION DATA (preserved for reference)

/*
initial begin
    clk = 0;
    forever #5 clk = ~clk;
end
*/

//initial begin
    //reset = 1;
    //start = 0;
    //pat_len_in = 0;
    //pattern = {`CHAR_WIDTH'd4, `CHAR_WIDTH'd1, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0};
    //pattern = {`CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0, `CHAR_WIDTH'd0};


    //#10

    //reset = 0;
    //start = 1;

    //#10

    //start = 0;

    //#200 $finish;
//end

endmodule
