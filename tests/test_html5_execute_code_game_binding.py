"""HTML5 execute_code `game` binding — the second half of
DEFERRED_ITEMS_PLAN.md item 9 (Kivy's half shipped as
tests/test_kivy_execute_code_game_proxy.py; this is the "architecturally
closer to desktop" HTML5 half flagged as its own follow-up there).

Before this fix, execute_code's Python environment on HTML5 (a real
Pyodide exec(), unlike Kivy's literal-source inlining) bound `game` to a
bare `None` — any `game.*` reference raised AttributeError. Fixed by
building a fresh `_Game(score, lives, health)` snapshot each call from
values synced in from the live JS `game` object, and diffing any change
back out into the same JSON patch mechanism `self.x`/`self.y` already
use. Design choice matches the Kivy fix and desktop's own real
semantics: `game.lives = X` from execute_code is a PLAIN write — no
caption update, no no_more_lives/no_more_health crossing check. Those
only fire from the set_lives/set_health ACTIONS (executeAction's switch
cases), never from a bare attribute assignment on any of the three
targets now.

PY_BOOTSTRAP is real embedded Python source, so it can be exec()'d
directly and its run_code/run_draw functions called for real —
deterministic, no network, no JS engine — following the exact
established pattern tests/test_sound_queue_primitive.py's
`py_bootstrap_ns` fixture already uses for this same string. The JS-side
glue (_syncJson/runCode in the HTML5Engine class) can't be exec()'d the
same way, so that half is covered by source-structure assertions instead
(Node isn't a CI dependency — see test_draw_action_codegen.py's HTML5
section for the established pattern).

Additionally verified once, ad hoc, in a real headless Chromium +
Pyodide session during development (`playwright`, not a project
dependency) as the strongest possible proof for the harder-to-verify
half: game.score/lives/health round-tripped correctly through a real
browser's run_code call for both a mutating and a read-only
execute_code body, matching every assertion below.
"""
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _py_bootstrap_source():
    m = re.search(r"const PY_BOOTSTRAP = `(.*?)`;", ENGINE, re.S)
    assert m, "PY_BOOTSTRAP template literal not found in engine.js"
    # Simulate JS template-literal escape processing (\` -> a literal
    # backtick) so the extracted text matches what Pyodide actually
    # receives at runtime, not the raw .js source text.
    return m.group(1).replace("\\`", "`")


@pytest.fixture(scope="module")
def py_bootstrap_ns():
    ns = {}
    exec(compile(_py_bootstrap_source(), "PY_BOOTSTRAP", "exec"), ns)
    return ns


def _sync(**overrides):
    base = {"x": 0, "y": 0, "visible": True, "mouse_x": 0, "mouse_y": 0,
            "keys": [], "score": 0, "lives": 3, "health": 100}
    base.update(overrides)
    return json.dumps(base)


# ---------------------------------------------------------------------------
# Real execution of run_code/run_draw — deterministic, no network/JS engine.
# ---------------------------------------------------------------------------

def test_game_score_lives_health_round_trip(py_bootstrap_ns):
    run_code = py_bootstrap_ns["run_code"]
    code = "game.score += 50\ngame.lives -= 1\ngame.health = 75"
    patch = json.loads(run_code("t1", code, _sync(score=100, lives=3, health=100)))
    assert patch["score"] == 150
    assert patch["lives"] == 2
    assert patch["health"] == 75


def test_unchanged_game_fields_produce_no_patch_keys(py_bootstrap_ns):
    # Matches x/y/visible's existing diff behaviour exactly.
    run_code = py_bootstrap_ns["run_code"]
    patch = json.loads(run_code("t2", "pass", _sync(score=100, lives=3, health=100)))
    assert "score" not in patch
    assert "lives" not in patch
    assert "health" not in patch


def test_reading_game_score_without_writing_is_side_effect_free(py_bootstrap_ns):
    # A draw-event-style use: read game.score to display it, don't mutate it.
    run_code = py_bootstrap_ns["run_code"]
    code = "self.last_seen_score = game.score"
    patch = json.loads(run_code("t3", code, _sync(score=42)))
    assert "score" not in patch


def test_game_is_a_fresh_object_not_shared_across_calls(py_bootstrap_ns):
    # Each call passes its own synced-in values; game must not silently
    # carry state from a previous instance's call.
    run_code = py_bootstrap_ns["run_code"]
    run_code("t4a", "game.score = 999", _sync(score=0))
    patch = json.loads(run_code("t4b", "pass", _sync(score=5)))
    assert "score" not in patch  # would be 999-vs-5 if game leaked across calls


def test_run_draw_does_not_propagate_game_field_changes(py_bootstrap_ns):
    # Matches run_draw's existing behaviour for x/y/visible (a draw event
    # doesn't move the instance either) — score/lives/health changes from
    # a draw-event execute_code body are legitimately discarded.
    run_draw = py_bootstrap_ns["run_draw"]
    code = "game.score = 500"
    result = json.loads(run_draw("t5", code, _sync(score=0)))
    assert "score" not in result
    assert set(result.keys()) <= {"draws", "sounds"}


def test_no_crossing_detection_side_effects_from_a_raw_write(py_bootstrap_ns):
    # The core design decision under test: game.lives crossing to <= 0
    # from execute_code must NOT fire anything — there is no
    # no_more_lives dispatch mechanism reachable from Python at all (that
    # only exists in engine.js's executeAction/set_lives case). This just
    # confirms the call doesn't raise and the patch is exactly the
    # expected shape, with nothing extra smuggled in.
    run_code = py_bootstrap_ns["run_code"]
    patch = json.loads(run_code("t6", "game.lives = 0", _sync(lives=3)))
    assert patch == {"lives": 0}


# ---------------------------------------------------------------------------
# Structural checks on PY_BOOTSTRAP source (belt-and-braces alongside the
# real-execution tests above; also doubles as documentation of the shape).
# ---------------------------------------------------------------------------

def test_game_class_defined_with_score_lives_health():
    src = _py_bootstrap_source()
    assert "class _Game:" in src
    assert "def __init__(self, score, lives, health):" in src


def test_game_bound_in_exec_globals_not_none():
    src = _py_bootstrap_source()
    # The old bug: 'game': None with no _Game construction at all.
    assert "'game': None" not in src
    assert "'game': game" in src


def test_no_crossing_detection_logic_in_game_class():
    # Checks for the actual crossing-detection CODE pattern (an "old"
    # snapshot compared against the new value, as set_lives/set_health
    # use), not the bare words — the class's own docstring legitimately
    # explains this design choice in prose, which a plain substring check
    # would also (wrongly) flag.
    src = _py_bootstrap_source()
    start = src.index("class _Game:")
    end = src.index("def run_code")
    game_class_body = src[start:end][src[start:end].index('"""', 3) + 3:]
    assert "old_lives" not in game_class_body
    assert "old_health" not in game_class_body
    assert ".events.no_more_lives" not in game_class_body
    assert ".events.no_more_health" not in game_class_body


class TestSyncJsonIncludesGameFields:
    def test_sync_json_reads_score_lives_health_from_live_game(self):
        m = re.search(r"_syncJson\(inst, game\) \{(.*?)\n    \}", ENGINE, re.S)
        assert m, "_syncJson method not found"
        body = m.group(1)
        assert "score: game.score, lives: game.lives, health: game.health" in body


class TestRunCodeAppliesPatchBack:
    def _run_code_method_body(self):
        m = re.search(r"runCode\(inst, code, game\) \{(.*?)\n    \}", ENGINE, re.S)
        assert m, "runCode method not found"
        return m.group(1)

    def test_applies_score_lives_health_from_patch(self):
        body = self._run_code_method_body()
        assert "if ('score' in patch) game.score = patch.score;" in body
        assert "if ('lives' in patch) game.lives = patch.lives;" in body
        assert "if ('health' in patch) game.health = patch.health;" in body

    def test_does_not_call_crossing_detection_helpers(self):
        # Checks for the actual JS crossing-detection code pattern
        # (oldLives/oldHealth, as set_lives/set_health use), not the bare
        # words — this method's own explanatory comment legitimately
        # mentions them in prose.
        body = self._run_code_method_body()
        assert "oldLives" not in body
        assert "oldHealth" not in body
        assert "events.no_more_lives" not in body
        assert "events.no_more_health" not in body
