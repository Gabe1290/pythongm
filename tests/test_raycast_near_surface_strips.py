"""A surface at the camera no longer builds a strip millions of rows tall (found 2026-11-23).

The camera walking north at 3 px/frame from y = 232 stops EXACTLY on the grid line y = 160 in
front of a 32 px ledge (too high to climb, taller than the 24 px eye). The ray meets the ledge
front at distance 0 (clamped to 1e-4 px), so one texel spans millions of rows and
_blit_tile_cached scaled every column's strip to ~10.8 million rows: ~190 ms a frame for as long
as the player stood there, in any stairs or ceiling room (raycast_6's gallery is such a ledge).

Now a strip taller than MAX_STRIP_ROWS is drawn one fill per visible texel instead. Normal strips
are far below the limit and keep the old path: an old-vs-new frame diff of raycast_5, raycast_6
and both perf levels (1,284 frames) is identical (commit message).
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

from runtime.game_runner import GameInstance, GameSprite  # noqa: E402
from extensions.raycast_2_5d import renderer  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from test_raycast_view import _room, _solid_instance  # noqa: E402
from test_raycast_stairs_render import _step  # noqa: E402


def _texture():
    spr = GameSprite.__new__(GameSprite)
    frame = pygame.Surface((32, 32))
    for y in range(32):
        pygame.draw.line(frame, (200, (y * 8) % 256, 40), (0, y), (31, y))
    spr.frames = [frame]
    return spr


def _ledge_on_the_line():
    """Camera centre (80, 160), exactly on a grid line, facing north at a 32 px ledge."""
    room = _room(480, 480)
    for g in range(15):
        for (x, y) in ((g, 0), (g, 14), (0, g), (14, g)):
            room.instances.append(_solid_instance("w", x * 32, y * 32))
    for x in range(1, 14):
        room.instances.append(_step(x * 32, 4 * 32, 32))         # row 4: y 128..160
    cam = GameInstance("obj_person", 64, 144, {}, action_executor=None)
    cam._cached_width = cam._cached_height = 32
    cam.facing_angle = 90.0
    room.instances.append(cam)
    room._all_sprites = {"tex": _texture()}
    raycast_state(room)["camera"] = {
        "enabled": True, "camera_object": "obj_person", "fov": 66, "render_distance": 20,
        "cell_size": 32, "columns": 320, "wall_texture": "tex", "wall_height": 3,
        "floor_color": "#00ff00", "ceiling_color": "#0000ff"}
    return room


def test_no_giant_strip_when_the_camera_stands_on_the_line(monkeypatch):
    tallest = []
    real_scale = pygame.transform.scale

    def scale(surface, size):
        tallest.append(size[1])
        if size[1] > 100_000:                 # the old path: record it, don't build gigabytes
            return pygame.Surface((size[0], 1))
        return real_scale(surface, size)

    monkeypatch.setattr(pygame.transform, "scale", scale)
    screen = pygame.Surface((640, 480))
    renderer.render_raycast_view(_ledge_on_the_line(), screen)
    # (At this pose the ledge covers the whole view, so no strip may be scaled at all.)
    assert max(tallest, default=0) <= renderer.MAX_STRIP_ROWS, max(tallest)
    # The ledge front still fills the centre column, textured (no floor / ceiling showing).
    col = {screen.get_at((320, y))[:3] for y in range(0, 480, 8)}
    assert (0, 255, 0) not in col and (0, 0, 255) not in col
    assert all(c[0] > 0 and c[2] == c[2] for c in col)


def _strip(monkeypatch, limit, shade_v):
    monkeypatch.setattr(renderer, "MAX_STRIP_ROWS", limit)
    screen = pygame.Surface((8, 400))
    screen.fill((0, 0, 0))
    frame = _texture().frames[0]
    # A tile 3,000 px tall starting 1,000 px above the screen: ~94 px per texel.
    renderer._blit_tile_cached(screen, {}, frame, 32, 5, 2, 4, -1000.0, 3000.0, 0, 400, shade_v)
    return [screen.get_at((3, y))[:3] for y in range(400)]


def test_the_texel_fill_draws_what_the_scaled_strip_draws(monkeypatch):
    for shade_v in (256, 180):
        scaled = _strip(monkeypatch, 10 ** 9, shade_v)      # old path
        filled = _strip(monkeypatch, 10, shade_v)           # forced fallback
        differing = [y for y in range(400) if scaled[y] != filled[y]]
        # Same texels, same shading; at most a row at each texel boundary may round differently.
        assert len(differing) <= 6, (shade_v, differing[:10])
        assert len(set(filled)) >= 4                        # several texels really drawn
