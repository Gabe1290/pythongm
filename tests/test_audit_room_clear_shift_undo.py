"""
Regression test for M23: Clear All / Shift All in the room editor must route
through the QUndoStack so they are reversible AND so they don't leave a stale
undo history that can resurrect removed instances on a later Ctrl+Z.

Before the fix, clear_all_instances() called room_canvas.clear_instances()
(which empties the list directly) and shift_all_instances() called
room_canvas.shift_all_instances(dx, dy) (which mutates x/y directly). Neither
pushed an undo command, so:
  - Clear All was the only destructive room op Ctrl+Z couldn't revert, and
  - a prior RemoveInstanceCommand on the stack could re-append its held
    instance into the supposedly-empty room on undo.

This exercises the actual RoomEditor methods (dialogs monkeypatched to auto-
confirm), constructing a real offscreen QApplication so it runs on 3.11 too.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _make_editor(tmp_path):
    from editors.room_editor import RoomEditor
    from editors.room_editor.object_instance import ObjectInstance

    editor = RoomEditor(str(tmp_path))
    canvas = editor.room_canvas
    canvas.instances.append(ObjectInstance("player", 10, 20))
    canvas.instances.append(ObjectInstance("wall", 30, 40))
    canvas.instances.append(ObjectInstance("wall", 50, 60))
    return editor, canvas


def test_clear_all_is_undoable(_qapp, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    editor, canvas = _make_editor(tmp_path)
    assert len(canvas.instances) == 3

    monkeypatch.setattr(QMessageBox, "question",
                        staticmethod(lambda *a, **k: QMessageBox.Yes))

    editor.clear_all_instances()
    assert len(canvas.instances) == 0
    # The clear must have pushed an undo command.
    assert canvas.undo_stack.canUndo()

    canvas.undo_stack.undo()
    assert len(canvas.instances) == 3
    names = sorted(i.object_name for i in canvas.instances)
    assert names == ["player", "wall", "wall"]

    # And redo re-clears.
    canvas.undo_stack.redo()
    assert len(canvas.instances) == 0


def test_clear_all_does_not_resurrect_previously_removed_instance(_qapp, tmp_path, monkeypatch):
    """The core M23 failure: delete one instance (undoable), then Clear All,
    then Ctrl+Z should restore the cleared layout — NOT pop the single
    previously-deleted instance into an otherwise-empty room."""
    from PySide6.QtWidgets import QMessageBox
    from editors.room_undo_commands import RemoveInstanceCommand

    editor, canvas = _make_editor(tmp_path)

    # Delete one instance through the undo stack (as a single delete does).
    victim = canvas.instances[0]
    canvas.undo_stack.push(RemoveInstanceCommand(canvas, victim))
    assert len(canvas.instances) == 2

    monkeypatch.setattr(QMessageBox, "question",
                        staticmethod(lambda *a, **k: QMessageBox.Yes))
    editor.clear_all_instances()
    assert len(canvas.instances) == 0

    # First Ctrl+Z must restore the cleared layout (the 2 remaining), not
    # walk back past the clear into the stale delete.
    canvas.undo_stack.undo()
    assert len(canvas.instances) == 2, (
        "Clear All undo must restore the cleared layout, not resurrect a "
        "previously-deleted instance"
    )


def test_shift_all_is_undoable(_qapp, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QDialog

    editor, canvas = _make_editor(tmp_path)
    originals = [(i.x, i.y) for i in canvas.instances]

    # Drive the modal shift dialog headlessly: patch QDialog.exec to fill the
    # X/Y offset spinboxes (creation order) and return Accepted.
    from PySide6.QtWidgets import QSpinBox

    def fake_exec(self):
        spins = self.findChildren(QSpinBox)
        # First spin is X offset, second is Y offset (creation order).
        spins[0].setValue(5)
        spins[1].setValue(7)
        return QDialog.Accepted

    monkeypatch.setattr(QDialog, "exec", fake_exec)

    editor.shift_all_instances()

    for (ox, oy), inst in zip(originals, canvas.instances):
        assert (inst.x, inst.y) == (ox + 5, oy + 7)
    assert canvas.undo_stack.canUndo()

    canvas.undo_stack.undo()
    for (ox, oy), inst in zip(originals, canvas.instances):
        assert (inst.x, inst.y) == (ox, oy)
