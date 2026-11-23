"""The view under a low ceiling (ceilings plan, C6).

docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md. Every mover gets ``raycast_ceiling_z`` beside
``raycast_floor_z``, and the camera's eased view height never rises above the ceiling over it:
walking off a ledge into a low tunnel drops the view to the tunnel's roof (minus the margin)
at once, then it eases down as usual. There is no movement refusal for a low ceiling: every cell's
ceiling is clamped to at least floor + eye + margin when the map is built, so every cell can be
stood in (tests/test_raycast_ceiling_heights.py).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.raycast_2_5d.climbing import after_collision, before_step  # noqa: E402
from extensions.raycast_2_5d.heights import CEILING_MARGIN, RAYCAST_EYE_HEIGHT  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from test_raycast_view import _room  # noqa: E402
from test_raycast_stairs_render import _step  # noqa: E402
from test_raycast_ceilings_render import _marker  # noqa: E402
from test_raycast_climbing import (  # noqa: E402
    _Runner, _mover, _move, _write_project, _run, _person, CELL,
)

load_all_plugins()

EYE = RAYCAST_EYE_HEIGHT * CELL           # 24 px
ROOM_TOP = 96.0                           # wall_height 3 x 32


def _scene(steps=None, low=None, low_height=40.0):
    """steps {(gx, gy): h}, lowered cells [(gx, gy)], the camera in cell (2, 7)."""
    room = _room(480, 480)
    for (gx, gy), h in (steps or {}).items():
        room.instances.append(_step(gx * CELL, gy * CELL, h))
    for gx, gy in (low or ()):
        room.instances.append(_marker(gx, gy, low_height))
    cam = _mover("obj_person", 2 * CELL, 7 * CELL)
    room.instances.append(cam)
    raycast_state(room)["camera"] = {"enabled": True, "camera_object": "obj_person",
                                     "cell_size": CELL, "wall_height": 3}
    return _Runner(room), room, cam


def test_a_mover_reads_the_ceiling_over_it():
    runner, _, cam = _scene(low=[(3, 7)])
    _move(runner, cam, 0, 0)
    assert cam.raycast_ceiling_z == ROOM_TOP            # no lowered ceiling here
    _move(runner, cam, 16, 0)                           # centre moves into cell 3
    assert cam.raycast_ceiling_z == 40.0


def test_a_monster_reads_it_too():
    runner, room, _ = _scene(low=[(5, 5)])
    monster = _mover("obj_monster", 5 * CELL, 5 * CELL)
    room.instances.append(monster)
    _move(runner, monster, 0, 0)
    assert monster.raycast_ceiling_z == 40.0


def test_the_view_drops_into_a_tunnel_instead_of_passing_through_its_roof():
    runner, room, cam = _scene(steps={(2, 7): 32.0}, low=[(3, 7)])
    st = raycast_state(room)
    _move(runner, cam, 0, 0)
    assert st["eye_floor"] == 32.0                      # standing on the ledge
    _move(runner, cam, 16, 0)                           # off the ledge, under the roof
    assert st["eye_floor"] + EYE <= 40.0 - CEILING_MARGIN        # eye <= 36 at once
    seen = [st["eye_floor"]]
    for _ in range(20):
        _move(runner, cam, 0, 0)
        seen.append(st["eye_floor"])
    assert all(e + EYE <= 40.0 - CEILING_MARGIN + 1e-9 for e in seen)
    assert seen[-1] == 0.0                              # then it eases down to the floor


def test_a_high_ceiling_changes_nothing():
    runner, room, cam = _scene(steps={(2, 7): 32.0})
    st = raycast_state(room)
    _move(runner, cam, 0, 0)
    _move(runner, cam, 16, 0)
    assert st["eye_floor"] > 30.0                       # still falling slowly from 32


def test_a_low_ceiling_never_blocks_walking():
    # The map clamps the ceiling to floor + eye + margin, so even a request for 0 is passable.
    runner, _, cam = _scene(low=[(3, 7)], low_height=0.0)
    _move(runner, cam, 16, 0)
    assert cam.x == 2 * CELL + 16 and cam.raycast_step_blocked == 0
    assert cam.raycast_ceiling_z == EYE + CEILING_MARGIN


def test_nothing_happens_without_an_enabled_camera():
    runner, room, cam = _scene(low=[(3, 7)])
    raycast_state(room)["camera"]["enabled"] = False
    _move(runner, cam, 16, 0)
    assert not hasattr(cam, "raycast_ceiling_z")


def test_through_the_real_loop_walking_off_a_platform_into_a_tunnel(tmp_path):
    marker = {"name": "obj_low", "asset_type": "object", "sprite": "spr_block",
              "visible": True, "solid": False, "persistent": False, "depth": 0,
              "events": {"create": {"actions": [
                  {"action": "set_ceiling_height", "parameters": {"height": "40"}}]}}}
    platform = {(x, 7): 32.0 for x in range(2, 5)}                  # x = 2..4, 32 px high
    tunnel = [{"object_name": "obj_low", "x": x * CELL, "y": 7 * CELL} for x in range(5, 11)]
    eyes = []
    runner = _run(_write_project(tmp_path, platform, {"obj_low": marker}, tunnel, person_x=2 * CELL),
                  90, on_frame=lambda r, f: eyes.append(
                      (raycast_state(r.current_room).get("eye_floor"), _person(r).x)))
    person = _person(runner)
    assert person.x > 6 * CELL                                      # walked into the tunnel
    assert person.raycast_ceiling_z == 40.0
    inside = [e for e, x in eyes if e is not None and x + 16 >= 5 * CELL]
    assert inside and all(e + EYE <= 40.0 - CEILING_MARGIN + 1e-9 for e in inside)
