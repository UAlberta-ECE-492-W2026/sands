module ram #(
    parameter int RAM_FIFO_DEPTH = 4,
    parameter int RAM_DELAY_CYCLES = 8
) (
    input logic clk,
    input logic request,
    input logic [31:0] address,

    output logic [`IDX_WIDTH-1:0] data
);

localparam int MAX_WORDS = 262144;
localparam int MAX_BYTES = MAX_WORDS * 4;
localparam int FIFO_DEPTH = (RAM_FIFO_DEPTH < 1) ? 1 : RAM_FIFO_DEPTH;
localparam int DELAY_STAGES = (RAM_DELAY_CYCLES < 1) ? 1 : RAM_DELAY_CYCLES;

logic [`IDX_WIDTH-1:0] mem [0:MAX_WORDS-1];
int unsigned loaded_words;

logic [31:0] pipe_addr [0:DELAY_STAGES-1];
logic pipe_valid [0:DELAY_STAGES-1];

logic [31:0] pipe_addr_n [0:DELAY_STAGES-1];
logic pipe_valid_n [0:DELAY_STAGES-1];
logic [`IDX_WIDTH-1:0] data_n;
int unsigned pending_count;
int unsigned pending_count_n;
logic overflow_n;

function automatic logic [`IDX_WIDTH-1:0] read_word(
    input logic [31:0] addr
);
    begin
        if (addr < loaded_words) begin
            read_word = mem[addr];
        end else begin
            read_word = '0;
        end
    end
endfunction

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

    data = '0;
    pending_count = 0;
    for (int i = 0; i < DELAY_STAGES; i++) begin
        pipe_valid[i] = 1'b0;
        pipe_addr[i] = '0;
    end
end

always_comb begin
    for (int i = 0; i < DELAY_STAGES; i++) begin
        pipe_valid_n[i] = 1'b0;
        pipe_addr_n[i] = '0;
    end

    data_n = data;
    pending_count_n = pending_count;
    overflow_n = 1'b0;

    if (pipe_valid[DELAY_STAGES-1]) begin
        data_n = read_word(pipe_addr[DELAY_STAGES-1]);
        pending_count_n = pending_count_n - 1;
    end

    for (int i = DELAY_STAGES-1; i > 0; i--) begin
        pipe_valid_n[i] = pipe_valid[i-1];
        pipe_addr_n[i] = pipe_addr[i-1];
    end

    if (request) begin
        if (pending_count_n < FIFO_DEPTH) begin
            pipe_valid_n[0] = 1'b1;
            pipe_addr_n[0] = address;
            pending_count_n = pending_count_n + 1;
        end else begin
            overflow_n = 1'b1;
        end
    end
end

always_ff @(posedge clk) begin
    if (overflow_n) begin
        $fatal(1, "ram: request FIFO overflow (depth=%0d, delay=%0d)", FIFO_DEPTH, DELAY_STAGES);
    end

    data <= data_n;
    pending_count <= pending_count_n;

    for (int i = 0; i < DELAY_STAGES; i++) begin
        pipe_valid[i] <= pipe_valid_n[i];
        pipe_addr[i] <= pipe_addr_n[i];
    end
end

endmodule
