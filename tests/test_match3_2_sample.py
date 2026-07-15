"""Bundled match3_2 sample — integrity checks.

match3_2 is the sprite/sound/animation follow-up to match3_1 (see that
sample's Roadmap). Same architecture — four execute_code events on one
controller object, no scripts — so this mirrors test_match3_sample.py's
checks, plus the assets and state-machine additions specific to this
version (sprite tiles, sound-queue calls, swap animation state). Qt-free
(no qapp fixture) so it runs without pytest-qt.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = REPO_ROOT / "samples" / "match3_2"

REQUIRED_EVENTS = ("create", "mouse_left_press", "step", "draw")
GEM_COLORS = ("red", "blue", "green", "yellow")
SOUND_NAMES = ("snd_swap", "snd_match", "snd_cascade")


def _object_data():
    return json.loads(
        (SAMPLE / "objects" / "obj_GridManager.json").read_text(encoding="utf-8"))


def _event_code(name):
    return _object_data()["events"][name]["actions"][0]["parameters"]["code"]


def test_sample_ships_complete():
    for rel in ("project.json", "objects/obj_GridManager.json",
                "rooms/rm_match3.json", "README.md", "CREDITS.txt"):
        assert (SAMPLE / rel).exists(), f"samples/match3_2/{rel} is missing"
    for color in GEM_COLORS:
        assert (SAMPLE / "sprites" / f"spr_gem_{color}.png").exists()
        assert (SAMPLE / "thumbnails" / f"spr_gem_{color}_thumb.png").exists()
    for name in SOUND_NAMES:
        assert (SAMPLE / "sounds" / f"{name}.wav").exists()


def test_registered_in_welcome_tab():
    from widgets.welcome_tab import SAMPLE_PROJECTS
    assert ("samples/match3_2", "Match-3 — Level 2") in SAMPLE_PROJECTS


def test_all_events_present_and_code_compiles():
    events = _object_data()["events"]
    assert set(REQUIRED_EVENTS) <= set(events), (
        f"expected events {REQUIRED_EVENTS}, got {sorted(events)}")
    for name in REQUIRED_EVENTS:
        actions = events[name]["actions"]
        assert actions, f"event {name} has no actions"
        for action in actions:
            assert action["action"] == "execute_code"
            code = action["parameters"]["code"]
            compile(code, f"match3_2/{name}", "exec")


def test_project_json_and_side_files_agree():
    """project.json embeds the object/room too; keep both in sync (unlike
    match3_1, where the embedded copy is deliberately a stale snapshot —
    see test_html5_python_export.py) so there's no merge-order surprise."""
    project = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    embedded_events = project["assets"]["objects"]["obj_GridManager"]["events"]
    side_events = _object_data()["events"]
    assert set(embedded_events) == set(side_events) == set(REQUIRED_EVENTS)


def test_room_contains_the_controller():
    room = json.loads(
        (SAMPLE / "rooms" / "rm_match3.json").read_text(encoding="utf-8"))
    names = [inst["object_name"] for inst in room["instances"]]
    assert names == ["obj_GridManager"]


def test_startup_room_matches():
    project = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    assert project["settings"]["startup_room"] == "rm_match3"
    assert "rm_match3" in project["assets"]["rooms"]


def test_project_declares_the_gem_sprites_and_sounds():
    project = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    sprites = project["assets"]["sprites"]
    sounds = project["assets"]["sounds"]
    for color in GEM_COLORS:
        name = f"spr_gem_{color}"
        assert name in sprites, f"{name} missing from project.json sprites"
        assert sprites[name]["file_path"] == f"sprites/{name}.png"
    for name in SOUND_NAMES:
        assert name in sounds, f"{name} missing from project.json sounds"
        assert sounds[name]["file_path"] == f"sounds/{name}.wav"


def test_sprites_are_tile_sized_with_no_prior_matches():
    """draw_sprite blits at native size (no scaling on desktop/web), so the
    gem art must be tile(96) - 8 == 88px to drop in where match3_1's
    filled-rectangle tile used to be."""
    from PIL import Image
    for color in GEM_COLORS:
        img = Image.open(SAMPLE / "sprites" / f"spr_gem_{color}.png")
        assert img.size == (88, 88), f"spr_gem_{color} is {img.size}, expected (88, 88)"


def test_draw_event_uses_sprite_commands_not_color_fills():
    code = _event_code("draw")
    assert "'type': 'sprite'" in code
    assert "self.sprite_names[color_idx]" in code


def test_sound_queue_used_for_swap_match_cascade():
    mouse_code = _event_code("mouse_left_press")
    step_code = _event_code("step")
    assert "self._sound_queue.append('snd_swap')" in mouse_code
    assert "self._sound_queue.append('snd_match')" in step_code
    assert "self._sound_queue.append('snd_cascade')" in step_code


def test_swap_animation_state_present():
    create_code = _event_code("create")
    for attr in ("swap_off", "swap_speed", "swap_phase", "last_swap",
                 "pending_marks", "arm_swap"):
        assert attr in create_code, f"expected create() to define {attr}"


def test_smoke_runner_covers_the_sample():
    text = (REPO_ROOT / "tools" / "smoke_run_samples.py").read_text(encoding="utf-8")
    assert '"match3_2"' in text, (
        "match3_2 must stay in tools/smoke_run_samples.py SAMPLES so the "
        "headless smoke pass exercises it")


def test_credits_file_covers_new_assets():
    text = (SAMPLE / "CREDITS.txt").read_text(encoding="utf-8")
    for color in GEM_COLORS:
        assert f"spr_gem_{color}.png" in text
    for name in SOUND_NAMES:
        assert f"{name}.wav" in text
    assert "CC0" in text
