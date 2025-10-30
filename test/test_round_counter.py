import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_round_counter(dut):
    dut._log.info("Start round counter testing")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")

    # Reset
    dut.rst_n.value = 0
    dut.advance.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    dut._log.info("Test project behavior")

    #--------------------------------------------------------------------------------#

    dut._log.info("Test `advance` functionality")

    dut.advance.value = 1

    # Wait for `advance` to stabilize
    await ClockCycles(dut.clk, 1)

    for i in range(1, 15):
        # Wait for `round`'s previous value to stabilize
        await ClockCycles(dut.clk, 1)

        assert dut.round.value == i, f"Expected round == {i}, got round == {dut.round.value}"
        assert dut.done.value == 0, "`done` flag unexpectedly high"
        
        if (i < 14):
            assert dut.is_final.value == 0, "`is_final flag high when it's not the final round"    

    #--------------------------------------------------------------------------------#

    dut._log.info("Test `is_final` flag")

    # `round` should already have value of 14
    assert dut.is_final.value == 1, "`is_final` flag failed"
    assert dut.done.value == 0, "`done` flag unexpectedly high"

    #--------------------------------------------------------------------------------#

    dut._log.info("Test `done` flag and counter resetting after incrementing past 14")

    # Wait for `round` to increment past 14
    await ClockCycles(dut.clk, 1)

    assert dut.done.value == 1, "`done` flag failed"
    assert dut.is_final.value == 0, "`is_final flag high when it's not the final round"    
    assert dut.round.value == 0, "`round` failed to reset after incrementing past 14"

    #--------------------------------------------------------------------------------#

    dut._log.info("Test counter stops incrementing when `advance` goes low")
    
    # `advance` is still high, let counter increment until `round` is 13
    await ClockCycles(dut.clk, 13)

    dut.advance.value = 0
    # Wait for `advance` to stabilize, round should increment to 14 in the meanwhile
    await ClockCycles(dut.clk, 1)

    last_updated_value = dut.round.value

    assert dut.is_final.value == 1, "is_final flag low when it should be high"

    # If counter failed to stop incrementing, `done` flag would be high
    await ClockCycles(dut.clk, 1)
    assert dut.done.value == 0, "done flag high when it should be low"

    await ClockCycles(dut.clk, 10)
    assert dut.round.value == last_updated_value, "Counter continued incrementing despite `advance` being low"
    
