`default_nettype none

//////////////////////////////
// Shift Rows Module
// By: Benjamin Vuong
//////////////////////////////


module shiftRows (
    
    input  wire [127:0] a,
    output wire [127:0] b

);

    genvar r, c;        // row, column
    generate

        for (c = 0; c < 4; c = c + 1) begin         : row_counter
            for (r = 0; r < 4; r = r + 1) begin     : col_counter

                // 32*c gives the least bit of a column c
                // Adding on 8*r gives the least bit of the r'th row on the column 
                localparam OUTPUT_INDEX = (32*c) + (8*r);

                // 32*( (c + r)%4 ) finds the least bit index for the cyclic-shifted input's column
                // Adding on 8*r again moves down the col., giving least bit of the r'th row on the column 
                localparam TRANSFORMED_INPUT_INDEX = 32*( (c + r)%4 ) + (8*r);

                // assign b with shiftRows(a)
                assign b[OUTPUT_INDEX +: 8] = a[TRANSFORMED_INPUT_INDEX +: 8];

            end
        end
        
    endgenerate

    

endmodule