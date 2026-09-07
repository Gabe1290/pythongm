"""M7, docs/FULL_AUDIT_2026-09-07.md: plugins/audio_actions.py used a plain
print() for every log line, including ones with emoji, sitting OUTSIDE (or
only partially inside) each action's try/except -- on a cp1252 Windows
console (the default for any exported .exe run from cmd, or any run
without PYTHONUTF8 set) that raised UnicodeEncodeError and aborted the
action before it did anything, instead of playing the sound. It also did
`float(parameters.get("volume", default))` with no exception handling, so
a volume given as an expression string (e.g. a global variable name) or a
typo raised ValueError uncaught.

Fix: route all logging through core.logger (which has its own
cp1252-safe console handler, ConsoleSafeHandler, for exactly this class of
bug -- see the 2026-08-17 desktop-export session note in CLAUDE.md), and
add a guarded _safe_volume helper that tries the action executor's own
_parse_value (for expressions) and falls back to a default on anything
that still isn't a real, finite number.
"""
import ast
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

pygame = pytest.importorskip("pygame")

from events.plugin_loader import load_all_plugins
from runtime.action_executor import ActionExecutor

REPO_ROOT = Path(__file__).resolve().parent.parent


class _Inst:
    """Minimal instance stand-in: audio actions only read
    .action_executor (for _get_game_runner and _parse_value)."""
    def __init__(self, action_executor):
        self.action_executor = action_executor


def _executor():
    ex = ActionExecutor(game_runner=None)
    load_all_plugins(ex)
    return ex


def _dispatch(ex, action_name, instance, params):
    return ex.action_handlers[action_name](instance, params)


# ---------------------------------------------------------------------------
# Structural: no plain print() left in the module (the actual cp1252 crash
# can't be reproduced portably in a test -- see conftest's own console
# encoding notes -- so this pins the fix's mechanism instead).
# ---------------------------------------------------------------------------

def test_no_bare_print_calls_remain():
    source = (REPO_ROOT / "plugins" / "audio_actions.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "print"):
            pytest.fail(
                "plugins/audio_actions.py must not call print() directly -- "
                "route through core.logger (ConsoleSafeHandler) instead, "
                "line %d" % node.lineno)


def test_module_imports_core_logger():
    source = (REPO_ROOT / "plugins" / "audio_actions.py").read_text(encoding="utf-8")
    assert "from core.logger import get_logger" in source


# ---------------------------------------------------------------------------
# Behavioural: bad volume input must not crash the action
# ---------------------------------------------------------------------------

class TestSafeVolume:
    def test_normal_float_passes_through(self):
        ex = _executor()
        plugin_ex = ex.action_handlers["play_sound"].__self__
        assert plugin_ex._safe_volume(_Inst(ex), {"volume": 0.5}, 1.0) == 0.5

    def test_missing_volume_uses_default(self):
        ex = _executor()
        plugin_ex = ex.action_handlers["play_sound"].__self__
        assert plugin_ex._safe_volume(_Inst(ex), {}, 0.7) == 0.7

    def test_non_numeric_string_falls_back_to_default(self):
        ex = _executor()
        plugin_ex = ex.action_handlers["play_sound"].__self__
        assert plugin_ex._safe_volume(_Inst(ex), {"volume": "pwned"}, 1.0) == 1.0

    def test_expression_is_resolved_via_parse_value(self):
        """A volume given as a global-variable expression should resolve
        through the action executor's own value parser, not just fail."""
        class _FakeRunner:
            global_variables = {"vol": 0.3}

        ex = ActionExecutor(game_runner=_FakeRunner())
        load_all_plugins(ex)
        plugin_ex = ex.action_handlers["play_sound"].__self__
        result = plugin_ex._safe_volume(_Inst(ex), {"volume": "global.vol"}, 1.0)
        assert result == 0.3

    def test_out_of_range_is_clamped(self):
        ex = _executor()
        plugin_ex = ex.action_handlers["play_sound"].__self__
        assert plugin_ex._safe_volume(_Inst(ex), {"volume": 5.0}, 1.0) == 1.0
        assert plugin_ex._safe_volume(_Inst(ex), {"volume": -2.0}, 1.0) == 0.0


class TestActionsSurviveBadVolume:
    """The actions themselves must not raise given a garbage volume --
    this is the actual crash the finding describes."""

    def test_play_sound_with_bad_volume_does_not_raise(self):
        ex = _executor()
        inst = _Inst(ex)
        _dispatch(ex, "play_sound", inst, {"sound": "nope", "volume": "pwned"})

    def test_play_music_with_bad_volume_does_not_raise(self):
        ex = _executor()
        inst = _Inst(ex)
        _dispatch(ex, "play_music", inst, {"music": "nope", "volume": "pwned"})

    def test_set_volume_with_bad_volume_does_not_raise(self):
        ex = _executor()
        inst = _Inst(ex)
        _dispatch(ex, "set_volume", inst, {"volume": "pwned"})

    def test_play_sound_with_normal_volume_still_works(self):
        """Behaviour-preservation baseline: a well-formed action still
        resolves the volume unchanged."""
        ex = _executor()
        plugin_ex = ex.action_handlers["play_sound"].__self__
        inst = _Inst(ex)
        assert plugin_ex._safe_volume(inst, {"sound": "beep", "volume": 0.8}, 1.0) == 0.8
