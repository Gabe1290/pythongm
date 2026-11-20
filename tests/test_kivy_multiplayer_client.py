"""LAN multiplayer CLIENT on the Kivy (Android/iOS) export.

A real Kivy export of ``samples/reseau_2`` is made, its ``mp_lan`` package put on
``sys.path`` exactly as the game would see it, and ``mp_lan.glue`` is driven
against a REAL desktop host (``NetworkSession`` in host mode) over 127.0.0.1 with
a stand-in scene and a stand-in ``main`` (the game's global store). Covers: the
files shipped, the generated action/condition/event code, Tier A (shared vars,
messages, identity, lifecycle events), ghost viewing (spawn without a create
event, interpolation, the y-up flip, destroy, room-change rebuild, unsafe
replicated var names), connection loss, ``leave_game``, and the things a phone
cannot do. The ``core.logger`` stand-in is checked in a clean subprocess.
"""
import json
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402
from extensions.multiplayer_lan.session import NetworkSession  # noqa: E402

pytestmark = skip_without_pyside6


# ---------------------------------------------------------------- the export

@pytest.fixture(scope="module")
def export_dir():
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    from export.Kivy.kivy_exporter import KivyExporter
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        src = ROOT / "samples" / "reseau_2"
        data = json.loads((src / "project.json").read_text(encoding="utf-8"))
        out = Path(tempfile.mkdtemp(prefix="kivy_mp_")) / "export"
        assert KivyExporter(data, src, out).export()
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None
    return out / "game"


def test_the_session_modules_and_glue_are_shipped(export_dir):
    shipped = {p.name for p in (export_dir / "mp_lan").glob("*.py")}
    assert shipped == {"__init__.py", "state.py", "framing.py", "network.py", "replication.py",
                       "ws_transport.py", "session.py", "glue.py"}
    ext = ROOT / "extensions" / "multiplayer_lan"
    for name in ("state", "framing", "network", "replication", "ws_transport", "session"):
        assert (export_dir / "mp_lan" / f"{name}.py").read_bytes() == (ext / f"{name}.py").read_bytes()


def test_generated_code_calls_the_glue_and_every_module_compiles(export_dir):
    for f in export_dir.rglob("*.py"):
        compile(f.read_text(encoding="utf-8"), str(f), "exec")
    quiz = (export_dir / "objects" / "obj_quiz.py").read_text(encoding="utf-8")
    assert "from mp_lan.glue import join; join('auto', 45782, '')" in quiz
    assert "from mp_lan.glue import send_message; send_message('reponse', 'A', 'host')" in quiz
    assert "from mp_lan.glue import unsupported; unsupported('host_game')" in quiz
    assert "def on_network_message(self):" in quiz and "def on_network_game_started(self):" in quiz
    scene = (export_dir / "scenes" / "room0.py").read_text(encoding="utf-8")
    assert "def _ext_update__multiplayer_lan(self, dt):" in scene


def test_the_core_logger_stand_in_makes_the_package_importable_without_the_ide(export_dir):
    code = ("import sys; sys.path.insert(0, %r); import mp_lan.glue as g; "
            "from mp_lan.session import NetworkSession; print('ok', g.active())" % str(export_dir))
    done = subprocess.run([sys.executable, "-I", "-c", code], cwd=str(export_dir.parent),
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0 and done.stdout.strip() == "ok False", done.stderr


# ---------------------------------------------------------------- stand-ins

class _App:
    def __init__(self):
        self.globals = {}


class _Inst:
    def __init__(self, scene, name):
        self.scene, self.object_name = scene, name
        self.x = self.y = 0
        self.image_height = 32
        self.image_index = 0.0
        self.visible = True
        self.solid = False                     # an "engine" attribute
        self.events = []

    def __getattr__(self, name):
        if name.startswith("on_"):
            def handler(name=name):
                self.events.append(name)
            if name[3:] in self.scene.handles:
                return handler
        raise AttributeError(name)


class _Scene:
    room_height = 400

    def __init__(self, handles=()):
        self.instances, self._pending_creates, self.handles = [], [], set(handles)
        self.created = []

    def create_instance(self, name, x, y):
        if name == "obj_missing":
            return None
        inst = _Inst(self, name)
        inst.x, inst.y = x, y
        self.instances.append(inst)
        self._pending_creates.append(inst)
        self.created.append(inst)
        return inst

    def destroy_instance(self, inst):
        if inst in self.instances:
            self.instances.remove(inst)


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
    for name in [n for n in sys.modules if n == "mp_lan" or n.startswith("mp_lan.")]:
        monkeypatch.delitem(sys.modules, name)
    import mp_lan.glue as g
    g.leave()
    g._warned.clear()
    yield g, app
    g.leave()
    for name in [n for n in sys.modules if n == "mp_lan" or n.startswith("mp_lan.")]:
        sys.modules.pop(name, None)


def _host():
    host = NetworkSession(mode="host", port=0, player_name="Prof")
    host.start()
    return host


def _run(g, scene, host, rounds=30):
    for _ in range(rounds):
        host.pump_before_step()
        g.update(scene)
        host.pump_after_update()
        time.sleep(0.004)


def _join(g, scene, host, name="Ada"):
    g.join("127.0.0.1", host.bound_port, name)
    assert g.active()
    _run(g, scene, host, 40)


# ---------------------------------------------------------------- Tier A

def test_join_gives_identity_globals_and_the_started_event(glue):
    g, app = glue
    host, scene = _host(), _Scene({"network_started", "player_joined"})
    inst = _Inst(scene, "obj_quiz")
    scene.instances.append(inst)
    try:
        _join(g, scene, host)
        assert app.globals["player_id"] == 1 and app.globals["player_count"] == 2
        assert (app.globals["is_host"], app.globals["is_client"]) == (0, 1)
        assert app.globals["network_role"] == "client" and app.globals["network_connected"] == 1
        assert inst.events.count("on_network_started") == 1
    finally:
        g.leave()
        host.close()


def test_shared_variables_flow_both_ways_and_get_shared_var_reads_them(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        _join(g, scene, host)
        host.set_shared("etat", "question")
        _run(g, scene, host, 20)
        assert app.globals["etat"] == "question"
        g.set_shared("reponse_ada", "B")            # a client write is a request the host applies
        _run(g, scene, host, 20)
        assert host.get_shared("reponse_ada") == "B"
        g.get_shared_into("etat", "copy")
        assert app.globals["copy"] == "question"
        g.get_shared_into("nothing_here", "other")
        assert app.globals["other"] == 0
    finally:
        g.leave()
        host.close()


def test_messages_both_ways_set_the_network_globals(glue):
    g, app = glue
    host, scene = _host(), _Scene({"network_message"})
    inst = _Inst(scene, "obj_quiz")
    scene.instances.append(inst)
    try:
        _join(g, scene, host)
        host.send_message("ping", {"n": 3}, "all")
        _run(g, scene, host, 20)
        assert (app.globals["network_event"], app.globals["network_data"]) == ("ping", {"n": 3})
        assert app.globals["network_sender"] == 0       # the host
        assert "on_network_message" in inst.events
        g.send_message("reponse", "A", "host")
        host_events = []
        for _ in range(20):
            host.pump_before_step()
            g.update(scene)
            host.pump_after_update()
            host_events += host.take_events()
            time.sleep(0.004)
        assert ("network_message", "reponse", "A", 1) in host_events
    finally:
        g.leave()
        host.close()


def test_a_second_player_joining_fires_player_joined(glue):
    g, app = glue
    host, scene = _host(), _Scene({"player_joined"})
    inst = _Inst(scene, "obj_quiz")
    scene.instances.append(inst)
    other = NetworkSession(mode="client", host="127.0.0.1", port=host.bound_port, player_name="Bob")
    try:
        _join(g, scene, host)
        other.start()
        for _ in range(40):
            other.pump_before_step()
            other.pump_after_update()
            _run(g, scene, host, 1)
        assert "on_player_joined" in inst.events
        assert app.globals["network_player_name"] == "Bob" and app.globals["player_count"] == 3
    finally:
        other.close()
        g.leave()
        host.close()


# ---------------------------------------------------------------- ghosts

def _row(nid, x, y, **extra):
    return {"nid": nid, "o": "obj_ball", "x": x, "y": y, "r": 0, "f": 2, "v": True, **extra}


def test_a_host_instance_becomes_a_ghost_without_its_create_event(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        _join(g, scene, host)
        nid = host.next_netid()
        host.push_local_instances([_row(nid, 96, 64, vars={"hp": 5})])
        _run(g, scene, host, 40)
        assert len(scene.created) == 1
        ghost = scene.created[0]
        assert ghost.object_name == "obj_ball" and ghost._net_ghost == nid
        assert ghost not in scene._pending_creates           # its create event never runs
        # Kivy is y-up from the sprite's bottom-left: 400 - 64 - 32
        assert (ghost.x, ghost.y) == (96, 400 - 64 - 32)
        assert ghost.image_index == 2 and ghost.visible is True
        assert ghost.hp == 5
    finally:
        g.leave()
        host.close()


def test_a_ghost_follows_the_host_and_is_destroyed_with_it(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        _join(g, scene, host)
        nid = host.next_netid()
        host.push_local_instances([_row(nid, 0, 0)])
        _run(g, scene, host, 30)
        host.push_local_instances([_row(nid, 200, 100)])
        _run(g, scene, host, 60)
        ghost = scene.created[0]
        assert ghost.x == pytest.approx(200, abs=1.0) and ghost.y == pytest.approx(400 - 100 - 32, abs=1.0)
        host.push_local_instances([])
        _run(g, scene, host, 40)
        assert ghost not in scene.instances and not g._ghosts
    finally:
        g.leave()
        host.close()


def test_a_room_change_rebuilds_the_ghosts_in_the_new_scene(glue):
    g, app = glue
    host, scene_a = _host(), _Scene()
    try:
        _join(g, scene_a, host)
        nid = host.next_netid()
        host.push_local_instances([_row(nid, 32, 32)])
        _run(g, scene_a, host, 30)
        scene_b = _Scene()
        _run(g, scene_b, host, 30)
        assert len(scene_b.created) == 1 and scene_b.created[0]._net_ghost == nid
    finally:
        g.leave()
        host.close()


def test_replicated_vars_cannot_overwrite_engine_attributes(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        _join(g, scene, host)
        nid = host.next_netid()
        host.push_local_instances([_row(nid, 0, 0, vars={
            "solid": 1, "x": 999, "visible": 0, "scene": "boom", "_secret": 1,
            "image_height": 1, "hp": 7})])
        _run(g, scene, host, 40)
        ghost = scene.created[0]
        assert ghost.solid is False and ghost.scene is scene and ghost.image_height == 32
        assert ghost.visible is True and not hasattr(ghost, "_secret")
        assert ghost.hp == 7                                 # a genuine author var still arrives
    finally:
        g.leave()
        host.close()


def test_an_unknown_ghost_object_is_skipped_not_fatal(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        _join(g, scene, host)
        nid = host.next_netid()
        host.push_local_instances([{"nid": nid, "o": "obj_missing", "x": 0, "y": 0, "r": 0, "f": 0, "v": True}])
        _run(g, scene, host, 40)
        assert not g._ghosts
    finally:
        g.leave()
        host.close()


# ---------------------------------------------------------------- loss, leave, limits

def test_losing_the_host_destroys_the_ghosts_and_fires_connection_lost(glue):
    g, app = glue
    host, scene = _host(), _Scene({"connection_lost"})
    watcher = _Inst(scene, "obj_quiz")
    scene.instances.append(watcher)
    try:
        _join(g, scene, host)
        nid = host.next_netid()
        host.push_local_instances([_row(nid, 0, 0)])
        _run(g, scene, host, 30)
        ghost = scene.created[0]
        host.close()
        for _ in range(60):
            g.update(scene)
            time.sleep(0.005)
        assert app.globals["network_connected"] == 0
        assert "on_connection_lost" in watcher.events
        assert ghost not in scene.instances
    finally:
        g.leave()


def test_leave_game_closes_the_session_and_clears_the_identity_globals(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        _join(g, scene, host)
        assert "player_id" in app.globals
        g.leave(scene)
        assert not g.active() and "player_id" not in app.globals and "network_connected" not in app.globals
        g.update(scene)                                      # a no-op, no crash
    finally:
        host.close()


def test_joining_an_unreachable_host_never_raises(glue):
    g, app = glue
    g.join("127.0.0.1", 9, "Ada")        # nothing listens on the discard port
    for _ in range(10):
        g.update(_Scene())
        time.sleep(0.01)
    # either never started, or lost at once -- the game just carries on
    assert app.globals.get("network_connected", 0) == 0


def test_what_a_phone_cannot_do_warns_once_and_changes_nothing(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        g.unsupported("host_game")
        g.unsupported("host_game")
        g.unsupported("network_spawn")
        assert {"host_game", "network_spawn"} <= g._warned and not g.active()
        g.join("auto", 45782, "Ada")                         # LAN discovery is desktop-only
        assert not g.active()
        _join(g, scene, host)
        assert g.is_owner(object()) is False                 # in a session a phone owns nothing
        g.leave()
        assert g.is_owner(object()) is True                  # single player: you own everything
    finally:
        g.leave()
        host.close()


# ---------------------------------------------------------------- real Kivy

def test_under_real_kivy_the_scene_hook_joins_and_spawns_a_real_ghost(tmp_path):
    """The generated scene's own update hook + the glue + REAL widgets, against a real host."""
    from export.Kivy.kivy_exporter import KivyExporter
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        src = ROOT / "samples" / "reseau_1"
        data = json.loads((src / "project.json").read_text(encoding="utf-8"))
        out = tmp_path / "export"
        assert KivyExporter(data, src, out).export()
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None
    result = tmp_path / "result.json"
    try:
        proc = subprocess.run([sys.executable, str(ROOT / "tests" / "_real_kivy_multiplayer.py"),
                               str(out / "game"), str(ROOT), str(result)],
                              capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        pytest.skip("real Kivy worker timed out")
    if not result.exists():
        pytest.skip(f"real Kivy cannot run here: {proc.stderr[-300:]}")
    data = json.loads(result.read_text(encoding="utf-8"))
    if data["error"] and any(s in data["error"] for s in ("No module named 'kivy'", "GL", "window", "Window")):
        pytest.skip("real Kivy cannot open a window here: " + data["error"][-200:])
    assert data["error"] is None, data["error"]
    assert data["player_id"] == 1
    assert len(data["ghosts"]) == 1
    g = data["ghosts"][0]
    assert g["object"] == "obj_person" and g["x"] == pytest.approx(128, abs=2)
    assert g["y"] == pytest.approx(g["room_height"] - 96 - g["image_height"], abs=2)
    # ...and it is THIS player's avatar: promoted, driven by the real generated step event
    # (is_instance_owner + key_pressed) with the right arrow held, reported up to the host.
    assert data["promoted"] is True
    assert data["avatar_moved"] > 20, data["avatar_moved"]
    assert data["held_right"] is True and data["released_right"] is False
    rows = data["own_rows"]
    assert rows and all(r["from"] == 1 for r in rows)
    assert max(r["x"] for r in rows) > 128 + 20
    assert all(r["y"] == pytest.approx(96, abs=2) for r in rows)      # wire y is the room's y-down 96
    # holding UP (`y = y - 4`): a larger Kivy y on screen, and a SMALLER y on the wire
    assert data["up_kivy_y_delta"] > 10, data["up_kivy_y_delta"]
    assert data["up_wire_y_after"] < data["up_wire_y_before"] - 10


# ---------------------------------------------------------------- the owned avatar

def _own_row(nid, x, y, owner):
    return {"nid": nid, "o": "obj_ball", "x": x, "y": y, "r": 0, "f": 0, "v": True, "own": owner}


def _run_until(g, scene, host, done, seconds=3.0):
    """Pump until done() -- paced reports (kivy_glue throttles them) need real time, not a frame count."""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        host.pump_before_step()
        g.update(scene)
        host.pump_after_update()
        if done():
            return True
        time.sleep(0.004)
    return done()


def test_the_avatar_the_host_assigned_is_promoted_owned_and_starts_where_the_host_put_it(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        _join(g, scene, host)
        mine, theirs = host.next_netid(), host.next_netid()
        host.push_local_instances([_own_row(mine, 96, 64, 1), _own_row(theirs, 200, 40, 0)])
        _run(g, scene, host, 40)
        assert g._local == {mine} and len(scene.created) == 2
        avatar = next(i for i in scene.created if i._net_ghost == mine)
        puppet = next(i for i in scene.created if i._net_ghost == theirs)
        assert (avatar.x, avatar.y) == (96, 400 - 64 - 32)          # not left in the corner
        assert g.is_owner(avatar) is True and g.is_owner(puppet) is False
        assert g.is_owner(_Inst(scene, "obj_placed")) is False      # a room-placed instance has no owner
    finally:
        g.leave()
        host.close()


def test_the_owner_moves_its_avatar_and_the_host_hears_it_in_room_coordinates(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    reports = []
    try:
        _join(g, scene, host)
        nid = host.next_netid()
        host.push_local_instances([_own_row(nid, 96, 64, 1)])
        _run(g, scene, host, 40)
        avatar = scene.created[0]

        def step():
            avatar.x += 4                      # the avatar's own events move it, in Kivy coordinates
            reports.extend(host.take_own_state().values())
            return any(r["x"] > 96 + 30 for r in reports)
        assert _run_until(g, scene, host, step)
        last = reports[-1]
        assert last["_from"] == 1 and last["y"] == 64          # wire y is the room's y-down 64
        assert avatar.x > 96 + 30                              # and the glue never overwrote it
    finally:
        g.leave()
        host.close()


def test_a_puppet_is_never_reported_up(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    reports = []
    try:
        _join(g, scene, host)
        nid = host.next_netid()
        host.push_local_instances([_own_row(nid, 300, 40, 0)])

        def step():
            reports.extend(host.take_own_state().values())
            return False
        _run_until(g, scene, host, step, seconds=1.0)
        assert not reports and not g._local
    finally:
        g.leave()
        host.close()


def test_held_keys_reach_the_host_as_named_inputs_and_a_dropped_report_is_refreshed(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    scene.keys_pressed = {}
    try:
        _join(g, scene, host)
        nid = host.next_netid()
        host.push_local_instances([_own_row(nid, 96, 64, 1)])
        _run(g, scene, host, 20)
        scene.keys_pressed[275] = True                         # the right arrow's Kivy keycode
        assert _run_until(g, scene, host, lambda: host.remote_input(1, "right"))
        scene.keys_pressed[275] = False
        assert _run_until(g, scene, host, lambda: not host.remote_input(1, "right"))
        # a lost report heals: wipe what the host believes, the refresh puts it back
        scene.keys_pressed[32] = True                          # space
        assert _run_until(g, scene, host, lambda: host.remote_input(1, "space"))
        host._input_state[1] = set()
        assert _run_until(g, scene, host, lambda: host.remote_input(1, "space"), seconds=2.0)
    finally:
        g.leave()
        host.close()


def test_bind_network_input_and_set_sync_rate(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    scene.keys_pressed = {97: True}                            # 'a'
    try:
        g.set_sync_rate(250)                                   # before joining: applied on join
        g.bind("fire", "A")
        g.bind("jump", "K_SPACE")
        g.bind("go", "ctrl")
        _join(g, scene, host)
        assert g._session.interp_delay == pytest.approx(0.25)
        assert g._held_inputs(scene) == ["fire"]
        scene.keys_pressed = {32: True}
        assert g._held_inputs(scene) == ["jump", "space"]
        g.set_sync_rate(40)
        assert g._session.interp_delay == pytest.approx(0.04)
        g.set_sync_rate("junk")                                # ignored
        assert g._session.interp_delay == pytest.approx(0.04)
    finally:
        g._bindings.clear()
        g._bindings.update({"left": "left", "right": "right", "up": "up", "down": "down", "space": "space"})
        g._interp_ms = None
        g.leave()
        host.close()


def test_losing_the_host_keeps_the_players_own_avatar_and_drops_the_puppets(glue):
    g, app = glue
    host, scene = _host(), _Scene()
    try:
        _join(g, scene, host)
        mine, theirs = host.next_netid(), host.next_netid()
        host.push_local_instances([_own_row(mine, 96, 64, 1), _own_row(theirs, 200, 40, 0)])
        _run(g, scene, host, 40)
        avatar = next(i for i in scene.created if i._net_ghost == mine)
        puppet = next(i for i in scene.created if i._net_ghost == theirs)
        host.close()
        for _ in range(80):
            g.update(scene)
            time.sleep(0.004)
        assert app.globals["network_connected"] == 0
        assert avatar in scene.instances and puppet not in scene.instances
        assert g._local == {mine}
    finally:
        g.leave()


def test_the_generated_code_binds_inputs_and_the_only_unsupported_ones_are_host_side(export_dir):
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("bind_network_input", {"name": "fire", "key": "a"}, "create")
    assert code == "from mp_lan.glue import bind; bind('fire', 'a')"
    code = gen._convert_simple_action("set_sync_rate", {"hz": 20, "interp_ms": 150}, "create")
    assert code == "from mp_lan.glue import set_sync_rate; set_sync_rate(150)"
    for name in ("host_game", "start_networked_game", "set_network_mode", "network_spawn",
                 "sync_instance", "set_instance_owner"):
        assert "unsupported" in gen._convert_simple_action(name, {}, "create"), name
