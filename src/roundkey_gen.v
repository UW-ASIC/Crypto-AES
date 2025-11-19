module roundkeygen_1lane (
    input  wire        clk,
    input  wire        rst_n,

    // Sliding window {w0..w7} from core
    input  wire [31:0] w0, w1, w2, w3,
    input  wire [31:0] w4, w5, w6, w7,
    input  wire [2:0]  rcon_idx_in,
    input  wire        use_rcon_in,   // AES-256: 1 for i%8==0, 0 for i%8==4

    input  wire        start,         // pulse: compute next quartet
    output reg  [31:0] w8, w9, w10, w11,
    output reg  [2:0]  rcon_idx_out,
    output reg         use_rcon_out,
    output reg         done,

    // shared S-box
    output reg  [7:0]  sbox_in,
    input  wire [7:0]  sbox_out
);

    // FSM state
    reg        active;
    reg        phase;        // 0 = issue, 1 = capture
    reg [2:0]  idx;          // 0..3

    reg [31:0] src_word;

    reg [31:0] sub_word;        // registered
    reg [31:0] sub_word_next;   // next-state

    reg [2:0]  rcon_idx;
    reg        use_rcon;

    // Rcon table
    wire [31:0] rcon [0:7];
    assign rcon[0] = 32'h01_00_00_00;
    assign rcon[1] = 32'h02_00_00_00;
    assign rcon[2] = 32'h04_00_00_00;
    assign rcon[3] = 32'h08_00_00_00;
    assign rcon[4] = 32'h10_00_00_00;
    assign rcon[5] = 32'h20_00_00_00;
    assign rcon[6] = 32'h40_00_00_00;
    assign rcon[7] = 32'h80_00_00_00;

    function automatic [31:0] rotword (input [31:0] w);
        rotword = {w[23:0], w[31:24]};
    endfunction

    // local temps (purely combinational inside a cycle)
    reg [31:0] t, k8, k9, k10, k11;
    /* verilator lint_off BLKSEQ */
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            active        <= 1'b0;
            phase         <= 1'b0;
            idx           <= 3'd0;
            sub_word      <= 32'd0;
            src_word      <= 32'd0;
            rcon_idx      <= 3'd0;
            use_rcon      <= 1'b1;
            w8            <= 32'd0;
            w9            <= 32'd0;
            w10           <= 32'd0;
            w11           <= 32'd0;
            rcon_idx_out  <= 3'd0;
            use_rcon_out  <= 1'b1;
            done          <= 1'b0;
            sbox_in       <= 8'h00;
        end else begin
            // defaults
            done          <= 1'b0;
            sub_word_next =  sub_word;  // start from current value

            if (start && !active) begin
                // start new quartet
                active        <= 1'b1;
                phase         <= 1'b0;
                idx           <= 3'd0;
                sub_word_next = 32'd0;

                rcon_idx      <= rcon_idx_in;
                use_rcon      <= use_rcon_in;
                src_word      <= use_rcon_in ? rotword(w7) : w7;

            end else if (active) begin
                if (!phase) begin
                    // ISSUE S-box input
                    case (idx)
                        3'd0: sbox_in <= src_word[31:24];
                        3'd1: sbox_in <= src_word[23:16];
                        3'd2: sbox_in <= src_word[15:8];
                        default: sbox_in <= src_word[7:0];  // idx == 3
                    endcase
                    phase <= 1'b1;

                end else begin
                    // CAPTURE S-box output into *next* sub_word
                    case (idx)
                        3'd0: sub_word_next[31:24] = sbox_out;
                        3'd1: sub_word_next[23:16] = sbox_out;
                        3'd2: sub_word_next[15:8]  = sbox_out;
                        default: sub_word_next[7:0] = sbox_out;  // idx == 3
                    endcase

                    if (idx == 3'd3) begin
                        // now have full SubWord in sub_word_next
                        t = sub_word_next;
                        if (use_rcon)
                            t = t ^ rcon[rcon_idx];

                        k8  = w0 ^ t;
                        k9  = w1 ^ k8;
                        k10 = w2 ^ k9;
                        k11 = w3 ^ k10;

                        w8  <= k8;
                        w9  <= k9;
                        w10 <= k10;
                        w11 <= k11;

                        rcon_idx_out <= use_rcon ? (rcon_idx + 3'd1) : rcon_idx;
                        use_rcon_out <= ~use_rcon;

                        active <= 1'b0;
                        phase  <= 1'b0;
                        done   <= 1'b1;

                    end else begin
                        idx   <= idx + 3'd1;
                        phase <= 1'b0;
                    end
                end
            end

            // commit next-state for sub_word
            sub_word <= sub_word_next;
        end
    end
    /* verilator lint_on BLKSEQ */
    wire _unused = &{w4, w5, w6};

endmodule
