"""set_facing_angle / enable_raycast_view registered as structured actions.

They were runtime-only (usable only from raw JSON / execute_code), which meant
they didn't round-trip through the action editor and the HTML5/Kivy exporters
had no metadata entry to dispatch on. They're now full ActionType schemas —
but the schemas live in the raycast EXTENSION (extensions/raycast_2_5d/
actions.py, Stage B3 of docs/RAYCAST_EXTENSION_PLAN.md), not the static
ACTION_TYPES dict. The loader merges an extension's PLUGIN_ACTIONS into
ACTION_TYPES at startup, so get_action_type() finds them once plugins are
loaded — which is why this module loads them before asserting.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# The IDE does this at startup; a bare test import does not, so load the
# extension's schemas into ACTION_TYPES before querying them.
from events.plugin_loader import load_all_plugins  # noqa: E402
load_all_plugins()

from events.action_types import get_action_type  # noqa: E402


def test_set_facing_angle_registered():
    at = get_action_type("set_facing_angle")
    assert at is not None
    assert at.category == "3D View"
    names = {p.name for p in at.parameters}
    assert names == {"angle", "relative"}
    angle = next(p for p in at.parameters if p.name == "angle")
    assert angle.param_type == "number"
    relative = next(p for p in at.parameters if p.name == "relative")
    assert relative.param_type == "boolean"


def test_enable_raycast_view_registered_with_full_param_set():
    at = get_action_type("enable_raycast_view")
    assert at is not None and at.category == "3D View"
    names = {p.name for p in at.parameters}
    # the full set the runtime handler consumes (see
    # execute_enable_raycast_view_action)
    for field in ("enable", "camera_object", "fov", "render_distance",
                  "cell_size", "columns", "wall_color", "floor_color",
                  "ceiling_color", "wall_texture", "sky_texture",
                  "floor_texture", "ceiling_texture", "wall_textured",
                  "floor_cast_res"):
        assert field in names, field


def test_raycast_texture_params_are_sprite_pickers():
    at = get_action_type("enable_raycast_view")
    for field in ("wall_texture", "sky_texture", "floor_texture", "ceiling_texture"):
        p = next(p for p in at.parameters if p.name == field)
        assert p.param_type == "sprite", field
        assert p.required is False


def test_raycast_color_params_are_colors():
    at = get_action_type("enable_raycast_view")
    for field in ("wall_color", "floor_color", "ceiling_color"):
        p = next(p for p in at.parameters if p.name == field)
        assert p.param_type == "color", field


def test_camera_object_is_optional_object_selector():
    at = get_action_type("enable_raycast_view")
    cam = next(p for p in at.parameters if p.name == "camera_object")
    assert cam.param_type == "object"
    assert cam.required is False   # blank = the acting object


def test_registration_backed_by_runtime_handlers():
    """The schemas are backed by real handlers — now the extension's
    PluginExecutor, registered onto the executor by load_all_plugins, rather
    than ActionExecutor methods (Stage B3)."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    load_all_plugins(ex)
    assert callable(ex.action_handlers.get("set_facing_angle"))
    assert callable(ex.action_handlers.get("enable_raycast_view"))
    # And they are no longer ActionExecutor methods.
    assert not hasattr(ex, "execute_set_facing_angle_action")
    assert not hasattr(ex, "execute_enable_raycast_view_action")
