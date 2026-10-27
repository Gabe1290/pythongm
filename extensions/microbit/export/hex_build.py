#!/usr/bin/env python3
"""Build a micro:bit "combined hex" -- MicroPython firmware with the student's
program inside, ready to drag onto a factory-fresh board's MICROBIT USB drive,
no prior MicroPython flash needed. Three builders, one per kind of file:

* ``embed_script`` / ``build_v1_combined_hex`` -- V1 (Stage X unit X8): the
  script appended at a fixed flash address;
* ``build_v2_hex`` / ``build_v2_combined_hex`` -- V2: ``main.py`` written into
  the MicroPython file system the firmware describes (further down);
* ``build_universal_hex`` -- both, in ONE file (the bottom of the module).

docs/MICROBIT_V2_HEX_PLAN.md explains the V2 and Universal parts.

The V1 half (this first part of the module):

Ported from the official ``micropython/micropython`` source tree's
``tools/hexlifyscript.py`` + ``tools/makecombinedhex.py`` (MIT,
Copyright (c) the MicroPython-on-micro:bit Developers -- see
``extensions/microbit/THIRD_PARTY_LICENSES.md``), adapted to work on
in-memory strings/bytes instead of files/argparse so it's testable
without real hardware: this is pure, deterministic Intel Hex text
manipulation, no device needed to verify its structure, the same tier
the plan's own golden-output tests already use.

V2 is a different mechanism and lives in the second half of this module
(``build_v2_hex``, docs/MICROBIT_V2_HEX_PLAN.md): V2's firmware already reaches
0x68000, past this module's fixed V1 ``SCRIPT_ADDR`` (0x3E000), so instead of
appending a script it writes ``main.py`` into the MicroPython **file system**,
whose location the firmware states in its own Flash Regions Table (``mpfs.py``,
``flash_regions.py``, ``intel_hex.py``).
"""
import binascii
import functools
import struct
from pathlib import Path

from . import mpfs
from .flash_regions import read_flash_regions
from .intel_hex import parse_hex, to_hex
from .universal_hex import BOARD_ID_V1, BOARD_ID_V2, create_universal_hex

FIRMWARE_DIR = Path(__file__).parent / "firmware"
V1_FIRMWARE_HEX = FIRMWARE_DIR / "micropython-microbit-v1.1.1.hex"
V2_FIRMWARE_HEX = FIRMWARE_DIR / "micropython-microbit-v2.1.2.hex"

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


# --------------------------------------------------------------------------
# V2: main.py in the MicroPython file system
# --------------------------------------------------------------------------

V2_SCRIPT_NAME = "main.py"


@functools.lru_cache(maxsize=1)
def _v2_firmware():
    """The vendored V2 firmware parsed once: ``(memory, start_records,
    layout)``. Callers must ``clone()`` the memory before changing it."""
    memory, start_records = parse_hex(V2_FIRMWARE_HEX.read_text(encoding="ascii"))
    layout = mpfs.layout_from_regions(read_flash_regions(memory))
    return memory, start_records, layout


def v2_max_script_size() -> int:
    """The largest ``main.py`` (bytes) a V2 combined hex can hold."""
    return mpfs.max_file_size(_v2_firmware()[2], V2_SCRIPT_NAME)


def build_v2_hex(script: bytes, firmware_hex: str = None) -> str:
    """The V2 firmware (Intel Hex text) with ``script`` as ``main.py`` in its
    file system: ready to drag onto a factory-fresh V2 board's MICROBIT drive.

    Every byte outside the file system region is the firmware's own, untouched;
    records come out in ascending address order. ``firmware_hex`` substitutes
    another V2 firmware (the vendored v2.1.2 by default). Raises
    ``ScriptTooLargeError`` if the script does not fit, ``ValueError`` for an
    empty one or a hex that is not a V2 MicroPython firmware.
    """
    script = bytes(script)
    if not script:
        raise ValueError("The script is empty; there is nothing to flash.")
    if firmware_hex is None:
        base, start_records, layout = _v2_firmware()
        memory = base.clone()
    else:
        memory, start_records = parse_hex(firmware_hex)
        layout = mpfs.layout_from_regions(read_flash_regions(memory))
    limit = mpfs.max_file_size(layout, V2_SCRIPT_NAME)
    if len(script) > limit:
        raise ScriptTooLargeError(
            f"Script too large for a V2 micro:bit: {len(script)} bytes (the most a "
            f"V2 board's file system holds is {limit}).")
    mpfs.add_file(memory, layout, V2_SCRIPT_NAME, script)
    return to_hex(memory, start_records)


def build_v2_combined_hex(main_py_path, output_hex_path) -> None:
    """Read ``main_py_path``, build the V2 hex around it and write it to
    ``output_hex_path`` (the V2 twin of ``build_v1_combined_hex``)."""
    script = Path(main_py_path).read_bytes()
    Path(output_hex_path).write_text(build_v2_hex(script), encoding="utf-8")


def extract_v2_script(combined_hex: str) -> bytes:
    """The ``main.py`` inside a V2 hex, read back through the file system the way
    the device does -- the mirror of ``build_v2_hex``, used by the tests as the
    strongest round-trip check available without a board."""
    memory, _ = parse_hex(combined_hex)
    layout = mpfs.layout_from_regions(read_flash_regions(memory))
    files = mpfs.read_files(memory, layout)
    if V2_SCRIPT_NAME not in files:
        raise ValueError("No main.py found in this hex's file system.")
    return files[V2_SCRIPT_NAME]


# --------------------------------------------------------------------------
# Both boards in one file: the Universal Hex
# --------------------------------------------------------------------------

def v1_max_script_size() -> int:
    """The largest script (bytes) the V1 firmware's single appended-script
    slot holds: 8 KB less the 4-byte "MP" + length header and at least one
    padding byte."""
    return _SCRIPT_MAX_LEN - 5


def universal_max_script_size() -> int:
    """The largest ``main.py`` a Universal Hex can carry: the smaller of the two
    boards' limits, which is V1's."""
    return min(v1_max_script_size(), v2_max_script_size())


def build_universal_hex(script: bytes) -> str:
    """ONE hex that flashes on either a V1 or a V2 board: the V1 firmware with
    ``script`` appended (``embed_script``) and the V2 firmware with it as
    ``main.py`` (``build_v2_hex``), each tagged with its board id and merged
    (``universal_hex``). Limited by V1's 8 KB script slot.

    Raises ``ScriptTooLargeError`` (with both limits in the message) if the
    script does not fit a V1 board, ``ValueError`` for an empty one.
    """
    script = bytes(script)
    if not script:
        raise ValueError("The script is empty; there is nothing to flash.")
    limit = universal_max_script_size()
    if len(script) > limit:
        raise ScriptTooLargeError(
            f"Script too large for a Universal Hex: {len(script)} bytes (a V1 board "
            f"holds at most {v1_max_script_size()}; build a V2-only .hex for up to "
            f"{v2_max_script_size()}).")
    v1 = embed_script(V1_FIRMWARE_HEX.read_text(encoding="utf-8"), script)
    v2 = build_v2_hex(script)
    return create_universal_hex([(BOARD_ID_V1, v1), (BOARD_ID_V2, v2)])


def build_universal_combined_hex(main_py_path, output_hex_path) -> None:
    """Read ``main_py_path``, build the Universal Hex around it and write it to
    ``output_hex_path`` (the Universal twin of the V1 and V2 file helpers)."""
    script = Path(main_py_path).read_bytes()
    Path(output_hex_path).write_text(build_universal_hex(script), encoding="utf-8")
