"""micro:bit sound (docs/MICROBIT_EXTENSION_PLAN.md, Stage S8).

Pure note/melody parsing and the simulator's sound queue, the square-wave
synthesis, the actions, and a real game loop. Whether it sounds *right* has
to be judged by ear on a real machine; these pin the numbers behind it.
"""
import ast
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
EXT_DIR = REPO_ROOT / "extensions" / "microbit"

import pytest

from extensions.microbit import sound as S
from extensions.microbit.melodies import MELODIES
from extensions.microbit.simulator import MicrobitSimulator, MAX_SOUND_QUEUE

ARTIC = S.ARTICULATION


def _total(steps):
    return sum(secs for _, secs in steps)


def _events(sim, seconds, step=0.01):
    out = []
    for _ in range(int(round(seconds / step))):
        out += [e for e in sim.update(step) if e[0].startswith("sound")]
    return out


# --- notes and melodies (pure) ---------------------------------------------------------

def test_sound_modules_are_pygame_free():
    for fname in ("sound.py", "melodies.py"):
        tree = ast.parse((EXT_DIR / fname).read_text(encoding="utf-8"))
        mods = {n.module.split(".")[0] for n in ast.walk(tree)
                if isinstance(n, ast.ImportFrom) and n.module and not n.level}
        mods |= {a.name.split(".")[0] for n in ast.walk(tree)
                 if isinstance(n, ast.Import) for a in n.names}
        assert not mods & {"pygame", "PySide6"}, fname


def test_note_frequencies_match_the_device_table():
    f = S.note_frequency
    assert f("A", "", 4) == pytest.approx(440, abs=0.2)
    assert f("C", "", 4) == pytest.approx(261.6, abs=0.2)     # middle C
    assert f("G", "", 4) == pytest.approx(392.0, abs=0.2)
    assert f("C", "", 5) == pytest.approx(2 * f("C", "", 4), rel=0.002)
    assert f("A", "", 3) == pytest.approx(220, abs=0.2)
    assert f("A", "#", 4) == pytest.approx(466.2, abs=0.3)


def test_flats_are_their_sharps_and_edge_cases_are_sensible():
    f = S.note_frequency
    assert f("E", "b", 4) == f("D", "#", 4)
    assert f("B", "b", 4) == f("A", "#", 4)
    assert f("A", "b", 4) == f("G", "#", 4)
    assert f("E", "#", 4) == f("F", "", 4)          # no sharp on the device
    assert f("B", "#", 4) == f("C", "", 5)
    assert f("C", "b", 4) == f("B", "", 3)
    assert f("F", "b", 4) == f("E", "", 4)


def test_quarter_note_at_120_bpm_is_half_a_second_with_articulation():
    steps = S.melody_notes(["c4:4"])
    assert steps[0][0] == pytest.approx(261.6, abs=0.2)
    assert steps[0][1] == pytest.approx(0.5 - ARTIC)
    assert steps[1] == (0.0, ARTIC)
    assert _total(steps) == pytest.approx(0.5)


def test_tempo_scales_the_length():
    slow = _total(S.melody_notes(["c4:4"], bpm=60))
    fast = _total(S.melody_notes(["c4:4"], bpm=240))
    assert slow == pytest.approx(1.0) and fast == pytest.approx(0.25)


def test_octave_and_duration_persist_within_a_melody_and_reset_after():
    a = S.melody_notes(["c5:2", "d", "e"])
    freqs = [hz for hz, _ in a[::2]]
    assert freqs == [pytest.approx(S.note_frequency("C", "", 5), rel=1e-6),
                     pytest.approx(S.note_frequency("D", "", 5), rel=1e-6),
                     pytest.approx(S.note_frequency("E", "", 5), rel=1e-6)]
    assert all(_total(a[i:i + 2]) == pytest.approx(0.25) for i in (0, 2, 4))
    b = S.melody_notes(["c"])                  # a new melody starts from scratch
    assert b[0][0] == pytest.approx(261.6, abs=0.2) and _total(b) == pytest.approx(0.5)


def test_rest_is_silent_for_its_length():
    steps = S.melody_notes(["r:2"])
    assert steps[0][0] == 0 and _total(steps) == pytest.approx(0.25)


def test_melody_from_a_space_separated_string_and_names_any_case():
    assert S.melody_notes("C4:4 E G") == S.melody_notes(["C4:4", "E", "G"])
    assert S.melody_notes("dadadadum") == S.melody_notes("DADADADUM")


@pytest.mark.parametrize("bad", ["", "x4", "c:", "c4:x", "c#:", "z", "c44"])
def test_unreadable_notes_raise(bad):
    with pytest.raises(ValueError):
        S.melody_notes([bad] if bad else [])


def test_all_21_builtin_melodies_exist_parse_and_have_length():
    assert len(MELODIES) == 21
    for name in ("DADADADUM", "ENTERTAINER", "PRELUDE", "ODE", "NYAN", "RINGTONE",
                 "FUNK", "BLUES", "BIRTHDAY", "WEDDING", "FUNERAL", "PUNCHLINE",
                 "PYTHON", "BADDY", "CHASE", "BA_DING", "WAWAWAWAA", "JUMP_UP",
                 "JUMP_DOWN", "POWER_UP", "POWER_DOWN"):
        steps = S.melody_notes(name)
        assert steps and _total(steps) > 0, name
        assert all(0 <= hz <= S.MAX_FREQUENCY for hz, _ in steps), name


def test_dadadadum_is_four_seconds_and_starts_with_a_rest_then_g():
    steps = S.melody_notes("DADADADUM")
    assert _total(steps) == pytest.approx(4.0)
    assert steps[0][0] == 0                                  # r4:2 -> rest
    assert steps[2][0] == pytest.approx(392.0, abs=0.2)      # G4


def test_tone_is_clamped():
    assert S.tone_notes(440, 100) == [(440.0, 0.1)]
    assert S.tone_notes(-5, 100)[0][0] == 0
    assert S.tone_notes(10 ** 9, 100)[0][0] == S.MAX_FREQUENCY
    assert S.tone_notes(440, 0)[0][1] == 0.001


# --- the simulator's sound queue ------------------------------------------------------------

def test_a_tone_starts_sounds_then_stops_and_reports_done():
    sim = MicrobitSimulator()
    sim.play_tone(440, 100)
    assert sim.tone == 440 and sim.sound_busy
    events = _events(sim, 0.2)
    assert events == [("sound_note", (440.0, 0.1)), ("sound_stop", None),
                      ("sound_done", None)]
    assert sim.tone == 0 and not sim.sound_busy


def test_tones_queue_one_after_another():
    sim = MicrobitSimulator()
    sim.play_tone(440, 100)
    sim.play_tone(880, 100)
    assert sim.tone == 440
    sim.update(0.11)
    assert sim.tone == 880
    events = _events(sim, 0.2)
    assert ("sound_done", None) in events
    assert [e for e in events if e[0] == "sound_done"] == [("sound_done", None)]


def test_melody_plays_notes_in_order_on_its_timeline():
    sim = MicrobitSimulator()
    sim.play_melody("DADADADUM")
    assert sim.tone == 0                      # opens with a rest
    sim.update(0.26)
    assert sim.tone == pytest.approx(392.0, abs=0.2)
    events = _events(sim, 4.2)
    assert events[-1] == ("sound_done", None)
    assert sim.tone == 0 and not sim.sound_busy


def test_stop_sound_silences_clears_and_does_not_report_done():
    sim = MicrobitSimulator()
    sim.play_tone(440, 1000)
    sim.play_tone(880, 1000)
    sim.update(0.1)
    sim.stop_sound()
    assert sim.tone == 0 and not sim.sound_busy
    events = _events(sim, 2.0)
    assert ("sound_stop", None) in events
    assert ("sound_done", None) not in events
    sim.stop_sound()                          # nothing playing: no stray event
    assert all(e[0] != "sound_stop" for e in sim.update(0.02))


def test_sound_queue_is_capped_and_repeats_are_not_stacked():
    sim = MicrobitSimulator()
    for hz in range(100, 100 + MAX_SOUND_QUEUE):
        assert sim.play_tone(hz, 1000) is True
    assert sim.play_tone(9999, 1000) is False
    sim = MicrobitSimulator()
    sim.play_tone(440, 1000)
    for _ in range(50):
        sim.play_tone(880, 1000)              # the same thing queued each frame
    assert len(sim._sound) == 2


def test_bad_melody_raises_and_leaves_the_sound_alone():
    sim = MicrobitSimulator()
    sim.play_tone(440, 1000)
    with pytest.raises(ValueError):
        sim.play_melody("not a melody 9")
    assert sim.tone == 440 and len(sim._sound) == 1


# --- synthesis (pure) -----------------------------------------------------------------------

def test_square_wave_has_the_right_length_amplitude_and_pitch():
    from extensions.microbit import audio
    rate = 44100
    data = audio.square_wave(441, 0.5, rate=rate, channels=1)
    assert len(data) == int(rate * 0.5) * 2                      # 16-bit mono
    import array
    samples = array.array("h")
    samples.frombytes(data)
    assert set(samples) == {audio.AMPLITUDE, -audio.AMPLITUDE}
    crossings = sum(1 for a, b in zip(samples, samples[1:]) if a != b)
    assert crossings == pytest.approx(2 * 441 * 0.5, abs=3)      # 2 per cycle
    stereo = audio.square_wave(441, 0.1, rate=rate, channels=2)
    assert len(stereo) == int(rate * 0.1) * 2 * 2


def test_square_wave_of_a_rest_or_nothing_is_empty():
    from extensions.microbit import audio
    assert audio.square_wave(0, 1.0) == b""
    assert audio.square_wave(440, 0) == b""
    assert len(audio.square_wave(440, 999)) == int(44100 * audio.MAX_SECONDS) * 2


# --- the speaker (needs pygame) ---------------------------------------------------------------

pygame = pytest.importorskip("pygame")
from conftest import skip_without_pygame  # noqa: E402


@skip_without_pygame
def test_play_is_audible_on_the_reserved_channel_when_a_mixer_exists():
    from extensions.microbit import audio
    pygame.init()
    audio.forget()
    if audio._usable_format() is None:
        pytest.skip("no mixer in this environment; state-only fallback")
    assert audio.play(440, 2.0) is True
    assert pygame.mixer.Channel(0).get_busy()
    audio.stop()
    assert not pygame.mixer.Channel(0).get_busy()
    assert audio.play(0, 1.0) is False                           # a rest


@skip_without_pygame
def test_play_falls_back_to_state_only_without_a_mixer(monkeypatch):
    from extensions.microbit import audio
    monkeypatch.setattr(audio, "_usable_format", lambda: None)
    assert audio.play(440, 1.0) is False
    audio.stop()                                                 # harmless


@skip_without_pygame
def test_speaker_survives_a_pygame_quit_and_reinit():
    """Regression guard (the cached-Font crash): no Sound/Channel objects are
    kept between calls, so re-initialising pygame can't leave a dangling one."""
    from extensions.microbit import audio
    pygame.init()
    audio.forget()
    audio.play(440, 0.2)
    pygame.quit()
    pygame.init()
    audio.stop()
    audio.play(523, 0.2)                                         # must not crash
    audio.stop()


# --- actions and the loop ---------------------------------------------------------------------

def _board():
    from events.plugin_loader import load_all_plugins
    from runtime.action_executor import ActionExecutor
    from runtime.game_runner import GameRoom

    class GR:
        class _R:
            instances = []
            extension_state = {}
        current_room = _R()
        global_variables = {}

    ex = ActionExecutor(game_runner=GR())
    load_all_plugins(ex)
    room = GameRoom("r", {"width": 100, "height": 100, "instances": [
        {"object": "microbit_1", "x": 0, "y": 0}]}, action_executor=None)
    inst = room.instances[0]
    inst.action_executor = ex
    return ex, inst, inst.extension_state["microbit"]["simulator"]


def _do(ex, inst, name, **params):
    return ex.action_handlers[name](inst, params)


def test_play_tone_action():
    ex, inst, sim = _board()
    _do(ex, inst, "microbit_play_tone", frequency="440 + 440", duration=250)
    assert sim.tone == 880 and sim.sound_busy
    _do(ex, inst, "microbit_play_tone")                  # defaults: 440 Hz, 500 ms
    assert len(sim._sound) == 2 and sim._sound[1] == [(440.0, 0.5)]


def test_play_melody_action_by_name_custom_notes_and_tempo():
    ex, inst, sim = _board()
    _do(ex, inst, "microbit_play_melody", melody="POWER_UP")
    assert sim.sound_busy
    sim.stop_sound()
    _do(ex, inst, "microbit_play_melody", melody="c4:4 e g", tempo=60)
    assert _total(sim._sound[0]) == pytest.approx(3.0)
    sim.stop_sound()
    _do(ex, inst, "microbit_play_melody", melody='"c4:4 e g"')     # quoted literal
    assert sim.sound_busy


def test_play_melody_bad_name_is_ignored_not_fatal():
    ex, inst, sim = _board()
    _do(ex, inst, "microbit_play_melody", melody="NOT_A_TUNE_9")
    assert not sim.sound_busy


def test_stop_sound_action():
    ex, inst, sim = _board()
    _do(ex, inst, "microbit_play_tone", frequency=440, duration=5000)
    _do(ex, inst, "microbit_stop_sound")
    assert not sim.sound_busy and sim.tone == 0


def _write_project(tmp_path, events):
    project = {
        "name": "mb", "version": "1.0",
        "settings": {"window_width": 320, "window_height": 400, "room_speed": 60},
        "assets": {"sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
                   "fonts": {}, "data": {},
                   "objects": {"microbit_1": {
                       "name": "microbit_1", "asset_type": "object", "sprite": "",
                       "visible": True, "solid": False, "events": events}},
                   "rooms": {"room0": {
                       "name": "room0", "asset_type": "room", "width": 320,
                       "height": 400, "background_color": "#000000",
                       "instances": [{"object": "microbit_1", "x": 160, "y": 110}]}}},
    }
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    return str(path)


@skip_without_pygame
def test_real_loop_plays_a_tone_lights_the_speaker_and_fires_sound_done(tmp_path):
    from extensions.microbit import layout as L, renderer as R
    from runtime.game_runner import GameRunner
    project = _write_project(tmp_path, {
        "microbit_button_a": {"actions": [
            {"action": "microbit_play_tone",
             "parameters": {"frequency": 440, "duration": 200}}]},
        "microbit_sound_done": {"actions": [
            {"action": "microbit_set_pixel", "parameters": {"x": 4, "y": 4}}]}})
    runner = GameRunner(project)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.process_pending_messages = lambda *a, **k: None
    seen = {}
    state = {"n": 0}
    lay = L.board_layout(160, 110)

    def sim_of():
        inst = next(i for i in runner.current_room.instances
                    if i.object_name == "microbit_1")
        return inst.extension_state["microbit"]["simulator"]

    class _FakeClock:
        def tick(self, fps=0):
            state["n"] += 1
            n = state["n"]
            if n == 3:
                sim_of().set_button("a", True)
            if n == 6:                                   # during the 200 ms tone
                seen["tone"] = sim_of().tone
                seen["busy"] = (pygame.mixer.Channel(0).get_busy()
                                if pygame.mixer.get_init() else None)
                seen["lit"] = tuple(runner.screen.get_at(lay.speaker[:2]))[:3]
            if n == 30:                                  # long after it ended
                seen["done_px"] = sim_of().get_pixel(4, 4)
                seen["tone_after"] = sim_of().tone
                seen["dark"] = tuple(runner.screen.get_at(lay.speaker[:2]))[:3]
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real
        pygame.mixer.Channel(0).stop() if pygame.mixer.get_init() else None
    assert seen["tone"] == 440
    assert seen["busy"] in (True, None)          # None: no mixer, state-only
    if seen["busy"] is None:
        pytest.skip("no mixer here: audio output not checked")
    assert seen["lit"] == R.SPEAKER_ON
    assert seen["done_px"] == 9 and seen["tone_after"] == 0
    assert seen["dark"] == R.SPEAKER_OFF
