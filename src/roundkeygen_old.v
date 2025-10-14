
// `include "sbox.v" 
// uncomment this line once sbox is implemented

module roundkeygen (
    input  wire       clk,      
    input  wire       rst_n,
    input  wire       [255:0] key,
    output wire       [127:0] round_key_0,
    output wire       [127:0] round_key_1,
    output wire       [127:0] round_key_2,
    output wire       [127:0] round_key_3,
    output wire       [127:0] round_key_4,
    output wire       [127:0] round_key_5,
    output wire       [127:0] round_key_6,
    output wire       [127:0] round_key_7,
    output wire       [127:0] round_key_8,
    output wire       [127:0] round_key_9,
    output wire       [127:0] round_key_10,
    output wire       [127:0] round_key_11,
    output wire       [127:0] round_key_12,
    output wire       [127:0] round_key_13,
    output wire       [127:0] round_key_14,


);

integer i;

// key register array
reg [31:0] kra [0:59];

assign round_key_0 = {kra[0], kra[1], kra[2], kra[3]};
assign round_key_1 = {kra[4], kra[5], kra[6], kra[7]};
assign round_key_2 = {kra[8], kra[9], kra[10], kra[11]};
assign round_key_3 = {kra[12], kra[13], kra[14], kra[15]};
assign round_key_4 = {kra[16], kra[17], kra[18], kra[19]};
assign round_key_5 = {kra[20], kra[21], kra[22], kra[23]};
assign round_key_6 = {kra[24], kra[25], kra[26], kra[27]};
assign round_key_7 = {kra[28], kra[29], kra[30], kra[31]};
assign round_key_8 = {kra[32], kra[33], kra[34], kra[35]};
assign round_key_9 = {kra[36], kra[37], kra[38], kra[39]};
assign round_key_10 = {kra[40], kra[41], kra[42], kra[43]};
assign round_key_11 = {kra[44], kra[45], kra[46], kra[47]};
assign round_key_12 = {kra[48], kra[49], kra[50], kra[51]};
assign round_key_13 = {kra[52], kra[53], kra[54], kra[55]};
assign round_key_14 = {kra[56], kra[57], kra[58], kra[59]};



// main logic

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        for(i = 0; i < 60; i = i + 1)
            kra[i] <= 32'h0;
    end 
    else begin
        for (i = 0; i < 8; i = i + 1)
            kra[i] <= key[255 - 32*i -: 32];


        for (i = 8; i < 60; i = i + 1) begin
            if (i % 8 == 0)
                kra[i] <= kra[i-8] ^ subword(rotword(kra[i-1])) ^ rcon [i/8];
            else if (i % 8 == 4)
                kra[i] <= kra[i-8] ^ subword(kra[i-1]);
            else
                kra[i] <= kra[i-8] ^ kra[i-1];
        end 
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
            subword = word
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