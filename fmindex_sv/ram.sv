module ram (
    input logic clk,
    input logic [32:0] address,

    output logic [32:0] data,
);

// C table
logic [`IDX_WIDTH-1:0] C_arr [0:`SIGMA-2] = {`IDX_WIDTH'd1, `IDX_WIDTH'd4, `IDX_WIDTH'd5, `IDX_WIDTH'd6};

// Occ table
logic [`IDX_WIDTH-1:0] Occ [0:`SIGMA-2][0:`N] = {
    {`IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd2, `IDX_WIDTH'd2, `IDX_WIDTH'd2, `IDX_WIDTH'd3}, // A
    {`IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1}, // C
    {`IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1}, // G
    {`IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd0, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd1, `IDX_WIDTH'd2, `IDX_WIDTH'd2}  // T
};

always_ff @(posedge clk) begin
    if (address <= 4)
        data = C_arr[address];
    else
        data = Occ[(address - 4) % 4][(address - 4) / 4];
end

endmodule
