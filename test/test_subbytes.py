import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

async def run_subbytes_case(clk, dut, state_in, state_out):
    dut.start.value = 1

    # `byte_in`` is loaded before `started` is asserted,
    # so `state_in` must be inputted alongside `start`
    dut.state_in.value = state_in

    await ClockCycles(clk, 1)

    dut.start.value = 0

    # Must wait 16 cycles for computation to complete
    # and 1 extra cycle for `state_out` to stabilize
    await ClockCycles(clk, 17)
    assert dut.state_out.value == state_out, f"Expected {state_out}, received {dut.state_out.value}"

@cocotb.test()
async def test_subbytes(dut):
    dut._log.info("Start subbytes testing")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())    

    dut._log.info("Reset")
    
    dut.rst_n.value = 0
    dut.start.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    #--------------------------------------------------------------------------------#

    dut._log.info("Test with all 0's in state_in value")

    await run_subbytes_case(dut.clk, dut, 0, 0x63636363636363636363636363636363)

    #--------------------------------------------------------------------------------#

    # LogicArray type allows bitwise operations
    dut._log.info("Test with all 1's in state_in value")

    await run_subbytes_case(dut.clk, dut, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0x16161616161616161616161616161616)

    #--------------------------------------------------------------------------------#

    dut._log.info("Test with known values from FIPS 197 AES standard (Appendix B, rounds 1 to 3)")

    await run_subbytes_case(dut.clk, dut, 0x193de3bea0f4e22b9ac68d2ae9f84808, 0xd42711aee0bf98f1b8b45de51e415230)
    await run_subbytes_case(dut.clk, dut, 0xa49c7ff2689f352b6b5bea43026a5049, 0x49ded28945db96f17f39871a7702533b)
    await run_subbytes_case(dut.clk, dut, 0xaa8f5f0361dde3ef82d24ad26832469a, 0xac73cf7befc111df13b5d6b545235ab8)