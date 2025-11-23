import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Constants for transaction fields encoded in header byte
MEM_ID          = 0b00
AES_ID          = 0b10
OP_LOAD_KEY     = 0b00
OP_LOAD_TEXT    = 0b01
OP_WRITE_RESULT = 0b10
OP_HASH         = 0b11


def make_header(opcode: int, source_id: int, dest_id: int) -> int:
    """
    Build header byte according to the aes.v decode:

        header_byte[1:0] -> opcode
        header_byte[3:2] -> source_id
        header_byte[5:4] -> dest_id
        header_byte[7:6] -> unused/0
    """
    return ((dest_id & 0x3) << 4) | ((source_id & 0x3) << 2) | (opcode & 0x3)


async def send_header_and_payload(aes, opcode: int, source_id: int,
                                  dest_id: int, payload: bytes, addr: int):
    """
    Send one transaction:

      beat 0: header byte
      beat 1: addr[23:16]
      beat 2: addr[15:8]
      beat 3: addr[7:0]
      then:   payload bytes (if any)

    All over (data_in, valid_in, ready_in).
    """

    header = make_header(opcode, source_id, dest_id)
    beats = [
        header,
        (addr >> 16) & 0xFF,
        (addr >> 8) & 0xFF,
        addr & 0xFF,
    ]

    # Header + 3 address beats
    for b in beats:
        # wait until DUT is ready
        while aes.ready_in.value == 0:
            await RisingEdge(aes.clk)

        aes.data_in.value = b
        aes.valid_in.value = 1
        await RisingEdge(aes.clk)

    # Now header is done; deassert valid
    aes.valid_in.value = 0
    await RisingEdge(aes.clk)

    # Payload (for LOAD_KEY / LOAD_TEXT); no payload for HASH / WRITE_RESULT
    for b in payload:
        while aes.ready_in.value == 0:
            await RisingEdge(aes.clk)

        aes.data_in.value = b
        aes.valid_in.value = 1
        await RisingEdge(aes.clk)

    aes.valid_in.value = 0
    await RisingEdge(aes.clk)


# ----------------------------------------------------------------------
# Common reset
# ----------------------------------------------------------------------
async def reset_dut(dut):
    """Reset the DUT"""

    # Use inner AES instance if it exists, otherwise use top directly
    aes = getattr(dut, "aes_inst", dut)

    aes.rst_n.value      = 0
    aes.valid_in.value   = 0
    aes.data_in.value    = 0
    aes.data_ready.value = 0
    aes.ack_ready.value  = 0

    await ClockCycles(aes.clk, 5)
    aes.rst_n.value = 1
    await ClockCycles(aes.clk, 2)
    aes._log.info("Reset complete")


# ----------------------------------------------------------------------
# Load 32-byte key into top-level AES
# ----------------------------------------------------------------------
async def load_key(dut, key_bytes: bytes):
    """Load 32-byte (256-bit) key into AES module (new bus protocol)"""
    assert len(key_bytes) == 32

    aes = getattr(dut, "aes_inst", dut)

    aes._log.info(f"Loading 256-bit key: {key_bytes.hex()}")

    # Old addr was 0x1000; RTL ignores addr, but keep it for consistency
    addr = 0x001000

    await send_header_and_payload(
        aes,
        opcode=OP_LOAD_KEY,
        source_id=MEM_ID,
        dest_id=AES_ID,
        payload=key_bytes,
        addr=addr,
    )

    await ClockCycles(aes.clk, 2)


# ----------------------------------------------------------------------
# Load 16-byte plaintext into top-level AES
# ----------------------------------------------------------------------
async def load_plaintext(dut, plaintext_bytes: bytes):
    """Load 16-byte (128-bit) plaintext into AES module (new bus protocol)"""
    assert len(plaintext_bytes) == 16

    aes = getattr(dut, "aes_inst", dut)

    aes._log.info(f"Loading plaintext: {plaintext_bytes.hex()}")

    # Old addr was 0x2000; again, RTL ignores addr value
    addr = 0x002000

    await send_header_and_payload(
        aes,
        opcode=OP_LOAD_TEXT,
        source_id=MEM_ID,
        dest_id=AES_ID,
        payload=plaintext_bytes,
        addr=addr,
    )

    await ClockCycles(aes.clk, 2)


# ----------------------------------------------------------------------
# Kick off encryption
# ----------------------------------------------------------------------
async def start_encryption(dut):
    """Start the AES encryption operation (new bus protocol)"""

    aes = getattr(dut, "aes_inst", dut)

    aes._log.info("Starting encryption...")

    # HASH_OP has *no* payload: just header + 3 addr bytes.
    addr = 0x000000

    await send_header_and_payload(
        aes,
        opcode=OP_HASH,
        source_id=MEM_ID,
        dest_id=AES_ID,
        payload=b"",
        addr=addr,
    )

    # give the core a couple cycles to latch start
    await ClockCycles(aes.clk, 2)


# ----------------------------------------------------------------------
# Read 16-byte result (ciphertext) from AES module
# ----------------------------------------------------------------------
async def read_result(dut):
    """Read 16-byte encryption result from AES module (new bus protocol)"""

    aes = getattr(dut, "aes_inst", dut)

    aes._log.info("Reading result...")

    # First send WRITE_RESULT header + dummy addr
    addr = 0x000000

    await send_header_and_payload(
        aes,
        opcode=OP_WRITE_RESULT,
        source_id=AES_ID,
        dest_id=MEM_ID,
        payload=b"",
        addr=addr,
    )

    # Now the wrapper should be in TX_RES; drive data_ready to pull bytes
    aes.data_ready.value = 1
    await RisingEdge(aes.clk)

    result = []

    for i in range(16):
        # Wait until AES says the current byte is valid
        while aes.data_valid.value == 0:
            aes._log.info("WAITING...")
            await RisingEdge(aes.clk)

        byte_val = int(aes.data_out.value)
        result.append(byte_val)

        aes._log.info(
            f"byte[{i}] data_ready={int(aes.data_ready.value)} "
            f"data_valid={int(aes.data_valid.value)} "
            f"data_out=0x{byte_val:02x}"
        )

        await RisingEdge(aes.clk)

    # Done streaming – deassert READY
    aes.data_ready.value = 0

    # ACK handshake to finish the transaction
    aes.ack_ready.value = 1
    for _ in range(100):
        if aes.ack_valid.value == 1:
            break
        await RisingEdge(aes.clk)
    await RisingEdge(aes.clk)
    aes.ack_ready.value = 0

    return bytes(result)


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
@cocotb.test()
async def test_aes_random_vectors(dut):
    """Test AES-256 encryption with random vectors vs PyCryptodome (new arch)"""

    aes = getattr(dut, "aes_inst", dut)

    aes._log.info("=== AES Random Test Vector Test ===")

    clock = Clock(aes.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Random key (256-bit) and plaintext (128-bit)
    key       = get_random_bytes(32)
    plaintext = get_random_bytes(16)

    aes._log.info(f"Random Key:       {key.hex()}")
    aes._log.info(f"Random Plaintext: {plaintext.hex()}")

    # Golden result from Python AES
    cipher   = AES.new(key, AES.MODE_ECB)
    expected = cipher.encrypt(plaintext)
    aes._log.info(f"Expected Result:  {expected.hex()}")

    # Load and encrypt with hardware
    await load_key(dut, key)
    await ClockCycles(aes.clk, 5)

    await load_plaintext(dut, plaintext)
    await ClockCycles(aes.clk, 5)

    await start_encryption(dut)

    # Let the core run; tune later if needed
    await ClockCycles(aes.clk, 1000)

    result = await read_result(dut)
    aes._log.info(f"Hardware Result:  {result.hex()}")

    assert result == expected, \
        f"Mismatch! HW={result.hex()}, Expected={expected.hex()}"

    aes._log.info("✓ Random vector test PASSED!")


@cocotb.test()
async def test_aes_simple_pattern(dut):
    """Test AES with a simple pattern (easier to debug) on new arch"""

    aes = getattr(dut, "aes_inst", dut)

    aes._log.info("=== AES Simple Pattern Test ===")

    clock = Clock(aes.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    #await reset_dut(dut)

    # Simple patterns: key = 0x00..1F, plaintext = 0x20..2F
    key       = bytes(range(32))
    plaintext = bytes([0x20 + i for i in range(16)])

    aes._log.info(f"Key:       {key.hex()}")
    aes._log.info(f"Plaintext: {plaintext.hex()}")

    cipher   = AES.new(key, AES.MODE_ECB)
    expected = cipher.encrypt(plaintext)
    aes._log.info(f"Expected:  {expected.hex()}")

    await load_key(dut, key)
    await ClockCycles(aes.clk, 5)

    await load_plaintext(dut, plaintext)
    await ClockCycles(aes.clk, 5)

    await start_encryption(dut)

    await ClockCycles(aes.clk, 1000)

    result = await read_result(dut)
    aes._log.info(f"Hardware:  {result.hex()}")

    assert result == expected, \
        f"Mismatch! HW={result.hex()}, Expected={expected.hex()}"

    aes._log.info("✓ Simple pattern test PASSED!")
