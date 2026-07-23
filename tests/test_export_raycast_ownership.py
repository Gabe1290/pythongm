"""Stage C completeness guard: the export engines own NO raycast code.

After Stage C, the 2.5D raycast feature is fully extension-owned on all three
targets. This pins that engine.js / kivy_exporter.py / code_generator.py carry
only the GENERIC extension seams (never raycast names), while the moved code
lives in extensions/raycast_2_5d/export_html5.js and export_kivy.py. A
regression that re-inlines raycast into an export engine trips here.

See docs/RAYCAST_EXTENSION_PLAN.md Stage C.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
EXPORT_HTML5 = (REPO_ROOT / "extensions" / "raycast_2_5d" / "export_html5.js").read_text(encoding="utf-8")
KIVY_EXPORTER = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
CODE_GEN = (REPO_ROOT / "export" / "Kivy" / "code_generator.py").read_text(encoding="utf-8")
EXPORT_KIVY = (REPO_ROOT / "extensions" / "raycast_2_5d" / "export_kivy.py").read_text(encoding="utf-8")


# --- HTML5 --------------------------------------------------------------------

def test_engine_js_defines_only_generic_seams():
    # The generic extension seams stay in the engine...
    assert "function renderExtensionRoom(room, ctx)" in ENGINE
    assert "function registerExtensionAction(name, fn)" in ENGINE
    assert "// __PYGM_EXTENSION_JS__" in ENGINE
    # ...but no raycast RENDER or ACTION code.
    for gone in ("buildRaycastWalls(cellSize)", "castFloorPlane(ctx",
                 "const RAYCAST_WALL_HEIGHT", "wallShade(side, corrected",
                 "case 'enable_raycast_view'", "case 'draw_minimap'",
                 "case 'draw_doom_hud'", "case 'set_facing_angle'"):
        assert gone not in ENGINE, f"engine.js still contains raycast code: {gone!r}"


def test_export_html5_owns_the_raycast_js():
    assert "Object.assign(GameRoom.prototype, {" in EXPORT_HTML5
    assert "renderRaycastView(ctx) {" in EXPORT_HTML5
    assert "const RAYCAST_WALL_HEIGHT = 1.5" in EXPORT_HTML5
    assert "registerRoomRenderer(function(room, ctx)" in EXPORT_HTML5
    for act in ("enable_raycast_view", "draw_minimap", "draw_doom_hud", "set_facing_angle"):
        assert f"registerExtensionAction('{act}'" in EXPORT_HTML5


# --- Kivy scene + base object -------------------------------------------------

def test_kivy_exporter_defines_only_generic_seams():
    assert "def _render_extension_overlay(self):" in KIVY_EXPORTER  # no-op default
    assert "__PYGM_EXTENSION_SCENE_CODE__" in KIVY_EXPORTER
    assert "__PYGM_EXTENSION_BASE_CODE__" in KIVY_EXPORTER
    for gone in ("def _render_raycast(self)", "def _cast_ray(self",
                 "def _build_raycast_walls(self", "def _draw_minimap(self, x, y, size",
                 "self.raycast_camera = None", "self._raycast_v_walls = None"):
        assert gone not in KIVY_EXPORTER, f"kivy_exporter still contains raycast code: {gone!r}"


def test_export_kivy_owns_the_scene_and_base_code():
    assert "SCENE_CODE = '''" in EXPORT_KIVY
    assert "BASE_OBJECT_CODE = '''" in EXPORT_KIVY
    assert "def _render_raycast(self):" in EXPORT_KIVY
    assert "def _draw_minimap(self, x, y, size" in EXPORT_KIVY
    # the overlay override + state hook the scene defaults get replaced by
    assert "self.raycast_camera = None" in EXPORT_KIVY


# --- Kivy action codegen ------------------------------------------------------

def test_code_generator_defines_only_the_generic_hook():
    assert "_extension_codegen()" in CODE_GEN
    for gone in ("elif action_type == 'enable_raycast_view'",
                 "elif action_type == 'set_facing_angle'",
                 "elif action_type == 'draw_minimap'",
                 "elif action_type == 'draw_doom_hud'"):
        assert gone not in CODE_GEN, f"code_generator still enumerates raycast: {gone!r}"


def test_export_kivy_owns_the_action_codegen():
    assert "ACTION_CODEGEN = {" in EXPORT_KIVY
    for act in ("set_facing_angle", "enable_raycast_view", "draw_doom_hud", "draw_minimap"):
        assert f"def _cg_{act}(" in EXPORT_KIVY
