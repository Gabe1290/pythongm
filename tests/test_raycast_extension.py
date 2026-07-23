"""The raycast renderer is an EXTENSION now, not core (Stage B2).

docs/RAYCAST_EXTENSION_PLAN.md. These pin the move itself: the renderer lives in
extensions/raycast_2_5d, core no longer carries a copy, and the extension is
discovered, enabled by default, and actually claims raycast rooms through the
Stage-B1 render hook. The behavioural raycast coverage (real frames rendering
correctly) lives in test_raycast_view / _viewport / _hud / the sample smoke
runner — this file is only about WHERE the code lives and that it wires up.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_renderer_module_exposes_the_public_surface():
    """The functions the exporters mirror and the tests drive, at module level
    (they were GameRoom methods before the move)."""
    from extensions.raycast_2_5d import renderer
    for name in ("render_raycast_view", "cast_ray", "build_raycast_walls",
                 "cast_floor_plane", "wall_shade"):
        assert callable(getattr(renderer, name)), name
    for const in ("RAYCAST_WALL_HEIGHT", "RAYCAST_SIDE_SHADE",
                  "RAYCAST_FOG_STRENGTH", "RAYCAST_MIN_SHADE"):
        assert isinstance(getattr(renderer, const), float), const


def test_core_no_longer_carries_the_renderer():
    """The whole point of a MOVE: core must not keep a shadow copy. If this
    fails, the renderer was duplicated, not moved."""
    from runtime.game_runner import GameRoom
    for gone in ("_render_raycast_view", "_cast_ray", "_build_raycast_walls",
                 "_cast_floor_plane", "_wall_shade"):
        assert not hasattr(GameRoom, gone), f"GameRoom still defines {gone}"


def test_generic_helpers_stay_in_core():
    """These are NOT raycast-specific and other paths use them — they must
    remain on GameRoom (plan: 'keep in core')."""
    from runtime.game_runner import GameRoom
    for kept in ("_render_draw_events", "_sprite_top_left", "_find_first_instance"):
        assert hasattr(GameRoom, kept), f"GameRoom lost the generic helper {kept}"


def test_core_carries_no_raycast_state_attributes():
    """Stage B3b: GameRoom no longer initialises raycast_camera or the wall
    caches — all raycast state lives under room.extension_state['raycast']. A
    fresh room has extension_state but no raycast namespace until the view is
    enabled."""
    from runtime.game_runner import GameRoom
    room = GameRoom("r", {"width": 64, "height": 64}, action_executor=None)
    assert room.extension_state == {}, "fresh room must not pre-stamp raycast state"
    for gone in ("raycast_camera", "_raycast_v_walls", "_raycast_h_walls",
                 "_raycast_v_wall_sprites", "_raycast_h_wall_sprites",
                 "_raycast_cell_size"):
        assert not hasattr(room, gone), f"GameRoom still carries {gone}"
    # The extension's helper creates the namespace lazily, with sane defaults.
    from extensions.raycast_2_5d.state import raycast_state, peek_camera
    assert peek_camera(room) is None            # non-creating
    st = raycast_state(room)                     # creating
    assert st["camera"] == {"enabled": False}
    assert st["v_walls"] is None and st["cell_size"] == 32
    assert room.extension_state["raycast"] is st


def test_extension_contributes_the_setup_actions():
    """Stage B3: set_facing_angle / enable_raycast_view are the extension's
    actions now — schema in PLUGIN_ACTIONS, handler on its PluginExecutor,
    and gone from core's ActionExecutor (a move, not a copy)."""
    from extensions.raycast_2_5d import PLUGIN_ACTIONS, PluginExecutor
    assert set(PLUGIN_ACTIONS) >= {"set_facing_angle", "enable_raycast_view"}
    ex = PluginExecutor()
    assert callable(getattr(ex, "execute_set_facing_angle_action", None))
    assert callable(getattr(ex, "execute_enable_raycast_view_action", None))

    from runtime.action_executor import ActionExecutor
    for gone in ("execute_set_facing_angle_action",
                 "execute_enable_raycast_view_action"):
        assert not hasattr(ActionExecutor, gone), f"ActionExecutor still has {gone}"

    from events.action_types import ACTION_TYPES
    # Not baked into the static core dict (they arrive via the loader merge).
    import events.action_types as at_mod
    src = (Path(at_mod.__file__)).read_text(encoding="utf-8")
    assert '"set_facing_angle": ActionType' not in src
    assert '"enable_raycast_view": ActionType' not in src


def test_extension_owns_draw_minimap_and_its_builder():
    """Stage B3.2: draw_minimap (schema + handler) and its geometry builder
    live in the extension; core no longer carries them."""
    from extensions.raycast_2_5d import PLUGIN_ACTIONS, PluginExecutor
    from extensions.raycast_2_5d.hud import (
        build_minimap_commands, MINIMAP_HEADING_LEN, MINIMAP_MARKER_HALF,
    )
    assert "draw_minimap" in PLUGIN_ACTIONS
    assert callable(getattr(PluginExecutor(), "execute_draw_minimap_action", None))
    assert callable(build_minimap_commands)
    assert (MINIMAP_MARKER_HALF, MINIMAP_HEADING_LEN) == (2.0, 7.0)

    # Gone from core: the builder, its constants, and the handler.
    import runtime.action_executor as ae
    for gone in ("build_minimap_commands", "MINIMAP_HEADING_LEN",
                 "MINIMAP_MARKER_HALF"):
        assert not hasattr(ae, gone), f"action_executor still exports {gone}"
    from runtime.action_executor import ActionExecutor
    assert not hasattr(ActionExecutor, "execute_draw_minimap_action")


def test_extension_owns_draw_doom_hud_and_its_builders():
    """Stage B3.3: draw_doom_hud (schema + handler), build_doom_hud_commands and
    doom_face_frame live in the extension; core no longer carries them. This is
    the last raycast action to move — core's ACTION_TYPES now has no "3D View"
    action baked in."""
    from extensions.raycast_2_5d import PLUGIN_ACTIONS, PluginExecutor
    from extensions.raycast_2_5d.hud import build_doom_hud_commands, doom_face_frame
    assert "draw_doom_hud" in PLUGIN_ACTIONS
    assert callable(getattr(PluginExecutor(), "execute_draw_doom_hud_action", None))
    assert callable(build_doom_hud_commands) and callable(doom_face_frame)

    import runtime.action_executor as ae
    for gone in ("build_doom_hud_commands", "doom_face_frame"):
        assert not hasattr(ae, gone), f"action_executor still exports {gone}"
    from runtime.action_executor import ActionExecutor
    assert not hasattr(ActionExecutor, "execute_draw_doom_hud_action")

    # All four "3D View" actions are the extension's now — none baked into the
    # static core dict source.
    import events.action_types as at_mod
    src = Path(at_mod.__file__).read_text(encoding="utf-8")
    for name in ("set_facing_angle", "enable_raycast_view", "draw_minimap",
                 "draw_doom_hud"):
        assert f'"{name}": ActionType' not in src, f"{name} still in core ACTION_TYPES"


def test_extension_is_discovered_and_enabled_by_default():
    from events.plugin_loader import list_available_extensions
    found = {e["folder"]: e for e in list_available_extensions()}
    assert "raycast_2_5d" in found, "raycast extension not discovered"
    assert found["raycast_2_5d"]["enabled"] is True


def test_loading_registers_the_room_renderer():
    from events.plugin_loader import load_all_plugins
    from runtime import extension_hooks
    load_all_plugins()
    names = [getattr(f, "__name__", "") for f in extension_hooks.get_room_renderers()]
    assert "render_room" in names, \
        "raycast extension's room renderer was not registered"


def test_render_room_claims_a_raycast_room_and_declines_others():
    """The extension's decision logic, unit-level: claim iff the room's
    raycast camera is enabled."""
    import extensions.raycast_2_5d as ext

    class _Room:
        # Raycast state lives in extension_state now (Stage B3b); render_room
        # peeks there. cfg=None models a room that never enabled the view.
        def __init__(self, cfg):
            self.extension_state = {"raycast": {"camera": cfg}} if cfg is not None else {}

    # A raycast room is claimed; render is delegated to the renderer.
    drew = {"n": 0}
    from extensions.raycast_2_5d import renderer
    real = renderer.render_raycast_view
    renderer.render_raycast_view = lambda room, screen: drew.update(n=drew["n"] + 1)
    try:
        assert ext.render_room(_Room({"enabled": True}), object()) is True
        assert drew["n"] == 1
    finally:
        renderer.render_raycast_view = real

    # A non-raycast room (or one with no camera) is declined, untouched.
    assert ext.render_room(_Room({"enabled": False}), object()) is False
    assert ext.render_room(_Room(None), object()) is False

    class _Bare:
        pass
    assert ext.render_room(_Bare(), object()) is False
