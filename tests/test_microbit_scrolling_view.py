"""The micro:bit board in a room with a scrolling view (micro:bit follow-up M4).

Finding (2026-11-01): the board is a SCREEN overlay on every target, on purpose -- it is drawn
after the room (outside any view translate) at the object's x/y read as window coordinates, and
a click is hit-tested against those same window coordinates. A scrolling view therefore moves the
object's sprite but not the board, like a draw_gui HUD. These tests pin that, so a future change
to either half (drawing or clicking) cannot silently split them.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

ROOT = Path(__file__).resolve().parent.parent


def _room(view_x):
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRoom
    load_all_plugins()
    data = {"width": 1200, "height": 300, "views_enabled": True,
            "views": {"view_0": {"visible": True, "view_x": view_x, "view_y": 0, "view_w": 400, "view_h": 300,
                                 "port_x": 0, "port_y": 0, "port_w": 400, "port_h": 300}},
            "instances": [{"object": "microbit_1", "x": 200, "y": 150}]}
    return GameRoom("r", data, action_executor=None)


class _Runner:
    def __init__(self, room):
        self.current_room = room


def _hooks():
    from runtime.extension_hooks import get_input_handlers
    return next(h for h in get_input_handlers()
                if h["mouse_down"].__module__ == "pygm_extension_microbit.input")


@pytest.mark.parametrize("view_x", [0, 400, 800])
def test_a_click_at_the_drawn_button_presses_it_whatever_the_view_scroll(view_x):
    from extensions.microbit import layout as L
    room = _room(view_x)
    inst = room.instances[0]
    lay = L.layout_for(inst)
    pos = lay.buttons["a"][:2]
    assert _hooks()["mouse_down"](_Runner(room), 1, *pos) is True
    assert inst.extension_state["microbit"]["simulator"].buttons["a"] is True


def test_the_view_scroll_does_not_move_the_board_layout():
    from extensions.microbit import layout as L
    near, far = L.layout_for(_room(0).instances[0]), L.layout_for(_room(800).instances[0])
    assert near.buttons == far.buttons and near.pads == far.pads


def test_the_drawn_board_is_the_same_pixels_whatever_the_view_scroll():
    import pygame
    from extensions.microbit import renderer
    shots = []
    for view_x in (0, 800):
        room = _room(view_x)
        surface = pygame.Surface((400, 300))
        surface.fill((10, 20, 30))
        renderer.draw_overlay(room.instances[0], surface)
        shots.append(pygame.image.tostring(surface, "RGB"))
    assert shots[0] == shots[1]
    assert shots[0] != pygame.image.tostring(_blank(), "RGB")        # and something was drawn


def _blank():
    import pygame
    s = pygame.Surface((400, 300))
    s.fill((10, 20, 30))
    return s


def test_html5_runs_the_overlays_after_the_per_view_loop_not_inside_it():
    """engine.js: runInstanceOverlays follows the loop that translates by each view (so the
    board is in canvas space, like the desktop's)."""
    src = (ROOT / "export/HTML5/templates/engine.js").read_text(encoding="utf-8")
    loop = src.index("ctx.translate(view.port_x - view.view_x, view.port_y - view.view_y);")
    restore = src.index("ctx.restore();", loop)
    overlay = src.index("runInstanceOverlays(this, ctx);", restore)
    assert 0 < overlay - restore < 200                    # right after the loop, nothing between
    assert "runInstanceOverlays" not in src[loop:restore]

