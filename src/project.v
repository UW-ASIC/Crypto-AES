/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// src/project.v
module tt_um_uwasic_onboarding_aes (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);
    // For now: drive all GPIOs as outputs, and ignore uio_in.
    assign uio_oe = 8'hFF;

    // Simple mapping of your AES bus onto TT pins (you can refine later):
    //
    // ui_in[0]  -> data_in[0]
    // ui_in[7:1] + maybe uio_in[...] can form byte, control, etc.
    //
    // For a minimal placeholder, you can just hook up aes but not fully use UI:
    wire [7:0] data_in   = ui_in;     // example
    wire       valid_in  = ena;       // example: use ena as "valid"
    wire       data_ready = 1'b1;     // always ready to consume or produce
    wire       ack_ready  = 1'b1;     // always ack

    wire [7:0] data_out;
    wire       ready_in;
    wire       data_valid;
    wire       ack_valid;

    wire [1:0] module_source_id_x;
    
    aes aes_inst (
        .clk        (clk),
        .rst_n      (rst_n),
        .data_in    (data_in),
        .ready_in   (ready_in),
        .valid_in   (valid_in),
        .data_out   (data_out),
        .data_ready (data_ready),
        .data_valid (data_valid),
        .ack_ready  (ack_ready),
        .ack_valid  (ack_valid),
        .module_source_id(module_source_id_x) // ignore in TT context
    );

    // For now, just drive uo_out with the AES data_out
    // plus maybe some status bits on uio_out.
    assign uo_out  = data_out;
    assign uio_out = {6'b0, data_valid, ready_in};

    // Mark unused signals to keep lint/synthesis happy
    wire _unused = &{uio_in, 1'b0, ack_valid, module_source_id_x};

endmodule
