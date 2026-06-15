"""Regression test for audit finding M25.

docs/FULL_AUDIT_2026-06-11.md M25: the eyedropper draws on the canvas if the
user drags while picking. SpriteCanvas.mousePressEvent emits color_picked
synchronously while self._painting is True; the slot _on_color_picked called
self._select_tool("pencil") immediately, swapping canvas._current_tool in the
middle of the active gesture. canvas.mouseMoveEvent then dispatched on_move to
the freshly-reset PencilTool, scribbling Bresenham lines in the picked colour
along the drag path. A clean pick also pushed a SpriteEditCommand and emitted
data_modified, marking the sprite dirty and polluting the undo stack.

Our authoritative (HEAD) fix neutralizes the gesture rather than deferring the
switch: _on_color_picked still switches to pencil immediately, but
SpriteCanvas.set_tool sets self._painting = False, so the in-flight gesture
goes inert — subsequent mouseMoveEvents do not draw and mouseReleaseEvent does
not emit canvas_modified. A pure pick therefore leaves the image untouched and
pushes no undo command / fires no data_modified (the L16 no-op guard in
_on_canvas_modified also drops inert commands). These tests assert that
equivalent-correct behaviour against our implementation.

These tests construct a real offscreen QApplication (no pytest-qt) so they run
on Python 3.11 too.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    return app


def _make_editor(qapp):
    from editors.sprite_editor.sprite_editor_main import SpriteEditor
    from PySide6.QtGui import QImage, QColor

    editor = SpriteEditor()
    # Seed the canvas with a known 8x8 image: distinct colours so the picker
    # samples something and any stray pencil stroke would be detectable.
    img = QImage(8, 8, QImage.Format_ARGB32)
    img.fill(QColor(10, 20, 30, 255))
    img.setPixelColor(2, 2, QColor(200, 100, 50, 255))  # the pixel we sample
    editor.canvas.set_image(img)
    return editor


def _drive_pick_gesture(editor, pixels, monkeypatch):
    """Drive a real press/move(s)/release through the canvas event handlers,
    mapping every screen position to the given sequence of pixel coords."""
    from PySide6.QtCore import QPoint, Qt, QPointF
    from PySide6.QtGui import QMouseEvent

    canvas = editor.canvas
    seq = list(pixels)

    def fake_screen_to_pixel(_pos):
        return seq[min(_drive_pick_gesture._i, len(seq) - 1)]

    monkeypatch.setattr(canvas, "_screen_to_pixel", fake_screen_to_pixel)

    def evt(etype, button):
        pos = QPointF(1.0, 1.0)
        return QMouseEvent(etype, pos, button, button, Qt.NoModifier)

    from PySide6.QtCore import QEvent

    _drive_pick_gesture._i = 0
    canvas.mousePressEvent(evt(QEvent.MouseButtonPress, Qt.LeftButton))
    for idx in range(1, len(seq)):
        _drive_pick_gesture._i = idx
        canvas.mouseMoveEvent(evt(QEvent.MouseMove, Qt.NoButton))
    _drive_pick_gesture._i = len(seq) - 1
    canvas.mouseReleaseEvent(evt(QEvent.MouseButtonRelease, Qt.LeftButton))


class TestEyedropperDoesNotDraw:
    def test_pick_with_drag_leaves_image_untouched(self, qapp, monkeypatch):
        from PySide6.QtGui import QColor

        editor = _make_editor(qapp)
        editor._select_tool("color_picker")
        before = editor.canvas.get_image().copy()

        # Press on the sampled pixel, then drag across several other pixels.
        _drive_pick_gesture(
            editor, [(2, 2), (3, 3), (4, 4), (5, 5)], monkeypatch
        )

        # The eyedropper must not have painted anything along the drag path —
        # the point of the fix. Our implementation switches to pencil and
        # neutralizes the gesture on the press-time pick, so the drag is inert.
        assert editor.canvas.get_image() == before
        # The press at (2,2) sampled that pixel's colour into the foreground;
        # the subsequent (inert) drag does not re-pick.
        assert editor.color_palette.get_foreground() == QColor(200, 100, 50, 255)

    def test_pick_neutralizes_gesture_and_switches(self, qapp, monkeypatch):
        # Our implementation switches to pencil immediately on the pick, but
        # SpriteCanvas.set_tool clears _painting so the in-flight gesture goes
        # inert: a subsequent move cannot draw and the release is a no-op.
        editor = _make_editor(qapp)
        editor._select_tool("color_picker")

        from PySide6.QtCore import Qt, QPointF, QEvent
        from PySide6.QtGui import QMouseEvent

        canvas = editor.canvas
        monkeypatch.setattr(canvas, "_screen_to_pixel", lambda _p: (2, 2))
        before = canvas.get_image().copy()

        def evt(etype, button):
            return QMouseEvent(etype, QPointF(1.0, 1.0), button, button, Qt.NoModifier)

        # On press the color is picked and the tool switches to pencil, but the
        # active gesture is neutralized (set_tool cleared _painting).
        canvas.mousePressEvent(evt(QEvent.MouseButtonPress, Qt.LeftButton))
        assert editor._active_tool_name == "pencil"
        assert canvas._painting is False

        # A move during the (now inert) gesture must not draw.
        canvas.mouseMoveEvent(evt(QEvent.MouseMove, Qt.NoButton))
        assert canvas.get_image() == before

        # Release ends the gesture without emitting a modification.
        canvas.mouseReleaseEvent(evt(QEvent.MouseButtonRelease, Qt.LeftButton))
        assert editor._active_tool_name == "pencil"
        assert canvas.get_image() == before

    def test_clean_pick_does_not_dirty_or_push_undo(self, qapp, monkeypatch):
        editor = _make_editor(qapp)
        editor._select_tool("color_picker")

        dirtied = []
        editor.data_modified.connect(lambda name: dirtied.append(name))
        undo_count_before = editor.undo_stack.count()

        _drive_pick_gesture(editor, [(2, 2), (3, 3)], monkeypatch)

        # A pure pick is a no-op edit: no undo command, sprite not marked dirty.
        assert editor.undo_stack.count() == undo_count_before
        assert dirtied == []

    def test_switch_to_pencil_on_pick(self, qapp):
        # _on_color_picked auto-switches back to pencil after picking a color.
        from PySide6.QtGui import QColor

        editor = _make_editor(qapp)
        editor._select_tool("color_picker")
        assert editor.canvas._painting is False

        editor._on_color_picked(QColor(1, 2, 3, 255))
        assert editor._active_tool_name == "pencil"

    def test_pencil_drag_still_draws(self, qapp, monkeypatch):
        # Behaviour preservation: a normal pencil drag must still paint.
        from PySide6.QtGui import QColor

        editor = _make_editor(qapp)
        editor._select_tool("pencil")
        editor.canvas.set_color(QColor(0, 255, 0, 255))
        before = editor.canvas.get_image().copy()

        _drive_pick_gesture(editor, [(1, 1), (1, 2), (1, 3)], monkeypatch)

        assert editor.canvas.get_image() != before
        # And the draw was recorded on the undo stack + marked dirty.
        assert editor.undo_stack.count() >= 1
