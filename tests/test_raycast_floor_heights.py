"""set_floor_height + the floor-height map (raycast stairs, S3).

docs/RAYCAST_STAIRS_PLAN.md: a step is an ordinary non-solid object whose
Create event runs ``set_floor_height``; the cells its sprite covers become
raised floor. This unit adds the action, the per-cell map the renderer (S5)
and the climbing rule (S8) will both read, and keeps steps out of the
billboard pass. Nothing is drawn as a step yet -- that is S5.
"""
import logging
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime.game_runner import GameInstance  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.heights import (  # noqa: E402
    build_floor_heights, is_step, max_floor_height, CEILING_MARGIN,
)
from extensions.raycast_2_5d.renderer import render_raycast_view  # noqa: E402
from test_raycast_view import (  # noqa: E402
    _room, _raycast_executor, _dispatch, _sprited_instance, _solid_instance,
)
from events.action_types import get_action_type  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402

load_all_plugins()

CELL = 32
HIGH = 1000.0          # a max_height that never clamps


def _step(x, y, height, w=32, h=32, top="", side="", name="obj_step"):
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = w
    inst._cached_height = h
    inst.raycast_floor_height = float(height)
    inst.raycast_step_top_texture = top
    inst.raycast_step_side_texture = side
    return inst


# --------------------------------------------------------------- the action

class TestSchema:
    def test_registered_in_3d_view_with_its_parameters(self):
        at = get_action_type("set_floor_height")
        assert at is not None and at.category == "3D View"
        params = {p.name: p for p in at.parameters}
        assert set(params) == {"height", "top_texture", "side_texture"}
        assert params["height"].param_type == "number"
        assert params["height"].default_value == 8
        for name in ("top_texture", "side_texture"):
            assert params[name].param_type == "sprite"
            assert params[name].required is False

    def test_manifest_declares_it(self):
        manifest = json.loads((REPO_ROOT / "extensions" / "raycast_2_5d"
                               / "extension.json").read_text(encoding="utf-8"))
        assert "set_floor_height" in manifest["provides_actions"]


class TestHandler:
    def _run(self, params):
        inst = GameInstance("obj_step", 0, 0, {}, action_executor=None)
        _dispatch(_raycast_executor(), "set_floor_height", inst, params)
        return inst

    def test_records_height_and_textures_on_the_instance(self):
        inst = self._run({"height": "16", "top_texture": "spr_top",
                          "side_texture": "spr_side"})
        assert inst.raycast_floor_height == 16.0
        assert inst.raycast_step_top_texture == "spr_top"
        assert inst.raycast_step_side_texture == "spr_side"
        assert is_step(inst)

    def test_height_is_an_expression(self):
        inst = self._run({"height": "8 * 3"})
        assert inst.raycast_floor_height == 24.0

    def test_blank_textures_and_garbage_height(self):
        inst = self._run({"height": "not a number"})
        assert inst.raycast_floor_height == 0.0
        assert inst.raycast_step_top_texture == ""
        assert inst.raycast_step_side_texture == ""

    def test_an_ordinary_instance_is_not_a_step(self):
        assert not is_step(GameInstance("obj_goal", 0, 0, {}, action_executor=None))


# ----------------------------------------------------------- the height map

class TestFloorHeightMap:
    def test_a_step_raises_its_own_cell(self):
        room = _room(256, 256)
        room.instances.append(_step(64, 96, 8, top="t", side="s"))
        heights, textures = build_floor_heights(room, CELL, HIGH)
        assert heights == {(2, 3): 8.0}
        assert textures == {(2, 3): ("t", "s")}
        st = raycast_state(room)
        assert st["floor_heights"] is heights and st["floor_textures"] is textures

    def test_a_wide_sprite_raises_every_cell_it_covers(self):
        room = _room(256, 256)
        room.instances.append(_step(32, 32, 16, w=64, h=32))
        heights, _ = build_floor_heights(room, CELL, HIGH)
        assert heights == {(1, 1): 16.0, (2, 1): 16.0}

    def test_a_box_ending_on_a_grid_line_stays_in_its_cells(self):
        """A 32x32 step at (32, 32) must not leak into column 2 or row 2."""
        room = _room(256, 256)
        room.instances.append(_step(32, 32, 8))
        heights, _ = build_floor_heights(room, CELL, HIGH)
        assert list(heights) == [(1, 1)]

    def test_off_grid_step_covers_the_cells_it_overlaps(self):
        room = _room(256, 256)
        room.instances.append(_step(40, 40, 8))      # straddles 4 cells
        heights, _ = build_floor_heights(room, CELL, HIGH)
        assert set(heights) == {(1, 1), (2, 1), (1, 2), (2, 2)}

    def test_the_sprite_origin_is_respected(self):
        """Origin-aware like all raycast geometry: a centred 32x32 sprite at
        (48, 48) occupies cell (1, 1), not (1..2, 1..2)."""
        room = _room(256, 256)
        step = _step(48, 48, 8)
        step.sprite = type("Spr", (), {"origin_x": 16, "origin_y": 16})()
        room.instances.append(step)
        heights, _ = build_floor_heights(room, CELL, HIGH)
        assert list(heights) == [(1, 1)]

    def test_overlap_highest_wins_with_its_textures(self):
        room = _room(256, 256)
        room.instances.append(_step(0, 0, 24, top="high", side="high_s"))
        room.instances.append(_step(0, 0, 8, top="low", side="low_s"))
        heights, textures = build_floor_heights(room, CELL, HIGH)
        assert heights[(0, 0)] == 24.0
        assert textures[(0, 0)] == ("high", "high_s")

    def test_ground_level_steps_add_no_raised_cell(self):
        room = _room(256, 256)
        room.instances.append(_step(0, 0, 0))
        heights, _ = build_floor_heights(room, CELL, HIGH)
        assert heights == {}

    def test_solid_instances_are_walls_never_steps(self):
        room = _room(256, 256)
        wall = _solid_instance("obj_wall", 0, 0)
        wall.raycast_floor_height = 16.0
        room.instances.append(wall)
        heights, _ = build_floor_heights(room, CELL, HIGH)
        assert heights == {}

    def test_rebuilt_from_the_live_instances(self):
        """A step destroyed (or created) at runtime is reflected at once."""
        room = _room(256, 256)
        step = _step(0, 0, 8)
        room.instances.append(step)
        assert build_floor_heights(room, CELL, HIGH)[0] == {(0, 0): 8.0}
        room.instances.remove(step)
        assert build_floor_heights(room, CELL, HIGH)[0] == {}
        room.instances.append(_step(64, 0, 16))
        assert build_floor_heights(room, CELL, HIGH)[0] == {(2, 0): 16.0}


class TestClamping:
    def test_max_floor_height_keeps_the_eye_below_the_ceiling(self):
        # wall_height 3 cells, eye 0.75 cell, cell 32: 96 - 24 - margin
        assert max_floor_height(32, 3.0, 0.75) == 72.0 - CEILING_MARGIN
        # today's default walls (1.5): only 24 px of headroom
        assert max_floor_height(32, 1.5, 0.75) == 24.0 - CEILING_MARGIN
        assert max_floor_height(32, 0.5, 0.75) == 0.0

    def test_too_high_is_clamped_and_warned_once(self, caplog):
        room = _room(256, 256)
        room.instances.append(_step(0, 0, 500, name="obj_tower"))
        with caplog.at_level(logging.WARNING, logger="extensions.raycast_2_5d.heights"):
            for _ in range(5):                       # five frames
                heights, _ = build_floor_heights(room, CELL, 68.0)
        assert heights == {(0, 0): 68.0}
        warnings = [r for r in caplog.records if "obj_tower" in r.getMessage()]
        assert len(warnings) == 1, [r.getMessage() for r in caplog.records]

    def test_negative_is_clamped_to_the_ground(self, caplog):
        room = _room(256, 256)
        room.instances.append(_step(0, 0, -16, name="obj_pit"))
        with caplog.at_level(logging.WARNING, logger="extensions.raycast_2_5d.heights"):
            heights, _ = build_floor_heights(room, CELL, HIGH)
        assert heights == {}
        assert any("obj_pit" in r.getMessage() for r in caplog.records)


# ------------------------------------------------- steps are not billboards

def _render_with(instances):
    room = _room(160, 160)
    room.instances.extend(instances)
    camera = GameInstance("obj_person", 16, 16, {}, action_executor=None)
    camera.facing_angle = 0.0
    room.instances.append(camera)
    raycast_state(room)["camera"] = {
        'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
        'render_distance': 20, 'cell_size': 32, 'columns': 64,
        'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
    }
    screen = pygame.Surface((320, 240))
    render_raycast_view(room, screen)
    w, h = screen.get_size()
    return any(screen.get_at((x, h // 2))[:3] == (255, 255, 0) for x in range(w))


class TestStepsAreNotBillboards:
    def test_control_the_same_sprite_without_the_action_is_a_billboard(self):
        assert _render_with([_sprited_instance("obj_goal", 96, 16, (255, 255, 0))])

    def test_a_step_is_not_drawn_as_a_cutout(self):
        step = _sprited_instance("obj_step", 96, 16, (255, 255, 0))
        step.raycast_floor_height = 8.0
        assert not _render_with([step])
