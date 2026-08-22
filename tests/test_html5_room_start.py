"""HTML5 export — the room_start event was entirely unimplemented.

runtime/game_runner.py's trigger_room_start_event fires `room_start` on
every instance in the room, on EVERY room entry (initial game start,
goto_room, restart_room, restart_game) — always after that entry's create
events, and after game_start on the one entry where both fire. Crucially,
it also fires for a room reused wholesale via HTML5's room-level
`set_room_persistent` (Game.changeRoom's `reuse` branch skips buildRoom
entirely, so none of that room's instances get a fresh create) — this is
the actual reason room_start exists as a distinct event from create at
all: it is the only hook that reliably fires on every room visit,
regardless of whether the instances in it are freshly built or carried
over. `engine.js` had zero references to "room_start" anywhere before this
fix; the event was simply never dispatched.

Verification tier, per this repo's "no Node in CI" convention (matching
test_html5_room_actions.py): source-level assertions on engine.js, plus a
real HTML5Exporter export proving the round-trip. The full behavioral
proof — a real headless-Chromium run (Playwright, not a CI dependency)
against a two-room export (rm_a non-persistent, rm_b persistent) — showed
exactly the matrix this event exists to support:

  initial rm_a:            create=1 game_start=1 room_start=1
  -> rm_b (fresh):          create=1 game_start=0 room_start=1
  -> rm_a (rebuilt fresh):  create=1 game_start=0 room_start=1
  -> rm_b (persistent reuse): create=1 (UNCHANGED) game_start=0 room_start=2

The last line is the one that matters: create did NOT re-fire on the
persistent room's second visit, but room_start did.
"""
import base64
import gzip
import json
import re
import tempfile
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _method_body(name):
    m = re.search(r"    " + re.escape(name) + r"\([^)]*\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, f"{name} not found"
    return m.group(1)


def test_game_room_constructor_arms_pending_room_start():
    m = re.search(r"class GameRoom \{\s*constructor\(data\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "GameRoom constructor not found"
    assert "this._pendingRoomStart = true;" in m.group(1)


def test_change_room_rearms_pending_room_start():
    body = _method_body("changeRoom")
    assert "this.currentRoom._pendingRoomStart = true;" in body


def test_step_dispatches_room_start_after_game_start():
    body = _method_body("step")
    assert "inst.events.room_start" in body
    assert "this._pendingRoomStart = false;" in body
    # Ordering: create (0) -> game_start (0b) -> room_start (0c), matching
    # runtime/game_runner.py's documented "after Create, before Room Start"
    # for game_start, and "after create events" for room_start.
    create_idx = body.index("inst.triggerCreateEvent(game);")
    game_start_idx = body.index("game._gameStartFired = true;")
    room_start_idx = body.index("this._pendingRoomStart = false;")
    assert create_idx < game_start_idx < room_start_idx


def test_room_start_fires_even_when_no_instance_has_a_pending_create():
    """The whole point of a per-ROOM flag instead of reusing the
    per-instance _pendingCreateEvent mechanism: a persistent room reused
    via changeRoom's `reuse` branch never calls buildRoom, so no instance
    in it has _pendingCreateEvent set on that revisit -- room_start must
    not be gated on that flag."""
    body = _method_body("step")
    room_start_block = body[body.index("if (this._pendingRoomStart)"):]
    assert "_pendingCreateEvent" not in room_start_block.split("}", 1)[0]


# ---------------------------------------------------------------------------
# End-to-end: a real export carries room_start events through to gameData.
# ---------------------------------------------------------------------------

def test_room_start_project_exports_and_round_trips():
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_room_start_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "room_start_html5",
        "settings": {"window_width": 200, "window_height": 200},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_logger": {
                    "name": "obj_logger", "sprite": "",
                    "events": {
                        "room_start": {"actions": [
                            {"action": "set_variable", "parameters": {
                                "variable": "room_start_count", "value": "1",
                                "scope": "self", "relative": True}},
                        ]},
                    },
                },
            },
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 200, "height": 200,
                          "persistent": True,
                          "instances": [{"object_name": "obj_logger", "x": 0, "y": 0}]},
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

    actions = embedded["assets"]["objects"]["obj_logger"]["events"]["room_start"]["actions"]
    assert actions[0]["action"] == "set_variable"
    assert actions[0]["parameters"]["variable"] == "room_start_count"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
