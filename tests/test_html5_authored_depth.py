"""HTML5 export — every instance's authored depth was silently ignored and
replaced with a hardcoded name-substring heuristic, GameObject.
getDepthForObject: "wall"->5, "box"->10, "soko"/"player"->20,
"ground"/"floor"/"store" (not "box")->0, else->10. Leftover from an early
Sokoban-style prototype, wired into the constructor
(`this.depth = this.getDepthForObject(name)`) and change_instance, and
never updated to read objectData.depth at all -- for every project since,
an object's actual authored `depth` field (events/action_types.py's
"Depth" property, read correctly by the desktop runtime's
GameInstance.set_object_data as `object_data.get('depth', 0)`) simply
never reached the HTML5 renderer.

Found via the promo game's maze level: obj_quit (authored depth -1000,
meant to always draw in front as a screen overlay button) has no name
substring the heuristic recognizes, so it fell into the default bucket
(10). mz_obj_wall (authored depth 0) matched "wall" -> bucket 5. Since
GameRoom._renderContents sorts descending by depth (higher depth drawn
first/further back, lower depth drawn last/in front), 10 > 5 meant the
walls drew ON TOP of the Quitter button — a maze's own walls could cover
its own quit overlay, regardless of what depth the object was actually
authored with. Any project with more than one authored depth value, where
the object names don't happen to match this heuristic's Sokoban
vocabulary, was affected identically.

Verification tier, per this repo's "no Node in CI" convention: source-
level assertions on engine.js, plus a real headless-Chromium run
(Playwright, not a CI dependency) against the actual exported promo game,
confirming the live instances' resolved .depth now matches each object's
authored value (obj_quit: -1000, mz_obj_wall: 0) instead of the heuristic's
bucket values (10, 5).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_get_depth_for_object_heuristic_is_removed():
    assert "getDepthForObject(" not in ENGINE
    assert ".includes('soko')" not in ENGINE


def test_constructor_reads_authored_depth():
    m = re.search(r"class GameObject \{\s*constructor\(name, x, y, data, objectData\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "GameObject constructor not found"
    body = m.group(1)
    assert "this.depth = (objectData && objectData.depth !== undefined) ? objectData.depth : 0;" in body


def test_change_instance_reads_authored_depth_of_the_new_object():
    m = re.search(r"case 'change_instance':\s*\{(.*?)\n            \}", ENGINE, re.S)
    assert m, "change_instance case not found"
    body = m.group(1)
    assert "inst.depth = (objectData && objectData.depth !== undefined) ? objectData.depth : 0;" in body


# ---------------------------------------------------------------------------
# End-to-end: a real export's instances resolve depth from authored data.
# ---------------------------------------------------------------------------

def test_authored_depth_project_exports_and_round_trips():
    import base64
    import gzip
    import json
    import tempfile
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_depth_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "authored_depth_html5",
        "settings": {"window_width": 200, "window_height": 200},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                # Names chosen to hit the OLD heuristic's "wall" bucket (5)
                # and default bucket (10) respectively, while their
                # AUTHORED depths are the opposite of that ordering --
                # proving depth comes from the data, not the name.
                "obj_wall_thing": {"name": "obj_wall_thing", "sprite": "",
                                    "depth": -1000, "events": {}},
                "obj_overlay": {"name": "obj_overlay", "sprite": "",
                                 "depth": 5, "events": {}},
            },
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 200, "height": 200,
                          "instances": [
                              {"object_name": "obj_wall_thing", "x": 0, "y": 0},
                              {"object_name": "obj_overlay", "x": 0, "y": 0},
                          ]},
            },
        },
        "room_order": ["rm_a"],
    }
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)

    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    embedded = json.loads(gzip.decompress(base64.b64decode(m.group(1))))

    assert embedded["assets"]["objects"]["obj_wall_thing"]["depth"] == -1000
    assert embedded["assets"]["objects"]["obj_overlay"]["depth"] == 5


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
