"""Stage P / H6: a real playtest of ``samples/microbit_1`` in headless Chromium.

Runs only where Playwright + Chromium are installed (the dev box). The export's
canvas is compared with the frame the pygame engine renders for the same
project: apart from anti-aliased edges and the text font (a CSS font in the
browser, pygame's in the desktop engine) the two must agree, and the help text
must be drawn in the colour the sample authors (white), not the default black.
"""
import base64
import functools
import http.server
import io
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

ENGINE = (ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_draw_text_honours_an_explicit_colour():
    """The same bug desktop had (fixed 2026-09-04): the colour an author set on
    draw_text was dropped, so white help text on a dark room drew black."""
    body = ENGINE[ENGINE.index("case 'draw_text': {"):ENGINE.index("case 'draw_lives':")]
    assert "(params.color || params.colour) || this.draw_color" in body


def _browser_ok():
    try:
        import microbit_js_parity
        return microbit_js_parity.available()
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="needs Playwright + Chromium")


def _desktop_frame(tmp_path, frames=40):
    shot = tmp_path / "py.png"
    env = dict(os.environ, PYGM_MAX_FRAMES=str(frames), PYGM_SCREENSHOT=str(shot),
               SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    subprocess.run([sys.executable, str(ROOT / "runtime" / "run_game.py"),
                    str(ROOT / "samples" / "microbit_1" / "project.json")],
                   env=env, check=True, capture_output=True, timeout=120)
    from PIL import Image
    return Image.open(shot).convert("RGB")


def _browser_frame(tmp_path):
    from playwright.sync_api import sync_playwright
    from export.HTML5.html5_exporter import HTML5Exporter
    from PIL import Image

    proj = tmp_path / "proj"
    shutil.copytree(ROOT / "samples" / "microbit_1", proj)
    out = tmp_path / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out, {})
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
    handler.log_message = lambda *a, **k: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    name = next(out.glob("*.html")).name
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            pg = browser.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(f"http://127.0.0.1:{server.server_address[1]}/{name}")
            pg.wait_for_function("window.game && window.game.currentRoom", timeout=20000)
            pg.wait_for_timeout(1500)
            data = pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
            browser.close()
    finally:
        server.shutdown()
    assert not errors, errors
    return Image.open(io.BytesIO(base64.b64decode(data.split(",")[1]))).convert("RGB")


@needs_browser
def test_the_exported_frame_matches_the_pygame_frame(tmp_path):
    from PIL import ImageChops
    py = _desktop_frame(tmp_path)
    js = _browser_frame(tmp_path)
    assert py.size == js.size
    w, h = py.size

    # The board, the strip and the room colour: edges only (anti-aliasing).
    top = (0, 0, w, 395)
    diff = ImageChops.difference(py.crop(top), js.crop(top)).convert("L").point(lambda v: 255 if v > 24 else 0)
    changed = sum(1 for v in diff.getdata() if v) / float(w * 395)
    assert changed < 0.03, changed

    # Solid areas agree exactly: the room, the board body, a lit LED.
    for xy in [(5, 5), (630, 470), (200, 60), (290, 90), (320, 210), (100, 140), (505, 100)]:
        assert py.getpixel(xy) == js.getpixel(xy), xy

    # The help text is white in both (the sample authors #ffffff), not black.
    def lightest(img):
        band = img.crop((40, 400, 420, 470))
        return max(sum(px) for px in band.getdata())
    assert lightest(js) >= 3 * 230, "help text not drawn in the authored colour"
    assert lightest(py) >= 3 * 230
