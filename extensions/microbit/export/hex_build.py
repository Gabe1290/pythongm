#!/usr/bin/env python3
"""Build a V1 micro:bit "combined hex" -- MicroPython firmware with a
script embedded at a fixed flash address, ready to drag onto a
factory-fresh board's MICROBIT USB drive, no prior MicroPython flash
needed (Stage X, unit X8, V1 only -- see docs/MICROBIT_STAGE_X_PLAN.md's
O5 for why).

Ported from the official ``micropython/micropython`` source tree's
``tools/hexlifyscript.py`` + ``tools/makecombinedhex.py`` (MIT,
Copyright (c) the MicroPython-on-micro:bit Developers -- see
``extensions/microbit/THIRD_PARTY_LICENSES.md``), adapted to work on
in-memory strings/bytes instead of files/argparse so it's testable
without real hardware: this is pure, deterministic Intel Hex text
manipulation, no device needed to verify its structure, the same tier
the plan's own golden-output tests already use.

V2 is NOT supported here. V2's firmware uses a real flash filesystem
(littlefs-style, multi-file), found by parsing a self-describing "Flash
Regions Table" baked into the firmware -- confirmed by downloading the
official v2.1.1 release and measuring its flash usage directly: it
already extends to 0x68000, well past this module's fixed V1
``SCRIPT_ADDR`` (0x3e000), so that address is simply wrong for V2, not
just unmaintained. Reimplementing V2's filesystem builder in Python is
a real, bounded, but separate and larger task -- not started.
"""
import binascii
import struct
from pathlib import Path

FIRMWARE_DIR = Path(__file__).parent / "firmware"
V1_FIRMWARE_HEX = FIRMWARE_DIR / "micropython-microbit-v1.1.1.hex"

_IHEX_TYPE_DATA = 0
_IHEX_TYPE_EXT_LIN_ADDR = 4

# Fixed flash address the V1 firmware reserves for one appended script
# (hexlifyscript.py's own "magic start address in flash of script").
SCRIPT_ADDR = 0x3E000
_SCRIPT_MAX_LEN = 0x2000
assert SCRIPT_ADDR >> 16 == 3, "the hardcoded 0x0003 extended-address record below assumes this"


class FirmwareOverflowError(Exception):
    """The firmware's own flash usage already reaches the script
    region -- embedding would corrupt it. Shouldn't happen with the
    vendored firmware (verified: it uses up to 0x386d4, well below
    SCRIPT_ADDR); guards against a future firmware swap that grew."""


class ScriptTooLargeError(Exception):
    """The script (plus its 4-byte header) doesn't fit in the 8 KB
    region V1 firmware reserves for it."""


def _make_ihex_record(addr: int, record_type: int, data: bytes) -> str:
    record = struct.pack('>BHB', len(data), addr & 0xFFFF, record_type) + data
    checksum = (-(sum(record))) & 0xFF
    return ':%s%02X' % (binascii.hexlify(record).decode('ascii').upper(), checksum)


def _hexlify_script(script: bytes) -> str:
    """``script`` as Intel Hex records at SCRIPT_ADDR, with the "MP" +
    length header MicroPython's own filesystem reader expects."""
    data = b'MP' + struct.pack('<H', len(script)) + script
    # Always pad with 1-16 zero bytes (matches hexlifyscript.py's own
    # `16 - len(data) % 16` exactly, including when already aligned --
    # not a bug to "optimize away").
    data = data + bytes(16 - len(data) % 16)
    if len(data) > _SCRIPT_MAX_LEN:
        raise ScriptTooLargeError(
            f"Script too large to embed: {len(data)} bytes (max {_SCRIPT_MAX_LEN}).")

    lines = [_make_ihex_record(0, _IHEX_TYPE_EXT_LIN_ADDR, b'\x00\x03')]
    addr = SCRIPT_ADDR
    for i in range(0, len(data), 16):
        lines.append(_make_ihex_record(addr, _IHEX_TYPE_DATA, data[i:i + 16]))
        addr += 16
    return '\n'.join(lines)


def _largest_flash_addr(firmware_lines) -> int:
    """The highest flash (not UICR) address the firmware's own data
    records use -- makecombinedhex.py's own overflow check."""
    largest = 0
    page = 0
    for line in firmware_lines:
        line = line.strip()
        if not line.startswith(':'):
            continue
        count = int(line[1:3], 16)
        addr = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
        if count == 2 and record_type == _IHEX_TYPE_EXT_LIN_ADDR:
            page = int(line[9:13], 16) << 16
        elif record_type == _IHEX_TYPE_DATA:
            if page < 0x10000000:  # flash only, not the UICR
                largest = max(largest, page + addr + count)
    return largest


def _find_uicr_line(firmware_lines):
    """The line starting the UICR's extended-linear-address record
    (0x10001000), or None if absent."""
    for i, line in enumerate(firmware_lines):
        if ':020000041000EA' in line:
            return i
    return None


def embed_script(firmware_hex: str, script: bytes) -> str:
    """The V1 firmware (as Intel Hex text) with ``script`` embedded at
    the fixed flash address V1 MicroPython reserves for one appended
    script, inserted before the UICR region (or near the end if the
    firmware has none)."""
    firmware_lines = firmware_hex.splitlines()
    if _largest_flash_addr(firmware_lines) > SCRIPT_ADDR:
        raise FirmwareOverflowError(
            "This firmware's own flash usage reaches the script region -- "
            "embedding would corrupt it.")

    script_hex = _hexlify_script(script)
    uicr_line = _find_uicr_line(firmware_lines)
    split = uicr_line if uicr_line is not None else len(firmware_lines) - 2

    lines = firmware_lines[:split] + [script_hex] + firmware_lines[split:]
    return '\n'.join(lines) + '\n'


def build_v1_combined_hex(main_py_path, output_hex_path) -> None:
    """Read ``main_py_path``, embed it into the vendored V1 firmware,
    and write the combined hex to ``output_hex_path``."""
    script = Path(main_py_path).read_bytes()
    firmware_hex = V1_FIRMWARE_HEX.read_text(encoding='utf-8')
    combined = embed_script(firmware_hex, script)
    Path(output_hex_path).write_text(combined, encoding='utf-8')


def extract_script(combined_hex: str) -> bytes:
    """The embedded script's exact bytes, read back out of a combined
    hex -- the mirror of ``embed_script``, matching how MicroPython's
    own filesystem reader (and microbit-fs's ``getIntelHexAppendedScript``)
    finds it: scan for the data record at SCRIPT_ADDR, check for the
    "MP" + length header, then read exactly that many bytes. Used by
    this module's own tests as the strongest round-trip check available
    without real hardware; also handy for debugging a built hex by eye.
    """
    page = 0
    chunks = {}
    for line in combined_hex.splitlines():
        line = line.strip()
        if not line.startswith(':'):
            continue
        count = int(line[1:3], 16)
        addr = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
        if count == 2 and record_type == _IHEX_TYPE_EXT_LIN_ADDR:
            page = int(line[9:13], 16) << 16
            continue
        if record_type != _IHEX_TYPE_DATA:
            continue
        full_addr = page + addr
        if SCRIPT_ADDR <= full_addr < SCRIPT_ADDR + _SCRIPT_MAX_LEN:
            data_hex = line[9:9 + count * 2]
            chunks[full_addr] = binascii.unhexlify(data_hex)

    data = b''.join(chunks[a] for a in sorted(chunks))
    if data[:2] != b'MP':
        raise ValueError("No embedded script found at SCRIPT_ADDR.")
    length = struct.unpack('<H', data[2:4])[0]
    return data[4:4 + length]
