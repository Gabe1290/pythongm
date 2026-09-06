"""Distance fog, and the haze that hides where the world runs out.

The point of fog here is not decoration. Beyond the render distance nothing is
drawn and the flat floor colour shows through, which looked like a dark brown
void with a floating island of terrain on it -- and that made the single
biggest performance dial this renderer has (the render distance itself)
unusable. Fading geometry into the sky, and the floor into the same colour
where the world ends, is what buys the speed. See
docs/BLOCK_WORLD_PERF_PLAN.md.

So the tests that matter are: the void is gone, near geometry is untouched,
and `fog: False` still gives exactly the old picture.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((1, 1))

from runtime.game_runner import GameRoom, GameInstance  # noqa: E402
from extensions.block_world.state import (  # noqa: E402
    block_world_state, set_block)
from extensions.block_world.renderer import (  # noqa: E402
    render_block_world_view, fog_amount, fog_mix, fog_add_for,
    FOG_CURVE, FOG_SKIP_BELOW, FOG_OPAQUE_ABOVE, FOG_ADD_STEPS)

W, H, CELL = 320, 240, 32
FLOOR = "#3a2f1c"
SKY = "#87CEEB"


def _room():
    return GameRoom("fog", {"width": 32 * CELL, "height": 32 * CELL},
                    action_executor=None)


def _camera(room, x=48.0, y=48.0, facing=0.0):
    inst = GameInstance("obj_person", x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = inst._cached_height = CELL
    inst.facing_angle = facing
    room.instances.append(inst)
    return inst


def _configure(room, **overrides):
    cfg = block_world_state(room)["camera"]
    cfg.update({
        "enabled": True, "camera_object": "obj_person", "cell_size": CELL,
        "z_layer": 0, "fov": 66, "render_distance": 8, "columns": 40,
        "wall_textured": False, "wall_color": "#ff0000",
        "floor_color": FLOOR, "ceiling_color": SKY, "eye_height": 1.5,
    })
    cfg.update(overrides)
    return cfg


def _render(room):
    screen = pygame.Surface((W, H))
    render_block_world_view(room, screen)
    return screen


class TestFogCurve:
    def test_it_is_zero_at_the_camera_and_one_at_the_render_distance(self):
        """Reaching exactly 1.0 at max_dist is what makes the edge of the
        world invisible -- anything less leaves a visible step there."""
        assert fog_amount(0.0, 100.0) == 0.0
        assert fog_amount(100.0, 100.0) == 1.0
        assert fog_amount(200.0, 100.0) == 1.0

    def test_it_is_weighted_toward_the_far_distance(self):
        """Squared, so the near and middle distance stay clear and the haze
        gathers where the geometry is about to run out."""
        assert fog_amount(50.0, 100.0) == pytest.approx(0.5 ** FOG_CURVE)
        assert fog_amount(50.0, 100.0) < 0.5

    def test_a_zero_render_distance_does_not_divide_by_zero(self):
        assert fog_amount(10.0, 0.0) == 0.0

    def test_mixing_by_zero_returns_the_original_colour_object(self):
        base = (10, 20, 30)
        assert fog_mix(base, 0.0, (255, 255, 255)) is base

    def test_mixing_by_one_reaches_the_fog_colour(self):
        assert fog_mix((10, 20, 30), 1.0, (200, 100, 50)) == (200, 100, 50)


class TestFogAddCache:
    def test_the_same_quantised_fog_reuses_one_tuple(self):
        """It is built per strip otherwise -- ~9,000 times a frame -- and
        building it inline cost more than the Surface op it feeds."""
        cache = {}
        a = fog_add_for(0.5, (200, 100, 50), cache)
        b = fog_add_for(0.5 + 0.5 / FOG_ADD_STEPS / 4, (200, 100, 50), cache)
        assert a is b
        assert len(cache) == 1

    def test_it_scales_the_fog_colour(self):
        assert fog_add_for(1.0, (200, 100, 50), {}) == (200, 100, 50)
        assert fog_add_for(0.5, (200, 100, 50), {}) == (100, 50, 25)


class TestTheVoidIsGone:
    """The bug fog exists to fix."""

    def _row_colours(self, screen, x=W // 2):
        return [screen.get_at((x, y))[:3] for y in range(H)]

    def test_the_ground_beyond_the_render_distance_is_not_raw_floor_colour(self):
        room = _room()
        _camera(room)
        _configure(room)
        floor = tuple(room.parse_color(FLOOR))
        screen = _render(room)
        horizon = H // 2
        # Between the horizon and where the ground plane reaches the render
        # distance there is, by construction, nothing to draw. That band used
        # to be raw floor colour.
        band = [screen.get_at((W // 2, y))[:3]
                for y in range(horizon + 1, horizon + 12)]
        assert floor not in band, (
            "the ground beyond the render distance is still the flat floor "
            "colour -- the void fog exists to hide")

    def test_that_band_is_the_fog_colour(self):
        room = _room()
        _camera(room)
        _configure(room)
        sky = tuple(room.parse_color(SKY))
        screen = _render(room)
        assert screen.get_at((W // 2, H // 2 + 4))[:3] == sky

    def test_the_floor_still_shows_under_the_players_feet(self):
        """The haze is tight to the horizon; the ground you stand on keeps its
        own colour, or the whole picture washes out."""
        room = _room()
        _camera(room)
        _configure(room)
        screen = _render(room)
        assert screen.get_at((W // 2, H - 2))[:3] == tuple(room.parse_color(FLOOR))

    def test_a_shorter_render_distance_hazes_more_of_the_screen(self):
        """The band that needs covering GROWS as the render distance shrinks,
        which is why its extent is derived from that distance rather than
        being a fixed fraction of the floor."""
        def haze_rows(distance):
            room = _room()
            _camera(room)
            _configure(room, render_distance=distance)
            sky = tuple(room.parse_color(SKY))
            screen = _render(room)
            return sum(1 for y in range(H // 2, H)
                       if screen.get_at((W // 2, y))[:3] == sky)

        assert haze_rows(4) > haze_rows(16)


class TestFogOff:
    def test_it_restores_the_flat_background_exactly(self):
        room = _room()
        _camera(room)
        _configure(room, fog=False)
        screen = _render(room)
        assert screen.get_at((W // 2, H // 2 + 4))[:3] == \
            tuple(room.parse_color(FLOOR))

    def _block_pixel(self, render_distance, fog):
        """A pixel that is definitely ON the block, found rather than guessed:
        the first row below the horizon that is neither sky nor floor.

        The block goes at (4, 2), which is two cells directly ahead: the ray
        starts at the camera's sprite CENTRE, so an instance placed at (48, 48)
        with a 32px sprite is casting from (64, 64) -- cell (2, 2), not the
        (1, 1) its top-left corner sits in. A block placed by the corner's cell
        row is simply never hit, and the render comes back empty with no error.
        """
        room = _room()
        _camera(room)
        _configure(room, fog=fog, render_distance=render_distance)
        set_block(room, 4, 2, 0, "cobble")
        screen = _render(room)
        # Found by the wall's own colour, not by "differs from the
        # background": the haze is a gradient between the floor and the sky,
        # so anything looking for a non-background pixel finds the haze first
        # and measures that instead.
        for y in range(H // 2 + 1, H):
            r, g, b = screen.get_at((W // 2, y))[:3]
            if r > g + 40 and r > b + 40:
                return y, (r, g, b)
        raise AssertionError("the block was not drawn at all")

    def test_geometry_under_the_skip_threshold_is_pixel_identical(self):
        """Fog below FOG_SKIP_BELOW is not worth a Surface op -- it is under a
        pixel of shift on an 8-bit channel -- so it is skipped entirely, and a
        block close to the camera comes out byte-for-byte as before."""
        # 2 cells away against 20: t = (2/20)^2 = 0.01, under the skip.
        y_on, lit = self._block_pixel(20, True)
        y_off, plain = self._block_pixel(20, False)
        assert y_on == y_off
        assert lit == plain

    def test_mid_distance_geometry_is_only_slightly_tinted(self):
        """It does tint further out -- that is the point -- but the curve has
        to stay gentle there or every existing project's colours shift."""
        _, lit = self._block_pixel(5, True)
        _, plain = self._block_pixel(5, False)
        assert lit != plain
        # (2/5)^2 is 16% of the way to the sky -- visible, not a wash-out.
        assert max(abs(a - b) for a, b in zip(lit, plain)) < 80
