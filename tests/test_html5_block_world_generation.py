"""HTML5 export -- Tier 7e Phase 3 (docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md):
seed-based procedural terrain generation. No JS engine/Playwright in this
environment (same standing limitation as every other HTML5 block-world/
raycast test) -- source-level structural assertions plus a brace/paren
balance check, mirroring test_html5_block_world_jump_inventory.py's tier.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

BW_JS_PATH = REPO_ROOT / "extensions" / "block_world" / "export_html5.js"
BW_JS = BW_JS_PATH.read_text(encoding="utf-8")


def test_source_is_brace_and_paren_balanced():
    # A cheap but real regression guard for hand-edited JS with no engine
    # to actually run it against -- catches an unclosed block/call outright.
    assert BW_JS.count("{") == BW_JS.count("}")
    assert BW_JS.count("(") == BW_JS.count(")")


def test_generation_functions_exist():
    for fn in ("bwChunkKey", "bwMarkChunkPresent", "bwHash01", "bwValueNoise",
               "bwTerrainHeight", "bwGenerateChunk", "bwEnsureChunksLoaded"):
        assert re.search(rf"function {fn}\(", BW_JS), fn


def test_set_and_remove_block_mark_chunk_present():
    for fn in ("bwSetBlock", "bwRemoveBlock"):
        m = re.search(rf"function {fn}\((.*?)\n\}}", BW_JS, re.S)
        assert m, fn
        assert "bwMarkChunkPresent(room, x, y)" in m.group(1), fn


def test_render_view_calls_ensure_chunks_loaded_before_column_index():
    m = re.search(r"function bwRenderView\(room, ctx\)\s*\{(.*?)\n\}", BW_JS, re.S)
    assert m
    body = m.group(1)
    ensure_pos = body.index("bwEnsureChunksLoaded(")
    columns_pos = body.index("bwColumnIndex(room)")
    assert ensure_pos < columns_pos


def test_enable_block_world_view_sets_seed_only_when_generate_is_on():
    m = re.search(r"registerExtensionAction\('enable_block_world_view'(.*?)\n\}\);", BW_JS, re.S)
    assert m
    body = m.group(1)
    assert "room._bwSeed = boolTrue(params.generate) ? Math.trunc(num('seed', 0)) : null;" in body


def test_load_block_world_detects_both_file_shapes():
    m = re.search(r"registerExtensionAction\('load_block_world'(.*?)\n\}\);", BW_JS, re.S)
    assert m
    body = m.group(1)
    assert "Array.isArray(fileData)" in body
    assert "Array.isArray(fileData.blocks)" in body
    assert "currentRoom._bwSeed = seed;" in body
    assert "currentRoom._bwGenerated = generated;" in body


def test_chunk_size_matches_desktop():
    from extensions.block_world.state import CHUNK_SIZE
    m = re.search(r"const BW_CHUNK_SIZE = (\d+);", BW_JS)
    assert m
    assert int(m.group(1)) == CHUNK_SIZE


def test_terrain_constants_match_desktop():
    from extensions.block_world.state import (
        TERRAIN_BASE_HEIGHT, TERRAIN_AMPLITUDE, TERRAIN_NOISE_SCALE)
    checks = {
        "BW_TERRAIN_BASE_HEIGHT": TERRAIN_BASE_HEIGHT,
        "BW_TERRAIN_AMPLITUDE": TERRAIN_AMPLITUDE,
        "BW_TERRAIN_NOISE_SCALE": TERRAIN_NOISE_SCALE,
    }
    for name, value in checks.items():
        m = re.search(rf"const {name} = ([\-0-9.]+);", BW_JS)
        assert m, name
        assert float(m.group(1)) == float(value), name
