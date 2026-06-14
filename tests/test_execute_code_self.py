"""Regression test for execute_code's self/other bindings (audit M45).

The exec namespace bound 'sel' but not 'self', so the self.<attr> code the
object editor's parser preserves as execute_code raised NameError at runtime
(caught and logged — a silent no-op). 'self' is now bound (fixed earlier in
82f9b04); this also binds 'other' for collision-context code, matching the eval
expression path.
"""

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor


class _Inst:
    def __init__(self):
        self.coins = 0


def test_execute_code_self_attr_assignment():
    ex = ActionExecutor(game_runner=None)
    inst = _Inst()
    ex.execute_execute_code_action(inst, {"code": "self.coins = self.coins + 1"})
    assert inst.coins == 1


def test_execute_code_self_augmented_assignment():
    ex = ActionExecutor(game_runner=None)
    inst = _Inst()
    inst.coins = 5
    ex.execute_execute_code_action(inst, {"code": "self.coins += 3"})
    assert inst.coins == 8


def test_execute_code_other_in_collision_context():
    ex = ActionExecutor(game_runner=None)
    inst = _Inst()
    other = _Inst()
    ex._collision_other = other  # set during collision events
    ex.execute_execute_code_action(inst, {"code": "other.coins = 42"})
    assert other.coins == 42


def test_execute_code_other_none_outside_collision():
    ex = ActionExecutor(game_runner=None)
    inst = _Inst()
    # No collision context: referencing other.coins assignment would AttributeError
    # on None, which is caught/logged — but the binding must exist (no NameError).
    ex.execute_execute_code_action(inst, {"code": "self.coins = 1 if other is None else 2"})
    assert inst.coins == 1
