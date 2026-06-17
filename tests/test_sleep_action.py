"""Regression test for the Sleep action (GameMaker "Sleep" equivalent).

Sleep performs a blocking pygame.time.delay(ms) so the rest of an action list
runs only after the pause — the intended use is letting a sound play in full
before a following action (e.g. a room change) cuts it off. Sounds play on
independent mixer channels, so they continue through the delay.

These tests monkeypatch pygame.time.delay so nothing actually sleeps; they
assert the millisecond value passed through, the [0, SLEEP_MAX_MS] clamp,
variable/expression parsing, and that the action auto-registers in the dispatch
table.
"""

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor


class _Instance:
    def __init__(self):
        self.object_name = "obj_test"
        self.variables = {}


@pytest.fixture
def executor():
    return ActionExecutor()


@pytest.fixture
def captured_delays(monkeypatch):
    """Capture pygame.time.delay calls without actually sleeping."""
    import pygame
    calls = []
    monkeypatch.setattr(pygame.time, "delay", lambda ms: calls.append(ms))
    return calls


def test_sleep_registered(executor):
    assert "sleep" in executor.action_handlers


def test_sleep_passes_milliseconds(executor, captured_delays):
    executor.execute_sleep_action(_Instance(), {"milliseconds": 1000})
    assert captured_delays == [1000]


def test_sleep_default_is_1000(executor, captured_delays):
    executor.execute_sleep_action(_Instance(), {})
    assert captured_delays == [1000]


def test_sleep_zero_does_not_delay(executor, captured_delays):
    executor.execute_sleep_action(_Instance(), {"milliseconds": 0})
    assert captured_delays == []


def test_sleep_negative_does_not_delay(executor, captured_delays):
    executor.execute_sleep_action(_Instance(), {"milliseconds": -50})
    assert captured_delays == []


def test_sleep_clamped_to_max(executor, captured_delays):
    executor.execute_sleep_action(_Instance(), {"milliseconds": 999999})
    assert captured_delays == [executor.SLEEP_MAX_MS]


def test_sleep_accepts_alias_ms(executor, captured_delays):
    executor.execute_sleep_action(_Instance(), {"ms": 500})
    assert captured_delays == [500]


def test_sleep_invalid_value_defaults(executor, captured_delays):
    executor.execute_sleep_action(_Instance(), {"milliseconds": "not_a_number"})
    assert captured_delays == [1000]


def test_sleep_string_number_parsed(executor, captured_delays):
    executor.execute_sleep_action(_Instance(), {"milliseconds": "750"})
    assert captured_delays == [750]
