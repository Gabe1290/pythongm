#!/usr/bin/env python3
"""Read a V2 firmware's Flash Regions Table (docs/MICROBIT_V2_HEX_PLAN.md, H1).

A micro:bit V2 MicroPython hex describes its own flash layout. The last flash
page the runtime uses ends with a table: one 16-byte row per region, then a
16-byte header, all little-endian::

    row    id(1) hash_type(1) first_page(2) length(4) hash_data(8)
    header magic1(4) version(2) table_length(2) region_count(2) page_log2(2) magic2(4)

``magic1`` is ``0x597f30fe`` and ``magic2`` is ``0xc1b1d79d``. The header is the
*last* 16 bytes of the page, and the rows run backwards from it (row 0 sits
directly below the header). Region 3 is the MicroPython file system, region 2 the
runtime and region 1 the Nordic SoftDevice slot. This is how the file system is
found -- V2 has no fixed address for it, unlike V1.

Layout from the MIT-licensed ``microbit-foundation/microbit-fs`` (``flash-
regions.ts``), checked here against the real v2.1.2 firmware.
"""
import struct
from dataclasses import dataclass, field
from typing import List, Optional

MAGIC_1 = 0x597F30FE
MAGIC_2 = 0xC1B1D79D

ROW_LEN = 16
HEADER_LEN = 16
DEFAULT_SCAN_PAGE = 4096

REGION_SOFT_DEVICE = 1
REGION_MICROPYTHON = 2
REGION_FS = 3

HASH_EMPTY = 0
HASH_DATA = 1
HASH_POINTER = 2


class FlashRegionsError(ValueError):
    """The firmware has no (valid) Flash Regions Table."""


@dataclass(frozen=True)
class Region:
    id: int
    hash_type: int
    first_page: int
    length: int
    hash_data: bytes
    pointer_text: str = ""          # for hash_type 2: the string the pointer names

    def start(self, page_size):
        return self.first_page * page_size

    def end(self, page_size):
        return self.start(page_size) + self.length


@dataclass(frozen=True)
class FlashRegions:
    page_size: int
    version: int
    region_count: int
    table_length: int
    header_address: int             # where the 16-byte header starts
    page_end: int                   # first address after the page holding the table
    regions: List[Region] = field(default_factory=list)

    def region(self, region_id) -> Optional[Region]:
        for r in self.regions:
            if r.id == region_id:
                return r
        return None

    @property
    def runtime_end(self):
        """Where the MicroPython runtime ends: the end of the page the table is in."""
        return self.page_end

    @property
    def fs_start(self):
        return self.region(REGION_FS).start(self.page_size)

    @property
    def fs_end(self):
        return self.region(REGION_FS).end(self.page_size)

    @property
    def micropython_version(self):
        r = self.region(REGION_MICROPYTHON)
        return r.pointer_text if r else ""


def _read_c_string(memory, address, limit=256):
    out = bytearray()
    while len(out) < limit:
        try:
            b = memory.get(address + len(out), 1)[0]
        except KeyError:
            break
        if b == 0:
            break
        out.append(b)
    return out.decode("ascii", "replace")


def find_header_address(memory, scan_page=DEFAULT_SCAN_PAGE):
    """Address of the table header: the first scan page whose last 16 bytes
    carry both magic numbers. ``None`` if no page does."""
    # every page end any data reaches, not just where a segment happens to stop:
    # the table could sit inside one long contiguous run of data
    page_ends = set()
    for start, data in memory.segments():
        first = (start // scan_page + 1) * scan_page
        last = ((start + len(data) - 1) // scan_page + 1) * scan_page
        page_ends.update(range(first, last + 1, scan_page))
    for end in sorted(page_ends):
        header = end - HEADER_LEN
        if not memory.is_set(header, HEADER_LEN):
            continue
        raw = memory.get(header, HEADER_LEN)
        magic1, = struct.unpack_from("<I", raw, 0)
        magic2, = struct.unpack_from("<I", raw, 12)
        if magic1 == MAGIC_1 and magic2 == MAGIC_2:
            return header
    return None


def read_flash_regions(memory, scan_page=DEFAULT_SCAN_PAGE):
    """Parse the table out of a firmware memory map. Raises ``FlashRegionsError``
    if there is none, or it names no MicroPython / file system region."""
    header = find_header_address(memory, scan_page)
    if header is None:
        raise FlashRegionsError(
            "No Flash Regions Table found: this is not a micro:bit V2 MicroPython hex.")
    raw = memory.get(header, HEADER_LEN)
    _magic1, version, table_length, region_count, page_log2, _magic2 = \
        struct.unpack("<IHHHHI", raw)
    page_size = 1 << page_log2
    page_end = header + HEADER_LEN

    regions = []
    for i in range(region_count):
        row_start = header - (i + 1) * ROW_LEN
        if row_start < 0 or not memory.is_set(row_start, ROW_LEN):
            raise FlashRegionsError(f"Region row {i} is missing from the table.")
        row = memory.get(row_start, ROW_LEN)
        region_id, hash_type, first_page, length = struct.unpack_from("<BBHI", row, 0)
        hash_data = row[8:16]
        pointer_text = ""
        if hash_type == HASH_POINTER:
            pointer_text = _read_c_string(memory, struct.unpack_from("<I", hash_data, 0)[0])
        regions.append(Region(region_id, hash_type, first_page, length, hash_data,
                              pointer_text))

    table = FlashRegions(page_size=page_size, version=version, region_count=region_count,
                         table_length=table_length, header_address=header,
                         page_end=page_end, regions=regions)
    if table.region(REGION_MICROPYTHON) is None:
        raise FlashRegionsError("The regions table has no MicroPython region.")
    if table.region(REGION_FS) is None:
        raise FlashRegionsError("The regions table has no file system region.")
    return table
