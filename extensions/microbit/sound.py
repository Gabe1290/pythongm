#!/usr/bin/env python3
"""Notes, melodies and tones as the simulator plays them (Stage S8).

Pure -- no pygame. ``melody_notes`` turns MicroPython's note strings
(``"C4:4"``, ``"Eb:8"``, ``"R:2"``) into ``(frequency_hz, seconds)`` steps,
following MicroPython's ``music.play`` (modmusic.cpp ``start_note``): the
octave and duration persist from one note to the next within a melody, a
quarter note is 4 ticks, 4 ticks make a beat and the default tempo is
120 bpm. Each note sounds for its length less a 10 ms articulation, then
rests for those 10 ms, as on the device.
"""
from .melodies import MELODIES

DEFAULT_BPM = 120
DEFAULT_TICKS = 4
DEFAULT_OCTAVE = 4
DEFAULT_DURATION = 4
ARTICULATION = 0.010
MAX_FREQUENCY = 20000

# Periods (microseconds) of octave 4, in MicroPython's order A B C D E F G
# (modmusic.cpp), and of the sharps A# - C# D# - F# G#.
_PERIODS_US = {"A": 2273, "B": 2025, "C": 3822, "D": 3405, "E": 3034,
               "F": 2863, "G": 2551}
_SHARPS_US = {"A": 2145, "C": 3608, "D": 3214, "F": 2703, "G": 2408}
# E# and B# have no entry on the device (silence); here they are the next
# natural note, and Cb / Fb the previous one, which is what a musician means.
_ENHARMONIC = {"E#": ("F", 0), "B#": ("C", 1), "Cb": ("B", -1), "Fb": ("E", 0)}
_FLAT_OF = {"A": "G", "B": "A", "D": "C", "E": "D", "G": "F"}   # Ab -> G# ...


def _period_us(letter, sharp, octave):
    base = _SHARPS_US[letter] if sharp else _PERIODS_US[letter]
    shift = octave - 4
    return base >> shift if shift >= 0 else base << -shift


def note_frequency(letter, accidental, octave):
    """Frequency (Hz) of a note, e.g. ``("A", "", 4)`` is 440 Hz."""
    letter = letter.upper()
    key = letter + accidental
    if key in _ENHARMONIC:
        letter, octave_shift = _ENHARMONIC[key]
        octave += octave_shift
        sharp = False
    elif accidental == "#":
        sharp = True
    elif accidental == "b":
        letter, sharp = _FLAT_OF[letter], True
    else:
        sharp = False
    period = _period_us(letter, sharp, octave)
    return min(MAX_FREQUENCY, 1_000_000.0 / period) if period > 0 else 0.0


def _parse_note(text, state):
    """One note string -> (frequency, ticks); updates ``state`` (octave and
    duration persist). Raises ``ValueError`` for anything else."""
    token = text.strip()
    if not token:
        raise ValueError("empty note")
    letter = token[0].upper()
    if letter not in "ABCDEFGR":
        raise ValueError(f"not a note: {text!r}")
    pos = 1
    accidental = ""
    if letter != "R" and pos < len(token) and token[pos] in "#b":
        accidental = token[pos]
        pos += 1
    if pos < len(token) and token[pos] != ":":
        if not token[pos].isdigit():
            raise ValueError(f"bad octave in {text!r}")
        state["octave"] = int(token[pos])
        pos += 1
    if pos < len(token):
        if token[pos] != ":" or not token[pos + 1:].isdigit():
            raise ValueError(f"bad duration in {text!r}")
        state["duration"] = int(token[pos + 1:])
    freq = 0.0 if letter == "R" else note_frequency(letter, accidental, state["octave"])
    return freq, state["duration"]


def melody_notes(spec, bpm=DEFAULT_BPM, ticks=DEFAULT_TICKS):
    """The ``(frequency_hz, seconds)`` steps of a melody. ``spec`` is a
    built-in name (``"DADADADUM"``, any case), a sequence of note strings, or
    one string of notes separated by spaces."""
    if isinstance(spec, str):
        named = MELODIES.get(spec.strip().upper())
        spec = named if named is not None else spec.split()
    if not spec:
        raise ValueError("no notes")
    bpm = max(1, int(bpm))
    tick_seconds = (60.0 / bpm) / ticks
    state = {"octave": DEFAULT_OCTAVE, "duration": DEFAULT_DURATION}
    steps = []
    for text in spec:
        freq, duration = _parse_note(str(text), state)
        sounding = max(ARTICULATION, tick_seconds * duration - ARTICULATION)
        steps.append((freq, sounding))
        steps.append((0.0, ARTICULATION))
    return steps


def tone_notes(frequency, milliseconds):
    """A single tone as steps: frequency clamped to 0-20000 Hz, at least 1 ms."""
    freq = max(0.0, min(float(MAX_FREQUENCY), float(frequency)))
    return [(freq, max(0.001, float(milliseconds) / 1000.0))]
