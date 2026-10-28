"""Stage P / H5: the HTML5 export plays the micro:bit speaker.

The structural tests always run (the loudness and the longest note equal
audio.py's, and the sound hooks are wired to the speaker). Where Playwright +
Chromium are installed (the dev box) the speaker is driven with a fake
AudioContext that records every call, so what is asserted is the sound that
would be made -- type, pitch, gain, length, replacement, cut-off -- and a real
export of ``samples/microbit_1`` is checked to reach it from an authored
action.
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


# -- structure (always runs) ---------------------------------------------------

def test_loudness_and_longest_note_match_audio_py():
    from extensions.microbit import audio
    m = re.search(r"^const AUDIO_AMPLITUDE = (\d+) / 32767;", JS, re.M)
    assert m and int(m.group(1)) == audio.AMPLITUDE
    m = re.search(r"^const AUDIO_MAX_SECONDS = ([0-9.]+);", JS, re.M)
    assert m and float(m.group(1)) == audio.MAX_SECONDS


def test_sound_reports_reach_the_speaker():
    assert "const soundHooks = {note: speaker.note, stop: speaker.stop};" in JS


def test_audio_is_resumed_on_the_first_gesture():
    for kind in ("pointerdown", "keydown", "touchstart"):
        assert "'%s'" % kind in JS


# -- behaviour in a real browser (dev box only) --------------------------------

def _browser_ok():
    try:
        import microbit_js_parity
        return microbit_js_parity.available()
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="needs Playwright + Chromium")

FAKE = """
(() => {
  const M = window.__pygmMicrobit;
  window.__log = [];
  const log = (...a) => window.__log.push(a);
  const ctx = {state: 'suspended', currentTime: 5, destination: 'dest',
    resume() { this.state = 'running'; log('resume'); },
    createGain() { const g = {gain: {value: 1}, connect(t) { log('gain->', t === 'dest' ? 'dest' : 'x'); }, disconnect() {}}; log('gain'); this.g = g; return g; },
    createOscillator() { const o = {type: '', frequency: {value: 0}, id: log.n = (log.n || 0) + 1,
      connect(t) { log('osc->gain'); }, disconnect() { log('disconnect', this.id); },
      start() { log('start', this.id, this.type, this.frequency.value, ctx.g.gain.value); },
      stop(when) { log('stop', this.id, when === undefined ? 'now' : when); }}; return o; }};
  window.__sp = M.makeSpeaker(() => ctx);
  window.__ctx = ctx;
})()
"""


@pytest.fixture
def blank_page():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        pg.set_content("<html><body></body></html>")
        pg.add_script_tag(content=JS)
        yield pg
        browser.close()


def _fresh(pg):
    pg.evaluate(FAKE)


@needs_browser
def test_a_note_is_a_square_wave_at_the_right_pitch_gain_and_length(blank_page):
    _fresh(blank_page)
    ok = blank_page.evaluate("window.__sp.note(440, 0.5)")
    log = blank_page.evaluate("window.__log")
    assert ok is True
    assert ["resume"] in log                                  # a suspended context is woken
    start = next(e for e in log if e[0] == "start")
    assert start[2:] == ["square", 440, pytest.approx(5000 / 32767)]
    assert ["stop", 1, 5.5] in log                            # currentTime + seconds


@needs_browser
def test_a_new_note_replaces_the_one_playing(blank_page):
    _fresh(blank_page)
    blank_page.evaluate("window.__sp.note(440, 5); window.__sp.note(880, 1)")
    log = blank_page.evaluate("window.__log")
    names = [e[0] + str(e[1]) if e[0] in ("start", "stop") and len(e) > 1 else e[0] for e in log]
    assert names.index("stop1") < names.index("start2")        # the old voice is cut first
    starts = [e for e in log if e[0] == "start"]
    assert [s[3] for s in starts] == [440, 880]
    assert ["stop", 1, "now"] in log


@needs_browser
def test_stop_and_rests_silence_the_speaker(blank_page):
    _fresh(blank_page)
    blank_page.evaluate("window.__sp.note(440, 5); window.__sp.stop()")
    assert ["stop", 1, "now"] in blank_page.evaluate("window.__log")
    _fresh(blank_page)
    assert blank_page.evaluate("window.__sp.note(0, 1)") is False       # a rest
    assert blank_page.evaluate("window.__sp.note(440, 0)") is False     # no length
    assert not [e for e in blank_page.evaluate("window.__log") if e[0] == "start"]


@needs_browser
def test_a_note_is_capped_at_ten_seconds(blank_page):
    _fresh(blank_page)
    blank_page.evaluate("window.__sp.note(440, 99)")
    assert ["stop", 1, 15] in blank_page.evaluate("window.__log")


@needs_browser
def test_no_audio_device_is_survivable(blank_page):
    assert blank_page.evaluate(
        "(() => { const s = window.__pygmMicrobit.makeSpeaker(() => { throw new Error('none'); });"
        " return [s.note(440, 1), s.stop(), s.resume()]; })()") == [False, None, None]


@needs_browser
def test_a_running_context_is_not_resumed_again(blank_page):
    _fresh(blank_page)
    blank_page.evaluate("window.__ctx.state = 'running'; window.__sp.note(440, 1)")
    assert ["resume"] not in blank_page.evaluate("window.__log")


@needs_browser
def test_audio_plan_matches_audio_py_rules(blank_page):
    got = blank_page.evaluate(
        "[[440, 1], [0, 1], [-5, 1], [440, 0], [440, -1], [440, 99], [262.5, 0.25]]"
        ".map(a => window.__pygmMicrobit.audioPlan(a[0], a[1]))")
    assert got == [{"frequency": 440, "seconds": 1}, None, None, None, None,
                   {"frequency": 440, "seconds": 10}, {"frequency": 262.5, "seconds": 0.25}]


@pytest.fixture(scope="module")
def game_page(tmp_path_factory):
    from playwright.sync_api import sync_playwright
    from export.HTML5.html5_exporter import HTML5Exporter

    work = tmp_path_factory.mktemp("mb_h5")
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


@needs_browser
def test_an_authored_play_tone_reaches_the_speaker_in_a_real_export(game_page):
    game_page.evaluate("""() => {
      window.__notes = []; window.__stops = 0;
      const h = window.__pygmMicrobit.soundHooks;
      h.note = (f, s) => window.__notes.push([f, s]); h.stop = () => window.__stops++;
      const b = game.currentRoom.instances.find(i => i.name === 'microbit_1');
      b.executeActions([{action: 'microbit_play_tone', parameters: {frequency: 523, duration: 250}}], game);
    }""")
    game_page.wait_for_timeout(250)
    notes = game_page.evaluate("window.__notes")
    assert notes and notes[0][0] == 523 and notes[0][1] == pytest.approx(0.25)
    assert not game_page.errors, game_page.errors
