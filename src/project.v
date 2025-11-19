// src/project.v
module tt_um_uwasic_onboarding_aes (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        ena,       // ignore or use as "chip enable"
    input  wire [7:0]  ui_in,
    output wire [7:0]  uo_out,
    input  wire [7:0]  uio_in,
    output wire [7:0]  uio_out,
    output wire [7:0]  uio_oe
);
    // Map TT IOs to your aes bus

    // data bus is on uio[*]
    wire [7:0] data_bus = uio_in;

    // outputs drive uio_out when sending, otherwise hi-Z via uio_oe
    // (you can start simple and just make aes always "output" on data bus)
    assign uio_oe  = 8'hFF;  // all driven for now; refine later

    // quick mapping for control:
    wire valid_in   = ui_in[0];
    wire ack_ready  = ui_in[2];
    wire [1:0] opcode    = { ui_in[4], ui_in[3] };
    wire [1:0] source_id = { ui_in[6], ui_in[5] };
    wire [1:0] dest_id   = { 1'b0, ui_in[7] }; // or something more sensible
    wire 
    // Outputs onto uo_out
    wire [1:0] module_source_id;
    wire       ready_in, data_valid, ack_valid;

    assign uo_out[0] = ready_in;
    assign uo_out[1] = data_valid;
    assign uo_out[2] = ack_valid;
    assign uo_out[3] = module_source_id[0];
    assign uo_out[4] = module_source_id[1];
    assign uo_out[7:5] = 3'b000;    // unused / status

    // Instantiate your AES core
    aes dut (
        .clk(clk),
        .rst_n(rst_n),

        .data_in(data_bus),
        .ready_in(ready_in),
        .valid_in(valid_in),
        .data_out(uio_out),
        .data_ready(data_ready),
        .data_valid(data_valid),

        .ack_ready(ack_ready),
        .ack_valid(ack_valid),
        .module_source_id(module_source_id),

        .opcode(opcode),
        .source_id(source_id),
        .dest_id(dest_id),
        .encdec(1'b0),         // tie off or map to some ui bit
        .addr(24'd0)           // tie off or time-multiplex
    );
endmodule
