#!/usr/bin/env python3
"""Generate the precomputed per-block-type average face colors used by the
Block World extension's HTML5/Kivy export ports (Phase 6, Units 8-9 of
docs/VOXEL_WORLD_PLAN.md).

Desktop's renderer maps real PNG textures onto every block face. Porting
that per-pixel texture-cropping pipeline to two more hand-written renderers
was judged not worth it for a first export cut (documented scope reduction,
same category as raycast's still-open per-target floor-casting deferral) --
instead, the export renderers draw each face as a flat color: the SAME
average color desktop itself already falls back to for untextured top/
bottom faces (renderer.face_average_color), just used for every face on
every target that has no real texture pipeline.

Run from the repo root:
    python3 tools/gen_block_world_face_colors.py

Writes tools/generated/block_world_face_colors.json, keyed by block type id,
each a {"top": [r,g,b], "bottom": [r,g,b], "side": [r,g,b]} triple. Pinned
against a live recomputation by
tests/test_block_world_export_face_colors.py, so a stale committed file (a
texture changed, a block type added) fails CI rather than silently drifting
from the actual bundled art.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
OUT = REPO_ROOT / "tools" / "generated" / "block_world_face_colors.json"


def build_table():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))

    from extensions.block_world.state import BLOCK_TYPES, block_face_textures
    from extensions.block_world.renderer import face_average_color

    table = {}
    for block_type in sorted(BLOCK_TYPES):
        faces = block_face_textures(block_type)
        table[block_type] = {
            face: list(face_average_color(path))
            for face, path in faces.items()
        }
    return table


def main():
    table = build_table()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(table, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"Wrote {OUT} ({len(table)} block types)")


if __name__ == "__main__":
    main()
