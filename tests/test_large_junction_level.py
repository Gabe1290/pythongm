"""Guard: tools/perf_levels/large_junction stays generated, legal and playable.

Regenerate with `python3 tools/gen_large_junction_level.py`. Walkability is checked cell by cell
with the camera's rule (climb at most max_step = 12 px, drop any height); openings are at least
two cells wide, so the 32 px player really fits through them.
"""
import importlib.util
import json
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEVEL = REPO / "tools" / "perf_levels" / "large_junction"
MAX_STEP = 12
EYE = 24
MARGIN = 4
WALL_TOP = 3 * 32


def _gen():
    spec = importlib.util.spec_from_file_location(
        "gen_large_junction_level", REPO / "tools" / "gen_large_junction_level.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _gen()
UPPER, CRYPT = GEN.upper(), GEN.crypt()


def _reach(g, start):
    seen, todo = {start}, deque([start])
    while todo:
        x, y = todo.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in seen or n in g.walls or not (0 <= n[0] < GEN.SIZE and 0 <= n[1] < GEN.SIZE):
                continue
            if g.floor.get(n, 0) - g.floor.get((x, y), 0) <= MAX_STEP:
                seen.add(n)
                todo.append(n)
    return seen


def _cells(g, prefix):
    return [(x, y) for obj, x, y in g.things if obj.startswith(prefix)]


def test_committed_rooms_match_the_generator():
    for name, g in (("room0", UPPER), ("room1", CRYPT)):
        room = json.loads((LEVEL / "rooms" / f"{name}.json").read_text(encoding="utf-8"))
        assert room == GEN.room_dict(name, g), f"{name} is stale: run the generator"


def test_every_height_is_legal():
    for g in (UPPER, CRYPT):
        for cell, h in g.floor.items():
            assert h <= (3 - 0.75) * 32 - MARGIN, (cell, h)
            assert g.ceil.get(cell, WALL_TOP) >= h + EYE + MARGIN, (cell, h, g.ceil.get(cell))


def test_the_upper_level_is_walkable_from_the_start():
    reach = _reach(UPPER, GEN.START)
    for cell in _cells(UPPER, "obj_gate_a"):
        assert cell in reach, ("gate", cell)
    for name, cell in {"pyramid top": (24, 12), "gallery": (5, 2), "plaza": (40, 10)}.items():
        assert cell in reach, name


def test_every_crypt_arrival_reaches_the_flags_and_a_way_back():
    arrivals = _cells(UPPER, "obj_gate_a")            # you land where you crossed the gate
    for start in arrivals:
        reach = _reach(CRYPT, start)
        for cell in _cells(CRYPT, "obj_goal") + _cells(CRYPT, "obj_gate_b"):
            assert cell in reach, (start, cell)


def test_no_gate_where_the_other_room_lands_you():
    assert not set(_cells(UPPER, "obj_gate_a")) & set(_cells(CRYPT, "obj_gate_b"))
    for g in (UPPER, CRYPT):
        markers = _cells(g, "obj_junction_")
        assert len(markers) == len(GEN.JUNCTIONS) == len(set(markers))
