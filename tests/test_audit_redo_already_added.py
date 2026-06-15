"""Regression tests for M24: the already_added flag on room undo commands must
be consumed on the first (push-time) redo so that a later Ctrl+Y actually
re-adds the paste/duplicate/paint instances and tiles instead of being a
permanent no-op.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from editors.room_undo_commands import (  # noqa: E402
    AddInstanceCommand,
    BatchAddInstancesCommand,
    AddTileCommand,
    BatchAddTilesCommand,
)


class _FakeSignal:
    def __init__(self):
        self.emitted = []

    def emit(self, value):
        self.emitted.append(value)


class _FakeCanvas:
    """Minimal stand-in for RoomCanvas exposing only what the commands touch."""

    def __init__(self):
        self.instances = []
        self.selected_instances = []
        self.tiles = []
        self.instance_added = _FakeSignal()
        self._tile_layer_dirty = False

    def update(self):  # QTimer.singleShot(0, self.canvas.update) target
        pass


class _FakeInstance:
    def __init__(self, name="obj"):
        self.object_name = name
        self.x = 0
        self.y = 0

    def to_dict(self):
        return {"object_name": self.object_name, "x": self.x, "y": self.y}


def _simulate_push(canvas, command):
    """QUndoStack.push() immediately invokes redo() once. We mimic that, given
    the canvas has already appended the object (already_added=True path)."""
    command.redo()


def test_add_instance_redo_reappears_after_undo():
    canvas = _FakeCanvas()
    inst = _FakeInstance("wall")
    # Canvas appends before pushing the command (the real flow).
    canvas.instances.append(inst)

    cmd = AddInstanceCommand(canvas, inst, already_added=True)
    _simulate_push(canvas, cmd)  # push-time redo: must be a no-op
    assert canvas.instances == [inst]

    cmd.undo()
    assert inst not in canvas.instances

    cmd.redo()  # Ctrl+Y must bring it back
    assert inst in canvas.instances

    # Round-trips repeatedly.
    cmd.undo()
    assert inst not in canvas.instances
    cmd.redo()
    assert inst in canvas.instances


def test_batch_add_instances_redo_reappears_after_undo():
    canvas = _FakeCanvas()
    insts = [_FakeInstance(f"wall{i}") for i in range(5)]
    canvas.instances.extend(insts)

    cmd = BatchAddInstancesCommand(canvas, insts, already_added=True)
    _simulate_push(canvas, cmd)
    assert canvas.instances == insts

    cmd.undo()
    assert all(i not in canvas.instances for i in insts)

    cmd.redo()
    assert all(i in canvas.instances for i in insts)


def test_add_tile_redo_reappears_after_undo():
    canvas = _FakeCanvas()
    tile = {"background": "bg", "x": 16, "y": 16}
    canvas.tiles.append(tile)

    cmd = AddTileCommand(canvas, tile, already_added=True)
    _simulate_push(canvas, cmd)
    assert canvas.tiles == [tile]

    cmd.undo()
    assert tile not in canvas.tiles

    cmd.redo()
    assert tile in canvas.tiles


def test_batch_add_tiles_redo_reappears_after_undo():
    canvas = _FakeCanvas()
    tiles = [{"background": "bg", "x": x, "y": 0} for x in range(4)]
    canvas.tiles.extend(tiles)

    cmd = BatchAddTilesCommand(canvas, tiles, already_added=True)
    _simulate_push(canvas, cmd)
    assert canvas.tiles == tiles

    cmd.undo()
    assert all(t not in canvas.tiles for t in tiles)

    cmd.redo()
    assert all(t in canvas.tiles for t in tiles)


def test_first_redo_is_noop_no_duplicate_add():
    """The push-time redo must NOT double-add (already_added consumed, not
    ignored)."""
    canvas = _FakeCanvas()
    inst = _FakeInstance("wall")
    canvas.instances.append(inst)

    cmd = AddInstanceCommand(canvas, inst, already_added=True)
    cmd.redo()  # push-time
    assert canvas.instances.count(inst) == 1
    assert canvas.instance_added.emitted == []  # no spurious signal on push
