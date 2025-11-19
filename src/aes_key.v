module aes_key (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [7:0]  din,
    input  wire        valid,
    input  wire [5:0]  byte_idx,   // <-- from top-level
    input  wire        last_byte,  // <-- from top-level (byte_idx == 31)
    output reg [255:0] key_out,
    output reg         ready
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            key_out <= 256'd0;
            ready   <= 1'b0;
        end else if (valid) begin
            key_out[255 - 8*(byte_idx - 1) -: 8] <= din;
            if (last_byte)
                ready <= last_byte;
        end
    end

endmodule
