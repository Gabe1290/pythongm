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


def test_numpad_and_punctuation_now_dispatchable():
    # RETARGETED to our HEAD design: L25 extended runtime/_keymap (via
    # _extended_keys) to actually DISPATCH numpad / punctuation / lock keys, so
    # these names ARE now in RUNTIME_SUPPORTED_KEY_NAMES (they fire at runtime).
    # The remote variant of this test asserted the opposite (never dispatchable);
    # our authoritative implementation makes them dispatchable instead.
    for name in ("numpad_0", "numpad_9", "numpad_plus", "numpad_period",
                 "semicolon", "comma", "period", "slash", "quote",
                 "pause", "capslock", "numlock", "scrolllock", "print"):
        assert name in GM_VK_TO_KEY_NAME.values()
        assert name in RUNTIME_SUPPORTED_KEY_NAMES


def test_pseudo_keys_are_dispatchable(caplog):
    # RETARGETED (2026-07-16, treasure/maze_4 re-validation): the runtime DOES
    # dispatch both pseudo-keys — keyboard.nokey fires each frame while the
    # instance has no key pressed (GameInstance.step) and anykey fires for any
    # key (_process_held_keys / handle_keyboard_press / handle_keyboard_release;
    # maze_3's controller_start relies on it). Warning "will never fire" for
    # them was a false positive that fired on every treasure/maze_4 import.
    from importers.gmk_mappings import RUNTIME_PSEUDO_KEY_NAMES
    assert RUNTIME_PSEUDO_KEY_NAMES == {"nokey", "anykey"}
    for name in ("nokey", "anykey"):
        assert name in GM_VK_TO_KEY_NAME.values()
        assert name in RUNTIME_SUPPORTED_KEY_NAMES
    # and resolving keyboard events bound to them stays quiet (VK 0 / VK 1)
    with caplog.at_level(logging.WARNING):
        assert resolve_event(5, 0, [])[1] == "nokey"
        assert resolve_event(5, 1, [])[1] == "anykey"
    assert not [r for r in caplog.records if "never fire" in r.getMessage()]


def test_resolve_event_warns_for_undispatchable_keyboard_key(caplog):
    # RETARGETED: under our HEAD numpad_0 is dispatchable (L25 extended the
    # runtime keymap), so it no longer warns. The genuinely-undispatchable case
    # is an unknown VK, which resolves to a "key_<n>" name the runtime can't
    # produce. VK 8000 is outside GM_VK_TO_KEY_NAME; held keyboard event (5).
    with caplog.at_level(logging.WARNING):
        event_key, sub_key, _ = resolve_event(5, 8000, [])
    assert event_key == "keyboard"
    assert sub_key == "key_8000"
    assert any("never fire" in r.getMessage() for r in caplog.records)


def test_resolve_event_warns_for_press_and_release(caplog):
    # RETARGETED: comma (VK 188) is now dispatchable; use an unknown VK (8000)
    # which stays undispatchable. press (9) and release (10).
    with caplog.at_level(logging.WARNING):
        resolve_event(9, 8000, [])
        resolve_event(10, 8000, [])
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
    # The pseudo-keys (nokey/anykey) are dispatched via dedicated runtime paths,
    # not the keymap, so the exact-sync invariant covers the PHYSICAL subset.
    from importers.gmk_mappings import RUNTIME_PSEUDO_KEY_NAMES
    physical = RUNTIME_SUPPORTED_KEY_NAMES - RUNTIME_PSEUDO_KEY_NAMES
    assert produced == physical, (
        "importer's RUNTIME_SUPPORTED_KEY_NAMES (physical subset) is out of "
        "sync with runtime/_keymap.pygame_key_name.\n"
        f"  only in importer set: {sorted(physical - produced)}\n"
        f"  only produced by runtime: {sorted(produced - physical)}"
    )
