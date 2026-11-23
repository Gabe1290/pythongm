"""set_ceiling_height + the per-cell ceiling map (docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, C1).

The mirror of set_floor_height (tests/test_raycast_floor_heights.py): a ceiling marker is an
ordinary non-solid object whose Create event runs ``set_ceiling_height``; the cells its sprite
covers get a lower ceiling. This unit adds the action, the map, the clamping, and keeps markers
out of the billboard pass and out of the climbing rule's movers. Nothing is drawn at a lowered
ceiling yet -- that is C3.
"""
import logging
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime.game_runner import GameInstance  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.heights import (  # noqa: E402
    build_ceiling_heights, is_ceiling, is_geometry, is_step, CEILING_MARGIN,
)
from extensions.raycast_2_5d import climbing  # noqa: E402
from test_raycast_view import (  # noqa: E402
    _room, _raycast_executor, _dispatch, _sprited_instance,
)
from test_raycast_floor_heights import _render_with  # noqa: E402
from events.action_types import get_action_type  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402

load_all_plugins()

CELL = 32
EYE = 24.0           # 0.75 cell
ROOM_CEILING = 96.0  # wall_height 3


def _marker(x, y, height, w=32, h=32, texture="", solid=False, name="obj_low"):
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": solid}
    inst._cached_width = w
    inst._cached_height = h
    inst.raycast_ceiling_height = float(height)
    inst.raycast_ceiling_texture = texture
    return inst


def _map(instances, floors=None):
    room = _room(320, 320)
    room.instances.extend(instances)
    return build_ceiling_heights(room, CELL, ROOM_CEILING, floors or {}, EYE), room


# ------------------------------------------------------------------ the action

class TestSchema:
    def test_registered_in_3d_view_with_its_parameters(self):
        at = get_action_type("set_ceiling_height")
        assert at is not None and at.category == "3D View"
        params = {p.name: p for p in at.parameters}
        assert set(params) == {"height", "texture"}
        assert params["height"].param_type == "number"
        assert params["height"].default_value == 40
        assert params["texture"].param_type == "sprite"
        assert params["texture"].required is False
        # Labels shared with existing actions, so every language already has them.
        assert params["height"].display_name == "Height"
        assert params["texture"].display_name == "Ceiling Texture"

    def test_manifest_declares_it(self):
        manifest = json.loads((REPO_ROOT / "extensions" / "raycast_2_5d"
                               / "extension.json").read_text(encoding="utf-8"))
        assert "set_ceiling_height" in manifest["provides_actions"]


class TestHandler:
    def _run(self, params):
        inst = GameInstance("obj_low", 0, 0, {}, action_executor=None)
        _dispatch(_raycast_executor(), "set_ceiling_height", inst, params)
        return inst

    def test_records_height_and_texture_on_the_instance(self):
        inst = self._run({"height": "48", "texture": "spr_low"})
        assert inst.raycast_ceiling_height == 48.0
        assert inst.raycast_ceiling_texture == "spr_low"
        assert is_ceiling(inst) and is_geometry(inst) and not is_step(inst)

    def test_height_is_an_expression(self):
        assert self._run({"height": "16 * 3"}).raycast_ceiling_height == 48.0

    def test_blank_texture_and_garbage_height(self):
        inst = self._run({"height": "not a number"})
        assert inst.raycast_ceiling_height == 0.0
        assert inst.raycast_ceiling_texture == ""

    def test_an_ordinary_instance_is_not_a_ceiling(self):
        inst = GameInstance("obj_goal", 0, 0, {}, action_executor=None)
        assert not is_ceiling(inst) and not is_geometry(inst)


# -------------------------------------------------------------- the ceiling map

class TestCeilingMap:
    def test_a_marker_lowers_its_own_cell(self):
        (ceilings, textures), room = _map([_marker(64, 32, 48, texture="spr_low")])
        assert ceilings == {(2, 1): 48.0}
        assert textures == {(2, 1): "spr_low"}
        assert raycast_state(room)["ceiling_heights"] is ceilings

    def test_a_wide_sprite_lowers_every_cell_it_covers(self):
        (ceilings, _), _ = _map([_marker(0, 0, 48, w=96)])
        assert set(ceilings) == {(0, 0), (1, 0), (2, 0)}

    def test_overlap_lowest_wins_with_its_texture(self):
        (ceilings, textures), _ = _map([_marker(0, 0, 64, texture="a"),
                                        _marker(0, 0, 40, texture="b")])
        assert ceilings == {(0, 0): 40.0} and textures == {(0, 0): "b"}

    def test_at_or_above_the_room_ceiling_changes_nothing(self):
        (ceilings, _), _ = _map([_marker(0, 0, ROOM_CEILING), _marker(32, 0, 500)])
        assert ceilings == {}

    def test_solid_instances_are_walls_never_ceilings(self):
        (ceilings, _), _ = _map([_marker(0, 0, 48, solid=True)])
        assert ceilings == {}

    def test_rebuilt_from_the_live_instances(self):
        marker = _marker(0, 0, 48)
        room = _room(320, 320)
        room.instances.append(marker)
        assert build_ceiling_heights(room, CELL, ROOM_CEILING, {}, EYE)[0] == {(0, 0): 48.0}
        room.instances.remove(marker)
        assert build_ceiling_heights(room, CELL, ROOM_CEILING, {}, EYE)[0] == {}


class TestClamping:
    def test_never_below_the_eye_plus_the_margin(self, caplog):
        with caplog.at_level(logging.WARNING):
            (ceilings, _), room = _map([_marker(0, 0, 10)])
            build_ceiling_heights(room, CELL, ROOM_CEILING, {}, EYE)      # a second frame
        assert ceilings == {(0, 0): EYE + CEILING_MARGIN}
        warnings = [r for r in caplog.records if "set_ceiling_height" in r.getMessage()]
        assert len(warnings) == 1, "warned once per instance, not once per frame"

    def test_the_lowest_legal_ceiling_follows_a_raised_floor(self):
        # A ceiling over a 32 px step must leave room to stand ON the step.
        (ceilings, _), _ = _map([_marker(0, 0, 40, w=64)], floors={(1, 0): 32.0})
        assert ceilings[(0, 0)] == 40.0
        assert ceilings[(1, 0)] == 32.0 + EYE + CEILING_MARGIN

    def test_a_legal_height_is_not_warned(self, caplog):
        with caplog.at_level(logging.WARNING):
            _map([_marker(0, 0, 48)])
        assert not [r for r in caplog.records if "set_ceiling_height" in r.getMessage()]


# ------------------------------------------- markers are level geometry, not things

class TestMarkersAreNotBillboards:
    def test_control_the_same_sprite_without_the_action_is_a_billboard(self):
        assert _render_with([_sprited_instance("obj_goal", 96, 16, (255, 255, 0))])

    def test_a_ceiling_marker_is_not_drawn_as_a_cutout(self):
        marker = _sprited_instance("obj_low", 96, 16, (255, 255, 0))
        marker.raycast_ceiling_height = 40.0
        assert not _render_with([marker])


def test_a_ceiling_marker_is_not_a_mover():
    marker = _marker(0, 0, 48)
    assert not climbing._is_mover(marker)
    assert climbing._is_mover(GameInstance("obj_monster", 0, 0, {}, action_executor=None))
