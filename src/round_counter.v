module round_counter (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       start,      // initializes counter by resetting round and flags
    input  wire       advance,    // advance one round
    output reg  [3:0] round,
    output reg        is_final,
    output reg        done
);

    always @(posedge clk or negedge rst_n)
    begin
        if (!rst_n || start) begin
            round <= '0;
            is_final <= '0;
            done <= '0;
        end else begin
            if (advance) begin
                round <= round + 4'b0001;
            end

            // round still has old value because of non-blocking assignment
            // so must check next round value to determine flag signal
            if (round + 1 == 4'b1110) begin
                is_final <= 1;
            end else if (round + 1 == 4'b1111) begin
                done <= 1;
            end
        end
    end

endmodule