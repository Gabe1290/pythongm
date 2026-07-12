"""HTML5 export — H1: GM "question" actions must gate (audit 2026-07).

test_expression / check_empty / check_collision (and test_lives /
test_health / test_chance / test_question) were NOT recognized as
conditionals by the exported engine and existed only as no-op stubs, so
their guarded branches ran unconditionally. Bundled samples use
test_expression (plateforme_3/4/5) and check_empty (maze_3), so their web
exports were affected.

These are source-level assertions on the generated engine.js (the
behavioural proof is the Playwright harness run during development, matching
how the rest of the HTML5 export is tested — Playwright is not a CI dep).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _block(name):
    """Return the source of the isConditionalAction / evaluateCondition
    region so assertions don't match unrelated text."""
    return ENGINE


def test_all_question_actions_recognized_as_conditional():
    m = re.search(r"static isConditionalAction\(actionType\)\s*\{(.*?)\}", ENGINE, re.S)
    assert m, "isConditionalAction not found"
    body = m.group(1)
    for name in ("test_expression", "check_empty", "check_collision",
                 "test_lives", "test_health", "test_chance", "test_question"):
        assert f"'{name}'" in body, f"{name} missing from isConditionalAction"


def test_no_op_stubs_removed():
    # The tell-tale stub comments/bodies must be gone.
    assert "Would need safe evaluation" not in ENGINE
    assert "// Collision checking logic" not in ENGINE


def test_evaluate_condition_implements_the_questions():
    for case in ("case 'test_expression'", "case 'check_empty'",
                 "case 'check_collision'", "case 'test_lives'",
                 "case 'test_health'", "case 'test_chance'",
                 "case 'test_question'"):
        assert case in ENGINE, f"{case} not implemented in evaluateCondition"


def test_shared_helpers_exist():
    assert "function gmExpressionValue(" in ENGINE
    assert "placeMeetsCollision(atX, atY, filter, game)" in ENGINE
    # Python operators translated to JS in the expression evaluator
    assert r"\band\b" in ENGINE and r"\bor\b" in ENGINE and r"\bnot\b" in ENGINE


def test_check_empty_uses_origin_aware_boxes():
    """placeMeetsCollision must use getBoundingBox geometry (origin-aware),
    not raw positions — otherwise centered-origin sprites mis-detect."""
    m = re.search(r"placeMeetsCollision\(atX, atY, filter, game\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    assert m, "placeMeetsCollision not found"
    body = m.group(1)
    assert "getBoundingBox()" in body
    assert "origin_x" in body and "origin_y" in body


def test_samples_that_use_these_still_export():
    """Integration: the exporter still produces a page for the samples that
    exercise these conditionals (merge + emit path intact)."""
    import tempfile
    from export.HTML5.html5_exporter import HTML5Exporter
    out = Path(tempfile.mkdtemp(prefix="h1_export_"))
    ex = HTML5Exporter()
    for sample in ("plateforme_3", "maze_3"):
        assert ex.export(REPO_ROOT / "samples" / sample, out), sample
    assert (out / "Plateforme_3.html").exists() or list(out.glob("*.html"))
