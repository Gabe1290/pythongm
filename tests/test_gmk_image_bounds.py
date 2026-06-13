"""Regression test for unbounded GMK image dimensions (audit M40).

_bgra_to_image computed width*height*4 and padded a short pixel buffer to that
size with no upper bound on the dimensions (parsed as int32), so a malicious
.gmk declaring e.g. 40000x40000 with a few bytes of data forced multi-GB
allocations and OOM. Dimensions are now validated before allocation.
"""

import pytest

from importers.gmk_converter import (
    GmkConverter,
    _check_image_dimensions,
    MAX_IMAGE_DIMENSION,
)


class TestCheckImageDimensions:
    def test_accepts_normal(self):
        _check_image_dimensions(32, 32)
        _check_image_dimensions(MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION)

    def test_rejects_oversized(self):
        with pytest.raises(ValueError):
            _check_image_dimensions(40000, 40000)

    def test_rejects_oversized_one_axis(self):
        with pytest.raises(ValueError):
            _check_image_dimensions(MAX_IMAGE_DIMENSION + 1, 16)

    def test_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            _check_image_dimensions(0, 16)
        with pytest.raises(ValueError):
            _check_image_dimensions(-1, 16)


class TestBgraToImage:
    def _converter(self, tmp_path):
        # GmkConverter only needs a project + output dir; we call the image
        # helper directly, so a bare object is enough.
        conv = GmkConverter.__new__(GmkConverter)
        return conv

    def test_oversized_raises_before_allocation(self, tmp_path):
        conv = self._converter(tmp_path)
        # A tiny buffer claiming 40000x40000 must raise, not allocate ~6.4 GB.
        with pytest.raises(ValueError):
            conv._bgra_to_image(b"\x00\x00\x00\x00", 40000, 40000)

    def test_valid_dimensions_work(self, tmp_path):
        conv = self._converter(tmp_path)
        img = conv._bgra_to_image(b"\x00" * (2 * 2 * 4), 2, 2)
        assert img.size == (2, 2)
        assert img.mode == "RGBA"
