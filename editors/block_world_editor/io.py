#!/usr/bin/env python3
"""Save/load a room's ``blocks/<room>.json`` sibling file (Phase 3,
docs/BLOCK_WORLD_EDITOR_PLAN.md).

Treats a room's block data as a per-room sibling file (like room
instances already are, ``rooms/<name>.json``) rather than inventing a new
top-level asset category -- the plan doc's own recommendation: a Block
World room's blocks are conceptually part of that room, not a separate
reusable asset multiple rooms would share. This is exactly the shape
``load_block_world`` (extensions/block_world/handlers.py) already reads
at runtime, so a world saved here is immediately playable with no
conversion step.

Tier 7e Phase 2 (docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md) adds a second
file shape for a room with a seed: ``{"seed": <int>, "blocks": [...]}``,
where "blocks" is only the TOUCHED chunks (state.to_touched_block_list) --
everything else regenerates on demand. A room with no seed (every room
before Phase 2, and the common case still) keeps saving the plain flat
list exactly as before -- this format is chosen ENTIRELY by whether the
room has a seed, not by any new editor UI, so nothing about existing
saves changes unless something (currently only the enable_block_world_view
action's `generate`/`seed` params) actually sets one.
"""
import json
import os
from pathlib import Path

from extensions.block_world.state import (
    block_world_state, to_block_list, to_touched_block_list,
    load_block_list, load_world_state,
)


def blocks_path(project_path, room_name: str) -> Path:
    return Path(project_path) / "blocks" / f"{room_name}.json"


def load_room_blocks(room, project_path, room_name: str) -> bool:
    """Load room_name's blocks/<room>.json into `room`, replacing whatever
    it currently holds. Returns True if a file existed and was loaded,
    False for a brand-new Block World room with nothing saved yet (not an
    error -- the editor should just open empty). Detects the seeded-world
    dict shape vs. the plain flat-list shape from the parsed JSON's own
    type, same as load_block_world's runtime action."""
    path = blocks_path(project_path, room_name)
    if not path.exists():
        return False
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        load_world_state(room, data.get("seed"), data.get("blocks", []))
    else:
        load_block_list(room, data)
    return True


def save_room_blocks(room, project_path, room_name: str) -> Path:
    """Write `room`'s current blocks to blocks/<room>.json, atomically
    (temp file + os.replace, so a crash mid-write never leaves a
    truncated file). Creates the blocks/ directory if it doesn't exist
    yet. Returns the path written."""
    path = blocks_path(project_path, room_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    seed = block_world_state(room).get("seed")
    if seed is None:
        payload = to_block_list(room)
    else:
        payload = {"seed": seed, "blocks": to_touched_block_list(room)}

    tmp_path = path.with_name(path.name + ".tmp")
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    return path
