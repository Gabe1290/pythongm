"""Guard: tools/perf_levels/base_heights stays generated, in range, and walkable.

Regenerate with `python3 tools/gen_heights_perf_level.py`.
"""

import importlib.util
import json
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEVEL = REPO / "tools" / "perf_levels" / "base_heights"


def _gen():
    spec = importlib.util.spec_from_file_location(
        "gen_heights_perf_level", REPO / "tools" / "gen_heights_perf_level.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _gen()


def _reachable(start):
    """Cells the camera can walk to: climb at most MAX_STEP, drop any height."""
    m, h = GEN.MAP, GEN.HEIGHT_OF
    seen, todo = {start}, deque([start])
    while todo:
        x, y = todo.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            ch = m[ny][nx]
            if ch == "#" or (nx, ny) in seen:
                continue
            if h[ch] - h[m[y][x]] <= GEN.MAX_STEP:
                seen.add((nx, ny))
                todo.append((nx, ny))
    return seen


def test_committed_room_matches_the_generator():
    room = json.loads((LEVEL / "rooms" / f"{GEN.ROOM}.json").read_text(encoding="utf-8"))
    assert room == GEN.build_room(), "stale: run tools/gen_heights_perf_level.py"


def test_seventeen_heights_all_within_the_view_limit():
    heights = {GEN.HEIGHT_OF[c] for row in GEN.MAP for c in row if c != "#"}
    assert heights == set(range(0, 129, 8))
    # heights.max_floor_height: (wall_height - eye 0.75) * cell - 4 margin
    assert max(heights) <= (GEN.WALL_HEIGHT - 0.75) * GEN.CELL - 4


def test_every_area_is_walkable_from_the_start():
    reach = _reachable(GEN.START)
    for name, cell in {"lookout 128 px": (29, 2), "balcony": (25, 6),
                       "courtyard platform": (27, 21), "pit": (6, 20),
                       "zig-zag": (14, 18)}.items():
        assert cell in reach, name
    # The pit has a way out, and the pedestals are deliberately out of reach.
    assert (1, 15) in _reachable((6, 20))
    assert (3, 3) not in reach and (7, 8) not in reach


def test_sludge_uses_its_own_texture_and_people_stand_on_floor():
    sludge = json.loads((LEVEL / "objects" / "obj_sludge.json").read_text(encoding="utf-8"))
    params = sludge["events"]["create"]["actions"][0]["parameters"]
    assert params["top_texture"] == "spr_nukage" and params["height"] == "8"
    assert (LEVEL / "sprites" / "spr_nukage.png").exists()
    for x, y in GEN.GUARDS + GEN.PICKUPS + [GEN.START]:
        assert GEN.MAP[y][x] != "#", (x, y)


def test_readme_maps_match_the_generator():
    for name in ("README.md", "README.fr.md"):
        text = (LEVEL / name).read_text(encoding="utf-8")
        assert "\n".join(GEN.MAP) in text, name
