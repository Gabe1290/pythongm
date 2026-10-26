"""Truth test for Tutorials/17_microbit_intro (micro:bit: Program a Virtual
Board), same discipline as tests/test_raycast_tutorial_lessons.py: the
build-along is rebuilt here exactly as the pages describe it and run through
the real GameRunner with real mouse clicks on the drawn buttons, so the
lesson can never teach something the engine doesn't actually do.
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
from extensions.microbit.images import IMAGES  # noqa: E402


def _grid(name):
    return [[int(c) for c in row] for row in IMAGES[name]]


def _act(action, **params):
    return {"action": action, "parameters": params}


def _write_project(tmp_path):
    """Exactly the three events Phase 2 of the lesson builds: Create ->
    Show Image HEART, Button A Pressed -> Show Image HAPPY, Button B
    Pressed -> Show Image SAD. No sprite, no is_microbit flag -- the lesson
    relies purely on the "microbit_1" name prefix, and no microbit_keyboard
    opt-in -- the lesson's buttons are only ever clicked with the mouse."""
    project = {
        "name": "mb_intro", "version": "1.0",
        "settings": {"window_width": 320, "window_height": 260, "room_speed": 60,
                      "active_extensions": ["microbit"]},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
            "fonts": {}, "data": {},
            "objects": {"microbit_1": {
                "name": "microbit_1", "asset_type": "object", "sprite": "",
                "visible": True, "solid": False,
                "events": {
                    "create": {"actions": [_act("microbit_show_image", image="HEART", hold=0)]},
                    "microbit_button_a": {"actions": [_act("microbit_show_image", image="HAPPY", hold=0)]},
                    "microbit_button_b": {"actions": [_act("microbit_show_image", image="SAD", hold=0)]},
                },
            }},
            "rooms": {"room0": {
                "name": "room0", "asset_type": "room", "width": 320, "height": 260,
                "background_color": "#1e3c5a",
                "instances": [{"object": "microbit_1", "x": 160, "y": 130}]}},
        },
    }
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    return str(path)


def _run(project_json, script, frames=30):
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


def _sim(runner):
    inst = next(i for i in runner.current_room.instances if i.object_name == "microbit_1")
    return inst.extension_state["microbit"]["simulator"]


def _click(pos):
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos))


def test_the_board_starts_with_a_heart_then_a_and_b_show_the_two_moods(tmp_path):
    project = _write_project(tmp_path)
    buttons = L.board_layout(160, 130).buttons
    seen = {}

    def script(frame, runner):
        sim = _sim(runner)
        if frame == 3:
            seen["heart"] = [row[:] for row in sim.display]
            _click(buttons["a"][:2])
        if frame == 8:
            seen["happy"] = [row[:] for row in sim.display]
            _click(buttons["b"][:2])
        if frame == 13:
            seen["sad"] = [row[:] for row in sim.display]

    _run(project, script, frames=16)
    assert seen["heart"] == _grid("HEART")
    assert seen["happy"] == _grid("HAPPY")
    assert seen["sad"] == _grid("SAD")


def test_without_the_microbit_name_prefix_no_board_is_drawn_and_events_never_fire(tmp_path):
    """Confirms the naming-rule claim on page 2: an object that does NOT
    start with "microbit" (and has no is_microbit flag) never gets a
    simulator at all, so its microbit_button_a event is simply dead code."""
    path = tmp_path / "project.json"
    data = {
        "name": "mb_intro_bad", "version": "1.0",
        "settings": {"window_width": 320, "window_height": 260, "room_speed": 60,
                      "active_extensions": ["microbit"]},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
            "fonts": {}, "data": {},
            "objects": {"obj_not_a_board": {
                "name": "obj_not_a_board", "asset_type": "object", "sprite": "",
                "visible": True, "solid": False,
                "events": {"create": {"actions": [_act("microbit_show_image", image="HEART", hold=0)]}},
            }},
            "rooms": {"room0": {
                "name": "room0", "asset_type": "room", "width": 320, "height": 260,
                "background_color": "#1e3c5a",
                "instances": [{"object": "obj_not_a_board", "x": 160, "y": 130}]}},
        },
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    seen = {}

    def script(frame, runner):
        if frame == 3:
            inst = next(i for i in runner.current_room.instances if i.object_name == "obj_not_a_board")
            seen["has_simulator"] = "microbit" in inst.extension_state

    _run(str(path), script, frames=6)
    assert seen["has_simulator"] is False
