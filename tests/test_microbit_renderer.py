"""The drawn micro:bit (docs/MICROBIT_EXTENSION_PLAN.md, Stage S5).

Pixel tests assert WHERE things land (the minimap lesson): LED (2,2) at
brightness 9 is red at its computed position, a pressed button changes
colour at its computed centre, and so on. Geometry lives in the pure
``layout`` module; ``draw_board``/``draw_overlay`` paint from it.
"""
import ast
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
EXT_DIR = REPO_ROOT / "extensions" / "microbit"

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()

from extensions.microbit import layout as L  # noqa: E402
from extensions.microbit import renderer as R  # noqa: E402
from extensions.microbit.simulator import MicrobitSimulator  # noqa: E402

BG = (30, 60, 90)


def _canvas(w=320, h=260):
    surf = pygame.Surface((w, h))
    surf.fill(BG)
    return surf


def _px(surf, pos):
    return tuple(surf.get_at(pos))[:3]


def _redness(color):
    r, g, b = color
    return r - max(g, b)


# --- layout (pure) ---------------------------------------------------------------

def test_layout_is_pure():
    tree = ast.parse((EXT_DIR / "layout.py").read_text(encoding="utf-8"))
    mods = {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    mods |= {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not mods & {"pygame", "PySide6"}


def test_board_is_centred_and_sized_at_scale_one():
    lay = L.board_layout(200, 150)
    x, y, w, h = lay.body
    assert (w, h) == (L.BODY_W, L.BODY_H)
    assert x + w / 2 == 200 and y + h / 2 == 150


def test_led_grid_is_5x5_evenly_spaced_and_centred_on_the_board():
    lay = L.board_layout(200, 150)
    assert lay.led_center(2, 2)[0] == 200
    for y in range(5):
        for x in range(4):
            ax, ay = lay.led_center(x, y)
            bx, by = lay.led_center(x + 1, y)
            assert (bx - ax, by - ay) == (L.LED_PITCH, 0)
    assert lay.led_center(0, 1)[1] - lay.led_center(0, 0)[1] == L.LED_PITCH


def test_scale_multiplies_every_distance():
    a, b = L.board_layout(100, 100, 1.0), L.board_layout(100, 100, 2.0)
    assert b.body[2] == 2 * a.body[2]
    assert b.led_center(4, 4)[0] - 100 == 2 * (a.led_center(4, 4)[0] - 100)
    assert b.buttons["b"][0] - 100 == 2 * (a.buttons["b"][0] - 100)


def test_buttons_flank_the_display_logo_is_above_pads_are_below():
    lay = L.board_layout(200, 150)
    assert lay.buttons["a"][0] < lay.led_center(0, 2)[0] < lay.led_center(4, 2)[0] < lay.buttons["b"][0]
    assert lay.logo[1] < lay.led_center(2, 0)[1]
    assert all(p[1] > lay.led_center(2, 4)[1] for p in lay.pads.values())
    assert list(lay.pads) == ["0", "1", "2", "3V", "GND"]
    xs = [lay.pads[n][0] for n in lay.pads]
    assert xs == sorted(xs)


def test_all_parts_sit_inside_the_body():
    lay = L.board_layout(200, 150)
    bx, by, bw, bh = lay.body
    inside = lambda x, y: bx <= x <= bx + bw and by <= y <= by + bh  # noqa: E731
    for row in lay.leds:
        assert all(inside(*c) for c in row)
    for cx, cy, r in lay.buttons.values():
        assert inside(cx - r, cy - r) and inside(cx + r, cy + r)
    for x, y, w, h in lay.pads.values():
        assert inside(x, y) and inside(x + w, y + h)


def test_led_color_scales_with_level_and_brightness():
    assert L.led_color(0) == L.OFF_COLOR
    assert L.led_color(9) == L.ON_COLOR
    assert L.led_color(9, 0) == L.OFF_COLOR            # display brightness 0
    mid = L.led_color(5)
    assert _redness(L.OFF_COLOR) < _redness(mid) < _redness(L.ON_COLOR)
    assert L.led_color(99) == L.ON_COLOR and L.led_color(-3) == L.OFF_COLOR
    assert L.led_color(9, 128) != L.ON_COLOR


# --- drawing -----------------------------------------------------------------------

def _draw(sim, scale=1.0, cx=160, cy=130, draw_body=True):
    surf = _canvas()
    lay = L.board_layout(cx, cy, scale)
    R.draw_board(surf, lay, sim, draw_body=draw_body)
    return surf, lay


def test_led_lit_at_nine_is_red_at_its_computed_position_and_dark_elsewhere():
    sim = MicrobitSimulator()
    sim.set_pixel(2, 2, 9)
    surf, lay = _draw(sim)
    lit = _px(surf, lay.led_center(2, 2))
    assert lit == L.ON_COLOR
    assert _px(surf, lay.led_center(0, 0)) == L.OFF_COLOR
    assert _px(surf, lay.led_center(4, 4)) == L.OFF_COLOR


def test_every_led_shows_its_own_brightness_in_place():
    sim = MicrobitSimulator()
    for y in range(5):
        for x in range(5):
            sim.display[y][x] = (x + y) % 10
    surf, lay = _draw(sim)
    for y in range(5):
        for x in range(5):
            assert _px(surf, lay.led_center(x, y)) == L.led_color((x + y) % 10), (x, y)


def test_display_brightness_dims_the_leds():
    sim = MicrobitSimulator()
    sim.set_pixel(1, 3, 9)
    full, lay = _draw(sim)
    sim.set_brightness(64)
    dim, _ = _draw(sim)
    assert _redness(_px(dim, lay.led_center(1, 3))) < _redness(_px(full, lay.led_center(1, 3)))


def test_image_shows_where_the_image_says():
    sim = MicrobitSimulator()
    sim.show_image("HEART")      # row 0 = 09090
    surf, lay = _draw(sim)
    row0 = [_px(surf, lay.led_center(x, 0)) == L.ON_COLOR for x in range(5)]
    assert row0 == [False, True, False, True, False]


def test_pressed_button_changes_colour_at_its_computed_centre():
    sim = MicrobitSimulator()
    up, lay = _draw(sim)
    sim.set_button("a", True)
    down, _ = _draw(sim)
    ax, ay, r = lay.buttons["a"]
    bx, by, _ = lay.buttons["b"]
    # off-centre sample, clear of the letter drawn in the middle
    spot = (ax, ay - r + 4)
    assert _px(up, spot) == R.BUTTON_COLOR
    assert _px(down, spot) == R.BUTTON_DOWN
    assert _px(down, (bx, by - r + 4)) == R.BUTTON_COLOR   # B untouched


def test_logo_and_touched_pin_light_up_in_place():
    sim = MicrobitSimulator()
    idle, lay = _draw(sim)
    sim.set_logo_touched(True)
    sim.set_pin_touched(1, True)
    touched, _ = _draw(sim)
    lx, ly, _, ry = lay.logo
    assert _px(idle, (lx, ly)) == R.LOGO_COLOR
    assert _px(touched, (lx, ly)) == R.LOGO_TOUCHED
    px, py, pw, ph = lay.pads["1"]
    inside = (px + 4, py + ph - 4)
    assert _px(touched, inside) == R.PAD_TOUCHED
    other = lay.pads["2"]
    assert _px(touched, (other[0] + 4, other[1] + other[3] - 4)) == R.PAD_COLOR


def test_board_moves_with_its_centre_and_scales():
    sim = MicrobitSimulator()
    sim.set_pixel(2, 2, 9)
    for cx, cy, scale in ((110, 100, 0.6), (200, 150, 1.0), (160, 130, 1.3)):
        surf = _canvas(400, 320)
        lay = L.board_layout(cx, cy, scale)
        R.draw_board(surf, lay, sim)
        assert _px(surf, lay.led_center(2, 2)) == L.ON_COLOR
        assert _px(surf, (lay.body[0] + 8, lay.body[1] + lay.body[3] // 2)) != BG


def test_body_can_be_left_out_for_a_sprite_board():
    sim = MicrobitSimulator()
    sim.set_pixel(2, 2, 9)
    surf, lay = _draw(sim, draw_body=False)
    bx, by, bw, bh = lay.body
    assert _px(surf, (bx + 6, by + bh // 2)) == BG          # no body
    assert _px(surf, lay.led_center(2, 2)) == L.ON_COLOR    # LEDs still drawn


# --- overlay on a real instance --------------------------------------------------------

def _room_with(instances):
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRoom
    load_all_plugins()
    return GameRoom("r", {"width": 320, "height": 260, "instances": instances},
                    action_executor=None)


def _overlay():
    from runtime.extension_hooks import get_instance_overlays
    return next(f for f in get_instance_overlays()
                if f.__module__ == "pygm_extension_microbit")


def test_overlay_draws_a_board_instance_centred_on_its_position():
    room = _room_with([{"object": "microbit_1", "x": 160, "y": 130}])
    inst = room.instances[0]
    inst.extension_state["microbit"]["simulator"].set_pixel(2, 2, 9)
    surf = _canvas()
    _overlay()(inst, surf)
    lay = L.board_layout(160, 130)
    assert _px(surf, lay.led_center(2, 2)) == L.ON_COLOR


def test_overlay_ignores_other_objects_and_invisible_boards():
    room = _room_with([{"object": "obj_wall", "x": 160, "y": 130},
                       {"object": "microbit_1", "x": 160, "y": 130}])
    wall, board = room.instances
    surf = _canvas()
    _overlay()(wall, surf)
    assert _px(surf, (160, 130)) == BG
    board.visible = False
    _overlay()(board, surf)
    assert _px(surf, (160, 130)) == BG


def test_overlay_honours_the_scale_property_on_the_object_or_instance():
    room = _room_with([{"object": "microbit_1", "x": 160, "y": 130}])
    inst = room.instances[0]
    inst.object_data = {"microbit_scale": 0.5}
    assert R.scale_of(inst) == 0.5
    inst.microbit_scale = 2
    assert R.scale_of(inst) == 2.0
    inst.microbit_scale = "huge"
    assert R.scale_of(inst) == 1.0


def test_sprite_instance_is_centred_on_its_sprite_and_skips_the_body():
    class _Sprite:
        origin_x, origin_y, width, height = 10, 10, 100, 80

    room = _room_with([{"object": "microbit_1", "x": 100, "y": 100}])
    inst = room.instances[0]
    inst.sprite = _Sprite()
    assert R.center_of(inst) == (100 - 10 + 50, 100 - 10 + 40)
    surf = _canvas()
    _overlay()(inst, surf)
    lay = R.layout_for(inst)
    assert _px(surf, (lay.body[0] + 6, lay.body[1] + lay.body[3] // 2)) == BG


def test_real_game_loop_renders_the_board_into_the_window(tmp_path):
    """End to end through GameRunner.run(): the final frame has the lit LED
    at its computed place (PYGM_SCREENSHOT-style, read off the screen)."""
    import json
    from runtime.game_runner import GameRunner
    project = {
        "name": "mb", "version": "1.0",
        "settings": {"window_width": 320, "window_height": 260, "room_speed": 60},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
            "fonts": {}, "data": {},
            "objects": {"microbit_1": {
                "name": "microbit_1", "asset_type": "object", "sprite": "",
                "visible": True, "solid": False,
                "events": {"create": {"actions": [
                    {"action": "microbit_set_pixel",
                     "parameters": {"x": 3, "y": 1, "brightness": 9}}]}}}},
            "rooms": {"room0": {
                "name": "room0", "asset_type": "room", "width": 320, "height": 260,
                "background_color": "#1e3c5a",
                "instances": [{"object": "microbit_1", "x": 160, "y": 130}]}},
        },
    }
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    runner = GameRunner(str(path))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.process_pending_messages = lambda *a, **k: None
    state = {"n": 0, "px": None, "off": None}

    class _FakeClock:
        def tick(self, fps=0):
            state["n"] += 1
            if state["n"] == 10:
                lay = L.board_layout(160, 130)
                state["px"] = _px(runner.screen, lay.led_center(3, 1))
                state["off"] = _px(runner.screen, lay.led_center(0, 4))
            if state["n"] >= 10:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real
    assert state["px"] == L.ON_COLOR
    assert state["off"] == L.OFF_COLOR


def test_drawing_survives_a_pygame_quit_and_reinit():
    """Regression: labels used a cached pygame Font, which dangles after
    pygame.quit() and crashed the whole test process (access violation) the
    next time a game rendered a board. Cached Surfaces are safe."""
    sim = MicrobitSimulator()
    _draw(sim)                     # warms the label cache
    pygame.quit()
    pygame.init()
    surf, lay = _draw(sim)
    assert _px(surf, lay.buttons["a"][:2]) != BG
