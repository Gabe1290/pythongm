#!/usr/bin/env python3
"""Makes the simulated Thymio's speaker audible, through the computer's sound system.

The real robot plays a tone (``sound.freq``, duration in 1/60 s) or one of eight factory sounds. The simulator
synthesises square-wave tones (the timbre of a small buzzer) and renders each factory sound as a short jingle that
*resembles* it -- the robot's own recordings are not reproduced. ``jingle_pcm`` / ``square_wave`` are pure (bytes
out, no mixer) so they are testable anywhere. With no usable mixer every call quietly does nothing: the simulator's own
tone state stays the authoritative record, and tests assert on that.

Each robot has a voice (0..MAX_VOICES-1) on a reserved mixer channel, after the four the micro:bit extension uses, so
two robots sounding at once do not cut each other off. ``mute`` silences every robot (the simulator keeps counting, so
a program that waits for "sound finished" still works).
"""
import array

import pygame

FPS = 60                    # the robot counts durations in 1/60 s
AMPLITUDE = 4000            # of 32767: a clear beep, not a loud one
MAX_VOICES = 4              # robots that can sound at the same time
CHANNEL_BASE = 4            # channels 0-3 belong to the micro:bit speaker
MAX_SECONDS = 10.0
MIN_HZ, MAX_HZ = 20, 20000
_CACHE_LIMIT = 64

# The eight factory sounds as (frequency Hz, frames) notes. Resemblances, not recordings.
SYSTEM_SOUNDS = {
    0: [(523, 8), (659, 8), (784, 14)],                         # Startup: rising
    1: [(784, 8), (659, 8), (523, 14)],                         # Shutdown: falling
    2: [(880, 6)],                                              # Arrow: a blip
    3: [(659, 8), (880, 12)],                                   # Central: two notes
    4: [(880, 6), (740, 6), (622, 6), (523, 6), (440, 6)],      # Free Fall: dropping
    5: [(150, 14)],                                             # Collision: a low thud
    6: [(523, 6), (659, 6), (784, 6), (1047, 12)],              # Target Friendly: cheerful
    7: [(988, 6), (740, 6), (988, 6), (740, 6)],                # Target Detected: alarm
}

# Rendered PCM by (notes, loop, rate, channels). Raw bytes only, never pygame Sound/Channel objects: those dangle after
# pygame.quit() and crash the process on next use (the same trap as a cached Font).
_pcm_cache = {}
_unusable = False
_reserved_count = 0
_muted = False


def total_frames(notes):
    return sum(max(0, int(frames)) for _freq, frames in notes)


def square_wave(frequency, seconds, rate=44100, channels=1, amplitude=AMPLITUDE):
    """Signed 16-bit little-endian PCM of a square wave; silence for a rest (frequency 0)."""
    frames = int(rate * min(max(0.0, seconds), MAX_SECONDS))
    if frames <= 0:
        return b""
    samples = array.array("h")
    if frequency <= 0:
        samples.extend([0] * (frames * channels))
        return samples.tobytes()
    step = frequency / float(rate)
    for i in range(frames):
        value = amplitude if (i * step) % 1.0 < 0.5 else -amplitude
        samples.extend([value] * channels)
    return samples.tobytes()


def jingle_pcm(notes, rate=44100, channels=1):
    """The notes ``[(Hz, frames), ...]`` one after the other as one PCM buffer."""
    return b"".join(square_wave(freq, frames / float(FPS), rate, channels) for freq, frames in notes)


def loop_pcm(frequency, rate=44100, channels=1):
    """About one second of a tone cut on a whole number of cycles, so that looping it does not click."""
    frequency = min(max(frequency, MIN_HZ), MAX_HZ)
    cycles = max(1, round(frequency))                   # ~1 s worth of cycles
    return square_wave(frequency, cycles / float(frequency), rate, channels)


def _usable_format():
    global _unusable
    if _unusable:
        return None
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        info = pygame.mixer.get_init()
    except pygame.error:
        _unusable = True
        return None
    if not info:
        _unusable = True
        return None
    rate, fmt, channels = info
    if fmt != -16:
        return None
    return rate, channels


def _voice_index(voice):
    return min(max(0, int(voice or 0)), MAX_VOICES - 1)


def _channel(voice):
    """Robot ``voice``'s reserved channel, fetched fresh each time (only integers are remembered)."""
    global _reserved_count
    voice = _voice_index(voice)
    try:
        if pygame.mixer.get_num_channels() < CHANNEL_BASE + MAX_VOICES + 4:
            pygame.mixer.set_num_channels(CHANNEL_BASE + MAX_VOICES + 4)
        _reserved_count = max(_reserved_count, CHANNEL_BASE + voice + 1)
        pygame.mixer.set_reserved(_reserved_count)
        return pygame.mixer.Channel(CHANNEL_BASE + voice)
    except pygame.error:
        return None


def set_muted(muted):
    """Silence (or restore) every robot. Whatever is sounding is cut off when muting."""
    global _muted
    _muted = bool(muted)
    if _muted:
        for voice in range(MAX_VOICES):
            stop(voice)


def toggle_muted():
    set_muted(not _muted)
    return _muted


def is_muted():
    return _muted


def play(notes, voice=0, loop=False):
    """Start ``notes`` ([(Hz, frames), ...]) on robot ``voice``'s speaker, replacing what it was playing. ``loop`` repeats a
    single tone until stopped (the robot's "continuous" duration -1). True if it is audible."""
    if _muted or not notes:
        return False
    fmt = _usable_format()
    channel = _channel(voice) if fmt else None
    if channel is None:
        return False
    if all(freq <= 0 for freq, _frames in notes):
        channel.stop()
        return False
    rate, channels = fmt
    key = (tuple((round(f, 2), int(n)) for f, n in notes), bool(loop), rate, channels)
    data = _pcm_cache.get(key)
    if data is None:
        data = loop_pcm(notes[0][0], rate, channels) if loop else jingle_pcm(notes, rate, channels)
        if not data:
            return False
        if len(_pcm_cache) >= _CACHE_LIMIT:
            _pcm_cache.clear()
        _pcm_cache[key] = data
    channel.play(pygame.mixer.Sound(buffer=data), loops=-1 if loop else 0)
    return True


def stop(voice=0):
    try:
        if pygame.mixer.get_init():
            pygame.mixer.Channel(CHANNEL_BASE + _voice_index(voice)).stop()
    except pygame.error:
        pass


def forget():
    """Drop cached audio and the "no mixer" verdict, and unmute (tests; a new game)."""
    global _unusable, _reserved_count, _muted
    for voice in range(MAX_VOICES):
        stop(voice)
    _pcm_cache.clear()
    _unusable = False
    _reserved_count = 0
    _muted = False
