"""The micro:bit speaker on a Kivy export (Stage P, unit K5).

Shipped as ``microbit_sim/speaker.py``. Kivy has no raw-sample mixer call that
works on every platform, so a note is rendered to a small mono WAV (the same
square wave and loudness as ``audio.py``) and played with ``SoundLoader`` like
any other sound. Each board has its own voice (its index among the room's boards, capped at
MAX_VOICES): a new note replaces the one playing ON THAT VOICE, a rest or ``sound_stop`` cuts
that voice off, so two boards can sound together.

Pure apart from the lazily imported ``SoundLoader`` (injectable for tests).
"""
import array
import atexit
import os
import shutil
import struct
import tempfile

AMPLITUDE = 5000            # of 32767, as audio.py
MAX_SECONDS = 10.0          # longest single note, as audio.py
RATE = 22050                # mono; a square wave does not need more
_FILE_LIMIT = 64            # rendered notes kept before the folder is emptied


def square_wave(frequency, seconds, rate=RATE, amplitude=AMPLITUDE):
    """Signed 16-bit little-endian mono PCM; empty for a rest (as audio.py)."""
    frames = int(rate * min(max(0.0, seconds), MAX_SECONDS))
    if frequency <= 0 or frames <= 0:
        return b""
    step = frequency / float(rate)
    return array.array("h", [amplitude if (i * step) % 1.0 < 0.5 else -amplitude
                             for i in range(frames)]).tobytes()


def wav_bytes(frequency, seconds, rate=RATE):
    """A complete RIFF/WAVE file for a note; empty bytes for a rest."""
    pcm = square_wave(frequency, seconds, rate)
    if not pcm:
        return b""
    header = (b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt " +
              struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16) +
              b"data" + struct.pack("<I", len(pcm)))
    return header + pcm


def _default_loader(path):
    from kivy.core.audio import SoundLoader
    return SoundLoader.load(path)


MAX_VOICES = 4          # boards that can sound at once; a fifth shares the last


def _voice_index(voice):
    return min(max(0, int(voice or 0)), MAX_VOICES - 1)


class Speaker:
    def __init__(self, loader=None, folder=None):
        self._loader = loader or _default_loader
        self._folder = folder
        self._files = {}
        self._playing = {}            # voice (one per board) -> the Sound playing on it

    def _path_for(self, frequency, seconds):
        key = (round(frequency, 2), round(seconds, 3))
        path = self._files.get(key)
        if path is not None and os.path.exists(path):
            return path
        if self._folder is None:
            self._folder = tempfile.mkdtemp(prefix="mb_speaker_")
            atexit.register(shutil.rmtree, self._folder, True)
        if len(self._files) >= _FILE_LIMIT:
            for old in self._files.values():
                try:
                    os.remove(old)
                except OSError:
                    pass
            self._files.clear()
        path = os.path.join(self._folder, "note_%d.wav" % len(self._files))
        with open(path, "wb") as handle:
            handle.write(wav_bytes(frequency, seconds))
        self._files[key] = path
        return path

    def note(self, frequency, seconds, voice=0):
        """Start a note on board ``voice``'s speaker, replacing the one it was
        playing. True if it is audible."""
        voice = _voice_index(voice)
        self.stop(voice)
        if frequency <= 0 or seconds <= 0:
            return False
        try:
            sound = self._loader(self._path_for(frequency, seconds))
            if not sound:
                return False
            sound.play()
        except Exception as exc:               # no audio device must not stop the game
            print("[WARN] micro:bit speaker: %s" % exc)
            return False
        self._playing[voice] = sound
        return True

    def stop(self, voice=0):
        sound = self._playing.pop(_voice_index(voice), None)
        if sound is not None:
            try:
                sound.stop()
            except Exception:
                pass

    def handle(self, kind, detail, voice=0):
        """Act on a simulator report from board ``voice``; True if it was a sound report."""
        if kind == "sound_note":
            self.note(*detail, voice=voice)
            return True
        if kind == "sound_stop":
            self.stop(voice)
            return True
        return False


_speaker = None


def get_speaker():
    global _speaker
    if _speaker is None:
        _speaker = Speaker()
    return _speaker
