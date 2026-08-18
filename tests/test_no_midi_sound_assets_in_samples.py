#!/usr/bin/env python3
"""
Regression: bundled samples must not ship raw .mid/.midi sound assets
(2026-08-14).

pygame.mixer.Sound() (what this runtime uses for every sound, including
looped background music -- there is no separate pygame.mixer.music/
streaming path) needs a system MIDI synth (e.g. Timidity + a soundfont) to
decode a .mid file at all. That's not guaranteed to exist on a player's
machine for an exported/shipped game (Windows/macOS ship no MIDI synth by
default, and browsers don't reliably decode .mid via <audio> either), so a
.mid sound asset is a real portability gap, not just a dev-box annoyance --
confirmed by tools/smoke_run_samples.py logging "Couldn't open timidity.cfg"
for treasure/maze_2/maze_3/maze_4 on a box without Timidity installed.

Those four were converted to .ogg (rendered via fluidsynth + a GM soundfont,
then vorbis-encoded) -- this pins that fix and guards against a future
GMK import or hand-added sample reintroducing a raw .mid sound.
"""

import json
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def _iter_sample_project_jsons():
    for project_json in sorted(SAMPLES_DIR.glob("*/project.json")):
        with open(project_json, encoding="utf-8") as f:
            data = json.load(f)
        yield project_json, data


def test_no_sound_asset_file_path_is_midi():
    offenders = []
    for project_json, data in _iter_sample_project_jsons():
        sounds = data.get("assets", {}).get("sounds", {})
        for name, entry in sounds.items():
            file_path = str(entry.get("file_path", "")).lower()
            if file_path.endswith((".mid", ".midi")):
                offenders.append(f"{project_json}: sound '{name}' -> {file_path}")
    assert not offenders, "MIDI sound asset(s) found:\n" + "\n".join(offenders)


def test_no_midi_files_physically_present_in_any_sample_sounds_dir():
    offenders = [
        str(p) for p in SAMPLES_DIR.glob("*/sounds/*")
        if p.suffix.lower() in (".mid", ".midi")
    ]
    assert not offenders, "MIDI sound file(s) found on disk:\n" + "\n".join(offenders)


def test_previously_midi_samples_now_reference_ogg():
    # Pins the specific 2026-08-14 fix, not just the general rule above.
    expected = {
        "treasure": ("music", "sounds/music.ogg"),
        "maze_2": ("sound_background", "sounds/sound_background.ogg"),
        "maze_3": ("sound_background", "sounds/sound_background.ogg"),
        "maze_4": ("sound_background", "sounds/sound_background.ogg"),
    }
    for sample_name, (sound_name, expected_path) in expected.items():
        project_json = SAMPLES_DIR / sample_name / "project.json"
        with open(project_json, encoding="utf-8") as f:
            data = json.load(f)
        entry = data["assets"]["sounds"][sound_name]
        assert entry["file_path"] == expected_path, (sample_name, entry["file_path"])
        assert (SAMPLES_DIR / sample_name / expected_path).exists()
