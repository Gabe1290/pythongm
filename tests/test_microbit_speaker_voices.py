"""Two boards sounding at once do not cut each other off (micro:bit follow-up M5).

The simulated speaker used to be ONE voice per game (desktop: mixer channel 0, HTML5: one
oscillator, Kivy: one Sound), so a second board's note replaced the first board's. Now each board
gets its own voice -- its index among the room's boards -- on all three targets; voice 0 is the
old single-speaker behaviour, so a one-board game is unchanged.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

JS = (ROOT / "extensions" / "microbit" / "export_html5.js").read_text(encoding="utf-8")


# -- desktop: a mixer channel per board ----------------------------------------------------

def _mixer():
    pygame = pytest.importorskip("pygame")
    from extensions.microbit import audio
    audio.forget()
    if audio._usable_format() is None:
        pytest.skip("no mixer in this environment")
    return pygame, audio


def test_two_boards_sound_on_two_channels_and_stop_independently():
    pygame, audio = _mixer()
    try:
        assert audio.play(440, 3.0, voice=0) is True
        assert audio.play(880, 3.0, voice=1) is True
        assert pygame.mixer.Channel(0).get_busy() and pygame.mixer.Channel(1).get_busy()
        audio.stop(0)
        assert not pygame.mixer.Channel(0).get_busy() and pygame.mixer.Channel(1).get_busy()
        assert audio.play(660, 3.0, voice=1) is True            # a new note replaces ITS OWN voice only
        audio.stop(1)
        assert not pygame.mixer.Channel(1).get_busy()
    finally:
        audio.stop(0)
        audio.stop(1)


def test_voice_zero_is_the_old_single_speaker():
    pygame, audio = _mixer()
    assert audio.play(440, 2.0) is True
    assert pygame.mixer.Channel(0).get_busy()
    audio.play(880, 2.0)                                        # same voice: replaced
    audio.stop()
    assert not pygame.mixer.Channel(0).get_busy()


def test_a_voice_beyond_the_cap_shares_the_last_and_reservations_grow_only_as_needed():
    pygame, audio = _mixer()
    assert audio.MAX_VOICES == 4
    try:
        audio.play(440, 2.0, voice=0)
        assert audio._reserved_count == 1
        audio.play(440, 2.0, voice=99)
        assert pygame.mixer.Channel(3).get_busy() and audio._reserved_count == 4
        audio.forget()
        assert audio._reserved_count == 0
    finally:
        for v in range(4):
            audio.stop(v)


def test_the_update_hook_gives_each_board_its_own_voice(monkeypatch):
    pytest.importorskip("pygame")
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRoom
    from extensions.microbit import runtime
    load_all_plugins()
    room = GameRoom("r", {"width": 400, "height": 300, "instances": [
        {"object": "microbit_1", "x": 100, "y": 100}, {"object": "microbit_1", "x": 300, "y": 100}]},
        action_executor=None)
    heard = []
    monkeypatch.setattr(runtime.audio, "play", lambda f, s, voice=0: heard.append(("play", voice, f)))
    monkeypatch.setattr(runtime.audio, "stop", lambda voice=0: heard.append(("stop", voice)))

    class Runner:
        current_room = room
        fps = 60
    for inst, hz in zip(room.instances, (440, 880)):
        inst.extension_state["microbit"]["simulator"].play_tone(hz, 200)
    runtime.update_microbits(Runner())
    assert ("play", 0, 440) in heard and ("play", 1, 880) in heard
    heard.clear()
    room.instances[1].extension_state["microbit"]["simulator"].stop_sound()
    runtime.update_microbits(Runner())
    assert ("stop", 1) in heard and not any(e[0] == "stop" and e[1] == 0 for e in heard)


# -- HTML5: an oscillator per board ----------------------------------------------------------

def test_html5_voices_are_per_board_and_capped_like_the_desktop():
    from extensions.microbit import audio
    assert re.search(r"^const AUDIO_MAX_VOICES = %d;" % audio.MAX_VOICES, JS, re.M)
    assert "soundHooks.note(detail[0], detail[1], voice);" in JS
    assert "soundHooks.stop(voice);" in JS
    assert "function note(frequency, seconds, id)" in JS and "function stop(id)" in JS


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
  let n = 0;
  const ctx = {state: 'running', currentTime: 5, destination: 'dest',
    createGain() { const g = {gain: {value: 1}, connect() {}, disconnect() {}}; this.g = g; return g; },
    createOscillator() { const id = ++n; return {type: '', frequency: {value: 0}, connect() {}, disconnect() {},
      start() { log('start', id, this.frequency.value); },
      stop(when) { log('stop', id, when === undefined ? 'now' : when); }}; }};
  window.__sp = M.makeSpeaker(() => ctx);
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
        pg.evaluate(FAKE)
        yield pg
        browser.close()


@needs_browser
def test_html5_two_boards_do_not_cut_each_other_off(blank_page):
    blank_page.evaluate("window.__sp.note(440, 5, 0); window.__sp.note(880, 5, 1)")
    log = blank_page.evaluate("window.__log")
    assert [e for e in log if e[0] == "start"] == [["start", 1, 440], ["start", 2, 880]]
    assert ["stop", 1, "now"] not in log and ["stop", 2, "now"] not in log   # neither note cut the other
    blank_page.evaluate("window.__sp.stop(0)")
    log = blank_page.evaluate("window.__log")
    assert ["stop", 1, "now"] in log and ["stop", 2, "now"] not in log


@needs_browser
def test_html5_a_new_note_replaces_only_its_own_voice_and_default_is_voice_zero(blank_page):
    blank_page.evaluate("window.__sp.note(440, 5); window.__sp.note(880, 5, 1); window.__sp.note(660, 5)")
    log = blank_page.evaluate("window.__log")
    assert ["stop", 1, "now"] in log and ["stop", 2, "now"] not in log


# -- Kivy: a Sound per board -----------------------------------------------------------------

class _Sound:
    def __init__(self, name, log):
        self.name, self.log = name, log

    def play(self):
        self.log.append(("play", self.name))

    def stop(self):
        self.log.append(("stop", self.name))


def _speaker(tmp_path):
    from extensions.microbit import kivy_audio
    log = []
    return kivy_audio.Speaker(lambda path: _Sound(Path(path).name, log), str(tmp_path)), log


def test_kivy_two_boards_keep_their_own_sound(tmp_path):
    sp, log = _speaker(tmp_path)
    sp.note(440, 1, 0)
    sp.note(880, 1, 1)
    assert [e[0] for e in log] == ["play", "play"]             # nothing was cut
    sp.stop(0)
    assert [e[0] for e in log] == ["play", "play", "stop"] and log[2][1] == log[0][1]
    sp.note(660, 1, 1)                                         # replaces board 1's own sound only
    assert [e[0] for e in log][3:] == ["stop", "play"] and log[3][1] == log[1][1]


def test_kivy_handle_routes_a_report_to_its_board_and_voice_zero_is_default(tmp_path):
    sp, log = _speaker(tmp_path)
    sp.handle("sound_note", (440, 1), 2)
    sp.handle("sound_note", (880, 1))
    sp.handle("sound_stop", None, 2)
    assert [e[0] for e in log] == ["play", "play", "stop"]
    assert sp.handle("radio", "x") is False


def test_the_kivy_scene_passes_each_boards_index():
    src = (ROOT / "extensions/microbit/export_kivy.py").read_text(encoding="utf-8")
    assert "for voice, board in enumerate(boards):" in src
    assert "get_speaker().handle(kind, detail, voice)" in src
