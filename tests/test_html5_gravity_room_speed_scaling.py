"""HTML5's gravity/friction accumulation ran at the browser's real,
uncapped frame rate (~60fps via requestAnimationFrame) regardless of the
room's configured room_speed, while only the FINAL position delta was
scaled by roomSpeedFactor (room_speed / 60). That correctly reproduces
desktop's real-world speed for constant-velocity motion (walking), but
is wrong for accelerating motion (gravity): a jump's arc is a fixed
number of STEPS regardless of real fps, and running twice as many of
those steps per real second (60 vs a configured room_speed of 30) means
reaching peak velocity in half the real time, over half the accumulated
distance — the position-delta scaling alone HALVES a jump's real-world
peak height instead of preserving it.

Found via the promo game's platform level, immediately after fixing
GameRoom.roomSpeed's own missing-settings bug (previous session turn):
desktop's real jump peak is ~115px (pure v²/(2*gravity) kinematics,
unaffected by fps entirely — GameRunner applies vspeed once per real
step with no extra scaling); HTML5's matched that BEFORE the
roomSpeed-from-settings fix landed (accidentally, because roomSpeed was
hardcoded to 60 = no scaling at all, same bug in a different guise) but
dropped to ~55px real peak height once roomSpeed correctly read the
project's actual 30 — the player could no longer reach platforms
desktop's identical physics reaches fine.

Fix: processMovement now scales gravity/friction's per-frame
accumulation by the SAME roomSpeedFactor as the position delta (computed
once, reused for both), so any real span of time accrues exactly as
much velocity, over exactly as much distance, as that span would at the
room's configured room_speed — matching desktop's jump height (and
fall/friction curves), not just its constant-velocity walk speed.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _process_movement_body():
    m = re.search(r"processMovement\(game\) \{(.*?)\n    \}", ENGINE, re.S)
    assert m, "processMovement not found"
    return m.group(1)


def test_room_speed_factor_computed_once_before_gravity():
    body = _process_movement_body()
    factor_idx = body.index("const roomSpeedFactor")
    gravity_idx = body.index("if (this._gravity !== 0)")
    assert factor_idx < gravity_idx, "roomSpeedFactor must be computed before gravity accumulates"


def test_gravity_accumulation_is_scaled_by_room_speed_factor():
    body = _process_movement_body()
    gravity_block = body[body.index("if (this._gravity !== 0)"):body.index("if (this._friction !== 0)")]
    assert "* roomSpeedFactor" in gravity_block
    assert gravity_block.count("* roomSpeedFactor") == 2  # hspeed AND vspeed components


def test_friction_accumulation_is_scaled_by_room_speed_factor():
    body = _process_movement_body()
    friction_block = body[body.index("if (this._friction !== 0)"):]
    friction_block = friction_block[:friction_block.index("// Handle grid-based movement")]
    assert "const scaledFriction = this._friction * roomSpeedFactor;" in friction_block


def test_position_delta_still_uses_the_same_factor_variable():
    body = _process_movement_body()
    # The later position-application block must NOT redeclare its own
    # roomSpeedFactor (that was the pre-fix duplication) — it reuses the
    # one already computed at the top of the method.
    assert body.count("const roomSpeedFactor") == 1
    assert "this.x + this._hspeed * roomSpeedFactor" in body
    assert "this.y + this._vspeed * roomSpeedFactor" in body


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
