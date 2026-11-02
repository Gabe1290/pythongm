"""Sending a program straight to a Thymio without Aseba Studio (extensions/thymio/export/device.py + the File-menu action).

Everything short of the robot is tested with fakes, so these run without ``tdmclient``, without the Thymio software and
without a robot. The real thing is checked by hand -- and, on a machine with a robot plugged in, by the last test, which
only runs when ``PYGM_THYMIO_HW=1`` (it sends the LED-only program ``thymio_hw_1_leds``: nothing moves).
"""
import os
import socket
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
SAMPLE = REPO_ROOT / "samples" / "thymio_hw_test" / "project.json"

import pytest

from extensions.thymio.export import device


# --- fakes -------------------------------------------------------------------------------------------

class FakeNode:
    def __init__(self, calls, compile_error=None, run_error=None, name="Thymio A"):
        self.calls, self.compile_error, self.run_error = calls, compile_error, run_error
        self.props = {"name": name}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.calls.append("unlock")

    async def compile(self, source):
        self.calls.append(("compile", source))
        return self.compile_error

    async def run(self):
        self.calls.append("run")
        return self.run_error


class FakeClient:
    """Stands in for tdmclient.ClientAsync; ``nodes`` appear after a few message pumps."""

    def __init__(self, nodes_after=2, statuses=(2,), lock_error=None, **node_kwargs):
        self.calls, self.pumps = [], 0
        self.nodes_after, self.statuses, self.lock_error, self.node_kwargs = nodes_after, statuses, lock_error, node_kwargs
        self.nodes = []
        self.tdm = SimpleNamespace(io=SimpleNamespace(socket=MagicMock()))

    def process_waiting_messages(self):
        self.pumps += 1
        if self.pumps >= self.nodes_after and not self.nodes:
            self.nodes = [SimpleNamespace(id_str=f"id{i}", props={"name": f"Thymio {i}"}, status=s)
                          for i, s in enumerate(self.statuses)]
        return True

    def disconnect(self):
        self.calls.append("disconnect")

    async def lock(self, **kwargs):
        self.calls.append(("lock", kwargs))
        if self.lock_error:
            raise self.lock_error
        return FakeNode(self.calls, **self.node_kwargs)

    def run_async_program(self, program):
        import asyncio
        asyncio.run(program())


@pytest.fixture
def tdmclient_stub(monkeypatch):
    """A stand-in ``tdmclient`` so the lock-error path is the same with or without the real package."""
    class NodeLockError(Exception):
        pass
    module = types.ModuleType("tdmclient")
    module.NodeLockError = NodeLockError
    module.ClientAsync = FakeClient
    monkeypatch.setitem(sys.modules, "tdmclient", module)
    return module


# --- robots ---------------------------------------------------------------------------------------------

def test_a_robot_knows_its_status_and_whether_a_program_can_be_sent():
    assert device.Robot("a", "n", 2).status_name == "available" and device.Robot("a", "n", 2).usable
    assert device.Robot("a", "n", 4).usable                                  # ready
    assert not device.Robot("a", "n", 3).usable and device.Robot("a", "n", 3).status_name == "busy"
    assert device.Robot("a", "n", 99).status_name == "99"


def test_list_robots_returns_what_the_manager_reports_and_disconnects():
    client = FakeClient(nodes_after=3, statuses=(2, 3))
    robots = device.list_robots(timeout=2, client_factory=lambda: client)
    assert [(r.id, r.name, r.status) for r in robots] == [("id0", "Thymio 0", 2), ("id1", "Thymio 1", 3)]
    assert client.pumps >= 3
    assert "disconnect" in client.calls                                      # never leaves the connection open
    client.tdm.io.socket.settimeout.assert_called_once()                     # and wakes the reader thread


def test_list_robots_with_no_robot_waits_out_the_timeout_and_returns_nothing():
    client = FakeClient(nodes_after=10 ** 9)
    assert device.list_robots(timeout=0.3, client_factory=lambda: client) == []
    assert "disconnect" in client.calls


def test_the_missing_package_is_reported_with_the_install_command(monkeypatch):
    monkeypatch.setitem(sys.modules, "tdmclient", None)                      # makes `import tdmclient` fail
    assert device.tdmclient_installed() is False
    with pytest.raises(device.ThymioLinkError) as err:
        device.list_robots(timeout=0.1)
    assert "pip install --user tdmclient" in str(err.value)


# --- sending ---------------------------------------------------------------------------------------------

def test_send_compiles_then_runs_then_releases_the_robot(tdmclient_stub):
    client = FakeClient()
    result = device.send_program("call leds.top(0,0,8)", node_id="id0", client_factory=lambda: client)
    assert result == device.SendResult(True, "done", "", "Thymio A")
    assert client.calls[0] == ("lock", {"node_id": "id0"})
    assert client.calls[1:4] == [("compile", "call leds.top(0,0,8)"), "run", "unlock"]
    assert "disconnect" in client.calls


def test_send_without_a_robot_id_locks_the_first_robot(tdmclient_stub):
    client = FakeClient()
    device.send_program("x", client_factory=lambda: client)
    assert client.calls[0] == ("lock", {})


def test_a_compile_error_is_a_result_and_the_program_is_not_started(tdmclient_stub):
    client = FakeClient(compile_error={"error_msg": "line 3: unknown variable foo"})
    result = device.send_program("bad", client_factory=lambda: client)
    assert (result.ok, result.stage) == (False, "compile")
    assert "unknown variable foo" in result.message
    assert "run" not in client.calls                                         # never started a program that did not compile
    assert "unlock" in client.calls


def test_run_false_only_loads_the_program(tdmclient_stub):
    client = FakeClient()
    assert device.send_program("x", run=False, client_factory=lambda: client).ok
    assert "run" not in client.calls


def test_a_run_error_is_reported(tdmclient_stub):
    client = FakeClient(run_error={"error_code": 7})
    result = device.send_program("x", client_factory=lambda: client)
    assert (result.ok, result.stage) == (False, "run") and "7" in result.message


def test_a_busy_robot_is_a_lock_result_not_a_crash(tdmclient_stub):
    client = FakeClient(lock_error=tdmclient_stub.NodeLockError("busy"))
    result = device.send_program("x", client_factory=lambda: client)
    assert (result.ok, result.stage) == (False, "lock")
    assert "disconnect" in client.calls


# --- the device manager ---------------------------------------------------------------------------------

def test_device_manager_running_sees_a_listening_port_and_a_closed_one():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    try:
        assert device.device_manager_running("127.0.0.1", port) is True
    finally:
        server.close()
    assert device.device_manager_running("127.0.0.1", port) is False


def test_an_already_running_manager_is_not_started_again():
    launched = []
    assert device.ensure_device_manager(running=lambda: True, launch=launched.append) is True
    assert launched == []


def test_a_stopped_manager_is_started_when_the_thymio_software_is_installed(monkeypatch, tmp_path):
    exe = tmp_path / "thymio-device-manager.exe"
    exe.write_text("")
    monkeypatch.setattr(device, "find_device_manager_executable", lambda: exe)
    up, launched = [False], []

    def launch(path):
        launched.append(path)
        up[0] = True                                                          # it comes up after being started
    assert device.ensure_device_manager(wait=2, running=lambda: up[0], launch=launch) is True
    assert launched == [exe]


def test_no_installed_manager_means_it_cannot_be_started(monkeypatch):
    monkeypatch.setattr(device, "find_device_manager_executable", lambda: None)
    assert device.ensure_device_manager(running=lambda: False, launch=lambda p: pytest.fail("launched")) is False


def test_a_manager_that_will_not_start_is_reported_not_raised(monkeypatch, tmp_path):
    monkeypatch.setattr(device, "find_device_manager_executable", lambda: tmp_path / "x")

    def boom(path):
        raise OSError("no")
    assert device.ensure_device_manager(running=lambda: False, launch=boom) is False
    # and one that starts but never listens gives up after `wait`
    assert device.ensure_device_manager(wait=0.5, running=lambda: False, launch=lambda p: None) is False


def test_the_executable_is_found_on_the_path_first(monkeypatch, tmp_path):
    exe = tmp_path / "thymio-device-manager"
    exe.write_text("")
    monkeypatch.setattr(device.shutil, "which", lambda name: str(exe))
    assert device.find_device_manager_executable() == exe


# --- the Aseba source for one object --------------------------------------------------------------------

def test_the_source_is_plain_aseba_without_the_xml_envelope():
    from extensions.thymio.export.aseba_exporter import AsebaExporter
    exporter = AsebaExporter()
    names = exporter.thymio_object_names(SAMPLE)
    assert names[0] == "thymio_hw_1_leds" and len(names) == 6
    source = exporter.generate_source(SAMPLE, "thymio_hw_1_leds")
    assert "<!DOCTYPE" not in source and "<network>" not in source and "CDATA" not in source
    assert "onevent button.forward" in source and "call leds.top(32, 0, 0)" in source


def test_the_source_matches_what_the_aesl_export_puts_inside_the_node(tmp_path):
    from xml.etree import ElementTree
    from extensions.thymio.export.aseba_exporter import AsebaExporter
    AsebaExporter().export(str(SAMPLE), str(tmp_path))
    body = (tmp_path / "thymio_hw_2_motors.aesl").read_text(encoding="utf-8").split("\n", 1)[1]
    inside = ElementTree.fromstring(body).find("node").text
    code = lambda text: [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]  # noqa: E731
    assert code(AsebaExporter().generate_source(SAMPLE, "thymio_hw_2_motors")) == code(inside)


def test_an_unknown_object_is_a_key_error():
    from extensions.thymio.export.aseba_exporter import AsebaExporter
    with pytest.raises(KeyError):
        AsebaExporter().generate_source(SAMPLE, "thymio_nope")


# --- the File-menu action -------------------------------------------------------------------------------

@pytest.fixture
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_in_background_returns_the_result_or_the_exception(qapp):
    from extensions.thymio.export import _in_background
    assert _in_background(lambda: 42) == 42
    result = _in_background(lambda: (_ for _ in ()).throw(ValueError("x")))
    assert isinstance(result, ValueError)


class _Ide:
    def __init__(self, dirty=False):
        self.current_project_path = str(SAMPLE.parent)
        self.statuses, self.saved = [], 0
        self._dirty = dirty
        self.project_manager = SimpleNamespace(is_dirty=lambda: self._dirty)

    def tr(self, text):
        return text

    def update_status(self, text):
        self.statuses.append(text)

    def _require_open_project(self):
        return True

    def save_project(self):
        self.saved += 1


@pytest.fixture
def flow(monkeypatch, qapp):
    """The File-menu flow with every dialog and the robot link replaced; returns what happened."""
    from extensions.thymio import export as exp
    box = SimpleNamespace(infos=[], warnings=[], criticals=[], sent=[], picks=[], robots=[device.Robot("id9", "Rob", 2)])
    monkeypatch.setattr(exp, "_in_background", lambda fn: _safely(fn))
    monkeypatch.setattr(exp.QMessageBox, "information", lambda *a: box.infos.append(a[2]))
    monkeypatch.setattr(exp.QMessageBox, "warning", lambda *a: box.warnings.append(a[2]))
    monkeypatch.setattr(exp.QMessageBox, "critical", lambda *a: box.criticals.append(a[2]))
    monkeypatch.setattr(exp.QInputDialog, "getItem",
                        lambda parent, title, label, items, *a: (box.picks.append((label, list(items))) or (items[-1], True)))
    monkeypatch.setattr(device, "tdmclient_installed", lambda: True)
    monkeypatch.setattr(device, "ensure_device_manager", lambda *a, **k: True)
    monkeypatch.setattr(device, "list_robots", lambda *a, **k: box.robots)
    monkeypatch.setattr(device, "send_program", lambda source, node_id=None, **k: box.sent.append((source, node_id))
                        or device.SendResult(True, "done", "", "Rob"))
    box.run = lambda ide: exp.send_to_thymio(ide)
    box.monkeypatch = monkeypatch
    return box


def _safely(fn):
    try:
        return fn()
    except Exception as exc:
        return exc


def test_the_happy_path_sends_the_chosen_objects_source_to_the_robot(flow):
    ide = _Ide()
    flow.run(ide)
    assert len(flow.sent) == 1
    source, node_id = flow.sent[0]
    assert node_id == "id9"
    assert "onevent button" in source                                         # the LAST object (the stub picks items[-1])
    assert flow.picks[0][0] == "Object to send:" and len(flow.picks[0][1]) == 6
    assert any("is now running on Rob" in text for text in flow.infos)
    assert not flow.warnings


def test_the_project_is_saved_first_only_when_it_has_unsaved_changes(flow):
    clean, dirty = _Ide(False), _Ide(True)
    flow.run(clean)
    flow.run(dirty)
    assert (clean.saved, dirty.saved) == (0, 1)


def test_without_the_package_it_says_how_to_install_it_and_sends_nothing(flow):
    flow.monkeypatch.setattr(device, "tdmclient_installed", lambda: False)
    flow.run(_Ide())
    assert any("pip install --user tdmclient" in text for text in flow.infos) and not flow.sent


def test_an_unreachable_device_manager_is_explained(flow):
    flow.monkeypatch.setattr(device, "ensure_device_manager", lambda *a, **k: False)
    flow.run(_Ide())
    assert any("device manager" in text for text in flow.warnings) and not flow.sent


def test_no_robot_is_explained(flow):
    flow.robots = []
    flow.monkeypatch.setattr(device, "list_robots", lambda *a, **k: [])
    flow.run(_Ide())
    assert any("No Thymio robot found" in text for text in flow.warnings) and not flow.sent


def test_several_robots_ask_which(flow):
    flow.monkeypatch.setattr(device, "list_robots",
                             lambda *a, **k: [device.Robot("a", "First", 2), device.Robot("b", "Second", 2)])
    flow.run(_Ide())
    labels = [p for p in flow.picks if p[0] == "Robot:"]
    assert labels and labels[0][1] == ["First (available)", "Second (available)"]
    assert flow.sent[0][1] == "b"                                             # the stub picks the last one


def test_a_compile_error_from_the_robot_is_shown_with_its_text(flow):
    flow.monkeypatch.setattr(device, "send_program",
                             lambda *a, **k: device.SendResult(False, "compile", "line 3: boom", "Rob"))
    flow.run(_Ide())
    assert any("line 3: boom" in text and "compile" in text for text in flow.warnings) and not flow.infos


def test_a_robot_in_use_by_another_program_is_explained(flow):
    flow.monkeypatch.setattr(device, "send_program", lambda *a, **k: device.SendResult(False, "lock", "busy"))
    flow.run(_Ide())
    assert any("Aseba Studio" in text for text in flow.warnings)


def test_a_link_error_during_the_send_is_shown(flow):
    def boom(*a, **k):
        raise device.ThymioLinkError("link down")
    flow.monkeypatch.setattr(device, "send_program", boom)
    flow.run(_Ide())
    assert "link down" in flow.warnings


def test_a_project_without_a_thymio_object_is_explained(flow, tmp_path):
    (tmp_path / "project.json").write_text('{"name": "p", "assets": {"objects": {"obj": {"events": {}}}}}', encoding="utf-8")
    ide = _Ide()
    ide.current_project_path = str(tmp_path)
    flow.run(ide)
    assert any("No Thymio objects" in text for text in flow.warnings) and not flow.sent


def test_the_menu_entry_exists_and_needs_a_project():
    import extensions.thymio as ext
    actions = {}

    def create_action(text, *args, **kwargs):
        actions[text] = MagicMock(name=text)                                  # a distinct action per entry
        return actions[text]
    ide = MagicMock()
    ide.tr = lambda text: text
    ide.create_action = create_action
    menu = MagicMock()
    ext._build_file_menu(ide, menu)
    send = actions["Send to &Thymio robot..."]
    send.setProperty.assert_any_call("pygm_requires_project", True)
    assert send in [c.args[0] for c in menu.addAction.call_args_list]
    assert ide.send_to_thymio_action is send


# --- translations -----------------------------------------------------------------------------------------

SEND_STRINGS = [
    "Send to &Thymio robot...", "Send to Thymio", "Object to send:", "Robot:", "Sending {0} to {1}...",
    "{0} is now running on {1}.", "Thymio send failed",
    "No Thymio robot found. Check the USB cable (or the wireless dongle) and that the robot is switched on.",
    "Talking to the robot needs the 'tdmclient' package. Install it with:\n\npip install --user tdmclient\n\nand try again.",
    "The robot did not accept the program ({0}):\n\n{1}",
]


@pytest.mark.parametrize("lang", ["fr", "pl"])
def test_the_send_to_thymio_text_is_translated_where_the_catalogs_must_match(qapp, lang):
    from PySide6.QtCore import QCoreApplication, QTranslator
    translator = QTranslator()
    assert translator.load(str(REPO_ROOT / "translations" / f"pygm2_{lang}.qm"))
    QCoreApplication.installTranslator(translator)
    try:
        for source in SEND_STRINGS:
            translated = QCoreApplication.translate("PyGameMakerIDE", source)
            assert translated and translated != source, (lang, source)
        assert "pip install --user tdmclient" in QCoreApplication.translate("PyGameMakerIDE", SEND_STRINGS[8])
    finally:
        QCoreApplication.removeTranslator(translator)


def test_french_keeps_its_accents_in_the_send_text(qapp):
    from PySide6.QtCore import QCoreApplication, QTranslator
    translator = QTranslator()
    assert translator.load(str(REPO_ROOT / "translations" / "pygm2_fr.qm"))
    QCoreApplication.installTranslator(translator)
    try:
        assert QCoreApplication.translate("PyGameMakerIDE", "Thymio send failed") == "Échec de l'envoi au Thymio"
        assert "trouvé" in QCoreApplication.translate("PyGameMakerIDE", SEND_STRINGS[7])
    finally:
        QCoreApplication.removeTranslator(translator)


# --- the real robot (only when asked for) ----------------------------------------------------------------

@pytest.mark.skipif(os.environ.get("PYGM_THYMIO_HW") != "1",
                    reason="needs a Thymio plugged in and the Thymio software; set PYGM_THYMIO_HW=1")
def test_a_real_robot_accepts_the_led_program():
    """Sends thymio_hw_1_leds (LEDs only: nothing moves) to the first robot and expects it to run."""
    from extensions.thymio.export.aseba_exporter import AsebaExporter
    assert device.ensure_device_manager()
    robots = device.list_robots(timeout=5)
    assert robots, "no robot found"
    result = device.send_program(AsebaExporter().generate_source(SAMPLE, "thymio_hw_1_leds"), node_id=robots[0].id)
    assert result.ok, result


@pytest.mark.skipif(os.environ.get("PYGM_THYMIO_HW") != "1",
                    reason="needs a Thymio plugged in and the Thymio software; set PYGM_THYMIO_HW=1")
def test_the_whole_menu_flow_against_a_real_robot(monkeypatch, qapp):
    """File -> Send to Thymio robot... end to end: only the dialogs are replaced (the first object, thymio_hw_1_leds,
    is picked); the device manager, robot list, compile and run are real."""
    from extensions.thymio import export as exp
    shown = {"info": [], "warn": []}
    monkeypatch.setattr(exp.QMessageBox, "information", lambda *a: shown["info"].append(a[2]))
    monkeypatch.setattr(exp.QMessageBox, "warning", lambda *a: shown["warn"].append(a[2]))
    monkeypatch.setattr(exp.QInputDialog, "getItem", lambda parent, title, label, items, *a: (items[0], True))
    ide = _Ide()
    exp.send_to_thymio(ide)
    assert not shown["warn"], shown["warn"]
    assert any("thymio_hw_1_leds is now running on" in text for text in shown["info"]), shown
