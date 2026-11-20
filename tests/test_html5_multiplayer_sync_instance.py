"""HTML5 export: sync_instance and set_instance_owner on the browser LAN client.

A browser can take part in an instance PLACED IN THE ROOM. ``sync_instance`` registers it under the desktop's own
id scheme (``<object>#<ordinal>``, counted per room per object in call order); it follows the host's copy (unless the
host gave it to this player, in which case it runs in the page and is reported up) and stands in for the puppet the
snapshot would spawn. ``set_instance_owner`` is the host's decision: in a page it only sets the local owner, which
the next snapshot overrides, as on the desktop client.

Always runs: structure. On the dev box (Playwright + Chromium): a real export joins a REAL desktop host over
127.0.0.1 (its WebSocket side).
"""
import re
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

JS = (ROOT / "extensions" / "multiplayer_lan" / "export_html5.js").read_text(encoding="utf-8")


# -- structure (always runs) -------------------------------------------------------------------------

def test_the_two_actions_are_real_and_only_network_spawn_is_still_host_only():
    assert "registerExtensionAction('sync_instance'" in JS
    assert "registerExtensionAction('set_instance_owner'" in JS
    assert "registerExtensionAction('network_spawn'" in JS
    assert "for (const name of ['network_spawn', 'sync_instance'" not in JS
    assert "inst.name + '#' + count" in JS                     # the desktop's <object>#<ordinal>


def test_replicated_variables_never_overwrite_engine_attributes():
    loop = JS[JS.index("// Replicated variables: plain values under an AUTHOR's name only"):][:700]
    assert "pyIsAuthorVar(key)" in loop and "listedNames.indexOf(key) < 0" in loop


# -- real browser against a real host (dev box only) -----------------------------------------------------

@pytest.fixture(scope="module")
def exported():
    pytest.importorskip("playwright.sync_api")
    import events.plugin_loader as loader
    from export.HTML5.html5_exporter import HTML5Exporter
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    try:
        out = Path(tempfile.mkdtemp(prefix="html5_sync_")) / "out"
        out.mkdir(parents=True)
        assert HTML5Exporter().export(ROOT / "samples" / "reseau_1", out)
    finally:
        loader.list_available_extensions = original
    return next(out.glob("*.html"))


@pytest.fixture(scope="module")
def browser():
    sync_api = pytest.importorskip("playwright.sync_api")
    with sync_api.sync_playwright() as pw:
        try:
            chromium = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"no Chromium: {exc}")
        yield chromium
        chromium.close()


@pytest.fixture()
def session(browser, exported):
    """A fresh desktop host (pumped on a thread) and a fresh page that has joined it."""
    from extensions.multiplayer_lan.session import NetworkSession
    host = NetworkSession(mode="host", port=0, player_name="Prof")
    host.start()
    if not host.bound_ws_port:
        host.close()
        pytest.skip("the host's WebSocket listener could not bind here")
    reports, stop = [], threading.Event()

    def pump():
        while not stop.is_set():
            host.pump_before_step()
            reports.extend(row for row in host.take_own_state().values())
            host.pump_after_update()
            time.sleep(0.004)

    thread = threading.Thread(target=pump, daemon=True)
    thread.start()
    page = browser.new_page()
    page.goto(exported.as_uri())
    page.wait_for_function("window.game && window.game.currentRoom", timeout=20000)
    page.evaluate("window.game.currentRoom.instances = []")
    page.evaluate("_mpClient(window.game).join('127.0.0.1', %d, 'Ada')" % host.bound_ws_port)
    page.wait_for_function("_mpClient(window.game).playerId >= 0", timeout=8000)
    yield page, host, reports
    stop.set()
    thread.join(timeout=2)
    page.close()
    host.close()


def _place(page, name="obj_ball", x=0, y=0, **attrs):
    """A room-placed instance, as a loaded room would hold it; returns its index in room.instances."""
    return page.evaluate("""([name, x, y, attrs]) => {
        const room = window.game.currentRoom;
        const inst = new GameObject(name, x, y, {}, {});
        Object.assign(inst, attrs);
        inst._gameRef = window.game;
        room.instances.push(inst);
        return room.instances.length - 1;
    }""", [name, x, y, attrs])


def _act(page, index, action, params):
    page.evaluate("([i, a, p]) => window.game.currentRoom.instances[i].executeAction({action: a, parameters: p}, window.game)",
                  [index, action, params])


def _inst(page, index, expr):
    return page.evaluate(f"(i) => {{ const o = window.game.currentRoom.instances[i]; return {expr}; }}", index)


def _row(nid, x, y, owner, **extra):
    return {"nid": nid, "o": "obj_ball", "x": x, "y": y, "r": 0, "f": 1, "v": True, "own": owner, **extra}


def test_a_synced_room_instance_follows_the_host_and_is_not_also_spawned(session):
    page, host, _ = session
    i = _place(page, x=0, y=0, hp=5, colour="red")
    _act(page, i, "sync_instance", {"vars": "hp, colour"})
    assert _inst(page, i, "[o._netId, o._netOwner]") == ["obj_ball#0", 0]
    host.push_local_instances([_row("obj_ball#0", 200, 100, 0, vars={"hp": 9, "colour": "blue", "secret": 1})])
    page.wait_for_function("window.game.currentRoom.instances[0].x > 150", timeout=8000)
    page.wait_for_timeout(300)
    x, y, frame, hp, colour, secret = _inst(page, i, "[o.x, o.y, o.image_index, o.hp, o.colour, o.secret]")
    assert (round(x), round(y), frame, hp, colour, secret) == (200, 100, 1, 9, "blue", None)   # only the listed names
    assert page.evaluate("window.game.currentRoom.instances.length") == 1                     # no duplicate puppet


def test_ids_are_the_object_name_and_an_ordinal_in_call_order(session):
    page, host, _ = session
    a, b, c = _place(page, "obj_ball"), _place(page, "obj_ball"), _place(page, "obj_coin")
    for idx in (a, b, c):
        _act(page, idx, "sync_instance", {})
    assert [_inst(page, idx, "o._netId") for idx in (a, b, c)] == ["obj_ball#0", "obj_ball#1", "obj_coin#0"]
    _act(page, a, "sync_instance", {})                                  # idempotent
    assert _inst(page, a, "o._netId") == "obj_ball#0"
    assert page.evaluate("_mpClient(window.game).synced.size") == 3


def test_an_instance_the_host_gave_this_player_runs_here_and_is_reported_up(session):
    page, host, reports = session
    i = _place(page, x=40, y=60, hp=5)
    _act(page, i, "sync_instance", {"vars": "hp"})
    host.push_local_instances([_row("obj_ball#0", 500, 500, 1)])        # owner 1 = this player
    page.wait_for_function("window.game.currentRoom.instances[0]._netOwner === 1", timeout=8000)
    page.evaluate("window.__mover = setInterval(() => { window.game.currentRoom.instances[0].x += 3; }, 20)")
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline and not any(r["nid"] == "obj_ball#0" and r["x"] > 70 for r in reports):
        time.sleep(0.05)
    page.evaluate("clearInterval(window.__mover)")
    mine = [r for r in reports if r["nid"] == "obj_ball#0"]
    assert mine and mine[-1]["_from"] == 1 and mine[-1]["vars"] == {"hp": 5}
    assert _inst(page, i, "o.x") < 400                                   # never pulled to the host's 500


def test_another_players_synced_instance_stays_a_puppet(session):
    page, host, reports = session
    i = _place(page)
    _act(page, i, "sync_instance", {})
    host.push_local_instances([_row("obj_ball#0", 120, 30, 2)])          # owner 2: another player
    page.wait_for_function("window.game.currentRoom.instances[0]._netOwner === 2", timeout=8000)
    page.wait_for_timeout(500)
    assert not [r for r in reports if r["nid"] == "obj_ball#0"]
    assert round(_inst(page, i, "o.x")) == 120


def test_without_a_session_nothing_is_registered_and_set_instance_owner_is_harmless(browser, exported):
    page = browser.new_page()
    try:
        page.goto(exported.as_uri())
        page.wait_for_function("window.game && window.game.currentRoom", timeout=20000)
        page.evaluate("window.game.currentRoom.instances = []")
        i = _place(page)
        _act(page, i, "sync_instance", {"vars": "hp"})
        _act(page, i, "set_instance_owner", {"player": "3"})
        assert _inst(page, i, "[o._netId, o._netOwner]") == [None, None]
    finally:
        page.close()


def test_set_instance_owner_sets_the_local_owner_and_a_snapshot_overrides_it(session):
    page, host, _ = session
    i = _place(page)
    _act(page, i, "sync_instance", {})
    _act(page, i, "set_instance_owner", {"player": "2"})
    assert _inst(page, i, "o._netOwner") == 2
    _act(page, i, "set_instance_owner", {"player": "junk"})
    assert _inst(page, i, "o._netOwner") == 0
    host.push_local_instances([_row("obj_ball#0", 10, 10, 0)])
    page.wait_for_function("window.game.currentRoom.instances[0]._netOwner === 0 && "
                           "_mpClient(window.game).ghosts.size === 1", timeout=8000)


def test_a_puppet_spawned_before_registration_is_replaced_by_the_room_instance(session):
    page, host, _ = session
    host.push_local_instances([_row("obj_ball#0", 50, 50, 0)])
    page.wait_for_function("_mpClient(window.game).ghosts.size === 1", timeout=8000)
    puppet = page.evaluate("window.game.currentRoom.instances.length")
    i = _place(page, x=0, y=0)
    _act(page, i, "sync_instance", {})
    page.wait_for_timeout(300)
    assert puppet >= 0
    assert page.evaluate("_mpClient(window.game).ghosts.get('obj_ball#0').inst === "
                         "window.game.currentRoom.instances[%d]" % i) is True
    assert page.evaluate("_mpClient(window.game).ghosts.get('obj_ball#0').registered") is True


def test_a_new_room_starts_its_own_registry(session):
    page, host, _ = session
    a = _place(page)
    _act(page, a, "sync_instance", {})
    page.evaluate("window.game.currentRoom = Object.assign(Object.create(Object.getPrototypeOf(window.game.currentRoom)), "
                  "window.game.currentRoom, {instances: []})")
    b = _place(page)
    _act(page, b, "sync_instance", {})
    assert _inst(page, b, "o._netId") == "obj_ball#0"
    assert page.evaluate("[_mpClient(window.game).synced.size, Object.keys(_mpClient(window.game).syncOrd).length]") == [1, 1]


def test_a_destroyed_synced_instance_is_skipped(session):
    page, host, _ = session
    i = _place(page, x=5, y=5)
    _act(page, i, "sync_instance", {})
    page.evaluate("window.__gone = window.game.currentRoom.instances[0]; window.__gone.toDestroy = true")
    host.push_local_instances([_row("obj_ball#0", 300, 300, 0)])
    page.wait_for_function("_mpClient(window.game).ghosts.size === 1", timeout=8000)
    page.wait_for_timeout(400)
    assert page.evaluate("window.__gone.x") == 5                         # nothing moved a destroyed instance
