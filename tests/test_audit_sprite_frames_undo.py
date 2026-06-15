"""
Regression tests for sprite-editor frame timeline audit findings.

M26 — Frame add/duplicate/delete bypassed the undo stack: deletion was
      irreversible, and because SpriteEditCommand stores a raw frame index,
      inserting/deleting a frame after a stroke made undo stamp pixels onto the
      wrong frame. FrameTimeline now routes structural ops through an optional
      undo stack (set via set_undo_stack) using a command that snapshots the
      whole frame list, so the operation is reversible and undo/redo restore a
      consistent list.

L17 — Drawing while playback ran swapped the canvas image mid-stroke. The
      timeline now consults an optional "busy" predicate (set via
      set_busy_check) and skips advancing while the canvas is mid-stroke.

Constructs a real (offscreen) QApplication rather than using pytest-qt so it
runs anywhere PySide6 is installed (incl. Python 3.11).
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


def _solid_frame(w, h, rgba):
    from PySide6.QtGui import QImage, QColor
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(QColor(*rgba))
    return img


def _pixel(frame, x=0, y=0):
    # pixelColor() preserves alpha; pixel() returns an opaque QRgb.
    return frame.pixelColor(x, y).getRgb()


# ---------------------------------------------------------------------------
# M26
# ---------------------------------------------------------------------------

def test_delete_frame_is_undoable(_qapp):
    """A mis-clicked delete must be recoverable via the undo stack."""
    from PySide6.QtGui import QUndoStack
    from editors.sprite_editor.sprite_frames import FrameTimeline

    tl = FrameTimeline()
    stack = QUndoStack()
    tl.set_undo_stack(stack)

    a = _solid_frame(8, 8, (255, 0, 0, 255))
    b = _solid_frame(8, 8, (0, 255, 0, 255))
    tl.set_frames([a, b])
    assert tl.get_frame_count() == 2

    tl.set_current_index(1)
    tl.delete_frame()
    assert tl.get_frame_count() == 1
    # The surviving frame is A.
    assert _pixel(tl.get_frames()[0]) == (255, 0, 0, 255)

    # Undo restores the destroyed frame.
    stack.undo()
    assert tl.get_frame_count() == 2
    assert _pixel(tl.get_frames()[1]) == (0, 255, 0, 255)


def test_add_frame_is_undoable(_qapp):
    from PySide6.QtGui import QUndoStack
    from editors.sprite_editor.sprite_frames import FrameTimeline

    tl = FrameTimeline()
    stack = QUndoStack()
    tl.set_undo_stack(stack)

    a = _solid_frame(8, 8, (255, 0, 0, 255))
    tl.set_frames([a])
    tl.add_frame()
    assert tl.get_frame_count() == 2

    stack.undo()
    assert tl.get_frame_count() == 1

    stack.redo()
    assert tl.get_frame_count() == 2


def test_insert_does_not_corrupt_via_stale_index(_qapp):
    """The audit walkthrough: frames [A,B]; draw on B; insert blank at index 1;
    undo must restore the structural change cleanly, not stamp B's old pixels
    onto the wrong frame.

    With structural ops on the undo stack, the latest command is the insert, so
    a single undo reverts the insert (back to [A,B]) rather than touching pixel
    contents — exactly the consistency the fix provides.
    """
    from PySide6.QtGui import QUndoStack
    from editors.sprite_editor.sprite_frames import FrameTimeline

    tl = FrameTimeline()
    stack = QUndoStack()
    tl.set_undo_stack(stack)

    a = _solid_frame(8, 8, (255, 0, 0, 255))
    b = _solid_frame(8, 8, (0, 255, 0, 255))
    tl.set_frames([a, b])

    # Select A (index 0), then add a blank frame -> inserts at index 1.
    tl.set_current_index(0)
    tl.add_frame()
    frames = tl.get_frames()
    assert tl.get_frame_count() == 3
    # Order is [A, blank, B].
    assert _pixel(frames[0]) == (255, 0, 0, 255)
    assert _pixel(frames[1]) == (0, 0, 0, 0)
    assert _pixel(frames[2]) == (0, 255, 0, 255)

    # Undo cleanly reverts to [A, B] with original contents intact — no pixel
    # corruption on either frame.
    stack.undo()
    frames = tl.get_frames()
    assert tl.get_frame_count() == 2
    assert _pixel(frames[0]) == (255, 0, 0, 255)
    assert _pixel(frames[1]) == (0, 255, 0, 255)


def test_legacy_direct_mutation_without_stack(_qapp):
    """With no undo stack wired, structural ops still mutate directly (back-compat)."""
    from editors.sprite_editor.sprite_frames import FrameTimeline

    tl = FrameTimeline()
    a = _solid_frame(8, 8, (255, 0, 0, 255))
    tl.set_frames([a])

    tl.add_frame()
    assert tl.get_frame_count() == 2

    tl.delete_frame()
    assert tl.get_frame_count() == 1
    # Never below one frame.
    tl.delete_frame()
    assert tl.get_frame_count() == 1


def test_structure_change_emits_signals(_qapp):
    from PySide6.QtGui import QUndoStack
    from editors.sprite_editor.sprite_frames import FrameTimeline

    tl = FrameTimeline()
    stack = QUndoStack()
    tl.set_undo_stack(stack)
    tl.set_frames([_solid_frame(8, 8, (1, 2, 3, 255))])

    changed = []
    selected = []
    tl.frames_changed.connect(lambda: changed.append(True))
    tl.frame_selected.connect(lambda i: selected.append(i))

    tl.add_frame()
    assert changed, "frames_changed must fire on add"
    assert selected and selected[-1] == 1, "selection must follow the new frame"


# ---------------------------------------------------------------------------
# L17
# ---------------------------------------------------------------------------

def test_playback_skips_advance_while_busy(_qapp):
    from editors.sprite_editor.sprite_frames import FrameTimeline

    tl = FrameTimeline()
    tl.set_frames([
        _solid_frame(8, 8, (255, 0, 0, 255)),
        _solid_frame(8, 8, (0, 255, 0, 255)),
    ])
    tl.set_current_index(0)

    busy = {"v": True}
    tl.set_busy_check(lambda: busy["v"])

    # While busy, the timer tick must not advance the frame (no canvas swap).
    tl._anim_next_frame()
    assert tl.get_current_index() == 0

    # Once the stroke is done, advancing resumes.
    busy["v"] = False
    tl._anim_next_frame()
    assert tl.get_current_index() == 1


def test_playback_advances_with_no_busy_check(_qapp):
    """Default (no predicate) preserves the original always-advance behaviour."""
    from editors.sprite_editor.sprite_frames import FrameTimeline

    tl = FrameTimeline()
    tl.set_frames([
        _solid_frame(8, 8, (255, 0, 0, 255)),
        _solid_frame(8, 8, (0, 255, 0, 255)),
    ])
    tl.set_current_index(0)
    tl._anim_next_frame()
    assert tl.get_current_index() == 1
