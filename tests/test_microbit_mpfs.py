"""The micro:bit MicroPython file system (docs/MICROBIT_V2_HEX_PLAN.md, unit H2).

No V2 board and no reference oracle could be used, so the checks are:
* two known-answer vectors worked out BY HAND from the documented layout and
  written below as literal bytes (independent of the builder's code);
* an independent reader that follows the device's own algorithm, round-tripped
  at every size boundary;
* exact capacity limits and every error path.
"""
import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.microbit.export import mpfs  # noqa: E402
from extensions.microbit.export.intel_hex import MemoryMap  # noqa: E402
from extensions.microbit.export.mpfs import (  # noqa: E402
    EmptyFileError, FilenameError, FsCorruptError, FsFullError, FsLayout, MpfsError,
    add_file, build_file_chunks, free_chunks, max_file_size, read_files)

# The real v2.1.2 file system region: pages 109-114.
LAYOUT = FsLayout(start=0x6D000, end=0x73000, page_size=4096)
FF = b"\xff"


def _fresh():
    return MemoryMap()


# --- the layout -----------------------------------------------------------------------------

def test_layout_matches_the_real_v2_region():
    assert LAYOUT.chunks_start == 0x6D000
    assert LAYOUT.persistent_page == 0x72000
    assert LAYOUT.chunk_count == 160                     # 5 pages of 32 chunks
    assert LAYOUT.chunk_address(1) == 0x6D000
    assert LAYOUT.chunk_address(2) == 0x6D080
    assert LAYOUT.chunk_address(160) == 0x6D000 + 159 * 128


def test_a_region_bigger_than_252_chunks_that_would_start_unaligned_is_refused():
    # 0x60000..0x73000 is 77,824 bytes: more than 252 chunks, so only the top
    # 252 * 128 bytes would be used, starting at 0x6B200 -- not page aligned.
    # That is refused when the layout is built, not guessed at later.
    with pytest.raises(MpfsError, match="align"):
        FsLayout(start=0x60000, end=0x73000, page_size=4096)


def test_an_oversized_region_that_does_align_uses_only_its_top():
    page = 128                                    # a small page makes the alignment hold
    layout = FsLayout(start=0, end=128 * 252 + page, page_size=page)
    assert layout.chunks_start == layout.end - 128 * 252
    assert layout.chunk_count == 251              # the top page is the persistent one


def test_an_empty_or_inverted_region_is_refused():
    with pytest.raises(MpfsError):
        FsLayout(start=0x1000, end=0x1000, page_size=4096)
    with pytest.raises(MpfsError):
        FsLayout(start=0x2000, end=0x1000, page_size=4096)


def test_an_unaligned_start_is_refused():
    with pytest.raises(MpfsError, match="align"):
        FsLayout(start=0x6D100, end=0x73000, page_size=4096)


# --- known-answer vectors, derived by hand -----------------------------------------------------

def test_vector_one_a_small_main_py_is_a_single_chunk():
    """name "main.py" (7), data b"x=1\\n" (4).
    header = end_offset, name_len, name = 9 bytes; end_offset = (9 + 4) % 126 = 13 = 0x0D.
    stream = header + data + 0xFF  ->  FE-marker chunk:
      FE | 0D 07 'm''a''i''n''.''p''y' | 'x''=''1' 0A | FF (the extra byte) | FF ... | tail FF
    """
    mem = _fresh()
    add_file(mem, LAYOUT, "main.py", b"x=1\n")
    expected = bytes.fromhex("FE" "0D" "07" "6D61696E2E7079" "783D310A") + FF * (128 - 14)
    assert len(expected) == 128
    assert mem.get(0x6D000, 128) == expected
    assert mem.get(0x72000, 1) == b"\xfd"                # the persistent-data marker
    # and nothing else was written
    assert [(s, len(d)) for s, d in mem.segments()] == [(0x6D000, 128), (0x72000, 1)]


def test_vector_two_a_file_spanning_two_chunks():
    """name "a" (1), data = bytes 0..129 (130 bytes).
    header = 3 bytes, end_offset = (3 + 130) % 126 = 7.
    stream = 03... : 3 header + 130 data + 1 extra = 134 bytes -> 2 chunks of 126.
    chunk 1: FE | 07 01 'a' | data[0:123]      | tail = 02
    chunk 2: 01 | data[123:130] (7 bytes) | FF (extra) | FF ... | tail FF
    """
    data = bytes(range(130))
    mem = _fresh()
    add_file(mem, LAYOUT, "a", data)
    chunk1 = bytes([0xFE, 0x07, 0x01, 0x61]) + data[:123] + bytes([0x02])
    chunk2 = bytes([0x01]) + data[123:130] + FF * (128 - 1 - 7)
    assert (len(chunk1), len(chunk2)) == (128, 128)
    assert mem.get(0x6D000, 128) == chunk1
    assert mem.get(0x6D080, 128) == chunk2
    assert read_files(mem, LAYOUT) == {"a": data}


def test_an_exact_fit_still_consumes_a_following_chunk():
    """header 3 + data 123 = 126 bytes fills chunk 1 exactly; the extra 0xFF byte
    pushes into chunk 2, end_offset is 0, and the reader returns all 123 bytes."""
    data = bytes([0x41]) * 123
    mem = _fresh()
    add_file(mem, LAYOUT, "a", data)
    c1 = mem.get(0x6D000, 128)
    c2 = mem.get(0x6D080, 128)
    assert c1[1] == 0                                    # end_offset: (3 + 123) % 126
    assert c1[127] == 2                                  # points at chunk 2
    assert c2 == bytes([1]) + FF * 127                   # marker, then nothing but 0xFF
    assert read_files(mem, LAYOUT) == {"a": data}


# --- build -> read round trips -----------------------------------------------------------------

@pytest.mark.parametrize("size", list(range(1, 140)) + [250, 251, 252, 253, 1000, 4095, 4096, 20150])
def test_round_trip_at_every_boundary(size):
    data = bytes((i * 7 + 3) & 0xFF for i in range(size))
    mem = _fresh()
    add_file(mem, LAYOUT, "main.py", data)
    assert read_files(mem, LAYOUT) == {"main.py": data}


def test_data_that_looks_like_markers_round_trips():
    data = bytes([0xFF, 0xFE, 0xFD, 0x00]) * 80
    mem = _fresh()
    add_file(mem, LAYOUT, "main.py", data)
    assert read_files(mem, LAYOUT)["main.py"] == data


@pytest.mark.parametrize("name", ["a", "main.py", "x" * 120, "é.py"])
def test_names_of_different_lengths_round_trip(name):
    mem = _fresh()
    add_file(mem, LAYOUT, name, b"hello world")
    assert read_files(mem, LAYOUT) == {name: b"hello world"}


def test_two_files_use_successive_chunks_and_both_read_back():
    mem = _fresh()
    add_file(mem, LAYOUT, "one.py", bytes(range(200)))                 # chunks 1-2
    add_file(mem, LAYOUT, "two.py", b"print('hi')\n")                  # chunk 3
    assert read_files(mem, LAYOUT) == {"one.py": bytes(range(200)), "two.py": b"print('hi')\n"}
    assert mem.get(LAYOUT.chunk_address(3), 1) == bytes([mpfs.FILE_START])
    assert free_chunks(mem, LAYOUT)[0] == 4


def test_file_chunk_count_matches_what_is_built():
    for size in (1, 10, 100, 117, 118, 126, 127, 300):
        data = bytes(size)
        built = build_file_chunks("main.py", data, list(range(1, 200)))
        assert len(built) == mpfs.file_chunk_count("main.py", data)


# --- capacity -------------------------------------------------------------------------------------

def test_the_exact_maximum_fits_and_one_more_byte_does_not():
    limit = max_file_size(LAYOUT, "main.py")
    assert limit == 160 * 126 - 9 - 1 == 20150
    mem = _fresh()
    add_file(mem, LAYOUT, "main.py", bytes(limit))
    assert len(read_files(mem, LAYOUT)["main.py"]) == limit
    with pytest.raises(FsFullError, match="not enough space"):
        add_file(_fresh(), LAYOUT, "main.py", bytes(limit + 1))


def test_a_full_file_system_says_so():
    mem = _fresh()
    add_file(mem, LAYOUT, "big.py", bytes(max_file_size(LAYOUT, "big.py")))
    assert free_chunks(mem, LAYOUT) == []
    with pytest.raises(FsFullError, match="no storage space"):
        add_file(mem, LAYOUT, "more.py", b"x")


# --- free-chunk handling ---------------------------------------------------------------------------

def test_freed_chunks_are_reusable_and_used_ones_are_skipped_correctly():
    mem = _fresh()
    mem.set(LAYOUT.chunk_address(2), bytes([0x77]))       # chunk 2 is somebody else's (marker 0x77)
    mem.set(LAYOUT.chunk_address(4), bytes([mpfs.FREED]))  # chunk 4 was freed
    assert free_chunks(mem, LAYOUT)[:4] == [1, 3, 4, 5]
    data = bytes(range(250))                              # needs 3 chunks: 1, 3, 4
    add_file(mem, LAYOUT, "n.py", data)
    # the file's own chunks hold the right data, wherever they landed
    assert read_files(mem, LAYOUT)["n.py"] == data
    assert mem.get(LAYOUT.chunk_address(2), 1) == bytes([0x77])      # untouched


# --- errors -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["", b""])
def test_an_empty_name_is_refused(name):
    with pytest.raises(FilenameError, match="needs a name"):
        add_file(_fresh(), LAYOUT, name, b"x")


def test_a_name_over_120_bytes_is_refused():
    add_file(_fresh(), LAYOUT, "x" * 120, b"x")           # 120 is fine
    with pytest.raises(FilenameError, match="too long"):
        add_file(_fresh(), LAYOUT, "x" * 121, b"x")
    with pytest.raises(FilenameError, match="too long"):
        add_file(_fresh(), LAYOUT, "é" * 61, b"x")        # 122 bytes in UTF-8


def test_an_empty_file_is_refused():
    with pytest.raises(EmptyFileError, match="must contain data"):
        add_file(_fresh(), LAYOUT, "main.py", b"")


def _written():
    mem = _fresh()
    add_file(mem, LAYOUT, "main.py", bytes(range(200)))   # chunks 1-2
    return mem


def test_a_chain_pointing_at_an_unused_chunk_is_corrupt():
    mem = _written()
    mem.set(LAYOUT.chunk_address(1) + 127, bytes([9]))     # chunk 1 -> chunk 9 (unused)
    with pytest.raises(FsCorruptError, match="points to unused"):
        read_files(mem, LAYOUT)


def test_a_chain_that_does_not_link_back_is_corrupt():
    mem = _written()
    mem.set(LAYOUT.chunk_address(2), bytes([5]))           # chunk 2's back-pointer is wrong
    with pytest.raises(FsCorruptError, match="link back"):
        read_files(mem, LAYOUT)


def test_a_looping_chain_is_caught_not_followed_forever():
    mem = _written()
    mem.set(LAYOUT.chunk_address(2) + 127, bytes([2]))     # chunk 2 -> itself
    mem.set(LAYOUT.chunk_address(2), bytes([2]))           # and back to itself
    with pytest.raises(FsCorruptError):
        read_files(mem, LAYOUT)


def test_two_files_with_one_name_are_refused_on_read():
    mem = _fresh()
    add_file(mem, LAYOUT, "dup.py", b"1")
    add_file(mem, LAYOUT, "dup.py", b"2")
    with pytest.raises(FsCorruptError, match="multiple files"):
        read_files(mem, LAYOUT)


def test_reading_an_empty_file_system_gives_no_files():
    assert read_files(_fresh(), LAYOUT) == {}
    assert free_chunks(_fresh(), LAYOUT) == list(range(1, 161))


def test_persistent_marker_is_written_and_nothing_outside_the_region():
    mem = _written()
    for start, data in mem.segments():
        assert LAYOUT.start <= start and start + len(data) <= LAYOUT.end


def test_module_is_pure():
    tree = ast.parse((REPO_ROOT / "extensions" / "microbit" / "export" / "mpfs.py")
                     .read_text(encoding="utf-8"))
    mods = {n.module.split(".")[0] for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom) and n.module and not n.level}
    mods |= {a.name.split(".")[0] for n in ast.walk(tree)
             if isinstance(n, ast.Import) for a in n.names}
    assert not mods & {"pygame", "PySide6", "serial", "microfs"}
