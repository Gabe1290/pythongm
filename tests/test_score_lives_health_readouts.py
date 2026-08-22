"""Cross-engine support for reading score/lives/health as bare tokens (in
set_variable's value) and a global variable's value in draw_text — added
for the promo game's hub screen, which shows each level's last score plus
a cross-level total.

Before this fix, neither engine had any way to copy the running score into
a named global variable, or to display a global's value as text:

- Desktop's ActionExecutor._parse_value resolved dotted references
  (self.x, other.hspeed, global.my_var) and bare instance attributes, but
  had no notion of the game-state readouts (score/lives/health) that
  _eval_bool_expression's namespace already exposes for CONDITIONS. A
  set_variable action with value="score" fell through every branch and
  returned the literal string "score" — so `global_variables['score_maze']
  = "score"` (text, not a number).

- HTML5's set_variable case never evaluated its value at all beyond a
  literal-number check; "score" was stored as the raw string "score".
  draw_text was even more literal — `String(params.text)` with zero
  resolution — so a text param of "global.score_maze" rendered the
  literal characters "global.score_maze" on screen instead of its value.

Fix: desktop's _parse_value now resolves bare "score"/"lives"/"health" via
game_runner (mirroring _eval_bool_expression's existing namespace).
engine.js's set_variable case gained the same three-name special case, and
draw_text now resolves an exact "global.<name>" reference, plus a
"+"-joined sum of such references (needed for the hub's total across all
6 levels) — deliberately narrower than desktop's full expression support,
to avoid changing any existing sample's literal on-screen text.

Verification tier: desktop via direct ActionExecutor calls (no GUI
needed); HTML5 via source-level assertions on engine.js, per this repo's
"no Node in CI" convention.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Desktop
# ---------------------------------------------------------------------------

class _FakeGameRunner:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.health = 100
        self.global_variables = {}


class _FakeInstance:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.object_name = "test"


def _executor():
    from runtime.action_executor import ActionExecutor
    gr = _FakeGameRunner()
    ex = ActionExecutor(game_runner=gr)
    return ex, gr, _FakeInstance()


def test_desktop_parse_value_resolves_bare_score_lives_health():
    ex, gr, inst = _executor()
    gr.score, gr.lives, gr.health = 40, 2, 65
    assert ex._parse_value("score", inst) == 40
    assert ex._parse_value("lives", inst) == 2
    assert ex._parse_value("health", inst) == 65


def test_desktop_set_variable_copies_score_into_a_global():
    ex, gr, inst = _executor()
    gr.score = 40
    ex.execute_set_variable_action(
        inst, {"variable": "score_maze", "value": "score", "scope": "global", "relative": False}
    )
    assert gr.global_variables["score_maze"] == 40


def test_desktop_draw_text_resolves_a_bare_global_and_a_sum_of_globals():
    ex, gr, inst = _executor()
    gr.global_variables = {"score_maze": 10, "score_plateforme": 5}

    ex.execute_draw_text_action(inst, {"text": "global.score_maze", "x": 0, "y": 0})
    assert inst._draw_queue[-1]["text"] == "10"

    ex.execute_draw_text_action(
        inst, {"text": "global.score_maze + global.score_plateforme", "x": 0, "y": 0}
    )
    assert inst._draw_queue[-1]["text"] == "15"


def test_desktop_sum_expression_defaults_missing_globals_to_zero():
    ex, gr, inst = _executor()
    gr.global_variables = {}
    total_expr = "global.score_maze + global.score_plateforme"
    assert ex._parse_value(total_expr, inst) == 0


# ---------------------------------------------------------------------------
# HTML5 (engine.js source-level, per this repo's no-Node-in-CI convention)
# ---------------------------------------------------------------------------

def test_html5_set_variable_resolves_bare_score_lives_health():
    m = re.search(r"case 'set_variable': \{(.*?)\n            \}", ENGINE, re.S)
    assert m, "set_variable case not found"
    body = m.group(1)
    assert "value === 'score' || value === 'lives' || value === 'health'" in body
    assert "value = game[value];" in body


def test_html5_draw_text_resolves_bare_global_reference():
    m = re.search(r"case 'draw_text': \{(.*?)\n            \}", ENGINE, re.S)
    assert m, "draw_text case not found"
    body = m.group(1)
    assert r"^global\.(\w+)$" in body
    assert "game.globalVariables[gmatch[1]]" in body


def test_html5_draw_text_resolves_sum_of_globals():
    m = re.search(r"case 'draw_text': \{(.*?)\n            \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "global\\.\\w+(\\s*\\+\\s*global\\.\\w+)+" in body
    assert "trimmed.split('+')" in body


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
