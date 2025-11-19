module aes_state(
    input  wire         clk,
    input  wire         rst_n,
    input  wire         mode,         // 0 = load plaintext, 1 = update from datapath
    input  wire [7:0]   din,          // byte input during plaintext load
    input  wire         valid,        // high when din is valid
    input  wire [5:0]   byte_idx,     // <-- from top-level
    input  wire         last_byte,    // <-- from top-level (byte_idx == 15)
    input  wire [127:0] dnext,        // next state value from AES round logic
    input  wire         wen,          // write enable for updating during rounds
    output reg  [127:0] state,        // current AES state
    output reg          ready         // high for one cycle after full plaintext loaded
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= 128'd0;
            ready <= 1'b0;
        end else begin
            if (mode == 1'b0 && valid) begin
                // load plaintext byte into proper position
                state[127 - 8*(byte_idx - 1)-: 8] <= din;
                // pulse ready on last byte
                if (last_byte)
                    ready <= last_byte;

            end else if (mode == 1'b1 && wen) begin
                // update whole state during rounds
                state <= dnext;
            end
        end
    end

endmodule
