#!/usr/bin/env python3
"""Intel Hex <-> a sparse memory map (docs/MICROBIT_V2_HEX_PLAN.md, unit H1).

Pure and deterministic: text in, text out, no device, no Qt. A micro:bit
firmware ``.hex`` is plain Intel Hex; building a combined hex means putting
file data at addresses *between* the firmware's own data, so records must be
re-emitted in ascending address order. That is what this module is for:
``parse_hex`` reads every data record into a ``MemoryMap`` (strictly -- a bad
checksum is an error, not a silently different flash image), and ``to_hex``
writes it back out.

The record layout is the standard one:
``:LLAAAATT<data>CC`` -- length, 16-bit address, type, data, checksum (the two's
complement of the sum of every preceding byte).
"""
import bisect
import binascii

TYPE_DATA = 0x00
TYPE_EOF = 0x01
TYPE_EXT_SEGMENT = 0x02       # data is a segment base: address = value << 4
TYPE_START_SEGMENT = 0x03
TYPE_EXT_LINEAR = 0x04        # data is the upper 16 bits of the address
TYPE_START_LINEAR = 0x05

RECORD_DATA_LEN = 16          # bytes per emitted data record (what the official hexes use)


class IntelHexError(ValueError):
    """The text is not valid Intel Hex."""


class MemoryMap:
    """Bytes at addresses, with gaps. Segments are kept sorted, non-overlapping
    and non-adjacent (adjacent ones merge), so iteration is in address order."""

    def __init__(self):
        self._starts = []         # sorted segment start addresses
        self._data = []           # parallel list of bytearrays

    # -- writing --------------------------------------------------------------

    def set(self, address, data):
        """Put ``data`` at ``address``, overwriting whatever was there."""
        data = bytes(data)
        if not data:
            return
        if address < 0:
            raise ValueError(f"negative address {address}")
        end = address + len(data)
        # every segment that overlaps or touches [address, end) is merged
        lo = bisect.bisect_left(self._starts, address)
        if lo > 0 and self._starts[lo - 1] + len(self._data[lo - 1]) >= address:
            lo -= 1
        hi = lo
        while hi < len(self._starts) and self._starts[hi] <= end:
            hi += 1
        if lo == hi:
            self._starts.insert(lo, address)
            self._data.insert(lo, bytearray(data))
            return
        new_start = min(address, self._starts[lo])
        new_end = max(end, self._starts[hi - 1] + len(self._data[hi - 1]))
        merged = bytearray(new_end - new_start)
        for i in range(lo, hi):
            off = self._starts[i] - new_start
            merged[off:off + len(self._data[i])] = self._data[i]
        merged[address - new_start:address - new_start + len(data)] = data
        self._starts[lo:hi] = [new_start]
        self._data[lo:hi] = [merged]

    def clone(self):
        other = MemoryMap()
        other._starts = list(self._starts)
        other._data = [bytearray(d) for d in self._data]
        return other

    # -- reading --------------------------------------------------------------

    def segments(self):
        """``[(start, bytes)]`` in ascending address order."""
        return [(s, bytes(d)) for s, d in zip(self._starts, self._data)]

    def __len__(self):
        """How many bytes are set."""
        return sum(len(d) for d in self._data)

    def is_set(self, address, length=1):
        """True if every byte in ``[address, address + length)`` is set."""
        i = bisect.bisect_right(self._starts, address) - 1
        return (i >= 0 and address + length <= self._starts[i] + len(self._data[i]))

    def get(self, address, length, default=None):
        """``length`` bytes at ``address``. Bytes that are not set come back as
        ``default`` (an int), or, if ``default`` is None, raise ``KeyError``."""
        out = bytearray()
        for a in range(address, address + length):
            out.append(self._byte(a, default))
        return bytes(out)

    def _byte(self, address, default):
        i = bisect.bisect_right(self._starts, address) - 1
        if i >= 0:
            off = address - self._starts[i]
            if off < len(self._data[i]):
                return self._data[i][off]
        if default is None:
            raise KeyError(f"address {address:#x} is not set")
        return default

    def slice(self, start, end):
        """A new map holding only the bytes in ``[start, end)``."""
        out = MemoryMap()
        for s, d in zip(self._starts, self._data):
            lo, hi = max(s, start), min(s + len(d), end)
            if lo < hi:
                out.set(lo, d[lo - s:hi - s])
        return out

    def __eq__(self, other):
        return isinstance(other, MemoryMap) and self.segments() == other.segments()


def make_record(address, record_type, data=b""):
    """One record as text: ``:LLAAAATT<data>CC`` with the checksum filled in.
    ``record_type`` is not restricted (the Universal Hex adds custom types)."""
    body = bytes([len(data), (address >> 8) & 0xFF, address & 0xFF, record_type]) + bytes(data)
    checksum = (-sum(body)) & 0xFF
    return ":" + binascii.hexlify(body + bytes([checksum])).decode("ascii").upper()


_record = make_record          # the name the tests and this module used first


def parse_hex(text):
    """Parse Intel Hex text. Returns ``(memory_map, start_records)`` where
    ``start_records`` are the raw lines of any start-address records (types 3
    and 5), kept so a rebuilt file can carry the firmware's own through.

    Raises ``IntelHexError`` for a malformed line or a bad checksum.
    """
    memory = MemoryMap()
    start_records = []
    base = 0
    seen_eof = False
    for number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if not line.startswith(":"):
            raise IntelHexError(f"line {number}: does not start with ':'")
        if seen_eof:
            raise IntelHexError(f"line {number}: data after the end-of-file record")
        try:
            raw = binascii.unhexlify(line[1:])
        except (binascii.Error, ValueError):
            raise IntelHexError(f"line {number}: not hexadecimal") from None
        if len(raw) < 5 or len(raw) != raw[0] + 5:
            raise IntelHexError(f"line {number}: wrong length")
        if sum(raw) & 0xFF:
            raise IntelHexError(f"line {number}: bad checksum")
        length, address, record_type = raw[0], (raw[1] << 8) | raw[2], raw[3]
        data = raw[4:4 + length]
        if record_type == TYPE_DATA:
            memory.set(base + address, data)
        elif record_type == TYPE_EOF:
            seen_eof = True
        elif record_type == TYPE_EXT_SEGMENT:
            if length != 2:
                raise IntelHexError(f"line {number}: bad extended segment record")
            base = ((data[0] << 8) | data[1]) << 4
        elif record_type == TYPE_EXT_LINEAR:
            if length != 2:
                raise IntelHexError(f"line {number}: bad extended linear record")
            base = ((data[0] << 8) | data[1]) << 16
        elif record_type in (TYPE_START_SEGMENT, TYPE_START_LINEAR):
            start_records.append(line.upper())
        else:
            raise IntelHexError(f"line {number}: unknown record type {record_type:#04x}")
    return memory, start_records


def to_hex(memory, start_records=(), end_of_file=True):
    """Intel Hex text for ``memory``: 16-byte data records in ascending address
    order, an extended-linear-address record whenever the upper 16 bits change,
    then any ``start_records`` and the end-of-file record. Lines end in ``\\n``,
    including the last."""
    lines = []
    upper = 0
    for start, data in memory.segments():
        offset = 0
        while offset < len(data):
            address = start + offset
            if (address >> 16) != upper:
                upper = address >> 16
                lines.append(_record(0, TYPE_EXT_LINEAR, bytes([upper >> 8, upper & 0xFF])))
            # never let a record cross a 64 KiB boundary
            room = 0x10000 - (address & 0xFFFF)
            chunk = data[offset:offset + min(RECORD_DATA_LEN, room)]
            lines.append(_record(address & 0xFFFF, TYPE_DATA, chunk))
            offset += len(chunk)
    lines.extend(start_records)
    if end_of_file:
        lines.append(":00000001FF")
    return "\n".join(lines) + "\n"
