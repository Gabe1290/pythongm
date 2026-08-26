"""HTML5 export — instances gained real xstart/ystart properties, matching
GameMaker's (and the desktop runtime's, runtime/game_runner.py's
GameInstance.xstart/ystart) canonical names for an instance's spawn
position.

Found while adding a "stop where the crosshair was" behavior to the promo
game's Sky Strike bombs: the fix used engine.js's existing internal
_startX/_startY (set by spawnInstance/buildRoom, previously read only by
the jump_to_start action), authored as `self._startY` in an if_condition
expression. That's an HTML5-only naming convention — the desktop runtime's
equivalent attribute is `ystart`, no underscore — so the exact same
authored expression silently always evaluated to False on desktop
(_eval_bool_expression catches the AttributeError and returns False), and
the bomb only ever stopped via its collision-with-target handler, never at
its intended drop point. Confirmed directly against the real
ActionExecutor._eval_bool_expression (tests/test_action_executor.py's own
MockInstance already has xstart/ystart, not _startX/_startY, for exactly
this reason): `self.y <= self._startY - 109` raises AttributeError and
returns False on every call; `self.y <= self.ystart - 109` works
correctly.

xstart/ystart are added ALONGSIDE the existing _startX/_startY (not a
replacement — jump_to_start and anything else already reading the
underscored names is unaffected), so any future authored expression
referencing self.xstart/self.ystart (or the bare names, gmExpressionValue
exposes both since neither starts with an underscore) now resolves
identically on both export targets.

Verification tier, per this repo's "no Node in CI" convention: source-
level assertions on engine.js. The desktop half was verified directly
against the real ActionExecutor (not HTML5-specific, so no Node/browser
needed for that proof); the HTML5 half via a real headless-Chromium run
(Playwright, not a CI dependency) against the actual exported promo game.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_spawn_instance_sets_xstart_ystart():
    m = re.search(r"spawnInstance\(objName, x, y\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    assert m, "spawnInstance not found"
    body = m.group(1)
    assert "inst.xstart = x;" in body
    assert "inst.ystart = y;" in body
    # Alongside, not instead of, the pre-existing internal names.
    assert "inst._startX = x;" in body
    assert "inst._startY = y;" in body


def test_build_room_sets_xstart_ystart():
    m = re.search(r"buildRoom\(roomName\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    assert m, "buildRoom not found"
    body = m.group(1)
    assert "inst.xstart = instData.x;" in body
    assert "inst.ystart = instData.y;" in body
    assert "inst._startX = instData.x;" in body
    assert "inst._startY = instData.y;" in body


def test_desktop_eval_bool_expression_resolves_ystart_but_not_underscored_startY():
    """The actual cross-target proof, run against the REAL desktop
    ActionExecutor (no Node/browser needed for this half)."""
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    from conftest import import_module_directly
    ae_module = import_module_directly("runtime/action_executor.py")
    ActionExecutor = ae_module.ActionExecutor

    class _Room:
        width = 480
        height = 480

    class _Runner:
        def __init__(self):
            self.score = 0
            self.lives = 3
            self.health = 100.0
            self.global_variables = {}
            self.current_room = _Room()

    class _Inst:
        def __init__(self, y, ystart):
            self.object_name = "sk_obj_bomb"
            self.x = 100.0
            self.y = y
            self.xstart = 100.0
            self.ystart = ystart
            self.hspeed = 0.0
            self.vspeed = -4.0
            self.image_index = 0.0
            self.image_speed = 1.0

    ex = ActionExecutor(game_runner=_Runner())

    # ystart (the fix): correctly distinguishes before/after the target.
    before = _Inst(y=464, ystart=468)
    after = _Inst(y=356, ystart=468)
    assert ex._eval_bool_expression(before, "self.y <= self.ystart - 109") is False
    assert ex._eval_bool_expression(after, "self.y <= self.ystart - 109") is True

    # _startY (the bug): no such attribute on desktop instances at all --
    # always silently False, regardless of position.
    assert ex._eval_bool_expression(after, "self.y <= self._startY - 109") is False


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
