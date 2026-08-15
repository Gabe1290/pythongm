#!/usr/bin/env python3
"""In-IDE visual Block World editor (Tier 7d, docs/BLOCK_WORLD_EDITOR_PLAN.md).

Paint/place/remove voxel blocks inside the IDE, the same way the Room
Editor already lets an author place object instances and paint tiles, and
save the result to a room's ``blocks/<room>.json`` sibling file --
exactly what ``load_block_world`` (extensions/block_world/handlers.py)
already knows how to load at runtime.
"""
