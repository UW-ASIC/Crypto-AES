

import cocotb
from cocotb.triggers import Timer
import random


def state_to_matrix(state_int):
    """Convert 128-bit integer to 4x4 byte matrix (column-major order)."""
    matrix = [[0 for _ in range(4)] for _ in range(4)]
    for col in range(4):
        for row in range(4):
            byte_index = (col * 32) + (row * 8)
            matrix[row][col] = (state_int >> byte_index) & 0xFF
    return matrix


def matrix_to_state(matrix):
    """Convert 4x4 byte matrix to 128-bit integer (column-major order)."""
    state = 0
    for col in range(4):
        for row in range(4):
            byte_index = (col * 32) + (row * 8)
            state |= (matrix[row][col] & 0xFF) << byte_index
    return state


def shift_rows_reference(input_state):
    """Python reference model for AES ShiftRows operation."""
    matrix = state_to_matrix(input_state)
    shifted = [[0 for _ in range(4)] for _ in range(4)]
    
    # Row 0: no shift
    # Row 1: shift left by 1
    # Row 2: shift left by 2
    # Row 3: shift left by 3
    for row in range(4):
        for col in range(4):
            shifted[row][col] = matrix[row][(col + row) % 4]
    
    return matrix_to_state(shifted)


def extract_row(state_int, row):
    """Extract a specific row from the state as a list of 4 bytes."""
    matrix = state_to_matrix(state_int)
    return matrix[row]


def print_state_matrix(state_int, label="State"):
    """Pretty print state as 4x4 hex matrix."""
    matrix = state_to_matrix(state_int)
    print(f"\n{label}:")
    for row in matrix:
        print("  " + " ".join(f"{byte:02x}" for byte in row))


@cocotb.test()
async def test_known_vector_1(dut):
    """Test with NIST FIPS-197 example (before ShiftRows)."""
    dut._log.info("Test: NIST FIPS-197 known vector")
    
    # Example from NIST FIPS-197 Appendix B (state before ShiftRows)
    # Input state (column-major):
    # d4 e0 b8 1e
    # bf b4 41 27
    # 5d 52 11 98
    # 30 ae f1 e5
    
    input_val = (
        0x30 | (0x5d << 8) | (0xbf << 16) | (0xd4 << 24) |
        (0xae << 32) | (0x52 << 40) | (0xb4 << 48) | (0xe0 << 56) |
        (0xf1 << 64) | (0x11 << 72) | (0x41 << 80) | (0xb8 << 88) |
        (0xe5 << 96) | (0x98 << 104) | (0x27 << 112) | (0x1e << 120)
    )
    
    # Expected output after ShiftRows (rows shift left):
    # d4 e0 b8 1e  <- row 0: no shift
    # 52 11 98 5d  <- row 1: shift left 1
    # 41 27 bf b4  <- row 2: shift left 2
    # 1e d4 e0 b8  <- row 3: shift left 3
    
    expected_val = shift_rows_reference(input_val)
    
    dut.a.value = input_val
    await Timer(1, units='ns')
    
    if dut.b.value != expected_val:
        dut._log.error(f"NIST vector failed!")
        print_state_matrix(input_val, "Input")
        print_state_matrix(int(dut.b.value), "Got")
        print_state_matrix(expected_val, "Expected")
        assert False, "NIST test vector failed"
    else:
        dut._log.info("NIST vector passed!")


@cocotb.test()
async def test_sequential_bytes(dut):
    """Test with sequential byte pattern to make shifts obvious."""
    dut._log.info("Test: Sequential bytes 0x00-0x0F")
    
    # Input: 
    # 00 04 08 0c
    # 01 05 09 0d
    # 02 06 0a 0e
    # 03 07 0b 0f
    
    input_val = 0
    for col in range(4):
        for row in range(4):
            byte_val = col * 4 + row
            byte_index = (col * 32) + (row * 8)
            input_val |= byte_val << byte_index
    
    expected_val = shift_rows_reference(input_val)
    
    dut.a.value = input_val
    await Timer(1, units='ns')
    
    if dut.b.value != expected_val:
        dut._log.error("Sequential byte test failed!")
        verify_row_by_row(dut, input_val, expected_val)
        assert False, "Sequential byte test failed"
    else:
        dut._log.info("Sequential byte test passed!")


@cocotb.test()
async def test_all_zeros(dut):
    """Test with all zeros."""
    dut._log.info("Test: All zeros")
    
    dut.a.value = 0
    await Timer(1, units='ns')
    
    assert dut.b.value == 0, "All zeros should produce all zeros"
    dut._log.info("All zeros test passed!")


@cocotb.test()
async def test_all_ones(dut):
    """Test with all ones."""
    dut._log.info("Test: All ones")
    
    input_val = (1 << 128) - 1
    dut.a.value = input_val
    await Timer(1, units='ns')
    
    # All ones should remain all ones after shifting
    assert dut.b.value == input_val, "All ones should produce all ones"
    dut._log.info("All ones test passed!")


@cocotb.test()
async def test_single_byte_per_row(dut):
    """Test with one non-zero byte in each row to verify exact positions."""
    dut._log.info("Test: Single byte per row")
    
    # Set byte 0xAA in different columns for each row
    # Row 0, Col 0: 0xAA
    # Row 1, Col 1: 0xBB
    # Row 2, Col 2: 0xCC
    # Row 3, Col 3: 0xDD
    
    input_val = (0xAA | (0xBB << 8) | (0xCC << 16) | (0xDD << 24) |
                 (0xBB << 40) | (0xCC << 80) | (0xDD << 120))
    
    expected_val = shift_rows_reference(input_val)
    
    dut.a.value = input_val
    await Timer(1, units='ns')
    
    if dut.b.value != expected_val:
        dut._log.error("Single byte per row test failed!")
        verify_row_by_row(dut, input_val, expected_val)
        assert False, "Single byte per row test failed"
    else:
        dut._log.info("Single byte per row test passed!")


@cocotb.test()
async def test_cyclic_property(dut):
    """Test that applying ShiftRows 4 times returns to original (cyclic property)."""
    dut._log.info("Test: Cyclic property (4 shifts = identity)")
    
    input_val = 0x0123456789ABCDEF_FEDCBA9876543210
    
    current = input_val
    for i in range(4):
        dut.a.value = current
        await Timer(1, units='ns')
        current = int(dut.b.value)
    
    if current != input_val:
        dut._log.error(f"Cyclic property failed!")
        dut._log.error(f"Original: {hex(input_val)}")
        dut._log.error(f"After 4x: {hex(current)}")
        assert False, "4 applications of ShiftRows should return to original"
    else:
        dut._log.info("Cyclic property test passed!")


@cocotb.test()
async def test_randomized(dut):
    """Test with 100 random inputs against Python reference model."""
    dut._log.info("Test: 100 random inputs")
    
    random.seed(42)  # Reproducible random tests
    
    for i in range(100):
        input_val = random.randint(0, (1 << 128) - 1)
        expected_val = shift_rows_reference(input_val)
        
        dut.a.value = input_val
        await Timer(1, units='ns')
        
        if dut.b.value != expected_val:
            dut._log.error(f"Random test {i} failed!")
            verify_row_by_row(dut, input_val, expected_val)
            assert False, f"Random test {i} failed"
    
    dut._log.info("All 100 random tests passed!")


def verify_row_by_row(dut, input_val, expected_val):
    """Detailed row-by-row verification when a test fails."""
    actual_val = int(dut.b.value)
    
    print_state_matrix(input_val, "Input")
    print_state_matrix(actual_val, "Actual Output")
    print_state_matrix(expected_val, "Expected Output")
    
    for row in range(4):
        input_row = extract_row(input_val, row)
        actual_row = extract_row(actual_val, row)
        expected_row = extract_row(expected_val, row)
        
        if actual_row != expected_row:
            dut._log.error(f"\nRow {row} FAILED:")
            dut._log.error(f"  Input:    {[f'{b:02x}' for b in input_row]}")
            dut._log.error(f"  Got:      {[f'{b:02x}' for b in actual_row]}")
            dut._log.error(f"  Expected: {[f'{b:02x}' for b in expected_row]}")
            
            for col in range(4):
                if actual_row[col] != expected_row[col]:
                    dut._log.error(f"    ❌ Byte at (row={row}, col={col}): got {actual_row[col]:02x}, expected {expected_row[col]:02x}")
        else:
            dut._log.info(f"Row {row} OK: {[f'{b:02x}' for b in actual_row]}")
