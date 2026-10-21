"""Blockly toolbox category consolidation (docs/BLOCKLY_SCRATCH_PARITY_PLAN.md
Feature 1): collapse the 13 fine-grained BLOCK_REGISTRY categories into a
Scratch-sized set (Motion/Looks/Sound/Events/Control/Sensing/Operators/
Variables) for the toolbox display only.

Design, confirmed by reading the code before writing these tests: category
identity stays fine-grained everywhere EXCEPT the toolbox-rendering layer
-- BlocklyConfig presets' enabled_categories, action_types.py's category=
strings, and BLOCK_REGISTRY itself are all untouched. Only
config/blockly_config.py's new TOOLBOX_CATEGORY_GROUPS/display_category()
(Python, mostly documentation/testing -- the live toolbox never calls
into Python for this) and blockly_workspace.html's hand-mirrored copy
(JS, the one actually consulted by generateToolboxXml) changed.

No Node.js in CI, so the JS side is verified structurally (source
assertions, matching this repo's established tier for this exact
function -- see tests/test_blockly_toolbox_js_filter.py) plus a drift
test comparing the two hand-written copies of the mapping.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_HTML = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
                   "blockly_workspace.html")
I18N_JS = (REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_i18n.js")

EXPECTED_GROUPS = {
    "Motion": {"Movement", "Views"},
    "Looks": {"Drawing", "Particles"},
    "Sound": {"Sound"},
    "Events": {"Events"},
    "Control": {"Control", "Timing", "Room", "Game"},
    "Sensing": {"Instance"},
    "Operators": {"Values"},
    "Variables": {"Score/Lives/Health"},
}


# ---------------------------------------------------------------------------
# Python side
# ---------------------------------------------------------------------------

def test_python_mapping_matches_expected_groups():
    from config.blockly_config import TOOLBOX_CATEGORY_GROUPS
    actual = {group: set(members) for group, members in TOOLBOX_CATEGORY_GROUPS.items()}
    assert actual == EXPECTED_GROUPS


def test_every_block_registry_category_is_covered_exactly_once():
    """The completeness guard the plan doc calls for: every CORE
    BLOCK_REGISTRY category lands in exactly one display group -- a
    category silently falling through unmapped would mean it vanishes
    from the toolbox the moment the grouped emission ships (an unmapped
    category still renders today, as its OWN standalone category, but
    after this change every core category must be claimed by a group;
    only an extension's own, added later via register_block_categories,
    should still fall through).

    BLOCK_REGISTRY is a shared, mutable, process-global dict --
    register_block_categories() (Thymio's own extension-load path, and
    any other extension's) can have already merged in extra categories
    by the time this test runs, depending on full-suite test order. So
    this checks against the fixed, hardcoded set of the 13 categories
    this feature was actually scoped against, not whatever
    BLOCK_REGISTRY.keys() happens to currently contain -- the live
    registry is only asserted to be a SUPERSET of that fixed set (every
    core category must still exist), not equal to it."""
    from config.blockly_config import BLOCK_REGISTRY, TOOLBOX_CATEGORY_GROUPS
    core_categories = {
        "Events", "Control", "Movement", "Timing", "Drawing",
        "Score/Lives/Health", "Instance", "Room", "Values", "Sound",
        "Game", "Particles", "Views",
    }
    assert core_categories <= set(BLOCK_REGISTRY.keys()), (
        "a core category went missing from BLOCK_REGISTRY entirely")
    all_mapped = {c for members in TOOLBOX_CATEGORY_GROUPS.values() for c in members}
    assert core_categories == all_mapped, (
        set(core_categories) ^ all_mapped)


@pytest.mark.parametrize("category,expected_group", [
    ("Movement", "Motion"), ("Views", "Motion"),
    ("Drawing", "Looks"), ("Particles", "Looks"),
    ("Sound", "Sound"),
    ("Events", "Events"),
    ("Control", "Control"), ("Timing", "Control"), ("Room", "Control"), ("Game", "Control"),
    ("Instance", "Sensing"),
    ("Values", "Operators"),
    ("Score/Lives/Health", "Variables"),
])
def test_display_category_resolves_each_fine_category(category, expected_group):
    from config.blockly_config import display_category
    assert display_category(category) == expected_group


def test_score_lives_health_lands_in_variables():
    """Explicit pin for the user's own stated choice (not the author's
    default proposal) during plan review: Score/Lives/Health merges into
    Variables rather than staying its own category."""
    from config.blockly_config import display_category
    assert display_category("Score/Lives/Health") == "Variables"


def test_unmapped_category_falls_through_to_itself():
    """An extension's own category (e.g. a future Thymio-style one, or
    simply a category nobody has sorted into a group yet) must not raise
    or silently disappear -- it keeps rendering as its own standalone
    toolbox category, unchanged from pre-consolidation behaviour."""
    from config.blockly_config import display_category
    assert display_category("Thymio Movement") == "Thymio Movement"
    assert display_category("Some Future Category") == "Some Future Category"


# ---------------------------------------------------------------------------
# JS side -- structural (no Node.js in CI)
# ---------------------------------------------------------------------------

def _js_source():
    return WORKSPACE_HTML.read_text(encoding="utf-8")


def _js_toolbox_category_groups():
    """Parse the hand-mirrored JS copy of TOOLBOX_CATEGORY_GROUPS into the
    same {group: set(members)} shape the Python test above checks, so the
    two copies can be compared directly."""
    src = _js_source()
    start = src.index("var TOOLBOX_CATEGORY_GROUPS = {")
    end = src.index("\n        };", start)
    blob = src[start:end]
    groups = {}
    for match in re.finditer(r"'([A-Za-z ]+)':\s*\[([^\]]*)\]", blob):
        group_name = match.group(1)
        members = re.findall(r"'([A-Za-z/ ]+)'", match.group(2))
        groups[group_name] = set(members)
    return groups


def test_js_mapping_matches_python_mapping():
    """Drift guard: the two hand-written copies (Python is the canonical
    definition; JS is what the live toolbox actually consults, since
    generateToolboxXml runs entirely client-side) must stay identical."""
    from config.blockly_config import TOOLBOX_CATEGORY_GROUPS
    py_mapping = {group: set(members) for group, members in TOOLBOX_CATEGORY_GROUPS.items()}
    js_mapping = _js_toolbox_category_groups()
    # JS additionally folds 'Audio' into Sound and 'Math'/'Logic'/'Text'
    # into Operators -- both are JS-only concepts (the always-on built-in
    # categories, and the plugin-sourced dynamic "Audio" category string)
    # that have no Python BLOCK_REGISTRY entry to mirror, so they're
    # expected extras, not a drift bug.
    js_mapping["Sound"].discard("Audio")
    js_mapping["Operators"] -= {"Math", "Logic", "Text"}
    assert js_mapping == py_mapping


def test_toolbox_group_colors_cover_every_group():
    src = _js_source()
    start = src.index("var TOOLBOX_GROUP_COLORS = {")
    end = src.index("\n        };", start)
    blob = src[start:end]
    colors = dict(re.findall(r"'([A-Za-z ]+)':\s*'(#[0-9A-Fa-f]{6})'", blob))
    for group in ("Motion", "Looks", "Sound", "Events", "Control",
                   "Sensing", "Operators", "Variables", "My Blocks"):
        assert group in colors, f"{group} has no toolbox colour"


def test_toolbox_group_order_lists_all_eight_core_groups():
    src = _js_source()
    m = re.search(r"var TOOLBOX_GROUP_ORDER = \[(.*?)\];", src, re.S)
    assert m
    order = re.findall(r"'([A-Za-z ]+)'", m.group(1))
    assert order == ["Motion", "Looks", "Sound", "Events", "Control",
                      "Sensing", "Operators", "Variables"]


def test_generate_toolbox_xml_uses_push_to_group_not_direct_emission():
    """The old per-fine-category `xml += '<category name="' + categoryName
    ...` emission is gone from the main loop -- blocks are pooled via
    pushToGroup and only emitted once, grouped, at the end."""
    src = _js_source()
    start = src.index("function generateToolboxXml(config) {")
    end = src.index("function extractBlockType(blockXml) {")
    body = src[start:end]
    assert "pushToGroup(categoryName, categoryBlocks);" in body
    assert "pushToGroup(customName, filteredBlocks);" in body
    assert "function emitGroup(groupName)" in body
    # The grouped emission is the ONLY place a <category> tag is built in
    # the live (dynamic) toolbox path.
    assert body.count("xml += '<category name=") == 1


def test_generated_block_body_colour_prefers_the_group_colour():
    src = _js_source()
    start = src.index("function registerCustomBlocks(actionDefs) {")
    end = src.index("function ", start + 10)
    body = src[start:end]
    assert "TOOLBOX_GROUP_COLORS[toolboxGroupOf(d.category)]" in body


# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------

def _i18n_source():
    return I18N_JS.read_text(encoding="utf-8")


@pytest.mark.parametrize("lang", ["fr", "pl", "de", "it", "uk"])
def test_category_messages_has_all_eight_groups_translated(lang):
    src = _i18n_source()
    start = src.index("const CATEGORY_MESSAGES")
    end = src.index("\n};", start)
    block = src[start:end]
    lang_start = block.index(f"'{lang}': {{")
    lang_end = block.index("}", lang_start)
    lang_block = block[lang_start:lang_end]
    for group in ("Motion", "Looks", "Sound", "Events", "Control",
                   "Sensing", "Operators", "Variables"):
        assert f"'{group}':" in lang_block, f"{lang} missing a translation for {group!r}"


def test_category_messages_no_longer_has_stale_fine_grained_keys():
    """The old fine-grained keys (Movement, Timing, Room, Game, Particles,
    Score/Lives/Health, Instance, Values, Math, Logic, Text) are no longer
    looked up anywhere (getCategoryMessage's only callers pass a group
    name) -- confirms they were replaced, not left alongside the new ones
    as dead weight."""
    src = _i18n_source()
    start = src.index("const CATEGORY_MESSAGES")
    end = src.index("\n};", start)
    block = src[start:end]
    for stale_key in ("'Movement'", "'Timing'", "'Room'", "'Game'",
                       "'Particles'", "'Score/Lives/Health'", "'Instance'",
                       "'Values'", "'Math'", "'Logic'"):
        assert stale_key not in block, f"stale key {stale_key} still present in CATEGORY_MESSAGES"
