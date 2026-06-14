"""Regression test for Blockly Thymio sub_actions dispatch (audit M44).

Blockly serialises a Thymio condition block's DO-slot children under a
"sub_actions" key, but the runtime only knew then_actions/else_actions, so the
nested children never ran and a false condition set skip_next, silently
skipping the unrelated next action. The generic conditional dispatch now honors
sub_actions.
"""

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor


class _Inst:
    def __init__(self):
        self.n = 0


def _executor(cond_result):
    ex = ActionExecutor(game_runner=None)
    ex.action_handlers["bump"] = lambda inst, p: setattr(inst, "n", inst.n + 1)
    ex.action_handlers["cond"] = lambda inst, p: cond_result
    return ex


def _bump():
    return {"action": "bump", "parameters": {}}


def test_sub_actions_run_when_true_top_level_key():
    ex, inst = _executor(True), _Inst()
    ex.execute_action_list(inst, [
        {"action": "cond", "parameters": {}, "sub_actions": [_bump()]},
    ])
    assert inst.n == 1


def test_sub_actions_run_when_true_in_parameters():
    ex, inst = _executor(True), _Inst()
    ex.execute_action_list(inst, [
        {"action": "cond", "parameters": {"sub_actions": [_bump()]}},
    ])
    assert inst.n == 1


def test_sub_actions_skipped_when_false_but_sibling_runs():
    ex, inst = _executor(False), _Inst()
    ex.execute_action_list(inst, [
        {"action": "cond", "parameters": {}, "sub_actions": [_bump()]},
        _bump(),  # unrelated sibling — must still run
    ])
    # nested bump skipped (cond false), sibling bump runs
    assert inst.n == 1


def test_then_actions_take_precedence_over_sub_actions():
    ex, inst = _executor(True), _Inst()
    ex.execute_action_list(inst, [
        {"action": "cond", "parameters": {"then_actions": [_bump()]},
         "sub_actions": [_bump(), _bump()]},
    ])
    assert inst.n == 1  # then_actions used, not the 2-item sub_actions
