"""Regression tests for Room Editor undo/redo correctness.

Audit M23 (docs/FULL_AUDIT_2026-06-11.md): Clear All / Shift All mutated the
instance list directly, bypassing the undo system — Clear All was unrevertible
and the stale undo stack would resurrect previously-deleted instances on Ctrl+Z.

Audit M24: AddInstanceCommand / BatchAddInstancesCommand / AddTileCommand /
BatchAddTilesCommand set already_added=True at push and never reset it, so
every Redo after Undo was a permanent no-op (paste/duplicate/paint lost).
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


def _canvas():
    from editors.room_editor.room_canvas import RoomCanvas
    return RoomCanvas()


def _inst(name="obj_a", x=0, y=0):
    from editors.room_editor.object_instance import ObjectInstance
    return ObjectInstance(name, x, y)


class TestClearAllUndo:
    def test_clear_all_is_undoable(self, _qapp):
        canvas = _canvas()
        canvas.instances.extend([_inst("a"), _inst("b"), _inst("c")])
        canvas.clear_instances()
        assert canvas.instances == []
        canvas.undo_stack.undo()
        assert len(canvas.instances) == 3

    def test_clear_all_does_not_resurrect_deleted_via_stale_stack(self, _qapp):
        canvas = _canvas()
        a, b = _inst("a"), _inst("b")
        canvas.instances.extend([a, b])
        # Delete a single instance through the undo system first.
        from editors.room_undo_commands import RemoveInstanceCommand
        canvas.undo_stack.push(RemoveInstanceCommand(canvas, a))
        assert a not in canvas.instances
        # Now Clear All.
        canvas.clear_instances()
        assert canvas.instances == []
        # One Ctrl+Z must restore the cleared layout (b), NOT resurrect 'a'.
        canvas.undo_stack.undo()
        assert b in canvas.instances
        assert a not in canvas.instances


class TestShiftAllUndo:
    def test_shift_all_is_undoable(self, _qapp):
        canvas = _canvas()
        i = _inst("a", 10, 20)
        canvas.instances.append(i)
        canvas.shift_all_instances(5, 7)
        assert (i.x, i.y) == (15, 27)
        canvas.undo_stack.undo()
        assert (i.x, i.y) == (10, 20)


class TestAddRedo:
    def test_add_instance_redo_after_undo(self, _qapp):
        from editors.room_undo_commands import AddInstanceCommand
        canvas = _canvas()
        i = _inst("a")
        canvas.instances.append(i)  # canvas pre-adds, like the live path
        canvas.undo_stack.push(AddInstanceCommand(canvas, i, already_added=True))
        assert i in canvas.instances
        canvas.undo_stack.undo()
        assert i not in canvas.instances
        canvas.undo_stack.redo()
        assert i in canvas.instances

    def test_batch_add_instances_redo_after_undo(self, _qapp):
        from editors.room_undo_commands import BatchAddInstancesCommand
        canvas = _canvas()
        items = [_inst("a"), _inst("b")]
        canvas.instances.extend(items)
        canvas.undo_stack.push(
            BatchAddInstancesCommand(canvas, items, already_added=True))
        canvas.undo_stack.undo()
        assert all(i not in canvas.instances for i in items)
        canvas.undo_stack.redo()
        assert all(i in canvas.instances for i in items)

    def test_add_tile_redo_after_undo(self, _qapp):
        from editors.room_undo_commands import AddTileCommand
        canvas = _canvas()
        tile = {"x": 0, "y": 0, "tile_x": 1, "tile_y": 1, "background": "bg"}
        canvas.tiles.append(tile)
        canvas.undo_stack.push(AddTileCommand(canvas, tile, already_added=True))
        canvas.undo_stack.undo()
        assert tile not in canvas.tiles
        canvas.undo_stack.redo()
        assert tile in canvas.tiles

    def test_batch_add_tiles_redo_after_undo(self, _qapp):
        from editors.room_undo_commands import BatchAddTilesCommand
        canvas = _canvas()
        tiles = [{"x": 0, "y": 0}, {"x": 1, "y": 0}]
        canvas.tiles.extend(tiles)
        canvas.undo_stack.push(
            BatchAddTilesCommand(canvas, tiles, already_added=True))
        canvas.undo_stack.undo()
        assert all(t not in canvas.tiles for t in tiles)
        canvas.undo_stack.redo()
        assert all(t in canvas.tiles for t in tiles)
