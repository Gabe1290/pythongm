"""`_draw_wall_strip` may shade before or after scaling. It must not matter.

The renderer picks between two orders purely on cost (`_SHADE_AT_SOURCE_ABOVE`):
shade the 1px texture column and then scale it up, or scale first and shade the
finished strip. The second is what it always did; the first is what makes
walking in block_world_1 3.4x faster, because a wall you are standing next to
projects a full-screen-height strip and shading it touches ~74x more pixels
than shading its source column.

That is only a legitimate optimisation if the two orders are *identical*, which
holds exactly while `pygame.transform.scale` is a nearest-neighbour copy: each
destination pixel then takes its value from one source pixel, so a per-pixel
multiply commutes with the resize. `smoothscale` interpolates BETWEEN source
pixels and would not commute at all.

So these tests pin the invariant rather than the implementation: drive the real
function down both branches and compare the pixels it puts on screen.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((1, 1))  # convert_alpha() needs an active video mode

import extensions.block_world.renderer as R  # noqa: E402

RENDERER_SRC = (REPO_ROOT / "extensions" / "block_world" / "renderer.py")


def _texture(tmp_path, w=16, h=16):
    """A texture with no two rows alike, so a shifted or interpolated sample
    cannot coincidentally match the right answer."""
    surf = pygame.Surface((w, h))
    for y in range(h):
        for x in range(w):
            surf.set_at((x, y), ((x * 29 + y * 7) % 256,
                                 (y * 53) % 256,
                                 (x * 101 + y * 3) % 256))
    path = tmp_path / ("tex_%dx%d.png" % (w, h))
    pygame.image.save(surf, str(path))
    return str(path)


def _draw(texture_path, threshold, y_top, full_h, shade, strip_w=2,
          screen_size=(8, 480)):
    """One strip, drawn with the branch `threshold` selects."""
    screen = pygame.Surface(screen_size)
    screen.fill((0, 0, 0))
    original = R._SHADE_AT_SOURCE_ABOVE
    R._SHADE_AT_SOURCE_ABOVE = threshold
    try:
        R._draw_wall_strip(screen, 0, strip_w, y_top, full_h, shade,
                           texture_path, 0.5, (255, 0, 255))
    finally:
        R._SHADE_AT_SOURCE_ABOVE = original
    return pygame.image.tostring(screen, "RGB")


# Heights spanning both regimes: a few pixels (distant block, shading the strip
# is cheaper) up to taller than the screen (a wall in your face, which is the
# case the optimisation exists for).
@pytest.mark.parametrize("full_h", [1, 3, 8, 31, 64, 200, 480, 961, 2000])
@pytest.mark.parametrize("shade", [0.35, 0.5, 0.85, 0.999])
def test_both_shading_orders_draw_the_same_pixels(tmp_path, full_h, shade):
    texture = _texture(tmp_path)
    at_source = _draw(texture, 0, 0.0, full_h, shade)          # always source
    at_strip = _draw(texture, 10 ** 9, 0.0, full_h, shade)     # always strip
    assert at_source == at_strip, (
        "shading before and after the scale disagree at full_h=%s shade=%s"
        % (full_h, shade))


@pytest.mark.parametrize("y_top", [-300.0, -17.5, -0.5, 0.0, 0.25, 120.0,
                                   479.5])
def test_they_agree_for_a_strip_clipped_at_either_edge(tmp_path, y_top):
    """The sub-texel crop and the seam patch both key off y_top, so a strip
    running off the top or bottom of the screen exercises different code than
    a fully visible one."""
    texture = _texture(tmp_path)
    assert (_draw(texture, 0, y_top, 640.0, 0.6)
            == _draw(texture, 10 ** 9, y_top, 640.0, 0.6))


def test_an_unshaded_strip_is_unaffected_by_the_threshold(tmp_path):
    texture = _texture(tmp_path)
    assert (_draw(texture, 0, 0.0, 300.0, 1.0)
            == _draw(texture, 10 ** 9, 0.0, 300.0, 1.0))


def test_shading_the_source_does_not_darken_the_cached_texture(tmp_path):
    """The source column is a subsurface of the CACHED texture surface, so the
    shading copy is load-bearing: without it the first shaded draw would darken
    the texture permanently and every later draw would compound it."""
    texture = _texture(tmp_path)
    first = _draw(texture, 0, 0.0, 480.0, 0.5)
    for _ in range(5):
        _draw(texture, 0, 0.0, 480.0, 0.5)
    assert _draw(texture, 0, 0.0, 480.0, 0.5) == first, (
        "repeated shaded draws drift -- the cached texture is being mutated")


def test_the_renderer_still_uses_nearest_neighbour_scale():
    """The equivalence above holds only for `transform.scale`. If the renderer
    ever moves to `smoothscale` the two orders stop matching and the whole
    optimisation is invalid -- parsed, not grepped, so a mention in a comment
    cannot satisfy it."""
    tree = ast.parse(RENDERER_SRC.read_text(encoding="utf-8"))
    called = {node.func.attr
              for node in ast.walk(tree)
              if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute)}
    assert "scale" in called
    assert "smoothscale" not in called, (
        "smoothscale interpolates between source pixels, so shading the source "
        "column is no longer equivalent -- see this module's docstring")
