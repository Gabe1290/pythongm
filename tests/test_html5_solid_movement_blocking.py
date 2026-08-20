"""HTML5 export — automatic solid-collision movement blocking.

Bug report: raycast_4's HTML5 export let the player walk straight through
walls. Root cause: engine.js's processMovement() applied hspeed/vspeed
unconditionally ("always move, collision events will handle response") and
relied entirely on the moving object's own collision-event ACTIONS to stop
it. The desktop runtime (GameRunner.check_movement_collision_with_blocker)
and the Kivy export (GameObject._movement_blocker) both instead block
movement automatically whenever a collision event is *registered* between
the two object types (even with zero actions) and at least one side is
`solid` — a wall's own collision handler is commonly left empty and blocks
purely through the `solid` flag, which is exactly the shape every raycast
sample's obj_person/obj_wall_h/obj_wall_v pair uses.

This ports the same blocking rule into engine.js's processMovement, per
axis, matching Kivy's GameObject._movement_blocker precedent (including its
"let it escape if already overlapping" rule so a spawn-position overlap
can't freeze an instance in place).

Verification tier, per this repo's "no Node in CI" convention (matching
test_html5_room_actions.py / test_html5_views.py): source-level assertions
on engine.js here. The actual behavioral proof — real Chromium via
Playwright (not a CI dependency, installed ad hoc for this session) driving
an exported raycast_4, maze_1, and plateforme_2 — showed: raycast_4's player
walked to x=902 in 6s pre-fix (straight through the first wall) vs. stopping
dead at x=107 and staying there post-fix; maze_1's grid-snap wall-stop and
plateforme_2's platform-resting/falling behavior were pixel-for-pixel
unchanged pre- vs. post-fix (both already worked via their own authored
collision actions, which this change doesn't bypass).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _method_body(name):
    m = re.search(r"    " + re.escape(name) + r"\([^)]*\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, f"{name} not found"
    return m.group(1)


def test_process_movement_no_longer_moves_unconditionally():
    body = _method_body("processMovement")
    assert "always move, collision events will handle response" not in body
    # The roomSpeed-scaled delta is computed into newX/newY, not applied
    # directly to this.x/this.y.
    assert "const newX = this.x + this._hspeed * roomSpeedFactor;" in body
    assert "const newY = this.y + this._vspeed * roomSpeedFactor;" in body


def test_process_movement_falls_back_to_unconditional_move_without_room():
    # Defensive fallback for a caller with no room context (shouldn't
    # normally happen) — must not throw, must still move.
    body = _method_body("processMovement")
    assert "if (!game || !game.currentRoom) {" in body
    assert "this.x = newX;" in body
    assert "this.y = newY;" in body


def test_process_movement_resolves_axes_independently():
    body = _method_body("processMovement")
    # x resolved (and applied) before y is even computed against a blocker,
    # matching the desktop/Kivy "horizontal all-or-nothing, then vertical"
    # order — a diagonal mover sliding along a wall keeps the axis that
    # isn't blocked instead of cancelling both.
    x_check = body.index("_movementBlocker(newX, this.y, game)")
    y_check = body.index("_movementBlocker(this.x, newY, game)")
    assert x_check < y_check


def test_process_movement_dedupes_and_fires_blocked_collisions():
    body = _method_body("processMovement")
    assert "const blockers = [];" in body
    assert "const fired = [];" in body
    assert "if (fired.indexOf(blocker) !== -1) continue;" in body
    assert "this._fireBlockedCollision(blocker, game);" in body


def test_movement_blocker_requires_registered_event_and_solid():
    body = _method_body("_movementBlocker")
    assert "if (!(this.solid || other.solid)) continue;" in body
    assert "if (!this._collisionEventExistsWith(other)) continue;" in body


def test_movement_blocker_lets_already_overlapping_pair_escape():
    body = _method_body("_movementBlocker")
    assert "const curRect = this.getBoundingBox();" in body
    assert "if (this.rectsCollide(curRect, otherRect)) continue;" in body


def test_collision_event_exists_checks_both_directions():
    body = _method_body("_collisionEventExistsWith")
    assert "this.events && this.events['collision_with_' + other.name]" in body
    assert "other.events && other.events['collision_with_' + this.name]" in body


def test_fire_blocked_collision_sets_collision_context_both_sides():
    body = _method_body("_fireBlockedCollision")
    # Mirrors checkCollisions()'s own _collision_other/_collision_speeds
    # protocol so action handlers reading `other` behave identically
    # whether triggered by a blocked move or a normal post-move overlap.
    assert "this._collision_other = other;" in body
    assert "this._collision_speeds = { selfHspeed, selfVspeed, otherHspeed, otherVspeed };" in body
    assert "other._collision_other = this;" in body
    assert "other.executeActions(theirs.actions || [], game);" in body


def test_engine_brace_balance_unaffected():
    # Cheap sanity check this edit didn't unbalance the file (matching this
    # repo's established verification for hand-edited engine.js sections).
    assert ENGINE.count("{") == ENGINE.count("}")
    assert ENGINE.count("(") == ENGINE.count(")")
