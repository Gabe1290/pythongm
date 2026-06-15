#!/usr/bin/env python3
"""Regression tests for L25 (2026-06-11 full audit).

GMK keyboard events for numpad / punctuation / lock keys map to pygm2 key
names the runtime keymap (runtime/_keymap.pygame_key_name) never produces, so
those imported events could never fire at runtime AND the import gave no
diagnostic. resolve_event() now warns when a keyboard binding resolves to a
key name outside the runtime-dispatchable set.

These tests pin two invariants:
  1. RUNTIME_SUPPORTED_KEY_NAMES exactly matches what runtime/_keymap produces
     (so the importer's notion of "dispatchable" stays in sync with the engine).
  2. resolve_event warns for keyboard events bound to undispatchable keys and
     stays quiet for dispatchable ones.

Pure logic; no Qt. runtime/_keymap imports pygame defensively, so the
cross-check is skipped if pygame is unavailable.
"""

import logging

import pytest

from importers.gmk_mappings import (
    GM_VK_TO_KEY_NAME,
    RUNTIME_SUPPORTED_KEY_NAMES,
    resolve_event,
)


def test_supported_set_contains_expected_basics():
    for name in ("left", "right", "up", "down", "a", "z", "0", "9",
                 "space", "enter", "escape", "f1", "f12", "shift"):
        assert name in RUNTIME_SUPPORTED_KEY_NAMES


def test_numpad_and_punctuation_not_in_supported_set():
    # These are the names that silently never fired before the fix.
    for name in ("numpad_0", "numpad_9", "numpad_plus", "numpad_period",
                 "semicolon", "comma", "period", "slash", "quote",
                 "pause", "capslock", "numlock", "scrolllock", "print"):
        assert name in GM_VK_TO_KEY_NAME.values()
        assert name not in RUNTIME_SUPPORTED_KEY_NAMES


def test_resolve_event_warns_for_undispatchable_keyboard_key(caplog):
    # VK 96 = numpad_0; held keyboard event (type 5).
    with caplog.at_level(logging.WARNING):
        event_key, sub_key, _ = resolve_event(5, 96, [])
    assert event_key == "keyboard"
    assert sub_key == "numpad_0"
    assert any("never fire" in r.getMessage() for r in caplog.records)


def test_resolve_event_warns_for_press_and_release(caplog):
    # VK 188 = comma; press (9) and release (10).
    with caplog.at_level(logging.WARNING):
        resolve_event(9, 188, [])
        resolve_event(10, 188, [])
    warnings = [r.getMessage() for r in caplog.records if "never fire" in r.getMessage()]
    assert len(warnings) == 2
    assert any("keyboard_press" in w for w in warnings)
    assert any("keyboard_release" in w for w in warnings)


def test_resolve_event_silent_for_dispatchable_key(caplog):
    # VK 37 = left arrow, fully supported by the runtime.
    with caplog.at_level(logging.WARNING):
        event_key, sub_key, _ = resolve_event(5, 37, [])
    assert (event_key, sub_key) == ("keyboard", "left")
    assert not [r for r in caplog.records if "never fire" in r.getMessage()]


def test_resolve_event_silent_for_letter_and_digit(caplog):
    with caplog.at_level(logging.WARNING):
        resolve_event(9, ord("A"), [])   # 'a'
        resolve_event(9, 48, [])         # '0'
    assert not [r for r in caplog.records if "never fire" in r.getMessage()]


def test_supported_set_matches_runtime_keymap_exactly():
    """The importer's supported set must equal what runtime/_keymap can emit.

    Probe the live runtime keymap over the full pygame keycode range and
    collect every name it produces, then compare to RUNTIME_SUPPORTED_KEY_NAMES.
    Guards against the two drifting apart in future edits to either file.
    """
    pygame = pytest.importorskip("pygame")
    from runtime._keymap import pygame_key_name

    produced = set()
    # SDL2 scatters keycodes across a wide range (arrows/F-keys/modifiers sit
    # above 0x40000000), so probe every public pygame.K_* constant rather than
    # a numeric span.
    for attr in dir(pygame):
        if not attr.startswith("K_"):
            continue
        code = getattr(pygame, attr)
        if not isinstance(code, int):
            continue
        name = pygame_key_name(code)
        if name is not None:
            produced.add(name)

    assert produced, "runtime keymap produced no names; probe range wrong?"
    assert produced == RUNTIME_SUPPORTED_KEY_NAMES, (
        "importer's RUNTIME_SUPPORTED_KEY_NAMES is out of sync with "
        "runtime/_keymap.pygame_key_name.\n"
        f"  only in importer set: {sorted(RUNTIME_SUPPORTED_KEY_NAMES - produced)}\n"
        f"  only produced by runtime: {sorted(produced - RUNTIME_SUPPORTED_KEY_NAMES)}"
    )
