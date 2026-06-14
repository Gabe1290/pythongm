"""Regression test for the GMK zlib decompression bomb (audit M41).

read_zlib_data called zlib.decompress with no output cap, so a small compressed
block could inflate to gigabytes and OOM the IDE during import of an untrusted
.gmk. It now uses a bounded decompressor and rejects blocks over the cap.
"""

import struct
import zlib

import pytest

import importers.gmk_reader as reader
from importers.gmk_reader import GmkStream, GmkReadError


def _block(raw: bytes) -> bytes:
    """A length-prefixed zlib block as read_zlib_data expects."""
    compressed = zlib.compress(raw)
    return struct.pack("<i", len(compressed)) + compressed


def test_normal_block_round_trips():
    payload = b"hello world" * 100
    stream = GmkStream(_block(payload))
    assert stream.read_zlib_data() == payload


def test_oversized_block_rejected(monkeypatch):
    # Cap tiny so a modest block trips it without allocating gigabytes.
    monkeypatch.setattr(reader, "MAX_ZLIB_DECOMPRESSED", 1024)
    payload = b"A" * (1024 * 64)  # 64 KB, well over the 1 KB cap
    stream = GmkStream(_block(payload))
    with pytest.raises(GmkReadError):
        stream.read_zlib_data()


def test_block_exactly_at_cap_ok(monkeypatch):
    monkeypatch.setattr(reader, "MAX_ZLIB_DECOMPRESSED", 4096)
    payload = b"B" * 4096
    stream = GmkStream(_block(payload))
    assert stream.read_zlib_data() == payload


def test_empty_block():
    stream = GmkStream(struct.pack("<i", 0))
    assert stream.read_zlib_data() == b""
