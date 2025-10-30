module round_counter (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       advance,    // advance one round
    output reg  [3:0] round,
    output reg        is_final,
    output reg        done
);

    // Use combinational logic to determine
    // next values of `round`, `is_final`, and `done`
    //
    // This handles resetting the counter after `round`
    // increments past 14 to replace need for `start` signal
    reg[3:0] next_round;
    reg next_is_final;
    reg next_done;

    always @(*)
    begin
        next_round = round;
        next_is_final = 0;
        next_done = 0;

        if (advance) begin
            if (round + 1 == 4'b1111) begin
                next_round = 0;
                next_done = 1;
            end else begin
                next_round = round + 1;

                if (round + 1 == 4'b1110) begin
                    next_is_final = 1;
                end
            end
        end
    end


    always @(posedge clk or negedge rst_n)
    begin
        if (!rst_n) begin
            round <= '0;
            is_final <= '0;
            done <= '0;
        end else begin
            round <= next_round;
            is_final <= next_is_final;
            done <= next_done;
        end
    end

endmodule