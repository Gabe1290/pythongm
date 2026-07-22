"""Regression tests for the Doom/Wolfenstein-style raycast 2.5D view
(docs/RAYCAST_2_5D_PLAN.md, Phase 1: desktop core, flat-color walls).

Covers, in order: the new persistent facing_angle instance state + its
set_facing_angle action, the enable_raycast_view action (both via the
established MockGameRunner/MockRoom action_executor pattern), thin wall
EDGES derived from solid instances (_build_raycast_walls -- reworked
from an earlier coarse per-cell occupancy grid specifically so a wall
thinner than a cell, e.g. an 8px strip on a cell boundary, reads and
collides as thin rather than opaquing its whole cell; see the "complete
rethink" note in the plan doc), the DDA raycast core against
deterministic geometry with closed-form expected distances (not just
"doesn't crash" -- this is exactly the kind of assertion that caught the
inverted fade-alpha bug earlier this session), a real-Surface pixel-sample
render test, and an end-to-end smoke run of the actual samples/raycast_1
sample through the real GameRunner loop, mirroring
tools/smoke_run_samples.py's headless-injected-input pattern.
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

from conftest import import_module_directly, skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()
from runtime.game_runner import GameRoom, GameInstance  # noqa: E402
# The raycast renderer moved into its extension (Stage B2,
# docs/RAYCAST_EXTENSION_PLAN.md). These tests exercise it directly, so they
# call the moved module-level functions/constants; the enable_raycast_view /
# set_facing_angle action tests below still target the core ActionExecutor
# (those actions stay in core through Stage B3).
from extensions.raycast_2_5d import renderer as _rc  # noqa: E402
from extensions.raycast_2_5d.renderer import (  # noqa: E402
    build_raycast_walls, cast_ray, render_raycast_view, wall_shade,
    RAYCAST_MIN_SHADE, RAYCAST_SIDE_SHADE, RAYCAST_WALL_HEIGHT,
)


# ---------------------------------------------------------------------------
# set_facing_angle / enable_raycast_view actions
# ---------------------------------------------------------------------------

_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


class MockInstance:
    def __init__(self, object_name="obj_person"):
        self.object_name = object_name
        self.facing_angle = 0.0


class MockRoom:
    def __init__(self):
        self.raycast_camera = {'enabled': False}
        self._raycast_v_walls = None


class MockGameRunner:
    def __init__(self):
        self.current_room = MockRoom()
        self.global_variables = {}


class TestSetFacingAngle:
    def test_absolute(self):
        executor = ActionExecutor()
        instance = MockInstance()
        executor.execute_set_facing_angle_action(instance, {"angle": 90})
        assert instance.facing_angle == 90.0

    def test_relative_accumulates(self):
        executor = ActionExecutor()
        instance = MockInstance()
        instance.facing_angle = 10.0
        executor.execute_set_facing_angle_action(instance, {"angle": 5, "relative": True})
        assert instance.facing_angle == 15.0

    def test_wraps_to_0_360(self):
        executor = ActionExecutor()
        instance = MockInstance()
        instance.facing_angle = 350.0
        executor.execute_set_facing_angle_action(instance, {"angle": 20, "relative": True})
        assert instance.facing_angle == 10.0

    def test_negative_relative_wraps_backward(self):
        executor = ActionExecutor()
        instance = MockInstance()
        instance.facing_angle = 10.0
        executor.execute_set_facing_angle_action(instance, {"angle": -20, "relative": True})
        assert instance.facing_angle == 350.0

    def test_bad_value_defaults_to_zero(self):
        executor = ActionExecutor()
        instance = MockInstance()
        executor.execute_set_facing_angle_action(instance, {"angle": "not-a-number"})
        assert instance.facing_angle == 0.0


class TestEnableRaycastView:
    def test_enable_sets_config_with_defaults(self):
        executor = ActionExecutor(game_runner=MockGameRunner())
        instance = MockInstance()
        executor.execute_enable_raycast_view_action(instance, {})
        cfg = executor.game_runner.current_room.raycast_camera
        assert cfg['enabled'] is True
        assert cfg['camera_object'] == "obj_person"  # falls back to the caller
        assert cfg['fov'] == 66
        assert cfg['cell_size'] == 32

    def test_enable_honors_overrides(self):
        executor = ActionExecutor(game_runner=MockGameRunner())
        instance = MockInstance()
        executor.execute_enable_raycast_view_action(instance, {
            "camera_object": "obj_camera", "fov": 90, "render_distance": 10,
            "cell_size": 16, "wall_color": "#123456",
        })
        cfg = executor.game_runner.current_room.raycast_camera
        assert cfg['camera_object'] == "obj_camera"
        assert cfg['fov'] == 90
        assert cfg['render_distance'] == 10
        assert cfg['cell_size'] == 16
        assert cfg['wall_color'] == "#123456"

    def test_disable_clears_config(self):
        runner = MockGameRunner()
        runner.current_room.raycast_camera = {'enabled': True, 'camera_object': 'x'}
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()
        executor.execute_enable_raycast_view_action(instance, {"enable": False})
        assert runner.current_room.raycast_camera == {'enabled': False}

    def test_no_current_room_is_a_noop(self):
        runner = MockGameRunner()
        runner.current_room = None
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()
        executor.execute_enable_raycast_view_action(instance, {})  # must not raise

    def test_cell_size_change_invalidates_grid_cache(self):
        runner = MockGameRunner()
        runner.current_room._raycast_v_walls = {(0, 0)}
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()
        executor.execute_enable_raycast_view_action(instance, {"cell_size": 16})
        assert runner.current_room._raycast_v_walls is None


# ---------------------------------------------------------------------------
# Wall-grid derivation
# ---------------------------------------------------------------------------

def _room(width, height):
    return GameRoom("test_room", {"width": width, "height": height}, action_executor=None)


def _solid_instance(name, x, y, width=32, height=32):
    """A solid instance for raycast tests. Defaults to a square 32x32
    footprint -- the "roughly square -> block all 4 edges of its cell"
    fallback in _build_raycast_walls, i.e. old-style full-block wall
    behaviour, so most existing tests didn't need to change when the
    engine moved from coarse per-cell occupancy to real wall edges."""
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": True}
    inst._cached_width = width
    inst._cached_height = height
    return inst


def _nonsolid_instance(name, x, y):
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    return inst


def _sprited_instance(name, x, y, color, width=16, height=16):
    """A visible, non-solid instance with a real (single-frame, flat-
    color) sprite -- a billboard candidate (goal/pickup/monster), not a
    wall. GameSprite's normal constructor loads an image file from disk;
    tests build the frame surface directly instead."""
    from runtime.game_runner import GameSprite

    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = width
    inst._cached_height = height
    inst.visible = True
    sprite = GameSprite.__new__(GameSprite)
    frame = pygame.Surface((width, height))
    frame.fill(color)
    sprite.frames = [frame]
    inst.sprite = sprite
    inst.image_index = 0
    return inst


class TestBuildRaycastWalls:
    """_build_raycast_walls derives thin wall EDGES (v_walls/h_walls)
    from solid instances, keyed by absolute grid-line index -- not a
    per-cell occupancy grid. See docs/RAYCAST_2_5D_PLAN.md's
    "Complete rethink" section for why: a coarse per-cell grid can't
    represent a wall thinner than a cell, which is what a real
    Doom/Wolfenstein-style maze needs for corridors wide enough to
    actually turn corners in."""

    def test_square_solid_instance_blocks_all_four_edges_of_its_cell(self):
        room = _room(128, 128)
        room.instances.append(_solid_instance("obj_wall", 64, 32))  # grid (2, 1)
        build_raycast_walls(room, 32)
        assert room._raycast_v_walls == {(2, 1), (3, 1)}
        assert room._raycast_h_walls == {(2, 1), (2, 2)}

    def test_wide_thin_instance_is_a_horizontal_edge_segment(self):
        # 32 wide x 8 tall, centered on the grid line at y=1*32=32 ->
        # top-left y = 32 - 4 = 28.
        room = _room(128, 128)
        room.instances.append(_solid_instance("obj_wall_h", 0, 28, width=32, height=8))
        build_raycast_walls(room, 32)
        assert room._raycast_h_walls == {(0, 1)}
        assert room._raycast_v_walls == set()

    def test_tall_thin_instance_is_a_vertical_edge_segment(self):
        # 8 wide x 32 tall, centered on the grid line at x=1*32=32 ->
        # top-left x = 32 - 4 = 28.
        room = _room(128, 128)
        room.instances.append(_solid_instance("obj_wall_v", 28, 0, width=8, height=32))
        build_raycast_walls(room, 32)
        assert room._raycast_v_walls == {(1, 0)}
        assert room._raycast_h_walls == set()

    def test_non_solid_instance_ignored(self):
        room = _room(128, 128)
        room.instances.append(_nonsolid_instance("obj_person", 64, 32))
        build_raycast_walls(room, 32)
        assert room._raycast_v_walls == set()
        assert room._raycast_h_walls == set()

    def test_instance_with_no_cached_object_data_ignored(self):
        room = _room(128, 128)
        inst = GameInstance("obj_x", 0, 0, {}, action_executor=None)
        assert inst._cached_object_data is None
        room.instances.append(inst)
        build_raycast_walls(room, 32)  # must not raise
        assert room._raycast_v_walls == set()
        assert room._raycast_h_walls == set()


# ---------------------------------------------------------------------------
# DDA raycast core -- deterministic geometry, closed-form expected distances
# ---------------------------------------------------------------------------

class TestCastRay:
    def test_hits_solid_instance_at_expected_distance(self):
        room = _room(160, 160)
        room.instances.append(_solid_instance("obj_wall", 64, 0))  # grid (2, 0)
        build_raycast_walls(room, 32)
        # Camera at grid (0.5, 0.5), i.e. (16, 16); ray along +x hits the
        # wall's west face at grid x=2 -> (2.5 - 1) = 1.5 cells = 48px.
        dist, side, hit, *_ = cast_ray(room, 16, 16, 0.0, 32, 20)
        assert dist == pytest.approx(48.0, abs=0.01)
        assert side == 0
        assert hit is True

    def test_perpendicular_ray_reports_the_other_side(self):
        room = _room(160, 160)
        room.instances.append(_solid_instance("obj_wall", 0, 64))  # grid (0, 2)
        build_raycast_walls(room, 32)
        # Straight down (GM screen-space: angle pi/2 in this method's raw
        # math convention, since _cast_ray takes screen-space radians
        # directly -- see _render_raycast_view for the GM-angle mapping).
        dist, side, hit, *_ = cast_ray(room, 16, 16, math.pi / 2, 32, 20)
        assert dist == pytest.approx(48.0, abs=0.01)
        assert side == 1
        assert hit is True

    def test_thin_horizontal_wall_only_blocks_its_own_row(self):
        """The whole point of edge-based (not cell-occupancy-based) walls:
        a thin segment registered for one row must not leak into an
        adjacent row -- that's what makes a genuinely thin wall read (and
        collide) as thin rather than opaquing its entire cell."""
        room = _room(96, 96)
        # Horizontal segment across row 0's south edge only.
        room.instances.append(_solid_instance("obj_wall_h", 0, 28, width=32, height=8))
        build_raycast_walls(room, 32)
        # Ray straight down through row 0 hits it...
        dist, side, hit, *_ = cast_ray(room, 16, 4, math.pi / 2, 32, 20)
        assert dist == pytest.approx(28.0, abs=0.01)
        assert side == 1
        assert hit is True
        # ...but the same ray one row over (row 1, no wall registered
        # there) sails through to the render-distance cap instead.
        dist2, side2, hit2, *_ = cast_ray(room, 16, 36, math.pi / 2, 32, 3)
        assert dist2 == pytest.approx(3 * 32, abs=0.01)
        assert hit2 is False

    def test_no_walls_at_all_reaches_max_cells(self):
        # No implicit "out of room bounds = wall" anymore (see the
        # "complete rethink" note in docs/RAYCAST_2_5D_PLAN.md) -- an
        # unenclosed map is a content bug for a real maze, not something
        # the raycaster itself guards against; here it should just march
        # to max_cells and stop cleanly, no crash / no infinite loop.
        room = _room(64, 64)
        build_raycast_walls(room, 32)
        dist, side, hit, *_ = cast_ray(room, 16, 16, 0.3, 32, 3)
        assert dist == pytest.approx(3 * 32, abs=0.01)
        assert hit is False


# ---------------------------------------------------------------------------
# Render -- real Surface, pixel-sampled (not just "doesn't crash")
# ---------------------------------------------------------------------------

class TestRenderRaycastView:
    def _room_with_camera_and_wall(self):
        room = _room(160, 160)
        wall = _solid_instance("obj_wall", 96, 64)  # grid (3, 2)
        room.instances.append(wall)
        # Instance x/y is the sprite's top-left corner (matching every real
        # GameInstance) -- _render_raycast_view centers the ray origin in
        # the occupied cell itself (+ half width/height), so this is 16px
        # up-left of the intended center-of-cell-(0,2) ray origin (16, 80).
        camera = GameInstance("obj_person", 0, 64, {}, action_executor=None)
        camera.facing_angle = 0.0  # facing +x (right), toward the wall
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        return room

    def test_center_column_shows_wall_color(self):
        room = self._room_with_camera_and_wall()
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        px = screen.get_at((w // 2, h // 2))[:3]
        # The wall colour (#ff0000), darkened by the distance-falloff shading
        # model (see renderer.wall_shade) -- still a pure red hue.
        assert px[1] == 0 and px[2] == 0
        assert int(255 * RAYCAST_MIN_SHADE) <= px[0] <= 255
        assert px[0] > 0

    def test_corners_show_floor_and_ceiling(self):
        room = self._room_with_camera_and_wall()
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        assert screen.get_at((2, 2))[:3] == (0, 0, 255)          # ceiling
        assert screen.get_at((2, h - 2))[:3] == (0, 255, 0)       # floor

    def test_y_face_is_subtly_shaded_not_halved(self):
        """The y-face (side==1) gets a SUBTLE hint (RAYCAST_SIDE_SHADE) plus
        distance falloff -- NOT the old binary half-brightness. That 2:1 break
        made an h-wall/v-wall junction at equal distance read as a hard corner
        that slid along the wall as you moved (user report 2026-07-19)."""
        room = _room(160, 160)
        wall = _solid_instance("obj_wall", 0, 64)  # grid (0, 2) -- a y-face hit
        room.instances.append(wall)
        # See _room_with_camera_and_wall's comment -- (0, 0) + the
        # render code's own +16/+16 centering gives the intended (16, 16)
        # ray origin (center of grid cell (0, 0)).
        camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        camera.facing_angle = -90.0  # GM angle -90 -> screen-space +y (down)
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 10,
            'render_distance': 20, 'cell_size': 32, 'columns': 16,
            'wall_color': '#993333', 'floor_color': '#000000', 'ceiling_color': '#000000',
        }
        screen = pygame.Surface((160, 120))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        shaded = screen.get_at((w // 2, h // 2))[:3]
        # base wall colour is (153, 51, 51); the old model rendered exactly
        # half of it (76, 25, 25). The new one must be clearly BRIGHTER than
        # that (subtle side hint), while still darkened somewhat.
        assert shaded[0] > 76, f"y-face still looks halved: {shaded}"
        assert shaded[0] < 153, f"y-face should be darkened at all: {shaded}"
        assert shaded[1] == shaded[2]  # hue preserved (r,g,g of the base)

    def test_missing_camera_still_renders_floor_and_ceiling(self):
        room = _room(160, 160)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'does_not_exist',
            'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)  # must not raise
        w, h = screen.get_size()
        assert screen.get_at((2, 2))[:3] == (0, 0, 255)
        assert screen.get_at((2, h - 2))[:3] == (0, 255, 0)

    def test_miss_column_shows_no_wall_sliver_at_horizon(self):
        """Regression: a ray that reaches render_distance without crossing
        a registered wall edge used to still draw a wall-colored strip
        (dist_cells==max_cells, plus whatever `side` the last non-hit DDA
        step happened to leave behind), producing a thin horizontal sliver
        of wall color right at the horizon for every miss column -- exactly
        the "alternating stripes at the horizon, wall filling only part of
        the screen" a player reported as "I end up outside the map" when
        they were really just facing an opening wider than render_distance.
        No wall anywhere in range: every column must be pure ceiling above
        the horizon and pure floor below it, never wall_color."""
        room = _room(480, 480)
        camera = GameInstance("obj_person", 240, 240, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 5, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        for x in range(0, w, 4):
            assert screen.get_at((x, h // 2 - 1))[:3] == (0, 0, 255), f"col {x} leaked wall color above horizon"
            assert screen.get_at((x, h // 2 + 1))[:3] == (0, 255, 0), f"col {x} leaked wall color below horizon"

    def test_camera_origin_is_centered_not_the_sprite_corner(self):
        """Regression: _cast_ray used to be given camera.x/camera.y raw --
        the sprite's top-left corner, not its center. Every instance in a
        grid maze (walls and the player alike) sits at exact multiples of
        cell_size, so a player at rest against a wall has a raw (x, y)
        landing exactly on a wall-bearing grid line; DDA rays cast from
        exactly on that line hit it (or graze past it) almost immediately
        and inconsistently by angle. This is the real scenario a user hit
        and reported (with a screenshot) as "I go backward and end up
        outside the map": hold Down from raycast_1's room0 spawn, get
        correctly blocked at (29, 416) by the west wall -- y=416 is
        exactly 13*32, landing dead on the wall grid line separating the
        two rows on either side of the corridor. Still facing east
        (facing_angle unchanged by movement, unlike position), the actual
        corridor ahead is open for ~300px, but the raw-origin bug rendered
        a wall a few px away across most of the FOV, appearing to fill the
        whole screen. Uses the real, unmodified sample (through the actual
        GameRunner.run() loop, not a hand-initialized room -- object_data
        and sprite dimensions aren't resolved until real startup runs, and
        a partially-initialized room silently produces an empty or
        wrongly-shaped wall set that made an earlier version of this test
        pass for the wrong reason)."""
        from runtime.game_runner import GameRunner

        project_json = str(REPO_ROOT / "samples" / "raycast_1" / "project.json")
        runner = GameRunner(project_json)
        runner.language = "en"
        runner.show_message_dialog = lambda *a, **k: None
        runner.show_highscore_dialog = lambda *a, **k: None
        runner._show_name_entry_dialog = lambda *a, **k: ""
        runner.process_pending_messages = lambda *a, **k: None

        state = {"frames": 0, "checked": False, "origins": None}
        MAX_FRAMES = 65

        class _FakeClock:
            def tick(self, fps=0):
                f = state["frames"] = state["frames"] + 1
                if f == 1:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
                if f == 60 and not state["checked"]:
                    state["checked"] = True
                    room = runner.current_room
                    player = next(
                        i for i in room.instances if i.object_name == "obj_person"
                    )
                    # Intercept the real production call -- not a
                    # reimplementation of its math -- to see exactly what
                    # ray origin _render_raycast_view actually uses.
                    # Pixel-sampling the rendered output can't distinguish
                    # pre-fix from post-fix here: strip height caps at the
                    # full screen once dist <= cell_size (32px), and both
                    # the pre-fix ~3px and post-fix ~29-35px near-wall
                    # readings fall under that cap, rendering identically.
                    # Patch the extension's module-level cast_ray (the render
                    # calls it by bare name, so a module-attribute patch is what
                    # intercepts it now that it's no longer a GameRoom method).
                    real_cast_ray = _rc.cast_ray
                    seen = []

                    def _spy(room_arg, px, py, *a, **k):
                        seen.append((px, py))
                        return real_cast_ray(room_arg, px, py, *a, **k)

                    _rc.cast_ray = _spy
                    try:
                        render_raycast_view(runner.current_room, runner.screen)
                    finally:
                        _rc.cast_ray = real_cast_ray
                    state["origins"] = (seen, player.x, player.y, player._cached_width, player._cached_height)
                if f >= MAX_FRAMES:
                    runner.running = False
                return 0

            def get_fps(self):
                return 60.0

        real_clock = pygame.time.Clock
        pygame.time.Clock = _FakeClock
        try:
            runner.run()
        finally:
            pygame.time.Clock = real_clock

        assert state["checked"], "tick hook never ran -- test setup is broken"
        seen, px, py, pw, ph = state["origins"]
        assert seen, "_render_raycast_view never called _cast_ray"
        expected = (px + pw / 2, py + ph / 2)
        for origin in seen:
            assert origin == pytest.approx(expected), (
                f"_render_raycast_view cast a ray from {origin}, expected the sprite-centered "
                f"{expected} -- raw player position {(px, py)} sits exactly on a wall-bearing "
                "grid line at this maze position"
            )

    def test_disabled_room_takes_the_normal_render_path(self):
        room = self._room_with_camera_and_wall()
        room.raycast_camera['enabled'] = False
        screen = pygame.Surface((320, 240))
        screen.fill((10, 10, 10))
        room._render_room(screen, (0, 0))
        # Normal path doesn't fill flat floor/ceiling colors -- the
        # background_color fill from render() (not _render_room) is what
        # would normally show; here just confirm it did NOT take the
        # raycast branch's ceiling color at the top-left.
        assert screen.get_at((2, 2))[:3] != (0, 0, 255)


class TestTexturedWalls:
    """Phase 5: a wall renders a vertical strip sampled from its own sprite,
    not a flat colour -- when the wall's solid instance has a sprite and
    wall_textured isn't disabled."""

    def _sprited_solid_wall(self, color=(255, 0, 255)):
        from runtime.game_runner import GameSprite
        room = _room(160, 160)
        wall = _solid_instance("obj_wall", 96, 64)   # square -> all 4 edges
        sprite = GameSprite.__new__(GameSprite)
        frame = pygame.Surface((32, 32))
        frame.fill(color)
        sprite.frames = [frame]
        wall.sprite = sprite
        room.instances.append(wall)
        camera = GameInstance("obj_person", 0, 64, {}, action_executor=None)
        camera.facing_angle = 0.0                    # facing +x, toward the wall
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        return room

    def test_solid_wall_is_textured_with_its_own_sprite(self):
        room = self._sprited_solid_wall(color=(255, 0, 255))
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        # centre column shows the sprite's MAGENTA hue (darkened by the
        # distance-falloff shading), NOT the flat wall_color red
        r, g, b = screen.get_at((w // 2, h // 2))[:3]
        assert g == 0 and r > 0 and b > 0 and r == b   # magenta, scaled

    def test_wall_textured_false_forces_flat_colour(self):
        room = self._sprited_solid_wall(color=(255, 0, 255))
        room.raycast_camera['wall_textured'] = False
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        # flat wall_color red (#ff0000), scaled by the shading model
        r, g, b = screen.get_at((w // 2, h // 2))[:3]
        assert g == 0 and b == 0 and r > 0

    def test_y_face_texture_strip_gets_the_same_subtle_shading(self):
        """A y-face (side==1) texture strip gets the same subtle side hint +
        distance falloff as the flat path -- not the old binary half-brightness
        (mirrors the flat test's geometry: camera at (0,0) facing down into a
        wall on the (0,2) grid line)."""
        from runtime.game_runner import GameSprite
        room = _room(160, 160)
        wall = _solid_instance("obj_wall", 0, 64)    # grid (0, 2) -- y-face hit
        sprite = GameSprite.__new__(GameSprite)
        frame = pygame.Surface((32, 32))
        frame.fill((200, 200, 200))
        sprite.frames = [frame]
        wall.sprite = sprite
        room.instances.append(wall)
        camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        camera.facing_angle = -90.0                  # screen-space +y (down)
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 10,
            'render_distance': 20, 'cell_size': 32, 'columns': 16,
            'wall_color': '#993333', 'floor_color': '#000000', 'ceiling_color': '#000000',
        }
        screen = pygame.Surface((160, 120))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        # the 200-grey texture, multiplied by the shade factor. The old model
        # gave exactly 100 (half); the new one must be clearly brighter while
        # still darkened, and stay neutral grey.
        px = screen.get_at((w // 2, h // 2))[:3]
        assert px[0] == px[1] == px[2], f"should stay neutral grey: {px}"
        assert 100 < px[0] < 200, f"expected a subtle shade, got {px}"

    def test_cast_ray_returns_tex_u_and_sprite_on_hit(self):
        room = self._sprited_solid_wall()
        build_raycast_walls(room, 32)
        dist, side, hit, tex_u, sprite = cast_ray(room, 16, 80, 0.0, 32, 20)
        assert hit is True
        assert 0.0 <= tex_u < 1.0
        assert sprite is room.instances[0].sprite

    def test_cast_ray_miss_returns_no_texture(self):
        room = _room(160, 160)
        build_raycast_walls(room, 32)                # no walls at all
        dist, side, hit, tex_u, sprite = cast_ray(room, 16, 16, 0.0, 32, 5)
        assert hit is False
        assert tex_u == 0.0 and sprite is None

    def test_spriteless_wall_falls_back_to_flat_colour(self):
        """A solid wall whose instance has no sprite still renders (flat)."""
        room = _room(160, 160)
        wall = _solid_instance("obj_wall", 96, 64)   # no .sprite set
        room.instances.append(wall)
        camera = GameInstance("obj_person", 0, 64, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        # flat wall_color red, scaled by the shading model
        r, g, b = screen.get_at((w // 2, h // 2))[:3]
        assert g == 0 and b == 0 and r > 0


class TestSky:
    """Phase 5b: a DOOM-style sky over the ceiling region -- panned by
    facing_angle, not scaled by distance. Absent sky_texture -> the flat
    ceiling_color fill (unchanged)."""

    def _open_room_with_sky(self):
        """A wall-less room (whole ceiling is sky at every angle) + a camera,
        with a horizontal-gradient sky sprite registered by name so a pan is
        detectable pixel-to-pixel."""
        from runtime.game_runner import GameSprite
        room = _room(320, 320)
        camera = GameInstance("obj_person", 128, 128, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        # 256x64 horizontal gradient: R ramps 0..255 across the width, so any
        # horizontal pan changes the sampled colour.
        frame = pygame.Surface((256, 64))
        for x in range(256):
            frame.fill((x, 0, 255 - x), (x, 0, 1, 64))
        sky = GameSprite.__new__(GameSprite)
        sky.frames = [frame]
        room._all_sprites = {'spr_sky': sky}
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00',
            'ceiling_color': '#0000ff', 'sky_texture': 'spr_sky',
        }
        return room

    def test_sky_replaces_flat_ceiling(self):
        room = self._open_room_with_sky()
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        # a ceiling pixel is now sky (gradient R>0/G==0), not the flat blue fill
        px = screen.get_at((160, 8))[:3]
        assert px != (0, 0, 255), "sky did not replace the flat ceiling fill"
        assert px[1] == 0, "sampled pixel is not from the gradient sky"

    def test_sky_pans_with_facing_angle(self):
        room = self._open_room_with_sky()
        screen = pygame.Surface((320, 240))
        cam = next(i for i in room.instances if i.object_name == "obj_person")

        cam.facing_angle = 0.0
        render_raycast_view(room, screen)
        at0 = screen.get_at((160, 8))[:3]

        cam.facing_angle = 90.0
        render_raycast_view(room, screen)
        at90 = screen.get_at((160, 8))[:3]

        assert at0 != at90, "sky did not pan when the camera turned"

    def test_floor_still_flat_below_horizon(self):
        room = self._open_room_with_sky()
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        assert screen.get_at((w // 2, h - 4))[:3] == (0, 255, 0)  # floor_color

    def test_no_sky_texture_keeps_flat_ceiling(self):
        room = self._open_room_with_sky()
        del room.raycast_camera['sky_texture']
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        assert screen.get_at((160, 8))[:3] == (0, 0, 255)  # flat ceiling_color


class TestFloorCasting:
    """Phase 5: low-res floor/ceiling texture casting. Full-res per-pixel was
    ~13x too slow in pure Python (timing spike), so the floor is cast into a
    downsampled surface and upscaled."""

    def _open_room(self, floor_color='#00ff00', ceiling_color='#0000ff'):
        room = _room(320, 320)
        camera = GameInstance("obj_person", 128, 128, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': floor_color,
            'ceiling_color': ceiling_color,
        }
        return room

    def _solid_tex(self, color):
        from runtime.game_runner import GameSprite
        spr = GameSprite.__new__(GameSprite)
        frame = pygame.Surface((32, 32))
        frame.fill(color)
        spr.frames = [frame]
        return spr

    def test_floor_texture_replaces_flat_floor(self):
        room = self._open_room()
        room._all_sprites = {'spr_floor': self._solid_tex((200, 40, 160))}
        room.raycast_camera['floor_texture'] = 'spr_floor'
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        # a floor pixel near the bottom is now the texture colour, not flat green
        assert screen.get_at((w // 2, h - 4))[:3] == (200, 40, 160)

    def test_no_floor_texture_keeps_flat_floor(self):
        room = self._open_room()
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        assert screen.get_at((w // 2, h - 4))[:3] == (0, 255, 0)

    def test_ceiling_texture_casts_when_no_sky(self):
        room = self._open_room()
        room._all_sprites = {'spr_ceil': self._solid_tex((40, 200, 160))}
        room.raycast_camera['ceiling_texture'] = 'spr_ceil'
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        assert screen.get_at((w // 2, 4))[:3] == (40, 200, 160)

    def test_sky_wins_over_ceiling_texture(self):
        room = self._open_room()
        room._all_sprites = {
            'spr_ceil': self._solid_tex((40, 200, 160)),
            'spr_sky': self._solid_tex((10, 20, 30)),
        }
        room.raycast_camera['ceiling_texture'] = 'spr_ceil'
        room.raycast_camera['sky_texture'] = 'spr_sky'
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        # sky claimed the ceiling; the ceiling_texture must not appear
        assert screen.get_at((w // 2, 4))[:3] == (10, 20, 30)

    def test_floor_cast_res_is_configurable_and_safe(self):
        room = self._open_room()
        room._all_sprites = {'spr_floor': self._solid_tex((200, 40, 160))}
        room.raycast_camera['floor_texture'] = 'spr_floor'
        for res in (1, 2, 8):
            room.raycast_camera['floor_cast_res'] = res
            screen = pygame.Surface((320, 240))
            render_raycast_view(room, screen)  # must not raise
            assert screen.get_at((160, 236))[:3] == (200, 40, 160)

    def test_full_textured_pipeline_under_budget(self):
        """Walls + sky + floor together stay well under a frame budget at the
        real 480x480 sample size (floor casting is the expensive part; the
        spike put 4x downsample at ~5ms)."""
        import time
        room = _room(480, 480)
        for gx in range(15):
            room.instances.append(_solid_instance(f"w{gx}0", gx * 32, 0))
            room.instances.append(_solid_instance(f"w{gx}14", gx * 32, 14 * 32))
        camera = GameInstance("obj_person", 32, 416, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room._all_sprites = {
            'spr_wall': self._solid_tex((150, 74, 56)),
            'spr_sky': self._solid_tex((90, 150, 210)),
            'spr_floor': self._solid_tex((100, 96, 80)),
        }
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 320,
            'wall_color': '#993333', 'floor_color': '#464632', 'ceiling_color': '#87CEEB',
            'wall_texture': 'spr_wall', 'sky_texture': 'spr_sky',
            'floor_texture': 'spr_floor', 'floor_cast_res': 4,
        }
        screen = pygame.Surface((480, 480))
        frames = 20
        start = time.perf_counter()
        for i in range(frames):
            camera.facing_angle = (i / frames) * 360.0
            render_raycast_view(room, screen)
        ms = (time.perf_counter() - start) / frames * 1000
        assert ms < 25.0, f"full textured raycast took {ms:.1f}ms/frame (floor cast too slow?)"


class TestBillboardSprites:
    """Phase 6 of the plan doc, scoped down to a first cut: non-solid
    visible sprited instances (goals, pickups, monsters) render as a
    camera-facing sprite scaled by distance, occluded per-column against
    walls -- not just left invisible in the first-person view the way
    obj_goal was before this feature landed."""

    def test_visible_sprite_renders_in_front_of_camera(self):
        room = _room(160, 160)
        goal = _sprited_instance("obj_goal", 96, 16, (255, 255, 0))  # ahead, no wall between
        room.instances.append(goal)
        camera = GameInstance("obj_person", 16, 16, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        found = any(screen.get_at((x, h // 2))[:3] == (255, 255, 0) for x in range(w))
        assert found, "billboard sprite never appeared on screen despite a clear line of sight"

    def test_sprite_behind_wall_is_occluded(self):
        room = _room(160, 160)
        wall = _solid_instance("obj_wall", 64, 0)  # directly between camera and goal
        room.instances.append(wall)
        goal = _sprited_instance("obj_goal", 96, 16, (255, 255, 0))
        room.instances.append(goal)
        camera = GameInstance("obj_person", 16, 16, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        found = any(screen.get_at((x, h // 2))[:3] == (255, 255, 0) for x in range(w))
        assert not found, "billboard sprite showed through a wall standing directly in front of it"

    def test_solid_instances_are_not_billboarded(self):
        """Solid instances are walls, already drawn as strips -- rendering
        them a second time as a billboard would double-draw and also
        misread any solid pickup/monster as a wall-strip AND a sprite."""
        room = _room(160, 160)
        wall = _solid_instance("obj_wall_solid_sprited", 64, 16, width=16, height=16)
        wall.visible = True
        from runtime.game_runner import GameSprite
        sprite = GameSprite.__new__(GameSprite)
        frame = pygame.Surface((16, 16))
        frame.fill((255, 255, 0))
        sprite.frames = [frame]
        wall.sprite = sprite
        wall.image_index = 0
        room.instances.append(wall)
        camera = GameInstance("obj_person", 16, 16, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
            # Force flat-colour walls so the ONLY way the sprite's yellow could
            # appear is a (wrong) billboard double-draw. With Phase 5 texturing
            # on, this solid wall would legitimately be textured with its own
            # yellow sprite, which is a separate behaviour (see
            # test_solid_wall_is_textured_with_its_own_sprite).
            'wall_textured': False,
        }
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        # The wall strip itself (drawn as wall_color) is expected; the
        # sprite's own yellow must never appear anywhere.
        found_yellow = any(
            screen.get_at((x, y))[:3] == (255, 255, 0) for x in range(0, w, 4) for y in range(0, h, 4)
        )
        assert not found_yellow, "a solid instance's sprite was billboarded on top of its wall strip"

    def test_camera_object_itself_is_never_billboarded(self):
        room = _room(160, 160)
        camera = _sprited_instance("obj_person", 16, 16, (255, 255, 0))
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)  # must not raise, and not draw itself
        w, h = screen.get_size()
        found_yellow = any(
            screen.get_at((x, y))[:3] == (255, 255, 0) for x in range(0, w, 4) for y in range(0, h, 4)
        )
        assert not found_yellow, "the camera's own instance was drawn as a billboard sprite"

    def test_nearer_sprite_draws_over_farther_one(self):
        """Painter's algorithm: two overlapping billboards must show the
        nearer one on top, not whichever happens to iterate last."""
        room = _room(160, 160)
        # Camera center is (32, 32) (default 32x32 GameInstance). Both
        # sprites' centers sit on y=32 too -- directly along the facing=0
        # ray, at different distances, so they genuinely overlap on
        # screen instead of merely being near each other.
        far = _sprited_instance("obj_far", 120, 20, (0, 255, 255), width=24, height=24)
        near = _sprited_instance("obj_near", 60, 20, (255, 0, 255), width=24, height=24)
        room.instances.append(far)
        room.instances.append(near)
        camera = GameInstance("obj_person", 16, 16, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        center = screen.get_at((w // 2, h // 2))[:3]
        assert center == (255, 0, 255), f"expected the nearer sprite's color at screen center, got {center}"


# ---------------------------------------------------------------------------
# Performance -- the one real technical risk this plan's Phase 0 spike
# flagged (pure-Python raycasting, no numpy). The spike measured ~1.6ms/
# frame for 320 columns against maze_1's real 15x15 grid on this machine;
# this guards against a future regression collapsing that headroom (e.g.
# an accidentally-quadratic change to _build_raycast_walls or _cast_ray).
# ---------------------------------------------------------------------------

class TestRaycastPerformance:
    def test_render_stays_well_under_frame_budget(self):
        import time

        room = _room(480, 480)  # matches maze_1/raycast_1's real room size
        for gx in range(15):
            room.instances.append(_solid_instance(f"w{gx}0", gx * 32, 0))
            room.instances.append(_solid_instance(f"w{gx}14", gx * 32, 14 * 32))
        camera = GameInstance("obj_person", 32, 416, {}, action_executor=None)
        camera.facing_angle = 0.0
        room.instances.append(camera)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 320,
            'wall_color': '#993333', 'floor_color': '#464632', 'ceiling_color': '#87CEEB',
        }
        screen = pygame.Surface((640, 480))

        frames = 30
        start = time.perf_counter()
        for i in range(frames):
            camera.facing_angle = (i / frames) * 360.0
            render_raycast_view(room, screen)
        elapsed_ms_per_frame = (time.perf_counter() - start) / frames * 1000

        # Generous ceiling (Phase 0's spike measured ~1.6ms on this
        # machine) -- this is a regression guard, not a hardware
        # benchmark, so it leaves large headroom for slower CI runners.
        assert elapsed_ms_per_frame < 20.0, (
            f"raycast render took {elapsed_ms_per_frame:.2f}ms/frame, "
            "expected well under 20ms (30+ fps of headroom)"
        )


# ---------------------------------------------------------------------------
# End-to-end smoke run of the real sample through the real GameRunner loop
# ---------------------------------------------------------------------------

class TestRaycast1SampleSmoke:
    def test_runs_without_crashing_and_facing_angle_responds_to_input(self):
        from runtime.game_runner import GameRunner

        project_json = str(REPO_ROOT / "samples" / "raycast_1" / "project.json")
        runner = GameRunner(project_json)
        runner.language = "en"
        runner.show_message_dialog = lambda *a, **k: None
        runner.show_highscore_dialog = lambda *a, **k: None
        runner._show_name_entry_dialog = lambda *a, **k: ""
        runner.process_pending_messages = lambda *a, **k: None

        state = {"frames": 0}
        MAX_FRAMES = 60

        class _FakeClock:
            def tick(self, fps=0):
                f = state["frames"] = state["frames"] + 1
                if f == 5:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
                if f == 35:
                    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_LEFT))
                if f >= MAX_FRAMES:
                    runner.running = False
                return 0

            def get_fps(self):
                return 60.0

        real_clock = pygame.time.Clock
        pygame.time.Clock = _FakeClock
        try:
            result = runner.run()
        finally:
            pygame.time.Clock = real_clock

        assert result is not False, "game loop reported a fatal crash"
        assert state["frames"] == MAX_FRAMES

        player = next(i for i in runner.current_room.instances if i.object_name == "obj_person")
        # 30 held frames * 3 deg/frame = 90 degrees turned left.
        assert player.facing_angle == pytest.approx(90.0, abs=0.01)
        assert runner.current_room.raycast_camera['enabled'] is True

    def test_player_is_blocked_by_walls_not_walking_through_them(self):
        """Regression: obj_person's continuous FPS-style movement (via
        set_direction_speed, not the grid-snapped start_moving_direction
        maze_1 uses) needs a *registered* collision_with_obj_wall handler
        for the engine's movement-blocking optimization to even run the
        check -- it's gated behind get_collision_listened_types(), not
        automatic just because obj_wall is solid. The first version of
        this sample dropped that handler (reasoning the AABB block was
        unconditional -- it isn't: registration is required even though
        the block itself doesn't depend on the handler's actions), so the
        player walked straight through every wall. Empty-actions handler
        fixes it; this pins the fix by holding forward into a known wall
        for far longer than the room is wide and confirming the player
        never leaves room bounds."""
        from runtime.game_runner import GameRunner

        project_json = str(REPO_ROOT / "samples" / "raycast_1" / "project.json")
        runner = GameRunner(project_json)
        runner.language = "en"
        runner.show_message_dialog = lambda *a, **k: None
        runner.show_highscore_dialog = lambda *a, **k: None
        runner._show_name_entry_dialog = lambda *a, **k: ""
        runner.process_pending_messages = lambda *a, **k: None

        state = {"frames": 0}
        MAX_FRAMES = 200  # 200 * 3px/frame = 600px, more than the 480px room

        class _FakeClock:
            def tick(self, fps=0):
                f = state["frames"] = state["frames"] + 1
                if f == 1:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
                if f >= MAX_FRAMES:
                    runner.running = False
                return 0

            def get_fps(self):
                return 60.0

        real_clock = pygame.time.Clock
        pygame.time.Clock = _FakeClock
        try:
            runner.run()
        finally:
            pygame.time.Clock = real_clock

        player = next(i for i in runner.current_room.instances if i.object_name == "obj_person")
        room = runner.current_room
        assert 0 <= player.x <= room.width, (
            f"player.x={player.x} escaped room bounds [0, {room.width}] -- "
            "walked through a wall"
        )
        assert 0 <= player.y <= room.height, (
            f"player.y={player.y} escaped room bounds [0, {room.height}] -- "
            "walked through a wall"
        )

    def test_player_can_turn_a_corner_in_the_maze(self):
        """Regression covering the full "complete rethink" fix described
        in docs/RAYCAST_2_5D_PLAN.md: raycast_1's walls were converted
        from full-cell 32px blocks to thin (8px) edge segments (a real
        engine change -- see the raycast extension's build_raycast_walls/cast_ray),
        because the earlier fix (just shrinking the player's collision
        bbox within full-cell-block corridors) still weren't reliably
        enough clearance to turn every corner. This walks the player east
        along the spawn corridor to the far wall, turns 90 degrees left
        with a realistic multi-frame gap between releasing forward and
        starting the turn (so residual velocity from the old direction
        can't confound the result), then walks forward again and confirms
        real progress deep into the next corridor -- not just barely
        crossing the threshold."""
        from runtime.game_runner import GameRunner

        project_json = str(REPO_ROOT / "samples" / "raycast_1" / "project.json")
        runner = GameRunner(project_json)
        runner.language = "en"
        runner.show_message_dialog = lambda *a, **k: None
        runner.show_highscore_dialog = lambda *a, **k: None
        runner._show_name_entry_dialog = lambda *a, **k: ""
        runner.process_pending_messages = lambda *a, **k: None

        class _FakeClock:
            def __init__(self):
                self.f = 0

            def tick(self, fps=0):
                self.f += 1
                f = self.f
                if f == 1:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
                if f == 200:  # long enough to reach the far wall and stop there
                    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_UP))
                if f == 205:  # realistic gap -- lets `nokey` zero hspeed/vspeed first
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
                if f == 235:  # 30 frames * 3 deg/frame = 90 degrees, now facing north
                    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_LEFT))
                if f == 240:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
                if f == 300:
                    runner.running = False
                return 0

            def get_fps(self):
                return 60.0

        real_clock = pygame.time.Clock
        pygame.time.Clock = _FakeClock
        try:
            runner.run()
        finally:
            pygame.time.Clock = real_clock

        player = next(i for i in runner.current_room.instances if i.object_name == "obj_person")
        assert player.facing_angle == pytest.approx(90.0, abs=0.01)
        # Started at y=416 (grid row 13); reaching y=239 requires having
        # turned the corner and walked deep into the next corridor
        # segment, not just barely nudging past the old blocking point.
        assert player.y < 300, (
            f"player.y={player.y} didn't make real progress after turning -- "
            "corner turn failed or movement stalled"
        )
