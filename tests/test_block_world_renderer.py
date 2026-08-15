"""Regression tests for the Block World renderer (Phase 2a of
docs/VOXEL_WORLD_PLAN.md).

Mirrors tests/test_raycast_view.py's structure and MockRoom/MockGameRunner
action-dispatch pattern, but the hit-test itself is genuinely different
(voxel cell OCCUPANCY, not derived thin wall EDGES) -- see
extensions/block_world/renderer.py's module docstring -- so the CastRay
tests target different geometry than raycast_2_5d's.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()
# convert_alpha() (renderer._load_texture) needs an active video mode, even
# under the dummy driver -- matches tests/test_background_scroll.py's setup.
pygame.display.set_mode((1, 1))

from runtime.game_runner import GameRoom, GameInstance  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.block_world.state import block_world_state, set_block  # noqa: E402
from extensions.block_world.renderer import (  # noqa: E402
    cast_ray, render_block_world_view, wall_shade,
    SIDE_SHADE, FOG_STRENGTH, MIN_SHADE,
)


# ---------------------------------------------------------------------------
# enable_block_world_view action
# ---------------------------------------------------------------------------

class MockInstance:
    def __init__(self, object_name="obj_person"):
        self.object_name = object_name
        self.facing_angle = 0.0
        self.action_executor = None


class MockRoom:
    def __init__(self):
        self.extension_state = {}


class MockGameRunner:
    def __init__(self):
        self.current_room = MockRoom()
        self.global_variables = {}


def _bw_executor(game_runner=None):
    ex = ActionExecutor(game_runner=game_runner)
    load_all_plugins(ex)
    return ex


def _dispatch(executor, action_name, instance, params):
    instance.action_executor = executor
    return executor.action_handlers[action_name](instance, params)


class TestEnableBlockWorldView:
    def test_enable_sets_config_with_defaults(self):
        executor = _bw_executor(game_runner=MockGameRunner())
        instance = MockInstance()
        _dispatch(executor, "enable_block_world_view", instance, {})
        cfg = block_world_state(executor.game_runner.current_room)["camera"]
        assert cfg["enabled"] is True
        assert cfg["camera_object"] == "obj_person"  # falls back to the caller
        assert cfg["fov"] == 66
        assert cfg["cell_size"] == 32
        assert cfg["z_layer"] == 0
        assert cfg["top_cast_res"] == 4
        assert cfg["eye_height"] == 1.5

    def test_enable_honors_overrides(self):
        executor = _bw_executor(game_runner=MockGameRunner())
        instance = MockInstance()
        _dispatch(executor, "enable_block_world_view", instance, {
            "camera_object": "obj_camera", "fov": 90, "render_distance": 10,
            "cell_size": 16, "wall_color": "#123456", "z_layer": 2,
            "top_cast_res": 8, "eye_height": 0.5,
        })
        cfg = block_world_state(executor.game_runner.current_room)["camera"]
        assert cfg["camera_object"] == "obj_camera"
        assert cfg["fov"] == 90
        assert cfg["render_distance"] == 10
        assert cfg["cell_size"] == 16
        assert cfg["wall_color"] == "#123456"
        assert cfg["z_layer"] == 2
        assert cfg["top_cast_res"] == 8
        assert cfg["eye_height"] == 0.5

    def test_pitch_is_clamped_here_too_not_just_at_render_time(self):
        """Was the one pitch-writing site (of four: this action,
        set_look_pitch, and the preview tool's two look controls) that
        didn't clamp -- rescued only by horizon_for's own defensive clamp at
        render time, so the STORED config value could still exceed the
        limit even though nothing could ever look further than it."""
        from extensions.block_world.renderer import MAX_PITCH_DEGREES
        executor = _bw_executor(game_runner=MockGameRunner())
        instance = MockInstance()
        _dispatch(executor, "enable_block_world_view", instance, {"pitch": 999})
        cfg = block_world_state(executor.game_runner.current_room)["camera"]
        assert cfg["pitch"] == MAX_PITCH_DEGREES

    def test_every_written_config_key_has_a_matching_action_parameter(self):
        """General guard for the class of bug eye_height/top_cast_res were:
        a config key the handler writes (so it clearly matters) but with no
        ActionParameter, so no author can ever reach it through the IDE. Not
        exhaustive of every read-only default, but every key this action
        itself sets should be a real, documented, settable parameter."""
        from extensions.block_world.actions import PLUGIN_ACTIONS

        executor = _bw_executor(game_runner=MockGameRunner())
        instance = MockInstance()
        _dispatch(executor, "enable_block_world_view", instance, {})
        cfg = block_world_state(executor.game_runner.current_room)["camera"]

        param_names = {p.name for p in PLUGIN_ACTIONS["enable_block_world_view"].parameters}
        # "enabled" is the stored/derived form of the "enable" parameter.
        # "vz" (Tier 7a) is pure internal runtime state -- always starts at
        # 0.0 here, only ever written afterward by jump/apply_gravity, never
        # something an author sets through enable_block_world_view itself.
        written_keys = set(cfg) - {"enabled", "vz"}
        missing = written_keys - param_names
        assert not missing, f"config keys with no matching ActionParameter: {missing}"

    def test_disable_clears_config(self):
        runner = MockGameRunner()
        block_world_state(runner.current_room)["camera"] = {"enabled": True, "camera_object": "x"}
        executor = _bw_executor(game_runner=runner)
        instance = MockInstance()
        _dispatch(executor, "enable_block_world_view", instance, {"enable": False})
        assert block_world_state(runner.current_room)["camera"] == {"enabled": False}

    def test_no_current_room_is_a_noop(self):
        runner = MockGameRunner()
        runner.current_room = None
        executor = _bw_executor(game_runner=runner)
        instance = MockInstance()
        _dispatch(executor, "enable_block_world_view", instance, {})  # must not raise


# ---------------------------------------------------------------------------
# cast_ray -- deterministic geometry
# ---------------------------------------------------------------------------

def _room(width, height):
    return GameRoom("test_room", {"width": width, "height": height}, action_executor=None)


class TestCastRay:
    def test_hits_block_at_expected_distance(self):
        room = _room(160, 160)
        set_block(room, 2, 0, 0, "stone")
        # Camera at grid (0.5, 0.5) i.e. (16, 16); ray along +x enters cell
        # (2, 0) at grid x=2 -> (2 - 0.5) = 1.5 cells = 48px.
        dist, side, hit, tex_u, block_type = cast_ray(room, 16, 16, 0, 0.0, 32, 20)
        assert dist == pytest.approx(48.0, abs=0.01)
        assert side == 0
        assert hit is True
        assert block_type == "stone"

    def test_perpendicular_ray_reports_the_other_side(self):
        room = _room(160, 160)
        set_block(room, 0, 2, 0, "dirt")
        dist, side, hit, tex_u, block_type = cast_ray(room, 16, 16, 0, math.pi / 2, 32, 20)
        assert dist == pytest.approx(48.0, abs=0.01)
        assert side == 1
        assert hit is True
        assert block_type == "dirt"

    def test_different_z_layer_is_independent(self):
        room = _room(160, 160)
        set_block(room, 2, 0, 5, "stone")  # placed on layer 5, not layer 0
        dist, side, hit, *_ = cast_ray(room, 16, 16, 0, 0.0, 32, 20)
        assert hit is False  # nothing on layer 0

        dist2, side2, hit2, *_ = cast_ray(room, 16, 16, 5, 0.0, 32, 20)
        assert hit2 is True
        assert dist2 == pytest.approx(48.0, abs=0.01)

    def test_no_blocks_reaches_max_cells(self):
        room = _room(64, 64)
        dist, side, hit, *_ = cast_ray(room, 16, 16, 0, 0.3, 32, 3)
        assert dist == pytest.approx(3 * 32, abs=0.01)
        assert hit is False

    def test_ray_enters_the_occupied_cell_from_any_direction(self):
        """Unlike raycast_2_5d's thin EDGE-based walls, a block fills its
        WHOLE cell -- a ray need not cross a specific registered line, just
        enter the occupied cell."""
        room = _room(160, 160)
        set_block(room, 1, 1, 0, "stone")
        dist, side, hit, *_ = cast_ray(room, 16, 16, 0, math.pi / 4, 32, 20)
        assert hit is True


class TestWallShade:
    def test_close_x_face_is_full_brightness(self):
        assert wall_shade(side=0, corrected=0.0, max_dist=100.0) == pytest.approx(1.0)

    def test_y_face_gets_the_side_hint(self):
        assert wall_shade(side=1, corrected=0.0, max_dist=100.0) == pytest.approx(SIDE_SHADE)

    def test_never_fully_black_at_max_distance(self):
        assert wall_shade(side=0, corrected=100.0, max_dist=100.0) == pytest.approx(
            max(MIN_SHADE, 1.0 - FOG_STRENGTH))


# ---------------------------------------------------------------------------
# render_block_world_view -- real Surface, pixel-sampled
# ---------------------------------------------------------------------------

def _camera_instance(name="obj_person", x=0, y=0, facing=0.0):
    """Top-left (0, 0) with a 32x32 footprint -- the renderer centers the ray
    origin at top_left + size/2, so this instance's centre lands at exactly
    (16, 16), i.e. grid (0.5, 0.5), matching TestCastRay's cast_ray(...)
    calls above (those pass px=16, py=16 directly)."""
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = 32
    inst._cached_height = 32
    inst.facing_angle = facing
    return inst


class TestRenderBlockWorldView:
    def test_no_camera_fills_flat_floor_and_ceiling_only(self):
        room = _room(160, 160)
        cfg = block_world_state(room)["camera"]
        cfg.update({"enabled": True, "camera_object": "obj_person"})
        screen = pygame.Surface((320, 240))
        render_block_world_view(room, screen)
        ceiling = room.parse_color(cfg.get("ceiling_color", "#87CEEB"))
        floor = room.parse_color(cfg.get("floor_color", "#3a2f1c"))
        assert screen.get_at((10, 10))[:3] == tuple(ceiling)
        assert screen.get_at((10, 230))[:3] == tuple(floor)

    def test_wall_column_drawn_with_flat_fallback_color(self):
        room = _room(320, 320)
        room.instances.append(_camera_instance())
        set_block(room, 2, 0, 0, "stone")
        cfg = block_world_state(room)["camera"]
        cfg.update({
            "eye_height": 0.5,  # 2a's look: eye at the middle of its layer
            "enabled": True, "camera_object": "obj_person", "z_layer": 0,
            "cell_size": 32, "columns": 64, "wall_textured": False,
            "wall_color": "#ff0000",
        })
        screen = pygame.Surface((320, 240))
        screen.fill((0, 255, 0))  # sentinel -- anything untouched stays green
        render_block_world_view(room, screen)
        center = screen.get_at((160, 120))[:3]
        assert center != (0, 255, 0), "expected the block wall to be drawn over the sentinel"
        assert center[0] > 0 and center[1] == 0 and center[2] == 0  # shaded pure red

    def test_wall_column_drawn_with_real_texture(self):
        """The textured path (the default) actually loads and blits one of
        the Phase 0 CC0 textures -- an end-to-end check that renderer.py,
        state.py's BLOCK_TYPES registry, and the imported PNGs all agree."""
        room = _room(320, 320)
        room.instances.append(_camera_instance())
        set_block(room, 2, 0, 0, "stone")
        cfg = block_world_state(room)["camera"]
        cfg.update({
            "eye_height": 0.5,  # 2a's look: eye at the middle of its layer
            "enabled": True, "camera_object": "obj_person", "z_layer": 0,
            "cell_size": 32, "columns": 64, "wall_textured": True,
        })
        screen = pygame.Surface((320, 240))
        screen.fill((0, 255, 0))
        render_block_world_view(room, screen)
        assert screen.get_at((160, 120))[:3] != (0, 255, 0)

    def test_no_hit_within_render_distance_leaves_floor_ceiling_showing(self):
        room = _room(320, 320)
        room.instances.append(_camera_instance())
        cfg = block_world_state(room)["camera"]
        cfg.update({"enabled": True, "camera_object": "obj_person", "render_distance": 2})
        screen = pygame.Surface((320, 240))
        render_block_world_view(room, screen)
        ceiling = tuple(room.parse_color(cfg.get("ceiling_color", "#87CEEB")))
        floor = tuple(room.parse_color(cfg.get("floor_color", "#3a2f1c")))
        assert screen.get_at((160, 60))[:3] == ceiling
        assert screen.get_at((160, 180))[:3] == floor


# ---------------------------------------------------------------------------
# extension wiring
# ---------------------------------------------------------------------------

def test_loading_registers_the_room_renderer():
    from runtime import extension_hooks
    load_all_plugins()
    names = [getattr(f, "__name__", "") for f in extension_hooks.get_room_renderers()]
    assert "render_room" in names, "block_world's room renderer was not registered"


def test_render_room_claims_a_block_world_room_and_declines_others():
    import extensions.block_world as ext

    class _Room:
        def __init__(self, cfg):
            self.extension_state = {"block_world": {"camera": cfg, "blocks": {}}} \
                if cfg is not None else {}

    drew = {"n": 0}
    from extensions.block_world import renderer
    real = renderer.render_block_world_view
    renderer.render_block_world_view = lambda room, screen: drew.update(n=drew["n"] + 1)
    try:
        assert ext.render_room(_Room({"enabled": True}), object()) is True
        assert drew["n"] == 1
    finally:
        renderer.render_block_world_view = real

    assert ext.render_room(_Room({"enabled": False}), object()) is False
    assert ext.render_room(_Room(None), object()) is False

    class _Bare:
        pass
    assert ext.render_room(_Bare(), object()) is False


def test_extension_contributes_the_setup_action():
    from extensions.block_world import PLUGIN_ACTIONS, PluginExecutor
    assert "enable_block_world_view" in PLUGIN_ACTIONS
    ex = PluginExecutor()
    assert callable(getattr(ex, "execute_enable_block_world_view_action", None))
