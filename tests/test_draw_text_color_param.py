"""draw_text must honour an explicit `color` / `colour` parameter.

Regression: the runtime only ever used the active Set-Drawing-Color
(default black), silently ignoring any `color` passed to draw_text -- so
every bundled reseau_* sample's `"color": "#ffffff"` rendered black on a
dark background and was unreadable. draw_text now takes an optional
`color`; blank / absent keeps the old behaviour (active colour, then
black), so this is backward-compatible.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame
pygame.init()

from runtime.action_executor import ActionExecutor


class _Inst:
    x = 0
    y = 0

    def __init__(self):
        self._draw_queue = []


def _queued_color(params):
    ex = ActionExecutor()
    inst = _Inst()
    ex.execute_draw_text_action(inst, {"text": '"t"', "x": "1", "y": "1", **params})
    return inst._draw_queue[-1]["color"]


def test_explicit_hex_color_is_used():
    assert _queued_color({"color": "#ffcc00"}) == (255, 204, 0)


def test_british_colour_alias():
    assert _queued_color({"colour": "#00ff00"}) == (0, 255, 0)


def test_no_color_param_falls_back_to_black():
    assert _queued_color({}) == (0, 0, 0)


def test_blank_color_param_falls_back_and_does_not_crash():
    assert _queued_color({"color": ""}) == (0, 0, 0)


def test_active_set_draw_color_still_wins_when_no_param():
    ex = ActionExecutor()
    inst = _Inst()
    inst.draw_color = (10, 20, 30)          # as set_draw_color would leave it
    ex.execute_draw_text_action(inst, {"text": '"t"', "x": "1", "y": "1"})
    assert inst._draw_queue[-1]["color"] == (10, 20, 30)


def test_color_param_is_declared_on_the_action_type():
    from events.action_types import get_action_type
    a = get_action_type("draw_text")
    assert a is not None
    assert "color" in {p.name for p in a.parameters}
