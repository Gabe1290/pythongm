"""File -> Stop Thymio robot (2026-11-22).

Halting a Thymio's program leaves the motors at their last target, so the robot
would drive on. Stopping therefore replaces the running program with
device.STOP_PROGRAM (motors 0, LEDs off, sound off) through the same send path
Send to Thymio uses, which was verified on a real robot. These tests drive the
device call and the IDE flow with fakes; a real robot is only used with
PYGM_THYMIO_HW=1.
"""
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extensions.thymio.export import device  # noqa: E402
from extensions.thymio.export.aseba_exporter import AsebaExporter  # noqa: E402


# --- the program ------------------------------------------------------------------------------------------

def test_the_stop_program_is_made_of_statements_the_exporter_already_sends():
    """Each line is exactly what an exported Stop Motors / LED / Stop Sound action produces, i.e. Aseba that was
    compiled on a real robot (2026-11-02), so the stop program cannot fail to compile for a new reason."""
    ex = AsebaExporter()
    off = {"red": "0", "green": "0", "blue": "0"}
    known = set()
    for text in (ex._translate_stop_motors({}), ex._translate_set_led_top(off),
                 ex._translate_set_led_bottom_left(off), ex._translate_set_led_bottom_right(off),
                 ex._translate_set_led_circle_all({}), ex._translate_stop_sound({})):
        known.update(text.splitlines())
    body = [line for line in device.STOP_PROGRAM.splitlines() if line and not line.startswith("#")]
    assert body and all(line in known for line in body), [l for l in body if l not in known]


def test_the_stop_program_stops_motors_leds_and_sound():
    p = device.STOP_PROGRAM
    assert "motor.left.target = 0" in p and "motor.right.target = 0" in p
    for led in ("leds.top", "leds.bottom.left", "leds.bottom.right", "leds.circle"):
        assert f"call {led}(" in p
    assert "call sound.freq(0, -1)" in p
    assert "onevent" not in p          # no handler left that could restart the motors


def test_stop_robot_sends_and_runs_it_on_the_chosen_robot(monkeypatch):
    seen = []
    monkeypatch.setattr(device, "send_program",
                        lambda source, node_id=None, run=True, **k: seen.append((source, node_id, run))
                        or device.SendResult(True, "done", "", "Rob"))
    assert device.stop_robot(node_id="id7").ok
    assert seen == [(device.STOP_PROGRAM, "id7", True)]


# --- the File-menu flow -------------------------------------------------------------------------------------

class _Ide:
    def __init__(self):
        self.statuses = []

    def tr(self, text):
        return text

    def update_status(self, text):
        self.statuses.append(text)


def _safely(fn):
    try:
        return fn()
    except Exception as exc:
        return exc


@pytest.fixture
def flow(monkeypatch):
    from extensions.thymio import export as exp
    box = SimpleNamespace(infos=[], warnings=[], stopped=[], picks=[], robots=[device.Robot("id9", "Rob", 2)])
    monkeypatch.setattr(exp, "_in_background", lambda fn: _safely(fn))
    monkeypatch.setattr(exp.QMessageBox, "information", lambda *a: box.infos.append(a[2]))
    monkeypatch.setattr(exp.QMessageBox, "warning", lambda *a: box.warnings.append(a[2]))
    monkeypatch.setattr(exp.QInputDialog, "getItem",
                        lambda parent, title, label, items, *a: (box.picks.append(list(items)) or (items[-1], True)))
    monkeypatch.setattr(device, "tdmclient_installed", lambda: True)
    monkeypatch.setattr(device, "ensure_device_manager", lambda *a, **k: True)
    monkeypatch.setattr(device, "list_robots", lambda *a, **k: box.robots)
    monkeypatch.setattr(device, "stop_robot", lambda node_id=None, **k: box.stopped.append(node_id)
                        or device.SendResult(True, "done", "", "Rob"))
    box.monkeypatch = monkeypatch
    box.run = lambda ide: exp.stop_thymio(ide)
    return box


def test_the_happy_path_stops_the_robot_and_says_so(flow):
    ide = _Ide()
    flow.run(ide)
    assert flow.stopped == ["id9"] and not flow.warnings
    assert ide.statuses[-1] == "Rob is stopped."


def test_several_robots_ask_which(flow):
    flow.robots = [device.Robot("a", "One", 2), device.Robot("b", "Two", 4)]
    flow.run(_Ide())
    assert flow.picks and flow.stopped == ["b"]


def test_no_robot_is_explained_and_nothing_is_sent(flow):
    flow.robots = []
    ide = _Ide()
    flow.run(ide)
    assert any("No Thymio robot found" in w for w in flow.warnings) and not flow.stopped
    assert ide.statuses[-1] == "Thymio stop: no robot found"


def test_an_unreachable_device_manager_is_explained(flow):
    flow.monkeypatch.setattr(device, "ensure_device_manager", lambda *a, **k: False)
    ide = _Ide()
    flow.run(ide)
    assert any("device manager" in w for w in flow.warnings) and not flow.stopped
    assert ide.statuses[-1] == "Thymio stop: no device manager"


def test_a_robot_held_by_another_program_is_explained(flow):
    flow.monkeypatch.setattr(device, "stop_robot", lambda **k: device.SendResult(False, "lock", "busy"))
    flow.run(_Ide())
    assert any("in use by another program" in w for w in flow.warnings)


def test_without_the_package_it_says_how_to_install_it(flow):
    flow.monkeypatch.setattr(device, "tdmclient_installed", lambda: False)
    flow.run(_Ide())
    assert any("pip install --user tdmclient" in t for t in flow.infos) and not flow.stopped


def test_the_menu_entry_exists_and_works_without_a_project():
    import extensions.thymio as ext
    actions = {}

    def create_action(text, *args, **kwargs):
        actions[text] = MagicMock(name=text)
        return actions[text]
    ide = MagicMock()
    ide.tr = lambda text: text
    ide.create_action = create_action
    menu = MagicMock()
    ext._build_file_menu(ide, menu)
    stop = actions["St&op Thymio robot"]
    stop.setProperty.assert_any_call("pygm_always_enabled", True)
    assert ("pygm_requires_project", True) not in [c.args for c in stop.setProperty.call_args_list]
    added = [c.args[0] for c in menu.addAction.call_args_list]
    assert added.index(stop) == added.index(actions["Send to &Thymio robot..."]) + 1


@pytest.mark.skipif(os.environ.get("PYGM_THYMIO_HW") != "1",
                    reason="needs a Thymio plugged in and the Thymio software; set PYGM_THYMIO_HW=1")
def test_a_real_robot_accepts_the_stop_program():
    assert device.ensure_device_manager()
    robots = device.list_robots(timeout=5)
    assert robots, "no robot found"
    assert device.stop_robot(node_id=robots[0].id).ok
