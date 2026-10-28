"""Stage P / H3: the HTML5 export draws the micro:bit board.

Always runs (no JS engine needed): the engine's instance-overlay seam exists
and is called from every render path, and every layout constant and colour in
export_html5.js equals the Python one. Where Playwright + Chromium are
installed (the dev box) the layout is fuzz-compared against layout.py, the
canvas output is compared pixel-for-pixel at every control against pygame's,
and a real export of ``samples/microbit_1`` is checked to paint the board
where the layout says it is.
"""
import functools
import http.server
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

def test_engine_has_the_instance_overlay_seam():
    assert "function registerInstanceOverlay(" in ENGINE
    assert "function runInstanceOverlays(room, ctx)" in ENGINE
    assert "registerInstanceOverlay(drawOverlay)" in JS


def test_overlays_run_after_every_room_render_path():
    """After the extension-claimed path (2.5D), the no-views path and the views
    path -- the desktop hook runs after Room.render whatever drew the room."""
    body = ENGINE[ENGINE.index("    render(ctx) {"):ENGINE.index("    _renderContents(ctx) {")]
    assert body.count("runInstanceOverlays(this, ctx);") == 3


@pytest.mark.parametrize("name", [
    "BODY_W", "BODY_H", "LED_PITCH", "LED_SIZE", "LED_CENTER_DY", "BUTTON_DX", "BUTTON_RADIUS",
    "LOGO_DY", "LOGO_RX", "LOGO_RY", "PAD_PITCH", "PAD_W", "PAD_H", "STRIP_GAP", "STRIP_PAD",
    "TILT_SIZE", "SHAKE_H", "RIGHT_CONTENT_W", "RIGHT_TOP_GAP", "SLIDER_STEP", "SLIDER_TRACK_H",
    "TILT_FULL",
])
def test_layout_constant_matches_python(name):
    from extensions.microbit import layout
    m = re.search(r"^const %s = (-?[0-9.]+);" % name, JS, re.M)
    assert m, name
    assert float(m.group(1)) == float(getattr(layout, name)), name


@pytest.mark.parametrize("name", [
    "OFF_COLOR", "ON_COLOR", "BODY_COLOR", "BODY_EDGE", "LED_WELL", "LED_CHIP", "BUTTON_COLOR",
    "BUTTON_DOWN", "BUTTON_EDGE", "LOGO_COLOR", "LOGO_TOUCHED", "LOGO_DOT", "PAD_COLOR",
    "PAD_TOUCHED", "PAD_EDGE", "PAD_HOLE", "LABEL_COLOR", "CORNER_GREEN", "TAG_LABEL",
    "PANEL_COLOR", "PANEL_EDGE", "PAD_WELL", "PAD_DOT", "TRACK_COLOR", "TRACK_FILL",
    "KNOB_COLOR", "SHAKE_COLOR", "SHAKE_ACTIVE", "SPEAKER_ON", "SPEAKER_OFF",
])
def test_colour_matches_python(name):
    from extensions.microbit import layout, renderer
    py = getattr(renderer, name, None) or getattr(layout, name)
    m = re.search(r"^const %s = \[(\d+), (\d+), (\d+)\];" % name, JS, re.M)
    assert m, name
    assert tuple(int(g) for g in m.groups()) == tuple(py), name


def test_sliders_pad_names_and_titles_match_python():
    from extensions.microbit import layout, renderer
    for name, (lo, hi) in layout.SLIDERS.items():
        assert f"{name}: [{lo}, {hi}]" in JS, name
    for pin in layout.PAD_NAMES:
        assert f"'{pin}'" in JS, pin
    for name, title in renderer.SLIDER_TITLES.items():
        assert f"{name}: '{title}'" in JS, name


# -- behaviour in a real browser (dev box only) --------------------------------

def _browser_ok():
    try:
        import microbit_js_parity
        return microbit_js_parity.available()
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="needs Playwright + Chromium")


@needs_browser
def test_layout_matches_layout_py_including_exact_halves():
    import microbit_js_parity
    bad = microbit_js_parity.compare_layout(300)
    assert not bad, f"first mismatch: {bad[0][0]}"


@needs_browser
def test_canvas_matches_pygame_at_every_control():
    import microbit_js_parity
    bad = microbit_js_parity.compare_pixels()
    assert not bad, f"{len(bad)} mismatches, first: {bad[0]}"


@pytest.fixture(scope="module")
def game_page(tmp_path_factory):
    from playwright.sync_api import sync_playwright
    from export.HTML5.html5_exporter import HTML5Exporter

    work = tmp_path_factory.mktemp("mb_h3")
    proj = work / "proj"
    shutil.copytree(ROOT / "samples" / "microbit_1", proj)
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


PIXEL_JS = """(names) => {
    const g = window.game, M = window.__pygmMicrobit;
    const b = g.currentRoom.instances.find(i => i.name === 'microbit_1');
    const lay = M.layoutFor(b);
    const ctx = document.querySelector('canvas').getContext('2d');
    const at = (x, y) => Array.from(ctx.getImageData(x, y, 1, 1).data.slice(0, 3));
    return {body: at(lay.body[0] + 6, lay.body[1] + Math.floor(lay.body[3] / 2)),
            led_on: at(lay.leds[0][1][0], lay.leds[0][1][1]),       // HEART row 0 is 09090
            led_off: at(lay.leds[0][0][0], lay.leds[0][0][1] + 0),
            button_a: at(lay.buttons.a[0] + Math.floor(lay.buttons.a[2] * 0.7), lay.buttons.a[1]),
            layout: lay};
}"""


@needs_browser
def test_the_real_engine_paints_the_board_where_the_layout_says(game_page):
    game_page.wait_for_timeout(400)
    r = game_page.evaluate(PIXEL_JS, [])
    assert r["body"] == [34, 36, 40]                       # the board body
    assert r["led_on"] == [255, 52, 40]                    # a lit LED of the heart
    assert r["led_off"][0] < 150                           # an unlit one
    assert r["button_a"] == [205, 205, 200]                # button A, not pressed
    game_page.evaluate("(() => { const g = window.game; const b = g.currentRoom.instances"
                       ".find(i => i.name === 'microbit_1'); window.__pygmMicrobit.boardOf(b).set_button('a', true); })()")
    game_page.wait_for_timeout(200)
    assert game_page.evaluate(PIXEL_JS, [])["button_a"] == [255, 214, 90]    # pressed
    assert not game_page.errors, game_page.errors


@needs_browser
def test_an_invisible_board_draws_nothing(game_page):
    game_page.evaluate("(() => { const b = window.game.currentRoom.instances.find(i => i.name === 'microbit_1');"
                       " b.visible = false; })()")
    game_page.wait_for_timeout(250)
    r = game_page.evaluate(PIXEL_JS, [])
    assert r["body"] != [34, 36, 40]
    game_page.evaluate("(() => { const b = window.game.currentRoom.instances.find(i => i.name === 'microbit_1');"
                       " b.visible = true; })()")
