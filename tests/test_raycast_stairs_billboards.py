"""Billboards (pickups, monsters, goals) in a room with steps
(docs/RAYCAST_STAIRS_PLAN.md, S7).

A billboard stands on the floor of its own cell, placed relative to it
exactly as on flat ground, and steps nearer than it hide its lower rows.
Rooms without steps are unchanged (the S4 identity proof covers billboards).
The tests read the yellow sprite's rows in the centre column and compare
them with the projection.
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

from runtime.game_runner import GameInstance  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.renderer import (  # noqa: E402
    render_raycast_view, stairs_y, RAYCAST_EYE_HEIGHT,
)
from test_raycast_view import _room, _sprited_instance  # noqa: E402
from test_raycast_stairs_render import _step  # noqa: E402

CELL = 32
H = W = 480
HALF = H / 2
EYE = RAYCAST_EYE_HEIGHT * CELL
YELLOW = (255, 255, 0)
CAM_X = 1                                  # camera in cell (1, 7), facing east
BB_CELL = (7, 7)                           # the billboard's cell
BB_DIST = BB_CELL[0] + 0.5 - (CAM_X + 0.5)  # 6 cells (billboard centred in its cell)


def _render(steps, camera_height=None):
    """steps: {(gx, gy): height}. A step far BEHIND the camera keeps every
    scene in stairs mode, so "no step near" scenes are comparable."""
    room = _room(480, 480)
    all_steps = dict(steps)
    all_steps.setdefault((0, 13), 8.0)
    if camera_height is not None:
        all_steps[(CAM_X, 7)] = camera_height
    for (gx, gy), h in all_steps.items():
        room.instances.append(_step(gx * CELL, gy * CELL, h))
    bb = _sprited_instance("obj_goal", BB_CELL[0] * CELL + 8, BB_CELL[1] * CELL + 8,
                           YELLOW, width=16, height=16)
    room.instances.append(bb)
    cam = GameInstance("obj_person", CAM_X * CELL, 7 * CELL, {}, action_executor=None)
    cam._cached_width = cam._cached_height = 32
    cam.facing_angle = 0.0
    room.instances.append(cam)
    raycast_state(room)["camera"] = {
        "enabled": True, "camera_object": "obj_person", "fov": 66,
        "render_distance": 20, "cell_size": CELL, "columns": 480,
        "wall_color": "#ff0000", "floor_color": "#00ff00",
        "ceiling_color": "#0000ff", "wall_height": 3, "wall_textured": False}
    screen = pygame.Surface((W, H))
    render_raycast_view(room, screen)
    return screen


def _yellow_rows(screen, x=W // 2):
    rows = [y for y in range(H) if screen.get_at((x, y))[:3] == YELLOW]
    assert rows, "billboard not visible"
    return rows[0], rows[-1]


def _ground_rows():
    """Where a 16-px billboard 6 cells away is drawn on flat ground."""
    full = H * 16 / (BB_DIST * CELL)
    return HALF - full / 2, HALF + full / 2


def test_on_flat_ground_it_is_where_it_always_was():
    top, bottom = _yellow_rows(_render({}))
    exp_top, exp_bottom = _ground_rows()
    assert abs(top - exp_top) <= 1.5 and abs(bottom - exp_bottom) <= 1.5


def test_on_a_block_it_is_drawn_higher_by_the_block_s_height():
    """On a 16-px block (lower than the eye, so its front cannot hide it)
    the billboard rises by 16 * view_h / distance."""
    top_g, bottom_g = _yellow_rows(_render({}))
    top_b, bottom_b = _yellow_rows(_render({BB_CELL: 16.0}))
    lift = 16 * H / (BB_DIST * CELL)                  # 40 px
    assert abs((top_g - top_b) - lift) <= 1.5, (top_g, top_b, lift)
    assert abs((bottom_g - bottom_b) - lift) <= 1.5


def test_from_a_raised_eye_a_ground_billboard_is_drawn_lower():
    top_g, _ = _yellow_rows(_render({}))
    top_r, _ = _yellow_rows(_render({}, camera_height=16.0))
    drop = 16 * H / (BB_DIST * CELL)
    assert abs((top_r - top_g) - drop) <= 1.5, (top_g, top_r, drop)


def test_a_step_in_front_hides_its_lower_rows():
    """A 24-px block (eye height) in cell 4: past its far edge (line 5,
    3.5 cells away) the column is free only above y(24) = the horizon. The
    billboard behind it keeps its upper half and loses the rest."""
    _, bottom_free = _yellow_rows(_render({}))
    top, bottom = _yellow_rows(_render({(4, 7): 24.0}))
    limit = stairs_y(24, EYE, 3.5 * CELL, HALF, H)    # == HALF
    assert bottom_free > limit + 10                   # it really reached below
    assert abs(bottom - (limit - 1)) <= 1.0, (bottom, limit)
    assert abs(top - _ground_rows()[0]) <= 1.5        # the top is untouched


def test_a_low_step_in_front_hides_nothing():
    """An 8-px block in front is too low to reach the billboard's rows."""
    assert _yellow_rows(_render({(4, 7): 8.0})) == _yellow_rows(_render({}))


def test_a_billboard_standing_on_its_own_step_is_not_hidden_by_it():
    """Its own step's front is nearer than the billboard, but the billboard
    stands ON that step: nothing of it may be cut."""
    top, bottom = _yellow_rows(_render({BB_CELL: 16.0}))
    full = H * 16 / (BB_DIST * CELL)
    assert abs((bottom - top + 1) - full) <= 2.0


def test_a_step_behind_it_hides_nothing():
    """A 24-px block BEHIND the billboard (cell 9) must not cut it: only
    crossings nearer than the billboard count."""
    assert _yellow_rows(_render({(9, 7): 24.0})) == _yellow_rows(_render({}))
