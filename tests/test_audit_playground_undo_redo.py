"""
Regression test for audit M22 (docs/FULL_AUDIT_2026-06-11.md):

Redo after Undo of "Add Wall" / "Add Robot" never restored the element.
PlaygroundCanvas.add_wall/add_robot append the element themselves then push an
AddElementCommand with already_added=True (so the push-triggered first redo()
doesn't double-add). The flag was never reset, so after the user undid the add,
every subsequent redo() was a permanent no-op and the element was lost while the
undo-stack index still advanced.

The fix consumes the flag on the first redo so later redos actually re-append
the element and re-emit element_added.

Constructs a real (offscreen) QApplication rather than using pytest-qt, so it
runs on Python 3.11 too.
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


def _make_canvas(_qapp):
    from editors.playground_editor.playground_canvas import PlaygroundCanvas
    return PlaygroundCanvas()


def test_add_wall_undo_then_redo_restores_wall(_qapp):
    canvas = _make_canvas(_qapp)

    added = []
    canvas.element_added.connect(added.append)

    wall = canvas.add_wall()
    assert wall in canvas.walls
    assert canvas.undo_stack.canUndo()

    canvas.undo_stack.undo()
    assert wall not in canvas.walls
    assert canvas.undo_stack.canRedo()

    canvas.undo_stack.redo()
    assert wall in canvas.walls, "Redo must bring the wall back"

    # And undo/redo must keep working as a cycle.
    canvas.undo_stack.undo()
    assert wall not in canvas.walls
    canvas.undo_stack.redo()
    assert wall in canvas.walls


def test_add_robot_undo_then_redo_restores_robot(_qapp):
    canvas = _make_canvas(_qapp)

    robot = canvas.add_robot()
    assert robot in canvas.robots

    canvas.undo_stack.undo()
    assert robot not in canvas.robots

    canvas.undo_stack.redo()
    assert robot in canvas.robots, "Redo must bring the robot back"


def test_initial_push_does_not_double_add(_qapp):
    """The push-triggered first redo() must stay a no-op (no duplicate)."""
    canvas = _make_canvas(_qapp)

    wall = canvas.add_wall()
    assert canvas.walls.count(wall) == 1


def test_redo_reemits_element_added(_qapp):
    canvas = _make_canvas(_qapp)

    wall = canvas.add_wall()

    seen = []
    canvas.element_added.connect(seen.append)

    canvas.undo_stack.undo()
    assert seen == []  # undo must not emit element_added

    canvas.undo_stack.redo()
    assert seen == [wall], "Redo must re-emit element_added for the restored wall"
