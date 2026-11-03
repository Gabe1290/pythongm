"""The simulated Thymio is audible: tones and factory-sound jingles play through the computer's sound system.

Pure synthesis is tested directly; behaviour is tested by running the reference programs of fiche 8
(tools/thymio_fiches_solutions.py) in the real GameRunner, reading the simulator's tone state and whether the robot's
reserved mixer channel is really busy (the dummy audio driver still runs a real mixer).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

pygame = pytest.importorskip("pygame")

from test_thymio_fiches import K, keys_of, run_program, tap  # noqa: E402


@pytest.fixture(autouse=True)
def _thymio_enabled(monkeypatch):
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    monkeypatch.setattr(plugin_loader, "is_extension_enabled",
                        lambda folder, default=True: True if folder == "thymio" else real(folder, default))


@pytest.fixture(autouse=True)
def _fresh_audio():
    from extensions.thymio import audio
    audio.forget()
    yield
    audio.forget()


def _first(frames, predicate):
    return next(i for i, f in enumerate(frames) if predicate(f))


# --- pure synthesis ---------------------------------------------------------------------------------------------

def test_a_square_wave_has_the_right_length_amplitude_and_pitch():
    from extensions.thymio import audio
    pcm = audio.square_wave(440, 0.5, rate=44100, channels=1)
    assert len(pcm) == 22050 * 2
    import array
    samples = array.array("h", pcm)
    assert max(samples) == audio.AMPLITUDE and min(samples) == -audio.AMPLITUDE
    crossings = sum(1 for a, b in zip(samples, samples[1:]) if a < 0 <= b)
    assert crossings == pytest.approx(220, abs=2)                     # 440 Hz for half a second


def test_a_rest_is_silence_not_nothing():
    from extensions.thymio import audio
    import array
    pcm = audio.square_wave(0, 0.1)
    assert len(pcm) == 4410 * 2 and set(array.array("h", pcm)) == {0}


def test_stereo_has_two_identical_samples_per_frame():
    from extensions.thymio import audio
    import array
    s = array.array("h", audio.square_wave(440, 0.01, channels=2))
    assert len(s) == 441 * 2 and s[0::2] == s[1::2]


def test_a_looped_tone_is_cut_on_whole_cycles_so_it_does_not_click():
    from extensions.thymio import audio
    import array
    for freq in (262, 440, 1000, 1500):
        s = array.array("h", audio.loop_pcm(freq))
        assert len(s) == pytest.approx(44100, rel=0.01)
        assert s[0] > 0 and s[-1] < 0                                  # starts a cycle, ends at the end of one


def test_a_jingle_is_its_notes_one_after_the_other():
    from extensions.thymio import audio
    notes = [(523, 6), (0, 3), (659, 12)]
    assert len(audio.jingle_pcm(notes)) == sum(int(44100 * n / 60) for _f, n in notes) * 2
    assert audio.total_frames(notes) == 21


def test_the_eight_factory_sounds_exist_and_are_short_and_distinct():
    from extensions.thymio import audio
    assert sorted(audio.SYSTEM_SOUNDS) == list(range(8))
    assert all(0 < audio.total_frames(n) <= 40 for n in audio.SYSTEM_SOUNDS.values())
    assert len({tuple(n) for n in audio.SYSTEM_SOUNDS.values()}) == 8


def test_the_system_sound_table_matches_the_actions_choice_list():
    from extensions.thymio import audio
    from extensions.thymio.actions import THYMIO_ACTIONS
    options = next(p.options for p in THYMIO_ACTIONS["thymio_play_system_sound"].parameters if p.name == "sound_id")
    assert [int(o.split(" - ")[0]) for o in options] == sorted(audio.SYSTEM_SOUNDS)


def test_nothing_is_cached_but_bytes():
    from extensions.thymio import audio
    audio.play([(440, 5)])
    assert all(isinstance(v, bytes) for v in audio._pcm_cache.values())


# --- through the engine ---------------------------------------------------------------------------------------

def test_each_button_plays_its_note_and_the_speaker_really_sounds():
    r = run_program("fiche8_sons_notes", 160, keys_of(tap(5, K.K_UP), tap(50, K.K_LEFT), tap(90, K.K_RIGHT),
                                                      tap(130, K.K_DOWN)))
    assert r[4]["tone"] == 0 and not r[4]["busy"]
    assert [r[i]["tone"] for i in (10, 55, 95, 135)] == [262, 330, 392, 523]
    assert r[10]["playing"] and r[10]["busy"]
    assert r[10]["dur"] == pytest.approx(25, abs=2)                      # 30 frames minus the ones that passed
    assert not r[45]["playing"]                                          # a 0.5 s note has ended


def test_the_press_plays_once_not_again_on_release():
    r = run_program("fiche8_sons_notes", 120, tap(5, K.K_UP, hold=25))
    assert r[20]["playing"]
    assert r[34]["dur"] == 0 or not r[34]["playing"]                     # released at 30: not restarted at 30+


def test_a_held_note_lasts_exactly_as_long_as_the_button():
    r = run_program("fiche8_sons_tenu", 120, {10: [("down", K.K_UP)], 60: [("up", K.K_UP)]})
    assert r[40]["playing"] and r[40]["busy"] and r[40]["tone"] == 440
    assert not r[70]["playing"] and not r[70]["busy"]


def test_sound_finished_chains_a_melody():
    r = run_program("fiche8_sons_melodie", 200, tap(5, K.K_SPACE))
    heard = []
    for f in r:
        if f["tone"] and (not heard or f["tone"] != heard[-1]) and f["playing"]:
            heard.append(f["tone"])
    assert heard == [262, 330, 392, 523]
    start = _first(r, lambda f: f["tone"] == 262)
    last = _first(r, lambda f: f["tone"] == 523)
    assert 58 <= last - start <= 66                                      # 3 notes of 20 frames, then the 4th starts


def test_factory_sounds_play_a_jingle_whose_length_is_the_event_time():
    from extensions.thymio import audio
    r = run_program("fiche8_sons_systeme", 200, keys_of(tap(5, K.K_UP), tap(60, K.K_LEFT), tap(120, K.K_SPACE)))
    assert r[7]["tone"] == 880 and r[7]["dur"] == pytest.approx(audio.total_frames(audio.SYSTEM_SOUNDS[2]) - 2, abs=2)
    assert r[63]["tone"] == 523 and r[63]["busy"]                        # Startup begins on 523 Hz
    assert r[63]["dur"] == pytest.approx(audio.total_frames(audio.SYSTEM_SOUNDS[0]) - 2, abs=2)
    assert r[123]["tone"] == 988                                         # Target Detected


def test_the_siren_alternates_two_tones_with_its_light():
    r = run_program("fiche8_sirene", 260, tap(5, K.K_SPACE))
    seen = []
    for f in r:
        if f["playing"] and (not seen or (f["tone"], f["top"]) != seen[-1]):
            seen.append((f["tone"], f["top"]))
    assert seen[:4] == [(440, (32, 0, 0)), (880, (0, 0, 32)), (440, (32, 0, 0)), (880, (0, 0, 32))]


def test_the_parking_radar_beeps_higher_as_the_box_gets_closer():
    r = run_program("fiche8_radar", 300, {10: [("down", K.K_UP)], 270: [("up", K.K_UP)]})
    tones = []
    for f in r:
        if f["playing"] and (not tones or f["tone"] != tones[-1]):
            tones.append(f["tone"])
    assert tones[0] == 800 and tones[-1] == 1500                          # far: low beeps, close: high beeps
    assert not any(f["playing"] for f in r[:40])                           # silent while nothing is near


def test_the_m_key_mutes_every_robot_but_the_simulator_still_counts():
    r = run_program("fiche8_sons_notes", 120, keys_of(tap(5, K.K_m), tap(20, K.K_UP), tap(60, K.K_m),
                                                      tap(80, K.K_LEFT)))
    assert r[25]["playing"] and not r[25]["busy"]                         # muted: the program runs, nothing is heard
    assert r[85]["playing"] and r[85]["busy"]                             # M again: sound is back


def test_muting_cuts_off_what_is_sounding():
    from extensions.thymio import audio
    assert audio.play([(440, 60)], voice=0)
    assert pygame.mixer.Channel(audio.CHANNEL_BASE).get_busy()
    audio.set_muted(True)
    assert not pygame.mixer.Channel(audio.CHANNEL_BASE).get_busy()
    assert audio.play([(440, 60)]) is False


def test_two_robots_use_two_channels():
    from extensions.thymio import audio
    assert audio.play([(440, 60)], voice=0) and audio.play([(660, 60)], voice=1)
    assert pygame.mixer.Channel(audio.CHANNEL_BASE).get_busy()
    assert pygame.mixer.Channel(audio.CHANNEL_BASE + 1).get_busy()


def test_the_micro_bit_channels_are_left_alone():
    from extensions.thymio import audio
    audio.play([(440, 60)], voice=0)
    assert audio.CHANNEL_BASE >= 4
    assert not any(pygame.mixer.Channel(c).get_busy() for c in range(4))


def test_no_mixer_is_a_quiet_no_op(monkeypatch):
    from extensions.thymio import audio
    monkeypatch.setattr(pygame.mixer, "get_init", lambda: None)
    monkeypatch.setattr(pygame.mixer, "init", lambda *a, **k: (_ for _ in ()).throw(pygame.error("no device")))
    assert audio.play([(440, 10)]) is False
    audio.stop()                                                           # must not raise
