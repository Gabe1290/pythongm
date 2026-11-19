"""Shared-folder (file exchange) multiplayer on the Kivy (Android/iOS) export.

Unlike the LAN extension (a phone is a client only) the file session is plain file I/O, so a
phone can HOST and JOIN. A real Kivy export of ``samples/fichier_1`` is made, its ``mp_files``
package put on ``sys.path`` as the game would see it, and ``mp_files.glue`` is driven against a
real desktop ``FileSession`` on a real temp folder, both ways round, with a stand-in scene and a
stand-in ``main`` (the global store). The ``core.logger`` stand-in is checked in a clean
subprocess. The connect screen is desktop-only: ``folder="auto"`` and ``show_lobby`` degrade.
"""
import json
import subprocess
import sys
import tempfile
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402
from extensions.multiplayer_files.session import FileSession  # noqa: E402

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def export_dir():
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    from export.Kivy.kivy_exporter import KivyExporter
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        src = ROOT / "samples" / "fichier_1"
        data = json.loads((src / "project.json").read_text(encoding="utf-8"))
        out = Path(tempfile.mkdtemp(prefix="kivy_mpf_")) / "export"
        assert KivyExporter(data, src, out).export()
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None
    return out / "game"


def test_the_session_modules_and_glue_are_shipped(export_dir):
    assert {p.name for p in (export_dir / "mp_files").glob("*.py")} == {
        "__init__.py", "state.py", "fileio.py", "session.py", "glue.py"}
    ext = ROOT / "extensions" / "multiplayer_files"
    for name in ("state", "fileio", "session"):
        assert (export_dir / "mp_files" / f"{name}.py").read_bytes() == (ext / f"{name}.py").read_bytes()


def test_generated_code_calls_the_glue_and_every_module_compiles(export_dir):
    for f in export_dir.rglob("*.py"):
        compile(f.read_text(encoding="utf-8"), str(f), "exec")
    code = "\n".join(f.read_text(encoding="utf-8") for f in (export_dir / "objects").glob("*.py"))
    assert "from mp_files.glue import " in code
    assert "unsupported" not in code
    scene = (export_dir / "scenes" / "room0.py").read_text(encoding="utf-8")
    assert "def _ext_update__multiplayer_files(self, dt):" in scene


def test_the_core_logger_stand_in_makes_the_package_importable_without_the_ide(export_dir):
    code = ("import sys; sys.path.insert(0, %r); import mp_files.glue as g; "
            "from mp_files.session import FileSession; print('ok', g.active())" % str(export_dir))
    done = subprocess.run([sys.executable, "-I", "-c", code], cwd=str(export_dir.parent),
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0 and done.stdout.strip() == "ok False", done.stderr


# ---------------------------------------------------------------- stand-ins

class _App:
    def __init__(self):
        self.globals = {}


class _Inst:
    def __init__(self, scene):
        self.scene, self.events = scene, []

    def __getattr__(self, name):
        if name.startswith("on_") and name[3:] in self.scene.handles:
            return lambda name=name: self.events.append(name)
        raise AttributeError(name)


class _Scene:
    def __init__(self, handles=()):
        self.handles, self.instances = set(handles), []

    def watcher(self):
        inst = _Inst(self)
        self.instances.append(inst)
        return inst


@pytest.fixture()
def glue(export_dir, monkeypatch):
    app = _App()
    fake_main = types.ModuleType("main")
    fake_main.set_global = lambda k, v: app.globals.__setitem__(k, v)
    fake_main.get_global = lambda k, d=0: app.globals.get(k, d)
    fake_main.get_game_app = lambda: app
    fake_main._log = lambda *a: None
    monkeypatch.setitem(sys.modules, "main", fake_main)
    monkeypatch.syspath_prepend(str(export_dir))
    for name in [n for n in sys.modules if n == "mp_files" or n.startswith("mp_files.")]:
        monkeypatch.delitem(sys.modules, name)
    import mp_files.glue as g
    g.leave()
    g._warned.clear()
    yield g, app
    g.leave()
    for name in [n for n in sys.modules if n == "mp_files" or n.startswith("mp_files.")]:
        sys.modules.pop(name, None)


def _tick(g, scene, *others):
    """One pass of everything, with each session's poll gate forced open."""
    for s in others:
        s._last_poll = 0.0
        s.pump_before_step()
        s.pump_after_update()
    if g.active():
        g._session._last_poll = 0.0
        g.update(scene)


def _settle(g, scene, *others, rounds=8):
    for _ in range(rounds):
        _tick(g, scene, *others)


# ---------------------------------------------------------------- the phone as CLIENT

def test_a_phone_joins_a_desktop_host_and_gets_identity_and_the_started_event(glue, tmp_path):
    g, app = glue
    host = FileSession(mode="host", folder=tmp_path, player_name="Prof", round_deadline=100)
    assert host.start()
    scene = _Scene({"file_session_started"})
    watcher = scene.watcher()
    g.join(str(tmp_path), "Ada")
    assert g.active()
    _settle(g, scene, host)
    assert app.globals["player_id"] == 1 and app.globals["is_host"] == 0
    assert watcher.events.count("on_file_session_started") == 1


def test_a_round_trip_shared_vars_end_turn_and_round_resolved(glue, tmp_path):
    g, app = glue
    host = FileSession(mode="host", folder=tmp_path, player_name="Prof", round_deadline=100)
    assert host.start()
    scene = _Scene({"round_resolved"})
    watcher = scene.watcher()
    g.join(str(tmp_path), "Ada")
    _settle(g, scene, host)
    start_round = app.globals["round_number"]
    g.set_shared("move_ada", "B2")
    g.end_turn()
    host.set_shared("move_prof", "A1")
    host.end_turn()
    _settle(g, scene, host)
    assert host.shared.get("move_ada") == "B2"
    assert app.globals["move_prof"] == "A1" and app.globals["round_number"] == start_round + 1
    assert "on_round_resolved" in watcher.events
    g.get_shared_into("move_prof", "copy")
    assert app.globals["copy"] == "A1"
    g.get_shared_into("nope", "none_here")
    assert app.globals["none_here"] is None


def test_messages_reach_the_phone_with_sender_and_data(glue, tmp_path):
    g, app = glue
    host = FileSession(mode="host", folder=tmp_path, player_name="Prof", round_deadline=100)
    assert host.start()
    scene = _Scene({"network_message_files"})
    watcher = scene.watcher()
    g.join(str(tmp_path), "Ada")
    _settle(g, scene, host)
    host.send_message("coucou", {"n": 1}, "all")
    host.end_turn()
    g.end_turn()
    _settle(g, scene, host)
    assert (app.globals["network_event"], app.globals["network_data"]) == ("coucou", {"n": 1})
    assert app.globals["network_sender"] == 0 and "on_network_message_files" in watcher.events


# ---------------------------------------------------------------- the phone as HOST

def test_a_phone_hosts_and_a_desktop_client_joins(glue, tmp_path):
    g, app = glue
    shared = tmp_path / "party"
    scene = _Scene({"player_joined_files", "round_resolved"})
    watcher = scene.watcher()
    g.host(str(shared), 4, "Prof", 100, False)
    assert g.active() and shared.is_dir()
    client = FileSession(mode="client", folder=shared, player_name="Bo")
    assert client.start()
    _settle(g, scene, client)
    assert app.globals["is_host"] == 1 and app.globals["player_id"] == 0
    assert app.globals["player_count"] == 2
    assert app.globals["network_player_name"] == "Bo" and "on_player_joined_files" in watcher.events
    g.set_shared("board", "X..")
    g.end_turn()
    client.set_shared("reply", "ok")
    client.end_turn()
    _settle(g, scene, client)
    assert client.shared.get("board") == "X.." and app.globals["reply"] == "ok"
    assert "on_round_resolved" in watcher.events


# ---------------------------------------------------------------- limits and failures

def test_leave_clears_the_status_globals_and_a_client_leave_is_noticed(glue, tmp_path):
    g, app = glue
    host = FileSession(mode="host", folder=tmp_path, player_name="Prof", round_deadline=100)
    assert host.start()
    scene = _Scene()
    g.join(str(tmp_path), "Ada")
    _settle(g, scene, host)
    assert "player_id" in app.globals
    g.leave()
    assert not g.active() and "player_id" not in app.globals and "round_number" not in app.globals
    _settle(g, scene, host)
    assert host.player_count == 1                     # the host saw the leave file
    g.update(scene)                                   # a no-op, no crash


def test_a_missing_or_unwritable_folder_never_raises(glue, tmp_path):
    g, app = glue
    blocker = tmp_path / "a_file"
    blocker.write_text("x", encoding="utf-8")
    g.host(str(blocker / "sub"), 4, "Prof", 30, False)   # cannot be created under a file
    assert not g.active()
    g.host("", 4, "Prof", 30, False)
    g.join("", "Ada")
    assert not g.active()


def test_auto_and_the_lobby_screen_are_desktop_only_and_warn_once(glue, tmp_path):
    g, app = glue
    g.join("auto", "Ada")
    g.join("auto", "Ada")
    assert not g.active() and "auto" in g._warned
    g.host(str(tmp_path / "p"), 4, "Prof", 30, True)       # show_lobby ignored: it just hosts
    assert g.active() and "lobby" in g._warned
    g.leave()


def test_the_default_player_name_comes_from_the_global(glue, tmp_path):
    g, app = glue
    app.globals["player_name"] = "Zoé"
    host = FileSession(mode="host", folder=tmp_path, player_name="Prof", round_deadline=100)
    assert host.start()
    scene = _Scene()
    g.join(str(tmp_path), "")
    _settle(g, scene, host)
    assert g._session.player_name == "Zoé"
