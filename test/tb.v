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
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg mode;
  reg [7:0] din;
  reg valid;
  reg [127:0] dnext;
  reg wen;
  reg [127:0] state;
  reg ready;

`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  // Replace tt_um_example with your module name:
  aes_state user_project (

      // Include power ports for the Gate Level test:
`ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
`endif
      
      .clk(clk),
      .rst_n(rst_n),
      .mode(mode),
      .din(din),
      .valid(valid),
      .dnext(dnext),
      .wen(wen),
      .state(state),
      .ready(ready)
  );

endmodule
