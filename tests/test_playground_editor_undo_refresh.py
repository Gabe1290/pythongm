"""Regression test for playground properties panel refresh on undo/redo (L11).

PlaygroundEditor.undo()/redo() ran the canvas undo stack but never refreshed the
element properties panel, so after undoing a move/property change the panel kept
showing the stale pre-undo value (and the next spinbox step jumped the element
from that stale base).
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


def test_undo_resyncs_properties_panel(_qapp, tmp_path):
    from editors.playground_editor import PlaygroundEditor
    from editors.playground_editor.playground_undo_commands import MoveElementCommand

    editor = PlaygroundEditor(str(tmp_path))
    robot = editor.canvas.add_robot()
    editor.canvas.selected_elements = [robot]

    # Record set_element calls.
    calls = []
    editor.element_properties.set_element = lambda el: calls.append(el)

    # Push a move command and undo it.
    robot.x, robot.y = 100, 100
    cmd = MoveElementCommand(editor.canvas, robot, 0, 0, 100, 100)
    editor.canvas.undo_stack.push(cmd)  # redo applies (x,y)=(100,100)
    calls.clear()

    editor.undo()  # reverts to (0, 0)
    assert robot.x == 0 and robot.y == 0
    # The panel must have been re-synced from the (now reverted) element.
    assert calls and calls[-1] is robot
