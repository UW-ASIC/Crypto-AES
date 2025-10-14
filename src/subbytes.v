`default_nettype none

module subbytes (
    input  wire         clk,      
    input  wire         rst_n,
    input  wire [127:0] state_in,
    output wire [127:0] state_out
);

    // replace each byte in state_in using
    // corresponding sbox values
    genvar i;
    generate
        for ( i = 0; i < 16; i = i + 1 )
        begin
            sbox sbox_inst( 
                state_in[8*i +: 8], 
                state_out[8*i +: 8] 
            );
        end
    endgenerate

endmodule