module ram (
    input logic clk,
    input logic [31:0] address,

    output logic [`IDX_WIDTH-1:0] data
);

localparam int MAX_WORDS = 262144;
localparam int MAX_BYTES = MAX_WORDS * 4;

logic [`IDX_WIDTH-1:0] mem [0:MAX_WORDS-1];
int unsigned loaded_words;

initial begin
    string index_file;
    int fd;
    int unsigned bytes_read;
    byte unsigned raw [0:MAX_BYTES-1];

    if (!$value$plusargs("INDEX_BIN=%s", index_file)) begin
        index_file = "index.bin";
    end

    fd = $fopen(index_file, "rb");
    if (fd == 0) begin
        $fatal(1, "ram: could not open FM-index file '%s'", index_file);
    end

    bytes_read = $fread(raw, fd);
    $fclose(fd);

    if ((bytes_read % 4) != 0) begin
        $fatal(1, "ram: expected a whole number of u32 words in '%s', got %0d bytes", index_file, bytes_read);
    end

    if (bytes_read > MAX_BYTES) begin
        $fatal(1, "ram: '%s' is too large for the simulator memory (%0d bytes > %0d bytes)", index_file, bytes_read, MAX_BYTES);
    end

    loaded_words = bytes_read / 4;

    for (int i = 0; i < loaded_words; i++) begin
        mem[i] = `IDX_WIDTH'({
            raw[i * 4 + 3],
            raw[i * 4 + 2],
            raw[i * 4 + 1],
            raw[i * 4 + 0]
        });
    end
end

always_ff @(posedge clk) begin
    int unsigned addr_idx;

    addr_idx = address;
    if (addr_idx < loaded_words) begin
        data <= mem[addr_idx];
    end else begin
        data <= '0;
    end
end

endmodule
