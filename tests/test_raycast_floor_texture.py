"""set_floor_texture: per-area floor textures at ground level (2026-11-23).

A floor patch is an ordinary non-solid object whose Create event runs ``set_floor_texture``;
the ground cells its sprite covers are cast with that sprite instead of the camera's floor
texture. Checked here on desktop, in a flat room and in a room with steps (the column walk),
plus the map's rules and that a patch is neither a billboard nor a mover.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime.game_runner import GameInstance, GameSprite  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.heights import (  # noqa: E402
    build_floor_textures, is_floor_patch, is_geometry,
)
from extensions.raycast_2_5d.renderer import render_raycast_view  # noqa: E402
from extensions.raycast_2_5d import climbing  # noqa: E402
from test_raycast_view import _room, _raycast_executor, _dispatch, _sprited_instance  # noqa: E402
from events.action_types import get_action_type  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402

load_all_plugins()

CELL = 32
PATCH = (255, 0, 255)
FLOOR = (0, 128, 0)
FLAT = (0, 255, 0)


def _sprite(color, size=16):
    spr = GameSprite.__new__(GameSprite)
    frame = pygame.Surface((size, size))
    frame.fill(color)
    spr.frames = [frame]
    spr.get_frame = lambda i=0, f=frame: f
    return spr


def _patch(x, y, texture="spr_rug", w=96, h=32, solid=False, name="obj_rug"):
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": solid}
    inst._cached_width = w
    inst._cached_height = h
    inst.raycast_floor_texture = texture
    return inst


def _step(x, y, height=8.0):
    inst = GameInstance("obj_step", x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = 32
    inst._cached_height = 32
    inst.raycast_floor_height = height
    inst.raycast_step_top_texture = ""
    inst.raycast_step_side_texture = ""
    return inst


def _render(instances, floor_texture="spr_floor"):
    """Camera in cell (0,0) facing east; returns the screen."""
    room = _room(320, 320)
    room._all_sprites = {"spr_rug": _sprite(PATCH), "spr_floor": _sprite(FLOOR)}
    room.instances.extend(instances)
    camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    camera._cached_width = camera._cached_height = 32   # rays start at (16, 16)
    camera.facing_angle = 0.0
    room.instances.append(camera)
    raycast_state(room)["camera"] = {
        'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
        'render_distance': 20, 'cell_size': CELL, 'columns': 64,
        'wall_color': '#ff0000', 'floor_color': '#00ff00', 'ceiling_color': '#0000ff',
        'floor_texture': floor_texture,
    }
    screen = pygame.Surface((320, 240))
    render_raycast_view(room, screen)
    return screen


# The centre column, 80 px below the horizon, looks at the floor ~2.25 cells east of the
# camera: cell (2, 0), inside a patch at x=64..160, y=0..32.
AHEAD = (160, 200)
# 10 px below the horizon: ~18 cells away, far past the patch.
FAR = (160, 130)


class TestSchema:
    def test_registered_in_3d_view(self):
        at = get_action_type("set_floor_texture")
        assert at is not None and at.category == "3D View"
        (p,) = at.parameters
        assert p.name == "texture" and p.param_type == "sprite"
        # Label shared with enable_raycast_view, so every language already has it.
        assert p.display_name == "Floor Texture"

    def test_the_handler_records_the_sprite_name(self):
        ex = _raycast_executor()
        inst = GameInstance("obj_rug", 0, 0, {}, action_executor=None)
        _dispatch(ex, "set_floor_texture", inst, {"texture": "spr_rug"})
        assert inst.raycast_floor_texture == "spr_rug"
        _dispatch(ex, "set_floor_texture", inst, {"texture": None})
        assert inst.raycast_floor_texture == ""


class TestMap:
    def _map(self, instances):
        room = _room(320, 320)
        room.instances.extend(instances)
        return build_floor_textures(room, CELL)

    def test_covers_every_cell_of_the_sprite_box(self):
        assert self._map([_patch(64, 0)]) == {(2, 0): "spr_rug", (3, 0): "spr_rug",
                                               (4, 0): "spr_rug"}

    def test_later_patch_wins_where_they_overlap(self):
        m = self._map([_patch(64, 0), _patch(96, 0, texture="spr_tile", w=32)])
        assert m[(3, 0)] == "spr_tile" and m[(2, 0)] == "spr_rug"

    def test_blank_and_solid_are_ignored(self):
        assert self._map([_patch(64, 0, texture=""), _patch(0, 64, solid=True)]) == {}

    def test_follows_a_moved_patch(self):
        room = _room(320, 320)
        p = _patch(64, 0, w=32)
        room.instances.append(p)
        assert build_floor_textures(room, CELL) == {(2, 0): "spr_rug"}
        p.x = 128
        assert build_floor_textures(room, CELL) == {(4, 0): "spr_rug"}


class TestGeometry:
    def test_a_patch_is_geometry_never_a_mover(self):
        p = _patch(64, 0)
        assert is_floor_patch(p) and is_geometry(p)
        assert not is_floor_patch(GameInstance("obj_x", 0, 0, {}, action_executor=None))
        assert climbing._is_mover(p) is False

    def test_a_patch_is_not_drawn_as_a_billboard(self):
        rug = _sprited_instance("obj_rug", 96, 16, (255, 255, 0))
        assert any(_render([rug]).get_at((x, 120))[:3] == (255, 255, 0) for x in range(320))
        rug.raycast_floor_texture = "spr_rug"
        assert not any(_render([rug]).get_at((x, 120))[:3] == (255, 255, 0)
                       for x in range(320))


class TestDrawn:
    def test_flat_room_patch_replaces_the_floor_texture(self):
        assert _render([]).get_at(AHEAD)[:3] == FLOOR
        screen = _render([_patch(64, 0)])
        assert screen.get_at(AHEAD)[:3] == PATCH
        assert screen.get_at(FAR)[:3] == FLOOR

    def test_flat_room_without_floor_texture_uses_the_floor_colour_around(self):
        screen = _render([_patch(64, 0)], floor_texture="")
        assert screen.get_at(AHEAD)[:3] == PATCH
        assert screen.get_at(FAR)[:3] == FLAT

    def test_room_with_steps_patch_is_drawn_on_the_ground(self):
        step = _step(0, 128)          # a step elsewhere switches to the column walk
        assert _render([step]).get_at(AHEAD)[:3] == FLOOR
        screen = _render([step, _patch(64, 0)])
        assert screen.get_at(AHEAD)[:3] == PATCH
        assert screen.get_at(FAR)[:3] == FLOOR

    def test_room_with_steps_without_floor_texture(self):
        screen = _render([_step(0, 128), _patch(64, 0)], floor_texture="")
        assert screen.get_at(AHEAD)[:3] == PATCH

    def test_a_step_on_a_patched_cell_keeps_the_step_top(self):
        # The step covers the patch's cell (2, 0): raised cells use the step's own top
        # (blank = the floor texture), never the ground patch under it.
        screen = _render([_patch(64, 0, w=32), _step(64, 0, height=8.0)])
        assert screen.get_at(AHEAD)[:3] != PATCH

    def test_a_patch_with_an_unknown_sprite_changes_nothing(self):
        before = pygame.image.tobytes(_render([]), "RGB")
        after = pygame.image.tobytes(_render([_patch(64, 0, texture="spr_missing")]), "RGB")
        assert before == after
