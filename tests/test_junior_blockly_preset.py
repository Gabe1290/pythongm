"""docs/KID_UI_SIMPLIFICATION_PLAN.md Phase 3: the junior tier's Blockly
preset is the beginner toolbox minus a short list of code-like / niche
blocks the junior tutorials never use."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.blockly_config import PRESETS, BlocklyConfig
from config.editions import EDITIONS


def test_junior_is_registered_and_selected_by_the_junior_edition():
    assert "junior" in PRESETS
    assert EDITIONS["junior"]["default_blockly_preset"] == "junior"
    assert EDITIONS["beginner"]["default_blockly_preset"] == "beginner"


def test_junior_is_beginner_minus_the_removed_blocks():
    beginner = PRESETS["beginner"].enabled_blocks
    junior = PRESETS["junior"].enabled_blocks
    removed = BlocklyConfig.JUNIOR_REMOVED_BLOCKS
    assert removed <= beginner, "removed list names a block beginner never had"
    assert junior == beginner - removed
    assert PRESETS["junior"].preset_name == "junior"


def test_beginner_preset_is_untouched():
    assert "execute_code" in PRESETS["beginner"].enabled_blocks


def test_junior_keeps_what_the_junior_tutorials_teach():
    junior = PRESETS["junior"].enabled_blocks
    for block in ("event_create", "event_keyboard_held", "event_collision",
                  "event_alarm", "move_set_hspeed", "move_set_vspeed",
                  "move_stop", "bounce", "reverse_horizontal", "set_alarm",
                  "draw_text", "draw_score", "score_set", "lives_set",
                  "draw_lives", "instance_create", "instance_destroy",
                  "room_restart", "game_end", "show_highscore",
                  "output_message", "restart_game", "set_draw_color",
                  "start_moving_direction", "jump_to_start",
                  "test_instance_count", "test_expression",
                  "start_block", "end_block"):
        assert block in junior, block


def test_junior_categories_all_still_have_blocks():
    cfg = PRESETS["junior"]
    assert cfg.enabled_categories == PRESETS["beginner"].enabled_categories
