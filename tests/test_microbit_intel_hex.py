"""Intel Hex <-> memory map (docs/MICROBIT_V2_HEX_PLAN.md, unit H1).

Synthetic cases for every edge, then the real vendored V2 firmware: the
parser must read all of it (strict checksums) and re-emitting it must give the
same memory back.
"""
import ast
import hashlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.microbit.export import intel_hex as ih  # noqa: E402
from extensions.microbit.export.intel_hex import (  # noqa: E402
    IntelHexError, MemoryMap, parse_hex, to_hex)

FIRMWARE = REPO_ROOT / "extensions" / "microbit" / "export" / "firmware"
V2_HEX = FIRMWARE / "micropython-microbit-v2.1.2.hex"
V2_SHA256 = "66fae07b71777e9e3a6b5122a27930b24cc0be5002ab9a67e92494c54a1645ef"


def _checksum_ok(line):
    raw = bytes.fromhex(line[1:])
    return sum(raw) & 0xFF == 0


# --- MemoryMap ------------------------------------------------------------------------

def test_set_and_get_with_a_gap():
    m = MemoryMap()
    m.set(0x100, b"abc")
    m.set(0x200, b"xyz")
    assert m.get(0x100, 3) == b"abc" and m.get(0x200, 3) == b"xyz"
    assert [s for s, _ in m.segments()] == [0x100, 0x200]
    assert len(m) == 6


def test_adjacent_writes_merge_into_one_segment():
    m = MemoryMap()
    m.set(10, b"aa")
    m.set(12, b"bb")
    m.set(8, b"cc")
    assert m.segments() == [(8, b"ccaabb")]


def test_overwrite_in_the_middle_keeps_the_rest():
    m = MemoryMap()
    m.set(0, b"0123456789")
    m.set(3, b"XY")
    assert m.segments() == [(0, b"012XY56789")]


def test_a_write_bridging_two_segments_joins_them():
    m = MemoryMap()
    m.set(0, b"aaaa")
    m.set(10, b"bbbb")
    m.set(3, b"-------------")        # 3..15 swallows the gap and the second segment
    assert m.segments() == [(0, b"aaa" + b"-------------")]


def test_a_write_that_extends_past_a_segment_end_wins():
    m = MemoryMap()
    m.set(0, b"abcd")
    m.set(2, b"WXYZ")
    assert m.segments() == [(0, b"abWXYZ")]


def test_get_missing_bytes_use_the_default_or_raise():
    m = MemoryMap()
    m.set(4, b"ab")
    assert m.get(2, 6, default=0xFF) == b"\xff\xffab\xff\xff"
    with pytest.raises(KeyError):
        m.get(2, 6)


def test_is_set_needs_the_whole_range():
    m = MemoryMap()
    m.set(4, b"abcd")
    assert m.is_set(4, 4) and m.is_set(5, 2)
    assert not m.is_set(3, 2) and not m.is_set(7, 2) and not m.is_set(100)


def test_slice_clips_and_clone_is_independent():
    m = MemoryMap()
    m.set(0, b"0123456789")
    s = m.slice(3, 7)
    assert s.segments() == [(3, b"3456")]
    c = m.clone()
    c.set(0, b"Z")
    assert m.get(0, 1) == b"0" and c.get(0, 1) == b"Z"
    assert m == m.clone() and m != c


def test_empty_and_negative_writes():
    m = MemoryMap()
    m.set(5, b"")
    assert len(m) == 0 and m.segments() == []
    with pytest.raises(ValueError):
        m.set(-1, b"x")


# --- parse_hex ------------------------------------------------------------------------

def test_parse_a_simple_hex():
    text = ":0400000102030405F1\n:00000001FF\n"
    # fix: build a valid record rather than trusting a hand checksum
    text = ih._record(0x10, ih.TYPE_DATA, b"\x01\x02\x03\x04") + "\n:00000001FF\n"
    memory, starts = parse_hex(text)
    assert memory.segments() == [(0x10, b"\x01\x02\x03\x04")] and starts == []


def test_extended_linear_and_segment_addresses():
    text = "\n".join([
        ih._record(0, ih.TYPE_EXT_LINEAR, b"\x00\x03"),
        ih._record(0x10, ih.TYPE_DATA, b"\xaa"),
        ih._record(0, ih.TYPE_EXT_SEGMENT, b"\x20\x00"),       # base 0x20000
        ih._record(0x4, ih.TYPE_DATA, b"\xbb"),
        ":00000001FF"])
    memory, _ = parse_hex(text)
    assert memory.get(0x30010, 1) == b"\xaa"
    assert memory.get(0x20004, 1) == b"\xbb"


def test_start_records_are_kept_verbatim_and_uppercased():
    rec = ih._record(0, ih.TYPE_START_SEGMENT, b"\x20\x00\x9c\x51")
    memory, starts = parse_hex(rec.lower() + "\n:00000001FF\n")
    assert starts == [rec]


def test_blank_lines_and_lowercase_are_fine():
    memory, _ = parse_hex("\n" + ih._record(0, ih.TYPE_DATA, b"\xab").lower() + "\n\n")
    assert memory.get(0, 1) == b"\xab"


@pytest.mark.parametrize("line,what", [
    ("0400000001020304", "start with"),
    (":zz", "hexadecimal"),
    (":0100", "length"),
])
def test_malformed_lines_are_errors(line, what):
    with pytest.raises(IntelHexError, match=what):
        parse_hex(line)


def test_a_bad_checksum_is_an_error_not_a_different_flash_image():
    good = ih._record(0, ih.TYPE_DATA, b"\x01\x02")
    bad = good[:-2] + ("00" if good[-2:] != "00" else "01")
    with pytest.raises(IntelHexError, match="checksum"):
        parse_hex(bad)


def test_data_after_the_end_of_file_record_is_an_error():
    with pytest.raises(IntelHexError, match="after the end-of-file"):
        parse_hex(":00000001FF\n" + ih._record(0, ih.TYPE_DATA, b"\x01"))


def test_unknown_record_type_and_bad_extended_records():
    with pytest.raises(IntelHexError, match="unknown record type"):
        parse_hex(ih._record(0, 0x0A, b"\x01"))
    with pytest.raises(IntelHexError, match="extended linear"):
        parse_hex(ih._record(0, ih.TYPE_EXT_LINEAR, b"\x01"))
    with pytest.raises(IntelHexError, match="extended segment"):
        parse_hex(ih._record(0, ih.TYPE_EXT_SEGMENT, b"\x01"))


# --- to_hex ---------------------------------------------------------------------------

def test_emits_16_byte_records_in_ascending_order_with_valid_checksums():
    m = MemoryMap()
    m.set(0x2000, bytes(range(40)))
    m.set(0x100, bytes(range(5)))
    lines = to_hex(m).splitlines()
    assert lines[-1] == ":00000001FF"
    data = [l for l in lines if l[7:9] == "00"]
    assert all(_checksum_ok(l) for l in lines)
    lengths = [int(l[1:3], 16) for l in data]
    assert lengths == [5, 16, 16, 8]
    addrs = [int(l[3:7], 16) for l in data]
    assert addrs == sorted(addrs)


def test_extended_address_records_appear_when_the_upper_bits_change():
    m = MemoryMap()
    m.set(0x10, b"\x01")
    m.set(0x31000, b"\x02")
    m.set(0x10001014, b"\x03")
    lines = to_hex(m).splitlines()
    ext = [l for l in lines if l[7:9] == "04"]
    assert [l[9:13] for l in ext] == ["0003", "1000"]      # none needed for the first, at 0
    assert parse_hex("\n".join(lines))[0] == m


def test_a_record_never_crosses_a_64k_boundary():
    m = MemoryMap()
    m.set(0xFFF8, bytes(range(16)))                       # straddles 0x10000
    lines = to_hex(m).splitlines()
    data = [(l[3:7], l[1:3]) for l in lines if l[7:9] == "00"]
    assert data == [("FFF8", "08"), ("0000", "08")]
    assert parse_hex("\n".join(lines))[0] == m


def test_round_trip_of_random_looking_memory():
    m = MemoryMap()
    for i, base in enumerate((0, 0x1234, 0x8000, 0xFFF0, 0x10020, 0x20000, 0x10001000)):
        m.set(base, bytes((base + k * 7 + i) & 0xFF for k in range(37 + i)))
    assert parse_hex(to_hex(m))[0] == m


def test_start_records_and_eof_are_written_last_and_optional():
    m = MemoryMap()
    m.set(0, b"\x01")
    start = ih._record(0, ih.TYPE_START_SEGMENT, b"\x20\x00\x9c\x51")
    lines = to_hex(m, start_records=[start]).splitlines()
    assert lines[-2:] == [start, ":00000001FF"]
    assert to_hex(m, end_of_file=False).splitlines()[-1] != ":00000001FF"


def test_module_is_pure():
    tree = ast.parse((REPO_ROOT / "extensions" / "microbit" / "export" / "intel_hex.py")
                     .read_text(encoding="utf-8"))
    mods = {n.module.split(".")[0] for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom) and n.module and not n.level}
    mods |= {a.name.split(".")[0] for n in ast.walk(tree)
             if isinstance(n, ast.Import) for a in n.names}
    assert not mods & {"pygame", "PySide6", "serial", "microfs"}


# --- the real V2 firmware ----------------------------------------------------------------

def test_the_vendored_v2_firmware_is_exactly_the_documented_release():
    assert hashlib.sha256(V2_HEX.read_bytes()).hexdigest() == V2_SHA256
    assert V2_HEX.stat().st_size == 1_239_726


def _real():
    return parse_hex(V2_HEX.read_text(encoding="ascii"))


def test_the_real_firmware_parses_with_strict_checksums_into_the_measured_layout():
    memory, starts = _real()
    assert [(s, len(d)) for s, d in memory.segments()] == [
        (0x00000, 2816), (0x01000, 107520), (0x1C000, 309836), (0x67FC0, 64),
        (0x77000, 25580), (0x7E000, 4899), (0x10001014, 8)]
    assert len(memory) == 450_723
    assert starts == [":0400000320009C51EC"]


def test_the_real_firmware_survives_a_re_emit_unchanged():
    memory, starts = _real()
    again, starts2 = parse_hex(to_hex(memory, starts))
    assert again == memory and starts2 == starts


def test_the_re_emitted_firmware_is_ascending_and_every_line_is_valid():
    memory, starts = _real()
    lines = to_hex(memory, starts).splitlines()
    assert all(_checksum_ok(l) for l in lines)
    upper, last = 0, -1
    for line in lines:
        rtype = int(line[7:9], 16)
        if rtype == 4:
            upper = int(line[9:13], 16) << 16
        elif rtype == 0:
            address = upper + int(line[3:7], 16)
            assert address > last
            last = address
