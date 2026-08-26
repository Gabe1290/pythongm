"""HTML5 export — Room-category actions: set_room_speed, set_background_color,
set_room_persistent, set_background.

Desktop runtime support for these four landed in 6ddc0e2; Kivy's followed in
two commits (test_kivy_room_actions.py). This closes the HTML5 gap.

Architecturally different from Kivy: HTML5 has no separate codegen step at
all — the exporter dumps the WHOLE project (rooms/objects/actions) straight
into `gameData` as JSON (html5_exporter.py's `json.dumps(project_data, ...)`,
proven unchanged by test_views_project_exports_and_boots_shape's precedent),
and engine.js's `executeAction` is a single shared runtime interpreter that
reads `action.parameters` generically. So there's nothing to generate per
room/action — the work is entirely inside engine.js's `case` handlers,
`GameRoom`, and `Game.changeRoom`/`buildRoom`.

Two real behavioral differences from Kivy worth calling out (both explained
in engine.js comments at the edit sites too):
 - HTML5's game loop is NOT dt-scaled (`this.x += this._hspeed`, no delta
   time) — the opposite architecture from Kivy's frame-rate-independent
   model. set_room_speed therefore scales hspeed/vspeed's final per-tick
   delta by `roomSpeed / 60`, NOT the game loop's call rate (which stays
   rAF-driven/uncapped) — a documented approximation, not a full
   step-rate throttle like desktop's `clock.tick(fps)`.
 - HTML5 previously reused every room FOREVER (`this.currentRoom =
   this.rooms[roomName]`, a permanent dict populated once at startup) — the
   OPPOSITE default from Kivy (which always rebuilt) and the same bug shape
   desktop had before its own persistent-room fix. set_room_persistent
   needed Game.buildRoom extracted as a reusable method and Game.changeRoom
   taught to rebuild non-persistent rooms fresh on revisit.
 - restart_game needs NO engine change at all: it's already
   `window.location.reload()`, a full page reload that trivially discards
   every room's state, more thorough than Kivy's explicit cache-clearing.

Verification tier, per this repo's "no Node in CI" convention (matching
test_html5_views.py): source-level assertions on engine.js (brace-balance
checked separately in this session — see the commit body) plus a real
HTML5Exporter export whose embedded gameData round-trips the project data
that drives these actions, proving the Python-side pass-through (there is no
other Python-side plumbing to break).
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
# GameRoom state
# ---------------------------------------------------------------------------

def test_room_bakes_persistent_and_room_speed():
    m = re.search(r"class GameRoom \{\s*constructor\(data\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "GameRoom constructor not found"
    body = m.group(1)
    assert "this.persistent = !!data.persistent;" in body
    assert "this.roomSpeed = 60;" in body
    assert "this.showBackgroundColor = true;" in body
    assert "this.dynamicBgName = '';" in body
    assert "this.dynamicBgVisible = false;" in body
    assert "this.dynamicBgForeground = false;" in body
    assert "this.dynamicBgTileH = false;" in body
    assert "this.dynamicBgTileV = false;" in body
    assert "this.dynamicBgHspeed = 0;" in body
    assert "this.dynamicBgVspeed = 0;" in body
    assert "this.dynamicBgScrollX = 0;" in body
    assert "this.dynamicBgScrollY = 0;" in body


def test_background_color_fill_honors_show_background_color():
    assert ("ctx.fillStyle = this.showBackgroundColor ? this.bgColor : '#000000';"
            in ENGINE)


# ---------------------------------------------------------------------------
# Dynamic background rendering + scroll
# ---------------------------------------------------------------------------

def test_render_contents_draws_dynamic_background_behind_or_in_front():
    m = re.search(r"    _renderContents\(ctx\)\s*\{(.*?)\n    \}\n\n    // Advances",
                  ENGINE, re.S)
    assert m, "_renderContents not found in expected shape"
    body = m.group(1)
    assert "if (!this.dynamicBgForeground) this._drawDynamicBackground(ctx);" in body
    assert "if (this.dynamicBgForeground) this._drawDynamicBackground(ctx);" in body
    # the "behind" call must precede the instance draw loop, and the
    # "foreground" call must follow it
    behind_pos = body.index("if (!this.dynamicBgForeground)")
    instances_pos = body.index("sortedInstances.forEach")
    front_pos = body.index("if (this.dynamicBgForeground) this._drawDynamicBackground")
    assert behind_pos < instances_pos < front_pos


def test_draw_dynamic_background_tiling_matches_baked_math():
    m = re.search(r"    _drawDynamicBackground\(ctx\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "_drawDynamicBackground not found"
    body = m.group(1)
    assert "this.dynamicBgTileH || this.dynamicBgHspeed !== 0" in body
    assert "this.dynamicBgTileV || this.dynamicBgVspeed !== 0" in body
    assert "this._gameRef" in body  # resolves the sprite by name via the game ref


def test_advance_dynamic_bg_scroll_scales_by_room_speed():
    m = re.search(r"    _advanceDynamicBgScroll\(\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "_advanceDynamicBgScroll not found"
    body = m.group(1)
    assert "this.roomSpeed / 60" in body
    assert "% iw" in body and "% ih" in body  # wraps modulo texture size
    assert "this._advanceDynamicBgScroll();" in ENGINE  # wired into step()


# ---------------------------------------------------------------------------
# set_room_speed's movement scaling
# ---------------------------------------------------------------------------

def test_process_movement_scales_by_room_speed_factor():
    m = re.search(r"    processMovement\(game\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "processMovement not found"
    body = m.group(1)
    assert "game.currentRoom.roomSpeed / 60" in body
    # Movement now resolves through _movementBlocker (see
    # test_html5_solid_movement_blocking.py) rather than an unconditional
    # `this.x +=` — the roomSpeed-scaled delta still feeds the same
    # newX/newY the blocking check is applied against.
    assert "const newX = this.x + this._hspeed * roomSpeedFactor;" in body
    assert "const newY = this.y + this._vspeed * roomSpeedFactor;" in body


# ---------------------------------------------------------------------------
# Persistent-room cache: buildRoom extraction + changeRoom reuse logic
# ---------------------------------------------------------------------------

def test_build_room_is_a_reusable_method():
    assert "buildRoom(roomName) {" in ENGINE
    # loadGame's startup pass and changeRoom's rebuild path both go through it
    assert "this.rooms[roomName] = this.buildRoom(roomName);" in ENGINE
    m = re.search(r"    changeRoom\(roomName, forceRebuild = false\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "changeRoom(roomName, forceRebuild) not found"
    assert "this.rooms[roomName] = this.buildRoom(roomName);" in m.group(1)


def test_change_room_reuses_only_visited_persistent_rooms():
    m = re.search(r"    changeRoom\(roomName, forceRebuild = false\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "const reuse = !forceRebuild && this._visitedRooms.has(roomName)" in body
    assert "existing && existing.persistent;" in body
    assert "this._visitedRooms.add(roomName);" in body


def test_restart_room_forces_rebuild():
    assert "game.changeRoom(game.currentRoom.name, true);" in ENGINE


def test_restart_game_rebuilds_every_room_in_process():
    # No longer a page reload (tests/test_restart_game_preserves_globals.py
    # covers why: a full reload also wiped game.globalVariables, the
    # promo hub's cross-level score badges). The in-process replacement
    # still discards every room's state unconditionally, same as the
    # reload did and same as desktop's restart_game — so persistence
    # semantics are unaffected.
    m = re.search(r"case 'restart_game':(.*?)break;", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "window.location.reload();" not in body
    assert "game.rooms[roomName] = game.buildRoom(roomName);" in body


def test_first_room_seeded_as_visited_at_startup():
    assert "this._visitedRooms.add(firstRoom);" in ENGINE
    assert "this._visitedRooms = new Set();" in ENGINE


# ---------------------------------------------------------------------------
# Action dispatch (executeAction's switch)
# ---------------------------------------------------------------------------

def test_all_four_actions_dispatched():
    for name in ("set_room_speed", "set_background_color",
                 "set_room_persistent", "set_background"):
        assert f"case '{name}':" in ENGINE, name


def test_set_room_speed_clamps():
    m = re.search(r"case 'set_room_speed':\s*\{(.*?)break;\s*\}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "Math.max(1, Math.min(240, speed))" in body


def test_set_background_string_false_is_not_truthy():
    # The enable_views precedent this mirrors: params come straight from
    # project JSON, which can hold the STRING "false" — a bare `!!params.x`
    # would treat that as true (a real, easy-to-write JS bug).
    m = re.search(r"case 'set_background':\s*\{(.*?)break;\s*\}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "vis === 'false'" in body
    assert "isTruthy" in body


def test_set_room_persistent_string_false_is_not_truthy():
    m = re.search(r"case 'set_room_persistent':\s*\{(.*?)break;\s*\}", ENGINE, re.S)
    assert m
    assert "p === 'false'" in m.group(1)


# ---------------------------------------------------------------------------
# End-to-end: a real export round-trips the project data these actions read
# ---------------------------------------------------------------------------

def test_room_actions_project_exports_and_round_trips():
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_room_actions_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "room_actions_html5",
        "settings": {"window_width": 320, "window_height": 240},
        "assets": {
            "sprites": {}, "sounds": {},
            "backgrounds": {"bg_sky": {"name": "bg_sky", "file_path": ""}},
            "objects": {
                "obj_setter": {
                    "name": "obj_setter", "sprite": "",
                    "events": {
                        "create": {"actions": [
                            {"action": "set_room_speed", "parameters": {"speed": 45}},
                            {"action": "set_background_color",
                             "parameters": {"color": "#112233", "show_color": False}},
                            {"action": "set_room_persistent",
                             "parameters": {"persistent": True}},
                            {"action": "set_background",
                             "parameters": {
                                 "background": "bg_sky", "visible": True,
                                 "foreground": False, "tiled_h": True,
                                 "tiled_v": False, "hspeed": 2, "vspeed": 0}},
                        ]},
                    },
                },
            },
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 320, "height": 240,
                          "persistent": True,
                          "instances": [{"object_name": "obj_setter", "x": 0, "y": 0}]},
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

    assert embedded["assets"]["rooms"]["rm_a"]["persistent"] is True
    actions = embedded["assets"]["objects"]["obj_setter"]["events"]["create"]["actions"]
    action_names = [a["action"] for a in actions]
    assert action_names == ["set_room_speed", "set_background_color",
                             "set_room_persistent", "set_background"]
    set_bg = next(a for a in actions if a["action"] == "set_background")
    assert set_bg["parameters"]["background"] == "bg_sky"
    assert set_bg["parameters"]["tiled_h"] is True

    # engine.js is inlined into the single exported .html, not a separate file
    assert "case 'set_background':" in html
