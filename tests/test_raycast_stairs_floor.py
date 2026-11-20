"""Textured step tops: the column-major floor cast of a room with steps
(docs/RAYCAST_STAIRS_PLAN.md, S6).

In a room with steps every low-res floor pixel is cast at the height of the
tread it belongs to: distance = (eye - h) * view_h / (y - horizon). These
tests check WHERE the floor lands (an x-encoded texture tells which point of
the grid a pixel sampled), that a step's own top texture is used, and that
no low-res block is ever left unpainted.
"""
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime.game_runner import GameSprite  # noqa: E402
from extensions.raycast_2_5d import renderer  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.renderer import (  # noqa: E402
    render_raycast_view, stairs_y, RAYCAST_EYE_HEIGHT,
)
from test_raycast_stairs_render import _stairs_room  # noqa: E402

CELL = 32
H = W = 480
HALF = H // 2
EYE = RAYCAST_EYE_HEIGHT * CELL
TEX_W = 64


def _sprite(frame):
    spr = GameSprite.__new__(GameSprite)
    spr.frames = [frame]
    return spr


def _x_encoded(channel):
    """64x1 texture: texel x is readable from one colour channel (x * 4)."""
    frame = pygame.Surface((TEX_W, 1))
    for tx in range(TEX_W):
        rgb = [0, 0, 0]
        rgb[channel] = tx * 4
        frame.set_at((tx, 0), tuple(rgb))
    return _sprite(frame)


def _solid(color):
    frame = pygame.Surface((32, 32))
    frame.fill(color)
    return _sprite(frame)


def _render(room, cam, cell_xy, angle, **extra):
    cam.x, cam.y = cell_xy[0] * CELL, cell_xy[1] * CELL
    cam.facing_angle = angle
    cfg = {"enabled": True, "camera_object": "obj_person", "fov": 66,
           "render_distance": 20, "cell_size": CELL, "columns": 480,
           "wall_color": "#ff0000", "floor_color": "#ff00ff",
           "ceiling_color": "#0000ff", "wall_height": 3, "wall_textured": False,
           "floor_cast_res": 1}
    cfg.update(extra)
    raycast_state(room)["camera"] = cfg
    screen = pygame.Surface((W, H))
    render_raycast_view(room, screen)
    return screen


def _expected_fraction(row, height, eye=EYE, cam_cx=2.5):
    """The grid x a floor pixel at `row` (centre column, facing east) should
    sample, for a tread at `height`: the inverse of the wall projection."""
    dist_cells = ((eye - height) / CELL) * H / (row - HALF)
    x = cam_cx + dist_cells
    return x - math.floor(x)


def _fraction(screen, row, channel=0):
    return (screen.get_at((W // 2, row))[channel] // 4) / TEX_W


class TestWhereTheFloorLands:
    """Facing the staircase from cell 2: the first riser (0 -> 8 px) stands
    on grid line x = 5, 2.5 cells away."""

    def _scene(self):
        room, cam = _stairs_room()
        room._all_sprites = {"spr_x": _x_encoded(0)}
        return room, cam

    def test_just_below_a_riser_the_ground_is_at_the_riser_s_line(self):
        room, cam = self._scene()
        screen = _render(room, cam, (2, 7), 0.0, floor_texture="spr_x")
        bottom = stairs_y(0, EYE, 2.5 * CELL, HALF, H)
        row = math.floor(bottom + 0.5) + 1
        expected = _expected_fraction(row, 0)
        assert expected > 0.85                        # just short of line 5
        assert abs(_fraction(screen, row) - expected) <= 1.5 / TEX_W

    def test_just_above_a_riser_the_step_top_starts_at_the_same_line(self):
        """The tread of the 8-px step, cast at height 8, meets its riser
        exactly: just above the riser's top it samples just PAST line 5."""
        room, cam = self._scene()
        screen = _render(room, cam, (2, 7), 0.0, floor_texture="spr_x")
        top = stairs_y(8, EYE, 2.5 * CELL, HALF, H)
        row = math.floor(top + 0.5) - 2
        expected = _expected_fraction(row, 8)
        assert expected < 0.15                        # just past line 5
        assert abs(_fraction(screen, row) - expected) <= 1.5 / TEX_W
        # cast at height 0 instead, the same row would land far beyond
        assert abs(_expected_fraction(row, 0) - expected) > 0.1

    def test_standing_on_the_platform_the_ground_beyond_uses_the_raised_eye(self):
        """From the 32-px platform (cell 10) facing west, the ground beyond the
        staircase is cast from an eye 32 px higher."""
        room, cam = self._scene()
        screen = _render(room, cam, (10, 7), 180.0, floor_texture="spr_x")
        eye = 32 + EYE
        # the wall face on line x = 1 is 9.5 cells away; just below its base:
        base = stairs_y(0, eye, 9.5 * CELL, HALF, H)
        row = math.floor(base + 0.5) + 1
        dist_cells = ((eye - 0) / CELL) * H / (row - HALF)
        x = 10.5 - dist_cells                          # facing west
        expected = x - math.floor(x)
        frac = _fraction(screen, row)
        # facing west the texture's x still grows eastward
        assert abs(frac - expected) <= 1.5 / TEX_W, (frac, expected)


class TestStepTopTextures:
    def test_a_step_s_own_top_texture_is_used_and_only_on_its_cells(self):
        room, cam = _stairs_room()
        room._all_sprites = {"spr_floor": _solid((90, 90, 90)),
                             "spr_top": _solid((0, 200, 0))}
        for inst in room.instances:
            if getattr(inst, "raycast_floor_height", None) == 8.0:
                inst.raycast_step_top_texture = "spr_top"
        screen = _render(room, cam, (2, 7), 0.0, floor_texture="spr_floor")
        # the 8-px tread lies between the first riser's top and the second's bottom
        tread8 = (stairs_y(8, EYE, 2.5 * CELL, HALF, H)
                  + stairs_y(8, EYE, 3.5 * CELL, HALF, H)) / 2
        tread16 = (stairs_y(16, EYE, 3.5 * CELL, HALF, H)
                   + stairs_y(16, EYE, 4.5 * CELL, HALF, H)) / 2
        assert screen.get_at((W // 2, int(tread8)))[:3] == (0, 200, 0)
        assert screen.get_at((W // 2, int(tread16)))[:3] == (90, 90, 90)
        assert screen.get_at((W // 2, H - 3))[:3] == (90, 90, 90)      # the ground

    def test_top_texture_alone_triggers_the_cast(self):
        """No floor texture: the ground stays the flat colour, the textured
        step tops are still cast."""
        room, cam = _stairs_room()
        room._all_sprites = {"spr_top": _solid((0, 200, 0))}
        for inst in room.instances:
            if getattr(inst, "raycast_floor_height", None) == 8.0:
                inst.raycast_step_top_texture = "spr_top"
        screen = _render(room, cam, (2, 7), 0.0)
        tread8 = (stairs_y(8, EYE, 2.5 * CELL, HALF, H)
                  + stairs_y(8, EYE, 3.5 * CELL, HALF, H)) / 2
        assert screen.get_at((W // 2, int(tread8)))[:3] == (0, 200, 0)
        assert screen.get_at((W // 2, H - 3))[:3] == (255, 0, 255)


class TestNoGaps:
    @pytest.mark.parametrize("pose", [((2, 7), 0.0), ((4, 7), 10.0), ((10, 7), 160.0),
                                      ((7, 6), 90.0), ((12, 3), 225.0), ((3, 12), 300.0)])
    @pytest.mark.parametrize("res", [1, 4])
    def test_every_floor_pixel_is_painted(self, pose, res):
        """The flat floor colour (magenta) must never show through when the
        floor is textured (solid cyan): a block the cast skipped would."""
        room, cam = _stairs_room()
        room._all_sprites = {"spr_floor": _solid((0, 255, 255))}
        screen = _render(room, cam, pose[0], pose[1], floor_texture="spr_floor",
                         floor_cast_res=res)
        leaks = [(x, y) for x in range(0, W, 3) for y in range(HALF, H)
                 if screen.get_at((x, y))[:3] == (255, 0, 255)]
        assert not leaks, leaks[:10]


def test_flat_rooms_do_not_cast(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("floor cast without any floor texture")
    monkeypatch.setattr(renderer, "cast_stairs_floor", boom)
    room, cam = _stairs_room()
    screen = _render(room, cam, (2, 7), 0.0)
    tread8 = (stairs_y(8, EYE, 2.5 * CELL, HALF, H)
              + stairs_y(8, EYE, 3.5 * CELL, HALF, H)) / 2
    assert screen.get_at((W // 2, int(tread8)))[:3] == (255, 0, 255)
