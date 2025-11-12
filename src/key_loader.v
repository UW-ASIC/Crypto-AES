module key_loader(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [7:0]  din,
    input  wire        valid,
    output reg  [255:0] key_out,
    output reg         ready
);

    reg [5:0] byte_count;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            key_out    <= 256'b0;
            byte_count <= 6'd0;
            ready      <= 1'b0;
        end else begin
            if (valid && !ready) begin
                // Shift in new byte from MSB side
                key_out <= {key_out[247:0], din};
                byte_count <= byte_count + 1'b1;
                if (byte_count == 6'd31) begin
                    ready <= 1'b1;
                end
            end
        end
    end

endmodule
