"""HTML5 export: a browser player controls the avatar the host gave it.

It used to be viewing only: ``is_instance_owner`` was an unknown question (always false, so an
avatar guarded by it never moved, even single player) and nothing was ever reported up to the host.
Now an instance the host assigned to this player (network_spawn owner=player_id) is promoted from a
puppet to a locally simulated avatar; this page reports its state ("own" frames) and the held named
inputs ("input" frames) every step, as the desktop client does.

Always runs: the structure. On the dev box (Playwright + Chromium) a real export of ``reseau_1`` joins
a REAL desktop host (the IDE's own NetworkSession, WebSocket side) over 127.0.0.1 and is driven with
real key presses.
"""
import json
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


# -- structure (always runs) -------------------------------------------------------

def test_the_client_reports_own_state_and_inputs_and_keeps_its_avatar_on_host_loss():
    assert "sendOwn(rows)" in JS and "this._send({ t: 'own', i: rows })" in JS
    assert "this._send({ t: 'input', held: held })" in JS
    assert "g.owner === client.playerId" in JS and "g.local = true" in JS
    assert "_teardownGhosts(true)" in JS and "if (keepLocal && g.local) continue;" in JS


def test_ownership_questions_and_input_actions_are_registered():
    assert "registerExtensionCondition('is_instance_owner'" in JS
    assert "registerExtensionCondition('remote_input'" in JS
    assert "registerExtensionAction('bind_network_input'" in JS
    assert "registerExtensionAction('set_sync_rate'" in JS
    for name in ("host_game_files", "join_game_files", "leave_game_files", "set_shared_var_files",
                 "get_shared_var_files", "send_network_message_files", "end_turn"):
        assert f"'{name}'" in JS
    # bind_network_input / set_sync_rate / sync_instance / set_instance_owner are real now; only network_spawn
    # (the host creates networked instances) is still a warning
    assert "registerExtensionAction('network_spawn', () => _mpWarnOnce('network_spawn'," in JS
    assert "registerExtensionAction('sync_instance'" in JS and "registerExtensionAction('set_instance_owner'" in JS


# -- real browser against a real host (dev box only) ---------------------------------

@pytest.fixture(scope="module")
def page_and_host():
    sync_api = pytest.importorskip("playwright.sync_api")
    import events.plugin_loader as loader
    from export.Kivy import code_generator  # noqa: F401  (loads the same plugin set the exporter uses)
    from export.HTML5.html5_exporter import HTML5Exporter
    from extensions.multiplayer_lan.session import NetworkSession
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    try:
        src = ROOT / "samples" / "reseau_1"
        out = Path(tempfile.mkdtemp(prefix="html5_mp_")) / "out"
        out.mkdir(parents=True)
        assert HTML5Exporter().export(src, out)
    finally:
        loader.list_available_extensions = original
    html = next(out.glob("*.html"))

    host = NetworkSession(mode="host", port=0, player_name="Prof")
    host.start()
    if not host.bound_ws_port:
        host.close()
        pytest.skip("the host's WebSocket listener could not bind here")
    own_log, stop = [], threading.Event()

    def pump():
        while not stop.is_set():
            host.pump_before_step()
            for nid, row in host.take_own_state().items():
                own_log.append((time.monotonic(), nid, row))
            host.pump_after_update()
            time.sleep(0.004)

    thread = threading.Thread(target=pump, daemon=True)
    thread.start()
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            stop.set()
            host.close()
            pytest.skip(f"no Chromium: {exc}")
        page = browser.new_page()
        page.goto(html.as_uri())
        page.wait_for_function("window.game && window.game.currentRoom", timeout=20000)
        yield page, host, own_log
        browser.close()
    stop.set()
    thread.join(timeout=2)
    host.close()


def _wait(page, expr, timeout=8000):
    page.wait_for_function(expr, timeout=timeout)


def test_without_a_session_you_own_everything(page_and_host):
    page, host, _ = page_and_host
    assert page.evaluate("_extConditions['is_instance_owner']({}, {}, window.game)") is True
    assert page.evaluate("_extConditions['remote_input']({}, {}, window.game)") is False


def test_a_browser_player_drives_the_avatar_the_host_gave_it(page_and_host):
    page, host, own_log = page_and_host
    page.evaluate("_mpClient(window.game).join('127.0.0.1', %d, 'Ada')" % host.bound_ws_port)
    _wait(page, "_mpClient(window.game).playerId >= 0")
    nid = host.next_netid()
    host.push_local_instances([{"nid": nid, "o": "obj_person", "x": 96, "y": 96, "r": 0, "f": 0,
                                "v": True, "own": 1}])
    _wait(page, "(() => { const g = _mpClient(window.game).ghosts; "
                "return g.size === 1 && Array.from(g.values())[0].local === true; })()")
    x0 = page.evaluate("Array.from(_mpClient(window.game).ghosts.values())[0].inst.x")
    assert page.evaluate("_extConditions['is_instance_owner']("
                         "Array.from(_mpClient(window.game).ghosts.values())[0].inst, {}, window.game)") is True

    page.keyboard.down("ArrowRight")
    page.wait_for_timeout(600)
    held_now = host.remote_input(1, "right")
    page.keyboard.up("ArrowRight")
    page.wait_for_timeout(300)
    x1 = page.evaluate("Array.from(_mpClient(window.game).ghosts.values())[0].inst.x")
    assert x1 > x0 + 20, f"the avatar did not move under its owner's keys ({x0} -> {x1})"
    assert held_now is True
    assert host.remote_input(1, "right") is False                     # released again
    reported = [row for _, n, row in own_log if n == nid]
    assert reported and reported[-1]["_from"] == 1
    assert reported[-1]["x"] == pytest.approx(x1, abs=8)
    assert max(r["x"] for r in reported) > x0 + 20


def test_another_players_avatar_stays_a_puppet_and_is_not_owned(page_and_host):
    page, host, own_log = page_and_host
    other = host.next_netid()
    host.push_local_instances([
        {"nid": other, "o": "obj_person", "x": 300, "y": 40, "r": 0, "f": 0, "v": True, "own": 0}])
    _wait(page, "Array.from(_mpClient(window.game).ghosts.values()).some(g => g.owner === 0)")
    owned_before = len([1 for _, n, _r in own_log if n == other])
    info = page.evaluate("""(() => { const g = Array.from(_mpClient(window.game).ghosts.entries())
        .find(([k, v]) => v.owner === 0)[1];
        return [!!g.local, _extConditions['is_instance_owner'](g.inst, {}, window.game)]; })()""")
    assert info == [False, False]
    page.keyboard.down("ArrowLeft")
    page.wait_for_timeout(400)
    page.keyboard.up("ArrowLeft")
    assert len([1 for _, n, _r in own_log if n == other]) == owned_before   # never reported up


def test_losing_the_host_keeps_the_players_own_avatar(page_and_host):
    page, host, _ = page_and_host
    host.push_local_instances([
        {"nid": 1, "o": "obj_person", "x": 96, "y": 96, "r": 0, "f": 0, "v": True, "own": 1}])
    _wait(page, "Array.from(_mpClient(window.game).ghosts.values()).some(g => g.local)")
    host.close()
    _wait(page, "_mpClient(window.game).connectionLost === true", 10000)
    left = page.evaluate("Array.from(_mpClient(window.game).ghosts.values()).map(g => [!!g.local, !!g.inst.toDestroy])")
    assert left and all(local and not gone for local, gone in left)


def test_if_condition_key_pressed_reads_the_held_keys(page_and_host):
    """if_condition key_pressed was never ported to the HTML5 engine (it always took the else branch),
    so an avatar steered by one never moved in a browser."""
    page, host, _ = page_and_host
    got = page.evaluate("""(() => {
        const inst = new GameObject('probe', 0, 0, {}, {});
        const q = key => inst.evaluateCondition(
            {action: 'if_condition', parameters: {condition_type: 'key_pressed', key: key}}, window.game);
        window.game.keys = {};
        const idle = [q('left'), q('a'), q('space')];
        window.game.keys = {ArrowLeft: true, a: true, ' ': true, ArrowRight: false};
        const held = [q('left'), q('a'), q('space'), q('right'), q('k_left'), q('LEFT'), q('')];
        window.game.keys = {};
        return [idle, held];
    })()""")
    assert got == [[False, False, False], [True, True, True, False, True, True, False]]


def test_the_engine_no_longer_says_key_pressed_is_unported():
    engine = (ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
    assert "case 'key_pressed': {" in engine
    assert "key_pressed/\n                // mouse_check are the two" not in engine.replace("\r\n", "\n")
