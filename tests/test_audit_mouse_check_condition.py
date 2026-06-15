"""
Regression test for audit M31.

The if_condition 'mouse_check' arm in ActionExecutor._evaluate_if_condition was
a `return False` stub, so every mouse condition a teacher built (Left/Right/
Middle button pressed, Over object) was silently always false. The editor saves
the chosen check under parameters['check']; the runtime now reads live mouse
state from pygame.

Pure-logic test: pygame is initialised headless (SDL dummy via conftest) and
mouse state is monkeypatched, so no real window is needed.
"""

import sys
import types
from pathlib import Path

import pygame
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.action_executor import ActionExecutor


@pytest.fixture(autouse=True)
def _pygame_init():
    pygame.init()
    yield


def _instance(x=100, y=100, sprite=True):
    inst = types.SimpleNamespace(x=x, y=y)
    if sprite:
        inst.sprite = types.SimpleNamespace(
            origin_x=0, origin_y=0,
            bbox_left=0, bbox_top=0, bbox_right=32, bbox_bottom=32,
        )
    else:
        inst.sprite = None
    return inst


def _check(parameters, monkeypatch, pressed=(0, 0, 0), pos=(0, 0)):
    monkeypatch.setattr(pygame.mouse, "get_pressed", lambda *a, **k: pressed)
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: pos)
    ex = ActionExecutor(game_runner=None)
    return ex._evaluate_if_condition(_instance(), "mouse_check", parameters)


def test_left_button(monkeypatch):
    assert _check({"check": "Left button pressed"}, monkeypatch, pressed=(1, 0, 0))
    assert not _check({"check": "Left button pressed"}, monkeypatch, pressed=(0, 0, 0))


def test_right_button(monkeypatch):
    assert _check({"check": "Right button pressed"}, monkeypatch, pressed=(0, 0, 1))
    assert not _check({"check": "Right button pressed"}, monkeypatch, pressed=(1, 0, 0))


def test_middle_button(monkeypatch):
    assert _check({"check": "Middle button pressed"}, monkeypatch, pressed=(0, 1, 0))


def test_over_object_inside_and_outside(monkeypatch):
    # instance at (100,100), bbox 0..32 -> world rect [100,132)
    assert _check({"check": "Over object"}, monkeypatch, pos=(110, 110))
    assert not _check({"check": "Over object"}, monkeypatch, pos=(200, 200))
    # half-open: the far edge (132) is outside
    assert not _check({"check": "Over object"}, monkeypatch, pos=(132, 110))


def test_over_object_without_sprite_is_false(monkeypatch):
    monkeypatch.setattr(pygame.mouse, "get_pressed", lambda *a, **k: (0, 0, 0))
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (100, 100))
    ex = ActionExecutor(game_runner=None)
    inst = _instance(sprite=False)
    assert ex._evaluate_if_condition(inst, "mouse_check", {"check": "Over object"}) is False


def test_unknown_check_is_false(monkeypatch):
    # "In region" has no params from the editor -> false, not a crash.
    assert not _check({"check": "In region"}, monkeypatch, pressed=(1, 1, 1))
