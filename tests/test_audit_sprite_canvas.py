"""Regression tests for sprite_canvas.py audit findings L15 and L16.

L15: _screen_to_pixel must floor (not truncate toward zero) so a screen
     position just left of / above the image maps to a negative coordinate
     the bounds checks reject, instead of snapping to column/row 0.
L16: mouseReleaseEvent must only emit canvas_modified when the gesture
     actually changed pixels — selection marquees and color-picker clicks
     leave the image untouched and must not dirty the sprite / push an undo.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QMouseEvent
from PySide6.QtCore import QEvent

from editors.sprite_editor.sprite_canvas import SpriteCanvas
from editors.sprite_editor.sprite_tools import (
    PencilTool, SelectTool, ColorPickerTool,
)


def _app():
    return QApplication.instance() or QApplication([])


def test_screen_to_pixel_floors_left_of_image():
    """L15: a click just left of the image must map to a negative x."""
    _app()
    canvas = SpriteCanvas()
    canvas.set_zoom(10)
    ox, oy = canvas._origin()

    # 9 screen-pixels left of the image's left edge: int() would give 0
    # (in-bounds), floor must give -1 (rejected by bounds checks).
    px, py = canvas._screen_to_pixel(QPoint(ox - 9, oy + 5))
    assert px == -1, f"expected -1, got {px}"

    # Just above the top edge, same band.
    px2, py2 = canvas._screen_to_pixel(QPoint(ox + 5, oy - 9))
    assert py2 == -1, f"expected -1, got {py2}"


def test_screen_to_pixel_inside_image_unchanged():
    """L15: in-bounds positions still map correctly (no regression)."""
    _app()
    canvas = SpriteCanvas()
    canvas.set_zoom(10)
    ox, oy = canvas._origin()

    # Exactly on the image origin -> (0, 0)
    assert canvas._screen_to_pixel(QPoint(ox, oy)) == (0, 0)
    # Inside the 3rd column / 4th row
    assert canvas._screen_to_pixel(QPoint(ox + 25, oy + 35)) == (2, 3)


def _press_release(canvas, px, py):
    """Drive a left-button press+release at image-pixel (px, py)."""
    ox, oy = canvas._origin()
    z = canvas.get_zoom()
    pos = QPoint(ox + px * z + z // 2, oy + py * z + z // 2)
    press = QMouseEvent(
        QEvent.MouseButtonPress, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier
    )
    release = QMouseEvent(
        QEvent.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier
    )
    canvas.mousePressEvent(press)
    canvas.mouseReleaseEvent(release)


def test_pencil_stroke_emits_modified():
    """L16 control: a real pencil stroke that changes pixels still emits."""
    _app()
    canvas = SpriteCanvas()
    canvas.set_zoom(10)
    canvas.set_color(QColor(255, 0, 0, 255))
    canvas.set_tool(PencilTool())

    emitted = []
    canvas.canvas_modified.connect(lambda: emitted.append(True))

    _press_release(canvas, 5, 5)
    assert emitted, "pencil stroke that drew a pixel must emit canvas_modified"


def test_select_marquee_does_not_emit_modified():
    """L16: a selection marquee changes no pixels -> no canvas_modified."""
    _app()
    canvas = SpriteCanvas()
    canvas.set_zoom(10)
    canvas.set_tool(SelectTool())

    emitted = []
    canvas.canvas_modified.connect(lambda: emitted.append(True))

    _press_release(canvas, 3, 3)
    assert not emitted, "selection marquee must not emit canvas_modified"
    # Snapshot must be dropped so a later gesture can't pick it up stale.
    assert canvas.get_stroke_snapshot() is None


def test_color_picker_does_not_emit_modified():
    """L16: a color-picker click changes no pixels -> no canvas_modified."""
    _app()
    canvas = SpriteCanvas()
    canvas.set_zoom(10)
    canvas.set_tool(ColorPickerTool())

    emitted = []
    canvas.canvas_modified.connect(lambda: emitted.append(True))

    _press_release(canvas, 4, 4)
    assert not emitted, "color picker click must not emit canvas_modified"
    assert canvas.get_stroke_snapshot() is None
