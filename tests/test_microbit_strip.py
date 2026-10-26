"""The sensor strip: tilt pad, shake button and sliders
(docs/MICROBIT_EXTENSION_PLAN.md, Stage S7).

Pure geometry/mapping tests, pixel tests at computed positions, hook-level
drag tests, and real ``GameRunner.run()`` loops where dragging the tilt pad
fires ``microbit_gesture_tilt_left`` and a slider fires ``microbit_loud_sound``.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()

from extensions.microbit import layout as L  # noqa: E402
from extensions.microbit import renderer as R  # noqa: E402
from extensions.microbit.simulator import MicrobitSimulator, REST_ACCELERATION  # noqa: E402

BG = (30, 60, 90)


def _px(surf, pos):
    return tuple(surf.get_at(pos))[:3]


def _center(rect):
    x, y, w, h = rect
    return x + w // 2, y + h // 2


# --- geometry / mappings (pure) ------------------------------------------------------------

def test_tilt_flanks_the_board_on_the_left_the_rest_on_the_right():
    board = L.board_layout(200, 150)
    strip = L.strip_layout(board)

    lx, ly, lw, lh = strip.panel_left
    assert lx + lw <= board.body[0] - L.STRIP_GAP + 1          # left of the body, gapped
    inside_left = lambda r: (lx <= r[0] and ly <= r[1]         # noqa: E731
                             and r[0] + r[2] <= lx + lw and r[1] + r[3] <= ly + lh)
    assert inside_left(strip.tilt)

    rx, ry, rw, rh = strip.panel_right
    assert rx >= board.body[0] + board.body[2] + L.STRIP_GAP - 1  # right of the body, gapped
    inside_right = lambda r: (rx <= r[0] and ry <= r[1]        # noqa: E731
                              and r[0] + r[2] <= rx + rw and r[1] + r[3] <= ry + rh)
    assert inside_right(strip.shake)
    assert all(inside_right(t) for t in strip.sliders.values())
    assert list(strip.sliders) == ["light", "temperature", "compass", "sound"]


def test_the_two_panels_are_gapped_from_the_board_and_do_not_overlap_it():
    board = L.board_layout(200, 150)
    strip = L.strip_layout(board)
    bx, by, bw, bh = board.body
    lx, ly, lw, lh = strip.panel_left
    rx, ry, rw, rh = strip.panel_right
    assert lx + lw < bx and rx > bx + bw                       # strictly clear, not touching
    assert bx - (lx + lw) >= L.STRIP_GAP - 1
    assert rx - (bx + bw) >= L.STRIP_GAP - 1


def test_strip_controls_do_not_overlap():
    strip = L.strip_layout(L.board_layout(200, 150))
    rects = [strip.tilt, strip.shake, *strip.sliders.values()]
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            apart = (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0]
                     or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])
            assert apart, (a, b)


def test_strip_scales_with_the_board():
    a = L.strip_layout(L.board_layout(100, 100, 1.0))
    b = L.strip_layout(L.board_layout(100, 100, 2.0))
    assert b.tilt[2] == 2 * a.tilt[2]
    assert b.panel_left[3] == 2 * a.panel_left[3]
    assert b.panel_right[3] == 2 * a.panel_right[3]


def test_tilt_pad_centre_is_rest_and_edges_are_one_g():
    rect = L.strip_layout(L.board_layout(200, 150)).tilt
    x, y, w, h = rect
    assert L.tilt_from_pos(rect, *_center(rect)) == REST_ACCELERATION
    assert L.tilt_from_pos(rect, x, y + h // 2) == (-1024, 0, 0)        # left edge
    assert L.tilt_from_pos(rect, x + w, y + h // 2) == (1024, 0, 0)     # right edge
    assert L.tilt_from_pos(rect, x + w // 2, y) == (0, 1024, 0)         # top = logo up
    assert L.tilt_from_pos(rect, x + w // 2, y + h) == (0, -1024, 0)


def test_tilt_pad_corners_and_outside_stay_within_one_g():
    rect = L.strip_layout(L.board_layout(200, 150)).tilt
    for pos in ((rect[0], rect[1]), (rect[0] - 500, rect[1] + 9999)):
        ax, ay, az = L.tilt_from_pos(rect, *pos)
        assert (ax * ax + ay * ay + az * az) ** 0.5 <= 1025


def test_tilt_pad_edges_trigger_the_real_gesture_algorithm():
    rect = L.strip_layout(L.board_layout(200, 150)).tilt
    for pos, gesture in (((rect[0], rect[1] + 50), "left"),
                         ((rect[0] + 100, rect[1] + 50), "right"),
                         ((rect[0] + 50, rect[1]), "up"),
                         ((rect[0] + 50, rect[1] + 100), "down")):
        sim = MicrobitSimulator()
        sim.set_acceleration(*L.tilt_from_pos(rect, *pos))
        events = []
        for _ in range(20):
            events += sim.update(0.02)
        assert ("gesture", gesture) in events, gesture


def test_tilt_to_pos_inverts_tilt_from_pos():
    rect = L.strip_layout(L.board_layout(200, 150)).tilt
    x, y, w, h = rect
    for pos in ((x + 22, y + 39), (x + 52, y + 49), (x + 22, y + 24), (x + 82, y + 79)):
        ax, ay, _ = L.tilt_from_pos(rect, *pos)
        back = L.tilt_to_pos(rect, ax, ay)
        assert abs(back[0] - pos[0]) <= 1 and abs(back[1] - pos[1]) <= 1


def test_slider_value_maps_the_track_to_the_range_and_clamps():
    strip = L.strip_layout(L.board_layout(200, 150))
    for name, (lo, hi) in L.SLIDERS.items():
        tx, ty, tw, th = strip.sliders[name]
        assert L.slider_value(name, strip.sliders[name], tx) == lo
        assert L.slider_value(name, strip.sliders[name], tx + tw) == hi
        assert L.slider_value(name, strip.sliders[name], tx - 50) == lo
        assert L.slider_value(name, strip.sliders[name], tx + tw + 50) == hi
        mid = L.slider_value(name, strip.sliders[name], tx + tw // 2)
        assert lo < mid < hi
        assert L.slider_fraction(name, lo) == 0 and L.slider_fraction(name, hi) == 1


def test_strip_hit_test_finds_each_control():
    strip = L.strip_layout(L.board_layout(200, 150))
    assert L.strip_hit_test(strip, *_center(strip.tilt)) == "tilt"
    assert L.strip_hit_test(strip, *_center(strip.shake)) == "shake"
    for name, track in strip.sliders.items():
        assert L.strip_hit_test(strip, *_center(track)) == f"slider:{name}"
    assert L.strip_hit_test(strip, strip.panel_left[0] + 1, strip.panel_left[1] + 1) is None
    assert L.strip_hit_test(strip, 5, 5) is None


def test_strip_visible_option():
    class I:
        object_data = {}
    inst = I()
    assert L.strip_visible(inst) is True
    inst.object_data = {"microbit_show_sensors": False}
    assert L.strip_visible(inst) is False
    inst.microbit_show_sensors = "true"
    assert L.strip_visible(inst) is True
    inst.microbit_show_sensors = "false"
    assert L.strip_visible(inst) is False


# --- drawing ----------------------------------------------------------------------------------

def _draw(sim, cx=300, cy=160):
    surf = pygame.Surface((650, 320))
    surf.fill(BG)
    board = L.board_layout(cx, cy)
    strip = L.strip_layout(board)
    R.draw_strip(surf, strip, sim, board.scale)
    return surf, strip


def test_tilt_dot_is_drawn_where_the_acceleration_says():
    sim = MicrobitSimulator()
    surf, strip = _draw(sim)
    assert _px(surf, L.tilt_to_pos(strip.tilt, 0, 0)) == R.PAD_DOT     # at rest: centre
    sim.set_acceleration(-1024, 0, 0)
    surf, strip = _draw(sim)
    assert _px(surf, L.tilt_to_pos(strip.tilt, -1024, 0)) == R.PAD_DOT
    assert _px(surf, (strip.tilt[0] + strip.tilt[2] - 8, strip.tilt[1] + 30)) == R.PAD_WELL


def test_slider_knob_and_fill_follow_the_value():
    sim = MicrobitSimulator()
    sim.set_light_level(255)
    sim.set_sound_level(0)
    surf, strip = _draw(sim)
    lx, ly, lw, lh = strip.sliders["light"]
    sx, sy, sw, sh = strip.sliders["sound"]
    assert _px(surf, (lx + lw // 2, ly + lh // 2)) == R.TRACK_FILL     # filled to the end
    assert _px(surf, (sx + sw // 2, sy + sh // 2)) == R.TRACK_COLOR    # empty


def test_shake_button_lights_while_shaking():
    sim = MicrobitSimulator()
    idle, strip = _draw(sim)
    sim.shake()
    sx, sy, sw, sh = strip.shake
    spot = (sx + 4, sy + 3)
    assert _px(idle, spot) == R.SHAKE_COLOR
    shaking, _ = _draw(sim)
    assert _px(shaking, spot) == R.SHAKE_ACTIVE


def test_overlay_draws_the_strip_unless_switched_off():
    from events.plugin_loader import load_all_plugins
    from runtime.extension_hooks import get_instance_overlays
    from runtime.game_runner import GameRoom
    load_all_plugins()
    overlay = next(f for f in get_instance_overlays()
                   if f.__module__ == "pygm_extension_microbit")
    room = GameRoom("r", {"width": 650, "height": 320, "instances": [
        {"object": "microbit_1", "x": 300, "y": 160}]}, action_executor=None)
    inst = room.instances[0]
    strip = L.strip_layout(L.board_layout(300, 160))
    spot = (strip.shake[0] + 4, strip.shake[1] + 3)

    surf = pygame.Surface((650, 320))
    surf.fill(BG)
    overlay(inst, surf)
    assert _px(surf, spot) == R.SHAKE_COLOR

    inst.microbit_show_sensors = False
    surf.fill(BG)
    overlay(inst, surf)
    assert _px(surf, spot) == BG


# --- the hook ----------------------------------------------------------------------------------

def _hooks():
    from runtime.extension_hooks import get_input_handlers
    return next(h for h in get_input_handlers()
                if h["mouse_down"].__module__ == "pygm_extension_microbit.input")


def _board_room():
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRoom
    load_all_plugins()
    room = GameRoom("r", {"width": 320, "height": 400, "instances": [
        {"object": "microbit_1", "x": 160, "y": 110}]}, action_executor=None)

    class Runner:
        current_room = room
    return Runner, room.instances[0]


def _sim(inst):
    return inst.extension_state["microbit"]["simulator"]


def _input_module():
    return _hooks()["mouse_down"].__globals__


def test_shake_button_click_shakes():
    runner, inst = _board_room()
    strip = L.strip_layout(L.board_layout(160, 110))
    h = _hooks()
    assert h["mouse_down"](runner, 1, *_center(strip.shake)) is True
    assert ("gesture", "shake") in _sim(inst).update(0.02)
    h["mouse_up"](runner, 1, 0, 0)


def test_pressing_the_tilt_pad_tilts_and_release_springs_back():
    runner, inst = _board_room()
    strip = L.strip_layout(L.board_layout(160, 110))
    h = _hooks()
    x, y, w, hgt = strip.tilt
    h["mouse_down"](runner, 1, x, y + hgt // 2)
    assert _sim(inst).acceleration == (-1024, 0, 0)
    h["mouse_up"](runner, 1, 0, 0)
    assert _sim(inst).acceleration == REST_ACCELERATION


def test_pressing_a_slider_sets_that_sensor_and_it_stays_after_release():
    runner, inst = _board_room()
    strip = L.strip_layout(L.board_layout(160, 110))
    h = _hooks()
    sim = _sim(inst)
    for name, setter_attr, hi in (("light", "light_level", 255),
                                  ("temperature", "temperature", 50),
                                  ("compass", "compass_heading", 359 % 360),
                                  ("sound", "sound_level", 255)):
        tx, ty, tw, th = strip.sliders[name]
        h["mouse_down"](runner, 1, tx + tw, ty + th // 2)
        h["mouse_up"](runner, 1, 0, 0)
        assert getattr(sim, setter_attr) == hi, name


def test_drag_follows_the_pointer_through_follow():
    runner, inst = _board_room()
    strip = L.strip_layout(L.board_layout(160, 110))
    h = _hooks()
    mod = _input_module()
    sim = _sim(inst)
    tx, ty, tw, th = strip.sliders["light"]
    h["mouse_down"](runner, 1, tx, ty + 2)
    assert sim.light_level == 0
    assert mod["drags"]() == [(inst, "slider:light")]
    mod["follow"](tx + tw // 2, 0)                  # pointer moved; y is ignored
    assert 100 < sim.light_level < 156
    mod["follow"](tx + tw + 99, 0)
    assert sim.light_level == 255
    h["mouse_up"](runner, 1, 0, 0)
    assert mod["drags"]() == []
    mod["follow"](tx, 0)                            # no drag: nothing moves
    assert sim.light_level == 255


def test_right_click_on_the_strip_does_nothing_and_falls_through():
    runner, inst = _board_room()
    strip = L.strip_layout(L.board_layout(160, 110))
    assert _hooks()["mouse_down"](runner, 3, *_center(strip.shake)) is False


def test_hidden_strip_cannot_be_clicked():
    runner, inst = _board_room()
    inst.microbit_show_sensors = False
    strip = L.strip_layout(L.board_layout(160, 110))
    assert _hooks()["mouse_down"](runner, 1, *_center(strip.shake)) is False


# --- real game loop ---------------------------------------------------------------------------------

def _act(action, **params):
    return {"action": action, "parameters": params}


def _write_project(tmp_path, events):
    project = {
        "name": "mb", "version": "1.0",
        "settings": {"window_width": 320, "window_height": 400, "room_speed": 60},
        "assets": {"sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
                   "fonts": {}, "data": {},
                   "objects": {"microbit_1": {
                       "name": "microbit_1", "asset_type": "object", "sprite": "",
                       "visible": True, "solid": False, "events": events}},
                   "rooms": {"room0": {
                       "name": "room0", "asset_type": "room", "width": 320,
                       "height": 400, "background_color": "#000000",
                       "instances": [{"object": "microbit_1", "x": 160, "y": 110}]}}},
    }
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    return str(path)


def _run(project_json, script, frames=40):
    from runtime.game_runner import GameRunner
    runner = GameRunner(project_json)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.process_pending_messages = lambda *a, **k: None
    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            state["frames"] += 1
            if runner.current_room is not None:
                script(state["frames"], runner)
            if state["frames"] >= frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        assert runner.run() is not False, "game loop reported a fatal crash"
    finally:
        pygame.time.Clock = real
    return runner


def _sim_of_runner(runner):
    inst = next(i for i in runner.current_room.instances if i.object_name == "microbit_1")
    return _sim(inst)


def test_dragging_the_tilt_pad_fires_the_tilt_event_then_release_rests(tmp_path, monkeypatch):
    project = _write_project(tmp_path, {
        "microbit_gesture_tilt_left": {"actions": [_act("microbit_set_pixel", x=0, y=0)]}})
    strip = L.strip_layout(L.board_layout(160, 110))
    x, y, w, h = strip.tilt
    left_edge = (x, y + h // 2)
    pointer = {"pos": (0, 0)}
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: pointer["pos"])
    seen = {}

    def script(frame, runner):
        sim = _sim_of_runner(runner)
        if frame == 3:
            pointer["pos"] = _center(strip.tilt)
            pygame.event.post(pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=_center(strip.tilt)))
        if frame == 6:
            pointer["pos"] = left_edge           # the drag moves; no event posted
        if frame == 25:
            seen["pixel"] = sim.get_pixel(0, 0)
            seen["accel"] = sim.acceleration
            pygame.event.post(pygame.event.Event(
                pygame.MOUSEBUTTONUP, button=1, pos=left_edge))
        if frame == 30:
            seen["rested"] = sim.acceleration

    _run(project, script)
    assert seen["pixel"] == 9                    # tilt_left fired in the real loop
    assert seen["accel"] == (-1024, 0, 0)
    assert seen["rested"] == REST_ACCELERATION


def test_dragging_the_sound_slider_fires_loud_then_quiet(tmp_path, monkeypatch):
    project = _write_project(tmp_path, {
        "microbit_loud_sound": {"actions": [_act("microbit_set_pixel", x=0, y=0)]},
        "microbit_quiet_sound": {"actions": [_act("microbit_set_pixel", x=1, y=0)]}})
    strip = L.strip_layout(L.board_layout(160, 110))
    tx, ty, tw, th = strip.sliders["sound"]
    pointer = {"pos": (tx, ty + 2)}
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: pointer["pos"])
    seen = {}

    def script(frame, runner):
        sim = _sim_of_runner(runner)
        if frame == 3:
            pygame.event.post(pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(tx, ty + 2)))
        if frame == 5:
            pointer["pos"] = (tx + tw, ty + 2)           # drag to the loud end
        if frame == 10:
            seen["loud"] = sim.get_pixel(0, 0)
            pointer["pos"] = (tx, ty + 2)                # and back to silence
        if frame == 16:
            seen["quiet"] = sim.get_pixel(1, 0)
            pygame.event.post(pygame.event.Event(
                pygame.MOUSEBUTTONUP, button=1, pos=(tx, ty + 2)))

    _run(project, script, frames=24)
    assert seen["loud"] == 9 and seen["quiet"] == 9


def test_clicking_shake_in_the_real_loop_fires_the_shake_event(tmp_path):
    project = _write_project(tmp_path, {
        "microbit_gesture_shake": {"actions": [_act("microbit_set_pixel", x=2, y=2)]}})
    strip = L.strip_layout(L.board_layout(160, 110))
    seen = {}

    def script(frame, runner):
        if frame == 3:
            pos = _center(strip.shake)
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos))
        if frame == 8:
            seen["px"] = _sim_of_runner(runner).get_pixel(2, 2)

    _run(project, script)
    assert seen["px"] == 9
