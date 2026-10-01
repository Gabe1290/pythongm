"""Pin tests for config/toolbox_visibility.py (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md,
Unit 1). Pure Python -- no Qt, no JS, not wired into either editor yet; this
file proves the resolver itself before U3/U4 call it from anywhere real.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _beginner():
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_config import BlocklyConfig
    return BlocklyConfig.get_beginner()


def test_hand_written_block_gating_is_unchanged():
    from config.toolbox_visibility import visible_actions
    cfg = _beginner()
    shown = visible_actions(cfg, project_data=None)
    assert "bounce" in shown            # in beginner's enabled_blocks
    assert "draw_sprite" not in shown  # a generated action, deliberately excluded from beginner (U2)


def test_audio_actions_are_always_visible_regardless_of_preset():
    from config.toolbox_visibility import visible_actions
    cfg = _beginner()
    assert "play_sound" not in cfg.enabled_blocks  # not hand-written-block-gated at all
    shown = visible_actions(cfg, project_data=None)
    for name in ("check_sound", "stop_sound", "play_sound", "play_music",
                 "stop_music", "set_volume"):
        assert name in shown


def test_extension_action_hidden_when_inactive_in_every_preset():
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_config import PRESETS
    from config.toolbox_visibility import visible_actions

    for preset_name, cfg in PRESETS.items():
        shown = visible_actions(cfg, project_data=None)
        assert "set_facing_angle" not in shown, (
            f"raycast_2_5d action visible in {preset_name!r} with no active project")


def test_extension_action_shown_in_beginner_when_active_via_settings():
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.toolbox_visibility import visible_actions

    cfg = _beginner()
    assert "set_facing_angle" not in visible_actions(cfg, project_data=None)

    project_data = {"settings": {"active_extensions": ["raycast_2_5d"]}}
    shown = visible_actions(cfg, project_data=project_data)
    assert "set_facing_angle" in shown        # active overrides the preset
    assert "enable_raycast_view" in shown
    assert "draw_minimap" in shown
    assert "draw_doom_hud" in shown


def test_extension_action_shown_when_active_via_usage_no_migration_needed():
    """A project that already USES a raycast action (no explicit
    settings.active_extensions at all) must show the rest of that
    extension's actions too -- decision 2026-09-30, "no migration"."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.toolbox_visibility import visible_actions

    cfg = _beginner()
    project_data = {
        "assets": {"objects": {"obj_cam": {"events": {"create": {
            "actions": [{"action": "set_facing_angle", "parameters": {}}]
        }}}}}
    }
    shown = visible_actions(cfg, project_data=project_data)
    assert "set_facing_angle" in shown
    assert "draw_minimap" in shown  # the rest of the extension, not just the used action


def test_globally_disabled_extension_is_never_active():
    from events.plugin_loader import load_all_plugins, set_extension_enabled
    load_all_plugins()
    from config.toolbox_visibility import active_extensions, visible_actions

    set_extension_enabled("raycast_2_5d", False)
    try:
        project_data = {"settings": {"active_extensions": ["raycast_2_5d"]}}
        assert "raycast_2_5d" not in active_extensions(project_data)
        shown = visible_actions(_beginner(), project_data=project_data)
        assert "set_facing_angle" not in shown
    finally:
        set_extension_enabled("raycast_2_5d", True)


def test_active_extensions_ignores_malformed_settings():
    from config.toolbox_visibility import active_extensions
    assert active_extensions(None) == set()
    assert active_extensions({}) == set()
    assert active_extensions({"settings": {"active_extensions": "not-a-list"}}) == set()
    assert active_extensions({"settings": {"active_extensions": None}}) == set()


def _js_hardcoded_action_block_types():
    """Extract the real <block type="..."> set from blockly_workspace.html's
    `categories` object -- the ground truth GENERATED_ACTION_NAMES must stay
    in sync with (config/blockly_config.py's own comment on that constant
    promises this test). Excludes the two shadow block types (math_number,
    text) and the 9 read-only value_* blocks, neither of which are actions."""
    import re
    js_path = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
               "blockly_workspace.html")
    text = js_path.read_text(encoding="utf-8")
    start = text.index('var categories = {')
    end = text.index('// Add Math and Logic categories')
    blob = text[start:end]
    types = set(re.findall(r'type="([a-zA-Z_][a-zA-Z0-9_]*)"', blob))
    types -= {"math_number", "text"}
    types = {t for t in types if not t.startswith("value_")}
    return types


def test_generated_action_names_matches_the_real_js_hardcoded_set():
    """Drift guard: if blockly_workspace.html's hardcoded `categories` object
    ever gains or loses a block, GENERATED_ACTION_NAMES
    (config/blockly_config.py) must be updated to match, or the whole
    docs/BLOCKLY_TOOLBOX_GATING_PLAN.md fix silently regresses for whatever
    action changed sides."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from events.action_types import ACTION_TYPES, ACTION_TO_BLOCKLY_MAP
    from events.plugin_loader import extension_for_action
    from config.blockly_config import GENERATED_ACTION_NAMES

    hardcoded = _js_hardcoded_action_block_types()
    expected_generated = set()
    for name, action in ACTION_TYPES.items():
        if extension_for_action(name) is not None:
            continue
        if action.category == "Audio":
            continue
        block_type = ACTION_TO_BLOCKLY_MAP.get(name, name)
        if block_type not in hardcoded:
            expected_generated.add(name)

    assert GENERATED_ACTION_NAMES == expected_generated, (
        f"missing from GENERATED_ACTION_NAMES: {expected_generated - GENERATED_ACTION_NAMES}; "
        f"stale entries no longer generated: {GENERATED_ACTION_NAMES - expected_generated}")
