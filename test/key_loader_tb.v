`timescale 1ns/1ps

module tb_key_loader;

    reg clk;
    reg rst_n;
    reg [7:0] din;
    reg valid;
    wire [255:0] key_out;
    wire ready;

    integer i;

    key_loader uut (
        .clk(clk),
        .rst_n(rst_n),
        .din(din),
        .valid(valid),
        .key_out(key_out),
        .ready(ready)
    );

    initial clk = 0;
    always #5 clk = ~clk;
    
    initial begin
        rst_n = 0; din = 8'h00; valid = 0;
        #20;
        rst_n = 1;

        for (i = 0; i < 32; i = i + 1) begin
            din = i;      
            valid = 1;
            #10;
            valid = 0;
            #10;
        end

        #50;

        $display("Key Out: %h", key_out);
        $display("Ready: %b", ready);

        $stop;
    end

endmodule
