"""Lowered ceilings drawn on desktop: the two-clip column walk (ceilings plan, C3).

docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md. A room with Set Ceiling Height markers takes the column
walk with a second clip from the top: the lowered ceiling is drawn at its own height, a LINTEL
(wall texture) shows where a lower ceiling begins, and walls rise only to the ceiling of the
cell in front of them. Rooms without markers draw exactly as before -- proven separately by an
old-vs-new frame diff (C3 commit message); here, the new picture is checked against the same
projection the renderer uses.

Flat colours, 480 x 480 view, walls 3 cells high (96 px), eye 24 px above the floor:
row(z, d) = 240 + (24 - z) * 480 / d.
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

from runtime.game_runner import GameInstance  # noqa: E402
from extensions.raycast_2_5d.renderer import (  # noqa: E402
    build_raycast_walls, cast_ray_steps, layout_column_ceilings, stairs_y,
)
from test_raycast_view import _room, _solid_instance  # noqa: E402
from test_raycast_stairs_render import _render, _kind, CELL, H, EYE  # noqa: E402

TUNNEL = 40.0
ROOM_TOP = 96.0


def _marker(gx, gy, height=TUNNEL):
    inst = GameInstance("obj_low", gx * CELL, gy * CELL, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = inst._cached_height = 32
    inst.raycast_ceiling_height = float(height)
    inst.raycast_ceiling_texture = ""
    return inst


def _walled_room(markers=()):
    room = _room(480, 480)
    for g in range(15):
        for (x, y) in ((g, 0), (g, 14), (0, g), (14, g)):
            room.instances.append(_solid_instance("w", x * CELL, y * CELL))
    room.instances.extend(markers)
    cam = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    cam._cached_width = cam._cached_height = 32
    room.instances.append(cam)
    return room, cam


def _centre_column(screen):
    return [_kind(screen.get_at((240, y))) for y in range(H)]


def _row(z, d):
    return 240 + (EYE - z) * 480 / d


# Tunnel over cells x = 5..8, rows 6..8; camera centre (80, 240), facing east.
TUNNEL_CELLS = [(x, y) for x in range(5, 9) for y in range(6, 9)]


class TestLookingIntoATunnel:
    def setup_method(self):
        room, cam = _walled_room([_marker(x, y) for x, y in TUNNEL_CELLS])
        self.col = _centre_column(_render(room, cam, (2, 7), 0.0))
        plain_room, plain_cam = _walled_room()
        self.plain = _centre_column(_render(plain_room, plain_cam, (2, 7), 0.0))
        # Entering the tunnel at x = 160 (d = 80), leaving it at x = 288 (d = 208).
        self.lintel_bottom = _row(TUNNEL, 80)          # 144
        self.tunnel_end = _row(TUNNEL, 208)            # ~203

    def test_the_lintel_hangs_where_the_room_ceiling_was(self):
        assert self.plain[50] == "ceiling"
        assert self.col[50] == "wall"                  # the lintel, wall-coloured
        assert self.col[int(self.lintel_bottom) - 2] == "wall"

    def test_the_tunnel_ceiling_is_drawn_at_its_own_height(self):
        assert self.plain[170] == "wall"               # the far wall, without a tunnel
        for y in range(int(self.lintel_bottom) + 2, int(self.tunnel_end) - 1):
            assert self.col[y] == "ceiling", y

    def test_beyond_the_tunnel_the_far_wall_shows_below_its_lip(self):
        # The ceiling rises again at the exit: that face looks away (no lintel);
        # the far wall shows from the tunnel's lip down.
        assert self.col[int(self.tunnel_end) + 3] == "wall"

    def test_the_floor_is_untouched(self):
        assert self.col[H - 5] == self.plain[H - 5] == "floor"


def test_a_wall_rises_only_to_the_ceiling_in_front_of_it():
    # Inside a tunnel (x = 10..13) that runs into the east wall (x = 448).
    low = [(x, y) for x in range(10, 14) for y in range(6, 9)]
    room, cam = _walled_room([_marker(x, y) for x, y in low])
    col = _centre_column(_render(room, cam, (11, 7), 0.0))
    plain_room, plain_cam = _walled_room()
    plain = _centre_column(_render(plain_room, plain_cam, (11, 7), 0.0))
    top = _row(TUNNEL, 448 - (11 * CELL + 16))       # d = 80 -> row 144
    assert plain[100] == "wall"                       # full-height wall without the tunnel
    assert col[100] == "ceiling"                      # tunnel ceiling above the wall's top
    assert col[int(top) + 3] == "wall"


def test_a_ceiling_only_room_takes_the_column_walk():
    """No step in the room, only a ceiling marker: still drawn (the walk runs)."""
    room, cam = _walled_room([_marker(x, y) for x, y in TUNNEL_CELLS])
    assert _centre_column(_render(room, cam, (2, 7), 0.0))[50] == "wall"


class TestTheWalk:
    def _crossings(self, ceilings):
        room, _cam = _walled_room()
        build_raycast_walls(room, CELL)
        return cast_ray_steps(room, 80.0, 240.0, 0.0, CELL, 20, {}, ceilings)

    def test_without_a_ceiling_map_the_stairs_crossings_are_unchanged(self):
        room, _cam = _walled_room()
        build_raycast_walls(room, CELL)
        steps = {(6, 7): 8.0}
        assert (cast_ray_steps(room, 80.0, 240.0, 0.0, CELL, 20, steps)
                == cast_ray_steps(room, 80.0, 240.0, 0.0, CELL, 20, steps, None))

    def test_a_ceiling_change_alone_is_a_crossing(self):
        crossings, hit = self._crossings({(5, 7): TUNNEL, (6, 7): TUNNEL})
        assert [(round(c[0], 6), c[1], c[4], c[5]) for c in crossings] == [
            (2.5, 0.0, (5, 7), TUNNEL), (4.5, 0.0, (7, 7), None)]
        assert hit[2] is True

    def test_layout_spans_never_overlap(self):
        crossings, hit = self._crossings({(5, 7): TUNNEL, (6, 7): 64.0})
        lay = layout_column_ceilings(crossings, hit, 0.0, None, EYE, ROOM_TOP, CELL,
                                     1.0, 240, 480, 20)
        spans = ([(a, b) for a, b, *_ in lay["ceilings"]]
                 + [(a, b) for a, b, *_ in lay["lintels"]]
                 + [(a, b) for a, b, *_ in lay["treads"]]
                 + [(a, b) for a, b, *_ in lay["risers"]]
                 + ([lay["wall"][:2]] if lay["wall"] else []))
        spans = sorted((max(a, 0.0), min(b, 480.0)) for a, b in spans if b > a)
        for (a0, b0), (a1, b1) in zip(spans, spans[1:]):
            assert b0 <= a1 + 1e-9, (spans,)
        # A lower ceiling ahead (40 after 64) is a lintel; the rise back to the room is not.
        assert [round(l[6]) for l in lay["lintels"]] == [40]
        assert stairs_y(TUNNEL, EYE, 80.0, 240, 480) == lay["lintels"][0][1]
