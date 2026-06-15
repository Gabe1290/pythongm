#!/usr/bin/env python3
"""Regression test for L11 (2026-06-11 audit):

PlaygroundEditor.undo()/redo() must re-sync the properties panel to the
selected element. Previously the canvas reverted but the panel kept the stale
pre-undo value, so the next spinbox tick stepped from the stale value
(undoing a 100->200 X change then nudging up jumped to 200.1 instead of 101).
"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _make_editor(tmp_path):
    from editors.playground_editor import PlaygroundEditor
    return PlaygroundEditor(str(tmp_path))


def test_undo_property_change_resyncs_panel(tmp_path):
    _app()
    from editors.playground_editor.playground_elements import PlaygroundWall
    from editors.playground_editor.playground_undo_commands import (
        ModifyElementCommand,
    )

    editor = _make_editor(tmp_path)

    wall = PlaygroundWall(x=100, y=50)
    editor.canvas.walls.append(wall)
    editor.canvas.selected_elements = [wall]
    editor.element_properties.set_element(wall)

    # Panel reflects the starting X.
    assert editor.element_properties.wall_x.value() == 100

    # Apply a property change via a command (as _on_property_changed would),
    # then sync the panel to the new value.
    cmd = ModifyElementCommand(editor.canvas, wall, "x", 100, 200, "Change x")
    editor.canvas.undo_stack.push(cmd)
    editor.element_properties.set_element(wall)
    assert wall.x == 200
    assert editor.element_properties.wall_x.value() == 200

    # Undo: the element reverts AND the panel must re-sync.
    editor.undo()
    assert wall.x == 100
    assert editor.element_properties.wall_x.value() == 100, (
        "panel still shows the stale pre-undo X value"
    )

    # Redo: panel must follow forward too.
    editor.redo()
    assert wall.x == 200
    assert editor.element_properties.wall_x.value() == 200

    editor.deleteLater()


def test_undo_move_resyncs_panel(tmp_path):
    _app()
    from editors.playground_editor.playground_elements import PlaygroundWall
    from editors.playground_editor.playground_undo_commands import (
        MoveElementCommand,
    )

    editor = _make_editor(tmp_path)

    wall = PlaygroundWall(x=10, y=20)
    editor.canvas.walls.append(wall)
    editor.canvas.selected_elements = [wall]
    editor.element_properties.set_element(wall)

    cmd = MoveElementCommand(editor.canvas, wall, 10, 20, 300, 400, "Move")
    editor.canvas.undo_stack.push(cmd)
    assert (wall.x, wall.y) == (300, 400)

    editor.undo()
    assert (wall.x, wall.y) == (10, 20)
    assert editor.element_properties.wall_x.value() == 10
    assert editor.element_properties.wall_y.value() == 20

    editor.deleteLater()


def test_undo_with_no_selection_clears_panel(tmp_path):
    _app()
    from editors.playground_editor.playground_elements import PlaygroundWall
    from editors.playground_editor.playground_undo_commands import (
        ModifyElementCommand,
    )

    editor = _make_editor(tmp_path)

    wall = PlaygroundWall(x=100, y=50)
    editor.canvas.walls.append(wall)
    editor.element_properties.set_element(wall)

    cmd = ModifyElementCommand(editor.canvas, wall, "x", 100, 200, "Change x")
    editor.canvas.undo_stack.push(cmd)

    # No element selected on the canvas -> panel should clear, not crash.
    editor.canvas.selected_elements = []
    editor.undo()
    assert editor.element_properties.current_element is None

    editor.deleteLater()
