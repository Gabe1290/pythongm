"""Regression test for modal dialogs swallowing KEYUP (audit M54).

Modal dialogs run their own pygame event loop and dropped KEYUP events, so a
key released while a dialog was open stayed in instance.keys_pressed and the
held-key event kept firing after the dialog closed ("haunted" movement).
_release_held_key_silent now clears the released key from every instance.
"""

import pytest

pygame = pytest.importorskip("pygame")

from runtime.game_runner import GameRunner


class _Room:
    def __init__(self, instances):
        self.instances = instances


class _Inst:
    def __init__(self, keys):
        self.keys_pressed = set(keys)


def test_release_held_key_silent_clears_key():
    runner = GameRunner.__new__(GameRunner)
    a = _Inst({"right", "up"})
    b = _Inst({"right"})
    runner.current_room = _Room([a, b])

    runner._release_held_key_silent(pygame.K_RIGHT)

    assert "right" not in a.keys_pressed
    assert "up" in a.keys_pressed  # other keys untouched
    assert "right" not in b.keys_pressed


def test_release_held_key_silent_no_room():
    runner = GameRunner.__new__(GameRunner)
    runner.current_room = None
    # Must not raise when there's no current room.
    runner._release_held_key_silent(pygame.K_RIGHT)


def test_release_held_key_silent_unknown_key():
    runner = GameRunner.__new__(GameRunner)
    inst = _Inst({"right"})
    runner.current_room = _Room([inst])
    # An unmapped key name should be a no-op, not an error.
    runner._release_held_key_silent(-99999)
    assert "right" in inst.keys_pressed
