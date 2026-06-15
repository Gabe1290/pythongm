"""Regression tests for L26 (FULL_AUDIT_2026-06-11).

importers.gmk_parser._bmp_to_bgra reads width/height from a BMP header that, in
the pre-v800 .gmk path, comes out of an untrusted zlib block. Before the fix a
header could declare enormous dimensions (e.g. 46340x46340) and force an ~8.6 GB
allocation + ~2.1 billion-iteration pure-Python loop, hanging/OOMing the IDE.

These are pure-logic tests (no Qt needed).
"""

import struct
import time

import pytest

from importers.gmk_parser import (
    _bmp_to_bgra,
    _BMP_MAX_DIMENSION,
)


def _make_bmp(width, height, bpp=24, pixel_bytes=None):
    """Build a minimal BMP. width/height go straight into the header at the
    offsets _bmp_to_bgra reads (18 and 22); pixel_bytes lets us understate the
    actual pixel data relative to the declared dimensions."""
    channels = bpp // 8
    row_size = (abs(width) * channels + 3) & ~3 if width > 0 else channels
    if pixel_bytes is None:
        pixel_bytes = b"\x00" * (row_size * abs(height))
    header_size = 54
    data_offset = header_size
    file_size = header_size + len(pixel_bytes)

    header = bytearray(header_size)
    header[0:2] = b"BM"
    struct.pack_into("<I", header, 2, file_size)
    struct.pack_into("<I", header, 10, data_offset)
    struct.pack_into("<I", header, 14, 40)  # info header size
    struct.pack_into("<i", header, 18, width)
    struct.pack_into("<i", header, 22, height)
    struct.pack_into("<H", header, 26, 1)   # planes
    struct.pack_into("<H", header, 28, bpp)
    return bytes(header) + pixel_bytes


def test_valid_small_bmp_still_parses():
    """A legitimate small BMP must still round-trip."""
    w, h = 4, 3
    bmp = _make_bmp(w, h, bpp=24)
    ow, oh, bgra = _bmp_to_bgra(bmp, transparent=False)
    assert ow == w
    assert oh == h
    assert len(bgra) == w * h * 4


def test_negative_height_topdown_still_parses():
    """Negative height (top-down BMP) is legal and must still work."""
    w, h = 4, -3
    bmp = _make_bmp(w, h, bpp=24)
    ow, oh, bgra = _bmp_to_bgra(bmp, transparent=False)
    assert ow == 4
    assert oh == 3
    assert len(bgra) == 4 * 3 * 4


def test_huge_dimensions_rejected_fast():
    """A header declaring 46340x46340 with no real pixel data must be rejected
    quickly (ValueError) rather than allocating GBs / looping billions."""
    bmp = _make_bmp(46340, 46340, bpp=24, pixel_bytes=b"\x00" * 16)
    start = time.monotonic()
    with pytest.raises(ValueError):
        _bmp_to_bgra(bmp, transparent=False)
    elapsed = time.monotonic() - start
    # Must fail essentially instantly, well before any pixel loop could run.
    assert elapsed < 1.0


def test_dimension_over_max_rejected():
    """Any single edge above the cap is rejected even if area math would pass."""
    over = _BMP_MAX_DIMENSION + 1
    # Provide plenty of pixel data so it's the dimension cap, not the area
    # check, that rejects it.
    row_size = (over * 3 + 3) & ~3
    bmp = _make_bmp(over, 1, bpp=24, pixel_bytes=b"\x00" * row_size)
    with pytest.raises(ValueError):
        _bmp_to_bgra(bmp, transparent=False)


def test_area_far_exceeds_data_rejected():
    """Dimensions under the per-edge cap but declaring far more pixel data than
    is present (the mid-band crafted case) must also be rejected."""
    # 4096x4096x3 ~= 48 MB declared, but only a handful of bytes present.
    bmp = _make_bmp(4096, 4096, bpp=24, pixel_bytes=b"\x00" * 32)
    with pytest.raises(ValueError):
        _bmp_to_bgra(bmp, transparent=False)


def test_zero_dimension_rejected():
    bmp = _make_bmp(0, 10, bpp=24, pixel_bytes=b"\x00" * 64)
    with pytest.raises(ValueError):
        _bmp_to_bgra(bmp, transparent=False)
