module tb;

    reg  clk;
    reg  rst_n;

    // your AES interface
    reg  [7:0] data_in;
    reg        valid_in;
    wire       ready_in;
    wire [7:0] data_out;
    reg        data_ready;
    wire       data_valid;

    reg        ack_ready;
    wire       ack_valid;
    wire [1:0] module_source_id;

    reg  [1:0] opcode;
    reg  [1:0] source_id;
    reg  [1:0] dest_id;
    reg        encdec;
    reg  [23:0] addr;

    // instantiate your AES top
    aes dut (
        .clk(clk),
        .rst_n(rst_n),
        .data_in(data_in),
        .ready_in(ready_in),
        .valid_in(valid_in),
        .data_out(data_out),
        .data_ready(data_ready),
        .data_valid(data_valid),
        .ack_ready(ack_ready),
        .ack_valid(ack_valid),
        .module_source_id(module_source_id),
        .opcode(opcode),
        .source_id(source_id),
        .dest_id(dest_id),
        .encdec(encdec),
        .addr(addr)
    );

    initial clk = 0;
    always #5 clk = ~clk;  // 100 MHz

endmodule
