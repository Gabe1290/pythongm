"""docs/KID_UI_SIMPLIFICATION_PLAN.md Phase 3: the junior tier's Blockly
toolbox is exactly what the junior tutorials (01-04, 15, 16) use. The needed
set is derived here from the tutorials' reference projects, so a tutorial
that starts needing a new block fails this test instead of stranding a
student (the junior tier hides Configure Action Blocks)."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from config.blockly_config import PRESETS, BlocklyConfig
from config.editions import EDITIONS

# Runtime action names the reference builders use that differ from the
# registered action/block name.
ACTION_ALIASES = {"end_game": "game_end"}

# Blocks kept that the builders can't show: events (not actions), blocks the
# lesson pages name but the builders express another way, and one block a
# preset invariant forces alongside instance_destroy_other.
LESSON_TEXT_EXTRAS = {
    "event_keyboard_nokey", "event_keyboard_held", "event_keyboard_press",
    "event_collision", "event_create", "event_step", "event_draw",
    "event_alarm", "event_other",
    "score_add", "lives_add", "else_action",
    "instance_destroy_other", "instance_destroy_object",
}


def _tutorial_blocks():
    from tools import tutorial_reference_projects as t
    from events.action_types import ACTION_TO_BLOCKLY_MAP

    actions = set()

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("action"), str):
                actions.add(o["action"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for name in ("build_t02", "build_t03", "build_t04", "build_t15", "build_t16"):
        for phase in range(1, 5):
            root = Path(tempfile.mkdtemp())
            try:
                getattr(t, name)(root, phase=phase)
            except TypeError:
                getattr(t, name)(root)
            walk(json.loads((root / "project.json").read_text(encoding="utf-8")))
            for f in root.glob("objects/*.json"):
                walk(json.loads(f.read_text(encoding="utf-8")))
    return {ACTION_ALIASES.get(a, ACTION_TO_BLOCKLY_MAP.get(a, a)) for a in actions}


def test_junior_is_registered_and_selected_by_the_junior_edition():
    assert "junior" in PRESETS
    assert EDITIONS["junior"]["default_blockly_preset"] == "junior"
    assert EDITIONS["beginner"]["default_blockly_preset"] == "beginner"
    assert PRESETS["junior"].preset_name == "junior"
    assert PRESETS["junior"].enabled_blocks == set(BlocklyConfig.JUNIOR_BLOCKS)


def test_junior_offers_every_block_the_tutorials_use():
    missing = _tutorial_blocks() - PRESETS["junior"].enabled_blocks
    assert not missing, f"junior toolbox lacks blocks the tutorials need: {missing}"


def test_junior_offers_nothing_beyond_the_tutorials():
    extra = (PRESETS["junior"].enabled_blocks - _tutorial_blocks()) - LESSON_TEXT_EXTRAS
    assert not extra, f"junior toolbox has blocks no tutorial uses: {extra}"


def test_junior_drops_the_code_like_blocks():
    junior = PRESETS["junior"].enabled_blocks
    for block in ("execute_code", "execute_script", "exit_event",
                  "test_variable", "sleep", "set_window_caption",
                  "if_collision", "set_gravity", "instance_change",
                  "move_direction", "room_if_next_exists"):
        assert block not in junior, block


def test_beginner_preset_is_untouched():
    assert "execute_code" in PRESETS["beginner"].enabled_blocks
    assert "if_collision" in PRESETS["beginner"].enabled_blocks


def test_junior_categories_all_still_have_blocks():
    assert PRESETS["junior"].enabled_categories == PRESETS["beginner"].enabled_categories
