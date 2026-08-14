"""Regression tests for Block World's collision/footing primitives (Phase 4
Unit 4) and the move_and_collide action built on them (Unit 5).

ground_layer/can_enter/cell_of were promoted verbatim from
tools/preview_block_world.py, where they were proven first across every
viewpoint that tool's own walkaround exercises -- these tests pin the exact
same formulas now that they live in the engine.
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
from extensions.block_world.state import (  # noqa: E402
    DEFAULT_MAX_STEP_UP, block_world_state, can_enter, cell_of, ground_layer,
    set_block,
)

CELL = 32


def _room():
    return GameRoom("collision", {"width": 40 * CELL, "height": 40 * CELL},
                    action_executor=None)


# ---------------------------------------------------------------------------
# ground_layer / can_enter / cell_of (Unit 4)
# ---------------------------------------------------------------------------

class TestGroundLayer:
    def test_empty_column_is_layer_zero(self):
        room = _room()
        assert ground_layer(room, 3, 3) == 0

    def test_one_block_stands_on_layer_one(self):
        room = _room()
        set_block(room, 3, 3, 0, "stone")
        assert ground_layer(room, 3, 3) == 1

    def test_a_stack_stands_above_its_own_top(self):
        room = _room()
        set_block(room, 3, 3, 0, "stone")
        set_block(room, 3, 3, 1, "stone")
        set_block(room, 3, 3, 2, "stone")
        assert ground_layer(room, 3, 3) == 3

    def test_a_gap_does_not_confuse_it(self):
        """A stack with a hole still reports the TOP, not the hole -- this
        is footing, not occlusion; stack_top's own semantics apply."""
        room = _room()
        set_block(room, 3, 3, 0, "stone")
        set_block(room, 3, 3, 5, "stone")   # floating, gap at 1-4
        assert ground_layer(room, 3, 3) == 6


class TestCanEnter:
    def test_flat_ground_is_always_enterable(self):
        room = _room()
        assert can_enter(room, 1, 0, 0)   # both cells empty, both layer 0

    def test_a_single_step_up_is_enterable(self):
        room = _room()
        set_block(room, 1, 0, 0, "stone")   # ground_layer there == 1
        assert can_enter(room, 1, 0, 0)     # standing at layer 0, rise of 1

    def test_two_layers_up_is_a_wall_not_a_step(self):
        room = _room()
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")   # ground_layer there == 2
        assert not can_enter(room, 1, 0, 0)  # rise of 2 > DEFAULT_MAX_STEP_UP

    def test_a_drop_of_any_distance_is_always_enterable(self):
        """No falling animation yet -- a drop is just a step down."""
        room = _room()
        set_block(room, 0, 0, 0, "stone")
        set_block(room, 0, 0, 1, "stone")
        set_block(room, 0, 0, 2, "stone")
        set_block(room, 0, 0, 3, "stone")
        standing = ground_layer(room, 0, 0)  # 4
        assert can_enter(room, 5, 5, standing)  # empty ground far below

    def test_max_step_up_is_configurable(self):
        room = _room()
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")   # ground_layer there == 2
        assert not can_enter(room, 1, 0, 0, max_step_up=1)
        assert can_enter(room, 1, 0, 0, max_step_up=2)

    def test_default_max_step_up_is_one(self):
        assert DEFAULT_MAX_STEP_UP == 1


class TestCellOf:
    def test_rounds_to_the_nearest_multiple_of_cell_size(self):
        """cell_of(v) is round(v / CELL): the grid line v is CLOSEST to,
        not "which cell's span contains v" -- verified against the actual
        function rather than assumed, since the two only agree for the
        first half of each cell (see the -1/+1 pair straddling the CELL/2
        boundary below)."""
        assert cell_of(0, CELL) == 0
        assert cell_of(CELL / 2 - 1, CELL) == 0    # just below the boundary
        assert cell_of(CELL / 2, CELL) == 1        # exactly on it -- rounds up
        assert cell_of(CELL - 1, CELL) == 1        # most of the way to cell 1
        assert cell_of(CELL, CELL) == 1
        assert cell_of(CELL + CELL // 2 - 1, CELL) == 1

    def test_a_body_at_rest_maps_back_to_its_own_cell(self):
        """The convention every instance in this engine rests at: x/y sit
        at exact multiples of CELL (top-left, not centre -- see
        renderer.py's own comment on why picking/rendering separately add
        width/2, height/2 to get a centre), so a body that hasn't moved
        since being placed round-trips to its own cell index exactly."""
        for cell in (0, 1, 5, 12):
            assert cell_of(cell * CELL, CELL) == cell

    def test_negative_coordinates(self):
        assert cell_of(-1, CELL) == 0
        assert cell_of(-CELL / 2 - 1, CELL) == -1


# ---------------------------------------------------------------------------
# move_and_collide (Unit 5)
# ---------------------------------------------------------------------------

class MockRunner:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}


def _world(z_layer=0):
    room = _room()
    camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    camera._cached_object_data = {"solid": False}
    camera._cached_width = camera._cached_height = CELL
    camera.facing_angle = 0.0
    room.instances.append(camera)
    cfg = block_world_state(room)["camera"]
    cfg.update({"enabled": True, "camera_object": "obj_person",
                "cell_size": CELL, "z_layer": z_layer})
    return room, camera


def _run(room, instance, action, **params):
    ex = ActionExecutor(game_runner=MockRunner(room))
    load_all_plugins(ex)
    instance.action_executor = ex
    return ex.action_handlers[action](instance, params)


class TestMoveAndCollide:
    def test_moves_freely_on_open_ground(self):
        room, camera = _world()
        _run(room, camera, "move_and_collide", dx=10, dy=5)
        assert (camera.x, camera.y) == (10.0, 5.0)

    def test_a_tall_obstruction_blocks_movement(self):
        room, camera = _world()
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")   # 2 tall -- a wall, not a step
        _run(room, camera, "move_and_collide", dx=40, dy=0)
        assert camera.x == 0.0

    def test_a_single_block_is_climbed_as_a_step(self):
        room, camera = _world()
        set_block(room, 1, 0, 0, "stone")
        _run(room, camera, "move_and_collide", dx=40, dy=0)
        assert camera.x == 40.0
        assert block_world_state(room)["camera"]["z_layer"] == 1

    def test_walking_off_a_ledge_drops_the_footing(self):
        room, camera = _world(z_layer=3)
        camera.x, camera.y = 1 * CELL, 0
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")
        set_block(room, 1, 0, 2, "stone")   # standing on top, layer 3
        # Open ground one cell over -- a big drop, but always allowed.
        _run(room, camera, "move_and_collide", dx=40, dy=0)
        assert block_world_state(room)["camera"]["z_layer"] == 0

    def test_sliding_along_a_wall(self):
        """Blocked on x, open on y -- axis-separated movement lets the
        unblocked axis through, the same as every collision-aware sample
        in this repo."""
        room, camera = _world()
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")
        _run(room, camera, "move_and_collide", dx=40, dy=20)
        assert camera.x == 0.0
        assert camera.y == 20.0

    def test_collide_off_ignores_the_grid(self):
        room, camera = _world()
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")
        _run(room, camera, "move_and_collide", dx=40, dy=0, collide=False)
        assert camera.x == 40.0

    def test_a_non_camera_mover_does_not_touch_the_cameras_z_layer(self):
        """Moves and collides correctly; it just has nowhere engine-level
        to store its own footing yet (see the handler's own docstring)."""
        room, camera = _world()
        npc = GameInstance("obj_npc", 5 * CELL, 5 * CELL, {}, action_executor=None)
        npc._cached_object_data = {"solid": False}
        npc._cached_width = npc._cached_height = CELL
        room.instances.append(npc)
        set_block(room, 6, 5, 0, "stone")
        _run(room, npc, "move_and_collide", dx=40, dy=0)
        assert npc.x == 5 * CELL + 40
        assert block_world_state(room)["camera"]["z_layer"] == 0

    def test_respects_a_movers_true_sprite_origin(self):
        """Deliberate improvement over the preview tool's own shortcut
        (raw x/y): a sprite with a non-zero origin must collide by its true
        top-left (room._sprite_top_left), not its raw position."""
        from runtime.game_runner import GameSprite
        room, camera = _world()
        spr = GameSprite.__new__(GameSprite)
        spr.frames = [pygame.Surface((32, 32))]
        spr.origin_x = 16
        spr.origin_y = 16
        camera.sprite = spr
        camera.x = 16   # raw x=16, true top-left = 16-16 = 0 -> cell 0
        camera.y = 16
        set_block(room, 1, 0, 0, "stone")
        set_block(room, 1, 0, 1, "stone")
        _run(room, camera, "move_and_collide", dx=40, dy=0)
        assert camera.x == 16, "should still be blocked using the TRUE top-left"

    def test_no_active_view_is_a_noop(self):
        room, camera = _world()
        block_world_state(room)["camera"]["enabled"] = False
        _run(room, camera, "move_and_collide", dx=40, dy=0)
        assert camera.x == 0.0

    def test_no_current_room_does_not_raise(self):
        camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        ex = ActionExecutor(game_runner=MockRunner(None))
        load_all_plugins(ex)
        camera.action_executor = ex
        ex.action_handlers["move_and_collide"](camera, {"dx": 5, "dy": 5})
