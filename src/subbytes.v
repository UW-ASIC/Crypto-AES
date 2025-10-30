`default_nettype none

module subbytes (
    input wire clk,
    input wire rst_n,
    input wire start, // Asserted for one clock cycle when `state_in` is ready
    input  wire [127:0] state_in,
    output reg [127:0] state_out,
    output reg done
);

    // To reduce hardware usage, 8 bytes of data will be
    // passed in each clock cycle for 16 total cycles
    // (plus one extra cycle for `state_out` to stabilize)
    //
    // In top level module that instantiates subbytes,
    // `start` should be asserted for one cycle to begin 
    // the subbytes operation
    //
    // `state_in` must be provided when asserting `start`
    // because `byte_in` loads in first byte of `state_in` in same
    // clock cycle that `start` is high

    reg started; // Keep track of if `start` has been asserted
    reg [3:0] current_clock_cycle; // 0 to 15

    reg [7:0] byte_in;
    reg [7:0] byte_out;

    // sbox is combinational and updates instantenously
    sbox sbox_inst(byte_in, byte_out);

    always @(posedge clk or negedge rst_n) 
    begin
        if(!rst_n) begin
            started <= 0;
            done <= 0;

            current_clock_cycle <= 0;
            
            byte_in <= '0;
            // byte_out is determined by sbox

            state_out <= '0;
        end else begin
            if (start) begin
                started <= 1;
                done <= 0;

                byte_in <= state_in[7:0];

                state_out <= '0;

                current_clock_cycle <= 0;
            end

            // For each cycle, byte_in for the next cycle will be calculated
            // and state_out for the current cycle will be updated to
            // accomodate for non-blocking assignment timing delays
            if (started) begin 
                state_out[8*current_clock_cycle +: 8] <= byte_out; 

                if (current_clock_cycle == 4'b1111) begin
                    done <= 1;
                    started <= 0;

                end else begin
                    byte_in <= state_in[8*(current_clock_cycle + 1) +: 8];
                end

                current_clock_cycle <= current_clock_cycle + 1;
            end
        end
    end

endmodule