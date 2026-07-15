"""Bundled match3_3 sample — integrity checks.

match3_3 is the move-limit / multi-room-level / special-tile follow-up to
match3_2 (closing match3_1's original three-part roadmap). Same
architecture — four execute_code events on one controller object placed
in three rooms instead of one. Mirrors test_match3_2_sample.py's checks,
plus the level-progression and special-tile additions. Qt-free (no qapp
fixture) so it runs without pytest-qt.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = REPO_ROOT / "samples" / "match3_3"

REQUIRED_EVENTS = ("create", "mouse_left_press", "step", "draw")
GEM_COLORS = ("red", "blue", "green", "yellow")
SOUND_NAMES = ("snd_swap", "snd_match", "snd_cascade", "snd_special", "snd_level_up")
ROOM_NAMES = ("rm_level1", "rm_level2", "rm_level3")


def _object_data():
    return json.loads(
        (SAMPLE / "objects" / "obj_GridManager.json").read_text(encoding="utf-8"))


def _event_code(name):
    return _object_data()["events"][name]["actions"][0]["parameters"]["code"]


def test_sample_ships_complete():
    for rel in ("project.json", "objects/obj_GridManager.json", "README.md", "CREDITS.txt"):
        assert (SAMPLE / rel).exists(), f"samples/match3_3/{rel} is missing"
    for room in ROOM_NAMES:
        assert (SAMPLE / "rooms" / f"{room}.json").exists()
    for color in GEM_COLORS:
        assert (SAMPLE / "sprites" / f"spr_gem_{color}.png").exists()
    for name in SOUND_NAMES:
        assert (SAMPLE / "sounds" / f"{name}.wav").exists()


def test_registered_in_welcome_tab():
    from widgets.welcome_tab import SAMPLE_PROJECTS
    assert ("samples/match3_3", "Match-3 — Level 3") in SAMPLE_PROJECTS


def test_all_events_present_and_code_compiles():
    events = _object_data()["events"]
    assert set(REQUIRED_EVENTS) <= set(events)
    for name in REQUIRED_EVENTS:
        actions = events[name]["actions"]
        assert actions, f"event {name} has no actions"
        for action in actions:
            assert action["action"] == "execute_code"
            compile(action["parameters"]["code"], f"match3_3/{name}", "exec")


def test_three_rooms_each_contain_the_controller():
    for room in ROOM_NAMES:
        data = json.loads((SAMPLE / "rooms" / f"{room}.json").read_text(encoding="utf-8"))
        names = [inst["object_name"] for inst in data["instances"]]
        assert names == ["obj_GridManager"], f"{room}: {names}"


def test_startup_room_and_room_order():
    project = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    assert project["settings"]["startup_room"] == "rm_level1"
    assert project["room_order"] == list(ROOM_NAMES)
    for room in ROOM_NAMES:
        assert room in project["assets"]["rooms"]


def test_project_declares_all_sprites_and_sounds():
    project = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    sprites = project["assets"]["sprites"]
    sounds = project["assets"]["sounds"]
    for color in GEM_COLORS:
        assert f"spr_gem_{color}" in sprites
    for name in SOUND_NAMES:
        assert name in sounds
        assert sounds[name]["file_path"] == f"sounds/{name}.wav"


def test_create_defines_level_config_for_all_three_rooms():
    code = _event_code("create")
    for room in ROOM_NAMES:
        assert f"'{room}'" in code, f"expected level_config to mention {room}"
    assert "self.room_name = room_name" in code, (
        "level advance relies on self.room_name (an instance attribute), "
        "not a bare local, surviving into a later execute_code call")


def test_advance_level_uses_goto_room_target_not_bare_local():
    code = _event_code("create")
    assert "def advance_level():" in code
    assert "self.goto_room_target = self.room_order[idx + 1]" in code
    # The landmine this sample's README documents: a nested def must not
    # close over a bare top-level local from create()'s exec locals.
    assert "self.room_order.index(self.room_name)" in code


def test_mouse_only_spends_a_move_on_a_matching_swap():
    code = _event_code("mouse_left_press")
    assert "if marks:" in code
    assert "self.moves = self.moves - 1" in code


def test_lost_state_retries_via_restart_room_flag():
    mouse_code = _event_code("mouse_left_press")
    step_code = _event_code("step")
    assert "self.lost = True" in step_code
    assert "self.restart_room_flag = True" in mouse_code


def test_step_creates_and_activates_special_tiles():
    code = _event_code("step")
    for marker in ("upgrade_specials", "('row',)", "('col',)", "('color', g[mid[1]][mid[0]])"):
        assert marker in code, f"missing {marker!r} in step()"


def test_draw_renders_special_tile_overlays_and_hud():
    code = _event_code("draw")
    assert "'type': 'ellipse'" in code
    assert "Moves left" in code
    assert "OUT OF MOVES" in code


def test_smoke_runner_covers_the_sample():
    text = (REPO_ROOT / "tools" / "smoke_run_samples.py").read_text(encoding="utf-8")
    assert '"match3_3"' in text


def test_credits_file_covers_new_and_reused_assets():
    text = (SAMPLE / "CREDITS.txt").read_text(encoding="utf-8")
    for name in SOUND_NAMES:
        assert f"{name}.wav" in text
    assert "CC0" in text
