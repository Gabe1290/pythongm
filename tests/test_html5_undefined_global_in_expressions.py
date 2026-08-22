"""A genuine JS-specific gotcha, found via the full end-to-end restart_game
scenario (tests/test_restart_game_preserves_globals.py covers the rest of
that fix): gmExpressionValue's `global` scope exposed game.globalVariables
directly, so a never-set global read as `undefined` in the expression.
Desktop's equivalent (_get_variable_value) already defaults a missing
global to a real 0 — Python arithmetic on 0 behaves normally. JavaScript
does not: `Math.max(undefined, 650)` is NaN, not 650, because ANY
arithmetic operation involving `undefined` produces NaN, unlike Python
where there's no untyped "undefined" to contaminate the expression.

This broke the high-water-mark score sync ("max(global.score_x, score)",
added to fix an unrelated bug the same session) on the very FIRST run of
any level after this session's removal of the hub's game_start-based
global pre-seeding (necessary for a different reason: game_start re-fires
on restart_game, so seeding via game_start would re-wipe the scores right
back to 0 on a game over — the exact bug this whole arc chases). Once
pre-seeding was removed, a global's very first read really is undefined,
and Math.max(undefined, score) silently produced NaN, which the
set_variable case's own `!isNaN(evaluated)` guard correctly refused to
store — leaving the OLD unevaluated expression STRING sitting in the
global forever, one layer removed from a plain wrong-number bug.

Fix: gmExpressionValue's `global` scope is a Proxy that returns 0 for a
key not yet present, matching desktop's default exactly, so any
expression referencing an unset global behaves identically whether it's
the very first read or the hundredth.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_gm_expression_value_global_scope_is_a_defaulting_proxy():
    m = re.search(r"function gmExpressionValue\(expr, inst, game\) \{(.*?)\n\}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "new Proxy(" in body
    assert "(prop in target ? target[prop] : 0)" in body


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
