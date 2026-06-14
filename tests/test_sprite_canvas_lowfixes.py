"""Regression tests for sprite editor L15/L16/L17.

L15: _screen_to_pixel truncated toward zero, so clicks just left/above the image
mapped to edge pixel 0 instead of -1.
L16: canvas_modified pushed inert undo commands / dirtied the sprite for
selection marquees and picker clicks (no pixel change).
L17: a stroke must stop animation playback so frame switches don't swap the
canvas image mid-stroke.
"""

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


class TestScreenToPixelFloor:  # L15
    def test_just_left_of_image_is_negative(self, _qapp):
        from PySide6.QtCore import QPoint
        from editors.sprite_editor.sprite_canvas import SpriteCanvas
        canvas = SpriteCanvas()
        canvas.set_zoom(10)
        ox, oy = canvas._origin()
        # 9px left of the image left edge at zoom 10 -> floor(-0.9) = -1.
        x, y = canvas._screen_to_pixel(QPoint(ox - 9, oy + 5))
        assert x == -1
        assert y == 0

    def test_inside_image_positive(self, _qapp):
        from PySide6.QtCore import QPoint
        from editors.sprite_editor.sprite_canvas import SpriteCanvas
        canvas = SpriteCanvas()
        canvas.set_zoom(10)
        ox, oy = canvas._origin()
        x, y = canvas._screen_to_pixel(QPoint(ox + 25, oy + 35))
        assert (x, y) == (2, 3)


class TestNoOpGesture:  # L16
    def test_unchanged_image_pushes_no_command(self, _qapp):
        from editors.sprite_editor.sprite_editor_main import SpriteEditor
        editor = SpriteEditor()
        # Snapshot equals current image (no pixels changed).
        editor.canvas.take_stroke_snapshot()
        before = editor.undo_stack.count()
        editor._on_canvas_modified()
        assert editor.undo_stack.count() == before  # no inert command pushed

    def test_real_change_pushes_command(self, _qapp):
        from PySide6.QtGui import QColor
        from editors.sprite_editor.sprite_editor_main import SpriteEditor
        editor = SpriteEditor()
        editor.canvas.take_stroke_snapshot()
        img = editor.canvas.get_image()
        img.setPixelColor(1, 1, QColor(255, 0, 0, 255))  # actually change a pixel
        before = editor.undo_stack.count()
        editor._on_canvas_modified()
        assert editor.undo_stack.count() == before + 1


class TestStopPlaybackOnStroke:  # L17
    def test_stroke_started_stops_playback(self, _qapp):
        from PySide6.QtCore import QPoint, Qt
        from PySide6.QtGui import QMouseEvent
        from editors.sprite_editor.sprite_editor_main import SpriteEditor
        editor = SpriteEditor()
        editor.frame_timeline._playing = True
        editor.canvas.stroke_started.emit()
        assert editor.frame_timeline._playing is False
