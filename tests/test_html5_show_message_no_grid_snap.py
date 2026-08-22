"""HTML5 export — show_message unconditionally snapped the calling instance
to the nearest 32px grid line (and zeroed hspeed/vspeed/speed) before
showing the alert, with no equivalent on desktop at all (_show_or_queue_
message, runtime/action_executor.py, has ZERO side effects beyond
displaying the dialog).

The comment at the deleted code said "prevents the player from drifting
off-grid during collision events" — a maze-sample-specific need, applied
globally to every show_message call on every exported game. Found via the
promo game's side-scroller: its intro show_message (fired from create,
before the player has moved at all) snapped y=400 to the nearest 32px
line (416), a full 16px teleport straight down — deep enough that the
player's feet (400+48=448, exactly flush with the ground's top edge)
ended up inside the ground, and the level then played out as "the player
just drops through the floor at level start" (no move_to_contact/gravity
bug involved — this fired before the player had fallen at all).

Verification tier: source-level assertion on engine.js (per this repo's
"no Node in CI" convention), plus a real headless-Chromium run against the
actual exported promo game (not a CI dependency) proving the player's
position is completely unchanged by the create event's show_message.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_show_message_no_longer_snaps_to_a_grid_or_stops_movement():
    m = re.search(r"case 'show_message':(.*?)break;", ENGINE, re.S)
    assert m, "show_message case not found"
    body = m.group(1)
    assert "msgGridSize" not in body
    assert "Math.round" not in body
    assert "this.hspeed = 0" not in body
    assert "this.vspeed = 0" not in body
    assert "alert(message)" in body


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
