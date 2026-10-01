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


# ---------------------------------------------------------------------------
# U3 — BlocklyWidget.apply_configuration sends the resolved payload.
# ---------------------------------------------------------------------------

def _apply_and_capture(widget, config):
    import json
    sent = {}

    def _capture(js):
        payload = js[len("window.blocklyApi.reconfigureToolbox("):-1]
        sent["config"] = json.loads(payload)

    widget.web_view.page().runJavaScript = _capture
    widget.apply_configuration(config)
    return sent["config"]


def test_apply_configuration_payload_for_beginner_with_and_without_raycast():
    from PySide6.QtWidgets import QApplication, QMainWindow
    QApplication.instance() or QApplication([])
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from editors.object_editor.blockly_widget import BlocklyWidget
    from config.blockly_config import PRESETS

    class _IDE(QMainWindow):
        current_project_data = None

    ide = _IDE()
    widget = BlocklyWidget(ide)
    try:
        beginner = PRESETS["beginner"]

        payload = _apply_and_capture(widget, beginner)
        blocks = set(payload["enabled_blocks"])
        assert "set_facing_angle" not in blocks       # raycast inactive
        assert "enable_raycast_view" not in blocks
        assert "restart_game" in blocks                # U2 addition, still works
        assert "draw_sprite" not in blocks              # U2 deliberate exclusion
        assert "event_create" in blocks                 # non-action entry preserved

        ide.current_project_data = {"settings": {"active_extensions": ["raycast_2_5d"]}}
        payload2 = _apply_and_capture(widget, beginner)
        blocks2 = set(payload2["enabled_blocks"])
        assert "set_facing_angle" in blocks2            # active overrides the preset
        assert "enable_raycast_view" in blocks2
        assert "draw_minimap" in blocks2
        assert "draw_doom_hud" in blocks2
        assert "restart_game" in blocks2                # unaffected by extension activation
    finally:
        widget.deleteLater()


def test_apply_configuration_replaces_not_unions_action_entries():
    """An inactive extension's action name, even if somehow present in
    config.enabled_blocks directly, must not survive -- the payload is
    built by REPLACING every action-governed entry with visible_actions'
    answer, not merely adding to the preset's raw set."""
    from PySide6.QtWidgets import QApplication, QMainWindow
    QApplication.instance() or QApplication([])
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from editors.object_editor.blockly_widget import BlocklyWidget
    from config.blockly_config import BlocklyConfig

    class _IDE(QMainWindow):
        current_project_data = None

    ide = _IDE()
    widget = BlocklyWidget(ide)
    try:
        cfg = BlocklyConfig(preset_name="custom")
        cfg.enabled_blocks = {"event_create", "set_facing_angle"}  # planted directly
        payload = _apply_and_capture(widget, cfg)
        assert "set_facing_angle" not in set(payload["enabled_blocks"])
        assert "event_create" in set(payload["enabled_blocks"])
    finally:
        widget.deleteLater()


def test_register_custom_blocks_sends_every_action_unfiltered():
    """docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, U3: "block definitions are
    registered regardless of toolbox" -- a saved workspace referencing a
    now-hidden block still loads, because Blockly.Blocks[blockType] exists
    independent of which blocks the toolbox palette shows. Structural proof
    (no JS engine to actually load a workspace in CI): _register_custom_blocks
    sends the FULL, unfiltered ACTION_TYPES to registerCustomBlocks -- no
    preset or project_data narrows this set, unlike apply_configuration's
    toolbox payload above."""
    src = (REPO_ROOT / "editors" / "object_editor" / "blockly_widget.py").read_text(encoding="utf-8")
    body_start = src.index("def _register_custom_blocks")
    body_end = src.index("\n    def ", body_start + 1)
    body = src[body_start:body_end]
    assert "for name, action_type in ACTION_TYPES.items():" in body
    assert "visible_actions" not in body
    assert "PRESETS" not in body
    assert "project_data" not in body

    # And on the JS side: registerCustomBlocks defines Blockly.Blocks[...]
    # unconditionally, with no reference to enabledBlocks/enabledCategories
    # at all (those only exist inside generateToolboxXml).
    js_src = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
              "blockly_workspace.html").read_text(encoding="utf-8")
    fn_start = js_src.index("function registerCustomBlocks(actionDefs) {")
    fn_end = js_src.index("generateActionCode = function", fn_start)
    fn_body = js_src[fn_start:fn_end]
    assert "enabledBlocks" not in fn_body
    assert "enabledCategories" not in fn_body
    assert "Blockly.Blocks[bt] = {" in fn_body
