import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from cocotb.types import LogicArray
from cocotb.types import Range

@cocotb.test()
async def test_round_counter(dut):
    dut._log.info("Start round counter testing")

    # Unsure what actual frequency is, for now set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")

    # Reset
    dut.rst_n.value = 0
    dut.start.value = 0
    dut.advance.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    dut._log.info("Test project behavior")

    #--------------------------------------------------------------------------------#

    dut._log.info("Test advance functionality")

    dut.advance.value = 1

    # Wait for advance to update
    await ClockCycles(dut.clk, 1)

    for i in range(1, 15):
        # Wait for counter's previous value to update
        await ClockCycles(dut.clk, 1)
        assert dut.round.value == i, f"Expected round == {i}, got round == {dut.round.value}"

    #--------------------------------------------------------------------------------#

    dut._log.info("Test is_final flag")

    # Wait for counter's previous value to update
    await ClockCycles(dut.clk, 1)

    assert dut.is_final.value == 1, f"is_final flag failed"

    #--------------------------------------------------------------------------------#

    dut._log.info("Test done flag")

    # Wait for counter's previous value to update
    await ClockCycles(dut.clk, 1)

    assert dut.done.value == 1, f"done flag failed"

    #--------------------------------------------------------------------------------#

    dut._log.info("Test start functionality")

    dut.start.value = 1

    # Wait one cycle for start to update, then one cycle for counter to update
    await ClockCycles(dut.clk, 2)

    assert dut.round.value == 0, f"Expected round to be 0, got {dut.round.value}"
    assert dut.is_final.value == 0, f"Expected is_final to be reset, but it's still high"
    assert dut.done.value == 0, f"Expected done to be reset, but it's still high"

    #--------------------------------------------------------------------------------#

    dut._log.info("Test counter stops incrementing when advance goes low")
    dut.rst_n.value = 0

    # Wait one cycle for rst_n to update, then one cycle for counter to update
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # advance is still high, let counter increment for a few cycles
    await ClockCycles(dut.clk, 5)
    dut.advance.value = 0

    last_updated_value = dut.round.value

    await ClockCycles(dut.clk, 5)
    assert dut.round.value == last_updated_value
