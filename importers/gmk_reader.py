#!/usr/bin/env python3
"""
Low-level binary stream reader for GameMaker .gmk files.

Provides primitives for reading little-endian integers, doubles, strings,
and zlib-compressed data blocks from a binary buffer.

Supports the v701 byte-level encryption (swap table cipher).
"""

import struct
import zlib


class GmkReadError(Exception):
    """Error reading from a GMK binary stream."""

    def __init__(self, message, position=None):
        if position is not None:
            message = f"[pos 0x{position:X}] {message}"
        super().__init__(message)
        self.position = position


def _make_encode_table(seed: int) -> list:
    """
    Generate the GM7 encryption encode table from a seed.

    This is a 256-entry permutation table built by performing
    10000 adjacent swaps driven by the seed.
    """
    table = list(range(256))
    a = 6 + (seed % 250)
    b = seed // 250
    for i in range(1, 10001):
        j = 1 + ((i * a + b) % 254)
        table[j], table[j + 1] = table[j + 1], table[j]
    return table


def _make_decode_table(seed: int) -> list:
    """
    Generate the GM7 decryption decode table (inverse of encode table).
    """
    encode = _make_encode_table(seed)
    decode = [0] * 256
    for i in range(256):
        decode[encode[i]] = i
    return decode


class GmkStream:
    """
    Binary stream reader for GMK file data.

    Wraps a bytes buffer with a position cursor and provides methods
    for reading GMK binary primitives (little-endian integers, doubles,
    length-prefixed strings, and zlib-compressed blocks).

    Supports optional v701 decryption via enable_decryption().
    """

    def __init__(self, data: bytes, pos: int = 0):
        self._data = data
        self._pos = pos
        self._decode_table = None  # Set by enable_decryption()

    @property
    def position(self) -> int:
        return self._pos

    @position.setter
    def position(self, value: int):
        self._pos = value

    def remaining(self) -> int:
        """Number of bytes remaining in the stream."""
        return len(self._data) - self._pos

    def at_end(self) -> bool:
        return self._pos >= len(self._data)

    def enable_decryption(self, seed: int):
        """
        Enable v701 byte-level decryption using the given seed.

        After calling this, all subsequent reads will be decrypted
        through the swap table cipher.
        """
        self._decode_table = _make_decode_table(seed)

    def disable_decryption(self):
        """Disable decryption (for sub-streams that are already decrypted)."""
        self._decode_table = None

    def _check(self, count: int):
        """Raise if not enough bytes remain."""
        if self._pos + count > len(self._data):
            raise GmkReadError(
                f"Attempted to read {count} bytes but only {self.remaining()} remain",
                self._pos,
            )

    def _decrypt_bytes(self, raw: bytes, start_pos: int) -> bytes:
        """Apply v701 decryption to raw bytes read from start_pos."""
        if self._decode_table is None:
            return raw
        result = bytearray(len(raw))
        for i, byte in enumerate(raw):
            result[i] = (self._decode_table[byte] - (start_pos + i)) & 0xFF
        return bytes(result)

    def read_byte(self) -> int:
        """Read a single byte (with decryption if enabled)."""
        self._check(1)
        pos = self._pos
        raw = self._data[pos]
        self._pos += 1
        if self._decode_table is not None:
            return (self._decode_table[raw] - pos) & 0xFF
        return raw

    def read_bytes(self, count: int) -> bytes:
        """Read raw bytes and advance position (with decryption if enabled)."""
        self._check(count)
        start = self._pos
        raw = self._data[start : start + count]
        self._pos += count
        return self._decrypt_bytes(raw, start)

    def read_int32(self) -> int:
        """Read a 32-bit signed little-endian integer."""
        raw = self.read_bytes(4)
        (value,) = struct.unpack_from("<i", raw, 0)
        return value

    def read_uint32(self) -> int:
        """Read a 32-bit unsigned little-endian integer."""
        raw = self.read_bytes(4)
        (value,) = struct.unpack_from("<I", raw, 0)
        return value

    def read_double(self) -> float:
        """Read a 64-bit IEEE 754 little-endian double."""
        raw = self.read_bytes(8)
        (value,) = struct.unpack_from("<d", raw, 0)
        return value

    def read_bool(self) -> bool:
        """Read a boolean stored as a 32-bit integer (0 = False)."""
        return self.read_int32() != 0

    def read_string(self) -> str:
        """
        Read a length-prefixed string.

        Format: 4-byte length (LE int32) followed by that many bytes.
        GM uses Windows-1252 encoding; we decode as latin-1 which is a
        safe superset for single-byte encodings.
        """
        length = self.read_int32()
        if length <= 0:
            # GM format uses -1 or 0 for empty strings (matches ENIGMA readStr)
            return ""
        raw = self.read_bytes(length)
        try:
            return raw.decode("latin-1")
        except UnicodeDecodeError:
            return raw.decode("utf-8", errors="replace")

    def read_zlib_data(self) -> bytes:
        """
        Read a zlib-compressed block.

        Format: 4-byte compressed length followed by the compressed data.
        Returns decompressed bytes.
        """
        comp_length = self.read_int32()
        if comp_length < 0:
            raise GmkReadError(
                f"Negative zlib data length: {comp_length}", self._pos - 4
            )
        if comp_length == 0:
            return b""
        compressed = self.read_bytes(comp_length)
        try:
            return zlib.decompress(compressed)
        except zlib.error as e:
            raise GmkReadError(f"Zlib decompression failed: {e}", self._pos) from e

    def read_zlib_stream(self) -> "GmkStream":
        """
        Read a zlib-compressed block and return a new GmkStream
        wrapping the decompressed data (decryption NOT inherited).
        """
        return GmkStream(self.read_zlib_data())

    def skip(self, count: int):
        """Advance position by count bytes (reads through decryption)."""
        self._check(count)
        self._pos += count

    def __repr__(self):
        return f"GmkStream(pos=0x{self._pos:X}, size=0x{len(self._data):X})"
