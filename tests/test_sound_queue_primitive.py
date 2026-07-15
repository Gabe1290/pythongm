"""The cross-platform `self._sound_queue` primitive.

execute_code has a live `game` object only on the desktop pygame runtime, so
`game.sounds[...].play()` (the obvious thing to reach for) only works there —
both the Kivy export and the Web/Pyodide export bind `game = None` in that
exec scope. samples/match3_2 needed sound from execute_code on all three
targets, which is what motivated `self._sound_queue.append('snd_x')` as a
primitive every runtime drains and plays the same way.

This file covers the desktop half (ActionExecutor._drain_sound_queue, and
execute_event calling it after every event, not just draw) and the Web half
(PY_BOOTSTRAP's run_code/run_draw folding the queue into their JSON patch).
The Kivy half has its own dedicated coverage in
tests/test_kivy_match3_2_sound_sprite_export.py, since it needs a full
generated-code + stub-kivy harness that doesn't fit this file's style.
"""
import json
import re
import sys
from pathlib import Path

import pytest

from conftest import import_module_directly

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


class MockInstance:
    def __init__(self):
        self.object_name = "test_object"
        self._sound_queue = []
        self.object_data = {'events': {}}


class MockSound:
    def __init__(self):
        self.played = 0
        self.volume = None

    def set_volume(self, v):
        self.volume = v

    def play(self):
        self.played += 1


class MockGameRunner:
    def __init__(self, sounds):
        self.sounds = sounds


# ---------------------------------------------------------------------------
# Desktop: ActionExecutor._drain_sound_queue
# ---------------------------------------------------------------------------

def test_drain_plays_bare_name_entry():
    snd = MockSound()
    ae = ActionExecutor(game_runner=MockGameRunner({"snd_swap": snd}))
    inst = MockInstance()
    inst._sound_queue = ["snd_swap"]

    ae._drain_sound_queue(inst)

    assert snd.played == 1
    assert snd.volume == 1.0
    assert inst._sound_queue == []


def test_drain_plays_dict_entry_with_custom_volume():
    snd = MockSound()
    ae = ActionExecutor(game_runner=MockGameRunner({"snd_match": snd}))
    inst = MockInstance()
    inst._sound_queue = [{"sound": "snd_match", "volume": 0.4}]

    ae._drain_sound_queue(inst)

    assert snd.played == 1
    assert snd.volume == 0.4


def test_drain_multiple_entries_in_order():
    a, b = MockSound(), MockSound()
    ae = ActionExecutor(game_runner=MockGameRunner({"a": a, "b": b}))
    inst = MockInstance()
    inst._sound_queue = ["a", "b", "a"]

    ae._drain_sound_queue(inst)

    assert a.played == 2
    assert b.played == 1


def test_drain_missing_sound_name_does_not_raise():
    ae = ActionExecutor(game_runner=MockGameRunner({}))
    inst = MockInstance()
    inst._sound_queue = ["snd_nonexistent"]

    ae._drain_sound_queue(inst)  # must not raise

    assert inst._sound_queue == []


def test_drain_with_no_game_runner_does_not_raise():
    ae = ActionExecutor()  # no game_runner at all
    inst = MockInstance()
    inst._sound_queue = ["snd_swap"]

    ae._drain_sound_queue(inst)  # must not raise


def test_drain_empty_queue_is_a_no_op():
    ae = ActionExecutor(game_runner=MockGameRunner({}))
    inst = MockInstance()
    inst._sound_queue = []

    ae._drain_sound_queue(inst)  # must not raise / touch anything

    assert inst._sound_queue == []


def test_execute_event_drains_sound_queue_for_any_event_not_just_draw():
    """The desktop half of the primitive must work from step/mouse events
    too, not just draw — a match3_2 requirement (swap/match/cascade sounds
    are queued from mouse_left_press and step)."""
    snd = MockSound()
    ae = ActionExecutor(game_runner=MockGameRunner({"snd_swap": snd}))
    inst = MockInstance()
    inst.object_data = {
        'events': {
            'step': {
                'actions': [
                    {'action': 'execute_code',
                     'parameters': {'code': "self._sound_queue.append('snd_swap')"}}
                ]
            }
        }
    }

    ae.execute_event(inst, 'step', inst.object_data['events'])

    assert snd.played == 1
    assert inst._sound_queue == []


# ---------------------------------------------------------------------------
# Web (Pyodide) bootstrap: PY_BOOTSTRAP's run_code / run_draw
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def py_bootstrap_ns():
    text = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
    m = re.search(r"const PY_BOOTSTRAP = `(.*?)`;", text, re.S)
    assert m, "PY_BOOTSTRAP block not found in engine.js"
    ns = {}
    exec(compile(m.group(1), "PY_BOOTSTRAP", "exec"), ns)
    return ns


def _sync(**overrides):
    base = {"x": 0, "y": 0, "mouse_x": 0, "mouse_y": 0, "keys": []}
    base.update(overrides)
    return json.dumps(base)


def test_run_code_returns_queued_sounds_in_patch(py_bootstrap_ns):
    run_code = py_bootstrap_ns["run_code"]
    code = ("self._sound_queue.append('snd_swap')\n"
            "self._sound_queue.append({'sound': 'snd_match', 'volume': 0.5})\n")
    patch = json.loads(run_code("t1", code, _sync()))
    assert patch["sounds"] == ["snd_swap", {"sound": "snd_match", "volume": 0.5}]


def test_run_code_patch_has_no_sounds_key_when_queue_empty(py_bootstrap_ns):
    run_code = py_bootstrap_ns["run_code"]
    patch = json.loads(run_code("t2", "pass", _sync()))
    assert "sounds" not in patch


def test_run_draw_propagates_both_draws_and_sounds(py_bootstrap_ns):
    run_draw = py_bootstrap_ns["run_draw"]
    code = ("self._draw_queue.append({'type': 'sprite', 'sprite_name': 'spr_gem_red', 'x': 1, 'y': 2})\n"
            "self._sound_queue.append('snd_cascade')\n")
    result = json.loads(run_draw("t3", code, _sync()))
    assert result["sounds"] == ["snd_cascade"]
    assert result["draws"] == [{"type": "sprite", "sprite_name": "spr_gem_red", "x": 1, "y": 2}]


def test_sound_queue_is_cleared_between_calls(py_bootstrap_ns):
    run_code = py_bootstrap_ns["run_code"]
    patch1 = json.loads(run_code("t4", "self._sound_queue.append('snd_swap')", _sync()))
    assert patch1["sounds"] == ["snd_swap"]
    patch2 = json.loads(run_code("t4", "pass", _sync()))
    assert "sounds" not in patch2, "queue must be drained/cleared after the first call"


def test_engine_js_playqueuedsounds_is_wired_into_runcode_and_rundraw():
    text = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
    assert "function playQueuedSounds(sounds, game)" in text
    assert "playQueuedSounds(patch.sounds, game);" in text
    assert "playQueuedSounds(result.sounds, game);" in text
