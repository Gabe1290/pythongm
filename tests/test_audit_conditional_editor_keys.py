#!/usr/bin/env python3
"""Regression tests for audit finding M30 (events/conditional_editor.py).

M30: the if_condition key_pressed combo stored display labels like
"Left Arrow" as the canonical (saved) value, which lower-cases to
"left arrow" and can never match the runtime's keys_pressed names
("left"/"right"/"up"/"down"/"enter"/...), leaving arrow-key conditions
permanently false. The combo must now store the lowercase pygame key
name, and legacy "Left Arrow"-style saved values must heal on load.

Built against a real offscreen QApplication (no pytest-qt) so it runs on
Python 3.11 too.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from PySide6.QtWidgets import QApplication

from events.conditional_editor import (
    ConditionalActionEditor,
    _normalize_legacy_key,
)


def _app():
    return QApplication.instance() or QApplication([])


def test_key_combo_stores_runtime_key_names():
    """Every key choice's saved userData must be a lowercase runtime key name."""
    _app()
    dlg = ConditionalActionEditor({})
    combo = dlg.key_check

    stored = {combo.itemData(i) for i in range(combo.count())}

    # The four arrow keys are the heart of M30: they must be the bare
    # runtime names, not "Left Arrow" etc.
    for name in ("left", "right", "up", "down"):
        assert name in stored, f"arrow key {name!r} missing from saved values"

    # None of the old display-label spellings may survive as a stored value.
    for bad in ("Left Arrow", "Right Arrow", "Up Arrow", "Down Arrow"):
        assert bad not in stored, f"legacy label {bad!r} still stored as value"

    # Every stored value must round-trip through .lower() to itself (i.e. it is
    # already a runtime-comparable name) and contain no spaces (runtime names
    # are single tokens).
    for v in stored:
        assert v == v.lower(), f"stored key {v!r} is not lowercase"
        assert " " not in v, f"stored key {v!r} contains a space"


def test_selecting_arrow_saves_runtime_name():
    """Picking an arrow in the combo persists the matching runtime name."""
    _app()
    dlg = ConditionalActionEditor({})
    dlg.condition_type.setCurrentIndex(dlg.condition_type.findData("key_pressed"))

    # Find the "Right Arrow" item by its display text and select it.
    idx = -1
    for i in range(dlg.key_check.count()):
        if dlg.key_check.itemData(i) == "right":
            idx = i
            break
    assert idx >= 0
    dlg.key_check.setCurrentIndex(idx)

    params = dlg.get_parameter_values()
    assert params["condition_type"] == "key_pressed"
    # This is the exact string the runtime does `key.lower() in keys_pressed`
    # against; keys_pressed holds "right" for the right arrow.
    assert params["key"] == "right"
    assert params["key"].lower() == "right"


def test_legacy_arrow_value_heals_on_load_and_resave():
    """A project saved with the old 'Left Arrow' value re-saves as 'left'."""
    _app()
    legacy = {
        "condition_type": "key_pressed",
        "key": "Left Arrow",
        "state": "Pressed",
    }
    dlg = ConditionalActionEditor(legacy)
    # The combo should have landed on the canonical "left" item.
    assert dlg.key_check.currentData() == "left"
    # And re-saving yields the runtime name, not the legacy label.
    assert dlg.get_parameter_values()["key"] == "left"


def test_non_arrow_keys_unaffected():
    """Letters / Space / Enter already matched; they must keep working."""
    _app()
    dlg = ConditionalActionEditor({})
    by_value = {dlg.key_check.itemData(i): i for i in range(dlg.key_check.count())}
    # Enter must be stored as "enter" (runtime name for K_RETURN), Space as
    # "space", and the WASD letters as their lowercase chars.
    assert "enter" in by_value
    assert "space" in by_value
    for letter in ("a", "w", "s", "d"):
        assert letter in by_value


def test_normalize_legacy_key_helper():
    assert _normalize_legacy_key("Left Arrow") == "left"
    assert _normalize_legacy_key("DOWN ARROW") == "down"
    # Already-canonical and unknown values pass through untouched.
    assert _normalize_legacy_key("left") == "left"
    assert _normalize_legacy_key("space") == "space"
    assert _normalize_legacy_key("a") == "a"
