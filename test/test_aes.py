import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Constants for transaction bus
MEM_ID        = 0b00
AES_ID        = 0b10
OP_LOAD_KEY   = 0b00
OP_LOAD_TEXT  = 0b01
OP_WRITE_RESULT = 0b10   # kept for semantics, though top-level no longer gates TX on it
OP_HASH       = 0b11


# ----------------------------------------------------------------------
# Common reset
# ----------------------------------------------------------------------
async def reset_dut(dut):
    """Reset the DUT"""
    dut.aes.rst_n.value      = 0
    dut.aes.valid_in.value   = 0
    dut.aes.data_in.value    = 0
    dut.aes.data_ready.value = 0
    dut.aes.ack_ready.value  = 0
    dut.aes.opcode.value     = 0
    dut.aes.source_id.value  = 0
    dut.aes.dest_id.value    = 0
    dut.aes.encdec.value     = 0
    dut.aes.addr.value       = 0
    await ClockCycles(dut.aes.clk, 5)
    dut.aes.rst_n.value = 1
    await ClockCycles(dut.aes.clk, 2)
    dut.aes._log.info("Reset complete")


# ----------------------------------------------------------------------
# Load 32-byte key into top-level AES
# ----------------------------------------------------------------------
async def load_key(dut, key_bytes: bytes):
    """Load 32-byte (256-bit) key into AES module (new arch)"""
    assert len(key_bytes) == 32

    dut.aes._log.info(f"Loading 256-bit key: {key_bytes.hex()}")

    dut.aes.opcode.value    = OP_LOAD_KEY
    dut.aes.source_id.value = MEM_ID
    dut.aes.dest_id.value   = AES_ID
    dut.aes.addr.value      = 0x1000

    # Wait until AES is ready to accept key bytes
    for _ in range(200):
        if dut.aes.ready_in.value == 1:
            break
        await RisingEdge(dut.aes.clk)

    # Stream 32 bytes, respecting ready_in each cycle
    for i, byte in enumerate(key_bytes):
        # Wait until ready_in is high for this beat
        while dut.aes.ready_in.value == 0:
            await RisingEdge(dut.aes.clk)

        dut.aes.data_in.value  = byte
        dut.aes.valid_in.value = 1
        await RisingEdge(dut.aes.clk)

    # Deassert valid_in
    dut.aes.valid_in.value = 0
    await ClockCycles(dut.aes.clk, 2)


# ----------------------------------------------------------------------
# Load 16-byte plaintext into top-level AES
# ----------------------------------------------------------------------
async def load_plaintext(dut, plaintext_bytes: bytes):
    """Load 16-byte (128-bit) plaintext into AES module (new arch)"""
    assert len(plaintext_bytes) == 16

    dut.aes._log.info(f"Loading plaintext: {plaintext_bytes.hex()}")

    dut.aes.opcode.value    = OP_LOAD_TEXT
    dut.aes.source_id.value = MEM_ID
    dut.aes.dest_id.value   = AES_ID
    dut.aes.addr.value      = 0x2000

    # Wait for ready_in to go high
    for _ in range(200):
        if dut.aes.ready_in.value == 1:
            break
        await RisingEdge(dut.aes.clk)

    # Stream 16 bytes, respecting ready_in
    for i, byte in enumerate(plaintext_bytes):
        while dut.aes.ready_in.value == 0:
            await RisingEdge(dut.aes.clk)

        dut.aes.data_in.value  = byte
        dut.aes.valid_in.value = 1
        await RisingEdge(dut.aes.clk)

    dut.aes.valid_in.value = 0
    await ClockCycles(dut.aes.clk, 2)


# ----------------------------------------------------------------------
# Kick off encryption
# ----------------------------------------------------------------------
async def start_encryption(dut):
    """Start the AES encryption operation (new arch)"""
    dut.aes._log.info("Starting encryption...")
    dut.aes.opcode.value    = OP_HASH
    dut.aes.source_id.value = MEM_ID  # not used by RTL, but set anyway
    dut.aes.dest_id.value   = AES_ID
    dut.aes.encdec.value    = 0  # encrypt
    await ClockCycles(dut.aes.clk, 2)


# ----------------------------------------------------------------------
# Read 16-byte result (ciphertext) from AES module
# ----------------------------------------------------------------------
async def read_result(dut):
    """Read 16-byte encryption result from AES module (new arch)"""
    dut.aes._log.info("Reading result...")

    # Set up "read result" transaction (fields mostly informational now)
    dut.aes.opcode.value    = OP_WRITE_RESULT
    dut.aes.source_id.value = AES_ID
    dut.aes.dest_id.value   = MEM_ID

    # Assert READY for streaming
    dut.aes.data_ready.value = 1
    await RisingEdge(dut.aes.clk)

    result = []

    for i in range(16):
        # Wait until AES says the current byte is valid
        while dut.aes.data_valid.value == 0:
            await RisingEdge(dut.aes.clk)

        # Sample the byte when data_valid && data_ready
        byte_val = int(dut.aes.data_out.value)
        result.append(byte_val)

        dut.aes._log.info(
            f"byte[{i}] data_ready={int(dut.aes.data_ready.value)} "
            f"data_valid={int(dut.aes.data_valid.value)} "
            f"data_out=0x{byte_val:02x}"
        )

        # Move to next cycle so DUT can advance its internal byte_cnt
        await RisingEdge(dut.aes.clk)

    # Done streaming – deassert READY
    dut.aes.data_ready.value = 0

    # ACK handshake to finish the transaction
    dut.aes.ack_ready.value = 1
    for _ in range(100):
        if dut.aes.ack_valid.value == 1:
            break
        await RisingEdge(dut.aes.clk)
    await RisingEdge(dut.aes.clk)
    dut.aes.ack_ready.value = 0

    return bytes(result)


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
@cocotb.test()
async def test_aes_random_vectors(dut):
    """Test AES-256 encryption with random vectors vs PyCryptodome (new arch)"""
    dut.aes._log.info("=== AES Random Test Vector Test ===")

    clock = Clock(dut.aes.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Random key (256-bit) and plaintext (128-bit)
    key       = get_random_bytes(32)
    plaintext = get_random_bytes(16)

    dut.aes._log.info(f"Random Key:       {key.hex()}")
    dut.aes._log.info(f"Random Plaintext: {plaintext.hex()}")

    # Golden result from Python AES
    cipher   = AES.new(key, AES.MODE_ECB)
    expected = cipher.encrypt(plaintext)
    dut.aes._log.info(f"Expected Result:  {expected.hex()}")

    # Load and encrypt with hardware
    await load_key(dut, key)
    await ClockCycles(dut.aes.clk, 5)

    await load_plaintext(dut, plaintext)
    await ClockCycles(dut.aes.clk, 5)

    await start_encryption(dut)

    # Let the core run; it will move to TX_RES once done
    # (you can tune this down once you know the exact cycle count)
    await ClockCycles(dut.aes.clk, 1000)

    result = await read_result(dut)
    dut.aes._log.info(f"Hardware Result:  {result.hex()}")

    assert result == expected, \
        f"Mismatch! HW={result.hex()}, Expected={expected.hex()}"

    dut.aes._log.info("✓ Random vector test PASSED!")


@cocotb.test()
async def test_aes_simple_pattern(dut):
    """Test AES with a simple pattern (easier to debug) on new arch"""
    dut.aes._log.info("=== AES Simple Pattern Test ===")

    clock = Clock(dut.aes.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Simple patterns: key = 0x00..1F, plaintext = 0x20..2F
    key       = bytes(range(32))
    plaintext = bytes([0x20 + i for i in range(16)])

    dut.aes._log.info(f"Key:       {key.hex()}")
    dut.aes._log.info(f"Plaintext: {plaintext.hex()}")

    cipher   = AES.new(key, AES.MODE_ECB)
    expected = cipher.encrypt(plaintext)
    dut.aes._log.info(f"Expected:  {expected.hex()}")

    await load_key(dut, key)
    await ClockCycles(dut.aes.clk, 5)

    await load_plaintext(dut, plaintext)
    await ClockCycles(dut.aes.clk, 5)

    await start_encryption(dut)

    # Let AES core finish 14 rounds
    await ClockCycles(dut.aes.clk, 1000)

    result = await read_result(dut)
    dut.aes._log.info(f"Hardware:  {result.hex()}")

    assert result == expected, \
        f"Mismatch! HW={result.hex()}, Expected={expected.hex()}"

    dut.aes._log.info("✓ Simple pattern test PASSED!")
