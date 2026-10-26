"""micro:bit radio (docs/MICROBIT_EXTENSION_PLAN.md, Stage S9).

Pure delivery rules, the actions, and a real ``GameRunner.run()`` room with
three boards: A's button sends 7, B (same group) receives it, A doesn't hear
itself, and C (a different group) hears nothing.
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

from extensions.microbit import radio
from extensions.microbit.simulator import MicrobitSimulator, MAX_RADIO_OUTBOX


def _radio_events(sim):
    return [d for k, d in sim.update(0.02) if k == "radio"]


# --- pure ----------------------------------------------------------------------------------

def test_radio_module_is_pure():
    tree = ast.parse((EXT_DIR / "radio.py").read_text(encoding="utf-8"))
    mods = {n.module.split(".")[0] for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom) and n.module and not n.level}
    mods |= {a.name.split(".")[0] for n in ast.walk(tree)
             if isinstance(n, ast.Import) for a in n.names}
    assert not mods & {"pygame", "PySide6"}


def test_group_is_clamped_to_0_255():
    assert radio.clamp_group(5) == 5
    assert radio.clamp_group("12") == 12
    assert radio.clamp_group(-3) == 0 and radio.clamp_group(9999) == 255
    assert radio.clamp_group("nope") == 0 and radio.clamp_group(None) == 0


def test_messages_stay_numbers_or_become_short_text():
    assert radio.clean_message(7) == 7 and radio.clean_message(2.5) == 2.5
    assert radio.clean_message(True) == 1
    assert radio.clean_message("hello") == "hello"
    assert radio.clean_message("x" * 100) == "x" * radio.MAX_MESSAGE
    assert radio.clean_message([1, 2]) == "[1, 2]"


def test_as_number_reads_numbers_and_numeric_text():
    assert radio.as_number(7) == 7 and radio.as_number(2.5) == 2.5
    assert radio.as_number("42") == 42 and isinstance(radio.as_number("42"), int)
    assert radio.as_number("2.5") == 2.5
    assert radio.as_number("hello") == 0 and radio.as_number("") == 0


def test_deliver_reaches_others_in_the_group_but_not_the_sender():
    a, b, c = MicrobitSimulator(), MicrobitSimulator(), MicrobitSimulator()
    a.radio_send(7)
    assert radio.deliver([a, b, c]) == 2
    assert _radio_events(b) == [7] and _radio_events(c) == [7]
    assert _radio_events(a) == []                       # never hears itself


def test_a_different_group_hears_nothing():
    a, b, c = MicrobitSimulator(), MicrobitSimulator(), MicrobitSimulator()
    c.set_radio_group(5)
    a.radio_send("hi")
    radio.deliver([a, b, c])
    assert _radio_events(b) == ["hi"]
    assert _radio_events(c) == []
    c.radio_send("psst")
    radio.deliver([a, b, c])
    assert _radio_events(a) == [] and _radio_events(b) == []


def test_changing_group_changes_who_hears():
    a, b = MicrobitSimulator(), MicrobitSimulator()
    a.set_radio_group(3)
    a.radio_send(1)
    radio.deliver([a, b])
    assert _radio_events(b) == []
    b.set_radio_group(3)
    a.radio_send(2)
    radio.deliver([a, b])
    assert _radio_events(b) == [2]


def test_messages_arrive_in_order_and_each_is_delivered_once():
    a, b = MicrobitSimulator(), MicrobitSimulator()
    for n in (1, 2, 3):
        a.radio_send(n)
    radio.deliver([a, b])
    assert _radio_events(b) == [1, 2, 3]
    radio.deliver([a, b])                               # outbox was emptied
    assert _radio_events(b) == []


def test_everyone_in_the_group_can_talk_to_everyone_else():
    boards = [MicrobitSimulator() for _ in range(3)]
    for i, board in enumerate(boards):
        board.radio_send(i)
    radio.deliver(boards)
    got = [sorted(_radio_events(b)) for b in boards]
    assert got == [[1, 2], [0, 2], [0, 1]]


def test_outbox_is_capped():
    a = MicrobitSimulator()
    sent = [a.radio_send(n) for n in range(MAX_RADIO_OUTBOX + 5)]
    assert sent.count(True) == MAX_RADIO_OUTBOX and sent[-1] is False


def test_a_lone_board_talks_to_nobody():
    a = MicrobitSimulator()
    a.radio_send(1)
    assert radio.deliver([a]) == 0
    assert radio.deliver([]) == 0


# --- actions ---------------------------------------------------------------------------------

def _two_boards():
    from events.plugin_loader import load_all_plugins
    from runtime.action_executor import ActionExecutor
    from runtime.game_runner import GameRoom

    class GR:
        class _R:
            instances = []
            extension_state = {}
        current_room = _R()
        global_variables = {}

    ex = ActionExecutor(game_runner=GR())
    load_all_plugins(ex)
    room = GameRoom("r", {"width": 100, "height": 100, "instances": [
        {"object": "microbit_a", "x": 0, "y": 0},
        {"object": "microbit_b", "x": 50, "y": 0}]}, action_executor=None)
    for inst in room.instances:
        inst.action_executor = ex
    sims = [i.extension_state["microbit"]["simulator"] for i in room.instances]
    return ex, room.instances, sims


def _do(ex, inst, name, **params):
    return ex.action_handlers[name](inst, params)


def test_set_group_action_clamps_and_sends_use_the_boards_group():
    ex, (a, b), (sa, sb) = _two_boards()
    _do(ex, a, "microbit_radio_set_group", group=999)
    assert sa.radio_group == 255
    _do(ex, a, "microbit_radio_set_group", group="2 + 1")
    assert sa.radio_group == 3
    _do(ex, a, "microbit_radio_send", value=9)
    radio.deliver([sa, sb])
    assert _radio_events(sb) == []                     # b is still in group 0
    _do(ex, b, "microbit_radio_set_group", group=3)
    _do(ex, a, "microbit_radio_send", value=9)
    radio.deliver([sa, sb])
    assert _radio_events(sb) == [9]


def test_send_action_evaluates_expressions_and_keeps_quoted_text():
    ex, (a, b), (sa, sb) = _two_boards()
    _do(ex, a, "microbit_radio_send", value="3 * 4")
    _do(ex, a, "microbit_radio_send", value='"go - now"')   # a dash, quoted
    _do(ex, a, "microbit_radio_send")                        # default: 1
    radio.deliver([sa, sb])
    assert _radio_events(sb) == [12, "go - now", 1]


def test_radio_actions_do_nothing_on_other_objects():
    ex, (a, b), _ = _two_boards()

    class Other:
        object_name = "obj_wall"
        extension_state = {}
        action_executor = ex
    for name in ("microbit_radio_set_group", "microbit_radio_send"):
        assert ex.action_handlers[name](Other(), {"group": 1, "value": 1}) is None


# --- real game loop ------------------------------------------------------------------------------

def _act(action, **params):
    return {"action": action, "parameters": params}


def _write_project(tmp_path, a_events, b_events, c_events, b_group=None):
    def obj(name, events):
        return {"name": name, "asset_type": "object", "sprite": "", "visible": True,
                "solid": False, "events": events}
    project = {
        "name": "mb", "version": "1.0",
        "settings": {"window_width": 640, "window_height": 400, "room_speed": 60},
        "assets": {"sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
                   "fonts": {}, "data": {},
                   "objects": {"microbit_a": obj("microbit_a", a_events),
                               "microbit_b": obj("microbit_b", b_events),
                               "microbit_c": obj("microbit_c", c_events)},
                   "rooms": {"room0": {
                       "name": "room0", "asset_type": "room", "width": 640,
                       "height": 400, "background_color": "#000000",
                       "instances": [{"object": "microbit_a", "x": 110, "y": 110},
                                     {"object": "microbit_b", "x": 320, "y": 110},
                                     {"object": "microbit_c", "x": 530, "y": 110}]}}},
    }
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    return str(path)


def _run(project_json, script, frames=30):
    import pygame
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


def _boards(runner):
    out = {}
    for inst in runner.current_room.instances:
        out[inst.object_name[-1]] = (inst, inst.extension_state["microbit"]["simulator"])
    return out


from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame


def test_a_button_sends_7_b_receives_it_a_and_other_group_do_not(tmp_path):
    from extensions.microbit.simulator import glyph_image
    project = _write_project(
        tmp_path,
        a_events={"microbit_button_a": {"actions": [_act("microbit_radio_send", value=7)]},
                  "microbit_radio_received": {"actions": [
                      _act("microbit_show_number", value="radio_number")]}},
        b_events={"microbit_radio_received": {"actions": [
            _act("microbit_show_number", value="radio_number")]}},
        c_events={"create": {"actions": [_act("microbit_radio_set_group", group=5)]},
                  "microbit_radio_received": {"actions": [
                      _act("microbit_show_number", value="radio_number")]}})
    seen = {}

    def script(frame, runner):
        boards = _boards(runner)
        if frame == 4:
            boards["a"][1].set_button("a", True)
        if frame == 12:
            seen["a"] = boards["a"][1].display
            seen["b"] = boards["b"][1].display
            seen["c"] = boards["c"][1].display
            seen["b_vars"] = (boards["b"][0].radio_number, boards["b"][0].radio_string)

    _run(project, script)
    blank = [[0] * 5 for _ in range(5)]
    assert seen["b"] == glyph_image("7")
    assert seen["a"] == blank           # the sender doesn't hear itself
    assert seen["c"] == blank           # a different group hears nothing
    assert seen["b_vars"] == (7, "7")


def test_text_message_lands_in_radio_string(tmp_path):
    project = _write_project(
        tmp_path,
        a_events={"microbit_button_a": {"actions": [
            _act("microbit_radio_send", value='"hello"')]}},
        b_events={}, c_events={})
    seen = {}

    def script(frame, runner):
        boards = _boards(runner)
        if frame == 4:
            boards["a"][1].set_button("a", True)
        if frame == 10:
            inst = boards["b"][0]
            seen["vars"] = (getattr(inst, "radio_string", None),
                            getattr(inst, "radio_number", None))

    # b has no radio_received handler: the variables are still filled in
    _run(project, script)
    assert seen["vars"] == ("hello", 0)


def test_boards_in_a_shared_non_default_group_talk(tmp_path):
    from extensions.microbit.simulator import glyph_image
    setg = {"create": {"actions": [_act("microbit_radio_set_group", group=9)]}}
    project = _write_project(
        tmp_path,
        a_events={**setg, "microbit_button_b": {"actions": [
            _act("microbit_radio_send", value=3)]}},
        b_events={**setg, "microbit_radio_received": {"actions": [
            _act("microbit_show_number", value="radio_number")]}},
        c_events={"microbit_radio_received": {"actions": [
            _act("microbit_show_number", value="radio_number")]}})
    seen = {}

    def script(frame, runner):
        boards = _boards(runner)
        if frame == 4:
            boards["a"][1].set_button("b", True)
        if frame == 12:
            seen["b"] = boards["b"][1].display
            seen["c"] = boards["c"][1].display

    _run(project, script)
    assert seen["b"] == glyph_image("3")
    assert seen["c"] == [[0] * 5 for _ in range(5)]
