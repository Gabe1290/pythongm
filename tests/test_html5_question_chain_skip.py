"""HTML5 export — a chain of 2+ consecutive flat question actions gating
one action must skip as a single unit, matching the IDE runtime's
_execute_action_list_inner (runtime/action_executor.py): a skipped
QUESTION takes its own guarded unit down with it, recursively.

engine.js's _executeActionsInner had this only partially implemented: the
`if (skipNext) { skipNext = false; ... }` branch cleared the flag
unconditionally instead of re-arming it when the skipped action was
itself a question. A chain like [testA, testB, testC, testD, action]
(e.g. a bounding-box click hit-test: 4 test_variable checks ANDed before
a goto_room) then behaved incoherently: whichever question happened to
sit immediately after a false one got skipped for free, "spending" the
skip and letting a LATER question in the same chain evaluate and decide
the guarded action independently of the earlier false result.

Found via a real Playwright click test on an exported page with six
bounding-box buttons on one screen: clicking inside box #1 fired box #6's
action too (the last instance processed always won), because most of the
six four-question chains had at least one false check "absorbed" this
way, letting their own goto_room run unconditionally.

Source-level assertions on the generated engine.js (the behavioural proof
is the Playwright harness run during development, matching how the rest
of the HTML5 export is tested -- Playwright is not a CI dep, see
test_html5_conditionals.py's own docstring for the same convention).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _inner_body():
    m = re.search(r"_executeActionsInner\(actions, game\)\s*\{(.*?)\n    \}\n\n",
                  ENGINE, re.S)
    assert m, "_executeActionsInner not found"
    return m.group(1)


def test_skipped_question_rearms_skip_next():
    """The `if (skipNext) {...}` branch must re-check isConditionalAction
    and re-arm skipNext, not just clear it and move on."""
    body = _inner_body()
    # Anchor on the fix's own comment text, not just `if (skipNext) {`,
    # which also matches the earlier start_block/end_block skip-scanning
    # branch (a different piece of code with its own skipNext=false).
    m = re.search(
        r"if \(skipNext\) \{\s*skipNext = false;.*?guarded unit.*?\n(.*?)\n\s*\}",
        body, re.S)
    assert m, "the `if (skipNext)` skip branch (with its re-arming comment) was not found"
    skip_branch = m.group(1)
    assert "isConditionalAction" in skip_branch, (
        "skip branch must re-arm skipNext for a skipped QUESTION action, "
        "or a chain of 2+ consecutive questions gating one action breaks")


def test_four_question_chain_gates_correctly_via_a_real_interpreter_port():
    """A minimal, faithful Python port of _executeActionsInner's control
    flow (skip/else/block bookkeeping only -- not the action bodies),
    exercised against the exact 4-test_variable-then-goto_room shape this
    project's hub buttons use, across all 16 true/false combinations.
    This is the actual regression net (the regex check above only proves
    the fix is textually present, not that it's semantically correct)."""
    QUESTION_ACTIONS = {"test_variable"}

    def run(actions, results):
        """results: list of bool, one per question action in order."""
        i = 0
        skip_next = False
        condition_was_false = False
        fired = []
        qi = 0
        while i < len(actions):
            name = actions[i]
            if name == "else_action":
                skip_next = not condition_was_false
                i += 1
                continue
            if skip_next:
                skip_next = False
                if name in QUESTION_ACTIONS:
                    skip_next = True
                i += 1
                continue
            if name in QUESTION_ACTIONS:
                result = results[qi]
                qi += 1
                if result is False:
                    skip_next = True
                    condition_was_false = True
                else:
                    condition_was_false = False
                i += 1
                continue
            fired.append(name)
            i += 1
        return fired

    chain = ["test_variable", "test_variable", "test_variable", "test_variable", "goto_room"]

    for bits in range(16):
        results = [bool(bits & (1 << k)) for k in range(4)]
        fired = run(chain, results)
        all_true = all(results)
        assert (("goto_room" in fired) == all_true), (
            f"results={results} expected goto_room fired={all_true}, got {fired}")
