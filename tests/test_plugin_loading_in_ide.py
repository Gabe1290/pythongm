"""Extensions/plugins load for the IDE too, not just the runtime (Stage A1).

Until 2026-07-22 load_all_plugins() was called in exactly ONE place —
GameRunner.__init__ — so plugin actions existed only inside a running game.
In the IDE, ACTION_TYPES had no play_sound, which silently contradicted the
Blockly toolbox's own comment that audio actions "auto-generate into a single
Audio category via registerCustomBlocks" (that path reads ACTION_TYPES, so it
produced nothing). Users could not add audio actions from the editor.

ensure_plugins_loaded() is now the single load point for both. See
docs/RAYCAST_EXTENSION_PLAN.md Stage A1 — this is the foundation for moving
optional features (starting with raycast) into extensions.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from events.action_types import ACTION_TYPES  # noqa: E402
from events.plugin_loader import ensure_plugins_loaded  # noqa: E402

# The audio plugin's actions. stop_sound is deliberately excluded: a STATIC
# ACTION_TYPES entry of that name already shadows the plugin's copy (the
# documented _load_actions landmine), so it proves nothing about plugin loading.
PLUGIN_ONLY_AUDIO = ["play_sound", "play_music", "stop_music", "set_volume"]


def test_plugin_actions_reach_action_types():
    """The schemas the IDE's action picker and Blockly read."""
    ensure_plugins_loaded()
    missing = [a for a in PLUGIN_ONLY_AUDIO if a not in ACTION_TYPES]
    assert not missing, f"plugin actions absent from ACTION_TYPES: {missing}"


def test_plugin_actions_carry_their_category():
    """Blockly groups auto-generated blocks by category — a plugin action with
    no category would land in the wrong toolbox group."""
    ensure_plugins_loaded()
    assert ACTION_TYPES["play_sound"].category == "Audio"


def test_is_idempotent():
    """Both the IDE and GameRunner call it; repeated calls must not duplicate
    actions or re-import plugin modules."""
    ensure_plugins_loaded()
    before = len(ACTION_TYPES)
    loader = ensure_plugins_loaded()
    again = ensure_plugins_loaded()
    assert len(ACTION_TYPES) == before
    assert loader is again, "should reuse the one shared loader"
    # modules imported once, not per call
    names = [getattr(m, "PLUGIN_NAME", "?") for m in loader.plugin_modules]
    assert len(names) == len(set(names)), f"plugin modules imported twice: {names}"


def test_schema_only_load_needs_no_executor():
    """The IDE path passes no ActionExecutor and must not raise."""
    loader = ensure_plugins_loaded()          # no executor
    assert loader is not None
    assert "play_sound" in ACTION_TYPES


def test_a_later_executor_still_gets_handlers():
    """A GameRunner created after the IDE already loaded schemas must still get
    its execute_* handlers registered on ITS executor — otherwise audio would
    be listed in the editor but do nothing at runtime."""
    from runtime.action_executor import ActionExecutor
    ensure_plugins_loaded()                   # schema-only first, as the IDE does
    ex = ActionExecutor()
    ensure_plugins_loaded(ex)                 # then a runtime executor
    assert "play_sound" in ex.action_handlers, \
        "plugin handlers not registered on an executor provided after load"


def test_both_entry_points_use_the_shared_loader():
    """Guard the 'one load point' property: the runtime and main.py must both
    go through ensure_plugins_loaded, or the IDE/runtime registries diverge
    again."""
    gr = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    mn = (REPO_ROOT / "main.py").read_text(encoding="utf-8")
    # GameRunner must keep calling it by the name ~28 test files patch
    # ('runtime.game_runner.load_all_plugins') — renaming that symbol breaks
    # every one of them, which is exactly what happened on the first attempt.
    assert "from events.plugin_loader import load_all_plugins" in gr
    assert "load_all_plugins(self.action_executor)" in gr
    assert "ensure_plugins_loaded()" in mn
    # and the IDE must load them BEFORE constructing the window, since the
    # action picker / Blockly read ACTION_TYPES at construction time.
    assert mn.index("ensure_plugins_loaded()") < mn.index("ide = PyGameMakerIDE()")


def test_the_alias_is_the_same_function():
    """ensure_plugins_loaded is just a clearer name for the IDE call site —
    if they ever diverge, the 'one load point' property is gone."""
    from events import plugin_loader
    assert plugin_loader.ensure_plugins_loaded is plugin_loader.load_all_plugins
