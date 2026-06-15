"""Regression tests for M40 — unbounded image dimensions in the GMK converter.

A .gmk is an untrusted foreign format whose sprite/background frames store
width/height as bare int32s (the parser only guards width>0 / height>0) with
the pixel-data length in a separate field. A malicious/corrupt file can declare
enormous dimensions backed by a few bytes of pixel data; the old
``_bgra_to_image`` would then allocate ``width*height*4`` bytes (twice) and run
a ``width*height``-iteration channel-swap loop, OOM-killing the IDE.

These tests exercise pure logic (no Qt / pygame), so they run on 3.11.
"""

import time

import pytest

from importers.gmk_converter import (
    GmkConverter,
    MAX_IMAGE_DIMENSION,
    _check_image_dimensions,
)


def _make_converter():
    # __init__ only stashes its argument; no parsing happens until convert().
    return GmkConverter.__new__(GmkConverter)


def test_huge_dimensions_with_tiny_buffer_rejected_fast():
    """The headline attack: 40000x40000 declared, 4 bytes of pixels."""
    conv = _make_converter()
    start = time.monotonic()
    with pytest.raises(ValueError):
        conv._bgra_to_image(b"\x00\x00\x00\x00", 40000, 40000)
    # Must fail without allocating ~6.4 GB or looping ~1.6e9 times.
    assert time.monotonic() - start < 1.0


def test_dimension_over_limit_rejected_even_with_data():
    """Past the per-side cap is rejected before any allocation."""
    conv = _make_converter()
    w = MAX_IMAGE_DIMENSION + 1
    with pytest.raises(ValueError):
        # Pretend the data is full-size so the short-buffer check can't fire.
        conv._bgra_to_image(b"\x00" * 16, w, 1)


def test_non_positive_dimensions_rejected():
    conv = _make_converter()
    for w, h in [(0, 10), (10, 0), (-5, 10), (10, -5)]:
        with pytest.raises(ValueError):
            conv._bgra_to_image(b"\x00" * 64, w, h)


def test_non_integer_dimensions_rejected():
    conv = _make_converter()
    with pytest.raises(ValueError):
        conv._bgra_to_image(b"\x00" * 64, 4.0, 4)


def test_grossly_short_buffer_still_pads():
    """RETARGETED to our HEAD design: M40 caps the DIMENSIONS (so the
    allocation can't OOM) but treats any short pixel buffer as data to PAD with
    transparent pixels rather than rejecting it. The remote variant rejected a
    >50%-missing buffer as hostile; our authoritative implementation pads it,
    which is safe because the dimensions are already bounded by
    MAX_IMAGE_DIMENSION. A 64x64 frame with only 100 bytes still produces a
    valid 64x64 image whose unfilled tail is transparent black."""
    conv = _make_converter()
    # 64x64 RGBA = 16384 bytes; supply only 100.
    img = conv._bgra_to_image(b"\x00" * 100, 64, 64)
    assert img.size == (64, 64)
    # The far corner is in the padded (all-zero) region.
    assert img.getpixel((63, 63)) == (0, 0, 0, 0)


def test_valid_frame_still_converts():
    """Legitimate full-size frames convert and swap B/R channels."""
    conv = _make_converter()
    # One opaque pixel, BGRA = (B=1, G=2, R=3, A=255).
    img = conv._bgra_to_image(bytes([1, 2, 3, 255]), 1, 1)
    assert img.size == (1, 1)
    # After BGRA -> RGBA the channels are (R=3, G=2, B=1, A=255).
    assert img.getpixel((0, 0)) == (3, 2, 1, 255)


def test_slightly_short_buffer_still_pads():
    """A modestly-short buffer (<= half missing) is still padded, not rejected."""
    conv = _make_converter()
    # 2x2 RGBA = 16 bytes; supply 12 (one pixel short). Within tolerance.
    data = bytes([10, 20, 30, 255]) * 3
    img = conv._bgra_to_image(data, 2, 2)
    assert img.size == (2, 2)
    # The padded last pixel is fully transparent black.
    assert img.getpixel((1, 1)) == (0, 0, 0, 0)


def test_validate_dimensions_guards_strip_preallocation():
    """The multi-frame strip path validates per-frame dims up front so the
    Image.new(strip_width, frame_h) allocation can't OOM.

    RETARGETED: our HEAD names the guard ``_check_image_dimensions`` (a
    module-level helper) rather than a ``_validate_image_dimensions`` method,
    but the behaviour is identical — raise on absurd dims, pass on sane ones."""
    with pytest.raises(ValueError):
        _check_image_dimensions(40000, 40000)
    # And a sane size passes.
    _check_image_dimensions(32, 48)
