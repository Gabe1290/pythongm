"""The older Universal Hex "blocks" layout (queue item A11): ``hex_to_blocks`` / ``create_universal_hex(blocks=True)``.

The big comparison -- our output equals the reference library's own golden blocks file, byte for byte --
needs 1-2 MB fixtures and is run by ``tools/verify_microbit_hex_against_reference.py`` (network). These
tests pin the layout's properties on small synthetic hexes so a regression shows up in CI.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extensions.microbit.export import universal_hex as uh  # noqa: E402
from extensions.microbit.export.intel_hex import make_record  # noqa: E402

V1, V2 = 0x9900, 0x9903
EOF = uh.EOF_RECORD


def _hex(records=60, base=0x0000, start=0, tail=True, ext=None):
    """A small Intel Hex: an extended-linear-address record, ``records`` 16-byte data records, EOF."""
    lines = [make_record(0, 4, bytes([(base >> 8) & 0xFF, base & 0xFF]))]
    address = start
    for n in range(records):
        lines.append(make_record(address & 0xFFFF, 0, bytes((n * 7 + k) & 0xFF for k in range(16))))
        address += 16
        if ext and n == ext[0]:
            lines.append(make_record(0, 4, bytes([ext[1] >> 8, ext[1] & 0xFF])))
            address = 0
    if tail:
        lines.append(EOF)
    return "\n".join(lines) + "\n"


def _blocks(text):
    """The text split into blocks at each Block Start's preceding extended-linear-address record."""
    records = uh.split_records(text)
    blocks, current = [], []
    for i, record in enumerate(records):
        if (uh.get_record_type(record) == uh.TYPE_EXT_LINEAR and i + 1 < len(records)
                and uh.get_record_type(records[i + 1]) == uh.TYPE_BLOCK_START):
            if current:
                blocks.append(current)
            current = []
        current.append(record)
    blocks.append(current)
    return blocks


def _chars(block):
    return sum(len(r) + 1 for r in block)


def test_every_block_is_exactly_512_characters_except_the_very_last_of_the_file():
    text = uh.create_universal_hex([(V1, _hex()), (V2, _hex(records=45))], blocks=True)
    blocks = _blocks(text)
    assert len(blocks) > 8
    assert [_chars(b) for b in blocks[:-1]] == [512] * (len(blocks) - 1)
    last = blocks[-1]
    assert last[-1] == EOF and uh.get_record_type(last[-2]) == uh.TYPE_BLOCK_END
    assert uh.get_record_data(last[-2]) == b""                  # a zero-length Block End: not padded
    assert _chars(last) < 512


def test_a_section_boundary_does_not_break_the_alignment():
    """The last block of the FIRST hex is padded, so the second hex starts on a 512-character boundary."""
    text = uh.create_universal_hex([(V1, _hex(records=25)), (V2, _hex(records=25))], blocks=True)
    blocks = _blocks(text)
    first_of_second = next(i for i, b in enumerate(blocks) if uh.get_record_data(b[1])[:2] == bytes([0x99, 0x03]))
    assert sum(_chars(b) for b in blocks[:first_of_second]) % 512 == 0


def test_every_block_opens_with_the_extended_address_and_the_blocks_board_id():
    text = uh.create_universal_hex([(V1, _hex()), (V2, _hex())], blocks=True)
    for block in _blocks(text):
        assert uh.get_record_type(block[0]) == uh.TYPE_EXT_LINEAR
        assert uh.get_record_type(block[1]) == uh.TYPE_BLOCK_START
        assert uh.get_record_data(block[1])[2:] == bytes([0xC0, 0xDE])
    ids = {uh.get_record_data(b[1])[:2] for b in _blocks(text)}
    assert ids == {bytes([0x99, 0x00]), bytes([0x99, 0x03])}


def test_v1_keeps_data_records_and_other_boards_use_custom_data():
    text = uh.create_universal_hex([(V1, _hex(records=20)), (V2, _hex(records=20))], blocks=True)
    types_by_board = {}
    for block in _blocks(text):
        board = uh.get_record_data(block[1])[:2]
        types_by_board.setdefault(board, set()).update(uh.get_record_type(r) for r in block[2:])
    assert uh.TYPE_DATA in types_by_board[bytes([0x99, 0x00])] and uh.TYPE_CUSTOM_DATA not in types_by_board[bytes([0x99, 0x00])]
    assert uh.TYPE_CUSTOM_DATA in types_by_board[bytes([0x99, 0x03])] and uh.TYPE_DATA not in types_by_board[bytes([0x99, 0x03])]


def test_separating_gives_back_each_board_hex():
    a, b = _hex(records=70), _hex(records=33, base=0x0001)
    parts = uh.separate_universal_hex(uh.create_universal_hex([(V1, a), (V2, b)], blocks=True))
    assert [board for board, _ in parts] == [V1, V2]
    assert parts[0][1] == a and parts[1][1] == b


def test_blocks_and_sections_carry_the_same_data():
    a, b = _hex(records=70), _hex(records=33)
    blocks = uh.separate_universal_hex(uh.create_universal_hex([(V1, a), (V2, b)], blocks=True))
    sections = uh.separate_universal_hex(uh.create_universal_hex([(V1, a), (V2, b)]))
    assert blocks == sections


def test_a_change_of_extended_address_is_repeated_at_the_start_of_the_blocks_after_it():
    text = uh.create_universal_hex([(V1, _hex(records=60, ext=(20, 0x0003)))], blocks=True)
    seen = []
    for block in _blocks(text):
        seen.append(uh.get_record_data(block[0]))
    assert seen[0] == bytes([0, 0]) and seen[-1] == bytes([0, 3])        # starts low, ends at 0x0003
    assert bytes([0, 3]) in seen[1:]
    assert seen == sorted(seen)                                           # never goes back


def test_an_extended_segment_record_becomes_a_linear_one():
    seg = make_record(0, 2, bytes([0x10, 0x00]))                          # segment 0x1000 -> linear 0x0001
    lines = [make_record(0, 4, b"\x00\x00"), make_record(0, 0, b"\x01" * 16), seg, make_record(0, 0, b"\x02" * 16), EOF]
    text = uh.create_universal_hex([(V1, "\n".join(lines) + "\n")], blocks=True)
    assert not any(uh.get_record_type(r) == uh.TYPE_EXT_SEGMENT for r in uh.split_records(text))
    assert make_record(0, 4, b"\x00\x01") in uh.split_records(text)


def test_a_hex_without_an_end_of_file_record_has_none_added_by_the_blocks_writer():
    text = uh.hex_to_blocks(_hex(records=12, tail=False), V1)
    assert EOF not in uh.split_records(text)
    assert all(_chars(b) == 512 for b in _blocks(text))


def test_errors_match_the_sections_writer():
    with pytest.raises(uh.UniversalHexError):
        uh.hex_to_blocks(uh.create_universal_hex([(V1, _hex())], blocks=True), V1)       # already universal
    with pytest.raises(uh.UniversalHexError):
        uh.hex_to_blocks(_hex(records=4)[:-len(EOF) - 1] + EOF + "\n" + make_record(0, 0, b"\x01" * 16) + "\n", V1)   # EOF not last
    with pytest.raises(uh.UniversalHexError):
        uh.hex_to_blocks(_hex(), 0x10000)                                              # board id out of range
    assert uh.hex_to_blocks("", V1) == "" and uh.create_universal_hex([], blocks=True) == ""


def test_the_default_is_still_the_sections_layout():
    a = _hex(records=30)
    assert uh.create_universal_hex([(V1, a)]) == uh.create_universal_hex([(V1, a)], blocks=False)
    assert uh.create_universal_hex([(V1, a)]) != uh.create_universal_hex([(V1, a)], blocks=True)


def _hex_sized(record_bytes, records=40):
    lines = [make_record(0, 4, b"\x00\x00")]
    for n in range(records):
        lines.append(make_record((n * record_bytes) & 0xFFFF, 0, bytes((n + k) & 0xFF for k in range(record_bytes))))
    lines.append(EOF)
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize("record_bytes", range(1, 33))
def test_blocks_stay_exactly_512_characters_for_every_record_size(record_bytes):
    """The Block End has to be reserved room or some record sizes overflow a block by a few characters."""
    text = uh.create_universal_hex([(V1, _hex_sized(record_bytes)), (V2, _hex_sized(record_bytes, 25))], blocks=True)
    blocks = _blocks(text)
    assert [_chars(b) for b in blocks[:-1]] == [512] * (len(blocks) - 1), record_bytes
    parts = uh.separate_universal_hex(text)
    assert parts[0][1] == _hex_sized(record_bytes) and parts[1][1] == _hex_sized(record_bytes, 25)


def test_the_standalone_blocks_writer_keeps_the_end_of_file_record_only_when_the_input_had_one():
    with_eof = uh.split_records(uh.hex_to_blocks(_hex(records=12), V1))
    assert with_eof[-1] == EOF and with_eof.count(EOF) == 1
    assert uh.get_record_type(with_eof[-2]) == uh.TYPE_BLOCK_END
    assert EOF not in uh.split_records(uh.hex_to_blocks(_hex(records=12, tail=False), V1))
