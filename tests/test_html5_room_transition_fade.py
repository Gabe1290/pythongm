"""HTML5 export — goto_room's transition='fade' (TODO.md: "Room-transition
fade effect isn't ported to HTML5/Kivy exports").

Desktop's GameRunner.change_room/_fade_overlay blocks in a pygame
sub-loop for the duration of the fade -- a browser's main thread can't
block like that, so Game.changeRoom now starts a small non-blocking
state machine (this._fadeTransition) instead, ticked and drawn from
gameLoop's existing render phase (which already runs every frame
regardless of this._sleepUntil freezing gameplay stepping, the same gate
the 'sleep' action already uses). The actual room switch (what used to
be the whole body of changeRoom) moved to _changeRoomImmediate, called
either directly (transition='none', unchanged behaviour) or at the
fade-out/fade-in midpoint from _renderFadeTransition.

Only goto_room's own explicit transition param ever sets this -- the
__next__/__previous__/__restart__ sentinels, and the separate next_room/
previous_room/restart_room/restart_game cases, never pass a transition,
matching desktop's execute_goto_room_action/change_room scope exactly.

No Node.js in CI (this repo's established convention, matching
test_html5_room_actions.py/test_html5_views.py): source-level regex
assertions on engine.js, plus a real HTML5Exporter export whose embedded
gameData round-trips a goto_room action's transition parameter -- proving
the Python-side pass-through, since there is no other Python-side
plumbing here at all (HTML5 has no per-project codegen step; engine.js's
executeAction reads action.parameters generically at runtime).
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


# ---------------------------------------------------------------------------
# Source-level structure
# ---------------------------------------------------------------------------

def test_fade_duration_constant_matches_desktop():
    # Desktop: GameRunner._FADE_TRANSITION_SECONDS = 0.25
    assert "const FADE_TRANSITION_MS = 250;" in ENGINE


def test_game_constructor_initializes_fade_state():
    m = re.search(r"class Game \{\s*constructor\(\) \{(.*?)\n    \}", ENGINE, re.S)
    assert m, "Game constructor not found"
    assert "this._fadeTransition = null;" in m.group(1)


def test_change_room_signature_accepts_transition():
    assert "changeRoom(roomName, forceRebuild = false, transition = 'none') {" in ENGINE


def test_change_room_fade_branch_does_not_switch_immediately():
    m = re.search(r"changeRoom\(roomName, forceRebuild = false, transition = 'none'\) \{(.*?)\n    \}\n\n    _changeRoomImmediate",
                   ENGINE, re.S)
    assert m, "changeRoom body not found"
    body = m.group(1)
    assert "if (transition === 'fade'" in body
    assert "phase: 'out'," in body
    assert "targetRoom: roomName," in body
    assert "this._sleepUntil = Date.now() + durationMs * 2;" in body
    assert "return;" in body
    # Falls through to the immediate switch only for a non-fade transition.
    assert "this._changeRoomImmediate(roomName, forceRebuild);" in body


def test_change_room_immediate_still_has_the_original_switch_logic():
    """The pre-existing body (room rebuild/reuse, _visitedRooms, canvas
    resize) must have moved verbatim into _changeRoomImmediate, not been
    rewritten -- this is the one thing that must stay behaviour-identical
    for transition='none', which is the overwhelming majority of real
    goto_room calls."""
    m = re.search(r"_changeRoomImmediate\(roomName, forceRebuild = false\) \{(.*?)\n    \}\n",
                   ENGINE, re.S)
    assert m, "_changeRoomImmediate body not found"
    body = m.group(1)
    assert "this.rooms[roomName] = this.buildRoom(roomName);" in body
    assert "this._visitedRooms.add(roomName);" in body
    assert "this.currentRoom._pendingRoomStart = true;" in body
    assert "this.canvas.width = this.currentRoom.width;" in body


def test_render_fade_transition_method_exists_and_is_called_from_game_loop():
    assert "_renderFadeTransition() {" in ENGINE
    m = re.search(r"gameLoop\(\) \{(.*?)requestAnimationFrame", ENGINE, re.S)
    assert m, "gameLoop body not found"
    body = m.group(1)
    # Called after drawHUD (the fade overlay sits on top of the HUD, same
    # as desktop drawing the fade overlay over everything already rendered).
    hud_pos = body.index("this.drawHUD();")
    fade_pos = body.index("this._renderFadeTransition();")
    assert fade_pos > hud_pos


def test_render_fade_transition_switches_rooms_at_the_midpoint():
    m = re.search(r"_renderFadeTransition\(\) \{(.*?)\n    \}\n", ENGINE, re.S)
    assert m, "_renderFadeTransition body not found"
    body = m.group(1)
    assert "t.phase === 'out' && elapsed >= t.durationMs" in body
    assert "this._changeRoomImmediate(t.targetRoom, t.forceRebuild);" in body
    assert "t.phase = 'in';" in body
    # fade-out ramps alpha up (revealing black); fade-in ramps it down
    # (revealing the new room) -- the exact mirror of desktop's _fade_overlay.
    assert "t.phase === 'out' ? progress : 1 - progress" in body
    assert "this._fadeTransition = null;" in body


def test_goto_room_action_case_forwards_transition():
    m = re.search(r"case 'goto_room':(.*?)break;", ENGINE, re.S)
    assert m, "goto_room action case not found"
    body = m.group(1)
    assert "game.changeRoom(roomName, false, params.transition || 'none');" in body


def test_other_room_actions_never_pass_a_transition():
    """Matches desktop's scope exactly: next_room/previous_room/
    restart_room/restart_game never request a fade."""
    assert "game.changeRoom(nextRoomName);" in ENGINE
    assert "game.changeRoom(prevRoomName);" in ENGINE
    assert "game.changeRoom(game.currentRoom.name, true);" in ENGINE
    assert "game.changeRoom(firstRoomName, true);" in ENGINE


# ---------------------------------------------------------------------------
# Real export round-trip -- Python-side pass-through only (no codegen here)
# ---------------------------------------------------------------------------

def test_goto_room_with_fade_transition_exports_and_round_trips():
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_fade_transition_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "fade_transition_html5",
        "settings": {"window_width": 320, "window_height": 240},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_door": {
                    "name": "obj_door", "sprite": "",
                    "events": {
                        "create": {"actions": [
                            {"action": "goto_room",
                             "parameters": {"room": "rm_b", "transition": "fade"}},
                        ]},
                    },
                },
            },
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 320, "height": 240,
                          "instances": [{"object_name": "obj_door", "x": 0, "y": 0}]},
                "rm_b": {"name": "rm_b", "width": 320, "height": 240, "instances": []},
            },
        },
        "room_order": ["rm_a", "rm_b"],
    }
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)

    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    embedded = json.loads(gzip.decompress(base64.b64decode(m.group(1))))

    actions = embedded["assets"]["objects"]["obj_door"]["events"]["create"]["actions"]
    goto = next(a for a in actions if a["action"] == "goto_room")
    assert goto["parameters"]["room"] == "rm_b"
    assert goto["parameters"]["transition"] == "fade"

    # engine.js is inlined into the single exported .html, not a separate file
    assert "_fadeTransition" in html
