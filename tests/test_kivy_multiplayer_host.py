"""LAN multiplayer: a phone (the Kivy export) can HOST.

A device can listen on a socket, so ``mp_lan.glue`` runs the desktop's own host session: ``host_game``,
``start_networked_game``, ``network_spawn`` (an instance everyone sees, with an owner), host-owned
``sync_instance``, ``set_instance_owner``, ``remote_input``, and the older ``set_network_mode`` spectator mode.
Driven against REAL desktop peers (``NetworkSession`` / ``NetworkClient`` over 127.0.0.1) with the real
GameObject helpers from a real export. Not available on a phone: the waiting-room screen and the discovery
beacon (``show_lobby`` is ignored; the game reads the global ``host_address`` and shows it).
"""
import socket
import sys
import time
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402
from extensions.multiplayer_lan.session import NetworkSession  # noqa: E402
from test_if_condition_parity import kivy_base_methods  # noqa: E402,F401
from test_kivy_multiplayer_client import export_dir, glue  # noqa: E402,F401  (fixtures)

pytestmark = skip_without_pyside6
ROOM_H, IMG_H = 400, 32


class _World:
    """A scene whose instances carry the REAL generated helpers (_gm_y, _set_gm_y, _create_gm)."""

    def __init__(self, base_methods):
        ns = {}
        exec(compile(base_methods + "    pass\n", "<helpers>", "exec"), ns)
        self.cls = ns["_C"]
        self.room_height = ROOM_H
        self.keys_pressed = {}
        self.instances = []
        self.destroyed = []
        self.handles = {}

    def make(self, name="obj_ball", gm_x=0, gm_y=0, **attrs):
        inst = self.cls()
        inst.scene = self
        inst.image_height, inst.grid_size = IMG_H, 32
        inst.object_name = name
        inst.x, inst.y = gm_x, ROOM_H - gm_y - IMG_H
        inst.image_index, inst.visible = 0.0, True
        inst.__dict__.update(attrs)
        inst.events = []
        for event in ("player_joined", "player_left", "network_message", "network_game_started",
                      "network_started"):
            setattr(inst, "on_" + event, (lambda e=event, i=inst: i.events.append(e)))
        self.instances.append(inst)
        return inst

    def create_instance(self, name, x, y):
        inst = self.make(name, x, 0)
        inst.y = y
        return inst

    def destroy_instance(self, inst):
        if inst in self.instances:
            self.instances.remove(inst)
        self.destroyed.append(inst)


@pytest.fixture()
def world(kivy_base_methods):
    return _World(kivy_base_methods)


def _pump(g, scene, peers=(), rounds=40):
    for _ in range(rounds):
        for p in peers:
            p.pump_before_step()
        g.update(scene)
        for p in peers:
            p.pump_after_update()
        time.sleep(0.004)


def _until(g, scene, peers, done, seconds=3.0):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        _pump(g, scene, peers, rounds=1)
        if done():
            return True
    return done()


def _joiner(g, name="Ada"):
    peer = NetworkSession(mode="client", host="127.0.0.1", port=g._session.bound_port, player_name=name)
    peer.start()
    return peer


def _hosted(g, world, peers_needed=0):
    g.host(0, "Prof", 4, False)
    assert g.active() and g._session.mode == "host"
    peers = [_joiner(g, f"P{i}") for i in range(peers_needed)]
    return peers


# ---------------------------------------------------------------- starting a host

def test_host_game_listens_and_sets_the_identity_globals_and_the_address(glue, world):
    g, app = glue
    try:
        g.host(0, "Prof", 4, False)
        assert g.active() and g._session.mode == "host" and g._session.bound_port > 0
        _pump(g, world, rounds=3)
        assert (app.globals["is_host"], app.globals["is_client"], app.globals["player_id"]) == (1, 0, 0)
        assert (app.globals["player_count"], app.globals["network_role"], app.globals["network_connected"]) == (1, "host", 1)
        assert app.globals["host_address"].endswith(":%d" % g._session.bound_port)
        assert g._session.player_name == "Prof"
    finally:
        g.leave()


def test_a_busy_port_never_raises_and_hosts_nothing(glue, world):
    g, app = glue
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("", 0))
    blocker.listen(1)
    try:
        g.host(blocker.getsockname()[1], "Prof", 4, False)
        assert not g.active() and "host_address" not in app.globals
    finally:
        blocker.close()
        g.leave()


def test_leave_game_frees_the_port_and_clears_the_address(glue, world):
    g, app = glue
    g.host(0, "Prof", 4, False)
    port = g._session.bound_port
    _pump(g, world, rounds=2)
    g.leave(world)
    assert not g.active() and "host_address" not in app.globals and "player_id" not in app.globals
    again = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        again.bind(("", port))                                      # the listening socket was really closed
    finally:
        again.close()


def test_the_waiting_room_screen_is_desktop_only_and_warns_once(glue, world):
    g, app = glue
    try:
        g.host(0, "Prof", 4, True)
        assert "lobby" in g._warned and g.active()
    finally:
        g.leave()


# ---------------------------------------------------------------- players, state and messages

def test_players_join_and_the_events_fire_on_the_scene(glue, world):
    g, app = glue
    watcher = world.make("obj_ctrl")
    try:
        g.host(0, "Prof", 4, False)
        peer = _joiner(g, "Ada")
        assert _until(g, world, [peer], lambda: app.globals.get("player_count") == 2 and peer.player_id >= 0)
        assert peer.player_id == 1 and "player_joined" in watcher.events
        assert app.globals["network_player_name"] == "Ada" and app.globals["network_sender"] == 1
    finally:
        g.leave()


def test_start_networked_game_reaches_the_clients(glue, world):
    g, app = glue
    try:
        g.host(0, "Prof", 4, False)
        peer = _joiner(g)
        events = []
        _until(g, world, [peer], lambda: peer.player_id >= 0)
        g.start_networked_game()
        assert _until(g, world, [peer], lambda: (events.extend(peer.take_events()),
                                                 any(e[0] == "network_game_started" for e in events))[1])
    finally:
        g.leave()


def test_shared_variables_and_messages_go_both_ways(glue, world):
    g, app = glue
    watcher = world.make("obj_ctrl")
    try:
        g.host(0, "Prof", 4, False)
        peer = _joiner(g)
        _until(g, world, [peer], lambda: peer.player_id >= 0)
        g.set_shared("etat", "question")
        assert _until(g, world, [peer], lambda: peer.shared.get("etat") == "question")
        peer.set_shared("reponse", "B")                             # a client write is a request the host applies
        assert _until(g, world, [peer], lambda: app.globals.get("reponse") == "B")
        g.send_message("ping", {"n": 1}, "all")
        got = []
        assert _until(g, world, [peer], lambda: (got.extend(peer.take_events()),
                                                 any(e[0] == "network_message" for e in got))[1])
        peer.send_message("pong", 7, "host")
        assert _until(g, world, [peer], lambda: app.globals.get("network_event") == "pong")
        assert (app.globals["network_data"], app.globals["network_sender"]) == (7, 1)
        assert "network_message" in watcher.events
    finally:
        g.leave()


# ---------------------------------------------------------------- networked instances

def test_network_spawn_creates_an_instance_everyone_sees_with_an_owner(glue, world):
    g, app = glue
    caller = world.make("obj_ctrl")
    try:
        g.host(0, "Prof", 4, False)
        peer = _joiner(g)
        _until(g, world, [peer], lambda: peer.player_id >= 0)
        spawned = g.network_spawn(caller, "obj_ball", 120, 80, 1)          # the author's position
        assert spawned is not None and spawned.object_name == "obj_ball" and spawned._net_owner == 1
        assert (spawned.x, ROOM_H - spawned.y - IMG_H) == (120, 80)
        creates = []
        assert _until(g, world, [peer], lambda: (creates.extend(peer.take_ghost_changes()[0]), bool(creates))[1])
        nid, obj, x, y = creates[0]
        assert (obj, x, y) == ("obj_ball", 120, 80) and peer.ghost_owner(nid) == 1
        assert nid == spawned._net_id
    finally:
        g.leave()


def test_the_owner_moves_its_instance_and_a_forged_claim_is_refused(glue, world):
    g, app = glue
    caller = world.make("obj_ctrl")
    try:
        g.host(0, "Prof", 4, False)
        mine, other = _joiner(g, "Ada"), _joiner(g, "Bo")
        _until(g, world, [mine, other], lambda: mine.player_id >= 0 and other.player_id >= 0)
        owned = g.network_spawn(caller, "obj_ball", 10, 10, mine.player_id)
        hosts = g.network_spawn(caller, "obj_ball", 50, 50, 0)
        row = lambda nid, x, y: {"nid": nid, "x": x, "y": y, "r": 0, "f": 2, "v": True}  # noqa: E731
        mine.push_own_instances([row(owned._net_id, 123, 77)])
        assert _until(g, world, [mine, other], lambda: owned.x == 123)
        assert ROOM_H - owned.y - IMG_H == 77 and owned.image_index == 2          # the owner's state, y flipped
        other.push_own_instances([row(owned._net_id, 999, 999), row(hosts._net_id, 999, 999)])   # not theirs
        _pump(g, world, [mine, other], rounds=40)
        assert owned.x == 123 and hosts.x == 50
    finally:
        g.leave()


def test_a_host_synced_room_instance_replicates_with_its_listed_variables(glue, world):
    g, app = glue
    ball = world.make("obj_ball", 30, 40, hp=5, secret=1)
    try:
        g.host(0, "Prof", 4, False)
        peer = _joiner(g)
        _until(g, world, [peer], lambda: peer.player_id >= 0)
        g.sync_instance(ball, "hp")
        assert ball._net_id == "obj_ball#0" and ball._net_owner == 0
        assert g.is_owner(ball) is True                                # the host's own instance
        seen = []
        _until(g, world, [peer], lambda: (seen.extend(peer.take_ghost_changes()[0]), bool(seen))[1])
        nid = seen[0][0]
        assert nid == "obj_ball#0" and peer.ghost_vars(nid) == {"hp": 5}          # only what was listed
    finally:
        g.leave()


def test_set_instance_owner_hands_an_instance_to_a_player(glue, world):
    g, app = glue
    ball = world.make("obj_ball", 30, 40)
    try:
        g.host(0, "Prof", 4, False)
        peer = _joiner(g)
        _until(g, world, [peer], lambda: peer.player_id >= 0)
        g.sync_instance(ball, "")
        _until(g, world, [peer], lambda: bool(peer.ghost_ids()))
        assert peer.ghost_owner("obj_ball#0") == 0
        g.set_instance_owner(ball, 1)
        assert _until(g, world, [peer], lambda: peer.ghost_owner("obj_ball#0") == 1)
        assert g.is_owner(ball) is False                              # no longer the host's
    finally:
        g.leave()


def test_a_destroyed_replicated_instance_is_dropped_and_despawns_on_clients(glue, world):
    g, app = glue
    caller = world.make("obj_ctrl")
    try:
        g.host(0, "Prof", 4, False)
        peer = _joiner(g)
        _until(g, world, [peer], lambda: peer.player_id >= 0)
        spawned = g.network_spawn(caller, "obj_ball", 5, 5, 0)
        _until(g, world, [peer], lambda: bool(peer.ghost_ids()))
        world.destroy_instance(spawned)
        assert _until(g, world, [peer], lambda: not peer.ghost_ids() or bool(peer.take_ghost_changes()[1]))
        assert not g._host_synced
    finally:
        g.leave()


def test_spawning_replicates_only_on_the_host(glue, world):
    g, app = glue
    caller = world.make("obj_ctrl")
    host = NetworkSession(mode="host", port=0, player_name="Prof")
    host.start()
    try:
        g.join("127.0.0.1", host.bound_port, "Ada")
        _pump(g, world, [host], rounds=20)
        assert g.network_spawn(caller, "obj_ball", 1, 1, 0) is None and len(world.instances) == 1
        g.start_networked_game()                                     # host-only: a quiet no-op here
        assert g.remote_input(0, "left") is False
    finally:
        g.leave()
        host.close()


# ---------------------------------------------------------------- named input

def test_remote_input_sees_what_a_client_and_the_host_hold(glue, world):
    g, app = glue
    try:
        g.host(0, "Prof", 4, False)
        peer = _joiner(g)
        _until(g, world, [peer], lambda: peer.player_id >= 0)
        peer.send_input(["right", "space"])
        assert _until(g, world, [peer], lambda: g.remote_input(1, "right"))
        assert g.remote_input(1, "space") and not g.remote_input(1, "left")
        assert not g.remote_input(0, "right")
        world.keys_pressed[275] = True                                # the host's own right arrow
        assert _until(g, world, [peer], lambda: g.remote_input(0, "right"))
    finally:
        g.leave()


# ---------------------------------------------------------------- the older spectator mode

def test_set_network_mode_host_broadcasts_positions_to_a_desktop_client(glue, world):
    from extensions.multiplayer_lan.network import NetworkClient
    g, app = glue
    a, b = world.make("obj_a", 10, 20), world.make("obj_b", 100, 50)
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    client = NetworkClient("127.0.0.1", port=port)
    try:
        g.set_network_mode("host", "", port)
        assert g.active() and g._session is None
        client.connect()
        a.x, b.visible = 33, False
        snap = None
        end = time.monotonic() + 3
        while time.monotonic() < end and not snap:
            _pump(g, world, rounds=2)
            snap = client.poll()
        rows = {row[0]: row for row in snap["i"]}
        assert rows[0][1:3] == [33, 20] and rows[1][1:3] == [100, 50] and rows[1][5] is False
    finally:
        client.close()
        g.leave()


def test_set_network_mode_client_copies_a_desktop_hosts_positions(glue, world):
    from extensions.multiplayer_lan.network import NetworkHost
    g, app = glue
    a, b = world.make("obj_a", 0, 0), world.make("obj_b", 0, 0)
    host = NetworkHost(port=0)
    host.start()
    port = host._listen_sock.getsockname()[1]
    try:
        g.set_network_mode("client", "127.0.0.1", port)
        end = time.monotonic() + 3
        while time.monotonic() < end and a.x != 64:
            host.broadcast_snapshot([(0, 64, 96, 0, 3, True), (1, 8, 9, 0, 0, False)])
            _pump(g, world, rounds=2)
        assert (a.x, ROOM_H - a.y - IMG_H, a.image_index) == (64, 96, 3)
        assert (b.x, b.visible) == (8, False)
    finally:
        host.close()
        g.leave()


def test_set_network_mode_with_nothing_to_connect_to_never_raises(glue, world):
    g, app = glue
    world.make("obj_a")
    g.set_network_mode("client", "127.0.0.1", 9)
    for _ in range(5):
        g.update(world) if g.active() else None
    g.set_network_mode("nonsense", "", 0)
    g.leave()


# ---------------------------------------------------------------- the generated code

def test_the_generated_code_for_the_host_actions(export_dir):
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator()
    code = lambda a, p: gen._convert_simple_action(a, p, "create")  # noqa: E731
    assert code("host_game", {"port": 4000, "player_name": "Prof", "max_players": 6, "show_lobby": True}) == \
        "from mp_lan.glue import host; host(4000, 'Prof', 6, True, 'PyGameMaker')"
    assert code("start_networked_game", {}) == "from mp_lan.glue import start_networked_game; start_networked_game()"
    assert code("set_network_mode", {"mode": "client", "host": "10.0.0.5", "port": 4000}) == \
        "from mp_lan.glue import set_network_mode; set_network_mode('client', '10.0.0.5', 4000)"
    assert code("network_spawn", {"object": "obj_ball", "x": 120, "y": 80, "owner": "player_id"}) == \
        "from mp_lan.glue import network_spawn; network_spawn(self, 'obj_ball', 120, 80, (self.player_id))"
    rel = code("network_spawn", {"object": "obj_ball", "x": 5, "y": 8, "relative": True, "owner": 0})
    assert "network_spawn(self, 'obj_ball', self.x + 5, self._gm_y() + 8, 0)" in rel


def test_remote_input_is_a_real_condition_now(export_dir):
    sys.path.insert(0, str(ROOT))
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        gen = code_generator.ActionCodeGenerator()
        gen.process_action({"action_type": "remote_input", "parameters": {"player": 1, "name": "left"}}, "step")
        gen.process_action({"action_type": "set_variable", "parameters": {"variable": "hit", "value": "1"}}, "step")
        assert "remote_input(1, 'left')" in gen.get_code()
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None


def test_the_kivy_generator_no_longer_reports_any_unsupported_network_action():
    sys.path.insert(0, str(ROOT))
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        code_generator.reset_unsupported_actions()
        gen = code_generator.ActionCodeGenerator()
        for name in ("host_game", "join_game", "leave_game", "start_networked_game", "set_shared_var",
                     "get_shared_var", "send_network_message", "network_spawn", "sync_instance",
                     "set_instance_owner", "bind_network_input", "set_sync_rate", "set_network_mode"):
            gen.process_action({"action_type": name, "parameters": {}}, "create")
        assert code_generator.get_unsupported_actions() == []
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None


# ---------------------------------------------------------------- real Kivy

def test_under_real_kivy_a_phone_hosts_and_spawns_a_real_networked_instance(tmp_path):
    """The generated scene's own update hook + the glue + REAL widgets (a real sprite), against a real client."""
    import json
    import subprocess
    pytest.importorskip("kivy")
    from export.Kivy.kivy_exporter import KivyExporter
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        src = ROOT / "samples" / "reseau_1"
        out = tmp_path / "export"
        assert KivyExporter(json.loads((src / "project.json").read_text(encoding="utf-8")), src, out).export()
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None
    result = tmp_path / "result.json"
    try:
        proc = subprocess.run([sys.executable, str(ROOT / "tests" / "_real_kivy_host.py"),
                               str(out / "game"), str(ROOT), str(result)],
                              capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        pytest.skip("real Kivy worker timed out")
    if not result.exists():
        pytest.skip(f"real Kivy cannot run here: {proc.stderr[-300:]}")
    data = json.loads(result.read_text(encoding="utf-8"))
    if data["error"] and any(s in data["error"] for s in ("No module named 'kivy'", "GL", "Window")):
        pytest.skip("real Kivy cannot open a window here: " + data["error"][-200:])
    assert data["error"] is None, data["error"]
    assert data["player_count"] == 2
    assert data["spawned"] == {"object": "obj_person", "x": 96.0, "gm_y": 64.0, "owner": 1, "has_sprite": True}
    assert len(data["client_saw"]) == 1
    nid, obj, x, y = data["client_saw"][0]
    assert (obj, x, y) == ("obj_person", 96, 64) and data["client_owner"] == 1
