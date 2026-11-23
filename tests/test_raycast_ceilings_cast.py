"""Lowered ceilings are cast textured (ceilings plan, C4).

docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md. A lowered ceiling span is cast column-major at its OWN
height, like the stairs plan's floor: the cell's own ceiling texture, else the camera's, else the
flat ceiling colour. Spans at the room ceiling are untouched (the room's own flat / sky / plane
pass drew them), so a sky stays visible wherever the ceiling is open.

Same hand-built rooms and projection as test_raycast_ceilings_render.py: 480 x 480 view, walls 3
cells high (96 px), eye 24 px above the floor, a tunnel (ceiling 40 px) over cells x = 5..8,
y = 6..8, the camera in cell (2, 7) facing east.
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

from runtime.game_runner import GameSprite  # noqa: E402
from test_raycast_ceilings_render import (  # noqa: E402
    _marker, _walled_room, TUNNEL_CELLS, _row, TUNNEL,
)
from test_raycast_stairs_render import _render, CEIL_RGB, H  # noqa: E402

A, B = (200, 100, 50), (30, 220, 140)
LINTEL_BOTTOM = _row(TUNNEL, 80)          # 144: where the tunnel ceiling starts
TUNNEL_END = _row(TUNNEL, 208)            # ~203: where it ends


def _tex(color, color2=None):
    """A 32 x 32 texture: one colour, or two halves (top / bottom, i.e. across the view)."""
    spr = GameSprite.__new__(GameSprite)
    frame = pygame.Surface((32, 32))
    frame.fill(color)
    if color2 is not None:
        frame.fill(color2, (0, 16, 32, 16))
    spr.frames = [frame]
    return spr


def _tunnel_room(sprites, marker_textures=None):
    markers = []
    for x, y in TUNNEL_CELLS:
        m = _marker(x, y)
        if marker_textures:
            m.raycast_ceiling_texture = marker_textures.get((x, y), "")
        markers.append(m)
    room, cam = _walled_room(markers)
    room._all_sprites = sprites
    return room, cam


def _rgb(screen, x, y):
    c = screen.get_at((x, y))
    return (c[0], c[1], c[2])


def _tunnel_rows():
    return range(int(LINTEL_BOTTOM) + 6, int(TUNNEL_END) - 6)


def test_the_camera_ceiling_texture_covers_a_lowered_ceiling():
    room, cam = _tunnel_room({"c": _tex(A)})
    screen = _render(room, cam, (2, 7), 0.0, ceiling_texture="c")
    for y in _tunnel_rows():
        assert _rgb(screen, 240, y) == A, y


def test_a_cell_texture_wins_over_the_camera_texture():
    room, cam = _tunnel_room({"c": _tex(A), "p": _tex(B)},
                             {cell: "p" for cell in TUNNEL_CELLS})
    screen = _render(room, cam, (2, 7), 0.0, ceiling_texture="c")
    for y in _tunnel_rows():
        assert _rgb(screen, 240, y) == B, y


def test_a_cell_texture_alone_is_enough_and_cells_without_one_fall_back():
    # Only cells x >= 7 carry their own texture; the camera has none: the near
    # part of the tunnel (x = 5, 6) stays the flat ceiling colour.
    room, cam = _tunnel_room({"p": _tex(B)},
                             {(x, y): "p" for x, y in TUNNEL_CELLS if x >= 7})
    screen = _render(room, cam, (2, 7), 0.0)
    near_row = int(_row(TUNNEL, 120))             # inside cell x = 5..6 (d = 112..144)
    far_row = int(_row(TUNNEL, 190))              # inside cell x = 7..8 (d = 176..208)
    assert _rgb(screen, 240, near_row) == CEIL_RGB
    assert _rgb(screen, 240, far_row) == B


def test_the_texture_is_sampled_not_flat():
    room, cam = _tunnel_room({"c": _tex(A, B)})
    screen = _render(room, cam, (2, 7), 0.0, ceiling_texture="c")
    seen = {_rgb(screen, x, 175) for x in range(120, 360)}
    assert seen == {A, B}


def test_without_any_texture_the_span_stays_the_flat_ceiling_colour():
    room, cam = _tunnel_room({})
    screen = _render(room, cam, (2, 7), 0.0)
    for y in _tunnel_rows():
        assert _rgb(screen, 240, y) == CEIL_RGB, y


def test_the_lintel_and_the_far_wall_are_drawn_over_the_cast():
    room, cam = _tunnel_room({"c": _tex(A)})
    screen = _render(room, cam, (2, 7), 0.0, ceiling_texture="c")
    assert _rgb(screen, 240, 50)[0] > 0 and _rgb(screen, 240, 50)[1:] == (0, 0)   # lintel: wall red
    assert _rgb(screen, 240, int(TUNNEL_END) + 4)[0] > 0                           # far wall below the lip


def test_a_lowered_ceiling_roofs_over_a_sky_and_the_open_ceiling_keeps_it():
    sky = _tex((10, 20, 250))
    room, cam = _tunnel_room({"sky": sky})
    screen = _render(room, cam, (2, 7), 0.0, sky_texture="sky")
    for y in _tunnel_rows():                       # the tunnel is a roof, not sky
        assert _rgb(screen, 240, y) == CEIL_RGB, y
    plain_room, plain_cam = _walled_room()
    plain_room._all_sprites = {"sky": sky}
    plain = _render(plain_room, plain_cam, (2, 7), 0.0, sky_texture="sky")
    assert _rgb(plain, 240, 50) == (10, 20, 250)   # where the ceiling is open, the sky shows


def test_a_cast_under_a_sky_uses_the_camera_texture():
    room, cam = _tunnel_room({"sky": _tex((10, 20, 250)), "c": _tex(A)})
    screen = _render(room, cam, (2, 7), 0.0, sky_texture="sky", ceiling_texture="c")
    for y in _tunnel_rows():
        assert _rgb(screen, 240, y) == A, y
    assert 0 <= int(LINTEL_BOTTOM) < H
