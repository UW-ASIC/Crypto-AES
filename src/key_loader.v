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
                key_out <= {key_out[247:0], din};
                if (byte_count == 6'd31) begin
                // 32nd byte arrived this cycle: assert ready and reset counter
                    ready      <= 1'b1;
                    byte_count <= 6'd0;
                end else begin
                    byte_count <= byte_count + 6'd1;
                end
            end else begin
                // ensure ready is only one clock cycle
                ready <= 1'b0;
            end
        end
    end

endmodule