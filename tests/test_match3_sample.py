"""Bundled match3_1 sample — integrity checks.

match3_1 is the first sample authored natively in the pygm2 format (no
.gmk origin). The whole game is four execute_code events on one
controller object, so these tests pin: the files shipping, the Welcome
tab registration, the event code staying valid Python, and the room
actually containing the controller instance. Qt-free (no qapp fixture)
so they run without pytest-qt.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = REPO_ROOT / "samples" / "match3_1"

REQUIRED_EVENTS = ("create", "mouse_left_press", "step", "draw")


def _object_data():
    return json.loads(
        (SAMPLE / "objects" / "obj_GridManager.json").read_text(encoding="utf-8"))


def test_sample_ships_complete():
    for rel in ("project.json", "objects/obj_GridManager.json",
                "rooms/rm_match3.json", "README.md", "CREDITS.txt"):
        assert (SAMPLE / rel).exists(), f"samples/match3_1/{rel} is missing"


def test_registered_in_welcome_tab():
    from widgets.welcome_tab import SAMPLE_PROJECTS
    assert ("samples/match3_1", "Match-3 — Level 1") in SAMPLE_PROJECTS


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
            # A syntax error here would only surface at runtime (the
            # executor logs and continues), i.e. as a dead sample.
            compile(code, f"match3_1/{name}", "exec")


def test_room_contains_the_controller():
    room = json.loads(
        (SAMPLE / "rooms" / "rm_match3.json").read_text(encoding="utf-8"))
    names = [inst["object_name"] for inst in room["instances"]]
    assert names == ["obj_GridManager"]


def test_startup_room_matches():
    project = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    assert project["settings"]["startup_room"] == "rm_match3"
    assert "rm_match3" in project["assets"]["rooms"]


def test_smoke_runner_covers_the_sample():
    text = (REPO_ROOT / "tools" / "smoke_run_samples.py").read_text(encoding="utf-8")
    assert '"match3_1"' in text, (
        "match3_1 must stay in tools/smoke_run_samples.py SAMPLES so the "
        "headless smoke pass exercises it")
