"""Billboards behind a lintel lose their top rows (ceilings plan, C5).

docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md. A lintel (where a lower ceiling begins) hides the upper rows
of anything standing behind it, exactly as a step hides the lower rows of a billboard behind that:
the column walk's top clip, recorded per crossing (``occluders_top``), limits what a billboard
further away may draw. Same hand-built tunnel room as test_raycast_ceilings_render.py.
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

from extensions.raycast_2_5d.renderer import _clip_top_before  # noqa: E402
from test_raycast_view import _sprited_instance  # noqa: E402
from test_raycast_ceilings_render import (  # noqa: E402
    _marker, _walled_room, TUNNEL_CELLS, _row, TUNNEL,
)
from test_raycast_stairs_render import _render, H  # noqa: E402

MAGENTA = (255, 0, 255)
LINTEL_BOTTOM = int(_row(TUNNEL, 80))        # 144


def _room_with_billboard(markers):
    room, cam = _walled_room(markers)
    # 16 wide, 96 tall, centred in cell (7, 7): d = 160, so it spans rows 96..384.
    room.instances.append(_sprited_instance("obj_goal", 232, 192, MAGENTA, width=16, height=96))
    return room, cam


def _sprite_rows(screen, x=240):
    return [y for y in range(H) if screen.get_at((x, y))[:3] == MAGENTA]


def test_a_lintel_hides_the_top_of_a_billboard_behind_it():
    room, cam = _room_with_billboard([_marker(x, y) for x, y in TUNNEL_CELLS])
    rows = _sprite_rows(_render(room, cam, (2, 7), 0.0))
    assert rows, "billboard not visible"
    assert min(rows) >= LINTEL_BOTTOM - 1            # nothing above the lintel's lower edge
    assert max(rows) > 300                           # the rest of it is there


def test_without_a_lintel_the_whole_billboard_shows():
    room, cam = _room_with_billboard([])
    rows = _sprite_rows(_render(room, cam, (2, 7), 0.0))
    assert min(rows) <= 100


def test_the_lintel_shows_where_the_billboard_would_have_been():
    room, cam = _room_with_billboard([_marker(x, y) for x, y in TUNNEL_CELLS])
    screen = _render(room, cam, (2, 7), 0.0)
    r, g, b = screen.get_at((240, 120))[:3]
    assert r > 0 and g == 0 and b == 0               # wall red (the lintel), not magenta


def test_a_billboard_in_front_of_the_lintel_is_not_clipped():
    # Camera inside the tunnel's mouth side: billboard in cell (3, 7), nearer than the lintel (x = 160).
    room, cam = _walled_room([_marker(x, y) for x, y in TUNNEL_CELLS])
    room.instances.append(_sprited_instance("obj_goal", 104 - 8, 192, MAGENTA, width=16, height=96))
    rows = _sprite_rows(_render(room, cam, (1, 7), 0.0))
    assert rows and min(rows) < LINTEL_BOTTOM - 20


def test_clip_top_before_picks_the_last_crossing_nearer_than_the_billboard():
    occ = [(50.0, 10.0), (100.0, 140.0), (200.0, 150.0)]
    assert _clip_top_before(occ, 40.0) == 0
    assert _clip_top_before(occ, 60.0) == 10
    assert _clip_top_before(occ, 150.0) == 140
    assert _clip_top_before([], 150.0) == 0
