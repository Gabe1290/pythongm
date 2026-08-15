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
"""
import json
import os
from pathlib import Path

from extensions.block_world.state import to_block_list, load_block_list


def blocks_path(project_path, room_name: str) -> Path:
    return Path(project_path) / "blocks" / f"{room_name}.json"


def load_room_blocks(room, project_path, room_name: str) -> bool:
    """Load room_name's blocks/<room>.json into `room`, replacing whatever
    it currently holds. Returns True if a file existed and was loaded,
    False for a brand-new Block World room with nothing saved yet (not an
    error -- the editor should just open empty)."""
    path = blocks_path(project_path, room_name)
    if not path.exists():
        return False
    with open(path, 'r', encoding='utf-8') as f:
        block_list = json.load(f)
    load_block_list(room, block_list)
    return True


def save_room_blocks(room, project_path, room_name: str) -> Path:
    """Write `room`'s current blocks to blocks/<room>.json, atomically
    (temp file + os.replace, so a crash mid-write never leaves a
    truncated file). Creates the blocks/ directory if it doesn't exist
    yet. Returns the path written."""
    path = blocks_path(project_path, room_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    block_list = to_block_list(room)

    tmp_path = path.with_name(path.name + ".tmp")
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(block_list, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    return path
