"""Regression tests for exit_event nesting + if_condition double-run (M43).

M43: exit_event inside an if_condition then/else branch or a repeat block was
caught at the innermost execute_action_list and swallowed, so the outer event
kept running (and repeat ran all remaining iterations). Nested action lists now
run through the non-catching workhorse so _ExitEvent propagates to the single
top-level catch. While fixing this, if_condition's then/else were found to run
TWICE (once internally, once via the generic dispatch branch); the internal
run was removed.
"""

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor


class _Inst:
    def __init__(self):
        self.n = 0
        self.keys_pressed = {"space"}


def _executor():
    ex = ActionExecutor(game_runner=None)
    ex.action_handlers["bump"] = lambda inst, p: setattr(inst, "n", inst.n + 1)
    return ex


def _if_space(then=None, els=None):
    return {"action": "if_condition", "parameters": {
        "condition_type": "key_pressed", "key": "space",
        "then_actions": then or [], "else_actions": els or []}}


def _bump():
    return {"action": "bump", "parameters": {}}


def test_then_branch_runs_exactly_once():
    ex, inst = _executor(), _Inst()
    ex.execute_action_list(inst, [_if_space(then=[_bump()])])
    assert inst.n == 1  # was 2 (double-run)


def test_else_branch_runs_exactly_once():
    ex, inst = _executor(), _Inst()
    inst.keys_pressed = set()  # condition false -> else
    ex.execute_action_list(inst, [_if_space(then=[_bump()], els=[_bump()])])
    assert inst.n == 1


def test_exit_in_then_aborts_event():
    ex, inst = _executor(), _Inst()
    ex.execute_action_list(inst, [
        _if_space(then=[{"action": "exit_event", "parameters": {}}]),
        _bump(),
    ])
    assert inst.n == 0  # the trailing bump must not run


def test_exit_in_repeat_block_aborts_event():
    ex, inst = _executor(), _Inst()
    ex.execute_action_list(inst, [
        {"action": "repeat", "parameters": {"times": "5"}},
        {"action": "start_block"},
        _bump(),
        {"action": "exit_event", "parameters": {}},
        {"action": "end_block"},
        _bump(),  # after the block — must not run
    ])
    # First iteration bumps once then exits; remaining 4 iterations and the
    # trailing bump are aborted.
    assert inst.n == 1


def test_exit_in_nested_generic_conditional_propagates():
    """exit_event inside a test_* conditional's then_actions aborts the event."""
    ex, inst = _executor(), _Inst()
    # if_condition whose then-branch contains another if_condition that exits.
    ex.execute_action_list(inst, [
        _if_space(then=[_if_space(then=[{"action": "exit_event", "parameters": {}}])]),
        _bump(),
    ])
    assert inst.n == 0
