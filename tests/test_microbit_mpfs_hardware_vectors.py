"""The MicroPython file system code against bytes captured from a REAL micro:bit.

``extensions/microbit/export/mpfs.py`` writes and reads the file system the micro:bit's MicroPython
keeps in flash (queue item A10). Its other tests compare it with itself and with hand-derived answers.
These compare it with the reference library's test vectors, which that library's spec says were
"created by transferring the files to a micro:bit running MicroPython v1.0.1 using Mu" -- so they are
what the device itself writes, including the boundary cases (a file that exactly fills a chunk, one
byte short, one byte over) and files stored at scattered chunk positions.

Data: ``tests/data/microbit_fs_hardware_vectors.json``, extracted from
microbit-foundation/microbit-fs ``src/__tests__/micropython-fs-builder.spec.ts`` (MIT, (c) 2019
Micro:bit Educational Foundation and the microbit-fs contributors; see THIRD_PARTY_LICENSES.md).
The firmware layout is the one that spec uses: file system at 0x38C00, 27 KiB.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extensions.microbit.export import mpfs  # noqa: E402
from extensions.microbit.export.intel_hex import MemoryMap, parse_hex  # noqa: E402

DATA = json.loads((Path(__file__).parent / "data" / "microbit_fs_hardware_vectors.json").read_text(encoding="utf-8"))
LAYOUT = mpfs.FsLayout(DATA["layout"]["start"], DATA["layout"]["start"] + DATA["layout"]["size"],
                       DATA["layout"]["page_size"])
WRITING = {v["name"]: v for v in DATA["writing"]}
READING = {v["name"]: v for v in DATA["reading"]}
CHUNK = mpfs.CHUNK_LEN


def _content(vector):
    return bytes.fromhex(vector["content_hex"])


def _written(*names):
    """An empty file system with these files added, in order."""
    memory = MemoryMap()
    for name in names:
        mpfs.add_file(memory, LAYOUT, name, _content(WRITING[name]))
    return memory


def _read(memory, address, size):
    return bytes(memory.get(address, size, default=0xEE))


def _memory_from_records(*vectors):
    """One memory holding every vector's records (each vector is its own piece of the same flash)."""
    lines = [r for v in vectors for r in v["records"] if r != ":00000001FF"] + [":00000001FF"]
    memory, _ = parse_hex(chr(10).join(lines) + chr(10))
    return memory


# -- the data itself ------------------------------------------------------------------------------

def test_the_vectors_are_what_the_extractor_says_they_are():
    assert LAYOUT.chunk_address(1) == 0x38C00
    assert sorted(WRITING) == ["one_chunk_minus.py", "one_chunk_plus.py", "test_file_1.py", "test_file_2.py", "two_chunks.py"]
    assert sorted(READING) == ["afirst.py", "alast.py", "main.py", "one_chunk_minus.py", "one_chunk_plus.py"]
    for v in WRITING.values():
        raw = bytes.fromhex(v["chunks_hex"])
        # the capture holds whole chunks plus the used 16-byte records of the last one
        assert raw[0] == mpfs.FILE_START and len(raw) % 16 == 0, v["name"]


# -- writing: our bytes == the device's bytes -----------------------------------------------------

@pytest.mark.parametrize("name", ["one_chunk_plus.py", "one_chunk_minus.py", "two_chunks.py", "test_file_1.py"])
def test_a_single_file_is_written_exactly_as_the_device_writes_it(name):
    vector = WRITING[name]
    want = bytes.fromhex(vector["chunks_hex"])
    # test_file_1.py was captured elsewhere on the device; the spec compares it at the file system's start
    memory = _written(name)
    assert _read(memory, LAYOUT.chunk_address(1), len(want)) == want
    # whatever the capture did not include of the last chunk is unused flash in ours
    rest = -len(want) % CHUNK
    assert _read(memory, LAYOUT.chunk_address(1) + len(want), rest) == bytes([mpfs.UNUSED]) * rest


def test_two_files_land_in_consecutive_chunks_with_the_right_links():
    memory = _written("test_file_1.py", "test_file_2.py")
    first, second = WRITING["test_file_1.py"], WRITING["test_file_2.py"]
    assert _read(memory, LAYOUT.chunk_address(1), len(first["chunks_hex"]) // 2) == bytes.fromhex(first["chunks_hex"])
    assert second["address"] == LAYOUT.chunk_address(2)
    assert _read(memory, second["address"], len(second["chunks_hex"]) // 2) == bytes.fromhex(second["chunks_hex"])


@pytest.mark.parametrize("name,chunks", [("one_chunk_minus.py", 1), ("one_chunk_plus.py", 2), ("two_chunks.py", 2),
                                          ("test_file_1.py", 1), ("test_file_2.py", 10)])
def test_the_chunk_count_is_the_devices(name, chunks):
    assert mpfs.file_chunk_count(name, _content(WRITING[name])) == chunks
    captured = len(bytes.fromhex(WRITING[name]["chunks_hex"]))
    assert -(-captured // CHUNK) == chunks


def test_the_boundary_cases_are_the_boundaries():
    """The three single-file vectors straddle the one-chunk limit: 125, 126 and 127 data bytes."""
    sizes = {n: len(_content(WRITING[n])) + 2 + len(n.encode()) for n in ("one_chunk_minus.py", "one_chunk_plus.py", "two_chunks.py")}
    assert sizes["one_chunk_minus.py"] == mpfs.DATA_LEN - 1       # leaves the last byte of the chunk unused
    assert sizes["one_chunk_plus.py"] == mpfs.DATA_LEN            # fills the chunk, so the next is taken (and left empty)
    assert sizes["two_chunks.py"] == mpfs.DATA_LEN + 1            # one byte into the second chunk


# -- reading: the device's bytes -> our files -----------------------------------------------------

@pytest.mark.parametrize("name", ["one_chunk_plus.py", "one_chunk_minus.py", "afirst.py", "alast.py", "main.py"])
def test_a_file_stored_by_the_device_is_read_back_exactly(name):
    files = mpfs.read_files(_memory_from_records(READING[name]), LAYOUT)
    assert files == {name: _content(READING[name])}


def test_three_files_at_scattered_chunk_positions_are_all_found():
    """The spec's 'files of different sizes in non-consecutive locations' case (11, 3 and 1 chunks)."""
    memory = _memory_from_records(READING["afirst.py"], READING["alast.py"], READING["main.py"])
    files = mpfs.read_files(memory, LAYOUT)
    assert files == {n: _content(READING[n]) for n in ("afirst.py", "alast.py", "main.py")}


def test_what_we_write_is_read_back_and_what_the_device_wrote_is_rewritten_identically():
    """A round trip through both directions on the same data."""
    for name in ("one_chunk_plus.py", "one_chunk_minus.py", "two_chunks.py", "test_file_2.py"):
        content = _content(WRITING[name])
        assert mpfs.read_files(_written(name), LAYOUT) == {name: content}
