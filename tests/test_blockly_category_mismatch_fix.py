"""Regression tests for docs/BLOCKLY_CATEGORY_MISMATCH_2026-10-15.md.

User request: "The 'Configure Action Blocks...' sub menu should display a
window that corresponds to the actual blockly editor Blocks... there is a
'Score/Lives/Health' and a 'Score' categories. The 'Grid' category should
be merged with the Movement category. ... 'Output' should be merged with
'Drawing'."

Root cause (see the plan doc for the full investigation): several
ActionType.category strings in events/action_types.py didn't match any
real hardcoded toolbox category in blockly_workspace.html's `categories`
JS dict, so registerCustomBlocks() auto-generated brand-new stray toolbox
categories for them ("Score" duplicating "Score/Lives/Health", "Grid"
duplicating/siblinging "Movement") instead of merging in. "Output" vs
"Drawing" was a separate, static, intentional split present identically
in every source -- a plain consolidation, not a leak.

While fixing the Output/Drawing merge, found a genuinely separate bug in
the same code: the "execute_code" block had NO <block type="execute_code">
entry anywhere in the real (post-load) toolbox -- it was undraggable, only
present in the static pre-load toolbox XML that every real page load
replaces. Fixed by adding it alongside output_message under the merged
"Drawing" category.

No Node/browser in CI, so the real toolbox's categories are checked by
parsing blockly_workspace.html's JS source structurally -- the same
established technique as test_toolbox_visibility.py's
_js_hardcoded_action_block_types().
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_HTML = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
                   "blockly_workspace.html")

STRAY_NAMES = {"Score", "Grid", "Output"}


def _real_toolbox_category_keys():
    """Top-level keys of the dynamic `categories` JS dict -- the one
    generateToolboxXml() actually builds the live toolbox from."""
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = text.index("var categories = {")
    end = text.index("// Add Math and Logic categories")
    blob = text[start:end]
    return re.findall(r"^\s*'([A-Za-z/ ]+)':\s*\{", blob, re.M)


def _static_initial_toolbox_category_names():
    """<category name="..."> in the static <xml id="toolbox"> block Blockly
    is first injected with, before any real page load replaces it."""
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = text.index('<xml id="toolbox"')
    end = text.index("</xml>", start)
    blob = text[start:end]
    return re.findall(r'<category name="([^"]+)"', blob)


def test_no_stray_categories_in_the_real_toolbox():
    keys = _real_toolbox_category_keys()
    assert not (set(keys) & STRAY_NAMES), keys
    assert "Score/Lives/Health" in keys
    assert "Drawing" in keys
    assert "Movement" in keys


def test_no_stray_categories_in_the_static_initial_toolbox():
    """The static pre-load XML should stay consistent with the real one
    too, even though generateToolboxXml() replaces it on every real page
    load -- no reason to leave it describing a toolbox that no longer
    exists."""
    names = _static_initial_toolbox_category_names()
    assert not (set(names) & STRAY_NAMES), names


def test_execute_code_is_reachable_in_both_toolboxes():
    """The bug found while fixing the Output/Drawing merge: execute_code
    had no toolbox entry anywhere in the live (post-load) toolbox."""
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = text.index("var categories = {")
    end = text.index("// Add Math and Logic categories")
    assert '<block type="execute_code">' in text[start:end]

    static_start = text.index('<xml id="toolbox"')
    static_end = text.index("</xml>", static_start)
    assert '<block type="execute_code">' in text[static_start:static_end]


def test_category_colors_map_has_score_lives_health():
    """Dynamically-generated blocks (test_health etc., now category=
    'Score/Lives/Health') get their individual block colour from this map,
    independent of which toolbox category box they land in."""
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = text.index("var categoryColors = {")
    end = text.index("};", start)
    blob = text[start:end]
    assert "'Score/Lives/Health': '#5CA65C'" in blob
    assert "'Output'" not in blob


def _action_to_block_type_map():
    """actionToBlockType: action name -> hardcoded Blockly block type.
    registerCustomBlocks() skips any action already in here (`if
    (actionToBlockType[actionName]) continue;`), so for these actions
    ActionType.category is never consulted for toolbox placement at all --
    only an action name ABSENT from this map can actually leak into a
    stray dynamic category."""
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = text.index("var actionToBlockType = {")
    end = text.index("\n        };", start)
    return set(re.findall(r"'([a-zA-Z0-9_]+)':\s*'[a-zA-Z0-9_]+'", text[start:end]))


def test_no_leaking_action_type_carries_a_stray_category():
    """events/action_types.py must not assign category= to any string that
    doesn't correspond to a real toolbox category, for any action that can
    actually leak (i.e. isn't already hardcoded-mapped) -- the exact bug
    this was. Actions already in actionToBlockType (set_score, snap_to_grid,
    ...) are a separate, harmless, purely-cosmetic mismatch: their
    ActionType.category is never consulted for toolbox placement, since
    registerCustomBlocks skips them outright -- not part of this bug and
    not asserted here."""
    from events.action_types import ACTION_TYPES
    mapped = _action_to_block_type_map()
    stray = {name: a.category for name, a in ACTION_TYPES.items()
              if a.category in STRAY_NAMES and name not in mapped}
    assert not stray, stray


@pytest.mark.parametrize("name,expected_category", [
    ("test_health", "Score/Lives/Health"),
    ("show_highscore", "Score/Lives/Health"),
    ("test_score", "Score/Lives/Health"),
    ("test_lives", "Score/Lives/Health"),
    ("clear_highscore", "Score/Lives/Health"),
    ("test_alignment", "Movement"),
])
def test_specific_actions_moved_to_their_real_category(name, expected_category):
    from events.action_types import ACTION_TYPES
    assert ACTION_TYPES[name].category == expected_category


def test_block_registry_has_no_output_category():
    from config.blockly_config import BLOCK_REGISTRY
    assert "Output" not in BLOCK_REGISTRY


def test_block_registry_drawing_absorbed_output_blocks():
    from config.blockly_config import BLOCK_REGISTRY
    drawing_types = {b["type"] for b in BLOCK_REGISTRY["Drawing"]}
    assert {"output_message", "execute_code"} <= drawing_types


def test_block_registry_score_lives_health_absorbed_leaking_actions():
    from config.blockly_config import BLOCK_REGISTRY
    types = {b["type"] for b in BLOCK_REGISTRY["Score/Lives/Health"]}
    assert {"test_health", "test_score", "test_lives",
            "show_highscore", "clear_highscore"} <= types


def test_block_registry_movement_absorbed_test_alignment():
    from config.blockly_config import BLOCK_REGISTRY
    types = {b["type"] for b in BLOCK_REGISTRY["Movement"]}
    assert "test_alignment" in types


def test_block_registry_game_no_longer_has_highscore_actions():
    """show_highscore/clear_highscore moved OUT of "Game" (they never
    really lived there in the live toolbox -- "Score" -- and now correctly
    match their real "Score/Lives/Health" home)."""
    from config.blockly_config import BLOCK_REGISTRY
    types = {b["type"] for b in BLOCK_REGISTRY["Game"]}
    assert "show_highscore" not in types
    assert "clear_highscore" not in types
    # game_end/restart_game were the plan doc's "deliberate, separate,
    # un-decided follow-up" -- since resolved (part 2, 2026-10-16):
    # game_end moved to "Room" (where it always really landed); "Game"
    # itself became a real category holding the 9 genuine game-lifecycle
    # actions, restart_game included.
    assert "game_end" not in types
    assert types == {
        "restart_game", "load_game", "save_game", "open_webpage",
        "set_window_caption", "show_info", "show_video",
        "splash_show_image", "splash_show_text",
    }


# --------------------------------------------------------------------------
# "Resolution, part 2" (2026-10-16): the "Game" category promoted from a
# stray, uncolored, category-gating-exempt dynamic fallback to a real one
# (20 actions carried category="Game", not just restart_game as first
# thought -- 11 were really Drawing actions, 9 are genuine game-lifecycle
# ones); the orphaned text/text_join value blocks given their own always-on
# "Text" category, same precedent as Math/Logic.
# --------------------------------------------------------------------------

GAME_LIFECYCLE_ACTIONS = {
    "restart_game", "load_game", "save_game", "open_webpage",
    "set_window_caption", "show_info", "show_video",
    "splash_show_image", "splash_show_text",
}
DRAWING_RECATEGORIZED_ACTIONS = {
    "draw_arrow", "draw_background", "draw_ellipse", "draw_line",
    "draw_scaled_text", "draw_sprite", "draw_variable", "fill_color",
    "set_color", "set_draw_color", "set_draw_font",
}


def test_game_is_a_real_toolbox_category_not_a_stray_one():
    keys = _real_toolbox_category_keys()
    assert "Game" in keys


def test_game_category_has_a_real_color():
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = text.index("var categoryColors = {")
    end = text.index("};", start)
    assert "'Game':" in text[start:end]


@pytest.mark.parametrize("name,expected_category", [
    ("draw_arrow", "Drawing"), ("draw_background", "Drawing"),
    ("draw_ellipse", "Drawing"), ("draw_line", "Drawing"),
    ("draw_scaled_text", "Drawing"), ("draw_sprite", "Drawing"),
    ("draw_variable", "Drawing"), ("fill_color", "Drawing"),
    ("set_color", "Drawing"), ("set_draw_color", "Drawing"),
    ("set_draw_font", "Drawing"),
])
def test_drawing_ish_game_actions_recategorized(name, expected_category):
    from events.action_types import ACTION_TYPES
    assert ACTION_TYPES[name].category == expected_category


def test_game_lifecycle_actions_still_carry_game_category():
    """These 9 never needed an action_types.py change -- only promoting
    "Game" itself to a real toolbox category."""
    from events.action_types import ACTION_TYPES
    for name in GAME_LIFECYCLE_ACTIONS:
        assert ACTION_TYPES[name].category == "Game"


def test_no_action_type_carries_game_except_the_real_lifecycle_set():
    """Every LEAKING action (not already hardcoded-mapped -- see
    _action_to_block_type_map) still carrying category="Game" must be one
    of the 9 genuine lifecycle ones -- anything else slipping back in
    would be a fresh instance of this exact bug. A handful of hardcoded/
    mapped actions (draw_text, draw_rectangle, draw_circle, set_alpha,
    show_message) also carry a stale category="Game" -- harmless, since
    their real toolbox placement never consults that field at all (same
    exclusion as test_no_leaking_action_type_carries_a_stray_category)."""
    from events.action_types import ACTION_TYPES
    mapped = _action_to_block_type_map()
    still_game = {name for name, a in ACTION_TYPES.items()
                  if a.category == "Game" and name not in mapped}
    assert still_game == GAME_LIFECYCLE_ACTIONS


def test_block_registry_drawing_absorbed_the_recategorized_actions():
    from config.blockly_config import BLOCK_REGISTRY
    types = {b["type"] for b in BLOCK_REGISTRY["Drawing"]}
    assert DRAWING_RECATEGORIZED_ACTIONS <= types


def test_block_registry_room_absorbed_game_end():
    from config.blockly_config import BLOCK_REGISTRY
    types = {b["type"] for b in BLOCK_REGISTRY["Room"]}
    assert "game_end" in types


@pytest.mark.parametrize("preset_attr", [
    "get_full", "get_beginner", "get_intermediate", "get_platformer",
    "get_grid_rpg", "get_sokoban", "get_testing", "get_implemented_only",
    "get_code_editor", "get_blockly_editor",
])
def test_no_preset_shows_game_blocks_without_enabling_the_game_category(preset_attr):
    """The regression this part-2 fix almost shipped: promoting "Game" to a
    real, gated category silently hid its blocks in any preset that relied
    on the old stray-category's category-gating exemption without also
    listing "Game" in enabled_categories."""
    from config.blockly_config import BlocklyConfig
    config = getattr(BlocklyConfig, preset_attr)()
    if GAME_LIFECYCLE_ACTIONS & config.enabled_blocks:
        assert "Game" in config.enabled_categories, preset_attr


def test_config_version_bumped_for_the_game_category_migration():
    from config.blockly_config import BlocklyConfig
    assert BlocklyConfig().config_version >= 3


def test_text_category_exists_in_both_toolboxes():
    names = _static_initial_toolbox_category_names()
    assert "Text" in names
    # 2026-10-21 (docs/BLOCKLY_SCRATCH_PARITY_PLAN.md Feature 1): the live
    # toolbox no longer gives Text its own <category> -- it pools into
    # 'Operators' alongside Values/Math/Logic (TOOLBOX_CATEGORY_GROUPS).
    # Its blocks still exist and are still reachable (see the next test);
    # only the standalone category label is gone, by design.
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    assert "pushToGroup('Text'," in text


def test_text_and_text_join_blocks_present_in_both_toolboxes():
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    # Dynamic (real, post-load) toolbox.
    dyn_start = text.index("// Add Math and Logic categories")
    dyn_end = text.index("// Generate categories based on config")
    dyn_blob = text[dyn_start:dyn_end]
    assert '<block type="text"></block>' in dyn_blob
    assert '<block type="text_join"></block>' in dyn_blob
    # Static (pre-load) toolbox.
    static_start = text.index('<xml id="toolbox"')
    static_end = text.index("</xml>", static_start)
    static_blob = text[static_start:static_end]
    assert '<block type="text"></block>' in static_blob
    assert '<block type="text_join"></block>' in static_blob


def test_execute_code_promoted_out_of_generated_action_names():
    """execute_code now has a real hardcoded toolbox entry (test above), so
    it is no longer "generated" by registerCustomBlocks -- it moved to
    PROMOTED_TO_HAND_WRITTEN_BLOCKS, the existing mechanism for exactly
    this (test_expression, move_towards already use it), so every preset
    that unions "all generated + promoted" blocks keeps showing it."""
    from config.blockly_config import GENERATED_ACTION_NAMES, PROMOTED_TO_HAND_WRITTEN_BLOCKS
    assert "execute_code" not in GENERATED_ACTION_NAMES
    assert "execute_code" in PROMOTED_TO_HAND_WRITTEN_BLOCKS


def test_no_preset_references_the_stray_output_category():
    """No BlocklyConfig preset's enabled_categories should name "Output"
    any more -- it was folded into "Drawing" (which every such preset
    already had, or now gets instead)."""
    from config.blockly_config import BlocklyConfig
    for attr in ("get_full", "get_beginner", "get_intermediate", "get_platformer",
                 "get_grid_rpg", "get_sokoban", "get_testing",
                 "get_implemented_only", "get_code_editor", "get_blockly_editor"):
        config = getattr(BlocklyConfig, attr)()
        assert "Output" not in config.enabled_categories, (attr, config.enabled_categories)


def test_blockly_config_dialog_shows_no_stray_categories(qapp_for_dialog):
    from dialogs.blockly_config_dialog import BlocklyConfigDialog
    dlg = BlocklyConfigDialog()
    try:
        names = {dlg.tree.topLevelItem(i).text(0)
                  for i in range(dlg.tree.topLevelItemCount())}
    finally:
        dlg.deleteLater()
    # The dialog shows TRANSLATED category names (it runs under whatever
    # language is active), but the stray English category keys this bug
    # produced ("Score", "Grid", "Output") were never given their own
    # translation entries, so they'd always render in raw English
    # regardless of active language -- a literal match against the English
    # stray names is still a correct check even if the real categories
    # above are localized.
    assert not (names & STRAY_NAMES), names


@pytest.fixture
def qapp_for_dialog():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_category_translations_have_no_output_entry():
    """The "Output" category-name translation entries became dead once the
    category itself was deleted from the toolbox."""
    from config.blockly_translations import CATEGORY_TRANSLATIONS
    for lang, table in CATEGORY_TRANSLATIONS.items():
        assert "Output" not in table, lang


def test_config_dialog_category_colors_has_no_output_entry():
    from dialogs.blockly_config_dialog import BLOCKLY_CATEGORY_COLORS
    assert "Output" not in BLOCKLY_CATEGORY_COLORS


# --------------------------------------------------------------------------
# docs/BLOCKLY_REMAINING_CATEGORY_ISSUES_PLAN.md Issue A (2026-10-16): the
# same stray-category bug as "Game" above, for "Particles" (8 actions) and
# "Views" (2 actions) -- both clean, single-purpose groups, no mixed-
# category untangling needed.
# --------------------------------------------------------------------------

PARTICLES_ACTIONS = {
    "create_particle_system", "destroy_particle_system", "clear_particles",
    "create_particle_type", "create_emitter", "destroy_emitter",
    "burst_particles", "stream_particles",
}
VIEWS_ACTIONS = {"enable_views", "set_view"}


def test_particles_and_views_are_real_toolbox_categories_not_stray_ones():
    keys = _real_toolbox_category_keys()
    assert "Particles" in keys
    assert "Views" in keys


@pytest.mark.parametrize("category,color", [("Particles", "'#E67E22'"), ("Views", "'#34568B'")])
def test_particles_and_views_have_real_colors(category, color):
    text = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = text.index("var categoryColors = {")
    end = text.index("};", start)
    assert f"'{category}': {color}" in text[start:end]


def test_no_action_type_carries_particles_or_views_outside_the_known_set():
    """No mapped/hardcoded exclusion needed here (unlike Game) -- every
    action carrying category="Particles"/"Views" genuinely leaks (verified
    against actionToBlockType when this was scoped), so this is a plain
    equality check."""
    from events.action_types import ACTION_TYPES
    still_particles = {name for name, a in ACTION_TYPES.items() if a.category == "Particles"}
    still_views = {name for name, a in ACTION_TYPES.items() if a.category == "Views"}
    assert still_particles == PARTICLES_ACTIONS
    assert still_views == VIEWS_ACTIONS


def test_block_registry_has_particles_and_views_categories():
    from config.blockly_config import BLOCK_REGISTRY
    assert {b["type"] for b in BLOCK_REGISTRY["Particles"]} == PARTICLES_ACTIONS
    assert {b["type"] for b in BLOCK_REGISTRY["Views"]} == VIEWS_ACTIONS


@pytest.mark.parametrize("preset_attr", [
    "get_full", "get_beginner", "get_intermediate", "get_platformer",
    "get_grid_rpg", "get_sokoban", "get_testing", "get_implemented_only",
    "get_code_editor", "get_blockly_editor",
])
def test_no_preset_shows_particles_or_views_blocks_without_enabling_the_category(preset_attr):
    """The same regression class the Game fix almost shipped: promoting a
    stray category to a real one gates it on enabled_categories, which 7
    of the 10 presets did not have for "Particles"/"Views" until this fix."""
    from config.blockly_config import BlocklyConfig
    config = getattr(BlocklyConfig, preset_attr)()
    if PARTICLES_ACTIONS & config.enabled_blocks:
        assert "Particles" in config.enabled_categories, preset_attr
    if VIEWS_ACTIONS & config.enabled_blocks:
        assert "Views" in config.enabled_categories, preset_attr


def test_config_version_bumped_for_the_particles_views_migration():
    from config.blockly_config import BlocklyConfig
    assert BlocklyConfig().config_version >= 4


def test_particles_already_has_real_translations_in_every_language():
    """Unexpected find while writing this test: "Particles" already had a
    real translation entry in all 7 languages in config/blockly_translations
    .py's CATEGORY_TRANSLATIONS -- leftover from before this category was
    ever wired up to the real toolbox. A pleasant bonus, not something
    this fix added; get_translated_category (used by the config dialog)
    picks it up automatically now that "Particles" is a real BLOCK_REGISTRY
    key."""
    from config.blockly_translations import CATEGORY_TRANSLATIONS, get_translated_category
    for lang in CATEGORY_TRANSLATIONS:
        assert "Particles" in CATEGORY_TRANSLATIONS[lang], lang
    assert get_translated_category("Particles", "fr") == "Particules"


def test_control_game_views_now_have_real_category_translations():
    """Superseded 2026-10-18 (docs/BLOCKLY_CONFIG_DIALOG_I18N_2026-10-18.md):
    this test used to assert the OPPOSITE -- that "Views" (and, by the same
    part-2 decision, "Game"/"Control") were DELIBERATELY left untranslated
    in the Configure Action Blocks dialog. That decision is reversed: a user
    reported the dialog showing "Control"/"Set Variable" in English in a
    non-English IDE, and investigating showed the gap was much wider than
    those two labels -- 3 whole categories (Control/Game/Views) had NO
    translation at all, category label included. All 3 are now translated
    in all 7 languages; see get_translated_category."""
    from config.blockly_translations import CATEGORY_TRANSLATIONS, get_translated_category
    for lang, table in CATEGORY_TRANSLATIONS.items():
        assert "Control" in table, lang
        assert "Game" in table, lang
        assert "Views" in table, lang
    assert get_translated_category("Control", "fr") == "Contrôle"
    assert get_translated_category("Game", "fr") == "Jeu"
    assert get_translated_category("Views", "fr") == "Vues"
