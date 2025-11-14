
// `include "sbox.v" 
// uncomment this line once sbox is implemented

module roundkeygen ( 
    input  wire       clk,      
    input  wire       rst_n,
    input  wire       [255:0] init_key,
    input  wire       advance,
    output reg       [127:0] round_key,
    output reg       round_key_valid


);

reg [6:0]     count;
reg [3:0]     i;

localparam  IDLE = 1'd0;
localparam  EXPAND = 1'd1;
reg phase;

// key register array
reg [31:0] key_buf [7:0];
reg [31:0] new_word;


// last word rotation
    function automatic [31:0] rotword(input [31:0] word);
        begin
            rotword = {word[23:0], word[31:24]};
        end
    endfunction
            

// run through sbox
    function automatic [31:0] subword(input [31:0] word);
        begin
            subword[31:24] = sbox(word[31:24]);
            subword[23:16] = sbox(word[23:16]);
            subword[15:8] = sbox(word[15:8]);
            subword[7:0] = sbox(word[7:0]);
        end
    endfunction

    function automatic [7:0] sbox(input [7:0] word);
        begin  
        // NOTE: for top-level integration, replace this with sbox module. see test/roundkeygen branch for module without dependencies
        end 
    endfunction


// xor round constant
    wire [31:0] rcon [7:0];

    assign rcon[0] = 32'h01000000;
    assign rcon[1] = 32'h02000000;
    assign rcon[2] = 32'h04000000;
    assign rcon[3] = 32'h08000000;
    assign rcon[4] = 32'h10000000;
    assign rcon[5] = 32'h20000000;
    assign rcon[6] = 32'h40000000;
    assign rcon[7] = 32'h80000000;


// main logic

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        for (i = 0; i < 8; i = i + 1) begin
            key_buf[i] <= 32'h0;
        end
        count <= 0;
        phase <= IDLE;
        new_word <= 32'h0;
        round_key <= 128'h0;
        round_key_valid <= 0;
    end 

    else begin
        case (phase)
            IDLE: begin
                if (advance) begin
                    for (i = 0; i < 8; i = i + 1) begin
                        key_buf[i] <= init_key[255 - (32*i) -: 32];
                    end
                    count <= 0;
                    phase <= EXPAND;
                end
            end


            EXPAND: begin
                if (count == 0) begin 
                    round_key <= init_key[255:128];
                    round_key_valid <= 1;
                    count <= 8;
                end else if (count < 63) begin 

                    for (i = 0; i < 7; i = i + 1)
                        key_buf[i] <= key_buf[i+1];
                    if (count % 8 == 0) begin
                        key_buf[7] <= key_buf[0] ^ subword(rotword(key_buf[7])) ^ rcon [(count-8)/8];
                    end
                    else if (count % 8 == 4) begin
                        key_buf[7] <= key_buf[0] ^ subword(key_buf[7]);
                    end
                    else begin
                        key_buf[7] <= key_buf[0] ^ key_buf[7];
                    end 


                    if (count % 4 == 0) begin
                        round_key <= {key_buf[4], key_buf[5], key_buf[6], key_buf[7]};
                        round_key_valid <= 1;
                    end
                    else begin
                        round_key_valid <= 0;
                    end

                    count <= count + 1;
                end else begin
                    phase <= IDLE;
                    round_key_valid <= 0;
                end

            end
        endcase
    end
end 
endmodule