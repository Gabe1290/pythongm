"""HTML5 export gains remember_destroyed support (follow-up to L17,
docs/FULL_AUDIT_2026-09-07.md, logged in TODO.md).

L17 fixed Kivy's missing "stay destroyed" opt-in
(GameRunner._destroyed_memory / remember_destroyed on the desktop
runtime). That finding's own rationale claimed "(desktop + HTML5
honour it)" -- independently verified false: `grep remember_destroyed
export/HTML5` was empty too, so an object flagged remember_destroyed
respawned on every room restart/revisit on the HTML5 export just like
Kivy did before its own fix.

Fix, mirroring both the desktop runtime and the Kivy port:
- GameObject bakes `this.remember_destroyed` from
  `objectData.remember_destroyed`, alongside the existing `this.solid`.
- Game gains `this._destroyedMemory`: roomName -> Set of
  "objectName|xstart|ystart" identity strings.
- GameRoom.step's cleanup pass (where instances_to_destroy is actually
  processed) records a destroyed instance's identity there when it
  opts in.
- Game.buildRoom -- "the ONE place a room is constructed" per its own
  docstring, covering both startup and every rebuild -- drops a
  remembered instance instead of pushing it. A persistent-room reuse
  never calls buildRoom at all, so it's unaffected (matches the desktop/
  Kivy precedent: only a genuine rebuild prunes).
- restart_game's case handler (a real in-process reset here, NOT
  window.location.reload() -- that changed after this repo's session
  notes were written, see test_restart_game_preserves_globals.py)
  explicitly clears _destroyedMemory, the same way it clears
  _visitedRooms -- this is per-playthrough state, not per-room.

Verification tier, per this repo's "no Node in CI" convention (matching
test_html5_room_actions.py): source-level assertions on engine.js
(brace-balance checked separately) plus a real HTML5Exporter export
whose embedded gameData round-trips the remember_destroyed flag (there
is no other Python-side plumbing to break -- the whole project dict is
dumped straight to JSON).
"""
import json
import re
import tempfile
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# GameObject bakes the flag
# ---------------------------------------------------------------------------

def test_game_object_bakes_remember_destroyed():
    m = re.search(r"class GameObject \{\s*constructor\(name, x, y, data, objectData\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "GameObject constructor not found"
    body = m.group(1)
    assert "this.remember_destroyed = objectData ? (objectData.remember_destroyed || false) : false;" in body


# ---------------------------------------------------------------------------
# Game._destroyedMemory: init, recording, application, restart-game clear
# ---------------------------------------------------------------------------

def test_game_constructor_initializes_destroyed_memory():
    m = re.search(r"class Game \{\s*constructor\(\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "Game constructor not found"
    assert "this._destroyedMemory = {};" in m.group(1)


def test_cleanup_pass_records_destroyed_identity_when_opted_in():
    m = re.search(r"// 8\. Cleanup destroyed instances(.*?)this\.instances = this\.instances\.filter",
                  ENGINE, re.S)
    assert m, "cleanup pass not found in the expected shape"
    body = m.group(1)
    assert "inst.toDestroy && inst.remember_destroyed" in body
    assert "game._destroyedMemory[this.name]" in body
    assert "`${inst.name}|${inst.xstart}|${inst.ystart}`" in body


def test_build_room_prunes_remembered_instances():
    m = re.search(r"    buildRoom\(roomName\)\s*\{(.*?)\n        return room;",
                  ENGINE, re.S)
    assert m, "buildRoom not found"
    body = m.group(1)
    assert "const remembered = this._destroyedMemory[roomName];" in body
    assert "inst.remember_destroyed && remembered &&" in body
    assert "remembered.has(`${inst.name}|${inst.xstart}|${inst.ystart}`)" in body
    # the prune must run BEFORE the instance is pushed into the room
    prune_pos = body.index("remembered.has(")
    push_pos = body.index("room.instances.push(inst);")
    assert prune_pos < push_pos


def test_restart_game_clears_destroyed_memory():
    m = re.search(r"case 'restart_game':\s*\{(.*?)break;\s*\}", ENGINE, re.S)
    assert m, "restart_game case not found"
    body = m.group(1)
    assert "game._destroyedMemory = {};" in body
    assert "game._visitedRooms.clear();" in body  # sanity: same reset scope


# ---------------------------------------------------------------------------
# End-to-end: a real export round-trips the remember_destroyed flag
# ---------------------------------------------------------------------------

def test_remember_destroyed_flag_round_trips_through_a_real_export():
    import base64
    import gzip
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_remember_destroyed_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "remember_destroyed_html5",
        "settings": {"window_width": 320, "window_height": 240},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_gem": {"name": "obj_gem", "sprite": "", "events": {},
                            "remember_destroyed": True},
                "obj_plain": {"name": "obj_plain", "sprite": "", "events": {}},
            },
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 320, "height": 240,
                          "instances": [
                              {"object_name": "obj_gem", "x": 10, "y": 10},
                              {"object_name": "obj_plain", "x": 90, "y": 90},
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
    assert m, "gameData not found embedded in the exported HTML"
    game_data = json.loads(gzip.decompress(base64.b64decode(m.group(1))))

    objects = game_data["assets"]["objects"]
    assert objects["obj_gem"]["remember_destroyed"] is True
    assert objects["obj_plain"].get("remember_destroyed", False) is False
