#!/usr/bin/env python3
"""Block World: a voxel block-building extension (Phase 1 of docs/VOXEL_WORLD_PLAN.md).

Working name only -- never use "Minecraft" anywhere in this extension (see
the plan doc's naming section): it's a trademark, and the goal is the same
"inspired by, not copied from" territory Luanti/Minetest itself occupies, not
a clone wearing someone else's name.

Phase 1 status: the per-room world data model and CC0 block texture registry
exist (state.py). There is no room renderer yet (Phase 2) and no actions yet
(Phase 3+) -- this extension currently contributes nothing to a running game
or to the action picker. events/plugin_loader.py treats PLUGIN_ACTIONS and
PLUGIN_ROOM_RENDERERS as optional (checked via hasattr), so declaring neither
here loads cleanly rather than needing empty placeholder declarations.
"""

PLUGIN_NAME = "Block World"
