"""The minimap shows raised floor cells (docs/RAYCAST_STAIRS_PLAN.md, S9).

build_minimap_commands draws each raised cell as a filled square under the
wall lines, shaded from the panel colour toward the wall colour by height.
A room without steps gets exactly the command list it always did.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

from extensions.raycast_2_5d.hud import build_minimap_commands, blend_hex  # noqa: E402
from extensions.raycast_2_5d.heights import build_floor_heights  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402

BACK, WALL = "#000000", "#c8c8c8"


def _cmds(raised=None, **extra):
    args = dict(v_walls={(1, 0), (3, 2)}, h_walls={(0, 1)}, cell_size=32,
                room_width=320, room_height=320, cam_x=48, cam_y=48,
                facing_angle=0.0, x=10, y=20, size=100, back_color=BACK,
                wall_color=WALL, player_color="#ffd040")
    args.update(extra)
    return build_minimap_commands(raised=raised, **args)


def test_no_raised_cells_changes_nothing():
    assert _cmds(None) == _cmds({}) == build_minimap_commands(
        v_walls={(1, 0), (3, 2)}, h_walls={(0, 1)}, cell_size=32, room_width=320,
        room_height=320, cam_x=48, cam_y=48, facing_angle=0.0, x=10, y=20,
        size=100, back_color=BACK, wall_color=WALL, player_color="#ffd040")


def test_raised_cells_are_filled_squares_on_their_cells_under_the_walls():
    cmds = _cmds({(2, 3): 8.0, (4, 3): 32.0})
    rects = cmds[1:3]                                  # right after the panel
    assert all(c["type"] == "rectangle" and c["filled"] for c in rects)
    assert cmds[3]["type"] == "line"                   # the walls come after
    scale = 100 / 320
    low = rects[0]                                     # sorted: (2, 3) first
    assert (low["x1"], low["y1"]) == pytest.approx((10 + 64 * scale, 20 + 96 * scale))
    assert (low["x2"], low["y2"]) == pytest.approx((10 + 96 * scale, 20 + 128 * scale))


def test_higher_cells_are_shaded_closer_to_the_wall_colour():
    cmds = _cmds({(2, 3): 8.0, (4, 3): 32.0})
    low, high = cmds[1]["color"], cmds[2]["color"]
    # 8 of 32 -> 25% + 0.25*50% = 37.5%; 32 of 32 -> 75%
    assert low == blend_hex(BACK, WALL, 0.375) == "#4b4b4b"
    assert high == blend_hex(BACK, WALL, 0.75) == "#969696"


def test_blend_hex():
    assert blend_hex("#000", "#ffffff", 0.5) == "#808080"
    assert blend_hex("#102030", "#102030", 0.3) == "#102030"
    assert blend_hex("black", "#ffffff", 0.5) == "#ffffff"   # cannot blend a name


def test_the_action_maps_the_room_s_steps():
    """Through the real draw_minimap handler: the heights the renderer and
    the climbing rule keep in the room's state appear on the map."""
    from runtime.game_runner import GameInstance
    from test_raycast_view import _room, _raycast_executor, _dispatch
    from test_raycast_stairs_render import _step

    room = _room(320, 320)
    room.instances.append(_step(64, 96, 8.0))
    cam = GameInstance("obj_person", 32, 32, {}, action_executor=None)
    cam._cached_width = cam._cached_height = 32
    room.instances.append(cam)
    st = raycast_state(room)
    st["camera"] = {"enabled": True, "camera_object": "obj_person", "cell_size": 32}
    st["v_walls"], st["h_walls"], st["cell_size"] = set(), set(), 32
    build_floor_heights(room, 32, 1000)

    class _Runner:
        current_room = room
        global_variables = {}

    hud = GameInstance("obj_hud", 0, 0, {}, action_executor=None)
    _dispatch(_raycast_executor(game_runner=_Runner()), "draw_minimap", hud,
              {"x": 0, "y": 0, "size": 100, "back_color": BACK, "wall_color": WALL})
    rects = [c for c in hud._draw_queue
             if c.get("type") == "rectangle" and c.get("filled")
             and c.get("color") not in (BACK,)]
    scale = 100 / 320
    assert any(c["x1"] == pytest.approx(64 * scale) and c["y1"] == pytest.approx(96 * scale)
               for c in rects), rects
