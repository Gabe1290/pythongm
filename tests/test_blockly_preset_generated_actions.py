"""Pin tests for docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2: presets learn
about the generated (no hand-written Blockly block) actions.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# docs/BLOCKLY_TOOLBOX_GATING_PLAN.md's "intermediate and the focused
# presets" list, plus "full" (handled by the same migration philosophy,
# just stated separately in the plan).
EVERYTHING_PRESETS = (
    "full", "intermediate", "platformer", "grid_rpg", "sokoban",
    "testing", "code_editor", "blockly_editor",
)

# Decided with the user 2026-10-01 (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, U2):
# the original 3-action partial audit, plus 17 more found by a full
# per-sample audit (this file's own
# test_beginner_edition_samples_only_use_visible_or_explicitly_excluded_generated_actions,
# written to catch exactly this kind of gap -- and it did).
BEGINNER_NEWLY_ADDED = {
    "restart_game", "set_window_caption", "set_draw_color",
    "start_moving_direction", "comment", "if_collision",
    "test_instance_count", "sleep", "move_to_contact", "execute_code",
    "if_object_exists", "set_direction_speed", "destroy_at_position",
    "check_empty", "jump_to_start", "test_alignment", "test_chance",
    "test_expression", "execute_script", "set_background",
}
BEGINNER_DELIBERATELY_EXCLUDED = {"set_draw_font", "draw_sprite"}

BEGINNER_EDITION_SAMPLES = (
    "maze_1", "maze_2", "maze_3", "maze_4",
    "plateforme_1", "plateforme_2", "plateforme_3",
    "match3_1", "match3_2", "match3_3",
    "views_1", "views_2",
    "treasure", "sky_strike_1",
)


def _presets():
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_config import PRESETS
    return PRESETS


def test_everything_presets_include_every_generated_action():
    from config.blockly_config import GENERATED_ACTION_NAMES
    presets = _presets()
    for name in EVERYTHING_PRESETS:
        missing = GENERATED_ACTION_NAMES - presets[name].enabled_blocks
        assert not missing, f"{name} preset missing generated actions: {missing}"


def test_beginner_gained_exactly_the_three_decided_actions():
    presets = _presets()
    beginner = presets["beginner"]
    assert BEGINNER_NEWLY_ADDED <= beginner.enabled_blocks
    assert not (BEGINNER_DELIBERATELY_EXCLUDED & beginner.enabled_blocks)


def test_beginner_edition_samples_only_use_visible_or_explicitly_excluded_generated_actions():
    """Every GENERATED action a beginner-edition sample actually uses must
    either show in the beginner toolbox, or be on the explicit "loads but
    can't be re-added from the picker" list this unit decided on.

    Scoped to GENERATED_ACTION_NAMES only -- a sample using a *hand-written*
    block beginner has never enabled (e.g. maze_1's room_goto_next) is a
    separate, pre-existing gap unrelated to this unit's bug (those blocks
    were never bulk-included anywhere, gated or not, so there's no
    regression here to pin)."""
    from events.plugin_loader import load_all_plugins, collect_project_action_names
    load_all_plugins()
    from config.blockly_config import PRESETS, GENERATED_ACTION_NAMES
    from config.toolbox_visibility import visible_actions

    beginner = PRESETS["beginner"]
    shown = visible_actions(beginner, project_data=None)
    allowed = shown | BEGINNER_DELIBERATELY_EXCLUDED

    unaccounted = {}
    for sample in BEGINNER_EDITION_SAMPLES:
        project_file = REPO_ROOT / "samples" / sample / "project.json"
        assert project_file.exists(), f"missing sample: {sample}"
        project_data = json.loads(project_file.read_text(encoding="utf-8"))
        used = collect_project_action_names(project_data)
        missing = (used - allowed) & GENERATED_ACTION_NAMES
        if missing:
            unaccounted[sample] = sorted(missing)

    assert unaccounted == {}, f"generated actions used but not visible/excluded: {unaccounted}"


def test_load_config_migrates_a_pre_unit2_saved_config_once(tmp_path, monkeypatch):
    import config.blockly_config as bc

    old_data = {
        "enabled_blocks": ["event_create", "move_set_hspeed"],
        "enabled_categories": ["Events"],
        "preset_name": "custom",
    }
    config_path = tmp_path / "blockly_config.json"
    config_path.write_text(json.dumps(old_data), encoding="utf-8")
    monkeypatch.setattr(bc, "get_config_path", lambda: config_path)

    cfg = bc.load_config()
    assert cfg.config_version == 2
    assert bc.GENERATED_ACTION_NAMES <= cfg.enabled_blocks
    assert {"event_create", "move_set_hspeed"} <= cfg.enabled_blocks  # not clobbered

    on_disk = json.loads(config_path.read_text(encoding="utf-8"))
    assert on_disk["config_version"] == 2
    assert "restart_game" in on_disk["enabled_blocks"]

    # Loading again must not re-print/re-save the migration (version already 2).
    saved_mtime = config_path.stat().st_mtime_ns
    cfg2 = bc.load_config()
    assert cfg2.config_version == 2
    assert config_path.stat().st_mtime_ns == saved_mtime


def test_fresh_config_is_already_current_version():
    from config.blockly_config import BlocklyConfig
    assert BlocklyConfig.get_beginner().config_version == 2
    assert BlocklyConfig(preset_name="custom").config_version == 2


def test_promoting_test_expression_to_a_block_kept_every_preset_showing_it():
    """Blockly audit B6c moved test_expression from GENERATED_ACTION_NAMES to
    a hand-written block. Six focused presets enabled it only through the
    generated set, so they silently lost it; PROMOTED_TO_HAND_WRITTEN_BLOCKS
    keeps them as they were. Thymio never had it."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_config import PRESETS, GENERATED_ACTION_NAMES
    assert "test_expression" not in GENERATED_ACTION_NAMES
    missing = sorted(name for name, cfg in PRESETS.items()
                     if name != "thymio" and "test_expression" not in cfg.enabled_blocks)
    assert missing == []



def test_every_preset_with_move_towards_point_shows_its_block():
    """Blockly audit B7: move_towards_point now loads into the hand-written
    move_towards block (no generated custom block any more), so a preset
    that enables the action must also enable the block."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_config import PRESETS
    missing = sorted(name for name, cfg in PRESETS.items()
                     if "move_towards_point" in cfg.enabled_blocks
                     and "move_towards" not in cfg.enabled_blocks)
    assert missing == []
