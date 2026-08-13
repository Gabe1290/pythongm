"""Regression tests for Block World Phase 2b -- stacked layers.

Where tests/test_block_world_renderer.py pins 2a's single-layer behaviour,
these pin what 2b adds: the whole vertical stack at each cell, an eye height
that can sit above or below a block, horizontal (top/bottom) faces, the
painter-ordered march, and the derived per-column index the renderer reads.

Geometry tests use ``columns: 1``. One column means camera_x is exactly 0,
so ray_offset is 0, the ray runs exactly along facing_angle and the fisheye
correction is exactly 1.0 -- the projection then has a closed form the test
can assert against directly, instead of sampling whichever column happens to
land nearest the centre.
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

import pygame
pygame.init()
pygame.display.set_mode((1, 1))  # convert_alpha() needs an active video mode

from runtime.game_runner import GameRoom, GameInstance  # noqa: E402
from extensions.block_world.state import (  # noqa: E402
    block_world_state, set_block, remove_block, load_block_list,
    column_index, stack_top,
)
from extensions.block_world.renderer import (  # noqa: E402
    march_ray, render_block_world_view, _fully_covers, _occupied,
)

CELL = 32
W, H = 320, 240
HORIZON = H / 2
FLOOR = "#3a2f1c"
CEILING = "#87CEEB"


def _room():
    return GameRoom("layers", {"width": 32 * CELL, "height": 32 * CELL},
                    action_executor=None)


def _camera(room, cell_x=0, cell_y=0, facing=0.0):
    inst = GameInstance("obj_person", cell_x * CELL, cell_y * CELL, {},
                        action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = inst._cached_height = CELL
    inst.facing_angle = facing
    room.instances.append(inst)
    return inst


def _configure(room, **overrides):
    cfg = block_world_state(room)["camera"]
    cfg.update({
        "enabled": True, "camera_object": "obj_person", "cell_size": CELL,
        "z_layer": 0, "fov": 66, "render_distance": 20, "columns": 1,
        "wall_textured": False, "wall_color": "#ff0000",
        "floor_color": FLOOR, "ceiling_color": CEILING,
    })
    cfg.update(overrides)
    return cfg


def _render(room):
    screen = pygame.Surface((W, H))
    render_block_world_view(room, screen)
    return screen


def _drawn_span(room, screen, x=W // 2):
    """(top_y, bottom_y) of the drawn (non floor/ceiling) run in a column,
    or None if the column shows only background."""
    floor_rgb = tuple(room.parse_color(FLOOR))
    ceil_rgb = tuple(room.parse_color(CEILING))
    ys = [y for y in range(H)
          if screen.get_at((x, y))[:3] not in (floor_rgb, ceil_rgb)]
    return (ys[0], ys[-1]) if ys else None


def _px_per_cell(dist_cells):
    """The projection scale at a distance, straight from the renderer's
    documented formula: screen_h * cell_size / distance_in_pixels."""
    return H * CELL / (dist_cells * CELL)


def _project(eye_z, zval, dist_cells):
    return HORIZON + (eye_z - zval) * _px_per_cell(dist_cells)


# ---------------------------------------------------------------------------
# march_ray
# ---------------------------------------------------------------------------

class TestMarchRay:
    def test_yields_cells_in_order_along_positive_x(self):
        room = _room()
        cells = [(mx, my) for mx, my, *_ in
                 march_ray(room, 16, 16, 0.0, CELL, 4)]
        assert cells == [(1, 0), (2, 0), (3, 0), (4, 0)]

    def test_exit_of_one_cell_is_the_entry_of_the_next(self):
        """The march must tile the ray with no gap or overlap -- a top face
        is drawn between a cell's own entry and exit, so a discontinuity here
        would show as a crack between adjacent cells' horizontal faces."""
        room = _room()
        steps = list(march_ray(room, 16, 16, 0.7, CELL, 8))
        for (_x, _y, _entry, exit_d, _s, _u), nxt in zip(steps, steps[1:]):
            assert exit_d == pytest.approx(nxt[2], abs=1e-9)

    def test_entry_is_always_nearer_than_exit(self):
        room = _room()
        for _x, _y, entry, exit_d, _s, _u in march_ray(room, 16, 16, 1.1, CELL, 8):
            assert entry < exit_d

    def test_entry_distances_match_a_known_geometry(self):
        room = _room()
        steps = list(march_ray(room, 16, 16, 0.0, CELL, 3))
        # From grid x=0.5, cell 1 starts at x=1 (0.5 cells), cell 2 at 1.5...
        assert [s[2] for s in steps] == pytest.approx([16.0, 48.0, 80.0])

    def test_respects_max_cells(self):
        room = _room()
        assert len(list(march_ray(room, 16, 16, 0.0, CELL, 5))) == 5


# ---------------------------------------------------------------------------
# the derived per-column index
# ---------------------------------------------------------------------------

class TestColumnIndex:
    def test_groups_a_stack_lowest_first(self):
        room = _room()
        set_block(room, 2, 3, 2, "stone")
        set_block(room, 2, 3, 0, "dirt")
        set_block(room, 2, 3, 1, "cobble")
        assert column_index(room)[(2, 3)] == [
            (0, "dirt"), (1, "cobble"), (2, "stone")]

    def test_separate_columns_stay_separate(self):
        room = _room()
        set_block(room, 0, 0, 0, "dirt")
        set_block(room, 5, 5, 0, "stone")
        index = column_index(room)
        assert index[(0, 0)] == [(0, "dirt")]
        assert index[(5, 5)] == [(0, "stone")]

    def test_is_cached_between_calls(self):
        room = _room()
        set_block(room, 1, 1, 0, "dirt")
        assert column_index(room) is column_index(room)

    def test_set_block_invalidates(self):
        room = _room()
        set_block(room, 1, 1, 0, "dirt")
        column_index(room)
        set_block(room, 1, 1, 1, "stone")
        assert column_index(room)[(1, 1)] == [(0, "dirt"), (1, "stone")]

    def test_remove_block_invalidates(self):
        room = _room()
        set_block(room, 1, 1, 0, "dirt")
        set_block(room, 1, 1, 1, "stone")
        column_index(room)
        remove_block(room, 1, 1, 1)
        assert column_index(room)[(1, 1)] == [(0, "dirt")]

    def test_load_block_list_invalidates(self):
        room = _room()
        set_block(room, 1, 1, 0, "dirt")
        column_index(room)
        load_block_list(room, [{"x": 9, "y": 9, "z": 0, "type": "sand"}])
        index = column_index(room)
        assert (1, 1) not in index
        assert index[(9, 9)] == [(0, "sand")]

    def test_stack_top_reports_the_highest_block(self):
        room = _room()
        set_block(room, 4, 4, 0, "dirt")
        set_block(room, 4, 4, 3, "stone")
        assert stack_top(room, 4, 4) == 3
        assert stack_top(room, 7, 7) is None


# ---------------------------------------------------------------------------
# occlusion helpers
# ---------------------------------------------------------------------------

class TestOcclusionHelpers:
    def test_occupied_finds_a_layer_in_the_stack(self):
        stack = [(0, "dirt"), (2, "stone")]
        assert _occupied(stack, 0) and _occupied(stack, 2)
        assert not _occupied(stack, 1)

    def test_gapless_stack_that_fills_the_screen_covers(self):
        stack = [(0, "s"), (1, "s"), (2, "s")]
        assert _fully_covers(stack, 0.5, HORIZON, H, 480)

    def test_a_stack_with_a_hole_never_covers(self):
        """The march must not stop at a column it can be seen through --
        otherwise whatever is visible beyond the gap is erased."""
        holed = [(0, "s"), (2, "s")]
        assert not _fully_covers(holed, 0.5, HORIZON, H, 480)

    def test_a_short_stack_does_not_cover(self):
        assert not _fully_covers([(0, "s")], 0.5, HORIZON, H, 20)


# ---------------------------------------------------------------------------
# projection -- rendered geometry against the closed form
# ---------------------------------------------------------------------------

class TestStackedProjection:
    def test_single_layer_is_still_centred_on_the_horizon(self):
        """Phase 2a's look is the eye_z = 0.5 special case and must not have
        moved: a lone block straddles the horizon symmetrically."""
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        _configure(room)
        top, bottom = _drawn_span(room, _render(room))
        assert abs((HORIZON - top) - (bottom - HORIZON)) <= 2

    def test_a_two_high_stack_is_twice_as_tall_upward(self):
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        set_block(room, 6, 0, 1, "stone")
        _configure(room)
        top, bottom = _drawn_span(room, _render(room))
        # 5.5 cells away: bottom pinned at z=0, top now at z=2.
        assert top == pytest.approx(_project(0.5, 2, 5.5), abs=2)
        assert bottom == pytest.approx(_project(0.5, 0, 5.5), abs=2)

    def test_a_block_above_the_camera_renders_entirely_above_the_horizon(self):
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 2, "stone")  # floating, nothing below it
        _configure(room)
        _top, bottom = _drawn_span(room, _render(room))
        assert bottom < HORIZON

    def test_standing_higher_pushes_a_block_down_the_screen(self):
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        _configure(room)
        low_top, _low_bottom = _drawn_span(room, _render(room))

        _configure(room, z_layer=2)  # same world, eye two layers up
        high_top, _high_bottom = _drawn_span(room, _render(room))
        assert high_top > low_top

    def test_eye_height_is_configurable_within_the_layer(self):
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        _configure(room, eye_height=0.9)
        top, bottom = _drawn_span(room, _render(room))
        assert top == pytest.approx(_project(0.9, 1, 5.5), abs=2)
        assert bottom == pytest.approx(_project(0.9, 0, 5.5), abs=2)


class TestHorizontalFaces:
    def test_top_face_is_drawn_when_looking_down_on_a_block(self):
        """Standing two layers up, a 1-high block shows its top: the drawn
        span reaches ABOVE the top of its vertical face, up to where that
        face's far edge projects."""
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        _configure(room, z_layer=2)
        top, bottom = _drawn_span(room, _render(room))
        side_face_top = _project(2.5, 1, 5.5)
        top_face_far_edge = _project(2.5, 1, 6.5)  # the cell's exit distance
        assert top == pytest.approx(top_face_far_edge, abs=2)
        assert top < side_face_top - 2, "no top face drawn"
        assert bottom == pytest.approx(_project(2.5, 0, 5.5), abs=2)

    def test_no_top_face_when_another_block_sits_on_it(self):
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        set_block(room, 6, 0, 1, "stone")
        _configure(room, z_layer=4)
        top, _bottom = _drawn_span(room, _render(room))
        # The visible top belongs to the UPPER block (z+1 == 2), not the
        # buried one -- so the span starts at the z=2 plane, not z=1.
        assert top == pytest.approx(_project(4.5, 2, 6.5), abs=2)

    def test_underside_is_drawn_when_looking_up_at_an_overhang(self):
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 3, "stone")
        _configure(room)  # eye 0.5, well below the block
        _top, bottom = _drawn_span(room, _render(room))
        assert bottom == pytest.approx(_project(0.5, 3, 6.5), abs=2)


class TestPainterOrdering:
    def test_a_near_wall_hides_a_far_one(self):
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        _configure(room, wall_color="#ff0000")
        near_only = _render(room)

        set_block(room, 10, 0, 0, "stone")  # farther, directly behind
        with_far = _render(room)
        assert (pygame.image.tostring(near_only, "RGB")
                == pygame.image.tostring(with_far, "RGB")), \
            "a farther block changed pixels a nearer one should own"

    def test_a_far_block_is_visible_over_a_short_near_one(self):
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        _configure(room, z_layer=3)  # high enough to see over the near block
        low_only = _drawn_span(room, _render(room))

        set_block(room, 10, 0, 4, "stone")  # tall, further away
        both = _drawn_span(room, _render(room))
        assert both[0] < low_only[0], "the far block should extend the span up"


class TestTexturedSeams:
    def test_a_textured_wall_reaches_its_computed_bottom_edge(self):
        """A textured strip scales its texture column to a ROUNDED height
        while the span it must fill is CEILED, so the blit could fall a row
        short and leave the flat floor colour showing along the bottom of the
        wall. Assert the exact last painted row, not the absence of a gap:
        the shortfall is at the very bottom of the span, so any test that
        looks for background *between* a wall's first and last drawn row is
        structurally blind to it (this one was, and passed against the bug).
        """
        import math
        for dist in (4, 5, 7, 11):
            room = _room()
            _camera(room)
            set_block(room, dist, 0, 0, "cobble")
            _configure(room, wall_textured=True)
            _top, bottom = _drawn_span(room, _render(room))
            px = _px_per_cell(dist - 0.5)
            assert bottom == math.ceil(HORIZON + 0.5 * px) - 1, \
                "wall at %d cells stops short of its bottom edge" % dist

    def test_flat_and_textured_walls_agree_on_their_extent(self):
        """The flat-colour path fills the span directly, so it is the
        reference for where a wall's edges belong."""
        room = _room()
        _camera(room)
        set_block(room, 4, 0, 0, "cobble")
        _configure(room, wall_textured=False)
        flat = _drawn_span(room, _render(room))
        _configure(room, wall_textured=True)
        assert _drawn_span(room, _render(room)) == flat


class TestTexturedHorizontalFaces:
    """Top and bottom faces are texture-mapped, not filled with the
    texture's average colour."""

    # Eye on layer 2 looking at a block 3.5 cells out puts its top face at
    # roughly y 200..223 -- comfortably inside the 240px test surface and
    # deep enough to hold several sample rows. Standing much higher pushes
    # the face off the bottom of the screen entirely.
    FACE_DIST, FACE_EYE = 3.5, 2.5

    def _face_block(self, room, block_type):
        _camera(room)
        set_block(room, int(self.FACE_DIST + 0.5), 0, 0, block_type)

    def _top_face_colors(self, room, **cfg_overrides):
        """Distinct colours down the middle column of a block's top face."""
        _configure(room, z_layer=2, wall_textured=True, **cfg_overrides)
        screen = _render(room)
        y_near = _project(self.FACE_EYE, 1, self.FACE_DIST)
        y_far = _project(self.FACE_EYE, 1, self.FACE_DIST + 1)
        return {screen.get_at((W // 2, y))[:3]
                for y in range(int(y_far) + 1, int(y_near))}

    def test_a_top_face_is_not_one_flat_colour(self):
        room = _room()
        self._face_block(room, "cobble")
        assert len(self._top_face_colors(room)) > 1, \
            "top face rendered as a single flat colour -- not textured"

    def test_top_cast_res_zero_falls_back_to_flat_shading(self):
        """The escape hatch stays available: casting tops is the expensive
        part of a deck-heavy frame."""
        room = _room()
        self._face_block(room, "cobble")
        assert len(self._top_face_colors(room, top_cast_res=0)) == 1

    def test_texturing_tops_changes_the_frame(self):
        room = _room()
        _camera(room)
        for x in range(4, 10):
            set_block(room, x, 0, 0, "cobble")
        _configure(room, z_layer=4, wall_textured=True, top_cast_res=0)
        flat = pygame.image.tostring(_render(room), "RGB")
        _configure(room, z_layer=4, wall_textured=True, top_cast_res=4)
        assert pygame.image.tostring(_render(room), "RGB") != flat

    def test_the_face_uses_its_own_top_texture_not_the_side_one(self, monkeypatch):
        """Assert the wiring, not the colours.

        The obvious version of this test -- render grass and check the top
        face is green-dominant, unlike its dirt-banded side -- passes even
        when the renderer is fed the SIDE texture, because a camera looking
        straight down +x holds the sampled row constant at v=0.5, where
        grass_side happens to be green too. Checking which Surface actually
        reaches the face rasteriser has no such blind spot."""
        from extensions.block_world import renderer as R
        from extensions.block_world.state import block_face_textures
        faces = block_face_textures("grass")
        assert faces["top"] != faces["side"]

        seen = []
        real = R._draw_horizontal_face_textured

        def spy(screen, x0, strip_w, y_a, y_b, texture, *args, **kwargs):
            seen.append(texture)
            return real(screen, x0, strip_w, y_a, y_b, texture, *args, **kwargs)

        monkeypatch.setattr(R, "_draw_horizontal_face_textured", spy)
        room = _room()
        self._face_block(room, "grass")
        self._top_face_colors(room)

        assert seen, "no textured horizontal face was drawn at all"
        expected = R._load_texture(faces["top"])
        assert all(t is expected for t in seen), \
            "top face was rasterised from a texture other than the top one"

    def test_an_underside_uses_the_bottom_texture(self, monkeypatch):
        """grass again: dirt underneath, green on top, so feeding the wrong
        one through is visible here in a way it is not for a block whose
        faces all share a texture."""
        from extensions.block_world import renderer as R
        from extensions.block_world.state import block_face_textures
        faces = block_face_textures("grass")
        assert faces["bottom"] != faces["top"]

        seen = []
        real = R._draw_horizontal_face_textured

        def spy(screen, x0, strip_w, y_a, y_b, texture, *args, **kwargs):
            seen.append(texture)
            return real(screen, x0, strip_w, y_a, y_b, texture, *args, **kwargs)

        monkeypatch.setattr(R, "_draw_horizontal_face_textured", spy)
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 3, "grass")  # overhead, so the eye sees under it
        _configure(room, wall_textured=True)
        _render(room)

        assert seen, "no underside was drawn"
        expected = R._load_texture(faces["bottom"])
        assert all(t is expected for t in seen), \
            "underside was rasterised from a texture other than the bottom one"


class TestFaceTexturePathsAreCached:
    def test_repeated_lookups_return_the_same_object(self):
        """Profiling one frame of the preview's terrace view found 60,905
        calls to block_face_textures, making os.path.join the single most
        expensive thing in the render path."""
        from extensions.block_world.state import block_face_textures
        assert block_face_textures("stone") is block_face_textures("stone")

    def test_each_block_type_still_resolves_its_own_faces(self):
        from extensions.block_world.state import block_face_textures
        assert block_face_textures("stone") != block_face_textures("dirt")
        grass = block_face_textures("grass")
        assert grass["top"].endswith("default_grass.png")
        assert grass["side"].endswith("default_grass_side.png")
        assert grass["bottom"].endswith("default_dirt.png")


class TestTransparentBlocksNeverOcclude:
    """Reported from a playtest: a glass block looked right from the side and
    at a distance, then showed raw sky and floor through itself when walked
    up to face-on.

    Cause was the occlusion early-out, not the compositing. Close up, the
    glass grew big enough to satisfy "this stack covers the whole column",
    which stopped the march -- so the blocks it should have composited
    against were never drawn at all. Being distance-dependent is what made it
    read as a texture glitch."""

    def test_a_transparent_stack_never_stops_the_march(self):
        big = 10_000  # far bigger than any screen: covers by any measure
        assert not _fully_covers([(0, "glass")], 0.5, HORIZON, H, big)
        assert not _fully_covers([(0, "water"), (1, "ice")], 0.5, HORIZON, H, big)
        # One transparent block in an otherwise solid stack is enough.
        assert not _fully_covers([(0, "stone"), (1, "glass")], 0.5, HORIZON, H, big)

    def test_an_opaque_stack_still_stops_it(self):
        """The guard must not have simply disabled the optimisation."""
        assert _fully_covers([(0, "stone")], 0.5, HORIZON, H, 10_000)

    def test_point_blank_glass_still_shows_what_is_behind_it(self):
        """The playtest case end to end: camera one cell from the glass,
        looking straight at it, close enough that the early-out used to
        fire."""
        room = _room()
        _camera(room)
        set_block(room, 1, 0, 0, "glass")  # half a cell away -- fills the view
        _configure(room, wall_textured=True, columns=64)
        glass_only = pygame.image.tostring(_render(room), "RGB")

        set_block(room, 3, 0, 0, "brick")
        assert pygame.image.tostring(_render(room), "RGB") != glass_only, \
            "point-blank glass hid the block behind it"

    def test_point_blank_stone_still_hides_what_is_behind_it(self):
        room = _room()
        _camera(room)
        set_block(room, 1, 0, 0, "stone")
        _configure(room, wall_textured=True, columns=64)
        stone_only = pygame.image.tostring(_render(room), "RGB")

        set_block(room, 3, 0, 0, "brick")
        assert pygame.image.tostring(_render(room), "RGB") == stone_only


class TestTransparentTextures:
    def test_an_alpha_texture_shows_the_block_behind_it(self):
        """2a drew one hit per column, so a glass block's transparent pixels
        exposed the flat sky. 2b paints far->near, so what is actually behind
        shows through. Deliberate -- and the reason the identity proof for
        this phase covers opaque blocks only."""
        room = _room()
        _camera(room)
        set_block(room, 4, 0, 0, "glass")
        _configure(room, wall_textured=True, columns=64)
        glass_only = pygame.image.tostring(_render(room), "RGB")

        set_block(room, 8, 0, 0, "brick")  # behind the glass
        with_backing = pygame.image.tostring(_render(room), "RGB")
        assert glass_only != with_backing
