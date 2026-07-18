"""set_facing_angle / enable_raycast_view registered as structured actions
(raycast 2.5D export-parity, plan Phases 2/3 shared prerequisite).

They were runtime-only (usable only from raw JSON / execute_code), which meant
they didn't round-trip through the action editor and the HTML5/Kivy exporters
had no metadata entry to dispatch on. Registering them in
events/action_types.py is the shared first step before either export target's
raycast renderer can be wired up — same shape as the enable_views/set_view
registration that unblocked the views export work.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

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
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    assert callable(getattr(ex, "execute_set_facing_angle_action", None))
    assert callable(getattr(ex, "execute_enable_raycast_view_action", None))
