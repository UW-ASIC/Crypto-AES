
// `include "sbox.v" 
// uncomment this line once sbox is implemented



// note in case leads are checking the branch:

// originally wrote roundkeygen_old very literally with all 60 words stored in registers to keep the logic simple and correct
// roundkeygen is restructured to output keys using a shift register to cut down on register usage
// keeping both files on this branch temporarily while i write tests, but will be removing the old version later

// will be writing test cases for some of the functionality, but i wont be able to do full tests until sbox is implemented
// if you do notice any flaws with my implementation please lmk!

module roundkeygen (
    input  wire       clk,      
    input  wire       rst_n,
    input  wire       [255:0] key,
    input  wire       start,
    output reg       [127:0] round_key_out,
    output reg       round_key_valid


);

integer     count;
integer     i;

localparam  IDLE = 1'd0;
localparam  EXPAND = 1'd1;
reg phase;

// key register array
reg [31:0] buf [7:0];
reg [31:0] new_word;



// main logic

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        for (i = 0; i < 8; i = i + 1)
            buf[i] <= 32'h0;
        count <= 0;
        phase <= IDLE;
    end 

    else begin
        case (phase)
            IDLE: begin
                if (start) begin
                    for (i = 0; i < 8; i = i + 1)
                        buf[i] <= key[255 - 32*i -: 32];
                    count <= 8;
                    round_key_valid <= 0;
                    phase <= EXPAND;
                end
            end


            EXPAND: begin
                if (count % 8 == 0) begin
                    new_word <= buf[0] ^ subword(rotword(buf[7])) ^ rcon [count/8];
                end
                else if (count % 8 == 4) begin
                    new_word <= buf[0] ^ subword(buf[7]);
                end
                else begin
                    new_word <= buf[0] ^ buf[7];
                end 


                for (i = 0; i < 7; i = i + 1)
                    buf[i] <= buf[i+1];
                buf[7] <= new_word;


                if (count % 4 == 0) begin
                    round_key_out <= {buf[4], buf[5], buf[6], buf[7]};
                    round_key_valid <= 1;
                end
                else begin
                    round_key_valid <= 0;
                end


                count <= count + 1;
                if (count == 60) begin
                    phase <= IDLE;
                end

            end
        endcase
    end
end 



// last word rotation
    function automatic [31:0] rotword(input [31:0] word);
        begin
            rotword = {word[23:0], word[31:24]};
        end
    endfunction
            

// run through sbox
    function automatic [31:0] subword(input [31:0] word);
        begin
            subword = word;
        end
    endfunction
//temp function to allow testing of this file


// xor round constant
    wire [31:0] rcon [0:7];

    assign rcon[0] = 32'h01000000;
    assign rcon[1] = 32'h02000000;
    assign rcon[2] = 32'h04000000;
    assign rcon[3] = 32'h08000000;
    assign rcon[4] = 32'h10000000;
    assign rcon[5] = 32'h20000000;
    assign rcon[6] = 32'h40000000;
    assign rcon[7] = 32'h80000000;