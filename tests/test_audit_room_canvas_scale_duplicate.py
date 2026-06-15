#!/usr/bin/env python3
"""Regression tests for room_canvas audit findings L12 and L13.

L12 — Instance hit-testing and selection highlight ignored scale, so scaled
      instances were unclickable over most of their visible area and the
      selection box outlined the wrong region.
L13 — Duplicate (Ctrl+D) clobbered the copy/paste clipboard.

Uses a real offscreen QApplication (no pytest-qt) so it runs on Python 3.11.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QRect, QPoint

from editors.room_editor.room_canvas import RoomCanvas
from editors.room_editor.object_instance import ObjectInstance


def _app():
    return QApplication.instance() or QApplication([])


def _make_instance(x, y, scale_x=1.0, scale_y=1.0, w=32, h=32):
    inst = ObjectInstance("obj_test", x, y)
    inst.scale_x = scale_x
    inst.scale_y = scale_y
    # draw_instance() normally stamps these; simulate that here.
    inst._sprite_width = w
    inst._sprite_height = h
    inst._origin_x = 0
    inst._origin_y = 0
    return inst


# ---------------------------------------------------------------------------
# L12
# ---------------------------------------------------------------------------

def test_footprint_rect_accounts_for_scale():
    _app()
    canvas = RoomCanvas()
    inst = _make_instance(100, 100, scale_x=2.0, scale_y=2.0, w=32, h=32)
    rect = canvas._instance_footprint(inst)
    # 32 * 2.0 = 64 in each dimension, top-left unchanged.
    assert rect == QRect(100, 100, 64, 64)


def test_hit_test_covers_scaled_right_half():
    _app()
    canvas = RoomCanvas()
    inst = _make_instance(100, 100, scale_x=2.0, scale_y=2.0, w=32, h=32)
    canvas.instances = [inst]
    # A point in the lower-right quarter of the drawn (scaled) sprite that
    # lies OUTSIDE the unscaled 32x32 rect but inside the 64x64 footprint.
    pt = QPoint(150, 150)
    assert canvas._instance_footprint(inst).contains(pt)
    assert canvas.find_instance_at(pt) is inst


def test_rubber_band_selects_scaled_instance():
    _app()
    canvas = RoomCanvas()
    inst = _make_instance(100, 100, scale_x=2.0, scale_y=2.0, w=32, h=32)
    canvas.instances = [inst]
    # A band that only intersects the scaled extent (x in 140..160),
    # outside the unscaled 32px rect (which ends at x=132).
    band = QRect(140, 140, 10, 10)
    assert inst in canvas.find_instances_in_rect(band)


def test_negative_scale_produces_positive_rect():
    _app()
    canvas = RoomCanvas()
    inst = _make_instance(100, 100, scale_x=-2.0, scale_y=1.0, w=32, h=32)
    rect = canvas._instance_footprint(inst)
    assert rect.width() == 64
    assert rect.height() == 32


def test_unit_scale_unchanged():
    _app()
    canvas = RoomCanvas()
    inst = _make_instance(50, 60, scale_x=1.0, scale_y=1.0, w=32, h=48)
    rect = canvas._instance_footprint(inst)
    assert rect == QRect(50, 60, 32, 48)


# ---------------------------------------------------------------------------
# L13
# ---------------------------------------------------------------------------

def test_duplicate_does_not_clobber_clipboard():
    _app()
    canvas = RoomCanvas()

    copied = _make_instance(10, 10)
    other = _make_instance(200, 200)
    canvas.instances = [copied, other]

    # User copies `copied`.
    canvas.selected_instances = [copied]
    assert canvas.copy_selected_instances() is True
    clipboard_after_copy = list(canvas.clipboard_instances)
    assert len(clipboard_after_copy) == 1
    assert clipboard_after_copy[0]["x"] == 10

    # User selects and duplicates an unrelated instance with Ctrl+D.
    canvas.selected_instances = [other]
    assert canvas.duplicate_selected_instances() is True

    # Clipboard must still hold the originally-copied instance, untouched.
    assert canvas.clipboard_instances == clipboard_after_copy
    assert canvas.clipboard_instances[0]["x"] == 10


def test_duplicate_still_creates_offset_copy():
    _app()
    canvas = RoomCanvas()
    inst = _make_instance(40, 40)
    canvas.instances = [inst]
    canvas.selected_instances = [inst]

    before = len(canvas.instances)
    assert canvas.duplicate_selected_instances() is True
    assert len(canvas.instances) == before + 1
    dup = canvas.selected_instances[0]
    assert dup is not inst
    assert dup.x == 40 + canvas.grid_size
    assert dup.y == 40 + canvas.grid_size


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
