"""Mouse and keyboard control of the drawn micro:bit
(docs/MICROBIT_EXTENSION_PLAN.md, Stage S6).

Click-at-computed-rect tests, then real ``GameRunner.run()`` loops with
posted pygame events: a click on A fires ``microbit_button_a`` and is
swallowed (no authored mouse event), a click elsewhere is not; the keyboard
shortcuts do nothing unless the object opts in, and an authored
``keyboard_press`` A event still fires with them off.
"""
import ast
import json
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


# --- hit-testing (pure) ----------------------------------------------------------------

def test_input_and_layout_modules_are_pygame_free():
    for fname in ("input.py", "layout.py", "state.py"):
        tree = ast.parse((EXT_DIR / fname).read_text(encoding="utf-8"))
        mods = {n.module.split(".")[0] for n in ast.walk(tree)
                if isinstance(n, ast.ImportFrom) and n.module and not n.level}
        mods |= {a.name.split(".")[0] for n in ast.walk(tree)
                 if isinstance(n, ast.Import) for a in n.names}
        assert not mods & {"pygame", "PySide6"}, fname


def test_hit_test_finds_every_control_at_its_computed_position():
    lay = L.board_layout(200, 150)
    assert L.hit_test(lay, *lay.buttons["a"][:2]) == "a"
    assert L.hit_test(lay, *lay.buttons["b"][:2]) == "b"
    assert L.hit_test(lay, *lay.logo[:2]) == "logo"
    for pin in (0, 1, 2):
        x, y, w, h = lay.pads[str(pin)]
        assert L.hit_test(lay, x + w // 2, y + h // 2) == f"pin{pin}"


def test_hit_test_misses_the_rest_of_the_board_and_the_non_touch_pads():
    lay = L.board_layout(200, 150)
    assert L.hit_test(lay, *lay.led_center(2, 2)) is None        # the LEDs
    assert L.hit_test(lay, 5, 5) is None                          # off the board
    for name in ("3V", "GND"):
        x, y, w, h = lay.pads[name]
        assert L.hit_test(lay, x + w // 2, y + h // 2) is None
    ax, ay, r = lay.buttons["a"]
    assert L.hit_test(lay, ax + r + 2, ay) is None                # just outside A
    assert L.hit_test(lay, ax + r - 2, ay) == "a"                 # just inside


def test_hit_test_follows_scale_and_position():
    for cx, cy, scale in ((100, 90, 0.5), (300, 200, 1.7)):
        lay = L.board_layout(cx, cy, scale)
        assert L.hit_test(lay, *lay.buttons["b"][:2]) == "b"


# --- the hook, called directly --------------------------------------------------------------

def _room_with(instances):
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRoom
    load_all_plugins()
    return GameRoom("r", {"width": 400, "height": 300, "instances": instances},
                    action_executor=None)


def _hooks():
    """The LOADED extension's input handlers (the loader imports it under a
    synthetic package, so importing the module directly would be a copy)."""
    from runtime.extension_hooks import get_input_handlers
    return next(h for h in get_input_handlers()
                if h["mouse_down"].__module__ == "pygm_extension_microbit.input")


class _Runner:
    def __init__(self, room):
        self.current_room = room


def _sim(inst):
    return inst.extension_state["microbit"]["simulator"]


@pytest.fixture
def one_board():
    room = _room_with([{"object": "microbit_1", "x": 200, "y": 150}])
    return _Runner(room), room.instances[0], _hooks()


def test_left_click_presses_and_release_lets_go(one_board):
    runner, inst, h = one_board
    lay = L.board_layout(200, 150)
    pos = lay.buttons["a"][:2]
    assert h["mouse_down"](runner, 1, *pos) is True        # swallowed
    assert _sim(inst).buttons == {"a": True, "b": False}
    assert h["mouse_up"](runner, 1, *pos) is True
    assert _sim(inst).buttons == {"a": False, "b": False}


def test_click_off_the_board_is_not_swallowed(one_board):
    runner, inst, h = one_board
    assert h["mouse_down"](runner, 1, 5, 5) is False
    assert h["mouse_up"](runner, 1, 5, 5) is False


def test_click_on_a_non_control_part_of_the_board_is_not_swallowed(one_board):
    runner, inst, h = one_board
    lay = L.board_layout(200, 150)
    assert h["mouse_down"](runner, 1, *lay.led_center(1, 1)) is False


def test_logo_and_pins_are_held_while_the_mouse_is_down(one_board):
    runner, inst, h = one_board
    lay = L.board_layout(200, 150)
    sim = _sim(inst)
    h["mouse_down"](runner, 1, *lay.logo[:2])
    assert sim.logo_touched is True
    h["mouse_up"](runner, 1, 0, 0)
    assert sim.logo_touched is False
    x, y, w, ph = lay.pads["2"]
    h["mouse_down"](runner, 1, x + 3, y + 3)
    assert sim.pins_touched[2] is True
    h["mouse_up"](runner, 1, 0, 0)
    assert sim.pins_touched[2] is False


def test_right_click_on_either_button_presses_the_ab_chord(one_board):
    runner, inst, h = one_board
    lay = L.board_layout(200, 150)
    sim = _sim(inst)
    assert h["mouse_down"](runner, 3, *lay.buttons["b"][:2]) is True
    assert sim.buttons == {"a": True, "b": True}
    events = sim.update(0.02)
    assert ("button", "ab") in events
    h["mouse_up"](runner, 3, 0, 0)
    assert sim.buttons == {"a": False, "b": False}


def test_right_click_on_logo_does_nothing_but_is_still_the_boards(one_board):
    runner, inst, h = one_board
    lay = L.board_layout(200, 150)
    assert h["mouse_down"](runner, 3, *lay.logo[:2]) is True
    assert _sim(inst).logo_touched is False


def test_other_mouse_buttons_are_ignored(one_board):
    runner, inst, h = one_board
    lay = L.board_layout(200, 150)
    assert h["mouse_down"](runner, 2, *lay.buttons["a"][:2]) is False
    assert h["mouse_down"](runner, 4, *lay.buttons["a"][:2]) is False
    assert _sim(inst).buttons["a"] is False


def test_a_lost_release_does_not_leave_a_button_stuck(one_board):
    runner, inst, h = one_board
    lay = L.board_layout(200, 150)
    h["mouse_down"](runner, 1, *lay.buttons["a"][:2])
    h["mouse_down"](runner, 1, *lay.buttons["b"][:2])      # no release between
    assert _sim(inst).buttons == {"a": False, "b": True}
    h["mouse_up"](runner, 1, 0, 0)
    assert _sim(inst).buttons == {"a": False, "b": False}


def test_topmost_board_wins_where_two_overlap():
    room = _room_with([{"object": "microbit_1", "x": 200, "y": 150},
                       {"object": "microbit_2", "x": 200, "y": 150}])
    low, high = room.instances
    h = _hooks()
    lay = L.board_layout(200, 150)
    h["mouse_down"](_Runner(room), 1, *lay.buttons["a"][:2])
    assert _sim(high).buttons["a"] is True and _sim(low).buttons["a"] is False
    h["mouse_up"](_Runner(room), 1, 0, 0)


def test_two_separate_boards_are_clicked_independently():
    room = _room_with([{"object": "microbit_1", "x": 120, "y": 150},
                       {"object": "microbit_2", "x": 520, "y": 150}])
    left, right = room.instances
    h = _hooks()
    h["mouse_down"](_Runner(room), 1, *L.board_layout(520, 150).buttons["b"][:2])
    assert _sim(right).buttons["b"] is True and _sim(left).buttons["b"] is False


def test_invisible_boards_cannot_be_clicked(one_board):
    runner, inst, h = one_board
    inst.visible = False
    lay = L.board_layout(200, 150)
    assert h["mouse_down"](runner, 1, *lay.buttons["a"][:2]) is False


def test_scaled_board_hit_test_uses_its_scale(one_board):
    runner, inst, h = one_board
    inst.microbit_scale = 2.0
    lay2 = L.board_layout(200, 150, 2.0)
    assert h["mouse_down"](runner, 1, *lay2.buttons["b"][:2]) is True
    assert _sim(inst).buttons["b"] is True


# --- keyboard (direct) -------------------------------------------------------------------------

def test_keyboard_is_off_by_default_and_on_by_option():
    room = _room_with([{"object": "microbit_1", "x": 0, "y": 0}])
    inst = room.instances[0]
    h = _hooks()
    assert h["key_down"](inst, "a") is False
    assert _sim(inst).buttons["a"] is False
    inst.microbit_keyboard = True
    assert h["key_down"](inst, "a") is True
    assert _sim(inst).buttons["a"] is True
    h["key_up"](inst, "a")
    assert _sim(inst).buttons["a"] is False
    assert h["key_down"](inst, "q") is False       # not a micro:bit key


def test_keyboard_option_can_come_from_the_object_and_as_text():
    room = _room_with([{"object": "microbit_1", "x": 0, "y": 0}])
    inst = room.instances[0]
    h = _hooks()
    inst.object_data = {"microbit_keyboard": "true"}
    assert h["key_down"](inst, "b") is True
    inst.object_data = {"microbit_keyboard": "false"}
    assert h["key_down"](inst, "a") is False


def test_arrow_keys_tilt_and_release_returns_to_rest():
    from extensions.microbit.simulator import REST_ACCELERATION
    room = _room_with([{"object": "microbit_1", "x": 0, "y": 0}])
    inst = room.instances[0]
    inst.microbit_keyboard = True
    h = _hooks()
    sim = _sim(inst)
    h["key_down"](inst, "left")
    assert sim.acceleration == (-1000, 0, 0)
    h["key_down"](inst, "up")
    assert sim.acceleration == (-1000, 1000, 0)
    h["key_up"](inst, "left")
    assert sim.acceleration == (0, 1000, 0)
    h["key_up"](inst, "up")
    assert sim.acceleration == REST_ACCELERATION
    h["key_down"](inst, "left")
    h["key_down"](inst, "right")                  # opposite keys cancel
    assert sim.acceleration == REST_ACCELERATION


def test_s_key_shakes():
    room = _room_with([{"object": "microbit_1", "x": 0, "y": 0}])
    inst = room.instances[0]
    inst.microbit_keyboard = True
    _hooks()["key_down"](inst, "s")
    assert ("gesture", "shake") in _sim(inst).update(0.02)


# --- real game loop --------------------------------------------------------------------------------

def _act(action, **params):
    return {"action": action, "parameters": params}


def _write_project(tmp_path, board_events, keyboard=False, other_events=None):
    board = {"name": "microbit_1", "asset_type": "object", "sprite": "",
             "visible": True, "solid": False, "events": board_events}
    if keyboard:
        board["microbit_keyboard"] = True
    objects = {"microbit_1": board}
    instances = [{"object": "microbit_1", "x": 200, "y": 150}]
    if other_events is not None:
        objects["obj_ctrl"] = {"name": "obj_ctrl", "asset_type": "object",
                               "sprite": "", "visible": True, "solid": False,
                               "events": other_events}
        instances.append({"object": "obj_ctrl", "x": 0, "y": 0})
    project = {
        "name": "mb", "version": "1.0",
        "settings": {"window_width": 400, "window_height": 300, "room_speed": 60},
        "assets": {"sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
                   "fonts": {}, "data": {}, "objects": objects,
                   "rooms": {"room0": {
                       "name": "room0", "asset_type": "room", "width": 400,
                       "height": 300, "background_color": "#000000",
                       "instances": instances}}},
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


def _post_click(pos, button=1):
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=button, pos=pos))
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, button=button, pos=pos))


def _board(runner):
    inst = next(i for i in runner.current_room.instances if i.object_name == "microbit_1")
    return inst, _sim(inst)


def test_clicking_a_fires_its_event_and_the_click_is_swallowed(tmp_path):
    project = _write_project(
        tmp_path,
        {"microbit_button_a": {"actions": [_act("microbit_show_image", image="HEART")]}},
        other_events={"mouse_left_button": {"actions": [
            _act("set_variable", variable="clicked", value="1")]}})
    lay = L.board_layout(200, 150)
    seen = {}

    def script(frame, runner):
        if frame == 3:
            _post_click(lay.buttons["a"][:2])
        if frame == 10:
            _, sim = _board(runner)
            seen["row0"] = list(sim.display[0])
            ctrl = next(i for i in runner.current_room.instances
                        if i.object_name == "obj_ctrl")
            seen["clicked"] = getattr(ctrl, "clicked", None)

    _run(project, script)
    assert seen["row0"] == [0, 9, 0, 9, 0]
    assert seen["clicked"] is None            # swallowed: no authored mouse event


def test_clicking_elsewhere_still_reaches_authored_mouse_events(tmp_path):
    project = _write_project(
        tmp_path, {},
        other_events={"mouse_left_button": {"actions": [
            _act("set_variable", variable="clicked", value="1")]}})
    seen = {}

    def script(frame, runner):
        if frame == 3:
            _post_click((10, 10))
        if frame == 8:
            ctrl = next(i for i in runner.current_room.instances
                        if i.object_name == "obj_ctrl")
            seen["clicked"] = getattr(ctrl, "clicked", None)

    _run(project, script)
    assert seen["clicked"] in (1, "1")


def test_quick_click_still_registers_a_press(tmp_path):
    """Down and up posted in the same frame: the press is state-only, so the
    event must still fire from the simulator's queued report."""
    project = _write_project(
        tmp_path,
        {"microbit_button_b": {"actions": [_act("microbit_set_pixel", x=0, y=0)]}})
    lay = L.board_layout(200, 150)
    seen = {}

    def script(frame, runner):
        if frame == 3:
            _post_click(lay.buttons["b"][:2])
        if frame == 8:
            seen["px"] = _board(runner)[1].get_pixel(0, 0)

    _run(project, script)
    assert seen["px"] == 9


def test_keyboard_off_ignores_keys_but_authored_events_still_fire(tmp_path):
    project = _write_project(
        tmp_path,
        {"microbit_button_a": {"actions": [_act("microbit_set_pixel", x=0, y=0)]},
         "keyboard_press": {"a": {"actions": [_act("microbit_set_pixel", x=4, y=4)]}}})
    seen = {}

    def script(frame, runner):
        if frame == 3:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
        if frame == 10:
            sim = _board(runner)[1]
            seen["authored"] = sim.get_pixel(4, 4)
            seen["microbit"] = sim.get_pixel(0, 0)

    _run(project, script)
    assert seen["authored"] == 9      # the author's own keyboard_press A ran
    assert seen["microbit"] == 0      # the micro:bit ignored the key


def test_keyboard_on_drives_buttons_tilt_and_shake_through_events(tmp_path):
    project = _write_project(
        tmp_path,
        {"microbit_button_a": {"actions": [_act("microbit_set_pixel", x=0, y=0)]},
         "microbit_gesture_tilt_left": {"actions": [_act("microbit_set_pixel", x=1, y=0)]},
         "microbit_gesture_shake": {"actions": [_act("microbit_set_pixel", x=2, y=0)]}},
        keyboard=True)
    seen = {}

    def script(frame, runner):
        if frame == 3:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
        if frame == 30:
            row = _board(runner)[1].display[0]
            seen["row"] = list(row[:3])

    _run(project, script)
    assert seen["row"] == [9, 9, 9]
