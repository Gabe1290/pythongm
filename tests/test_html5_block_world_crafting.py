"""HTML5 export structural coverage for Block World's Tier 8 crafting
(docs/BLOCK_WORLD_CRAFTING_PLAN.md Unit 2): set_crafting_recipe/craft_item.

No JS engine/Playwright in CI (same standing limitation as every other
HTML5 block-world/raycast test) -- source-level structural assertions,
matching test_html5_block_world_reward.py's tier for this same extension.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

BW_JS = (REPO_ROOT / "extensions" / "block_world" / "export_html5.js").read_text(encoding="utf-8")


def _action_body(name):
    m = re.search(r"registerExtensionAction\('%s'(.*?)\n\}\);" % re.escape(name),
                   BW_JS, re.S)
    assert m, "%s not registered" % name
    return m.group(1)


def test_set_crafting_recipe_registered():
    assert "registerExtensionAction('set_crafting_recipe'" in BW_JS


def test_craft_item_registered():
    assert "registerExtensionAction('craft_item'" in BW_JS


def test_set_crafting_recipe_validates_output_before_storing():
    body = _action_body("set_crafting_recipe")
    assert "BLOCK_FACE_COLORS.hasOwnProperty(output)" in body
    assert "cfg.recipes" in body


def test_set_crafting_recipe_requires_input_1():
    body = _action_body("set_crafting_recipe")
    # input_1 is checked and can abort registration; input_2/input_3 are
    # independently optional (pushed only if well-formed) -- mirrors
    # handlers.execute_set_crafting_recipe_action's design decision 2.
    assert "bwCraftingSlot(params.input_1, params.input_1_count, obj, game)" in body
    assert "if (!first) return;" in body
    assert "inputs.push(extra)" in BW_JS  # inside the forEach helper


def test_craft_item_checks_inventory_flag_and_recipe_presence():
    body = _action_body("craft_item")
    assert "cfg.inventory" in body
    assert "cfg.recipes || {}" in body


def test_craft_item_is_all_or_nothing():
    """Every input is checked in one pass BEFORE any consuming pass runs --
    two separate loops over recipe.inputs, not one combined check-and-consume
    loop that could partially consume before finding a shortfall."""
    body = _action_body("craft_item")
    check_loop = body.index("inv[pair[0]] >= pair[1]")
    consume_loop = body.index("inv[pair[0]] -= pair[1]")
    assert check_loop < consume_loop


def test_crafting_slot_helper_shared_by_both_actions():
    """bwCraftingSlot is a standalone helper (not inlined per-call), so
    input_1/input_2/input_3 validation can't silently drift apart."""
    assert "function bwCraftingSlot(" in BW_JS
    body = _action_body("set_crafting_recipe")
    assert "bwCraftingSlot(" in body


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
