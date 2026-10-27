#!/usr/bin/env python3
"""The micro:bit MicroPython file system: build and read it
(docs/MICROBIT_V2_HEX_PLAN.md, unit H2).

The same format on V1 and V2 -- MicroPython's ``filesystem.c`` -- laid into
flash as a doubly-linked list of **128-byte chunks**. Where it lives is the
only difference (``FsLayout``: V2 reads it from the Flash Regions Table).

Each chunk is ``marker(1) | data(126) | tail(1)``:

* the first chunk of a file has marker ``0xFE`` and starts its data area with a
  header: ``end_offset(1) name_length(1) name(...)`` and then the file's bytes;
* any other chunk's marker is the **index of the previous chunk** of the file,
  and the tail byte of every chunk is the index of the **next** one (``0xFF``
  for the last);
* ``0xFF`` marks an unused chunk, ``0x00`` a freed one (reusable), and ``0xFD``
  the first byte of the "persistent data" page, which closes the file system.

Chunk indexes start at 1 at the lowest address (0 means "freed"). A file's data
is followed by one extra ``0xFF`` byte, so a file that exactly fills its last
chunk still consumes the next one -- which is what MicroPython itself does.
``end_offset`` is ``(header_length + file_length) mod 126``: where the last
chunk's data stops.

Written from the documented behaviour and TypeScript source of the MIT-licensed
``microbit-foundation/microbit-fs`` (``micropython-fs-builder.ts``; see
``THIRD_PARTY_LICENSES.md``). One deliberate difference: each chunk is written to
the address of **its own index**, so the result is also right when the free
chunks are not consecutive (the reference writes the file as one consecutive
run, which is only correct on an empty file system).
"""
from dataclasses import dataclass

CHUNK_LEN = 128
MARKER_LEN = 1
TAIL_LEN = 1
DATA_LEN = CHUNK_LEN - MARKER_LEN - TAIL_LEN          # 126
MAX_FILENAME_LEN = 120
# A one-byte pointer, minus the four values reserved as markers (0, 0xFD-0xFF).
MAX_CHUNKS = 256 - 4

FREED = 0x00
PERSISTENT = 0xFD
FILE_START = 0xFE
UNUSED = 0xFF

_TAIL_INDEX = CHUNK_LEN - 1


class MpfsError(ValueError):
    """Base class for file system errors."""


class FilenameError(MpfsError):
    """The file name is empty or too long."""


class EmptyFileError(MpfsError):
    """A file must contain at least one byte."""


class FsFullError(MpfsError):
    """There are not enough free chunks for the file."""


class FsCorruptError(MpfsError):
    """The chunk chain being read does not hold together."""


@dataclass(frozen=True)
class FsLayout:
    """Where the file system sits in flash. ``start``/``end`` bound the whole
    region (for V2, the Flash Regions Table's file system region); its last
    page is the persistent-data page, so chunks occupy ``[chunks_start, end -
    page_size)``."""
    start: int
    end: int
    page_size: int

    def __post_init__(self):
        if self.end <= self.start or self.page_size <= 0:
            raise MpfsError("The file system region is empty.")
        if self.chunks_start % self.page_size:
            raise MpfsError(
                "The file system start address does not align with the flash page size.")

    @property
    def chunks_start(self):
        """Chunk 1's address. A region bigger than 252 chunks can't be
        addressed with one-byte pointers, so the file system uses only the top
        of it (the reference library's rule)."""
        return max(self.start, self.end - CHUNK_LEN * MAX_CHUNKS)

    @property
    def persistent_page(self):
        return self.end - self.page_size

    @property
    def chunk_count(self):
        return (self.persistent_page - self.chunks_start) // CHUNK_LEN

    def chunk_address(self, index):
        return self.chunks_start + (index - 1) * CHUNK_LEN


def layout_from_regions(regions):
    """The ``FsLayout`` for a parsed V2 ``FlashRegions``."""
    return FsLayout(regions.fs_start, regions.fs_end, regions.page_size)


def _marker(memory, address):
    return memory.get(address, 1, default=UNUSED)[0]


def free_chunks(memory, layout):
    """Indexes of every unused or freed chunk, ascending."""
    return [i for i in range(1, layout.chunk_count + 1)
            if _marker(memory, layout.chunk_address(i)) in (UNUSED, FREED)]


def _encode_name(name):
    raw = name.encode("utf-8") if isinstance(name, str) else bytes(name)
    if not raw:
        raise FilenameError("A file needs a name.")
    if len(raw) > MAX_FILENAME_LEN:
        raise FilenameError(
            f'The file name "{name}" is too long (at most {MAX_FILENAME_LEN} bytes).')
    return raw


def file_chunk_count(name, data):
    """How many chunks a file takes (header + data + the extra 0xFF byte)."""
    raw = _encode_name(name)
    return -(-(2 + len(raw) + len(data) + 1) // DATA_LEN)


def max_file_size(layout, name="main.py", used_chunks=0):
    """The largest file (bytes) that fits an otherwise-empty file system."""
    raw = _encode_name(name)
    return (layout.chunk_count - used_chunks) * DATA_LEN - (2 + len(raw)) - 1


def build_file_chunks(name, data, free):
    """The chunks of one file as ``[(index, 128 bytes)]``, using the chunk
    indexes in ``free`` in order. Raises ``FsFullError`` if there are too few."""
    raw = _encode_name(name)
    data = bytes(data)
    if not data:
        raise EmptyFileError(f'The file "{name}" is empty; a file must contain data.')
    header_len = 2 + len(raw)
    end_offset = (header_len + len(data)) % DATA_LEN
    stream = bytes([end_offset, len(raw)]) + raw + data + b"\xff"
    needed = -(-len(stream) // DATA_LEN)
    if needed > len(free):
        raise FsFullError(
            f'There is not enough space for "{name}": it needs {needed} chunks '
            f"({len(stream)} bytes) and only {len(free)} are free.")

    chunks = []
    for n in range(needed):
        body = stream[n * DATA_LEN:(n + 1) * DATA_LEN]
        chunk = bytearray(b"\xff" * CHUNK_LEN)
        chunk[0] = FILE_START if n == 0 else free[n - 1]       # marker: file start / previous
        chunk[MARKER_LEN:MARKER_LEN + len(body)] = body
        if n < needed - 1:
            chunk[_TAIL_INDEX] = free[n + 1]                    # tail: next chunk
        chunks.append((free[n], bytes(chunk)))
    return chunks


def add_file(memory, layout, name, data):
    """Write one file into ``memory`` (a ``MemoryMap`` holding the firmware) and
    set the persistent-data marker. Mutates ``memory``."""
    free = free_chunks(memory, layout)
    if not free:
        raise FsFullError("There is no storage space left.")
    for index, chunk in build_file_chunks(name, data, free):
        memory.set(layout.chunk_address(index), chunk)
    memory.set(layout.persistent_page, bytes([PERSISTENT]))


def read_files(memory, layout):
    """Every file in the file system as ``{name: bytes}``, by following the
    chunk chains the way the device does. Raises ``FsCorruptError`` for a chain
    that does not link up, and for two files with one name."""
    used = {}
    starts = []
    for index in range(1, layout.chunk_count + 1):
        chunk = memory.get(layout.chunk_address(index), CHUNK_LEN, default=UNUSED)
        marker = chunk[0]
        if marker in (UNUSED, FREED, PERSISTENT):
            continue
        used[index] = chunk
        if marker == FILE_START:
            starts.append(index)

    files = {}
    for start in starts:
        first = used[start]
        end_offset, name_len = first[1], first[2]
        data_from = 3 + name_len
        name = first[3:data_from].decode("utf-8", "replace")
        if name in files:
            raise FsCorruptError(f"Found multiple files named: {name}.")
        out = bytearray()
        current, current_index = first, start
        remaining = len(used) + 1                  # a chain longer than the chunks in use loops
        while remaining:
            remaining -= 1
            nxt = current[_TAIL_INDEX]
            if nxt == UNUSED:
                out += current[data_from:1 + end_offset]
                break
            out += current[data_from:_TAIL_INDEX]
            following = used.get(nxt)
            if following is None:
                raise FsCorruptError(f"Chunk {current_index} points to unused chunk {nxt}.")
            if following[0] != current_index:
                raise FsCorruptError(
                    f"Chunk {nxt} does not link back to chunk {current_index}.")
            current, current_index = following, nxt
            data_from = 1                          # only a file's first chunk has a header
        else:
            raise FsCorruptError("Malformed file chunks did not link correctly.")
        files[name] = bytes(out)
    return files
