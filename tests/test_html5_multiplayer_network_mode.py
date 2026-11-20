"""HTML5 export: set_network_mode (the older v1 action) and the warn-once host actions.

A browser cannot accept connections, so ``host_game`` / ``set_network_mode`` in host mode stay no-ops -- but they
warn ONCE (not on every call), and ``set_network_mode`` is a registered action: before, it logged "Unknown action"
every time. In client mode it is a join (the same port convention as ``join_game``).

Always runs: structure. On the dev box (Playwright + Chromium): a real export runs the actions against a REAL
desktop host over 127.0.0.1.
"""
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

JS = (ROOT / "extensions" / "multiplayer_lan" / "export_html5.js").read_text(encoding="utf-8")


def test_set_network_mode_is_a_registered_action_and_host_game_warns_once():
    assert "registerExtensionAction('set_network_mode'" in JS
    assert "registerExtensionAction('host_game', () => _mpWarnOnce('host_game'" in JS


@pytest.fixture(scope="module")
def exported():
    pytest.importorskip("playwright.sync_api")
    import events.plugin_loader as loader
    from export.HTML5.html5_exporter import HTML5Exporter
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    try:
        out = Path(tempfile.mkdtemp(prefix="html5_netmode_")) / "out"
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


def _page(browser, exported):
    page = browser.new_page()
    logs = []
    page.on("console", lambda m: logs.append(m.text))
    page.goto(exported.as_uri())
    page.wait_for_function("window.game && window.game.currentRoom", timeout=20000)
    page.evaluate("window.game.currentRoom.instances = []")
    page.evaluate("""window.__run = (a, p) => {
        const inst = new GameObject('obj_x', 0, 0, {}, {});
        inst._gameRef = window.game;
        inst.executeAction({action: a, parameters: p}, window.game);
    }; 0""")
    return page, logs


def test_host_actions_warn_once_and_never_log_unknown_action(browser, exported):
    page, logs = _page(browser, exported)
    for _ in range(3):
        page.evaluate("__run('host_game', {})")
        page.evaluate("__run('set_network_mode', {mode: 'host'})")
    page.wait_for_timeout(100)
    page.close()
    assert not [l for l in logs if "Unknown action" in l]
    assert len([l for l in logs if "host_game is not available" in l]) == 1
    assert len([l for l in logs if "set_network_mode is not available" in l]) == 1


def test_client_mode_joins_a_real_host(browser, exported):
    from extensions.multiplayer_lan.session import NetworkSession
    host = NetworkSession(mode="host", port=0, player_name="Prof")
    host.start()
    if not host.bound_ws_port:
        host.close()
        pytest.skip("the host's WebSocket listener could not bind here")
    stop = threading.Event()

    def pump():
        while not stop.is_set():
            host.pump_before_step()
            host.take_own_state()
            host.pump_after_update()
            time.sleep(0.004)

    thread = threading.Thread(target=pump, daemon=True)
    thread.start()
    page, logs = _page(browser, exported)
    try:
        # the raw TCP port the author typed; the WebSocket listener is the next one up
        page.evaluate("__run('set_network_mode', {mode: 'client', host: '127.0.0.1', port: %d})" % (host.bound_ws_port - 1))
        page.wait_for_function("_mpClient(window.game).playerId >= 0", timeout=8000)
        assert host.player_count == 2
        assert not [l for l in logs if "Unknown action" in l]
    finally:
        stop.set()
        thread.join(timeout=2)
        page.close()
        host.close()
