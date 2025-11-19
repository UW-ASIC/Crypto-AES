//////////////////////////////
// Shift Rows Module (MSB-aligned)
// Consistent with:
//   - byte j at a[127 - 8*j -: 8]
//   - j = 4*c + r, column-major
//////////////////////////////
module shiftRows_msb (
    input  wire [127:0] a,
    output wire [127:0] b
);
    genvar r, c;
    generate
        for (c = 0; c < 4; c = c + 1) begin : col_loop
            for (r = 0; r < 4; r = r + 1) begin : row_loop
                // Byte indices (0..15)
                localparam integer J_OUT = 4*c + r;
                localparam integer J_IN  = 4*((c + r) % 4) + r;

                // MSB-first indexing: byte j at [127 - 8*j -: 8]
                assign b[127 - 8*J_OUT -: 8] = a[127 - 8*J_IN -: 8];
            end
        end
    endgenerate
endmodule
