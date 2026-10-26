#!/usr/bin/env python3
"""Makes the simulated speaker audible (Stage S8).

Square-wave synthesis -- the same timbre as the real board's buzzer -- played
on one reserved mixer channel. ``square_wave`` is pure (bytes out, no mixer),
so it is testable anywhere. When there is no usable mixer (no audio device, or
a sample format other than 16-bit signed) every call quietly does nothing:
the simulator's own ``tone`` state is the authoritative record, and tests
assert on that.
"""
import array

import pygame

AMPLITUDE = 5000            # of 32767: a clear beep, not a loud one
MAX_SECONDS = 10.0          # longest single note rendered
_CACHE_LIMIT = 64

# Rendered PCM by (frequency, seconds, rate, channels). Raw bytes are cached,
# never pygame Sound/Channel objects: those dangle after a pygame.quit() and
# crash the process on next use (the same trap as a cached Font).
_pcm_cache = {}
_unusable = False


def square_wave(frequency, seconds, rate=44100, channels=1, amplitude=AMPLITUDE):
    """Signed 16-bit little-endian PCM of a square wave; empty for a rest."""
    frames = int(rate * min(max(0.0, seconds), MAX_SECONDS))
    if frequency <= 0 or frames <= 0:
        return b""
    samples = array.array("h")
    step = frequency / float(rate)
    for i in range(frames):
        value = amplitude if (i * step) % 1.0 < 0.5 else -amplitude
        samples.extend([value] * channels)
    return samples.tobytes()


def _usable_format():
    """``(rate, channels)`` of the running mixer, or ``None``. Starts the mixer
    if nothing has, and gives up for good if it can't."""
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
    if fmt != -16:                       # only 16-bit signed is synthesised
        return None
    return rate, channels


def _reserved_channel():
    """The one channel the speaker uses, reserved so a game's own sounds
    never take it (and it never takes theirs). Fetched fresh each time."""
    try:
        if pygame.mixer.get_num_channels() < 2:
            pygame.mixer.set_num_channels(8)
        pygame.mixer.set_reserved(1)
        return pygame.mixer.Channel(0)
    except pygame.error:
        return None


def play(frequency, seconds):
    """Start a note now, replacing whatever the speaker was playing. Returns
    True if it is audible, False if it was a rest or there is no mixer."""
    fmt = _usable_format()
    channel = _reserved_channel() if fmt else None
    if channel is None:
        return False
    if frequency <= 0:
        channel.stop()
        return False
    rate, channels = fmt
    key = (round(frequency, 2), round(seconds, 3), rate, channels)
    data = _pcm_cache.get(key)
    if data is None:
        data = square_wave(frequency, seconds, rate, channels)
        if not data:
            return False
        if len(_pcm_cache) >= _CACHE_LIMIT:
            _pcm_cache.clear()
        _pcm_cache[key] = data
    channel.play(pygame.mixer.Sound(buffer=data))
    return True


def stop():
    """Cut the speaker off."""
    try:
        if pygame.mixer.get_init():
            pygame.mixer.Channel(0).stop()
    except pygame.error:
        pass


def forget():
    """Drop cached audio and the "no mixer" verdict (tests; a new game)."""
    global _unusable
    _pcm_cache.clear()
    _unusable = False
