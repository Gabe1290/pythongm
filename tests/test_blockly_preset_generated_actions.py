"""Pin tests for docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2: presets learn
about the generated (no hand-written Blockly block) actions.
"""
import json
import os
import re
import sys
from pathlib import Path

import pytest

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
# set_draw_font/draw_sprite used to be deliberately left out here (sky_strike_1
# was thought to be the only user of either); the 2026-10-23 hand-written-block
# audit below found maze_3/maze_4 also use set_draw_font, so both are now
# enabled too (see HAND_WRITTEN_GAPS_CLOSED) and there is nothing left to
# exclude.
BEGINNER_DELIBERATELY_EXCLUDED = set()

# 2026-10-23: curating which samples Beginner shows (same spirit as the
# Junior-tier cleanup) surfaced that this file's own
# test_beginner_edition_samples_only_use_visible_or_explicitly_excluded_generated_actions
# is deliberately scoped to GENERATED_ACTION_NAMES only -- its docstring says
# a sample using a *hand-written* block beginner never enabled (its own
# example: maze_1's room_goto_next) is "a separate, pre-existing gap unrelated
# to this unit's bug". A fresh audit against config.toolbox_visibility's real
# toolbox_enabled_blocks() (the alias-aware pipeline the live Blockly editor
# actually uses) found every beginner-edition sample except plateforme_1 and
# match3_1/2/3 relied on at least one such hand-written block. Rather than
# drop those samples from the edition, closed the gaps so beginner stays
# fully buildable from the picker.
HAND_WRITTEN_GAPS_CLOSED = {
    "room_goto_next", "health_set", "move_snap_to_grid", "set_sprite",
    "set_variable", "if_condition", "wrap_around_room", "enable_views",
    "set_view",
}

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


def _action_to_block_type_map():
    """actionToBlockType: action name -> hardcoded Blockly block type. An
    action in here is a hardcoded block whose real toolbox placement is
    wherever its literal <block type> XML sits in blockly_workspace.html's
    `categories` dict -- NOT derived from ActionType.category, which is
    simply never consulted for it (confirmed: several hardcoded actions,
    e.g. draw_score/draw_lives/draw_health_bar, carry a stale category=
    "Score" left over from before docs/BLOCKLY_CATEGORY_MISMATCH_2026-10-15.md's
    "Score"->"Score/Lives/Health" merge -- harmless since it's dead data
    for them, but would be a false positive here if not excluded)."""
    text = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
            "blockly_workspace.html").read_text(encoding="utf-8")
    start = text.index("var actionToBlockType = {")
    end = text.index("\n        };", start)
    return set(re.findall(r"'([a-zA-Z0-9_]+)':\s*'[a-zA-Z0-9_]+'", text[start:end]))




def test_everything_presets_also_enable_the_categories_their_generated_actions_need():
    """A generated action showing in enabled_blocks is not enough on its
    own -- the real toolbox also gates the whole category box on
    enabled_categories. docs/BLOCKLY_CATEGORY_MISMATCH_2026-10-15.md
    "Resolution, part 2": promoting "Game" from a stray, category-gating-
    exempt fallback to a real category silently hid its 9 actions in
    get_platformer/get_grid_rpg/get_sokoban/get_testing until this was
    caught and fixed; the 11 actions recategorized Game->Drawing hit the
    same risk for get_platformer specifically (the one "everything" preset
    that did not already have "Drawing" enabled). docs/
    BLOCKLY_REMAINING_CATEGORY_ISSUES_PLAN.md Issue A: the same promotion
    for "Particles"/"Views" hit the identical risk for 7 of the 8
    "everything" presets.

    Originally scoped to ONLY "Game"/"Drawing"/"Particles"/"Views" -- the
    categories those two fixes touched -- because a broader version (every
    category) found a genuinely separate, unrelated bug: "Control" and
    "Timing" silently missing from several presets despite their blocks
    being enabled (Issue B). Now that Issue B is fixed too (2026-10-16,
    all 7 affected presets + the "thymio" plugin preset), this checks
    EVERY category again -- the full, unscoped audit -- across every
    registered preset, not just the "everything" ones (Issue B's
    "thymio" gap was in the plugin-loaded preset, outside
    EVERYTHING_PRESETS entirely)."""
    from events.action_types import ACTION_TYPES
    mapped = _action_to_block_type_map()
    presets = _presets()
    for name, cfg in presets.items():
        missing = {}
        for action_name in cfg.enabled_blocks:
            if action_name in mapped:
                continue
            action = ACTION_TYPES.get(action_name)
            if action is None:
                continue
            if action.category not in cfg.enabled_categories:
                missing.setdefault(action.category, []).append(action_name)
        assert not missing, f"{name} preset: blocks enabled but their category is not: {missing}"


# docs/BLOCKLY_REMAINING_CATEGORY_ISSUES_PLAN.md Issue B's full catalogue,
# found by the repo-wide audit the general test above now runs permanently
# -- pinned here so a future change to any of these presets is obviously
# compared against the known-fixed baseline, not just "does the general
# test still pass" (which a differently-shaped regression could still
# satisfy by accident).
ISSUE_B_CATALOGUE = {
    "blockly_editor": {"Control"},
    "code_editor": {"Control"},
    "grid_rpg": {"Control", "Timing"},
    "platformer": {"Control", "Timing"},
    "sokoban": {"Control", "Timing"},
    "testing": {"Control", "Timing", "Score/Lives/Health"},
    "thymio": {"Control"},
}


@pytest.mark.parametrize("preset_name,categories", sorted(ISSUE_B_CATALOGUE.items()))
def test_issue_b_catalogue_presets_now_have_their_missing_categories(preset_name, categories):
    presets = _presets()
    cfg = presets[preset_name]
    missing = categories - cfg.enabled_categories
    assert not missing, (preset_name, missing)


def test_thymio_preset_control_blocks_have_the_control_category_enabled():
    """extensions/thymio/blockly_categories.py's _build_thymio_preset()
    explicitly adds start_block/end_block/else_action to enabled_blocks
    (they're useful even in a Thymio-focused toolbox) but, before this
    fix, never added "Control" -- the real category all three belong to
    -- to enabled_categories, so they were silently invisible despite
    being deliberately, explicitly enabled (not just swept in by the
    generic GENERATED_ACTION_NAMES union every other Issue B preset
    relied on)."""
    presets = _presets()
    thymio = presets["thymio"]
    assert {"start_block", "end_block", "else_action"} <= thymio.enabled_blocks
    assert "Control" in thymio.enabled_categories


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


def test_beginner_preset_enables_the_hand_written_gap_closures():
    presets = _presets()
    assert HAND_WRITTEN_GAPS_CLOSED <= presets["beginner"].enabled_blocks
    assert "Views" in presets["beginner"].enabled_categories


def test_beginner_edition_samples_are_fully_buildable_from_the_picker():
    """Every action (hand-written or generated, under its canonical name or
    a legacy alias) a beginner-edition sample actually uses must be
    addable from the Beginner toolbox -- the real pipeline the live
    Blockly editor sends to JS (config.toolbox_visibility.
    toolbox_enabled_blocks(), which resolves both extension/Audio-always-
    visible actions and the action-name<->block-type mapping), not just
    the GENERATED_ACTION_NAMES-scoped check above. 2026-10-23: this is
    what makes it safe to keep all 14 samples in the Beginner edition
    instead of pruning the ones that use a hand-written block (see
    HAND_WRITTEN_GAPS_CLOSED)."""
    from events.plugin_loader import load_all_plugins, collect_project_action_names
    load_all_plugins()
    from events.action_types import ACTION_TYPE_ALIASES, ACTION_TO_BLOCKLY_MAP
    from config.blockly_config import PRESETS
    from config.toolbox_visibility import toolbox_enabled_blocks

    beginner = PRESETS["beginner"]
    enabled_block_types = toolbox_enabled_blocks(beginner, project_data=None)

    unaccounted = {}
    for sample in BEGINNER_EDITION_SAMPLES:
        project_file = REPO_ROOT / "samples" / sample / "project.json"
        assert project_file.exists(), f"missing sample: {sample}"
        project_data = json.loads(project_file.read_text(encoding="utf-8"))
        used = collect_project_action_names(project_data)

        missing = set()
        for name in used:
            canonical = ACTION_TYPE_ALIASES.get(name, name)
            block_type = ACTION_TO_BLOCKLY_MAP.get(canonical, canonical)
            if (block_type not in enabled_block_types
                    and canonical not in enabled_block_types
                    and name not in enabled_block_types):
                missing.add(name)
        if missing:
            unaccounted[sample] = sorted(missing)

    assert unaccounted == {}, f"actions used but not addable from the picker: {unaccounted}"


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
    assert cfg.config_version == 4
    assert bc.GENERATED_ACTION_NAMES <= cfg.enabled_blocks
    assert {"event_create", "move_set_hspeed"} <= cfg.enabled_blocks  # not clobbered
    # restart_game/burst_particles/set_view (added by the version-1->2
    # migration) need their real categories too, which the version-2->3
    # and version-3->4 migrations add in the same pass since this config
    # started below version 2 either way.
    assert {"Game", "Particles", "Views"} <= cfg.enabled_categories

    on_disk = json.loads(config_path.read_text(encoding="utf-8"))
    assert on_disk["config_version"] == 4
    assert "restart_game" in on_disk["enabled_blocks"]
    assert {"Game", "Particles", "Views"} <= set(on_disk["enabled_categories"])

    # Loading again must not re-print/re-save the migration (version already current).
    saved_mtime = config_path.stat().st_mtime_ns
    cfg2 = bc.load_config()
    assert cfg2.config_version == 4
    assert config_path.stat().st_mtime_ns == saved_mtime


def test_load_config_migrates_a_version2_config_missing_the_game_category(tmp_path, monkeypatch):
    """docs/BLOCKLY_CATEGORY_MISMATCH_2026-10-15.md "Resolution, part 2":
    a config already migrated once under the OLD (Unit 2) scheme --
    config_version == 2, restart_game already in enabled_blocks -- still
    could never have had "Game" in enabled_categories, since it did not
    exist as a real, toggleable category at that point. The version-2->3
    migration must catch this case specifically (not just version-1
    configs)."""
    import config.blockly_config as bc

    old_data = {
        "enabled_blocks": sorted(bc.GENERATED_ACTION_NAMES | {"event_create"}),
        "enabled_categories": ["Events"],
        "preset_name": "custom",
        "config_version": 2,
    }
    config_path = tmp_path / "blockly_config.json"
    config_path.write_text(json.dumps(old_data), encoding="utf-8")
    monkeypatch.setattr(bc, "get_config_path", lambda: config_path)

    cfg = bc.load_config()
    assert cfg.config_version == 4
    assert "Game" in cfg.enabled_categories

    on_disk = json.loads(config_path.read_text(encoding="utf-8"))
    assert on_disk["config_version"] == 4
    assert "Game" in on_disk["enabled_categories"]


def test_load_config_migrates_a_version3_config_missing_particles_and_views(tmp_path, monkeypatch):
    """docs/BLOCKLY_REMAINING_CATEGORY_ISSUES_PLAN.md Issue A: same
    situation as the version-2->3 "Game" migration, for a config already
    at version 3 (migrated under THAT scheme) with particle/view actions
    already in enabled_blocks but no way to have ever had "Particles"/
    "Views" enabled, since neither existed as a real category yet."""
    import config.blockly_config as bc

    old_data = {
        "enabled_blocks": ["event_create", "burst_particles", "set_view"],
        "enabled_categories": ["Events"],
        "preset_name": "custom",
        "config_version": 3,
    }
    config_path = tmp_path / "blockly_config.json"
    config_path.write_text(json.dumps(old_data), encoding="utf-8")
    monkeypatch.setattr(bc, "get_config_path", lambda: config_path)

    cfg = bc.load_config()
    assert cfg.config_version == 4
    assert "Particles" in cfg.enabled_categories
    assert "Views" in cfg.enabled_categories

    on_disk = json.loads(config_path.read_text(encoding="utf-8"))
    assert on_disk["config_version"] == 4
    assert "Particles" in on_disk["enabled_categories"]
    assert "Views" in on_disk["enabled_categories"]


def test_load_config_does_not_add_game_or_particles_or_views_when_no_block_is_enabled(tmp_path, monkeypatch):
    """The version migrations should not turn a category on for a config
    that never had any of its actions enabled in the first place."""
    import config.blockly_config as bc

    old_data = {
        "enabled_blocks": ["event_create", "move_set_hspeed"],
        "enabled_categories": ["Events", "Movement"],
        "preset_name": "custom",
        "config_version": 2,
    }
    config_path = tmp_path / "blockly_config.json"
    config_path.write_text(json.dumps(old_data), encoding="utf-8")
    monkeypatch.setattr(bc, "get_config_path", lambda: config_path)

    cfg = bc.load_config()
    assert cfg.config_version == 4
    assert "Game" not in cfg.enabled_categories
    assert "Particles" not in cfg.enabled_categories
    assert "Views" not in cfg.enabled_categories


def test_fresh_config_is_already_current_version():
    from config.blockly_config import BlocklyConfig
    assert BlocklyConfig.get_beginner().config_version == 4
    assert BlocklyConfig(preset_name="custom").config_version == 4


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



def test_every_preset_with_destroy_other_also_offers_destroy_all_of_object():
    """Blockly audit B19: maze_4 (in the beginner edition) needs the new
    instance_destroy_object block to round-trip its trigger object."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from config.blockly_config import PRESETS
    missing = sorted(name for name, cfg in PRESETS.items()
                     if "instance_destroy_other" in cfg.enabled_blocks
                     and "instance_destroy_object" not in cfg.enabled_blocks)
    assert missing == []
