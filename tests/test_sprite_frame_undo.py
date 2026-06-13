"""Regression test for sprite-editor frame undo (audit M26).

add_frame / duplicate_frame / delete_frame mutated the frame list directly and
only emitted frames_changed — no undo command was pushed, so frame deletion
was irreversible. The timeline now calls an _undo_hook the editor wires to a
FrameEditCommand, making the structural frame ops undoable.
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


def _make_editor():
    """Minimal stand-in wiring the timeline to a real FrameEditCommand."""
    from PySide6.QtGui import QImage, QColor, QUndoStack
    from editors.sprite_editor.sprite_frames import FrameTimeline
    from editors.sprite_editor.sprite_canvas import SpriteCanvas
    from editors.sprite_editor.sprite_editor_main import FrameEditCommand

    class _Editor:
        def __init__(self):
            self.frame_timeline = FrameTimeline()
            self.canvas = SpriteCanvas()
            self.undo_stack = QUndoStack()
            self.frame_timeline._undo_hook = self._record

        def _record(self, of, oi, nf, ni, desc):
            self.undo_stack.push(
                FrameEditCommand(self, of, nf, oi, ni, desc))

    ed = _Editor()
    # Seed with one solid frame so we can detect it surviving an undo.
    img = QImage(8, 8, QImage.Format_ARGB32)
    img.fill(QColor(10, 20, 30, 255))
    ed.frame_timeline.set_frames([img])
    return ed


def test_delete_frame_is_undoable(_qapp):
    ed = _make_editor()
    ed.frame_timeline.add_frame()  # now 2 frames, current = index 1
    assert ed.frame_timeline.get_frame_count() == 2

    ed.frame_timeline.set_current_index(0)
    ed.frame_timeline.delete_frame()  # delete the original artwork frame
    assert ed.frame_timeline.get_frame_count() == 1

    ed.undo_stack.undo()  # restore deleted frame
    assert ed.frame_timeline.get_frame_count() == 2


def test_add_frame_undo_redo(_qapp):
    ed = _make_editor()
    ed.frame_timeline.add_frame()
    assert ed.frame_timeline.get_frame_count() == 2
    ed.undo_stack.undo()
    assert ed.frame_timeline.get_frame_count() == 1
    ed.undo_stack.redo()
    assert ed.frame_timeline.get_frame_count() == 2


def test_duplicate_frame_undo(_qapp):
    ed = _make_editor()
    ed.frame_timeline.duplicate_frame()
    assert ed.frame_timeline.get_frame_count() == 2
    ed.undo_stack.undo()
    assert ed.frame_timeline.get_frame_count() == 1


def test_no_hook_still_mutates_directly(_qapp):
    """Standalone timeline (no editor) keeps its old direct-mutation behavior."""
    from PySide6.QtGui import QImage
    from editors.sprite_editor.sprite_frames import FrameTimeline
    tl = FrameTimeline()
    tl.set_frames([QImage(8, 8, QImage.Format_ARGB32)])
    tl.add_frame()
    assert tl.get_frame_count() == 2  # direct mutation, no hook needed
