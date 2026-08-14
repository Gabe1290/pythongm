"""Regression tests for Block World's hotbar (Phase 3 Unit 3).

Scoped deliberately small, per docs/VOXEL_WORLD_PLAN.md's Phase 3 notes: a
fixed DEFAULT_HOTBAR list and one action (select_hotbar_slot) that writes
two plain instance attributes. place_block itself needs no change -- its
`block` parameter already resolves a bare instance-variable-name expression,
so binding it to the literal string "hotbar_block" is the whole integration.
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
from extensions.block_world.state import DEFAULT_HOTBAR, block_world_state, get_block, set_block  # noqa: E402

CELL = 32


class _Runner:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}


def _world():
    room = GameRoom("hotbar", {"width": 40 * CELL, "height": 40 * CELL},
                    action_executor=None)
    camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    camera._cached_object_data = {"solid": False}
    camera._cached_width = camera._cached_height = CELL
    camera.facing_angle = 0.0
    room.instances.append(camera)
    cfg = block_world_state(room)["camera"]
    cfg.update({"enabled": True, "camera_object": "obj_person", "cell_size": CELL,
                "z_layer": 0, "fov": 66, "render_distance": 20, "columns": 1,
                "wall_textured": False, "eye_height": 0.5})
    return room, camera


def _run(room, camera, action, **params):
    ex = ActionExecutor(game_runner=_Runner(room))
    load_all_plugins(ex)
    camera.action_executor = ex
    return ex.action_handlers[action](camera, params)


class TestSelectHotbarSlot:
    def test_defaults_to_slot_zero(self):
        room, camera = _world()
        _run(room, camera, "select_hotbar_slot")
        assert camera.hotbar_index == 0
        assert camera.hotbar_block == DEFAULT_HOTBAR[0]

    def test_absolute_index(self):
        room, camera = _world()
        _run(room, camera, "select_hotbar_slot", index=3)
        assert camera.hotbar_index == 3
        assert camera.hotbar_block == DEFAULT_HOTBAR[3]

    def test_relative_accumulates(self):
        room, camera = _world()
        for _ in range(3):
            _run(room, camera, "select_hotbar_slot", index=1, relative=True)
        assert camera.hotbar_index == 3
        assert camera.hotbar_block == DEFAULT_HOTBAR[3]

    def test_wraps_forward_past_the_end(self):
        room, camera = _world()
        _run(room, camera, "select_hotbar_slot", index=len(DEFAULT_HOTBAR))
        assert camera.hotbar_index == 0

    def test_wraps_backward_past_the_start(self):
        room, camera = _world()
        _run(room, camera, "select_hotbar_slot", index=0)
        _run(room, camera, "select_hotbar_slot", index=-1, relative=True)
        assert camera.hotbar_index == len(DEFAULT_HOTBAR) - 1

    def test_works_without_an_active_block_world_view(self):
        """Only touches the calling instance, not room state -- a menu
        screen can set the starting slot before the 3D view is enabled."""
        room, camera = _world()
        block_world_state(room)["camera"]["enabled"] = False
        _run(room, camera, "select_hotbar_slot", index=2)
        assert camera.hotbar_index == 2

    def test_no_action_executor_does_not_raise(self):
        """GameInstance(..., action_executor=None) does not actually leave
        .action_executor as None (its constructor gives it a real one
        regardless), so a genuinely bare stand-in is the only way to
        construct this case -- same pattern other extension tests use for
        "no executor at all"."""
        class _Bare:
            object_name = "obj_person"
            action_executor = None

        camera = _Bare()
        from extensions.block_world.handlers import PluginExecutor
        PluginExecutor().execute_select_hotbar_slot_action(camera, {"index": 1})
        assert not hasattr(camera, "hotbar_index")


class TestHotbarFeedsPlaceBlock:
    def test_place_block_builds_with_the_selected_slot(self):
        room, camera = _world()
        _run(room, camera, "select_hotbar_slot", index=2)
        _run(room, camera, "place_block", block="hotbar_block")
        assert get_block(room, 1, 0, 0) == DEFAULT_HOTBAR[2]

    def test_changing_the_slot_changes_what_gets_placed_next(self):
        """Two fresh rooms, not two placements from the same camera spot --
        after the first placement the camera is flush against it (matches
        TestPickBlock's own "nowhere to place" case), which would test
        that rule, not the hotbar."""
        room0, camera0 = _world()
        _run(room0, camera0, "select_hotbar_slot", index=0)
        _run(room0, camera0, "place_block", block="hotbar_block")
        assert get_block(room0, 1, 0, 0) == DEFAULT_HOTBAR[0]

        room1, camera1 = _world()
        _run(room1, camera1, "select_hotbar_slot", index=1)
        _run(room1, camera1, "place_block", block="hotbar_block")
        assert get_block(room1, 1, 0, 0) == DEFAULT_HOTBAR[1]

    def test_without_selecting_a_slot_first_place_block_is_a_noop(self):
        """No hotbar_block attribute yet -- _parse_value falls through to
        the literal string "hotbar_block", which is not a real block type,
        so place_block's own validation silently rejects it. A documented
        rough edge (see the handler's docstring), not a crash."""
        room, camera = _world()
        _run(room, camera, "place_block", block="hotbar_block")
        assert get_block(room, 1, 0, 0) is None
