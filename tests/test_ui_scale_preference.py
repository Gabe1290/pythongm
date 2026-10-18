"""Regression tests for TODO.md's "Preferences' 'UI Scale' setting is
dead" (found 2026-10-16): the 0.5x-2.0x spinner in Preferences > Appearance
saved to config but nothing ever read it back and applied it.

Decision made: wire it up rather than remove it, reusing the exact
mechanism main.py already uses to apply font family/size globally
(app.setFont(...) at startup) -- scale the resolved base font point size
by ui_scale before handing it to QFont. This does not independently
rescale toolbar icons or hardcoded-pixel dialog layouts (an honest,
narrower scope than "proportionally app-wide"); only text-size-driven
layout benefits, matching the existing "some settings require restarting
the IDE" convention font family/size already followed (no live-apply
needed in Preferences' apply_settings(), since font changes never did
either).
"""
import ast
from pathlib import Path

import pytest

from utils.config import resolve_scaled_font_size

REPO_ROOT = Path(__file__).resolve().parent.parent
MAIN_PY = REPO_ROOT / "main.py"


class TestResolveScaledFontSize:
    def test_default_scale_is_a_no_op(self):
        assert resolve_scaled_font_size(10, 1.0) == 10

    @pytest.mark.parametrize("base,scale,expected", [
        (10, 1.5, 15),
        (12, 2.0, 24),
        (10, 0.5, 6),  # clamped: 10 * 0.5 = 5, floored to the 6pt minimum
        (16, 1.25, 20),
    ])
    def test_scales_and_rounds(self, base, scale, expected):
        assert resolve_scaled_font_size(base, scale) == expected

    def test_never_returns_below_the_minimum_floor(self):
        """An extreme-but-legal combination (8pt base, 0.5x -- both within
        the spinners' own real ranges) must never produce an unusably tiny
        global application font."""
        assert resolve_scaled_font_size(8, 0.5) >= 6

    def test_large_scale_is_honored_without_an_upper_clamp(self):
        assert resolve_scaled_font_size(24, 2.0) == 48


def test_main_py_startup_actually_calls_the_scaling_helper():
    """Mutation-resistant: parses main.py's AST rather than grepping for a
    string, so commenting out the real call (leaving the text sitting in a
    comment) would NOT satisfy this -- the lesson from CLAUDE.md's
    2026-08-17 "mutation-test string-presence assertions" note."""
    tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
    call_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "resolve_scaled_font_size" in call_names


def test_main_py_imports_the_helper_from_utils_config():
    tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "utils.config":
            imported_names.update(alias.name for alias in node.names)
    assert "resolve_scaled_font_size" in imported_names


def test_appearance_config_still_round_trips_ui_scale():
    """Saving/reading ui_scale through Config itself is untouched by this
    fix -- confirms the fix is purely about applying the already-saved
    value, not a storage-format change. Config.save() is mocked (matching
    tests/test_allow_multiple_instances_setting.py's established pattern)
    so this doesn't touch the real on-disk ~/.pygamemaker/config.json."""
    from unittest.mock import patch
    from utils.config import Config
    original = Config.get_appearance_config()
    try:
        with patch("utils.config.Config.save"):
            Config.set_appearance_config(ui_scale=1.5)
            assert Config.get_appearance_config()["ui_scale"] == 1.5
    finally:
        with patch("utils.config.Config.save"):
            Config.set_appearance_config(ui_scale=original["ui_scale"])
