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

import math
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
    march_ray, render_block_world_view, _fully_covers, _has_neighbor,
    _stack_opaque_spans, _merge_covered, _is_covered,
)
import extensions.block_world.renderer as bw_renderer  # noqa: E402

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
        # Pinned deliberately. These tests assert closed-form projection
        # geometry, and an eye at the middle of its own layer keeps the
        # arithmetic 1:1 with the layer numbers. The SHIPPED default is 1.5
        # (a two-block-tall body, so you can see the tops of blocks beside
        # you) -- TestDefaultEyeHeight covers that.
        "eye_height": 0.5,
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
    def test_neighbor_found_in_a_contiguous_stack(self):
        stack = [(0, "dirt"), (1, "stone"), (2, "brick")]
        assert _has_neighbor(stack, 0, +1)   # 0 has a block at 1
        assert _has_neighbor(stack, 1, +1)   # 1 has a block at 2
        assert _has_neighbor(stack, 1, -1)   # 1 has a block at 0
        assert _has_neighbor(stack, 2, -1)   # 2 has a block at 1

    def test_no_neighbor_across_a_gap(self):
        """The whole point of doing this by adjacency, not by scanning for
        'is z+1 present anywhere': a block further up the same stack must
        NOT count as a neighbour of a lower one it isn't touching."""
        stack = [(0, "dirt"), (2, "brick")]   # gap at z=1
        assert not _has_neighbor(stack, 0, +1)   # nothing at z=1
        assert not _has_neighbor(stack, 1, -1)   # nothing at z=1, from above

    def test_no_neighbor_past_either_end(self):
        stack = [(0, "dirt"), (1, "stone")]
        assert not _has_neighbor(stack, 1, +1)   # nothing above the top entry
        assert not _has_neighbor(stack, 0, -1)   # nothing below the bottom entry

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


class TestCumulativeCoverage:
    """The perf-only occlusion-culling helpers the column loop in
    render_block_world_view uses to skip cells that are guaranteed hidden
    by nearer, already-collected opaque geometry -- a multi-cell
    generalization of _fully_covers's single-stack check above."""

    def test_stack_opaque_spans_one_per_block(self):
        stack = [(0, "s"), (1, "s"), (2, "s")]
        spans = _stack_opaque_spans(stack, 0.5, HORIZON, 40, H)
        assert len(spans) == 3
        for y0, y1 in spans:
            assert y1 - y0 == pytest.approx(40)

    def test_stack_opaque_spans_skips_transparent_blocks(self):
        stack = [(0, "s"), (1, "glass"), (2, "s")]
        spans = _stack_opaque_spans(stack, 0.5, HORIZON, 40, H)
        assert len(spans) == 2  # the glass block contributes nothing

    def test_stack_opaque_spans_clips_to_the_screen(self):
        # A close, tall stack whose projection runs off both edges of the
        # screen -- each block's span must still be clipped to [0, H].
        stack = [(0, "s"), (1, "s")]
        spans = _stack_opaque_spans(stack, 0.5, HORIZON, 10_000, H)
        assert all(0.0 <= y0 and y1 <= H for y0, y1 in spans)

    def test_merge_covered_joins_overlapping_ranges(self):
        covered = []
        _merge_covered(covered, 10, 50)
        _merge_covered(covered, 40, 80)
        assert covered == [(10, 80)]

    def test_merge_covered_joins_touching_ranges(self):
        covered = []
        _merge_covered(covered, 10, 50)
        _merge_covered(covered, 50, 80)
        assert covered == [(10, 80)]

    def test_merge_covered_keeps_disjoint_ranges_separate(self):
        covered = []
        _merge_covered(covered, 10, 20)
        _merge_covered(covered, 40, 50)
        assert covered == [(10, 20), (40, 50)]

    def test_merge_covered_bridges_a_gap_it_fills(self):
        covered = []
        _merge_covered(covered, 10, 20)
        _merge_covered(covered, 40, 50)
        _merge_covered(covered, 15, 45)
        assert covered == [(10, 50)]

    def test_is_covered_true_inside_a_single_range(self):
        assert _is_covered([(10, 50)], 20, 30)

    def test_is_covered_false_when_partially_outside(self):
        assert not _is_covered([(10, 50)], 20, 60)

    def test_is_covered_false_across_a_gap_between_ranges(self):
        # Even though the union of two ranges spans the query, containment
        # requires a SINGLE covering range -- correct, because two
        # disjoint (unmerged) ranges by definition have a gap between them.
        assert not _is_covered([(10, 20), (30, 40)], 15, 35)

    def test_empty_span_is_trivially_covered(self):
        assert _is_covered([], 10, 10)


class TestOcclusionCullingSkipsHiddenCells:
    """Integration: a farther cell whose whole projected span is already
    guaranteed covered by nearer, gapless opaque geometry along the SAME
    ray is dropped before it ever reaches _draw_wall_strip -- proving the
    perf shortcut actually fires, on top of TestPainterOrdering's proof
    (above, in this same file) that skipping it never changes a pixel."""

    def _wall_strip_call_count(self, monkeypatch, room):
        calls = {"n": 0}
        real = bw_renderer._draw_wall_strip

        def spy(*a, **k):
            calls["n"] += 1
            return real(*a, **k)

        monkeypatch.setattr(bw_renderer, "_draw_wall_strip", spy)
        _render(room)
        return calls["n"]

    def test_a_fully_covering_near_wall_drops_the_far_ones(self, monkeypatch):
        room = _room()
        _camera(room)
        # A close, tall, gapless wall -- projects far enough to fill the
        # whole screen height at this distance -- directly in front of two
        # more (redundant) walls further down the same ray.
        for z in range(0, 8):
            set_block(room, 2, 0, z, "stone")
        set_block(room, 6, 0, 0, "stone")
        set_block(room, 10, 0, 0, "stone")
        _configure(room, wall_color="#ff0000")
        with_far_walls = self._wall_strip_call_count(monkeypatch, room)

        room2 = _room()
        _camera(room2)
        for z in range(0, 8):
            set_block(room2, 2, 0, z, "stone")
        _configure(room2, wall_color="#ff0000")
        without_far_walls = self._wall_strip_call_count(monkeypatch, room2)

        assert with_far_walls == without_far_walls, \
            "the two farther, fully-hidden walls should cost zero extra draws"

    def test_an_open_sightline_still_draws_every_visible_cell(self, monkeypatch):
        """The culling must not over-reach: cells that are genuinely
        visible (nothing gapless/opaque in front of them along this ray)
        still get drawn, one hit per occupied cell crossed."""
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")   # short -- doesn't fill the screen
        set_block(room, 10, 0, 4, "stone")  # tall, but far enough to sit
                                              # above the near block's span
        _configure(room, wall_color="#ff0000", z_layer=3)
        calls = self._wall_strip_call_count(monkeypatch, room)
        assert calls == 2


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


class TestPitch:
    """Phase 2c. Looking up and down is a Y-SHEAR: the horizon slides and
    every other formula is untouched. That works because the renderer states
    height as one line through `horizon`, and because pitch does not change
    azimuth -- a screen column is still the same ray, so the horizontal DDA
    never learns about it."""

    def test_level_puts_the_horizon_at_the_middle(self):
        from extensions.block_world.renderer import horizon_for
        assert horizon_for(H, 0) == pytest.approx(H / 2)

    def test_looking_up_pushes_the_horizon_down_the_screen(self):
        """Look up and you see more sky, so the horizon appears LOWER."""
        from extensions.block_world.renderer import horizon_for
        assert horizon_for(H, 20) > H / 2
        assert horizon_for(H, -20) < H / 2

    def test_the_shift_is_screen_height_times_tan(self):
        """The vertical focal length works out to exactly screen_h pixels."""
        from extensions.block_world.renderer import horizon_for
        assert horizon_for(H, 30) == pytest.approx(H / 2 + H * math.tan(math.radians(30)))

    def test_it_is_clamped(self):
        from extensions.block_world.renderer import horizon_for, MAX_PITCH_DEGREES
        assert horizon_for(H, 5000) == pytest.approx(horizon_for(H, MAX_PITCH_DEGREES))
        assert horizon_for(H, -5000) == pytest.approx(horizon_for(H, -MAX_PITCH_DEGREES))

    def _sky_rows(self, room):
        """How many rows of the empty view are ceiling rather than floor."""
        screen = _render(room)
        ceil_rgb = tuple(room.parse_color(CEILING))
        return sum(1 for y in range(H)
                   if screen.get_at((W // 2, y))[:3] == ceil_rgb)

    def test_the_rendered_horizon_follows_the_pitch(self):
        room = _room()
        _camera(room)
        _configure(room)
        level = self._sky_rows(room)
        _configure(room, pitch=20)
        assert self._sky_rows(room) > level, "looking up should show more sky"
        _configure(room, pitch=-20)
        assert self._sky_rows(room) < level, "looking down should show less sky"

    def test_a_level_view_is_unchanged_by_the_feature(self):
        """Backward compatibility: an absent pitch and an explicit zero must
        render the same frame, so every world built before 2c is untouched."""
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        _configure(room)
        block_world_state(room)["camera"].pop("pitch", None)
        absent = pygame.image.tostring(_render(room), "RGB")
        _configure(room, pitch=0)
        assert pygame.image.tostring(_render(room), "RGB") == absent

    def test_the_overlay_maths_follows_the_pitched_horizon(self):
        """project_point and unproject_to_plane take the horizon explicitly.
        If an overlay kept assuming screen centre, the placement outline
        would slide off the geometry the moment you looked up or down."""
        from extensions.block_world.renderer import (project_point, horizon_for,
                                                     unproject_to_plane)
        horizon = horizon_for(H, -25)
        common = dict(cam_x=16, cam_y=16, eye_z=0.5, facing_screen_rad=0.3,
                      fov_rad=math.radians(66), screen_w=W, screen_h=H,
                      cell_size=CELL, horizon=horizon)
        sx, sy = project_point(240, 90, 0, **common)
        assert unproject_to_plane(sx, sy, 0, **common) == pytest.approx((240, 90))
        # And the pitched projection really does differ from the level one.
        level = project_point(240, 90, 0, **dict(common, horizon=None))
        assert level[1] != pytest.approx(sy)

    def test_pitch_deepens_how_steeply_you_can_aim(self):
        """The point of the whole phase: at level the steepest ray drops
        about half a cell per cell (~26 deg). Looking down lifts that, which
        is what makes digging down possible."""
        from extensions.block_world.renderer import screen_ray, horizon_for
        def steepest(pitch):
            _angle, z_per_px = screen_ray(
                W / 2, H - 1, 0.0, math.radians(66), W, H, CELL,
                horizon_for(H, pitch))
            return -z_per_px * CELL
        assert steepest(0) == pytest.approx(0.5, abs=0.05)
        assert steepest(-30) > 1.0
        assert steepest(-60) > steepest(-30)


class TestPointProjection:
    """project_point is the inverse of what the render loop does per column.
    Anything overlaid on the view -- the placement outline today, a selection
    box or a marker later -- rides on it, so it has to agree with the
    rasteriser exactly, not approximately."""

    FOV = math.radians(66)

    def _project(self, wx, wy, wz, eye_z=0.5, facing=0.0):
        from extensions.block_world.renderer import project_point
        return project_point(wx, wy, wz, 16, 16, eye_z, facing, self.FOV,
                             W, H, CELL)

    def test_straight_ahead_at_eye_height_is_the_screen_centre(self):
        assert self._project(16 + 5 * CELL, 16, 0.5) == pytest.approx((W / 2, H / 2))

    def test_behind_the_camera_is_none(self):
        assert self._project(16 - 5 * CELL, 16, 0.5) is None

    def test_on_the_camera_plane_is_none(self):
        """Exactly at zero depth the divide would blow up."""
        assert self._project(16, 16 + 3 * CELL, 0.5) is None

    @pytest.mark.parametrize("eye_z", [0.5, 1.5, 3.5, 5.5])
    @pytest.mark.parametrize("zval", [0, 1, 2, 3])
    def test_vertical_mapping_matches_the_renderer_formula(self, eye_z, zval):
        """Parametrised over EYE HEIGHT as well as block height: with only
        eye_z = 0.5 covered, hardcoding that constant in the projection
        passes every test and then misplaces every overlay the moment the
        player stands on anything."""
        got = self._project(16 + 5 * CELL, 16, zval, eye_z=eye_z)[1]
        assert got == pytest.approx(_project(eye_z, zval, 5.0))

    def test_fov_edges_map_to_the_screen_edges(self):
        depth = 5 * CELL
        lateral = depth * math.tan(self.FOV / 2)
        assert self._project(16 + depth, 16 - lateral, 0.5)[0] == pytest.approx(0)
        assert self._project(16 + depth, 16 + lateral, 0.5)[0] == pytest.approx(W)

    def test_it_lands_on_geometry_the_renderer_actually_drew(self):
        """The test that matters: project the top edge of a wall and check
        the wall really is drawn there. Everything above could agree with the
        formula while both drifted from the picture."""
        room = _room()
        _camera(room)
        set_block(room, 6, 0, 0, "stone")
        _configure(room)
        drawn_top, _bottom = _drawn_span(room, _render(room))
        # Near face of that block, at its top (z = 1).
        projected = self._project(6 * CELL, 16, 1)[1]
        assert abs(projected - drawn_top) <= 1


class TestUnprojectToPlane:
    """The inverse of project_point onto a horizontal plane -- what turns a
    mouse position into the floor square it appears to be over. Being an
    EXACT inverse is the whole point: a cursor that lands a cell away from
    where it looks is worse than no cursor."""

    FOV = math.radians(66)

    def _common(self, facing=0.4):
        return dict(cam_x=16, cam_y=16, eye_z=0.5, facing_screen_rad=facing,
                    fov_rad=self.FOV, screen_w=W, screen_h=H, cell_size=CELL)

    @pytest.mark.parametrize("world", [
        (200, 40), (90, 300), (400, -120), (64, 64), (700, 500),
    ])
    def test_round_trips_with_project_point(self, world):
        from extensions.block_world.renderer import project_point, unproject_to_plane
        wx, wy = world
        common = self._common()
        sx, sy = project_point(wx, wy, 0, **common)
        back = unproject_to_plane(sx, sy, 0, **common)
        assert back == pytest.approx((wx, wy))

    @pytest.mark.parametrize("eye_z,plane_z", [
        (0.5, 0),    # standing on the ground
        (2.5, 2),    # standing on a two-high stack
        (5.5, 5),    # up on the terrace deck
        (3.5, 0),    # looking down at the ground from a ledge
        (0.5, 3),    # looking up at an overhang
    ])
    def test_round_trips_at_any_eye_height(self, eye_z, plane_z):
        """Parametrised over the eye-to-plane DISTANCE, not just eye height.
        Every case above with a difference of exactly 0.5 would still pass
        with that value hardcoded -- (3.5, 0) and (0.5, 3) are the ones that
        actually exercise it, and without them the cursor would drift the
        moment the player stood on anything."""
        from extensions.block_world.renderer import project_point, unproject_to_plane
        common = dict(cam_x=16, cam_y=16, eye_z=eye_z, facing_screen_rad=0.4,
                      fov_rad=self.FOV, screen_w=W, screen_h=H, cell_size=CELL)
        sx, sy = project_point(200, 40, plane_z, **common)
        assert unproject_to_plane(sx, sy, plane_z, **common) == pytest.approx((200, 40))

    def test_above_the_horizon_never_meets_the_floor(self):
        from extensions.block_world.renderer import unproject_to_plane
        assert unproject_to_plane(400, HORIZON - 40, 0, **self._common()) is None

    def test_exactly_on_the_horizon_is_none(self):
        """The divide runs away to infinity as the horizon is approached."""
        from extensions.block_world.renderer import unproject_to_plane
        assert unproject_to_plane(400, HORIZON, 0, **self._common()) is None

    def test_lower_on_the_screen_is_nearer(self):
        from extensions.block_world.renderer import unproject_to_plane
        common = self._common(facing=0.0)
        near = unproject_to_plane(W / 2, HORIZON + 90, 0, **common)
        far = unproject_to_plane(W / 2, HORIZON + 10, 0, **common)
        assert near[0] < far[0], "moving down the screen should come closer"

    def test_the_screen_centre_is_straight_ahead(self):
        from extensions.block_world.renderer import unproject_to_plane
        wx, wy = unproject_to_plane(W / 2, HORIZON + 60, 0, **self._common(facing=0.0))
        assert wy == pytest.approx(16)   # no lateral offset
        assert wx > 16                   # in front

    def test_right_of_centre_lands_to_the_right(self):
        """Screen-right is the facing direction turned +90 degrees in this
        y-down frame, so facing east it is south (+y)."""
        from extensions.block_world.renderer import unproject_to_plane
        common = self._common(facing=0.0)
        left = unproject_to_plane(W * 0.25, HORIZON + 60, 0, **common)
        right = unproject_to_plane(W * 0.75, HORIZON + 60, 0, **common)
        assert left[1] < 16 < right[1]

    def test_a_ceiling_plane_works_the_other_way_up(self):
        """Symmetric: a plane above the eye is met by rays above the horizon
        and never by ones below it."""
        from extensions.block_world.renderer import unproject_to_plane
        common = self._common(facing=0.0)
        assert unproject_to_plane(400, HORIZON - 40, 3, **common) is not None
        assert unproject_to_plane(400, HORIZON + 40, 3, **common) is None


class TestCellOutline:
    def test_outlines_a_cell_and_reports_it(self):
        from extensions.block_world.renderer import draw_cell_outline
        screen = pygame.Surface((W, H))
        screen.fill((0, 0, 0))
        drew = draw_cell_outline(screen, (4, 0, 0), 16, 16, 0.5, 0.0,
                                 math.radians(66), CELL)
        assert drew is True
        lit = [(x, y) for y in range(H) for x in range(W)
               if screen.get_at((x, y))[:3] != (0, 0, 0)]
        assert lit, "nothing was drawn"

    def test_the_outline_sits_below_the_horizon(self):
        """It marks a floor square at the camera's own layer, and the eye is
        half a block above that floor -- so it belongs under the horizon. An
        outline drawn above it would be projecting from the wrong height."""
        from extensions.block_world.renderer import draw_cell_outline
        screen = pygame.Surface((W, H))
        screen.fill((0, 0, 0))
        draw_cell_outline(screen, (4, 0, 0), 16, 16, 0.5, 0.0,
                          math.radians(66), CELL)
        ys = [y for y in range(H) for x in range(W)
              if screen.get_at((x, y))[:3] != (0, 0, 0)]
        assert min(ys) > HORIZON

    def test_all_four_corners_of_the_square_are_drawn(self):
        """Pins the SHAPE, not just that ink landed. Checking only that
        something was drawn, or only its bounding box, lets a quad collapse
        to a triangle unnoticed -- one wrong corner still paints roughly the
        right region of screen."""
        from extensions.block_world.renderer import draw_cell_outline, project_point
        screen = pygame.Surface((W, H))
        screen.fill((0, 0, 0))
        draw_cell_outline(screen, (4, 0, 0), 16, 16, 0.5, 0.0,
                          math.radians(66), CELL)
        lit = {(x, y) for y in range(H) for x in range(W)
               if screen.get_at((x, y))[:3] != (0, 0, 0)}
        assert lit

        for wx, wy in ((4 * CELL, 0), (5 * CELL, 0),
                       (5 * CELL, CELL), (4 * CELL, CELL)):
            sx, sy = project_point(wx, wy, 0, 16, 16, 0.5, 0.0,
                                   math.radians(66), W, H, CELL)
            near = [(x, y) for (x, y) in lit
                    if abs(x - sx) <= 2 and abs(y - sy) <= 2]
            assert near, "corner (%d, %d) of the square was never drawn" % (wx, wy)

    def test_a_cell_behind_the_camera_is_skipped(self):
        """Half a quad projected from behind the camera is nonsense, and
        worse than drawing nothing."""
        from extensions.block_world.renderer import draw_cell_outline
        screen = pygame.Surface((W, H))
        screen.fill((0, 0, 0))
        assert draw_cell_outline(screen, (-6, 0, 0), 16, 16, 0.5, 0.0,
                                 math.radians(66), CELL) is False
        assert screen.get_at((W // 2, H // 2))[:3] == (0, 0, 0)

    def test_a_cell_far_off_to_the_side_is_skipped_cleanly(self):
        from extensions.block_world.renderer import draw_cell_outline
        screen = pygame.Surface((W, H))
        screen.fill((0, 0, 0))
        # In front, but way outside the field of view.
        draw_cell_outline(screen, (2, -40, 0), 16, 16, 0.5, 0.0,
                          math.radians(66), CELL)  # must not raise
        assert screen.get_at((W // 2, H // 2))[:3] == (0, 0, 0)

    def test_it_tracks_the_facing_angle(self):
        from extensions.block_world.renderer import draw_cell_outline
        def render(facing):
            screen = pygame.Surface((W, H))
            screen.fill((0, 0, 0))
            draw_cell_outline(screen, (4, 0, 0), 16, 16, 0.5, facing,
                              math.radians(66), CELL)
            return pygame.image.tostring(screen, "RGB")
        assert render(0.0) != render(math.radians(20))


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
