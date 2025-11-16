import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def test_add_round_key_basic(dut):
    """Simple XOR functional test for AddRoundKey module"""

    for _ in range(20):
        # 20 tests cycles on random 128-bit values
        state_in  = random.getrandbits(128)
        round_key = random.getrandbits(128)

        # Drive DUT inputs
        dut.state_in.value  = state_in
        dut.round_key.value = round_key

        await Timer(1, units="ns")

        expected = state_in ^ round_key
        got = dut.state_out.value.integer

        assert got == expected, (
            f"Mismatch: state_in={state_in:032x}, "
            f"round_key={round_key:032x}, "
            f"got={got:032x}, expected={expected:032x}"
        )

    cocotb.log.info("All random XOR checks passed!")


@cocotb.test()
async def test_add_round_key_edge_cases(dut):
    """Edge cases: all zeros, all ones, alternating bits"""

    vectors = [
        (0x0, 0x0),
        (0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0x0),
        (0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA, 0x55555555555555555555555555555555),
    ]

    for state_in, round_key in vectors:
        dut.state_in.value  = state_in
        dut.round_key.value = round_key
        await Timer(1, units="ns")
        expected = state_in ^ round_key
        assert dut.state_out.value.integer == expected, (
            f"Edge case fail: {state_in:032x} ^ {round_key:032x}"
        )