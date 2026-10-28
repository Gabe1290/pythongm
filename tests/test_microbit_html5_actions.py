"""Stage P / H2: the micro:bit actions, conditions and events run in a real
HTML5 export.

CI has no JS engine, so the structural tests (the seams exist, the extension
registers every action and condition, the event table matches events.py) always
run. The behavioural test exports ``samples/microbit_1`` (with a few extra
authored events), loads it in headless Chromium and presses the simulated
buttons -- it runs only where Playwright + Chromium are installed (the dev
box) and is skipped elsewhere.
"""
import functools
import http.server
import json
import shutil
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

JS = (ROOT / "extensions" / "microbit" / "export_html5.js").read_text(encoding="utf-8")
ENGINE = (ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")

ACTIONS = ["microbit_show_image", "microbit_scroll_text", "microbit_show_number",
           "microbit_set_pixel", "microbit_clear_display", "microbit_set_brightness",
           "microbit_play_tone", "microbit_play_melody", "microbit_stop_sound",
           "microbit_radio_set_group", "microbit_radio_send", "microbit_read_sensor"]
CONDITIONS = ["microbit_if_button", "microbit_if_gesture", "microbit_if_tilt", "microbit_if_pixel"]


# -- structure (always runs) ---------------------------------------------------

def test_engine_has_the_condition_seam():
    assert "function registerExtensionCondition(" in ENGINE
    assert "!!_extConditions[actionType] ||" in ENGINE          # isConditionalAction
    assert "_extConditions[actionType](this, params, game)" in ENGINE   # evaluateCondition
    assert "this.instanceData = data;" in ENGINE


def test_extension_defines_every_action_and_condition():
    for name in ACTIONS:
        assert f"    {name}(inst, p, game, sim)" in JS, name
    for name in CONDITIONS:
        assert f"    {name}(inst, p, game, sim)" in JS, name
    assert "registerExtensionAction(name" in JS and "registerExtensionCondition(name" in JS
    assert "registerFrameUpdate(updateMicrobits)" in JS


def test_the_16_names_are_exactly_the_manifest_actions():
    manifest = json.loads((ROOT / "extensions" / "microbit" / "extension.json").read_text(encoding="utf-8"))
    assert sorted(ACTIONS + CONDITIONS) == sorted(manifest["provides_actions"])


def test_event_tables_match_events_py():
    from extensions.microbit.events import GESTURE_NAMES, _FIXED
    for (kind, detail), name in _FIXED.items():
        key = f"{kind}:{'' if detail is None else detail}"
        assert f'"{key}": "{name}"' in JS, key
    for gesture, entry in GESTURE_NAMES.items():
        assert f'"{gesture}": "{entry[0]}"' in JS, gesture


def test_every_simulator_event_has_a_name():
    """Every kind of report the simulator makes either fires an event or is one
    of the three the runtime handles itself (radio, sound note, sound stop)."""
    for kind in ("button", "logo", "pin", "gesture", "sound", "display_done", "sound_done", "radio"):
        assert f"'{kind}'" in JS or f'"{kind}:' in JS or kind in JS, kind


# -- behaviour in a real browser (dev box only) --------------------------------

def _browser_ok():
    try:
        import microbit_js_parity
        return microbit_js_parity.available()
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="needs Playwright + Chromium")


def _extra_step_events():
    """Authored events added to the sample's board, exercising a condition, a
    sensor read and a variable the test can inspect."""
    return {
        "step": {"actions": [
            {"action": "set_variable", "parameters": {"variable": "a_down", "value": "0"}},
            {"action": "microbit_if_button", "parameters": {"button": "a"}},
            {"action": "set_variable", "parameters": {"variable": "a_down", "value": "1"}},
            {"action": "microbit_read_sensor", "parameters": {"sensor": "light level", "variable": "lux"}},
            {"action": "microbit_read_sensor", "parameters": {"sensor": "temperature", "variable": "global.temp"}},
        ]},
    }


@pytest.fixture(scope="module")
def page(tmp_path_factory):
    from playwright.sync_api import sync_playwright
    from export.HTML5.html5_exporter import HTML5Exporter

    work = tmp_path_factory.mktemp("mb_h2")
    proj = work / "proj"
    shutil.copytree(ROOT / "samples" / "microbit_1", proj)
    obj_file = proj / "objects" / "microbit_1.json"
    data = json.loads(obj_file.read_text(encoding="utf-8"))
    data["events"].update(_extra_step_events())
    obj_file.write_text(json.dumps(data), encoding="utf-8")
    out = work / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out, {})

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
    handler.log_message = lambda *a, **k: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    page_name = next(out.glob("*.html")).name
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(f"http://127.0.0.1:{server.server_address[1]}/{page_name}")
        pg.wait_for_function(
            "window.game && window.game.currentRoom && window.game.currentRoom.instances.some(i => i.name === 'microbit_1')",
            timeout=20000)
        pg.errors = errors
        yield pg
        browser.close()
    server.shutdown()


def _eval(page, js):
    return page.evaluate("(() => { const g = window.game; const b = g.currentRoom.instances"
                         ".find(i => i.name === 'microbit_1'); const M = window.__pygmMicrobit;"
                         " const sim = M.boardOf(b); " + js + " })()")


def _grid(name):
    from extensions.microbit.simulator import parse_image
    return parse_image(name)


@needs_browser
def test_the_create_event_showed_the_heart(page):
    page.wait_for_timeout(200)
    assert _eval(page, "return sim.display;") == _grid("HEART")
    assert not page.errors, page.errors


@needs_browser
def test_pressing_a_and_b_fire_their_events(page):
    _eval(page, "sim.set_button('a', true);")
    page.wait_for_timeout(250)
    assert _eval(page, "return sim.display;") == _grid("HAPPY")
    _eval(page, "sim.set_button('a', false); sim.set_button('b', true);")
    page.wait_for_timeout(250)
    assert _eval(page, "return sim.display;") == _grid("SAD")
    _eval(page, "sim.set_button('b', false);")
    assert not page.errors, page.errors


@needs_browser
def test_a_condition_gates_the_next_action(page):
    _eval(page, "sim.set_button('a', false);")
    page.wait_for_timeout(250)
    assert _eval(page, "return b.a_down;") == 0
    _eval(page, "sim.set_button('a', true);")
    page.wait_for_timeout(250)
    assert _eval(page, "return b.a_down;") == 1
    _eval(page, "sim.set_button('a', false);")
    page.wait_for_timeout(250)
    assert _eval(page, "return b.a_down;") == 0


@needs_browser
def test_read_sensor_writes_instance_and_global_variables(page):
    _eval(page, "sim.set_light_level(77); sim.set_temperature(33);")
    page.wait_for_timeout(250)
    assert _eval(page, "return b.lux;") == 77
    assert _eval(page, "return g.globalVariables.temp;") == 33


@needs_browser
def test_shake_rolls_the_die_and_the_logo_scrolls_text(page):
    _eval(page, "sim.shake();")
    page.wait_for_timeout(300)
    obj = json.loads((ROOT / "samples" / "microbit_1" / "objects" / "microbit_1.json").read_text(encoding="utf-8"))
    faces = [_grid(a["parameters"]["image"]) for a in obj["events"]["microbit_gesture_shake"]["actions"]
             if a["action"] == "microbit_show_image"]
    assert len(faces) == 6
    roll = _eval(page, "return b.roll;")
    assert roll in (1, 2, 3, 4, 5, 6)                            # irandom(5) + 1
    assert _eval(page, "return sim.display;") == faces[roll - 1]  # the face for that roll
    _eval(page, "sim.set_logo_touched(true);")
    page.wait_for_timeout(300)
    assert _eval(page, "return sim.busy;") is True      # "Rolls" is scrolling
    assert not page.errors, page.errors


@needs_browser
def test_a_radio_message_fires_the_event_and_sets_the_variables(page):
    """Two boards in one room, same group: a send on one is heard by the other
    (radio_receive reports through the real update, then the event name table)."""
    r = page.evaluate("""(() => {
        const g = window.game, M = window.__pygmMicrobit;
        const room = g.currentRoom;
        const a = room.instances.find(i => i.name === 'microbit_1');
        const other = Object.create(a);            // a second board sharing the first's events
        other._mb = new M.MicrobitSimulator();
        other.events = {microbit_radio_received: {actions: [
            {action: 'set_variable', parameters: {variable: 'heard', value: '1'}}]}};
        room.instances.push(other);
        M.boardOf(a).radio_send('hello');
        for (let i = 0; i < 3; i++) M.updateMicrobits(g);
        room.instances.pop();
        return {heard: other.heard, string: other.radio_string, number: other.radio_number};
    })()""")
    assert r == {"heard": 1, "string": "hello", "number": 0}
