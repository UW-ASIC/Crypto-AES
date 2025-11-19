module aes_round (
    input wire [127:0] state_in ,   // from textloader
    input wire [127:0] key_in ,     // or a round_key_reg if you iterate keys
    input wire [5:0] round ,   // which round we’re in
    output reg [127:0] state_out
);
   
    addRoundKey ark (
        .state_in(state_in),
        .round_key(key_in),
        .state_out(state_in)
    );

    subbytes sb (
        .clk(clk),
        .rst_n(rsn_n),
        .start(start),
        .state_in(state_in),
        .state_out(state_in),
        .done(done)
    );

    shiftrows sr (
        .a(state_in),
        .b(state_in)
    );

    mixcolumns mc (
        .state_in(state_in),
        .final_round(round == 14),
        .state_out(state_in)
    );

endmodule