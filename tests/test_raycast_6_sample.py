"""samples/raycast_6 ("The Junction" / « La jonction »), docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md D5.

The committed files must match tools/gen_raycast_6_junction.py, the two rooms must share the corridor
and its junction marker (the point of the sample), and the game must really play through the real
GameRunner: walking down the corridor takes the player from room0 into room1 at the gate without the
walk stopping or jumping, and the flag ends the game.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402

import gen_raycast_6_junction as gen  # noqa: E402

SAMPLE = ROOT / "samples" / "raycast_6"


def test_the_committed_files_match_the_generator():
    assert gen.check(SAMPLE) == []


def test_every_sprite_file_is_there():
    for name in gen.sprites():
        assert (SAMPLE / "sprites" / f"{name}.png").is_file(), name


def _cells(room, obj):
    return {(i["x"] // 32, i["y"] // 32) for i in room["instances"] if i["object_name"] == obj}


def test_the_two_rooms_share_the_corridor_and_its_junction():
    r0, r1 = gen.room(0), gen.room(1)
    assert _cells(r0, "obj_junction") == _cells(r1, "obj_junction") == {gen.JUNCTION}
    corridor = {(x, y) for x in gen.CORRIDOR_X for y in gen.CORRIDOR_ROWS}
    assert corridor <= _cells(r0, "obj_low") and corridor <= _cells(r1, "obj_low")
    assert _cells(r0, "obj_goal") == _cells(r1, "obj_goal")
    # the gate that leaves each room is not where the other one lets you arrive
    assert {x for x, _ in _cells(r0, "obj_gate_a")} == {gen.GATE_A_X}
    assert {x for x, _ in _cells(r1, "obj_gate_b")} == {gen.GATE_B_X}


def test_the_level_has_what_the_guide_promises():
    objs = gen.objects()
    create = objs["obj_person"]["events"]["create"]["actions"][0]["parameters"]
    assert create["wall_height"] == "3" and create["max_step"] == "12"
    low = objs["obj_low"]["events"]["create"]["actions"][0]
    assert low["action"] == "set_ceiling_height" and low["parameters"]["height"] == "40"
    ev = objs["obj_person"]["events"]
    assert ev["collision_with_obj_gate_a"]["actions"][0]["parameters"] == {
        "room": "room1", "marker": "obj_junction"}
    assert ev["collision_with_obj_gate_b"]["actions"][0]["parameters"] == {
        "room": "room0", "marker": "obj_junction"}
    for name in ("obj_low", "obj_junction", "obj_gate_a", "obj_gate_b"):
        assert objs[name]["visible"] is False and not objs[name]["solid"]


def _play(script, frames):
    from runtime.game_runner import GameRunner
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    runner = GameRunner(str(SAMPLE / "project.json"))
    runner.language = "en"
    messages = []
    runner.show_message_dialog = lambda *a, **k: messages.append(a[0] if a else "")
    runner.process_pending_messages = lambda *a, **k: None
    trace = []
    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            f = state["f"] = state["f"] + 1
            room = runner.current_room
            p = next((i for i in room.instances if i.object_name == "obj_person"), None)
            for at, action in script:
                if f == at and p is not None:
                    action(runner, p)
            if p is not None:
                trace.append({"room": room.name, "x": p.x, "y": p.y, "facing": p.facing_angle})
            if f >= frames or messages:
                runner.running = False
            return 0

        def get_fps(self):
            return 30.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real_clock
    return runner, trace, messages


def _into_the_corridor(runner, p):
    p.x, p.y, p.facing_angle = 3 * 32, 7 * 32 + 16, 0.0         # in the hall, facing the corridor
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))


def test_walking_the_corridor_crosses_into_room1_without_a_break_and_reaches_the_flag():
    runner, trace, messages = _play([(2, _into_the_corridor)], 400)
    rooms = [t["room"] for t in trace]
    assert rooms[0] == "room0" and "room1" in rooms
    assert rooms == sorted(rooms)                                # room0 ... room0, room1 ... room1: once
    walk = [t for t in trace[3:]]
    steps = [b["x"] - a["x"] for a, b in zip(walk, walk[1:])]
    assert all(0 <= s <= 4 for s in steps), max(steps)           # never stops, never jumps
    assert all(abs(t["y"] - walk[0]["y"]) < 1 for t in walk)
    assert all(t["facing"] == 0.0 for t in walk)                 # the facing is carried across
    assert messages and "junction" in messages[0]                # the flag, in room1


def test_without_walking_the_player_stays_in_the_start_hall():
    runner, trace, messages = _play([], 30)
    assert {t["room"] for t in trace} == {"room0"} and not messages


def test_room0_has_the_gallery_and_room1_the_low_ceiling_under_it():
    from extensions.raycast_2_5d.heights import build_ceiling_heights, build_floor_heights
    seen = {}

    def probe(name):
        def run(runner, p):
            room = runner.current_room
            heights, _ = build_floor_heights(room, 32, 1e9)
            ceilings, _ = build_ceiling_heights(room, 32, 96.0, heights, 24.0)
            seen[name] = (room.name, heights, ceilings)
        return run

    _play([(3, probe("room0")), (2, _into_the_corridor), (92, probe("room1"))], 400)
    name0, heights, c0 = seen["room0"]
    name1, _, c1 = seen["room1"]
    assert (name0, name1) == ("room0", "room1")
    assert heights[(3, 2)] == gen.GALLERY and heights[(3, 6)] == 8 and heights[(3, 4)] == 24
    hall = {(x, y) for x in gen.HALL_X for y in range(1, 14)}
    assert hall <= set(c1) and not (hall & set(c0))              # the hall is low only in room1
    assert all(v == gen.TUNNEL for v in c1.values())
