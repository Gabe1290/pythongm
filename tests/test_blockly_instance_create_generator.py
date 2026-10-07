"""Regression test: the "Create instance of X at x: ... y: ..." Blockly
block (type `instance_create`) silently produced no action at all.

`generatePyGameMakerCode`'s switch in blockly_generators.js had no `case
'instance_create':` branch, so any such block fell through to `default:
return null` and was dropped from the compiled action list entirely --
e.g. Tutorial 2's (Catch the Star) star-spawner alarm event re-armed
itself every frame but never actually created a star, reported live by a
user following the French tutorial, whose Blockly workspace matched this
exact shape (alarm -> "Create obj_star at x: <random integer from 1 to
600> y: 0" -> re-arm alarm).

A second, related gap: `getInputValue` only recognized a short hardcoded
whitelist of nested block types for a Number-type value socket
(math_number, text, and this project's own value_x/value_y/value_score/
value_lives/value_health placeholders) -- not Blockly's own standard
"random integer from %1 to %2" block (`math_random_int`, a core Blockly
Math-category block, not something this project defines), which is
exactly what the tutorial has the student drag into the X socket. Any
other nested value socket in the toolbox is equally exposed to this gap,
but this test scopes itself to the reported, reproduced case.

No Node.js in this environment (consistent with this repo's established
"no JS engine in CI" tier for blockly_i18n.js/engine.js edits), so this
asserts on the generator's source structure rather than executing it.
The fix was additionally verified by REAL execution during development,
using the `quickjs` Python package installed ad hoc for that one-time
check (same precedent as the HTML5 execute_code Playwright spike) --
not a project dependency, not committed, and not relied on here.
"""
import re
from pathlib import Path

GEN_JS = (
    Path(__file__).resolve().parent.parent
    / "editors" / "object_editor" / "blockly" / "blockly_generators.js"
)


def _js_source():
    return GEN_JS.read_text(encoding="utf-8")


def test_braces_balance():
    content = _js_source()
    depth = 0
    for ch in content:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        assert depth >= 0, "unbalanced closing brace in blockly_generators.js"
    assert depth == 0


def test_instance_create_has_a_switch_case():
    content = _js_source()
    assert "case 'instance_create':" in content, (
        "instance_create has no generator case -- every 'Create instance of "
        "X at x/y' block in the toolbox silently produces no action"
    )


def test_instance_create_case_emits_create_instance_action():
    content = _js_source()
    m = re.search(
        r"case 'instance_create':(.*?)case '",
        content, re.S,
    )
    assert m, "could not locate the instance_create case body"
    body = m.group(1)
    assert "'create_instance'" in body or '"create_instance"' in body, (
        "instance_create must emit the runtime's create_instance action "
        f"(the action BLOCKLY_TO_ACTION_MAP maps it to); body was: {body!r}"
    )
    assert "getFieldValue('OBJECT')" in body
    assert "getInputValue(block, 'X'" in body
    assert "getInputValue(block, 'Y'" in body


def test_get_input_value_resolves_math_random_int():
    content = _js_source()
    m = re.search(r"function getInputValue\(.*?\n\}", content, re.S)
    assert m, "could not locate getInputValue"
    body = m.group(0)
    assert "math_random_int" in body, (
        "getInputValue doesn't special-case Blockly's standard "
        "math_random_int block -- nesting it (as the tutorial instructs) "
        "into any Number-type socket silently falls back to the default "
        "value instead of a real random expression"
    )
    assert "'FROM'" in body and "'TO'" in body, (
        "must read math_random_int's own FROM/TO value inputs, not a "
        "field value -- both are themselves nested Number-type blocks"
    )
    # The runtime's expression evaluator (runtime/action_executor.py
    # _evaluate_expression, mirrored in HTML5's engine.js and Kivy's
    # kivy_exporter.py) only implements single-argument irandom(n) (0..n
    # inclusive) on all three export targets, not a two-argument range
    # function -- so this must synthesize the range from irandom(), not
    # emit an unsupported irandom_range(a, b) call.
    assert "irandom(" in body
    assert "irandom_range(" not in body, (
        "no target engine implements a two-argument irandom_range() call -- "
        "the range must be synthesized as irandom(to - from) + from"
    )


def test_resolved_random_expression_is_accepted_by_the_runtime_evaluator():
    """The exact expression shape getInputValue now produces for
    math_random_int(1, 600) must actually evaluate on the desktop runtime,
    land in range, and do so consistently (not just parse without error)."""
    import sys
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))
    from runtime.action_executor import ActionExecutor

    ex = ActionExecutor.__new__(ActionExecutor)
    ex.game_runner = None
    ex._collision_speeds = {}

    expr = "irandom((600) - (1)) + (1)"
    seen = set()
    for _ in range(500):
        val = ex._evaluate_expression(expr, instance=None)
        assert isinstance(val, int), (val, type(val))
        assert 1 <= val <= 600, f"out of range: {val}"
        seen.add(val)
    # Should see real variety, not a single constant (e.g. a silent
    # fallback to 0 that happened to pass the range check by accident).
    assert len(seen) > 50, f"suspiciously low variety: {len(seen)} distinct values"
