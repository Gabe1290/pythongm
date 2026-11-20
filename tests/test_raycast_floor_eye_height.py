#!/usr/bin/env python3
"""The floor cast and the wall pass agree on the eye height (stairs plan S1).

docs/RAYCAST_STAIRS_PLAN.md, finding F1: since walls became 1.5x taller
(``RAYCAST_WALL_HEIGHT = 1.5``) the wall pass puts the eye at 0.75 cell, but
the floor/ceiling cast still used 0.5 cell, so the floor under a wall's base
was sampled at 2/3 of the wall's distance -- the floor slid against the wall
bases as you walked, and its tiles did not line up with the grid the walls
stand on. Same formula on desktop, Kivy and HTML5.

These tests check WHERE the floor lands, not that something drew: one screen
row below a wall's base (and one row above its top, for the ceiling), the
cast floor point must lie just short of the wall's own grid line. The texture
encodes its column in the red channel (64 texels per cell), so the sampled
pixel tells us the fractional cell position the cast reached.
"""

import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402

from extensions.raycast_2_5d.renderer import (  # noqa: E402
    cast_floor_plane, RAYCAST_WALL_HEIGHT,
)

W = H = 480
CELL = 32
TEX_W = 64                      # texels per cell, along x
CAM_CX = CAM_CY = 3.5           # camera at a cell centre, facing east (+x)
# Wall lines at x = 6, 7, 9 -> distances 2.5, 3.5, 5.5 cells.
DISTANCES = (2.5, 3.5, 5.5)
FOV = math.radians(66)


def _wall_base_offset(distance_cells, view_h=H):
    """Pixels from the horizon to a wall's base: the wall pass's own formula
    (renderer.render_raycast_view: full_h / 2)."""
    full_h = view_h * CELL * RAYCAST_WALL_HEIGHT / (distance_cells * CELL)
    return full_h / 2.0


def _texel_fraction(red):
    """Fractional cell position encoded by a red value (red = tx * 4)."""
    return (red // 4) / TEX_W


def _assert_just_short_of_line(frac, distance, row_offset, view_h=H):
    """The cast point for the row ``row_offset`` px below the horizon must be
    where the WALL pass would put a floor point on that row: the wall pass
    maps distance D to an offset of base(D) px, so this row is at
    D * base(D) / row_offset cells -- slightly nearer than the wall, i.e. just
    short of its line (fraction near 1). The old 0.5-cell eye cast it at ~2/3
    of that distance instead (fraction ~0.1-0.6)."""
    expected = CAM_CX + distance * _wall_base_offset(distance, view_h) / row_offset
    expected_frac = expected - math.floor(expected)
    assert expected_frac > 0.8          # sanity: the row really is just short
    assert abs(frac - expected_frac) <= 1.5 / TEX_W, (
        f"floor under a wall {distance} cells away was cast at cell fraction "
        f"{frac:.3f}; the wall pass puts that row at {expected_frac:.3f}")


def _encoded_texture_surface():
    surf = pygame.Surface((TEX_W, 1))
    for tx in range(TEX_W):
        surf.set_at((tx, 0), (tx * 4, 0, 0))
    return surf


@pytest.mark.parametrize("distance", DISTANCES)
def test_desktop_floor_meets_wall_base(distance):
    screen = pygame.Surface((W, H))
    cast_floor_plane(screen, _encoded_texture_surface(), CAM_CX, CAM_CY,
                     0.0, FOV, 1, ceiling=False, view_h=H)
    j = math.ceil(_wall_base_offset(distance)) + 1
    red = screen.get_at((W // 2, H // 2 + j))[0]
    _assert_just_short_of_line(_texel_fraction(red), distance, j)


@pytest.mark.parametrize("distance", DISTANCES)
def test_desktop_ceiling_meets_wall_top(distance):
    """The ceiling is the floor cast mirrored, so it must meet the wall tops
    the same way (walls are symmetric about the horizon)."""
    screen = pygame.Surface((W, H))
    cast_floor_plane(screen, _encoded_texture_surface(), CAM_CX, CAM_CY,
                     0.0, FOV, 1, ceiling=True, view_h=H)
    j = math.ceil(_wall_base_offset(distance)) + 1
    red = screen.get_at((W // 2, H // 2 - 1 - j))[0]
    _assert_just_short_of_line(_texel_fraction(red), distance, j)


@pytest.mark.parametrize("distance", DISTANCES)
def test_desktop_letterboxed_floor_meets_wall_base(distance):
    """viewport_height shrinks the projection reference; the agreement must
    hold for the letterboxed view too (raycast_4 uses viewport_height=400)."""
    view_h = 400
    screen = pygame.Surface((W, H))
    cast_floor_plane(screen, _encoded_texture_surface(), CAM_CX, CAM_CY,
                     0.0, FOV, 1, ceiling=False, view_h=view_h)
    j = math.ceil(_wall_base_offset(distance, view_h)) + 1
    red = screen.get_at((W // 2, view_h // 2 + j))[0]
    _assert_just_short_of_line(_texel_fraction(red), distance, j, view_h)


@pytest.mark.parametrize("distance", DISTANCES)
def test_kivy_floor_meets_wall_base(distance):
    from test_kivy_raycast import (
        _stub_kivy_env, _scene_class, _blank_scene, _export_raycast_1,
    )
    exported = _export_raycast_1()
    with _stub_kivy_env(exported):
        scene = _blank_scene(_scene_class(exported))
        scene.display_width, scene.display_height = W, H
        pixels = bytearray(TEX_W * 4)
        for tx in range(TEX_W):
            pixels[tx * 4] = tx * 4
            pixels[tx * 4 + 3] = 255
        buf, sw, sh = scene._floor_buffer(bytes(pixels), TEX_W, 1, 1,
                                          facing_screen_rad=0.0, fov_rad=FOV,
                                          cam_cx=CAM_CX, cam_cy=CAM_CY)
    j = math.ceil(_wall_base_offset(distance)) + 1
    red = buf[(j * sw + W // 2) * 4]
    _assert_just_short_of_line(_texel_fraction(red), distance, j)


def test_html5_uses_the_wall_pass_eye_height():
    """No JS engine in CI: pin the shipped formula (structural, like the rest
    of the HTML5 raycast tests)."""
    js = (REPO_ROOT / "extensions" / "raycast_2_5d" / "export_html5.js").read_text(
        encoding="utf-8")
    assert "const posZ = 0.5 * RAYCAST_WALL_HEIGHT * viewH;" in js
    assert "const posZ = 0.5 * viewH" not in js
