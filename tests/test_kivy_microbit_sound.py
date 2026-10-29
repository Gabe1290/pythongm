"""Stage P / K5: the micro:bit speaker on the Kivy export.

A note is rendered to a mono WAV (``kivy_audio.py``, shipped as
``microbit_sim/speaker.py``) and played through ``SoundLoader``. The samples are
compared with the desktop synth (``audio.square_wave``), the speaker is driven
with a fake loader, and the generated scene is checked to route the simulator's
sound reports to it.
"""
import importlib
import io
import os
import sys
import wave
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_microbit_draw import _board  # noqa: E402
from test_kivy_microbit_actions import _stub_kivy, _export  # noqa: E402

from extensions.microbit import audio, kivy_audio  # noqa: E402
from extensions.microbit.simulator import MicrobitSimulator  # noqa: E402

NOTES = [(440, 0.5), (262.5, 0.1), (3951, 0.05), (1, 1), (440, 99), (440, 0), (0, 1), (-5, 1)]


@pytest.mark.parametrize("frequency,seconds", NOTES)
def test_the_samples_are_the_desktop_synth_at_the_kivy_rate(frequency, seconds):
    assert kivy_audio.square_wave(frequency, seconds) == audio.square_wave(
        frequency, seconds, rate=kivy_audio.RATE, channels=1)


def test_loudness_and_longest_note_match_audio_py():
    assert kivy_audio.AMPLITUDE == audio.AMPLITUDE
    assert kivy_audio.MAX_SECONDS == audio.MAX_SECONDS


@pytest.mark.parametrize("frequency,seconds", [(440, 0.5), (880, 0.1)])
def test_wav_bytes_is_a_valid_mono_16_bit_file(frequency, seconds):
    with wave.open(io.BytesIO(kivy_audio.wav_bytes(frequency, seconds))) as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, kivy_audio.RATE)
        assert w.getnframes() == int(kivy_audio.RATE * seconds)
        assert w.readframes(w.getnframes()) == kivy_audio.square_wave(frequency, seconds)


def test_a_rest_has_no_file():
    assert kivy_audio.wav_bytes(0, 1) == b"" and kivy_audio.wav_bytes(440, 0) == b""


class _Sound:
    def __init__(self, path, log):
        self.path, self.log = path, log

    def play(self):
        self.log.append(("play", self.path))

    def stop(self):
        self.log.append(("stop", self.path))


def _speaker(tmp_path, fail=None):
    log, paths = [], []

    def loader(path):
        paths.append(path)
        if fail == "none":
            return None
        if fail == "raise":
            raise RuntimeError("no audio device")
        return _Sound(os.path.basename(path), log)
    return kivy_audio.Speaker(loader, str(tmp_path)), log, paths


def test_a_note_is_written_as_a_wav_and_played(tmp_path):
    sp, log, paths = _speaker(tmp_path)
    assert sp.note(440, 0.25) is True
    assert log == [("play", os.path.basename(paths[0]))]
    assert Path(paths[0]).read_bytes() == kivy_audio.wav_bytes(440, 0.25)


def test_a_new_note_replaces_the_one_playing(tmp_path):
    sp, log, _ = _speaker(tmp_path)
    sp.note(440, 1)
    sp.note(880, 1)
    assert [e[0] for e in log] == ["play", "stop", "play"]
    assert log[1][1] == log[0][1]                      # the first voice is the one cut


def test_a_rest_and_stop_silence_the_speaker(tmp_path):
    sp, log, paths = _speaker(tmp_path)
    sp.note(440, 1)
    assert sp.note(0, 1) is False
    assert [e[0] for e in log] == ["play", "stop"]
    sp.stop()                                          # nothing left to stop
    assert [e[0] for e in log] == ["play", "stop"]
    assert sp.note(440, 0) is False and len(paths) == 1


def test_the_same_note_reuses_its_file(tmp_path):
    sp, _, paths = _speaker(tmp_path)
    sp.note(440, 0.5)
    sp.note(440, 0.5)
    assert paths[0] == paths[1] and len(os.listdir(tmp_path)) == 1


def test_the_file_cache_is_bounded(tmp_path):
    sp, _, _ = _speaker(tmp_path)
    for i in range(kivy_audio._FILE_LIMIT + 5):
        sp.note(100 + i, 0.01)
    assert len(os.listdir(tmp_path)) <= kivy_audio._FILE_LIMIT


@pytest.mark.parametrize("fail", ["none", "raise"])
def test_no_audio_device_is_survivable(tmp_path, fail):
    sp, log, _ = _speaker(tmp_path, fail=fail)
    assert sp.note(440, 1) is False
    sp.stop()
    assert log == []


def test_handle_routes_only_sound_reports(tmp_path):
    sp, log, _ = _speaker(tmp_path)
    assert sp.handle("sound_note", (440, 0.5)) is True
    assert sp.handle("sound_stop", None) is True
    assert sp.handle("button", "a") is False
    assert [e[0] for e in log] == ["play", "stop"]


# -- the generated scene ---------------------------------------------------------------

class _Fake:
    def __init__(self):
        self.calls = []

    def handle(self, kind, detail):
        if kind in ("sound_note", "sound_stop"):
            self.calls.append((kind, detail))
        return True


def _scene_with_fake_speaker():
    scene_mod = importlib.import_module("scenes.room0")
    scene = scene_mod.Room0.__new__(scene_mod.Room0)
    inst, _ = _board()
    inst._mb_draw = lambda room_h: None
    scene.instances, scene.room_height = [inst], 480
    speaker = importlib.import_module("microbit_sim.speaker")
    speaker._speaker = fake = _Fake()
    return scene, inst, fake


def test_the_scene_sends_the_simulators_sound_reports_to_the_speaker():
    twin = MicrobitSimulator()
    twin.play_tone(440, 500)
    expected = [r for r in twin.update(1 / 60) if r[0].startswith("sound")]
    assert expected and expected[0][0] == "sound_note"
    game = _export({})
    with _stub_kivy(game):
        scene, inst, fake = _scene_with_fake_speaker()
        inst._mb_play_tone(440, 500)
        scene._update_extensions(1 / 60)
        inst._mb_stop_sound()
        scene._update_extensions(1 / 60)
    assert fake.calls[0] == expected[0]
    assert fake.calls[-1] == ("sound_stop", None)


def test_a_silent_frame_makes_no_sound_call():
    game = _export({})
    with _stub_kivy(game):
        scene, inst, fake = _scene_with_fake_speaker()
        scene._update_extensions(1 / 60)
    assert fake.calls == []


def test_the_shipped_speaker_is_the_source_and_needs_no_pygame():
    game = _export({})
    shipped = (game / "microbit_sim" / "speaker.py").read_bytes()
    assert shipped == (ROOT / "extensions/microbit/kivy_audio.py").read_bytes()
    assert b"import pygame" not in shipped


def test_the_wav_header_fields_the_wave_module_does_not_expose():
    import struct
    data = kivy_audio.wav_bytes(440, 0.1)
    riff_size, = struct.unpack("<I", data[4:8])
    fmt = struct.unpack("<IHHIIHH", data[16:36])
    assert riff_size == len(data) - 8
    assert fmt == (16, 1, 1, kivy_audio.RATE, kivy_audio.RATE * 2, 2, 16)   # PCM, mono, byte rate, align, bits
    assert data[36:40] == b"data" and struct.unpack("<I", data[40:44])[0] == len(data) - 44
