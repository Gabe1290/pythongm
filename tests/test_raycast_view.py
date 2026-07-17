"""Regression tests for the Doom/Wolfenstein-style raycast 2.5D view
(docs/RAYCAST_2_5D_PLAN.md, Phase 1: desktop core, flat-color walls).

Covers, in order: the new persistent facing_angle instance state + its
set_facing_angle action, the enable_raycast_view action (both via the
established MockGameRunner/MockRoom action_executor pattern), the wall
grid derived from solid instances, the DDA raycast core against
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
        self._raycast_grid = None


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
        runner.current_room._raycast_grid = {(0, 0): True}
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()
        executor.execute_enable_raycast_view_action(instance, {"cell_size": 16})
        assert runner.current_room._raycast_grid is None


# ---------------------------------------------------------------------------
# Wall-grid derivation
# ---------------------------------------------------------------------------

def _room(width, height):
    return GameRoom("test_room", {"width": width, "height": height}, action_executor=None)


def _solid_instance(name, x, y):
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": True}
    return inst


def _nonsolid_instance(name, x, y):
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    return inst


class TestBuildRaycastGrid:
    def test_solid_instance_marks_its_cell(self):
        room = _room(128, 128)
        room.instances.append(_solid_instance("obj_wall", 64, 32))
        room._build_raycast_grid(32)
        assert room._raycast_grid == {(2, 1): True}

    def test_non_solid_instance_ignored(self):
        room = _room(128, 128)
        room.instances.append(_nonsolid_instance("obj_person", 64, 32))
        room._build_raycast_grid(32)
        assert room._raycast_grid == {}

    def test_instance_with_no_cached_object_data_ignored(self):
        room = _room(128, 128)
        inst = GameInstance("obj_x", 0, 0, {}, action_executor=None)
        assert inst._cached_object_data is None
        room.instances.append(inst)
        room._build_raycast_grid(32)  # must not raise
        assert room._raycast_grid == {}


class TestRaycastIsWall:
    def test_out_of_bounds_is_wall(self):
        room = _room(128, 128)
        room._build_raycast_grid(32)
        assert room._raycast_is_wall(-1, 0, 32) is True
        assert room._raycast_is_wall(0, -1, 32) is True
        assert room._raycast_is_wall(4, 0, 32) is True  # 4*32=128 >= width
        assert room._raycast_is_wall(0, 4, 32) is True

    def test_in_bounds_empty_cell_is_not_wall(self):
        room = _room(128, 128)
        room._build_raycast_grid(32)
        assert room._raycast_is_wall(0, 0, 32) is False

    def test_in_bounds_solid_cell_is_wall(self):
        room = _room(128, 128)
        room.instances.append(_solid_instance("obj_wall", 64, 32))
        room._build_raycast_grid(32)
        assert room._raycast_is_wall(2, 1, 32) is True


# ---------------------------------------------------------------------------
# DDA raycast core -- deterministic geometry, closed-form expected distances
# ---------------------------------------------------------------------------

class TestCastRay:
    def test_hits_room_edge_at_expected_distance(self):
        # No solid instances -- the only "wall" is the room boundary.
        # Camera at grid-cell-center (0.5, 0.5) facing +x (angle 0): the
        # ray travels through cells x=0..4 and hits the out-of-bounds
        # edge at grid x=5 (room width 160 = 5 cells of 32).
        # side_x starts at (1 - 0.5) = 0.5, then advances by 1.0 per
        # cell; it reports the hit at side_x - delta_x = 5.5 - 1 = 4.5
        # cells = 144px.
        room = _room(160, 64)
        room._build_raycast_grid(32)
        dist, side = room._cast_ray(16, 16, 0.0, 32, 20)
        assert dist == pytest.approx(144.0, abs=0.01)
        assert side == 0

    def test_hits_solid_instance_at_expected_distance(self):
        room = _room(160, 160)
        room.instances.append(_solid_instance("obj_wall", 64, 0))  # grid (2, 0)
        room._build_raycast_grid(32)
        # Camera at grid (0.5, 0.5), i.e. (16, 16); ray along +x hits the
        # wall's west face at grid x=2 -> (2.5 - 1) = 1.5 cells = 48px.
        dist, side = room._cast_ray(16, 16, 0.0, 32, 20)
        assert dist == pytest.approx(48.0, abs=0.01)
        assert side == 0

    def test_perpendicular_ray_reports_the_other_side(self):
        room = _room(160, 160)
        room.instances.append(_solid_instance("obj_wall", 0, 64))  # grid (0, 2)
        room._build_raycast_grid(32)
        # Straight down (GM screen-space: angle pi/2 in this method's raw
        # math convention, since _cast_ray takes screen-space radians
        # directly -- see _render_raycast_view for the GM-angle mapping).
        dist, side = room._cast_ray(16, 16, math.pi / 2, 32, 20)
        assert dist == pytest.approx(48.0, abs=0.01)
        assert side == 1

    def test_ray_within_a_single_open_cell_reaches_render_distance(self):
        room = _room(64, 64)  # 2x2 cells, all open
        room._build_raycast_grid(32)
        dist, side = room._cast_ray(16, 16, 0.3, 32, 3)
        # max_cells=3 with nothing to hit inside the room bounds along
        # this short ray -- but the room edge is still a wall, so this
        # mostly guards against an infinite loop / crash on a tiny map.
        assert dist > 0


# ---------------------------------------------------------------------------
# Render -- real Surface, pixel-sampled (not just "doesn't crash")
# ---------------------------------------------------------------------------

class TestRenderRaycastView:
    def _room_with_camera_and_wall(self):
        room = _room(160, 160)
        wall = _solid_instance("obj_wall", 96, 64)  # grid (3, 2)
        room.instances.append(wall)
        camera = GameInstance("obj_person", 16, 80, {}, action_executor=None)
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
        room._render_raycast_view(screen)
        w, h = screen.get_size()
        assert screen.get_at((w // 2, h // 2))[:3] == (255, 0, 0)

    def test_corners_show_floor_and_ceiling(self):
        room = self._room_with_camera_and_wall()
        screen = pygame.Surface((320, 240))
        room._render_raycast_view(screen)
        w, h = screen.get_size()
        assert screen.get_at((2, 2))[:3] == (0, 0, 255)          # ceiling
        assert screen.get_at((2, h - 2))[:3] == (0, 255, 0)       # floor

    def test_missing_camera_still_renders_floor_and_ceiling(self):
        room = _room(160, 160)
        room.raycast_camera = {
            'enabled': True, 'camera_object': 'does_not_exist',
            'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        }
        screen = pygame.Surface((320, 240))
        room._render_raycast_view(screen)  # must not raise
        w, h = screen.get_size()
        assert screen.get_at((2, 2))[:3] == (0, 0, 255)
        assert screen.get_at((2, h - 2))[:3] == (0, 255, 0)

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


# ---------------------------------------------------------------------------
# Performance -- the one real technical risk this plan's Phase 0 spike
# flagged (pure-Python raycasting, no numpy). The spike measured ~1.6ms/
# frame for 320 columns against maze_1's real 15x15 grid on this machine;
# this guards against a future regression collapsing that headroom (e.g.
# an accidentally-quadratic change to _build_raycast_grid or _cast_ray).
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
            'wall_color': '#993333', 'floor_color': '#464632', 'ceiling_color': '#1e1e28',
        }
        screen = pygame.Surface((640, 480))

        frames = 30
        start = time.perf_counter()
        for i in range(frames):
            camera.facing_angle = (i / frames) * 360.0
            room._render_raycast_view(screen)
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
