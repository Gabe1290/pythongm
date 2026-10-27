"""The V2 Flash Regions Table (docs/MICROBIT_V2_HEX_PLAN.md, unit H1).

The parser must reproduce the numbers MEASURED on the real v2.1.2 firmware
(pages 109-114 for the file system, runtime ending at 0x68000), and refuse
anything that is not a V2 MicroPython hex -- including the V1 firmware.
"""
import struct
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.microbit.export import flash_regions as fr  # noqa: E402
from extensions.microbit.export.flash_regions import (  # noqa: E402
    FlashRegionsError, find_header_address, read_flash_regions)
from extensions.microbit.export.intel_hex import MemoryMap, parse_hex  # noqa: E402

FIRMWARE = REPO_ROOT / "extensions" / "microbit" / "export" / "firmware"
V1_HEX = FIRMWARE / "micropython-microbit-v1.1.1.hex"
V2_HEX = FIRMWARE / "micropython-microbit-v2.1.2.hex"


def _table_bytes(rows, page_log2=12, version=1):
    """A table as the firmware lays it out: rows nearest the header first, then
    the header; ``rows`` is a list of (id, hash_type, first_page, length, hash8)."""
    # row 0 sits directly below the header, so lay the rows out bottom-up:
    # the LAST row sits lowest
    body = b"".join(struct.pack("<BBHI", rid, ht, page, length) + h
                    for rid, ht, page, length, h in reversed(rows))
    header = struct.pack("<IHHHHI", fr.MAGIC_1, version, 16 * len(rows), len(rows),
                         page_log2, fr.MAGIC_2)
    return body + header


def _memory_with_table(rows, page_end=0x8000, extra=None):
    blob = _table_bytes(rows)
    m = MemoryMap()
    m.set(page_end - len(blob), blob)
    for addr, data in (extra or {}).items():
        m.set(addr, data)
    return m


ROWS = [(3, 0, 20, 0x6000, bytes(8)),                    # file system  (row 0, nearest the header)
        (2, 0, 4, 0x10000, bytes(8)),                    # runtime
        (1, 0, 1, 0x3000, bytes(8))]


# --- the real firmware ------------------------------------------------------------------

def _real():
    memory, _ = parse_hex(V2_HEX.read_text(encoding="ascii"))
    return memory


def test_real_v2_firmware_table_matches_the_measured_numbers():
    table = read_flash_regions(_real())
    assert (table.page_size, table.version, table.region_count) == (4096, 1, 3)
    assert table.table_length == 48
    assert table.header_address == 0x67FF0
    assert table.runtime_end == 0x68000
    assert (table.fs_start, table.fs_end) == (0x6D000, 0x73000)
    assert table.region(fr.REGION_FS).first_page == 109
    assert table.region(fr.REGION_FS).length == 0x6000 == 24576
    mp = table.region(fr.REGION_MICROPYTHON)
    assert (mp.start(4096), mp.length) == (0x1C000, 0x4BA4C)
    assert table.region(fr.REGION_SOFT_DEVICE).start(4096) == 0x1000


def test_real_v2_firmware_names_its_version():
    text = read_flash_regions(_real()).micropython_version
    assert text.startswith("micro:bit v2.1.2") and "MicroPython" in text


def test_real_v2_filesystem_region_is_empty_in_the_stock_hex():
    memory = _real()
    table = read_flash_regions(memory)
    assert not any(memory.is_set(a) for a in range(table.fs_start, table.fs_end, 256))


def test_the_v1_firmware_has_no_regions_table_and_is_refused():
    memory, _ = parse_hex(V1_HEX.read_text(encoding="ascii"))
    assert find_header_address(memory) is None
    with pytest.raises(FlashRegionsError, match="not a micro:bit V2"):
        read_flash_regions(memory)


# --- synthetic tables ---------------------------------------------------------------------

def test_parses_a_hand_built_table():
    table = read_flash_regions(_memory_with_table(ROWS))
    assert table.fs_start == 20 * 4096 and table.fs_end == 20 * 4096 + 0x6000
    assert table.region(2).first_page == 4 and table.region(1).length == 0x3000
    assert table.region(99) is None


def test_the_table_is_found_inside_one_long_contiguous_run_of_data():
    m = _memory_with_table(ROWS, page_end=0x8000)
    table_start = 0x8000 - len(_table_bytes(ROWS))
    m.set(0x1000, bytes(table_start - 0x1000))         # data runs right up to the table
    m.set(0x8000, bytes(0x1000))                       # and on past it, contiguously
    assert len(m.segments()) == 1
    assert read_flash_regions(m).header_address == 0x8000 - 16


def test_a_pointer_hash_reads_the_string_it_points_at():
    text = b"micro:bit v9.9 test\0"
    ptr = struct.pack("<I", 0x2000) + bytes(4)
    rows = [(3, 0, 20, 0x6000, bytes(8)), (2, 2, 4, 0x10000, ptr)]
    m = _memory_with_table(rows, extra={0x2000: text})
    assert read_flash_regions(m).micropython_version == "micro:bit v9.9 test"


def test_a_pointer_into_missing_memory_gives_an_empty_string_not_a_crash():
    rows = [(3, 0, 20, 0x6000, bytes(8)), (2, 2, 4, 0x10000, struct.pack("<I", 0x5000) + bytes(4))]
    assert read_flash_regions(_memory_with_table(rows)).micropython_version == ""


def test_a_table_without_a_file_system_region_is_refused():
    rows = [(2, 0, 4, 0x10000, bytes(8)), (1, 0, 1, 0x3000, bytes(8))]
    with pytest.raises(FlashRegionsError, match="no file system region"):
        read_flash_regions(_memory_with_table(rows))


def test_a_table_without_a_micropython_region_is_refused():
    rows = [(3, 0, 20, 0x6000, bytes(8)), (1, 0, 1, 0x3000, bytes(8))]
    with pytest.raises(FlashRegionsError, match="no MicroPython region"):
        read_flash_regions(_memory_with_table(rows))


def test_a_truncated_table_is_refused():
    m = _memory_with_table(ROWS)
    segs = m.segments()
    broken = MemoryMap()
    start, data = segs[0]
    broken.set(start + 16, data[16:])                  # lose the lowest row
    with pytest.raises(FlashRegionsError, match="missing"):
        read_flash_regions(broken)


def test_magic_in_the_wrong_place_is_not_a_table():
    m = MemoryMap()
    m.set(0x1000, struct.pack("<I", fr.MAGIC_1) + bytes(12))      # magic1 only
    assert find_header_address(m) is None


def test_a_different_page_size_is_honoured():
    blob = _table_bytes(ROWS, page_log2=10)
    m = MemoryMap()
    m.set(0x4000 - len(blob), blob)
    table = read_flash_regions(m, scan_page=1024)
    assert table.page_size == 1024 and table.fs_start == 20 * 1024
