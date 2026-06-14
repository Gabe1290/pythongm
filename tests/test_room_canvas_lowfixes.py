"""Regression tests for room editor L12 (scaled hit-test) and L13 (duplicate clipboard)."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _canvas():
    from editors.room_editor.room_canvas import RoomCanvas
    return RoomCanvas()


def _inst(name="a", x=0, y=0, sx=1.0, sy=1.0):
    from editors.room_editor.object_instance import ObjectInstance
    i = ObjectInstance(name, x, y)
    i.scale_x = sx
    i.scale_y = sy
    i._sprite_width = 32
    i._sprite_height = 32
    i._origin_x = 0
    i._origin_y = 0
    return i


class TestScaledHitTest:  # L12
    def test_click_in_scaled_region_hits(self, _qapp):
        from PySide6.QtCore import QPoint
        canvas = _canvas()
        inst = _inst(x=0, y=0, sx=2.0, sy=2.0)  # drawn 64x64
        canvas.instances.append(inst)
        # A point at (50, 50) is inside the 64x64 footprint but outside 32x32.
        assert canvas.find_instance_at(QPoint(50, 50)) is inst

    def test_unscaled_still_works(self, _qapp):
        from PySide6.QtCore import QPoint
        canvas = _canvas()
        inst = _inst(x=0, y=0)
        canvas.instances.append(inst)
        assert canvas.find_instance_at(QPoint(10, 10)) is inst
        assert canvas.find_instance_at(QPoint(50, 50)) is None


class TestDuplicateClipboard:  # L13
    def test_duplicate_preserves_clipboard(self, _qapp):
        canvas = _canvas()
        copied = _inst("copied", 5, 5)
        canvas.instances.append(copied)
        # User copies something.
        canvas.clipboard_instances = [copied.to_dict()]
        sentinel = list(canvas.clipboard_instances)

        # Duplicate a different instance.
        other = _inst("other", 100, 100)
        canvas.instances.append(other)
        canvas.selected_instances = [other]
        canvas.duplicate_selected_instances()

        # The clipboard must still hold the copied instance, not 'other'.
        assert canvas.clipboard_instances == sentinel
        assert canvas.clipboard_instances[0]["object_name"] == "copied"
