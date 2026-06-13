"""Regression tests for if_condition key_pressed and mouse_check (M30, M31).

M30: the editor stored arrow keys as 'Left Arrow' etc., which lowercased to
'left arrow' and never matched the runtime's 'left'/'right'/'up'/'down'
key names, so arrow conditions were permanently false.

M31: the mouse_check arm was a hard `return False` stub that ignored the saved
'check' value — every mouse condition was always false.
"""

import sys
import types

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor


class _Instance:
    def __init__(self, keys=None, x=0, y=0):
        self.keys_pressed = set(keys or [])
        self.x = x
        self.y = y
        self._cached_width = 32
        self._cached_height = 32


@pytest.fixture
def executor():
    return ActionExecutor(game_runner=None)


class TestKeyPressed:
    def test_arrow_canonical_matches(self, executor):
        inst = _Instance(keys={"left"})
        assert executor._evaluate_if_condition(
            inst, "key_pressed", {"key": "left"}) is True

    def test_legacy_left_arrow_heals(self, executor):
        inst = _Instance(keys={"left"})
        assert executor._evaluate_if_condition(
            inst, "key_pressed", {"key": "Left Arrow"}) is True

    def test_non_pressed_key_false(self, executor):
        inst = _Instance(keys={"right"})
        assert executor._evaluate_if_condition(
            inst, "key_pressed", {"key": "left"}) is False

    def test_letter_key(self, executor):
        inst = _Instance(keys={"a"})
        assert executor._evaluate_if_condition(
            inst, "key_pressed", {"key": "a"}) is True


class TestMouseCheck:
    def _fake_pygame(self, pressed=(0, 0, 0), pos=(0, 0)):
        mouse = types.SimpleNamespace(
            get_pressed=lambda num_buttons=3: pressed,
            get_pos=lambda: pos,
        )
        return types.SimpleNamespace(
            get_init=lambda: True,
            mouse=mouse,
        )

    def test_left_button(self, executor, monkeypatch):
        monkeypatch.setitem(sys.modules, "pygame", self._fake_pygame(pressed=(1, 0, 0)))
        inst = _Instance()
        assert executor._evaluate_if_condition(
            inst, "mouse_check", {"check": "Left button pressed"}) is True

    def test_right_button_not_pressed(self, executor, monkeypatch):
        monkeypatch.setitem(sys.modules, "pygame", self._fake_pygame(pressed=(1, 0, 0)))
        inst = _Instance()
        assert executor._evaluate_if_condition(
            inst, "mouse_check", {"check": "Right button pressed"}) is False

    def test_over_object_true(self, executor, monkeypatch):
        monkeypatch.setitem(sys.modules, "pygame", self._fake_pygame(pos=(10, 10)))
        inst = _Instance(x=0, y=0)  # bbox 0..32
        assert executor._evaluate_if_condition(
            inst, "mouse_check", {"check": "Over object"}) is True

    def test_over_object_false_outside(self, executor, monkeypatch):
        monkeypatch.setitem(sys.modules, "pygame", self._fake_pygame(pos=(100, 100)))
        inst = _Instance(x=0, y=0)
        assert executor._evaluate_if_condition(
            inst, "mouse_check", {"check": "Over object"}) is False
