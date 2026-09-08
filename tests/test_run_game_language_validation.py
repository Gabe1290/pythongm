"""L20, docs/FULL_AUDIT_2026-09-07.md: run_game.py swallows a wrong
language silently.

run_game.py accepted any second positional argument as the language
code with zero validation -- a typo (a mis-ordered flag landing in the
language slot, "fr_FR" instead of "fr") silently produced English
runtime translations (CAPTION_TRANSLATIONS/get_runtime_translation both
fall back to English for an unrecognized code, never raising) with no
warning anywhere, easy to miss in a Test Game run where the tester
isn't specifically checking every displayed string.

Fix: _validate_language checks the given code against
core.language_manager.LanguageManager's own known-code list and warns +
falls back to 'en' on a mismatch. That import is best-effort (wrapped
in try/except) since LanguageManager depends on PySide6, which this
standalone pygame process -- and every exported game built from it --
deliberately does not require; a genuinely PySide6-less environment
skips validation rather than crashing a shipped game over a diagnostic
nicety.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def test_known_language_code_passes_through_unchanged():
    from runtime.run_game import _validate_language
    assert _validate_language("fr") == "fr"
    assert _validate_language("de") == "de"
    assert _validate_language("ja") == "ja"


def test_english_is_always_accepted():
    from runtime.run_game import _validate_language
    assert _validate_language("en") == "en"


def test_typo_language_code_falls_back_to_english(monkeypatch):
    from runtime import run_game
    warnings = []
    monkeypatch.setattr(run_game.logger, "warning", lambda msg: warnings.append(msg))

    result = run_game._validate_language("fr_FR")

    assert result == "en"
    assert len(warnings) == 1
    assert "fr_FR" in warnings[0]


def test_a_misplaced_flag_in_the_language_slot_falls_back_to_english(monkeypatch):
    """The exact scenario the audit names: --net-host mis-ordered so it
    lands in the language argument slot instead of being parsed as a
    flag."""
    from runtime import run_game
    warnings = []
    monkeypatch.setattr(run_game.logger, "warning", lambda msg: warnings.append(msg))

    result = run_game._validate_language("--net-host")

    assert result == "en"
    assert len(warnings) == 1


def test_unrecognized_code_does_not_warn_when_language_manager_is_unavailable(monkeypatch):
    """A genuinely PySide6-less environment (an exported game may not
    bundle it) must fail open -- pass the language through rather than
    crash or silently swap it, since there's nothing to validate against."""
    from runtime import run_game
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "core.language_manager":
            raise ImportError("simulated: PySide6 not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    warnings = []
    monkeypatch.setattr(run_game.logger, "warning", lambda msg: warnings.append(msg))

    result = run_game._validate_language("fr_FR")

    assert result == "fr_FR"  # unchanged, not silently swapped to 'en'
    assert warnings == []  # nothing to warn about -- validation was skipped
