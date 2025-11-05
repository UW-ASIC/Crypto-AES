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
  reg start;
  reg advance;    // advance one round
  reg [3:0] round;
  reg is_final;
  reg done;

`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  round_counter user_project (

    // Include power ports for the Gate Level test:
    `ifdef GL_TEST
          .VPWR(VPWR),
          .VGND(VGND),
    `endif

    .clk(clk),
    .rst_n(rst_n),
    .advance(advance),
    .round(round),
    .is_final(is_final),
    .done(done)
  );

endmodule
