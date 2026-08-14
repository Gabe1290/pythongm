"""HTML5 export -- Block World voxel view port (Phase 6 Unit 8 of
docs/VOXEL_WORLD_PLAN.md).

Source-level assertions (no JS engine / Playwright in CI -- same standing
limitation as tests/test_html5_raycast.py). The generic extension-data hook
(_collect_extension_data) is exercised for real through a live
HTML5Exporter().export() of the real block_world_1 sample, which is the
strongest available proof that blocks/room0.json actually reaches the
exported page.
"""
import base64
import gzip
import json
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE_CORE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
BW_JS = (REPO_ROOT / "extensions" / "block_world" / "export_html5.js").read_text(encoding="utf-8")
ENGINE = ENGINE_CORE + "\n" + BW_JS


def test_extension_js_stays_out_of_core():
    assert "blockWorldCamera" not in ENGINE_CORE
    assert "BLOCK_FACE_COLORS" not in ENGINE_CORE


def test_room_renderer_registered():
    assert "registerRoomRenderer(function(room, ctx)" in BW_JS
    assert "room.blockWorldCamera && room.blockWorldCamera.enabled" in BW_JS
    assert "bwRenderView(room, ctx)" in BW_JS


def test_all_eight_actions_registered():
    for action in ("enable_block_world_view", "place_block", "break_block",
                    "select_hotbar_slot", "move_and_collide",
                    "draw_block_world_hud", "load_block_world", "set_look_pitch"):
        assert f"registerExtensionAction('{action}'" in BW_JS, action


def test_face_color_table_has_every_block_type():
    """Pinned against the live BLOCK_TYPES registry -- a block type added to
    state.py without regenerating this table would otherwise render as
    'undefined' (falls back to wall_color) silently."""
    from extensions.block_world.state import BLOCK_TYPES
    m = re.search(r"const BLOCK_FACE_COLORS = \{(.*?)\n\};", BW_JS, re.S)
    assert m
    body = m.group(1)
    for block_type in BLOCK_TYPES:
        assert re.search(rf"\b{re.escape(block_type)}:\s*\{{", body), block_type


def test_unbreakable_matches_state_py():
    from extensions.block_world.state import BLOCK_TYPES, is_breakable
    unbreakable = {bt for bt in BLOCK_TYPES if not is_breakable(bt)}
    m = re.search(r"const BW_UNBREAKABLE = new Set\((\[[^\]]*\])\)", BW_JS)
    assert m
    js_set = set(json.loads(m.group(1).replace("'", '"')))
    assert js_set == unbreakable


def test_default_hotbar_matches_state_py():
    from extensions.block_world.state import DEFAULT_HOTBAR
    m = re.search(r"const BW_DEFAULT_HOTBAR = \[(.*?)\];", BW_JS, re.S)
    assert m
    js_list = [s.strip().strip("'") for s in m.group(1).replace("\n", " ").split(",") if s.strip()]
    assert js_list == DEFAULT_HOTBAR


def test_shading_constants_match_renderer_py():
    from extensions.block_world.renderer import (
        SIDE_SHADE, FOG_STRENGTH, MIN_SHADE, TOP_SHADE, BOTTOM_SHADE,
        DEFAULT_EYE_HEIGHT, MAX_PITCH_DEGREES)
    checks = {
        "BW_SIDE_SHADE": SIDE_SHADE, "BW_FOG_STRENGTH": FOG_STRENGTH,
        "BW_MIN_SHADE": MIN_SHADE, "BW_TOP_SHADE": TOP_SHADE,
        "BW_BOTTOM_SHADE": BOTTOM_SHADE, "BW_DEFAULT_EYE_HEIGHT": DEFAULT_EYE_HEIGHT,
        "BW_MAX_PITCH_DEGREES": MAX_PITCH_DEGREES,
    }
    for name, value in checks.items():
        m = re.search(rf"const {name} = ([0-9.]+);", BW_JS)
        assert m, name
        assert float(m.group(1)) == value, name


def test_extension_data_hook_present_in_exporter():
    src = (REPO_ROOT / "export" / "HTML5" / "html5_exporter.py").read_text(encoding="utf-8")
    assert "_collect_extension_data" in src
    assert "export_data.py" in src
    assert "collect_export_data" in src


def test_block_world_1_exports_and_embeds_world_data():
    """The real sample exports, and blocks/room0.json's content reaches
    gameData._extension_data.block_world_files -- the actual mechanism
    load_block_world relies on at runtime in a browser."""
    from export.HTML5.html5_exporter import HTML5Exporter

    src = REPO_ROOT / "samples" / "block_world_1"
    out = Path(tempfile.mkdtemp(prefix="block_world_html5_")) / "out"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(src, out)

    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    data = json.loads(gzip.decompress(base64.b64decode(m.group(1))))

    ext_data = data.get("_extension_data", {})
    files = ext_data.get("block_world_files", {})
    assert "blocks/room0.json" in files

    with open(src / "blocks" / "room0.json", "r", encoding="utf-8") as f:
        expected = json.load(f)
    assert files["blocks/room0.json"] == expected

    # The actions themselves made it into the exported object data too.
    objs = data["assets"]["objects"]
    blob = json.dumps(objs.get("obj_person", {}))
    for action in ("enable_block_world_view", "load_block_world",
                    "move_and_collide", "draw_block_world_hud"):
        assert action in blob

    # engine.js the export actually ships includes the extension's JS.
    assert "registerExtensionAction('enable_block_world_view'" in html


def test_export_data_walker_recurses_into_if_condition():
    """collect_export_data must find load_block_world even nested inside an
    if_condition's then/else branches, not just top-level action lists."""
    from extensions.block_world.export_data import collect_export_data

    project_data = {
        "assets": {
            "objects": {
                "obj_x": {
                    "events": {
                        "create": {"actions": [
                            {"action": "if_condition", "parameters": {
                                "then_actions": [
                                    {"action": "load_block_world",
                                     "parameters": {"data_file": "blocks/nested.json"}},
                                ],
                                "else_actions": [],
                            }},
                        ]},
                        "keyboard": {
                            "w": {"actions": [
                                {"action": "load_block_world",
                                 "parameters": {"data_file": "blocks/keyed.json"}},
                            ]},
                        },
                    },
                },
            },
        },
    }
    tmp = Path(tempfile.mkdtemp(prefix="bw_export_data_"))
    (tmp / "blocks").mkdir()
    (tmp / "blocks" / "nested.json").write_text(
        json.dumps([{"x": 0, "y": 0, "z": 0, "type": "stone"}]), encoding="utf-8")
    (tmp / "blocks" / "keyed.json").write_text(
        json.dumps([{"x": 1, "y": 1, "z": 1, "type": "dirt"}]), encoding="utf-8")

    result = collect_export_data(tmp, project_data)
    files = result["block_world_files"]
    assert files["blocks/nested.json"] == [{"x": 0, "y": 0, "z": 0, "type": "stone"}]
    assert files["blocks/keyed.json"] == [{"x": 1, "y": 1, "z": 1, "type": "dirt"}]


def test_export_data_skips_unknown_and_missing_files_silently():
    from extensions.block_world.export_data import collect_export_data

    project_data = {
        "assets": {"objects": {"obj_x": {"events": {"create": {"actions": [
            {"action": "load_block_world", "parameters": {"data_file": "blocks/missing.json"}},
        ]}}}}},
    }
    tmp = Path(tempfile.mkdtemp(prefix="bw_export_data_missing_"))
    result = collect_export_data(tmp, project_data)
    assert result["block_world_files"] == {}
    assert len(result["block_textures"]) == 32   # the full bundled set, always embedded


# --- Real per-pixel wall textures (Phase 6 Tier 4a) --------------------------

def test_wall_strip_draws_a_real_texture_when_loaded():
    """Structural check (no JS engine): the wall-strip draw site uses
    ctx.drawImage with the same sub-rect-slicing shape as the raycast HTML5
    wall pass, falling back to the flat color only when the Image hasn't
    finished loading."""
    m = re.search(r"if \(y1v > y0v\) \{(.*?)\n {16}\}\n", BW_JS, re.S)
    assert m, "wall-strip draw block not found"
    body = m.group(1)
    assert "bwTexture(room._gameRef" in body
    assert "tex.complete && tex.width > 0" in body
    assert "ctx.drawImage(tex, texX, srcY, 1, srcH, x0, y0v, stripW" in body
    assert "bwShadeColor(sideColor, shade)" in body   # the fallback path


def test_block_face_files_table_has_every_block_type():
    from extensions.block_world.state import BLOCK_TYPES
    m = re.search(r"const BLOCK_FACE_FILES = \{(.*?)\n\};", BW_JS, re.S)
    assert m
    body = m.group(1)
    for block_type in BLOCK_TYPES:
        assert re.search(rf"\b{re.escape(block_type)}:\s*\{{", body), block_type


def test_bw_texture_builds_an_image_from_the_embedded_data_uri():
    m = re.search(r"function bwTexture\(game, filename\)\s*\{(.*?)\n\}", BW_JS, re.S)
    assert m
    body = m.group(1)
    assert "gameData._extension_data" in body
    assert "block_textures" in body
    assert "data:image/png;base64," in body


# --- Real per-pixel top/bottom textures (Phase 6 Tier 4b) --------------------

def test_horizontal_face_texture_function_ports_the_projection_math():
    m = re.search(r"function bwDrawHorizontalFaceTextured\([^)]*\)\s*\{(.*)",
                  BW_JS, re.S)
    assert m, "bwDrawHorizontalFaceTextured not found"
    body = m.group(1)[:4000]
    # k = (eyeZ - planeZ) * H * cellSize, and the inverse-projection texel().
    assert "(eyeZ - planeZ) * H * cellSize" in body
    assert "y + 0.5 - horizon" in body
    assert "rayDist" in body
    assert "Math.floor(gx)" in body and "Math.floor(gy)" in body


def test_top_bottom_faces_call_the_textured_path_with_fallback():
    m = re.search(r"if \(eyeZ > z \+ 1 && !above\) \{(.*?)\n {16}\} else if \(eyeZ < z && !below\) \{(.*?)\n {16}\}\n",
                  BW_JS, re.S)
    assert m, "top/bottom face draw block not found"
    top_body, bottom_body = m.group(1), m.group(2)
    for body, face in ((top_body, "top"), (bottom_body, "bottom")):
        assert "bwTextureData(room._gameRef" in body, face
        assert f"fileSet.{face}" in body, face
        assert "bwDrawHorizontalFaceTextured(" in body, face
        assert "bwShadeColor(color, lit)" in body, face   # the fallback path


def test_top_cast_res_disables_texturing_at_zero():
    m = re.search(r"const topTextured = (.*?);", BW_JS)
    assert m
    assert "topRes >= 1" in m.group(1)
