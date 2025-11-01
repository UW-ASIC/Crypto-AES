module aes_state(
    input  wire         clk,
    input  wire         rst_n,
    input  wire         mode,       // 0 = load plaintext, 1 = update from datapath
    input  wire [7:0]   din,        // byte input during plaintext load
    input  wire         valid,      // high when din is valid
    input  wire [127:0] dnext,      // next state value from AES round logic
    input  wire         wen,        // write enable for updating during rounds
    output reg  [127:0] state,      // current AES state
    output reg          ready       // high for one cycle after full plaintext loaded
);

    reg [3:0] current_byte_number; // 0 to 15 to count 16 total bytes

    always @(posedge clk or negedge rst_n)
    begin
        if (!rst_n) begin
            current_byte_number <= '0;
            state <= '0;
            ready <= '0;
        end
        else begin
            if (mode == 0 && valid == 1) begin // Mode 0: Load in plain text from `din`
                if (current_byte_number == 15) begin
                    ready <= 1;
                    // No need to reset current_byte_number because
                    // it will automatically overflow to 0 after 15
                end else begin
                    ready <= 0;
                end

                // Load in bytes from MSB (left) to LSB (right)
                state[127 - 8*current_byte_number -: 8] <= din[7:0];
                current_byte_number <= current_byte_number + 1;
            end else if (mode == 1 && wen == 1) begin // Mode 1: Update state with `dnext`
                ready <= 0;
                state[127:0] <= dnext[127:0];
            end
        end
    end

endmodule