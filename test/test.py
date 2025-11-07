# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_roundkeygen(dut):
    """Test AES round key generator"""

    dut._log.info("=== Starting RoundKeyGen test ===")

    # 10us clock
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # reset phase
    dut._log.info("Applying reset")
    dut.rst_n.value = 0
    dut.advance.value = 0
    dut.init_key.value = 0
    await Timer(100, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    dut._log.info("Reset released")

    # load initial key (random value for now)
    init_key = int(
        "603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4", 16
    )
    dut.init_key.value = init_key

    # pulse 'advance'
    dut.advance.value = 1
    await RisingEdge(dut.clk)
    dut.advance.value = 0
    

    # generated round keys
    valid_rounds = 0
    max_cycles = 200  # safety limit
    dut._log.info("Monitoring round keys...")

    for _ in range(max_cycles):
        await RisingEdge(dut.clk)
        if dut.round_key_valid.value:
            val = dut.round_key.value
            s = str(val).lower()
            if "x" in s or "z" in s:
                dut._log.warning(f"Round key {valid_rounds}: contains X {val}")
            else:
                key_hex = f"{val.to_unsigned():032x}"
                dut._log.info(f"Round key {valid_rounds}: {key_hex}")
            valid_rounds += 1

        if valid_rounds >= 15:
            break

    assert valid_rounds > 0, "No valid round keys produced!"
    dut._log.info(f"Test completed successfully — {valid_rounds} valid round keys observed.")
