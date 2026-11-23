"""Guard: tools/perf_levels/stairs_speed stays the room the stairs speed test measures.

The level exists so a person can feel what
test_raycast_stairs_render.py::test_a_staircase_costs_at_most_a_bit_more_than_a_flat_room
measures; it is only useful while its rooms match that test's `_stairs_room()`.
Regenerate with `python3 tools/gen_stairs_perf_level.py`.
"""

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEVEL = REPO / "tools" / "perf_levels" / "stairs_speed"
CELL = 32


def _generator():
    spec = importlib.util.spec_from_file_location(
        "gen_stairs_perf_level", REPO / "tools" / "gen_stairs_perf_level.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _room(name):
    return json.loads((LEVEL / "rooms" / f"{name}.json").read_text(encoding="utf-8"))


def _cells(room, prefix):
    return {(i["x"] // CELL, i["y"] // CELL): i["object_name"]
            for i in room["instances"] if i["object_name"].startswith(prefix)}


def test_committed_rooms_match_the_generator():
    gen = _generator()
    for name, steps in gen.ROOMS.items():
        assert _room(name) == gen.build_room(name, steps), (
            f"{name} is stale: run tools/gen_stairs_perf_level.py")


def test_staircase_matches_the_speed_test_layout():
    # tests/test_raycast_stairs_render.py::_stairs_room: rows 5..9, steps of
    # 8/16/24/32 px at x = 5..8, a 32 px platform at x = 9..11.
    expected = {}
    for row in range(5, 10):
        for i, x in enumerate(range(5, 9)):
            expected[(x, row)] = f"obj_step_{8 * (i + 1)}"
        for x in range(9, 12):
            expected[(x, row)] = "obj_step_32"
    assert _cells(_room("salle_escalier"), "obj_step_") == expected
    for name in ("obj_step_8", "obj_step_16", "obj_step_24", "obj_step_32"):
        obj = json.loads((LEVEL / "objects" / f"{name}.json").read_text(encoding="utf-8"))
        height = obj["events"]["create"]["actions"][0]["parameters"]["height"]
        assert height == name.rsplit("_", 1)[1]


def test_flat_room_is_the_same_room_without_steps():
    stairs, flat = _room("salle_escalier"), _room("salle_plate")
    assert not _cells(flat, "obj_step_")
    assert _cells(flat, "obj_wall") == _cells(stairs, "obj_wall")
    assert len(_cells(flat, "obj_wall")) == 4 * 15 - 4          # the border, corners once
    for room in (stairs, flat):
        cams = [i for i in room["instances"] if i["object_name"] == "obj_person"]
        assert [(c["x"], c["y"]) for c in cams] == [(2 * CELL, 7 * CELL)]   # the test's camera


def test_project_embeds_both_rooms_and_caps_at_60():
    project = json.loads((LEVEL / "project.json").read_text(encoding="utf-8"))
    assert list(project["assets"]["rooms"]) == ["salle_escalier", "salle_plate"]
    assert project["settings"]["room_speed"] == 60
