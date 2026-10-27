"""The Universal Hex (docs/MICROBIT_V2_HEX_PLAN.md, unit H5).

Checked against independent facts, since no board and no reference run is
possible here:
* checksums worked out by hand, and two record strings the reference library
  hard-codes in its source (``:0400000BFFFFFFFFF5`` and the 12-byte one);
* a property test: for hex inputs of every length from 0 to 70 records, the
  section text length is an exact multiple of 512 characters;
* a separator that must give back each board's own memory;
* the real V1 and V2 firmware.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.microbit.export import hex_build  # noqa: E402
from extensions.microbit.export import universal_hex as u  # noqa: E402
from extensions.microbit.export.intel_hex import make_record, parse_hex  # noqa: E402
from extensions.microbit.export.universal_hex import UniversalHexError  # noqa: E402

V1, V2 = u.BOARD_ID_V1, u.BOARD_ID_V2


def _hex(n_data, data_len=16, base=0x1000, start_record=True, ext=None):
    """A small valid Intel Hex with ``n_data`` data records."""
    lines = []
    if ext is not None:
        lines.append(ext)
    for i in range(n_data):
        lines.append(make_record((base + i * data_len) & 0xFFFF, 0,
                                 bytes((i + k) & 0xFF for k in range(data_len))))
    if start_record:
        lines.append(make_record(0, 3, b"\x20\x00\x9c\x51"))
    lines.append(":00000001FF")
    return "\n".join(lines) + "\n"


def _types(text):
    return [int(l[7:9], 16) for l in text.splitlines() if l]


def _checksums_ok(text):
    return all(sum(bytes.fromhex(l[1:])) & 0xFF == 0 for l in text.splitlines() if l)


# --- records: hand-computed and the reference's own hard-coded strings --------------------------

def test_block_start_records_match_a_hand_computed_checksum():
    # 04 00 00 0A 99 03 C0 DE -> sum 584 -> checksum (-584) & 0xFF = 0xB8
    assert u.block_start_record(V2) == ":0400000A9903C0DEB8"
    # ... and for 0x9900: sum 581 -> 0xBB
    assert u.block_start_record(V1) == ":0400000A9900C0DEBB"


def test_block_end_records_match_the_strings_the_reference_hard_codes():
    assert u.block_end_record(0) == ":0000000BF5"
    assert u.block_end_record(4) == ":0400000BFFFFFFFFF5"
    assert u.block_end_record(0x0C) == ":0C00000BFFFFFFFFFFFFFFFFFFFFFFFFF5"


def test_padded_data_and_extended_address_records():
    assert u.padded_data_record(0) == ":0000000CF4"
    assert u.padded_data_record(2) == ":0200000CFFFFF4"
    assert u.ext_lin_address_record(0) == ":020000040000FA"
    assert u.ext_lin_address_record(0x20000000) == ":020000042000DA"


def test_record_validation():
    with pytest.raises(UniversalHexError):
        u.create_record(0x10000, 0)
    with pytest.raises(UniversalHexError, match="too many bytes"):
        u.create_record(0, 0, bytes(33))
    with pytest.raises(UniversalHexError, match="not valid"):
        u.create_record(0, 0x07)
    with pytest.raises(UniversalHexError):
        u.block_start_record(0x10000)
    with pytest.raises(UniversalHexError):
        u.ext_lin_address_record(-1)
    with pytest.raises(UniversalHexError, match="too small"):
        u.get_record_type(":00")
    with pytest.raises(UniversalHexError, match="start with"):
        u.get_record_type("0000000001FF0000000000")


def test_convert_record_keeps_the_data_and_fixes_the_checksum():
    rec = make_record(0x1234, 0, b"\x01\x02\x03")
    custom = u.convert_record_to(rec, u.TYPE_CUSTOM_DATA)
    assert custom[7:9] == "0D" and custom[9:-2] == rec[9:-2]
    assert sum(bytes.fromhex(custom[1:])) & 0xFF == 0
    assert u.convert_record_to(custom, u.TYPE_DATA) == rec


def test_extended_segment_converts_to_linear_only_for_64k_multiples():
    assert u.convert_ext_segment_to_linear(make_record(0, 2, b"\x10\x00")) == \
        u.ext_lin_address_record(0x10000)
    with pytest.raises(UniversalHexError, match="Invalid Extended Segment"):
        u.convert_ext_segment_to_linear(make_record(0, 2, b"\x01\x00"))
    with pytest.raises(UniversalHexError, match="Invalid Extended Segment"):
        u.convert_ext_segment_to_linear(make_record(0, 2, b"\x10\x01"))


def test_find_data_field_length():
    assert u.find_data_field_length(_hex(5).splitlines()) == 16
    assert u.find_data_field_length(_hex(5, data_len=32).splitlines()) == 32
    with pytest.raises(UniversalHexError, match="too large"):
        u.find_data_field_length([":" + "00" * 40])


# --- one section ----------------------------------------------------------------------------------

def test_a_section_opens_with_the_address_and_block_start_and_ends_with_block_end():
    section = u.hex_to_section(_hex(3), V2)
    lines = section.splitlines()
    assert lines[0] == ":020000040000FA"
    assert lines[1] == u.block_start_record(V2)
    assert u.get_record_type(lines[-2]) == u.TYPE_BLOCK_END
    assert lines[-1] == ":00000001FF"


def test_v2_data_records_become_custom_data_and_v1_ones_stay_data():
    v2 = _types(u.hex_to_section(_hex(5), V2))
    v1 = _types(u.hex_to_section(_hex(5), V1))
    assert v2.count(u.TYPE_CUSTOM_DATA) == 5 and v2.count(u.TYPE_DATA) == 0
    assert v1.count(u.TYPE_DATA) == 5 and v1.count(u.TYPE_CUSTOM_DATA) == 0
    # the other V1 id behaves like V1
    assert _types(u.hex_to_section(_hex(5), 0x9901)).count(u.TYPE_DATA) == 5


def test_custom_data_keeps_each_records_address_and_bytes():
    original = _hex(4).splitlines()[:4]
    section = u.hex_to_section(_hex(4), V2).splitlines()
    custom = [l for l in section if l[7:9] == "0D"]
    for a, b in zip(original, custom):
        assert a[3:7] == b[3:7] and a[9:-2] == b[9:-2]


def test_start_address_records_are_dropped():
    assert 3 not in _types(u.hex_to_section(_hex(3, start_record=True), V2))
    assert 5 not in _types(u.hex_to_section(
        _hex(3, start_record=False).replace(":00000001FF", make_record(0, 5, b"\x00\x01\x02\x03") + "\n:00000001FF"), V2))


def test_extended_segment_records_are_converted_to_linear():
    seg = make_record(0, 2, b"\x20\x00")
    section = u.hex_to_section(_hex(2, ext=seg), V2)
    assert 2 not in _types(section)
    assert section.splitlines()[0] == u.ext_lin_address_record(0x20000)


def test_a_leading_linear_address_is_kept_not_repeated():
    ela = u.ext_lin_address_record(0x30000)
    lines = u.hex_to_section(_hex(2, ext=ela), V2).splitlines()
    assert lines[0] == ela and lines[1] == u.block_start_record(V2)
    assert lines.count(ela) == 1


def test_every_section_is_an_exact_multiple_of_512_characters():
    """The property behind the format: padding makes each section's text
    (newlines included, the end-of-file record excluded) a whole number of
    512-character blocks -- for ANY input length."""
    for n in range(0, 71):
        for board in (V1, V2):
            section = u.hex_to_section(_hex(n), board)
            body = section[:-len(":00000001FF\n")]
            assert len(body) % 512 == 0, (n, board, len(body))
            assert _checksums_ok(section)


@pytest.mark.parametrize("data_len", [16, 32])
def test_alignment_holds_for_16_and_32_byte_records_and_padding_uses_that_size(data_len):
    for n in (1, 7, 31, 32, 33):
        section = u.hex_to_section(_hex(n, data_len=data_len), V2)
        assert len(section[:-len(":00000001FF\n")]) % 512 == 0
        pads = [l for l in section.splitlines() if l[7:9] == "0C"]
        assert all(int(l[1:3], 16) <= data_len for l in pads)


def test_an_empty_input_gives_an_empty_section():
    assert u.hex_to_section("", V2) == "" and u.hex_to_section("\n\n", V2) == ""


def test_an_already_universal_hex_is_refused():
    uni = u.create_universal_hex([(V1, _hex(3)), (V2, _hex(3))])
    with pytest.raises(UniversalHexError, match="already a Universal Hex"):
        u.hex_to_section(uni, V2)


def test_an_eof_in_the_middle_is_an_error_not_silently_truncated():
    broken = _hex(2) .replace(":00000001FF\n", "") + ":00000001FF\n" + make_record(0, 0, b"\x01\x02") + "\n"
    with pytest.raises(UniversalHexError, match="EoF record found at record"):
        u.hex_to_section(broken, V2)


def test_a_makecode_v1_hex_gets_a_useful_error():
    ram = u.ext_lin_address_record(0x20000000)
    makecode = _hex(2, start_record=False).replace(
        ":00000001FF\n", ":00000001FF\n" + ram + "\n" + make_record(0, 0, b"\x01\x02") + "\n")
    with pytest.raises(UniversalHexError, match="MakeCode"):
        u.hex_to_section(makecode, V1)


# --- the whole file -------------------------------------------------------------------------------

def test_only_the_last_section_keeps_the_end_of_file_record():
    uni = u.create_universal_hex([(V1, _hex(5)), (V2, _hex(5))])
    lines = uni.splitlines()
    assert lines.count(":00000001FF") == 1 and lines[-1] == ":00000001FF"
    assert [u.get_record_type(l) for l in lines].count(u.TYPE_BLOCK_START) == 2
    assert _checksums_ok(uni) and uni.endswith("\n")


def test_the_two_boards_appear_in_order_with_their_ids():
    uni = u.create_universal_hex([(V1, _hex(5)), (V2, _hex(5))])
    starts = [l for l in uni.splitlines() if l[7:9] == "0A"]
    assert starts == [u.block_start_record(V1), u.block_start_record(V2)]


def test_a_last_hex_without_an_eof_still_gets_one():
    no_eof = _hex(3).replace(":00000001FF\n", "")
    uni = u.create_universal_hex([(V1, _hex(3)), (V2, no_eof)])
    assert uni.splitlines()[-1] == ":00000001FF"


def test_nothing_in_nothing_out():
    assert u.create_universal_hex([]) == ""


def test_one_board_alone_is_still_a_valid_universal_hex():
    uni = u.create_universal_hex([(V2, _hex(5))])
    assert u.is_universal_hex(uni) and len(u.separate_universal_hex(uni)) == 1


def test_is_universal_hex():
    assert u.is_universal_hex(u.create_universal_hex([(V1, _hex(3)), (V2, _hex(3))]))
    assert not u.is_universal_hex(_hex(3))
    assert not u.is_universal_hex("")
    assert not u.is_universal_hex(":020000040000FA\n:1000000000\n")
    # CRLF files too
    assert u.is_universal_hex(u.create_universal_hex(
        [(V1, _hex(3)), (V2, _hex(3))]).replace("\n", "\r\n"))


# --- separating ------------------------------------------------------------------------------------

def test_separating_gives_each_board_its_own_memory_back():
    a, b = _hex(9, base=0x1000), _hex(13, base=0x4000)
    uni = u.create_universal_hex([(V1, a), (V2, b)])
    got = dict(u.separate_universal_hex(uni))
    assert parse_hex(got[V1])[0] == parse_hex(a)[0]
    assert parse_hex(got[V2])[0] == parse_hex(b)[0]
    assert list(dict(u.separate_universal_hex(uni))) == [V1, V2]


def test_separating_keeps_data_across_address_changes():
    from extensions.microbit.export.intel_hex import MemoryMap, to_hex
    m = MemoryMap()
    for base in (0x0, 0xFFF0, 0x10020, 0x20000, 0x10001000):
        m.set(base, bytes((base + k) & 0xFF for k in range(50)))
    one = to_hex(m)
    uni = u.create_universal_hex([(V1, one), (V2, one)])
    for _, text in u.separate_universal_hex(uni):
        assert parse_hex(text)[0] == m


def test_separating_rejects_what_is_not_a_universal_hex():
    with pytest.raises(UniversalHexError, match="Empty"):
        u.separate_universal_hex("")
    with pytest.raises(UniversalHexError, match="invalid"):
        u.separate_universal_hex(_hex(3))


def test_a_bad_block_start_record_is_reported():
    uni = u.create_universal_hex([(V1, _hex(3)), (V2, _hex(3))]).splitlines()
    bad = make_record(0, u.TYPE_BLOCK_START, b"\x99\x03")        # 2 bytes, not 4
    uni[1] = bad
    with pytest.raises(UniversalHexError, match="Block Start record invalid"):
        u.separate_universal_hex("\n".join(uni) + "\n")


# --- the real firmware -----------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real():
    v1 = hex_build.embed_script(hex_build.V1_FIRMWARE_HEX.read_text(encoding="ascii"),
                                b"print(1)\n")
    v2 = hex_build.build_v2_hex(b"print(1)\n")
    return v1, v2, u.create_universal_hex([(V1, v1), (V2, v2)])


def test_the_real_universal_hex_is_valid_and_about_the_expected_size(real):
    _, _, uni = real
    assert _checksums_ok(uni)
    assert 1_700_000 < len(uni) < 2_100_000             # the ~1.8 MB the research predicted
    assert max(int(l[1:3], 16) for l in uni.splitlines()) <= 32
    assert u.is_universal_hex(uni)


def test_each_real_section_is_aligned_to_512_characters(real):
    _, _, uni = real
    lines = uni.splitlines()
    marks = [i for i, l in enumerate(lines) if l[7:9] == "0A"]
    assert len(marks) == 2
    # the first section runs from line 0 (its address record) to just before the
    # second section's address record; its text length is a whole number of blocks
    second_start = marks[1] - 1
    first = "\n".join(lines[:second_start]) + "\n"
    assert len(first) % 512 == 0
    body = "\n".join(lines[second_start:-1]) + "\n"        # without the EoF record
    assert len(body) % 512 == 0


def test_the_real_v1_section_keeps_ordinary_data_records(real):
    _, _, uni = real
    types = _types(uni[:uni.index(u.block_start_record(V2))])     # the V1 section only
    assert u.TYPE_CUSTOM_DATA not in types and u.TYPE_DATA in types


def test_the_real_v2_section_has_only_custom_data(real):
    _, _, uni = real
    v2_part = uni[uni.index(u.block_start_record(V2)):]
    types = _types(v2_part)
    assert u.TYPE_DATA not in types and u.TYPE_CUSTOM_DATA in types


def test_the_real_boards_each_get_their_own_firmware_and_script_back(real):
    v1, v2, uni = real
    got = dict(u.separate_universal_hex(uni))
    assert set(got) == {V1, V2}
    assert parse_hex(got[V1])[0] == parse_hex(v1)[0]
    assert parse_hex(got[V2])[0] == parse_hex(v2)[0]
    assert hex_build.extract_script(got[V1]) == b"print(1)\n"
    assert hex_build.extract_v2_script(got[V2]) == b"print(1)\n"


def test_the_real_v2_file_system_survives_the_trip(real):
    from extensions.microbit.export import mpfs
    from extensions.microbit.export.flash_regions import read_flash_regions
    _, _, uni = real
    memory, _ = parse_hex(dict(u.separate_universal_hex(uni))[V2])
    layout = mpfs.layout_from_regions(read_flash_regions(memory))
    assert mpfs.read_files(memory, layout) == {"main.py": b"print(1)\n"}
