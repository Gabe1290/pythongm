"""Structured draw_* actions (draw_rectangle/ellipse/circle/line/arrow/
variable/health_bar/background) have codegen on the Kivy and HTML5 export
targets (TODO.md / docs/DEFERRED_ITEMS_PLAN.md follow-up #2).

Before this fix these 8 actions hit each target's "unknown action" default
and silently no-op'd when exported — an author using the built-in draw
actions (as opposed to hand-authored execute_code draw-queue dicts) saw
nothing rendered on Kivy/HTML5 even though the same room worked on desktop.

Fixing this also surfaced a genuine, separate desktop-runtime bug: 'arrow'
was queued by execute_draw_arrow_action but had no entry in
runtime/game_runner.py's _DRAW_HANDLERS, so draw_arrow silently drew
nothing even on the pygame desktop runtime. That's covered here too.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Kivy codegen
# ---------------------------------------------------------------------------

def _gen(action_type, params, event_type="draw", **kwargs):
    g = ActionCodeGenerator(base_indent=2, **kwargs)
    g.process_action({"action_type": action_type, "parameters": params}, event_type)
    return g.get_code()


def _valid(src):
    wrapper = "class _C:\n    def m(self, other=None):\n" + src + "\n"
    try:
        compile(wrapper, "<gen>", "exec")
        return True
    except SyntaxError:
        return False


def test_kivy_draw_rectangle():
    out = _gen("draw_rectangle", {"x1": 1, "y1": 2, "x2": 3, "y2": 4, "filled": True})
    assert "type='rectangle'" in out
    assert "x1=1, y1=2, x2=3, y2=4, filled=True" in out
    assert _valid(out)


def test_kivy_draw_ellipse():
    out = _gen("draw_ellipse", {"x1": 1, "y1": 2, "x2": 3, "y2": 4, "filled": False})
    assert "type='ellipse'" in out
    assert "filled=False" in out
    assert _valid(out)


def test_kivy_draw_circle():
    out = _gen("draw_circle", {"x": 10, "y": 20, "radius": 5})
    assert "type='circle'" in out
    assert "radius=5" in out
    assert _valid(out)


def test_kivy_draw_line():
    out = _gen("draw_line", {"x1": 0, "y1": 0, "x2": 50, "y2": 50})
    assert "type='line'" in out
    assert _valid(out)


def test_kivy_draw_arrow_precomputes_tip_with_trig():
    out = _gen("draw_arrow", {"x1": 0, "y1": 0, "x2": 100, "y2": 0, "tip_size": 12})
    assert "import math as _m" in out
    assert "atan2" in out
    assert "type='arrow'" in out
    assert "tip1_x=_at1x" in out and "tip2_x=_at2x" in out
    assert _valid(out)


def test_kivy_draw_variable_resolves_score_global():
    out = _gen("draw_variable", {"x": 5, "y": 5, "variable": "score"})
    # score resolves through the same _EXPR_GLOBAL_MAP mechanism the other
    # expression-consuming actions already use.
    assert "get_score()" in out
    assert "type='text'" in out
    assert _valid(out)


def test_kivy_draw_health_bar_reads_game_health():
    out = _gen("draw_health_bar", {"x1": 0, "y1": 0, "x2": 100, "y2": 20,
                                    "back_color": "#111111", "bar_color": "#222222"})
    assert "get_game_app" in out
    assert "type='health_bar'" in out
    assert "'#111111'" in out and "'#222222'" in out
    assert _valid(out)


def test_kivy_draw_background_resolves_path():
    out = _gen("draw_background", {"background": "bg_test", "x": 0, "y": 0, "tiled": True},
                background_paths={"bg_test": "assets/images/bg_test.png"})
    assert "type='background'" in out
    assert "assets/images/bg_test.png" in out
    assert "tiled=True" in out
    assert _valid(out)


def test_kivy_draw_background_missing_asset_is_honest_noop():
    out = _gen("draw_background", {"background": "bg_missing", "x": 0, "y": 0})
    assert "not found in export" in out
    assert _valid(out)


# ---------------------------------------------------------------------------
# HTML5 — static source checks (Node isn't a CI dep; see test_html5_views.py
# / test_draw_queue_background_health_bar.py for the established pattern)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("action_type", [
    "draw_rectangle", "draw_ellipse", "draw_circle", "draw_line",
    "draw_arrow", "draw_variable", "draw_health_bar", "draw_background",
])
def test_html5_execute_action_case_present(action_type):
    assert re.search(r"case '%s':" % re.escape(action_type), ENGINE), (
        f"case '{action_type}' missing from executeAction's switch")


def test_html5_draw_rectangle_ellipse_push_correct_type():
    m = re.search(r"case 'draw_rectangle':\s*\n\s*case 'draw_ellipse':(.*?)break;", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "actionType === 'draw_rectangle' ? 'rectangle' : 'ellipse'" in body
    assert "parseNumParam" in body


def test_html5_draw_arrow_precomputes_tips():
    m = re.search(r"case 'draw_arrow': \{(.*?)\n            \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "Math.atan2" in body
    assert "tip1_x" in body and "tip2_x" in body


def test_html5_draw_variable_uses_gm_expression_value():
    m = re.search(r"case 'draw_variable': \{(.*?)\n            \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "gmExpressionValue(params.variable, this, game)" in body


def test_html5_draw_health_bar_reads_game_health():
    m = re.search(r"case 'draw_health_bar':(.*?)break;", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "game ? game.health : 100" in body


def test_html5_draw_background_pushes_background_name():
    m = re.search(r"case 'draw_background':(.*?)break;", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "params.background || params.background_name" in body


def test_html5_render_draw_commands_handles_arrow():
    m = re.search(r"case 'arrow': \{(.*?)\n            \}", ENGINE, re.S)
    assert m, "case 'arrow' missing from renderDrawCommands"
    body = m.group(1)
    assert "ctx.moveTo" in body and "ctx.lineTo" in body
    assert "ctx.stroke()" in body


# ---------------------------------------------------------------------------
# Desktop runtime — the 'arrow' _DRAW_HANDLERS gap surfaced while building
# the Kivy/HTML5 parity fix (see module docstring).
# ---------------------------------------------------------------------------

def test_desktop_draw_handlers_includes_arrow():
    from runtime.game_runner import GameInstance
    assert GameInstance._DRAW_HANDLERS.get('arrow') == '_draw_arrow'


def test_desktop_draw_arrow_renders_three_segments():
    import pygame
    pygame.font.init()
    from types import SimpleNamespace
    from runtime.game_runner import GameInstance

    action_executor = SimpleNamespace(
        game_runner=SimpleNamespace(project_data={"assets": {"fonts": {}}}))
    inst = GameInstance("obj_test", 0, 0, {}, action_executor)

    pygame.display.set_mode((1, 1))
    screen = pygame.Surface((200, 200))
    screen.fill((0, 0, 0))
    inst._draw_arrow(screen, {
        "x1": 10, "y1": 100, "x2": 150, "y2": 100,
        "tip1_x": 140, "tip1_y": 90, "tip2_x": 140, "tip2_y": 110,
        "color": "#FFFFFF",
    })
    # Sample along the shaft and one tip segment; both must be non-black.
    assert screen.get_at((80, 100))[:3] == (255, 255, 255)
    assert screen.get_at((145, 95))[:3] != (0, 0, 0)
