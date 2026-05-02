// module tb;

//     reg  clk;
//     reg  rst_n;

//     // your AES interface
//     reg  [7:0] data_in;
//     reg        valid_in;
//     wire       ready_in;
//     wire [7:0] data_out;
//     reg        data_ready;
//     wire       data_valid;

//     reg        ack_ready;
//     wire       ack_valid;
//     wire [1:0] module_source_id;

//     reg  [1:0] opcode;
//     reg  [1:0] source_id;
//     reg  [1:0] dest_id;
//     reg        encdec;
//     reg  [23:0] addr;

//     // instantiate your AES top
//     aes dut (
//         .clk(clk),
//         .rst_n(rst_n),
//         .data_in(data_in),
//         .ready_in(ready_in),
//         .valid_in(valid_in),
//         .data_out(data_out),
//         .data_ready(data_ready),
//         .data_valid(data_valid),
//         .ack_ready(ack_ready),
//         .ack_valid(ack_valid),
//         .module_source_id(module_source_id),
//         .opcode(opcode),
//         .source_id(source_id),
//         .dest_id(dest_id),
//         .encdec(encdec),
//         .addr(addr)
//     );

//     initial clk = 0;
//     always #5 clk = ~clk;  // 100 MHz

// endmodule
`default_nettype none
`timescale 1ns / 1ps

/* This testbench just instantiates the module and makes some convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

  // Dump the signals to a VCD file. You can view it with gtkwave or surfer.
  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0, tb);
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;
`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  // Replace tt_um_example with your module name:
  tt_um_uwasic_onboarding_aes dut (

      // Include power ports for the Gate Level test:
`ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
`endif

      .ui_in  (ui_in),    // Dedicated inputs
      .uo_out (uo_out),   // Dedicated outputs
      .uio_in (uio_in),   // IOs: Input path
      .uio_out(uio_out),  // IOs: Output path
      .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset
  );

endmodule