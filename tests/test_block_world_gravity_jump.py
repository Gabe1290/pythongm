"""Jump mechanic (Tier 7a, docs/DEFERRED_GAPS_2026_PLAN.md): vertical
velocity, gravity accumulation, and real landing detection for the block
world's first-person camera.

Desktop-engine only, matching the plan's own scoping (like Tier 5.1) --
HTML5/Kivy export parity is a separate, later unit, not part of this one.

Design recap (see handlers.py docstrings for the full reasoning):
  - move_and_collide's ORIGINAL instant-footing behaviour (snap to ground
    in both directions, no falling) is preserved EXACTLY when gravity is
    not configured (enable_block_world_view's `gravity` param defaults to
    0) -- every project that predates this tier is unaffected.
  - gravity > 0 switches on real physics: apply_gravity (bind in the Step
    event, unconditional every frame) integrates vz/z_layer and lands
    cleanly; jump (bind to a key press) gives upward velocity, but only
    while grounded, so it cannot double-jump or fly.
  - move_and_collide's step-up gate compares the mover's ACTUAL height
    against the target cell, not the ground directly below it -- those
    differ once airborne, and using ground-below would wrongly refuse or
    allow moves for a body already off the ground.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from runtime.game_runner import GameRoom, GameInstance  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.block_world.state import block_world_state, set_block  # noqa: E402
from extensions.block_world.handlers import (  # noqa: E402
    DEFAULT_GRAVITY, DEFAULT_JUMP_SPEED)

CELL = 32


class _Runner:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}


def _world(gravity=0.0, z_layer=0.0):
    room = GameRoom("gravity", {"width": 40 * CELL, "height": 40 * CELL},
                     action_executor=None)
    camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    camera._cached_object_data = {"solid": False}
    camera._cached_width = camera._cached_height = CELL
    camera.facing_angle = 0.0
    room.instances.append(camera)
    cfg = block_world_state(room)["camera"]
    cfg.update({"enabled": True, "camera_object": "obj_person", "cell_size": CELL,
                "z_layer": z_layer, "vz": 0.0, "gravity": gravity,
                "fov": 66, "render_distance": 20, "columns": 1,
                "wall_textured": False, "eye_height": 0.5})
    return room, camera, cfg


def _run(room, camera, action, **params):
    ex = ActionExecutor(game_runner=_Runner(room))
    load_all_plugins(ex)
    camera.action_executor = ex
    return ex.action_handlers[action](camera, params)


class TestLegacyBehaviourUnchangedWhenGravityIsOff:
    def test_moving_onto_lower_ground_still_snaps_instantly(self):
        """gravity=0 (the default) -- the ORIGINAL behaviour: a drop is
        just a step down, no falling."""
        room, camera, cfg = _world(gravity=0.0, z_layer=3.0)
        set_block(room, 0, 0, 0, "stone")
        set_block(room, 0, 0, 1, "stone")
        set_block(room, 0, 0, 2, "stone")  # ground_layer(0,0) == 3
        # Move sideways onto an all-air column -- ground_layer == 0 there.
        _run(room, camera, "move_and_collide", dx=CELL, dy=0)
        assert cfg["z_layer"] == 0  # snapped instantly, no gravity involved

    def test_apply_gravity_is_a_noop_without_gravity_configured(self):
        room, camera, cfg = _world(gravity=0.0, z_layer=5.0)
        _run(room, camera, "apply_gravity")
        assert cfg["z_layer"] == 5.0
        assert cfg.get("vz", 0.0) == 0.0

    def test_jump_is_a_noop_without_gravity_configured(self):
        room, camera, cfg = _world(gravity=0.0, z_layer=0.0)
        _run(room, camera, "jump")
        assert cfg.get("vz", 0.0) == 0.0


class TestJumpArc:
    def test_jump_gives_upward_velocity_only_when_grounded(self):
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=0.0)
        _run(room, camera, "jump")
        assert cfg["vz"] == DEFAULT_JUMP_SPEED

    def test_jump_while_airborne_is_refused(self):
        """No double-jump/flying by mashing the key."""
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=0.0)
        _run(room, camera, "jump")
        first_vz = cfg["vz"]
        _run(room, camera, "jump")  # already airborne -- must not stack
        assert cfg["vz"] == first_vz

    def test_full_arc_rises_then_lands_back_on_flat_ground(self):
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=0.0)
        _run(room, camera, "jump")

        heights = []
        for _ in range(200):
            _run(room, camera, "apply_gravity")
            heights.append(cfg["z_layer"])
            if cfg["vz"] == 0.0 and cfg["z_layer"] == 0.0:
                break

        assert max(heights) > 0.0  # really left the ground
        assert cfg["z_layer"] == 0.0  # landed back exactly on it
        assert cfg["vz"] == 0.0
        # A real arc: height rises then falls, not monotonic in one direction.
        peak_index = heights.index(max(heights))
        assert 0 < peak_index < len(heights) - 1

    def test_falling_speed_is_capped_at_terminal_velocity(self):
        from extensions.block_world.handlers import TERMINAL_FALL_SPEED
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=1000.0)
        for _ in range(2000):
            _run(room, camera, "apply_gravity")
        assert cfg["vz"] >= TERMINAL_FALL_SPEED


class TestFallingOffALedge:
    def test_walking_off_a_ledge_in_gravity_mode_does_not_snap_down(self):
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=1.0)
        set_block(room, 0, 0, 0, "stone")  # ground_layer(0,0) == 1, camera grounded there
        # Adjacent column is all air (ground_layer == 0).
        _run(room, camera, "move_and_collide", dx=CELL, dy=0)
        assert cfg["z_layer"] == 1.0  # NOT snapped down -- still airborne height

    def test_then_apply_gravity_carries_it_down_to_the_real_ground(self):
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=1.0)
        set_block(room, 0, 0, 0, "stone")
        _run(room, camera, "move_and_collide", dx=CELL, dy=0)
        assert cfg["z_layer"] == 1.0

        for _ in range(500):
            _run(room, camera, "apply_gravity")
            if cfg["vz"] == 0.0 and cfg["z_layer"] == 0.0:
                break
        assert cfg["z_layer"] == 0.0
        assert cfg["vz"] == 0.0


class TestStepUpStillInstantInGravityMode:
    def test_stepping_onto_a_one_block_rise_snaps_immediately(self):
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=0.0)
        set_block(room, 1, 0, 0, "stone")  # one cell ahead, ground_layer(1,0) == 1
        _run(room, camera, "move_and_collide", dx=CELL, dy=0)
        assert cfg["z_layer"] == 1.0  # instant step-up, not a slow rise
        assert cfg["vz"] == 0.0


class TestCanEnterUsesActualHeightNotGroundBelowWhenAirborne:
    def test_airborne_body_is_not_blocked_by_a_tall_obstacle_it_is_above(self):
        """The mover is 2 layers up (mid-jump) over open ground; an
        adjacent column has a 2-layer-tall stack (ground_layer == 2).
        Using ground-BELOW as the step-up reference would wrongly refuse
        this move (0 -> 2 exceeds max_step_up); using the mover's actual
        height (2) correctly allows it."""
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=2.0)
        cfg["vz"] = 0.5  # mid-air, e.g. still rising from a jump
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")  # ground_layer(1,0) == 2
        _run(room, camera, "move_and_collide", dx=CELL, dy=0)
        assert camera.x == CELL  # the move was allowed

    def test_grounded_body_is_still_blocked_by_the_same_obstacle(self):
        """Same world, but grounded (not airborne) at layer 0 -- the
        original wall-vs-step distinction must still hold."""
        room, camera, cfg = _world(gravity=DEFAULT_GRAVITY, z_layer=0.0)
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")  # ground_layer(1,0) == 2, too tall to step onto
        _run(room, camera, "move_and_collide", dx=CELL, dy=0)
        assert camera.x == 0  # refused
