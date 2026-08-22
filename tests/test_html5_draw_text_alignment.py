"""HTML5 export never applied set_draw_font's halign/valign at all — the
canvas 'text'/'scaled_text' render case hardcoded ctx.textAlign='left' and
ctx.textBaseline='top' unconditionally, and the set_draw_font action case
didn't even store the values. Desktop already supported this correctly
(execute_set_draw_font_action stores instance.draw_halign/draw_valign;
GameInstance._align_text_pos shifts x/y by the rendered text's own
width/height — a genuine measurement, not a guess).

Needed for the promo game's hub screen: its two header lines are meant to
be centered in a 480px-wide room, and every previous attempt at that used
hand-guessed x offsets against the text's approximate width (fragile —
this repo's own CLAUDE.md documents a "Quitter"/"Score" pixel-overlap bug
from exactly this class of guess, earlier this session).

Fix: set_draw_font now also stores this.draw_halign/this.draw_valign
(matching GM's numeric align 0/1/2 -> left/center/right fallback, same
mapping as desktop's _GM_FONT_ALIGN_FALLBACK); draw_text forwards them
into the queued command; the render case sets ctx.textAlign/textBaseline
from the command, letting canvas do the real measurement instead of
manual width math — a different (but equally exact) mechanism from
desktop's approach, not a byte-for-byte port of it.

Verification tier: desktop via a real ActionExecutor + GameInstance call
(pygame font metrics are real, not mocked); HTML5 via source-level
assertions on engine.js, per this repo's "no Node in CI" convention.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Desktop (already correct — a guard against a future regression)
# ---------------------------------------------------------------------------

def test_desktop_center_halign_shifts_x_left_by_half_the_text_width():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.action_executor import ActionExecutor
    from runtime.game_runner import GameInstance

    class FakeInstance:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.object_name = "test"

    ex = ActionExecutor(game_runner=None)
    inst = FakeInstance()
    ex.execute_set_draw_font_action(inst, {"halign": "center"})
    assert inst.draw_halign == "center"

    real_inst = GameInstance.__new__(GameInstance)
    real_inst.draw_halign = "center"
    real_inst.draw_valign = "top"
    x, y = real_inst._align_text_pos(240, 12, width=100, height=20)
    assert x == 240 - 50  # shifted left by half the (real) text width


# ---------------------------------------------------------------------------
# HTML5
# ---------------------------------------------------------------------------

def test_html5_set_draw_font_stores_halign_and_valign():
    m = re.search(r"case 'set_draw_font': \{(.*?)\n            \}", ENGINE, re.S)
    assert m, "set_draw_font case not found"
    body = m.group(1)
    assert "this.draw_halign" in body
    assert "this.draw_valign" in body
    # GM numeric align fallback, matching desktop's _GM_FONT_ALIGN_FALLBACK
    assert "{ 0: 'left', 1: 'center', 2: 'right' }" in body


def test_html5_draw_text_forwards_halign_valign_into_the_queued_command():
    m = re.search(r"case 'draw_text': \{(.*?)\n            \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "halign: this.draw_halign || 'left'" in body
    assert "valign: this.draw_valign || 'top'" in body


def test_html5_text_render_applies_canvas_native_alignment():
    case = ENGINE[ENGINE.index("case 'text':"):]
    case = case[:case.index("case 'lives'")]
    assert "cmd.halign || 'left'" in case
    assert "cmd.valign || 'top'" in case
    assert "ctx.textAlign = " in case
    assert "ctx.textBaseline = " in case
    # no longer hardcoded
    assert "ctx.textAlign = 'left';\n" not in case.split("halign")[0]


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
