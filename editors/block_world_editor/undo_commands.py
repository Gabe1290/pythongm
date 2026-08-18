#!/usr/bin/env python3
"""Undo/redo for the Block World editor, matching
editors/room_undo_commands.py's shape: a QUndoCommand's constructor
snapshots what's needed to reverse the action, undo()/redo() mutate the
live state.

One SetBlockCommand class covers both place and break -- the plan doc's
own suggestion named two separate PlaceBlockCommand/RemoveBlockCommand
classes, but they'd be identical except for which of new_type/old_type is
None, so a single class parametrized by (new_type, old_type) avoids
duplicating that logic for no behavioural difference.
"""
from PySide6.QtGui import QUndoCommand

from extensions.block_world.state import (
    get_block, set_block, remove_block, to_block_list, load_block_list,
)


def _apply(room, x, y, z, block_type):
    if block_type is None:
        remove_block(room, x, y, z)
    else:
        set_block(room, x, y, z, block_type)


class SetBlockCommand(QUndoCommand):
    """Reversibly set (or clear, with new_type=None) one voxel cell.

    old_type is captured by the CALLER at the moment of the edit (not
    re-derived here), since by the time undo()/redo() run the cell's
    live contents no longer reflect what was there before the edit.
    """

    def __init__(self, room, x, y, z, new_type, old_type, description=None):
        if description is None:
            description = "Place Block" if new_type is not None else "Break Block"
        super().__init__(description)
        self.room = room
        self.x, self.y, self.z = x, y, z
        self.new_type = new_type
        self.old_type = old_type

    def undo(self):
        _apply(self.room, self.x, self.y, self.z, self.old_type)

    def redo(self):
        _apply(self.room, self.x, self.y, self.z, self.new_type)


def make_set_block_command(room, x, y, z, new_type, description=None):
    """Build a SetBlockCommand capturing the cell's CURRENT contents as
    old_type -- the usual way to construct one from a live edit (as
    opposed to a test constructing one directly with an explicit
    old_type)."""
    old_type = get_block(room, x, y, z)
    return SetBlockCommand(room, x, y, z, new_type, old_type, description=description)


class ClearWorldCommand(QUndoCommand):
    """Reversibly remove every block in the room -- mirrors
    editors/room_undo_commands.py's BatchRemoveInstancesCommand shape
    (Clear All routed through undo rather than mutating state directly,
    so it doesn't become the one destructive op Ctrl+Z can't revert).
    Captures the whole world via to_block_list/load_block_list rather
    than per-cell SetBlockCommands, since a world can have far more
    blocks than a user would want as individual undo steps."""

    def __init__(self, room, description="Clear World"):
        super().__init__(description)
        self.room = room
        self.previous_blocks = to_block_list(room)

    def undo(self):
        load_block_list(self.room, self.previous_blocks)

    def redo(self):
        load_block_list(self.room, [])
