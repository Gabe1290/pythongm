"""Font assets actually affect draw_text/draw_scaled_text rendering
(TODO.md's "font assets aren't consumed by draw_text" follow-up from the
deferred-items plan's tier-1 asset-editor work).

set_draw_font (runtime/action_executor.py execute_set_draw_font_action)
stored a font *asset name* plus halign/valign on the instance, but
_draw_text/_draw_scaled_text always rendered at a hardcoded 24pt default
font and always blit at the raw (x, y) with no alignment — draw_font/
draw_halign/draw_valign were set but never read anywhere. Fixed via
_resolve_draw_font (looks the asset up in project_data, builds/caches a
real Font honoring font_name/size/bold/italic) and _align_text_pos
(shifts the blit position per halign/valign, matching GameMaker's
draw_set_halign/draw_set_valign semantics).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pygame
pygame.font.init()
from runtime.game_runner import GameInstance


def _instance(fonts=None):
    action_executor = SimpleNamespace(
        game_runner=SimpleNamespace(project_data={"assets": {"fonts": fonts or {}}}))
    inst = GameInstance("obj_test", 0, 0, {}, action_executor)
    return inst


class TestGetCachedFont:
    def test_default_family_matches_prior_behavior(self):
        inst = _instance()
        font = inst._get_cached_font(24)
        assert isinstance(font, pygame.font.Font)

    def test_caches_by_full_key_not_just_size(self):
        inst = _instance()
        a = inst._get_cached_font(24, family="Arial")
        b = inst._get_cached_font(24, family="Arial")
        c = inst._get_cached_font(24, family="Courier")
        assert a is b  # same key -> cached, not rebuilt
        assert len(inst._font_cache) == 2  # different family -> different entry

    def test_bold_italic_do_not_collide_with_plain(self):
        inst = _instance()
        plain = inst._get_cached_font(20)
        bold = inst._get_cached_font(20, bold=True)
        italic = inst._get_cached_font(20, italic=True)
        assert len({id(plain), id(bold), id(italic)}) == 3


class TestResolveDrawFont:
    def test_no_draw_font_uses_default_24pt(self):
        inst = _instance()
        font = inst._resolve_draw_font()
        assert font is inst._get_cached_font(24)

    def test_missing_font_asset_falls_back_to_default(self):
        inst = _instance(fonts={})
        inst.draw_font = "fnt_does_not_exist"
        font = inst._resolve_draw_font()
        assert font is inst._get_cached_font(24)

    def test_known_font_asset_resolves_size_and_style(self):
        inst = _instance(fonts={
            "fnt_title": {"font_name": "Arial", "size": 32, "bold": True, "italic": False},
        })
        inst.draw_font = "fnt_title"
        font = inst._resolve_draw_font()
        assert font is inst._get_cached_font(32, "Arial", True, False)
        # Genuinely a different (bigger, bold) font than the untouched default.
        assert font is not inst._get_cached_font(24)

    def test_bad_size_value_does_not_crash(self):
        inst = _instance(fonts={
            "fnt_bad": {"font_name": "Arial", "size": "not-a-number"},
        })
        inst.draw_font = "fnt_bad"
        font = inst._resolve_draw_font()  # must not raise
        assert isinstance(font, pygame.font.Font)


class TestAlignTextPos:
    def test_left_top_is_unshifted(self):
        inst = _instance()
        assert inst._align_text_pos(10, 20, 100, 40) == (10, 20)

    def test_center_middle_shifts_by_half(self):
        inst = _instance()
        inst.draw_halign = "center"
        inst.draw_valign = "middle"
        assert inst._align_text_pos(10, 20, 100, 40) == (10 - 50, 20 - 20)

    def test_right_bottom_shifts_by_full(self):
        inst = _instance()
        inst.draw_halign = "right"
        inst.draw_valign = "bottom"
        assert inst._align_text_pos(10, 20, 100, 40) == (10 - 100, 20 - 40)


def _bbox_of_non_background(screen, bg=(0, 0, 0)):
    """Bounding box (left, top, right, bottom) of every pixel that
    differs from bg, or None if the surface is untouched. pygame.Surface
    doesn't allow patching .blit (immutable C type — same class of issue
    as pygame.mixer.Sound elsewhere in this suite), so this end-to-end
    class renders onto a real surface and inspects real pixels instead of
    spying on the blit call."""
    w, h = screen.get_size()
    xs, ys = [], []
    for x in range(0, w, 2):       # every-other-pixel is plenty for a
        for y in range(0, h, 2):   # coarse bounding box, and much faster
            if screen.get_at((x, y))[:3] != bg:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


class TestDrawTextEndToEnd:
    def _render(self, inst, cmd, method="_draw_text", size=(200, 200)):
        pygame.display.set_mode((1, 1))
        screen = pygame.Surface(size)
        screen.fill((0, 0, 0))
        getattr(inst, method)(screen, cmd)
        return screen

    def test_default_alignment_renders_at_raw_xy(self):
        inst = _instance()
        screen = self._render(inst, {"text": "Hi", "x": 10, "y": 20, "color": "#FFFFFF"})
        bbox = _bbox_of_non_background(screen)
        assert bbox is not None
        # Glyph rendering leaves a little padding before the first ink
        # pixel; the top-left of the drawn text must be close to (10, 20),
        # not shifted by a full glyph width/height the way misapplied
        # alignment would.
        assert 10 <= bbox[0] < 25
        assert 20 <= bbox[1] < 35

    def test_center_alignment_shifts_the_render_left(self):
        inst = _instance()
        inst.draw_halign = "center"
        unaligned = self._render(_instance(), {"text": "Hello World", "x": 100, "y": 20, "color": "#FFFFFF"})
        centered = self._render(inst, {"text": "Hello World", "x": 100, "y": 20, "color": "#FFFFFF"})
        left_unaligned = _bbox_of_non_background(unaligned)[0]
        left_centered = _bbox_of_non_background(centered)[0]
        assert left_centered < left_unaligned  # shifted left, per anchor=center

    def test_scaled_text_aligns_against_post_scale_size(self):
        inst = _instance()
        inst.draw_halign = "right"
        screen = self._render(
            inst, {"text": "Hi", "x": 150, "y": 20, "xscale": 3.0, "yscale": 1.0, "color": "#FFFFFF"},
            method="_draw_scaled_text", size=(300, 100))
        bbox = _bbox_of_non_background(screen)
        assert bbox is not None
        # Right-aligned at x=150 with a 3x-wide surface: the right edge of
        # the rendered text must land at/near x=150, well left of where an
        # unaligned (left-anchored) render would put its right edge.
        assert bbox[2] <= 155

    def test_custom_font_asset_changes_rendered_size(self):
        """A bigger font asset must actually produce a wider bounding box,
        not just resolve to a Font object that's never used."""
        small = _instance()
        big = _instance(fonts={"fnt_big": {"font_name": None, "size": 72}})
        big.draw_font = "fnt_big"

        small_bbox = _bbox_of_non_background(
            self._render(small, {"text": "Hello", "x": 0, "y": 0, "color": "#FFFFFF"}, size=(400, 400)))
        big_bbox = _bbox_of_non_background(
            self._render(big, {"text": "Hello", "x": 0, "y": 0, "color": "#FFFFFF"}, size=(400, 400)))

        small_width = small_bbox[2] - small_bbox[0]
        big_width = big_bbox[2] - big_bbox[0]
        assert big_width > small_width
