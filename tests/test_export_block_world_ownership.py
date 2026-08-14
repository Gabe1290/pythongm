"""Completeness guard, block_world edition (Phase 6 Unit 10 of
docs/VOXEL_WORLD_PLAN.md): the export engines own NO block-world code.

Mirrors tests/test_export_raycast_ownership.py exactly -- the Stage-C
generic seams (renderExtensionRoom/registerExtensionAction on HTML5,
_render_extension_overlay/the two class-body markers plus the generic
_extension_codegen()/_collect_extension_data hooks on Kivy) live in the
core export engines; block-world-specific code lives only in
extensions/block_world/. A regression that re-inlines it trips here.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
EXPORT_HTML5 = (REPO_ROOT / "extensions" / "block_world" / "export_html5.js").read_text(encoding="utf-8")
HTML5_EXPORTER = (REPO_ROOT / "export" / "HTML5" / "html5_exporter.py").read_text(encoding="utf-8")
KIVY_EXPORTER = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
CODE_GEN = (REPO_ROOT / "export" / "Kivy" / "code_generator.py").read_text(encoding="utf-8")
EXPORT_KIVY = (REPO_ROOT / "extensions" / "block_world" / "export_kivy.py").read_text(encoding="utf-8")
EXPORT_DATA = (REPO_ROOT / "extensions" / "block_world" / "export_data.py").read_text(encoding="utf-8")


# --- HTML5 --------------------------------------------------------------------

def test_engine_js_defines_only_generic_seams():
    assert "function renderExtensionRoom(room, ctx)" in ENGINE
    assert "function registerExtensionAction(name, fn)" in ENGINE
    for gone in ("BLOCK_FACE_COLORS", "bwMarchRay", "bwRenderView",
                 "registerExtensionAction('enable_block_world_view'",
                 "registerExtensionAction('place_block'"):
        assert gone not in ENGINE, f"engine.js still contains block-world code: {gone!r}"


def test_html5_exporter_defines_only_the_generic_data_hook():
    assert "_collect_extension_data" in HTML5_EXPORTER
    assert "export_data.py" in HTML5_EXPORTER
    for gone in ("block_world_files", "BLOCK_FACE_COLORS"):
        assert gone not in HTML5_EXPORTER, f"html5_exporter still names block-world: {gone!r}"


def test_export_html5_owns_the_block_world_js():
    assert "const BLOCK_FACE_COLORS = {" in EXPORT_HTML5
    assert "function bwRenderView(room, ctx)" in EXPORT_HTML5
    assert "registerRoomRenderer(function(room, ctx)" in EXPORT_HTML5
    for act in ("enable_block_world_view", "place_block", "break_block",
                "select_hotbar_slot", "move_and_collide", "draw_block_world_hud",
                "load_block_world", "set_look_pitch"):
        assert f"registerExtensionAction('{act}'" in EXPORT_HTML5


# --- Kivy scene + base object -------------------------------------------------

def test_kivy_exporter_defines_only_generic_seams():
    assert "def _render_extension_overlay(self):" in KIVY_EXPORTER  # no-op default
    assert "__PYGM_EXTENSION_SCENE_CODE__" in KIVY_EXPORTER
    assert "_collect_extension_data" in KIVY_EXPORTER
    for gone in ("def _render_block_world(self)", "def _bw_march_ray(self",
                 "self.block_world_camera = None", "BLOCK_FACE_COLORS"):
        assert gone not in KIVY_EXPORTER, f"kivy_exporter still contains block-world code: {gone!r}"


def test_export_kivy_owns_the_scene_code():
    assert "SCENE_CODE = '''" in EXPORT_KIVY
    assert "def _render_block_world(self):" in EXPORT_KIVY
    assert "def _bw_march_ray(self" in EXPORT_KIVY
    assert "self.block_world_camera = None" in EXPORT_KIVY


# --- Kivy action codegen ------------------------------------------------------

def test_code_generator_defines_only_the_generic_hook():
    assert "_extension_codegen()" in CODE_GEN
    for gone in ("elif action_type == 'enable_block_world_view'",
                 "elif action_type == 'move_and_collide'",
                 "elif action_type == 'place_block'"):
        assert gone not in CODE_GEN, f"code_generator still enumerates block-world: {gone!r}"


def test_export_kivy_owns_the_action_codegen():
    assert "ACTION_CODEGEN = {" in EXPORT_KIVY
    for act in ("enable_block_world_view", "place_block", "break_block",
                "select_hotbar_slot", "move_and_collide", "draw_block_world_hud",
                "load_block_world", "set_look_pitch"):
        assert f"def _cg_{act}(" in EXPORT_KIVY


# --- Shared export-data collector (both targets use the ONE file) ------------

def test_export_data_module_is_target_agnostic():
    # The docstring may reference html5_exporter.py/kivy_exporter.py as
    # CALLERS (both do call this module) -- what must never appear is
    # target-specific SYNTAX/logic bleeding in (a JS statement, a Kivy
    # import, gameData/scene-specific shaping).
    for gone in ("kivy.graphics", "from kivy", "import kivy", "gameData",
                 "self.scene", "InstructionGroup", "registerExtensionAction"):
        assert gone not in EXPORT_DATA, f"export_data.py leaks target-specific code: {gone!r}"
    assert "def collect_export_data(" in EXPORT_DATA
