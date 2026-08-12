#!/usr/bin/env python3
"""Block World: a voxel block-building extension (Phase 2a of docs/VOXEL_WORLD_PLAN.md).

Working name only -- never use "Minecraft" anywhere in this extension (see
the plan doc's naming section): it's a trademark, and the goal is the same
"inspired by, not copied from" territory Luanti/Minetest itself occupies, not
a clone wearing someone else's name.

Phase 2a status: the per-room world data model + CC0 block texture registry
(state.py), a flat single-layer first-person voxel renderer (renderer.py),
and the one action needed to turn it on (enable_block_world_view,
actions.py/handlers.py). There is still no place_block/break_block, no
hotbar, no collision (Phase 3/4) -- a room can be lit up and looked at, not
yet played in.

The one hook this extension declares is a room renderer
(runtime/extension_hooks.py): when a room's block-world camera says the
first-person view is on, render_room claims the room and draws it instead
of the engine's top-down pass -- mirrors extensions/raycast_2_5d/__init__.py
exactly. The renderer is imported lazily, on the first claimed frame, so the
IDE (which loads extensions only for their schemas) never pays for a pygame
import.
"""

PLUGIN_NAME = "Block World"

from .actions import PLUGIN_ACTIONS
from .handlers import PluginExecutor
from .state import peek_camera


def render_room(room, screen):
    """Room-renderer hook: claim the room iff its block-world camera is
    enabled. Non-creating peek (see state.peek_camera) -- this runs for
    every room in the game, block-world or not, and must not stamp
    block-world state onto rooms that never used it."""
    cfg = peek_camera(room)
    if not cfg or not cfg.get("enabled"):
        return False                     # not a block-world room -- engine draws it
    from . import renderer
    renderer.render_block_world_view(room, screen)
    return True


PLUGIN_ROOM_RENDERERS = [render_room]
