"""Block World: the visible-window fast path is pixel-identical (2026-11-22).

Standing against a wall, a texel is taller than the screen, and _draw_wall_strip
used to scale its 1px column to the full projected height -- 133,000 px for a
480 px window, 76x the screen's area per frame while walking in block_world_1,
40% of the frame -- only to blit a screen-high slice. _fill_visible_window
paints just that slice with one fill per texel. These tests pin the two facts
it rests on and compare the real function with the fast path on and off.
"""
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402

TEX = ROOT / "extensions" / "block_world" / "textures" / "source_hand_painted_expanded"
OPAQUE = [TEX / "default_brick.png", TEX / "default_stone.png", TEX / "default_dirt.png"]
SEE_THROUGH = [TEX / "default_glass.png", TEX / "default_leaves.png", TEX / "default_water_source_animated.png"]


@pytest.fixture
def screen():
    pygame.init()
    return pygame.display.set_mode((640, 480))


@pytest.mark.parametrize("src_h, dest_h", [(1, 2), (3, 7), (16, 15), (5, 133893), (3, 200000), (16, 48001)])
def test_pygame_scale_maps_row_r_to_r_times_src_over_dest(screen, src_h, dest_h):
    """The fast path's row rule, checked against the real transform.scale."""
    col = pygame.Surface((1, src_h))
    for j in range(src_h):
        col.set_at((0, j), (j, 0, 0))
    out = pygame.transform.scale(col, (2, dest_h))
    rows = range(dest_h) if dest_h < 1000 else random.Random(dest_h).sample(range(dest_h), 500) + [0, dest_h - 1]
    assert all(out.get_at((1, r))[0] == r * src_h // dest_h for r in rows)


def _draw(renderer, screen, fast, args):
    screen.fill((7, 9, 11))
    renderer._WINDOW_FILL_ABOVE = 2 if fast else 10 ** 9
    renderer._draw_wall_strip(screen, *args)
    return pygame.image.tobytes(screen, "RGB")


def _cases(textures, n, seed):
    rnd = random.Random(seed)
    for _ in range(n):
        full_h = rnd.choice([rnd.uniform(1000, 400000), rnd.uniform(960, 3000), rnd.uniform(5, 900)])
        y_top = rnd.uniform(-full_h, 480)
        fog = rnd.choice([0.0, 0.0, rnd.uniform(0.0, 0.9)])
        fog_color = rnd.choice([None, (120, 150, 200)])
        yield (rnd.randint(0, 636), rnd.choice([1, 2, 4]), y_top, full_h, rnd.choice([1.0, rnd.uniform(0.2, 1.0)]),
               str(rnd.choice(textures)), rnd.random(), (90, 90, 90), 480, fog, fog_color, None)


@pytest.mark.parametrize("textures, seed", [(OPAQUE, 1), (OPAQUE, 2), (SEE_THROUGH, 3)])
def test_the_fast_path_draws_exactly_what_scale_and_blit_drew(screen, textures, seed):
    from extensions.block_world import renderer
    saved = renderer._WINDOW_FILL_ABOVE
    try:
        for args in _cases(textures, 600, seed):
            assert _draw(renderer, screen, True, args) == _draw(renderer, screen, False, args), args
    finally:
        renderer._WINDOW_FILL_ABOVE = saved


def test_the_fast_path_really_runs_for_a_wall_in_your_face(screen, monkeypatch):
    """Guard against a vacuous identity proof: a tall opaque strip must take the fill path, not scale."""
    from extensions.block_world import renderer
    scaled = []
    real = pygame.transform.scale
    monkeypatch.setattr(pygame.transform, "scale", lambda s, size, *a: scaled.append(size) or real(s, size, *a))
    renderer._draw_wall_strip(screen, 100, 4, -60000.0, 120000.0, 0.8, str(OPAQUE[0]), 0.3, (90, 90, 90), 480)
    assert not any(h > 960 for _w, h in scaled), scaled
