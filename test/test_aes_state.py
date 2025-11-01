import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import LogicArray
from cocotb.types import Range

async def load_byte(clk, dut, byte, expected_state):
    dut.din.value = byte

    dut.valid.value = 1
    await ClockCycles(clk, 1)
    dut.valid.value = 0

    # Wait for `state` to update with new byte loaded in
    await ClockCycles(clk, 1)

    assert dut.state.value == expected_state, f"Expected `state` to be {expected_state}, received {dut.state.value}"

@cocotb.test()
async def test_aes_state(dut):

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 0
    dut.din.value = 0
    dut.valid.value = 0
    dut.dnext.value = 0
    dut.wen.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test AES State behavior")

    #----------------------------------------------------------#

    dut._log.info("Test Mode 0: Load plain text")
    dut.mode.value = 0

    await ClockCycles(dut.clk, 1)

    length = Range(127, "downto", 0)

    text = LogicArray(0x3243f6a8885a308d31319002e0370734, length)

    # `expected_state` will be updated inside loop
    # as bytes are loaded in
    expected_state = LogicArray(0, length)

    for i in range(16):
        # Expecting to load in bytes from MSB (left) to LSB (right)
        byte = (text[127 - 8*i: 128 - 8*(i + 1)])
        expected_state |= LogicArray(byte.integer << (128 - 8*(i + 1)), length)

        await load_byte(dut.clk, dut, byte, expected_state)

        if (i != 15):
            assert dut.ready.value == 0, "`ready` flag unexpectedly asserted" 

    dut._log.info("Test `ready` flag is asserted after text is fully loaded")
    assert dut.ready.value == 1, "`ready` flag failed to assert after text was loaded"
    
    #----------------------------------------------------------#

    dut._log.info("Test bytes are not loaded in when `valid == 0")

    dut.valid.value = 0
    dut.din.value = 0

    await ClockCycles(dut.clk, 18)

    assert dut.state.value == text, "State unexpectedly loaded in bytes when `valid == 0`"

    #----------------------------------------------------------#

    dut._log.info("Test Mode 1: Update from datapath")
    dut.mode.value = 1
    dut.valid.value = 0

    updated_state = LogicArray(0x736203afe30a99efc618223436b21c22, length)
    dut.dnext.value = updated_state

    await ClockCycles(dut.clk, 1) 

    dut._log.info("Test `state` is not overwritten when `wen == 0`")
    assert dut.state.value == text, "State unexpectedly overwritten when `wen == 0`"

    dut._log.info("Test `state` is overwritten with updated state when `wen == 1`")
    dut.wen.value = 1

    # Wait one cycle for `wen` and `dnext` to update
    # and one cycle for `state` to update
    await ClockCycles(dut.clk, 2)
    
    assert dut.state.value == updated_state, f"Expected `state` to be {updated_state}, received {dut.state.value}"

    dut._log.info("Test `ready` flag is not asserted after overwriting `state`")
    assert dut.ready.value == 0, "`ready` flag unexpectedly asserted" 

    dut._log.info("AES State test complete")

