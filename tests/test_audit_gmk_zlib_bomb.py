"""Regression test for M41: bounded zlib decompression in the GMK reader.

A .gmk is an untrusted foreign format, so a small compressed block must not
be allowed to inflate without bound (decompression bomb) and OOM the IDE.
read_zlib_data must cap the decompressed size and raise GmkReadError instead.

Pure logic; no Qt required.
"""

import struct
import zlib

import pytest

from importers.gmk_reader import (
    GmkReadError,
    GmkStream,
    MAX_ZLIB_DECOMPRESSED,
)


def _zlib_block(payload: bytes) -> bytes:
    """Build the on-wire form: 4-byte LE compressed length + compressed data."""
    compressed = zlib.compress(payload)
    return struct.pack("<i", len(compressed)) + compressed


def test_normal_block_round_trips():
    payload = b"hello gamemaker " * 100
    stream = GmkStream(_zlib_block(payload))
    assert stream.read_zlib_data() == payload


def test_empty_block_returns_empty():
    stream = GmkStream(struct.pack("<i", 0))
    assert stream.read_zlib_data() == b""


def test_block_at_cap_still_decompresses():
    # Highly compressible payload exactly at the cap: must succeed, not raise.
    payload = b"\x00" * MAX_ZLIB_DECOMPRESSED
    block = _zlib_block(payload)
    # The compressed form of all-zeros is tiny (a few KB), so this is cheap.
    assert len(block) < 1_000_000
    stream = GmkStream(block)
    result = stream.read_zlib_data()
    assert len(result) == MAX_ZLIB_DECOMPRESSED


def test_decompression_bomb_is_rejected_not_allocated():
    # A tiny compressed block that inflates well past the cap.
    bomb_size = MAX_ZLIB_DECOMPRESSED + (64 * 1024 * 1024)
    payload = b"\x00" * bomb_size
    block = _zlib_block(payload)
    # The bomb is small on the wire despite the huge expansion.
    assert len(block) < 1_000_000
    stream = GmkStream(block)
    with pytest.raises(GmkReadError) as exc:
        stream.read_zlib_data()
    assert "decompression bomb" in str(exc.value).lower() or "maximum" in str(
        exc.value
    ).lower()


def test_corrupt_zlib_raises_gmk_error():
    block = struct.pack("<i", 8) + b"notzlib!"
    stream = GmkStream(block)
    with pytest.raises(GmkReadError):
        stream.read_zlib_data()


def test_negative_length_raises():
    stream = GmkStream(struct.pack("<i", -5))
    with pytest.raises(GmkReadError):
        stream.read_zlib_data()
