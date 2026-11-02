"""Two simulator-vs-robot differences found while building samples/thymio_hw_test, now fixed.

1. **Button release.** The real Thymio runs a button's ``onevent button.*`` handler on every change of
   state, press AND release; the simulator fired it only on press, so a "released" handler (and the
   "let go and it stops" idiom) never ran there. Both input paths (the game runtime and the playground
   runner) now fire ``thymio_button_<x>`` and ``thymio_any_button`` on press and on release.
2. **Draw events on a robot.** The room's render loop skipped ``instance.render()`` for a
   ``custom_rendered`` instance (a robot whose body an overlay draws) -- and ``render()`` is what runs the
   draw event, so a ``draw_text`` on a Thymio-named object drew nothing. The draw event now still runs.
"""
import ast
import json
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
SAMPLE = REPO_ROOT / "samples" / "thymio_hw_test"

import pytest


@pytest.fixture(autouse=True)
def _thymio_enabled(monkeypatch):
    """A developer's own config may switch the extension off; force it on without touching any file."""
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    monkeypatch.setattr(plugin_loader, "is_extension_enabled",
                        lambda folder, default=True: True if folder == "thymio" else real(folder, default))


def _robot(events):
    """A stand-in robot: records executed events and button presses."""
    fired, presses = [], []
    sim = SimpleNamespace(set_button=lambda name, down: presses.append((name, down)), x=0, y=0, angle=0)
    executor = SimpleNamespace(execute_event=lambda inst, name, evs: fired.append(name))
    robot = SimpleNamespace(extension_state={"thymio": {"simulator": sim}}, object_name="bot",
                            object_data={"events": events}, action_executor=executor)
    return robot, presses, fired


# --- the shared helper ------------------------------------------------------------------------------

def test_fire_button_events_runs_the_button_event_and_the_any_button_event():
    from extensions.thymio.input import fire_button_events
    robot, _, fired = _robot({"thymio_button_left": {}, "thymio_any_button": {}})
    assert fire_button_events(robot.action_executor, robot, "left") is True
    assert fired == ["thymio_button_left", "thymio_any_button"]


def test_fire_button_events_skips_what_is_not_defined_and_says_so():
    from extensions.thymio.input import fire_button_events
    robot, _, fired = _robot({"thymio_button_left": {}})
    assert fire_button_events(robot.action_executor, robot, "right") is False
    assert fired == []
    assert fire_button_events(robot.action_executor, robot, "left") is True
    assert fired == ["thymio_button_left"]


def test_a_failing_handler_is_logged_not_raised():
    from extensions.thymio.input import fire_button_events
    robot, _, _ = _robot({"thymio_button_left": {}})
    robot.action_executor = SimpleNamespace(execute_event=lambda *a: (_ for _ in ()).throw(RuntimeError("boom")))
    assert fire_button_events(robot.action_executor, robot, "left") is True       # fired, error swallowed


# --- both input paths: press and release ------------------------------------------------------------

def test_keyboard_press_and_release_each_fire_the_events():
    from extensions.thymio import input as inp
    robot, presses, fired = _robot({"thymio_button_forward": {}, "thymio_any_button": {}})
    assert inp.key_down(robot, "up") is True
    assert fired == ["thymio_button_forward", "thymio_any_button"]
    inp.key_up(robot, "up")
    assert fired == ["thymio_button_forward", "thymio_any_button"] * 2
    assert presses == [("forward", True), ("forward", False)]            # the state is cleared BEFORE the release event


def test_the_release_event_sees_the_button_already_released():
    """A 'released' guard inside the handler must read 0, so the state is cleared first."""
    from extensions.thymio import input as inp
    state = {}
    sim = SimpleNamespace(set_button=lambda name, down: state.__setitem__(name, 1 if down else 0))
    seen = []
    robot = SimpleNamespace(extension_state={"thymio": {"simulator": sim}}, object_name="bot",
                            object_data={"events": {"thymio_button_forward": {}}},
                            action_executor=SimpleNamespace(execute_event=lambda i, n, e: seen.append(state["forward"])))
    inp.key_down(robot, "up")
    inp.key_up(robot, "up")
    assert seen == [1, 0]


def test_mouse_press_and_release_each_fire_the_events():
    from extensions.thymio import input as inp, renderer as renderer_mod
    robot, presses, fired = _robot({"thymio_button_center": {}})
    runner = SimpleNamespace(current_room=SimpleNamespace(instances=[robot]))
    real = renderer_mod.ThymioRenderer.hit_test_button
    renderer_mod.ThymioRenderer.hit_test_button = lambda self, rx, ry, ang, mx, my: "center" if (mx, my) == (9, 9) else None
    try:
        assert inp.mouse_down(runner, 1, 9, 9) is True
        assert inp.mouse_up(runner, 1, 9, 9) is True
    finally:
        renderer_mod.ThymioRenderer.hit_test_button = real
    assert fired == ["thymio_button_center"] * 2


def _function_source(path, name):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(Path(path).read_text(encoding="utf-8"), node)
    raise AssertionError(name)


@pytest.mark.parametrize("method", ["_on_key_pressed", "_on_key_released", "_on_mouse_pressed", "_on_mouse_released"])
def test_the_playground_runner_uses_the_shared_helper_for_every_press_and_release(method):
    source = _function_source(REPO_ROOT / "extensions/thymio/playground_runner.py", method)
    assert "fire_button_events(" in source, method


# --- through the real game loop: "let go and it stops" ---------------------------------------------------

def _run(project_path, at_frame, action, frames=40):
    """Run the real GameRunner; call ``action(runner)`` at ``at_frame`` and return its result."""
    import pygame
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRunner
    load_all_plugins()
    pygame.init()
    runner = GameRunner(str(project_path))
    out = {}
    real_clock = pygame.time.Clock

    class FakeClock:
        n = 0

        def tick(self, fps=0):
            FakeClock.n += 1
            if FakeClock.n == at_frame:
                out["result"] = action(runner)
            if FakeClock.n == frames:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return 16

        def get_fps(self):
            return 60.0
    pygame.time.Clock = FakeClock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real_clock
    return out["result"]


def test_the_motors_program_stops_when_the_button_is_released():
    from extensions.thymio import input as inp
    from extensions.thymio.state import simulator_of

    def act(runner):
        robot = next(i for i in runner.current_room.instances if i.object_name == "thymio_hw_2_motors")
        sim = simulator_of(robot)
        trace = [sim.get_motor_speeds()]
        inp.key_down(robot, "up")                       # hold "forward"
        trace.append(sim.get_motor_speeds())
        inp.key_up(robot, "up")                          # let go
        trace.append(sim.get_motor_speeds())
        return trace
    idle, held, released = _run(SAMPLE / "project.json", 5, act)
    assert idle == (0, 0)
    assert held == (100, 100)                            # driving while held
    assert released == (0, 0)                            # and it stops on release: the whole point


# --- a draw event on a robot actually draws -------------------------------------------------------------

def _project_with_draw_on_a_robot(tmp_path):
    work = tmp_path / "proj"
    shutil.copytree(SAMPLE, work)
    path = work / "objects" / "thymio_hw_1_leds.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["events"]["draw"] = {"actions": [{"action": "draw_text", "parameters": {
        "text": '"HELLO"', "x": "20", "y": "20", "color": "#ff0000"}}]}
    path.write_text(json.dumps(obj), encoding="utf-8")
    project = json.loads((work / "project.json").read_text(encoding="utf-8"))
    project["assets"]["objects"]["thymio_hw_1_leds"] = obj
    (work / "project.json").write_text(json.dumps(project), encoding="utf-8")
    return work / "project.json"


def _red_pixels(runner):
    runner.render()
    screen = runner.screen
    return sum(1 for x in range(0, 120) for y in range(10, 40) if tuple(screen.get_at((x, y)))[:3] == (255, 0, 0))


def test_a_draw_event_on_a_thymio_named_object_draws(tmp_path):
    assert _run(_project_with_draw_on_a_robot(tmp_path), 5, _red_pixels) > 50


def test_without_the_draw_event_nothing_red_is_drawn_there(tmp_path):
    """The control: the same spot is not red in the unmodified sample (so the test above sees the new text)."""
    assert _run(SAMPLE / "project.json", 5, _red_pixels) == 0
