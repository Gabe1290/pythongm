"""micro:bit events and the frame update (docs/MICROBIT_EXTENSION_PLAN.md, S4).

Pure mapping tests, then a real ``GameRunner.run()`` over a tiny project:
a tick hook (the ``_FakeClock`` pattern) sets simulator inputs and the
authored handlers' actions must land in the display buffer.
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


# --- mapping -----------------------------------------------------------------

def test_every_simulator_report_has_an_event():
    from extensions.microbit.events import event_name_for, MICROBIT_EVENT_TYPES
    reports = [("button", "a"), ("button", "b"), ("button", "ab"),
               ("logo", "touched"), ("pin", 0), ("pin", 1), ("pin", 2),
               ("sound", "loud"), ("sound", "quiet"), ("display_done", None),
               ("sound_done", None)]
    from extensions.microbit.simulator import MicrobitSimulator  # noqa: F401
    gestures = ["up", "down", "left", "right", "face up", "face down",
                "freefall", "2g", "3g", "6g", "8g", "shake"]
    reports += [("gesture", g) for g in gestures]
    for kind, detail in reports:
        name = event_name_for(kind, detail)
        assert name in MICROBIT_EVENT_TYPES, (kind, detail)


def test_unknown_reports_have_no_event():
    from extensions.microbit.events import event_name_for
    assert event_name_for("gesture", "wave") is None
    assert event_name_for("pin", 7) is None
    assert event_name_for("nonsense", None) is None


def test_event_names_are_unique_and_prefixed():
    from extensions.microbit.events import MICROBIT_EVENT_TYPES
    assert len(MICROBIT_EVENT_TYPES) == 7 + 12 + 4
    for name, ev in MICROBIT_EVENT_TYPES.items():
        assert name == ev.name and name.startswith("microbit_")
        assert ev.category == "micro:bit"


def test_events_register_after_load_but_not_in_the_static_dict():
    src = (REPO_ROOT / "events" / "event_types.py").read_text(encoding="utf-8")
    assert "microbit_" not in src
    from events.plugin_loader import load_all_plugins
    from events.event_types import EVENT_TYPES
    load_all_plugins()
    assert "microbit_button_a" in EVENT_TYPES
    assert "microbit_gesture_shake" in EVENT_TYPES


def test_frame_update_is_registered_after_collision():
    from events.plugin_loader import load_all_plugins
    from runtime.extension_hooks import get_frame_updates
    load_all_plugins()
    mine = [(f, p) for f, p in get_frame_updates()
            if f.__module__ == "pygm_extension_microbit"]
    assert [p for _, p in mine] == ["after_collision"]


# --- real game loop ------------------------------------------------------------

def _act(action, **params):
    return {"action": action, "parameters": params}


def _write_project(tmp_path, events, extra_instances=()):
    project = {
        "name": "mb", "version": "1.0",
        "settings": {"window_width": 200, "window_height": 200,
                     "room_speed": 60},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
            "fonts": {}, "data": {},
            "objects": {
                "microbit_1": {"name": "microbit_1", "asset_type": "object",
                               "sprite": "", "visible": True, "solid": False,
                               "events": events},
                "obj_plain": {"name": "obj_plain", "asset_type": "object",
                              "sprite": "", "visible": True, "solid": False,
                              "events": {}},
            },
            "rooms": {"room0": {
                "name": "room0", "asset_type": "room", "width": 200,
                "height": 200, "background_color": "#000000",
                "instances": [{"object": "microbit_1", "x": 20, "y": 20},
                              *extra_instances]}},
        },
    }
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    return str(path)


def _run(project_json, script, frames=30):
    """Run the real loop; ``script(frame, runner)`` is called every tick."""
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
        result = runner.run()
    finally:
        pygame.time.Clock = real
    assert result is not False, "game loop reported a fatal crash"
    return runner


def _board(runner):
    inst = next(i for i in runner.current_room.instances
                if i.object_name == "microbit_1")
    return inst, inst.extension_state["microbit"]["simulator"]


def test_button_a_event_fires_and_its_show_image_lands_in_the_buffer(tmp_path):
    project = _write_project(tmp_path, {
        "microbit_button_a": {"actions": [_act("microbit_show_image", image="HEART")]},
    })
    seen = {}

    def script(frame, runner):
        _, sim = _board(runner)
        if frame == 5:
            sim.set_button("a", True)
        if frame == 8:
            seen["row0"] = list(sim.display[0])

    _run(project, script)
    assert seen["row0"] == [0, 9, 0, 9, 0]


def test_event_fires_once_per_press_not_every_frame(tmp_path):
    project = _write_project(tmp_path, {
        "microbit_button_a": {"actions": [
            _act("set_variable", variable="presses", value="presses + 1",
                 relative=False)]},
    })
    calls = []

    def script(frame, runner):
        inst, sim = _board(runner)
        if frame == 2:
            inst.presses = 0
        if frame == 5:
            sim.set_button("a", True)
        calls.append(getattr(inst, "presses", None))

    _run(project, script, frames=20)
    assert calls[-1] == 1


def test_other_events_route_to_their_own_handlers(tmp_path):
    project = _write_project(tmp_path, {
        "microbit_button_b": {"actions": [_act("microbit_set_pixel", x=0, y=0)]},
        "microbit_pin_1": {"actions": [_act("microbit_set_pixel", x=1, y=0)]},
        "microbit_logo_touched": {"actions": [_act("microbit_set_pixel", x=2, y=0)]},
        "microbit_gesture_shake": {"actions": [_act("microbit_set_pixel", x=3, y=0)]},
    })
    seen = {}

    def script(frame, runner):
        _, sim = _board(runner)
        if frame == 3:
            sim.set_button("b", True)
            sim.set_pin_touched(1, True)
            sim.set_logo_touched(True)
            sim.shake()
        if frame == 6:
            seen["row0"] = list(sim.display[0])

    _run(project, script)
    assert seen["row0"] == [9, 9, 9, 9, 0]


def test_unhandled_events_and_plain_objects_are_harmless(tmp_path):
    project = _write_project(
        tmp_path, {}, extra_instances=[{"object": "obj_plain", "x": 5, "y": 5}])

    def script(frame, runner):
        _, sim = _board(runner)
        if frame == 3:
            sim.set_button("a", True)

    runner = _run(project, script)
    plain = next(i for i in runner.current_room.instances
                 if i.object_name == "obj_plain")
    assert "microbit" not in plain.extension_state


def test_display_done_event_chains_animations(tmp_path):
    project = _write_project(tmp_path, {
        "microbit_button_a": {"actions": [
            _act("microbit_show_image", image="HAPPY", hold=100)]},
        "microbit_display_done": {"actions": [_act("microbit_set_pixel", x=4, y=4)]},
    })
    seen = {}

    def script(frame, runner):
        _, sim = _board(runner)
        if frame == 3:
            sim.set_button("a", True)
        if frame == 25:
            seen["corner"] = sim.get_pixel(4, 4)

    _run(project, script, frames=30)
    assert seen["corner"] == 9


def test_no_microbit_in_room_means_no_work(tmp_path):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from runtime.extension_hooks import get_frame_updates
    hook = next(f for f, _ in get_frame_updates()
                if f.__module__ == "pygm_extension_microbit")

    class _Room:
        instances = []

    class _GR:
        current_room = _Room()
        fps = 60

    assert hook(_GR()) is None
    _GR.current_room = None
    assert hook(_GR()) is None
