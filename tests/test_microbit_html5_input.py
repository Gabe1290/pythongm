"""Stage P / H4: mouse, touch and keyboard control of the board in an HTML5 export.

Always runs: the engine's input-hook seam exists and is wired into the mouse,
touch and keyboard paths; the extension has no duplicate top-level function
names (a later one silently replaces an earlier -- this happened once, caught
by the H3 pixel test). On the dev box (Playwright + Chromium) the hit tests,
tilt and slider maths are fuzz-compared with the Python ones, and a real
export of ``samples/microbit_1`` is driven with real mouse, touch and key
events.
"""
import functools
import http.server
import json
import re
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


# -- structure (always runs) ---------------------------------------------------

def test_engine_has_the_input_seam_wired_into_every_input_path():
    assert "function registerInputHandler(" in ENGINE and "function runInputHandlers(" in ENGINE
    assert "hookMouse('mouse_down'" in ENGINE and "hookMouse('mouse_up'" in ENGINE
    assert ENGINE.count("hookMouse('mouse_down'") == 2      # mouse + touch
    assert "runInputHandlers('key_down', inst," in ENGINE
    assert "runInputHandlers('key_up', inst," in ENGINE
    assert "this.pointer = pt" in ENGINE or "this.pointer = {x: 0, y: 0}" in ENGINE
    # a release outside the canvas still ends a press that began on it
    assert "window.addEventListener('mouseup'" in ENGINE


def test_extension_registers_its_input_handler():
    assert "registerInputHandler({mouse_down: mouseDown, mouse_up: mouseUp, key_down: keyDown, key_up: keyUp})" in JS
    assert "follow(game.pointer.x, game.pointer.y)" in JS


def test_no_duplicate_top_level_function_names():
    names = re.findall(r"^function ([A-Za-z0-9_]+)\(", JS, re.M)
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, f"later definitions silently replace earlier ones: {dupes}"


def test_input_constants_match_python():
    from extensions.microbit import input as py_input
    assert f"const TILT_HELD = {py_input.TILT};" in JS
    for key in py_input.TILT_KEYS:
        assert f"'{key}'" in JS
    from extensions.microbit.layout import SLIDERS
    for name in SLIDERS:
        assert f"{name}: 'set_" in JS.replace("light: 'set_light_level'", "light: 'set_") or name in JS


# -- behaviour in a real browser (dev box only) --------------------------------

def _browser_ok():
    try:
        import microbit_js_parity
        return microbit_js_parity.available()
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="needs Playwright + Chromium")


@needs_browser
def test_hit_tests_tilt_and_sliders_match_python():
    import microbit_js_parity
    bad, hits = microbit_js_parity.compare_input()
    assert not bad, f"first mismatch: {bad[0]}"
    kinds = {h for pair in hits for h in pair if h}
    assert {"a", "b", "logo", "pin0", "tilt", "shake", "slider:light"} <= kinds     # the fuzz reached them


@pytest.fixture(scope="module")
def page(tmp_path_factory):
    from playwright.sync_api import sync_playwright
    from export.HTML5.html5_exporter import HTML5Exporter

    work = tmp_path_factory.mktemp("mb_h4")
    proj = work / "proj"
    shutil.copytree(ROOT / "samples" / "microbit_1", proj)
    helper = proj / "objects" / "obj_help.json"
    data = json.loads(helper.read_text(encoding="utf-8"))
    # An authored click handler elsewhere in the room: it must see clicks that
    # miss the board and must NOT see the ones that land on it.
    data.setdefault("events", {})["mouse_left_press"] = {"actions": [
        {"action": "set_variable", "parameters": {"variable": "clicked", "value": "1"}}]}
    helper.write_text(json.dumps(data), encoding="utf-8")
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
        context = browser.new_context(has_touch=True, viewport={"width": 1100, "height": 900})
        pg = context.new_page()
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


def _js(page, body):
    return page.evaluate("(() => { const g = window.game, M = window.__pygmMicrobit;"
                         " const b = g.currentRoom.instances.find(i => i.name === 'microbit_1');"
                         " const help = g.currentRoom.instances.find(i => i.name === 'obj_help');"
                         " const sim = M.boardOf(b); " + body + " })()")


def _client(page, x, y):
    """Page coordinates of canvas point (x, y)."""
    r = page.evaluate("(() => { const c = document.getElementById('gameCanvas'); const r = c.getBoundingClientRect();"
                      " return [r.left + c.clientLeft, r.top + c.clientTop, c.clientWidth / c.width,"
                      " c.clientHeight / c.height]; })()")
    return r[0] + x * r[2], r[1] + y * r[3]


def _layout(page):
    return _js(page, "const l = M.layoutFor(b); const s = M.stripLayout(l); return {lay: l, strip: s};")


def _reset(page):
    # clear() too: the display plays its queue in order, so an earlier test's
    # scrolling text would otherwise hold up the next image.
    _js(page, "sim.set_button('a', false); sim.set_button('b', false); sim.set_acceleration(0, 0, -1024);"
              " sim.set_logo_touched(false); sim.clear(); delete help.clicked; delete b.roll; return 0;")
    page.mouse.move(5, 5)
    page.wait_for_timeout(120)


@needs_browser
def test_a_click_presses_a_button_and_fires_its_event(page):
    _reset(page)
    ax, ay, _ = _layout(page)["lay"]["buttons"]["a"]
    page.mouse.move(*_client(page, ax, ay))
    page.mouse.down()
    page.wait_for_timeout(200)
    assert _js(page, "return sim.buttons.a;") is True
    from extensions.microbit.simulator import parse_image
    assert _js(page, "return sim.display;") == parse_image("HAPPY")       # microbit_button_a ran
    page.mouse.up()
    page.wait_for_timeout(100)
    assert _js(page, "return sim.buttons.a;") is False
    assert not page.errors, page.errors


@needs_browser
def test_clicks_on_the_board_are_swallowed_and_clicks_elsewhere_are_not(page):
    _reset(page)
    ax, ay, _ = _layout(page)["lay"]["buttons"]["b"]
    page.mouse.click(*_client(page, ax, ay))
    page.wait_for_timeout(150)
    assert _js(page, "return help.clicked;") is None          # swallowed: no authored mouse event
    page.mouse.click(*_client(page, 600, 450))
    page.wait_for_timeout(150)
    assert _js(page, "return help.clicked;") == 1             # a miss reaches it as before


@needs_browser
def test_a_right_click_on_a_button_presses_both(page):
    _reset(page)
    ax, ay, _ = _layout(page)["lay"]["buttons"]["a"]
    page.mouse.move(*_client(page, ax, ay))
    page.mouse.down(button="right")
    page.wait_for_timeout(150)
    assert _js(page, "return [sim.buttons.a, sim.buttons.b];") == [True, True]
    page.mouse.up(button="right")
    page.wait_for_timeout(100)
    assert _js(page, "return [sim.buttons.a, sim.buttons.b];") == [False, False]


@needs_browser
def test_the_logo_and_a_pin_are_touchable(page):
    _reset(page)
    lay = _layout(page)["lay"]
    lx, ly = lay["logo"][0], lay["logo"][1]
    page.mouse.move(*_client(page, lx, ly))
    page.mouse.down()
    page.wait_for_timeout(120)
    assert _js(page, "return sim.logo_touched;") is True
    page.mouse.up()
    px, py, pw, ph = lay["pads"]["1"]
    page.mouse.move(*_client(page, px + pw // 2, py + ph // 2))
    page.mouse.down()
    page.wait_for_timeout(120)
    assert _js(page, "return sim.pins_touched[1];") is True
    page.mouse.up()
    page.wait_for_timeout(100)
    assert _js(page, "return [sim.logo_touched, sim.pins_touched[1]];") == [False, False]


@needs_browser
def test_dragging_the_tilt_pad_follows_the_pointer_and_springs_back(page):
    _reset(page)
    tx, ty, tw, th = _layout(page)["strip"]["tilt"]
    page.mouse.move(*_client(page, tx + tw // 2, ty + th // 2))
    page.mouse.down()
    page.mouse.move(*_client(page, tx + tw - 4, ty + th // 2), steps=4)
    page.wait_for_timeout(250)
    assert _js(page, "return sim.acceleration[0];") > 800           # dragged right
    page.mouse.move(*_client(page, tx + 4, ty + th // 2), steps=4)
    page.wait_for_timeout(250)
    assert _js(page, "return sim.acceleration[0];") < -800          # followed it left
    page.mouse.up()
    page.wait_for_timeout(150)
    assert _js(page, "return sim.acceleration;") == [0, 0, -1024]   # springs back to rest


@needs_browser
def test_dragging_a_slider_sets_the_sensor(page):
    _reset(page)
    kx, ky, kw, kh = _layout(page)["strip"]["sliders"]["light"]
    page.mouse.move(*_client(page, kx + kw // 2, ky + kh // 2))
    page.mouse.down()
    page.wait_for_timeout(200)
    mid = _js(page, "return sim.light_level;")
    assert 120 <= mid <= 135                                        # half of 0-255
    page.mouse.move(*_client(page, kx + kw, ky + kh // 2), steps=3)
    page.wait_for_timeout(200)
    assert _js(page, "return sim.light_level;") == 255
    page.mouse.up()


@needs_browser
def test_the_shake_button_shakes(page):
    _reset(page)
    sx, sy, sw, sh = _layout(page)["strip"]["shake"]
    page.mouse.click(*_client(page, sx + sw // 2, sy + sh // 2))
    page.wait_for_timeout(300)
    # The gesture itself is brief (it ends after the damping period, as on the
    # device); what lasts is its event: the sample rolls the die.
    assert _js(page, "return b.roll;") in (1, 2, 3, 4, 5, 6)


@needs_browser
def test_releasing_outside_the_canvas_still_releases(page):
    _reset(page)
    ax, ay, _ = _layout(page)["lay"]["buttons"]["a"]
    page.mouse.move(*_client(page, ax, ay))
    page.mouse.down()
    page.wait_for_timeout(100)
    page.mouse.move(5, 5)
    page.mouse.up()
    page.wait_for_timeout(100)
    assert _js(page, "return sim.buttons.a;") is False


@needs_browser
def test_a_tap_works_like_a_click(page):
    _reset(page)
    ax, ay, _ = _layout(page)["lay"]["buttons"]["b"]
    x, y = _client(page, ax, ay)
    page.touchscreen.tap(x, y)
    page.wait_for_timeout(250)
    from extensions.microbit.simulator import parse_image
    assert _js(page, "return sim.display;") == parse_image("SAD")           # microbit_button_b ran
    assert _js(page, "return sim.buttons.b;") is False                      # and it was released


@needs_browser
def test_keyboard_a_b_s_and_the_arrows(page):
    _reset(page)
    page.keyboard.down("a")
    page.wait_for_timeout(150)
    assert _js(page, "return sim.buttons.a;") is True
    page.keyboard.up("a")
    page.wait_for_timeout(100)
    assert _js(page, "return sim.buttons.a;") is False
    page.keyboard.down("ArrowLeft")
    page.wait_for_timeout(150)
    assert _js(page, "return sim.acceleration;") == [-1000, 0, 0]
    page.keyboard.down("ArrowUp")
    page.wait_for_timeout(150)
    assert _js(page, "return sim.acceleration;") == [-1000, 1000, 0]
    page.keyboard.up("ArrowLeft")
    page.keyboard.up("ArrowUp")
    page.wait_for_timeout(150)
    assert _js(page, "return sim.acceleration;") == [0, 0, -1024]
    page.keyboard.press("s")
    page.wait_for_timeout(300)
    assert _js(page, "return b.roll;") in (1, 2, 3, 4, 5, 6)           # the shake event ran
    assert not page.errors, page.errors


@needs_browser
def test_keyboard_control_is_opt_in(page):
    _reset(page)
    _js(page, "b.microbit_keyboard = false; b.objectData.microbit_keyboard = false; return 0;")
    page.keyboard.down("a")
    page.wait_for_timeout(150)
    assert _js(page, "return sim.buttons.a;") is False
    page.keyboard.up("a")
    _js(page, "b.microbit_keyboard = true; return 0;")
