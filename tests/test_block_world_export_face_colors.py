"""Pins tools/generated/block_world_face_colors.json (the precomputed table
the HTML5/Kivy export ports embed as flat-color fallbacks -- see
extensions/block_world/export_html5.js's header comment for why) against a
live recomputation from the real bundled textures, so a texture change or a
new block type can't silently drift the committed file out of date."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

COMMITTED = REPO_ROOT / "tools" / "generated" / "block_world_face_colors.json"


def test_committed_table_matches_live_recomputation():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_block_world_face_colors", REPO_ROOT / "tools" / "gen_block_world_face_colors.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    live = gen.build_table()
    with open(COMMITTED, "r", encoding="utf-8") as f:
        committed = json.load(f)

    assert set(committed) == set(live)
    for block_type, faces in live.items():
        assert committed[block_type] == faces, block_type


def test_every_block_type_present():
    from extensions.block_world.state import BLOCK_TYPES
    with open(COMMITTED, "r", encoding="utf-8") as f:
        committed = json.load(f)
    assert set(committed) == set(BLOCK_TYPES)
    for entry in committed.values():
        assert set(entry) == {"top", "bottom", "side"}
