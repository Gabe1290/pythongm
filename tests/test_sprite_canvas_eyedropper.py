"""Regression test for the sprite-editor eyedropper drag bug (audit M25).

The color picker emits color_picked synchronously from mousePressEvent while
_painting is True; the editor's slot auto-switches to Pencil via set_tool().
Before the fix, _painting stayed True, so subsequent mouseMoveEvents drew
Bresenham lines with the freshly-swapped Pencil along the drag path (and the
release marked the sprite modified on a clean pick). set_tool now clears
_painting, making a tool swap mid-gesture inert.
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


def test_set_tool_ends_active_gesture(_qapp):
    from editors.sprite_editor.sprite_canvas import SpriteCanvas
    from editors.sprite_editor.sprite_tools import ColorPickerTool, PencilTool

    canvas = SpriteCanvas()
    canvas.set_tool(ColorPickerTool())
    # Simulate being mid-gesture (what mousePressEvent sets).
    canvas._painting = True

    # The auto-switch that _on_color_picked performs.
    canvas.set_tool(PencilTool())

    assert canvas._painting is False, (
        "switching tools mid-gesture must end the active stroke so the new "
        "Pencil does not draw on subsequent moves")


def test_pick_then_drag_does_not_modify_image(_qapp):
    from PySide6.QtGui import QColor
    from editors.sprite_editor.sprite_canvas import SpriteCanvas
    from editors.sprite_editor.sprite_tools import ColorPickerTool, PencilTool

    canvas = SpriteCanvas()
    img = canvas.get_image()
    img.fill(QColor(0, 0, 0, 0))
    img.setPixelColor(5, 5, QColor(255, 0, 0, 255))  # the pixel to pick
    before = img.copy()

    canvas.set_tool(ColorPickerTool())
    canvas._painting = True
    # Editor swaps to pencil after a pick:
    canvas.set_tool(PencilTool())

    # A drag move arrives. The canvas guards on _painting, which is now False,
    # so no PencilTool stroke is dispatched and the image is untouched.
    if canvas._painting and canvas._current_tool:
        canvas._current_tool.on_move(canvas.get_image(), 10, 10,
                                     canvas._current_color)

    assert canvas.get_image() == before, "drag after pick must not draw"
