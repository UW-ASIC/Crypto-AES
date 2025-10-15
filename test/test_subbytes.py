import cocotb
from cocotb.triggers import Timer  
from cocotb.types import Range

async def run_subbytes_case(dut, state_in, state_out):
    dut.state_in.value = state_in
    # No clock cycle because combinational logic only
    await Timer(1, "ns")
    assert dut.state_out.value == state_out, f"Expected {state_out}, received {dut.state_out.value}"

@cocotb.test()
async def test_subbytes(dut):
    dut._log.info("Start subbytes testing")

    # No reset because combinational logic only

    #--------------------------------------------------------------------------------#

    dut._log.info("Test with all 0's in state_in value")

    await run_subbytes_case(dut, 0, 0x63636363636363636363636363636363)

    #--------------------------------------------------------------------------------#

    # LogicArray type allows bitwise operations
    dut._log.info("Test with all 1's in state_in value")

    await run_subbytes_case(dut, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0x16161616161616161616161616161616)

    #--------------------------------------------------------------------------------#

    dut._log.info("Test with known values from FIPS 197 AES standard (Appendix B, rounds 1 to 3)")

    await run_subbytes_case(dut, 0x193de3bea0f4e22b9ac68d2ae9f84808, 0xd42711aee0bf98f1b8b45de51e415230)
    await run_subbytes_case(dut, 0xa49c7ff2689f352b6b5bea43026a5049, 0x49ded28945db96f17f39871a7702533b)
    await run_subbytes_case(dut, 0xaa8f5f0361dde3ef82d24ad26832469a, 0xac73cf7befc111df13b5d6b545235ab8)