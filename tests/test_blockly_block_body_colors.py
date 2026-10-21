"""Hand-written Blockly block bodies now match their Scratch-sized toolbox
group's color -- the follow-up flagged (not silently skipped) when
docs/BLOCKLY_SCRATCH_PARITY_PLAN.md Feature 1 shipped: each of the ~115
block definitions in blockly_blocks.js sets its own color independently of
the toolbox category dict, and those colors didn't even match the OLD
per-category toolbox colors either, so the two were already visually
inconsistent before this fix.

Scope: the 73 CORE (non-Thymio) blocks only, matching the plan's own
"redesigning the Thymio extension's own category set is out of scope"
call -- Thymio's ~42 blocks keep their own, untouched colors.

No Node.js in CI, so this is a structural/source check (parses each
Blockly.Blocks['name'] = {...} span and its own setColour(...) call),
cross-referenced against the same category->group mapping
tests/test_blockly_toolbox_category_groups.py already verifies.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BLOCKS_JS = (REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_blocks.js")
WORKSPACE_HTML = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
                   "blockly_workspace.html")

GROUP_COLORS = {
    "Motion": "#4C97FF",
    "Looks": "#9966FF",
    "Sound": "#CF63CF",
    "Events": "#FFBF00",
    "Control": "#FFAB19",
    "Sensing": "#5CB1D6",
    "Operators": "#59C059",
    "Variables": "#FF8C1A",
}

# category -> block types, from blockly_workspace.html's hardcoded
# `categories` dict (the live toolbox's own source of truth for which
# category a hand-written block belongs to).
_LEGACY_SOUND_BLOCKS = {"music_play", "music_stop", "sound_play"}


def _category_of_block():
    src = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = src.index("function generateToolboxXml(config) {")
    end = src.index("function extractBlockType(blockXml) {")
    body = src[start:end]
    cat_start = body.index("var categories = {")
    cat_end = body.index("};", cat_start)
    cat_blob = body[cat_start:cat_end]

    category_of = {}
    for m in re.finditer(
        r"'([A-Za-z/ ]+)':\s*\{\s*color:\s*'(#[0-9A-Fa-f]+)',\s*blocks:\s*\[(.*?)\]\s*\}\s*,",
        cat_blob, re.S
    ):
        cat, blocks_blob = m.group(1), m.group(3)
        for block_type in re.findall(r'type="([a-zA-Z0-9_]+)"', blocks_blob):
            if block_type in ("math_number", "text", "logic_compare"):
                continue
            category_of[block_type] = cat
    for name in _LEGACY_SOUND_BLOCKS:
        category_of[name] = "Sound"
    return category_of


def _group_of_block():
    from config.blockly_config import TOOLBOX_CATEGORY_GROUPS
    cat_to_group = {
        member: group
        for group, members in TOOLBOX_CATEGORY_GROUPS.items()
        for member in members
    }
    category_of = _category_of_block()
    return {block: cat_to_group[cat] for block, cat in category_of.items()
            if cat in cat_to_group}


def _block_body_colors():
    """{block_type: colour} for the FIRST setColour(...) call inside each
    Blockly.Blocks['name'] = {...} span (one per block, scoped so a later
    block's color can never be misattributed to an earlier one)."""
    src = BLOCKS_JS.read_text(encoding="utf-8")
    starts = [
        (m.start(), m.group(1))
        for m in re.finditer(r"Blockly\.Blocks\['([a-zA-Z0-9_]+)'\]\s*=\s*\{", src)
    ]
    colors = {}
    for i, (pos, name) in enumerate(starts):
        span_end = starts[i + 1][0] if i + 1 < len(starts) else len(src)
        span = src[pos:span_end]
        m = re.search(r'setColour\("(#[0-9A-Fa-f]+)"\)', span)
        if m and name not in colors:
            colors[name] = m.group(1)
    return colors


def _core_blocks():
    return [b for b in _block_body_colors()
            if not b.startswith("thymio_") and not b.startswith("event_thymio_")]


def test_every_core_block_is_mapped_to_a_group():
    """A core block with no category/group mapping would silently keep
    its stale color forever -- this would have caught the gap before the
    recolor shipped."""
    group_of = _group_of_block()
    unmapped = [b for b in _core_blocks() if b not in group_of]
    assert unmapped == [], f"core blocks with no group mapping: {unmapped}"


@pytest.mark.parametrize("block_type,expected_group", [
    ("event_create", "Events"), ("event_step", "Events"),
    ("move_set_hspeed", "Motion"), ("wrap_around_room", "Motion"),
    ("draw_text", "Looks"), ("execute_code", "Looks"), ("output_message", "Looks"),
    ("score_set", "Variables"), ("health_add", "Variables"),
    ("instance_destroy", "Sensing"), ("if_can_push", "Sensing"),
    ("if_condition", "Control"), ("set_alarm", "Control"), ("room_goto", "Control"),
    ("value_x", "Operators"),
    ("sound_play", "Sound"), ("music_play", "Sound"), ("music_stop", "Sound"),
])
def test_sample_blocks_land_in_the_expected_group(block_type, expected_group):
    assert _group_of_block()[block_type] == expected_group


def test_every_core_blocks_body_colour_matches_its_group_colour():
    colors = _block_body_colors()
    group_of = _group_of_block()
    mismatches = []
    for block in _core_blocks():
        group = group_of.get(block)
        if group is None:
            continue  # covered by test_every_core_block_is_mapped_to_a_group
        expected = GROUP_COLORS[group]
        actual = colors[block]
        if actual != expected:
            mismatches.append((block, group, actual, expected))
    assert mismatches == [], mismatches


def test_thymio_blocks_were_left_untouched():
    """Confirms the recolor was scoped correctly -- Thymio's own block
    colors (a separate, untouched category set) are unaffected, including
    the two colors (#FF6B6B, #9B59B6) that happen to collide with core
    blocks' OLD colors, the exact case a blind find-and-replace across
    the whole file would have gotten wrong."""
    colors = _block_body_colors()
    thymio_colors = {b: c for b, c in colors.items()
                      if b.startswith("thymio_") or b.startswith("event_thymio_")}
    assert thymio_colors, "no Thymio blocks found -- test itself is broken"
    assert not (set(thymio_colors.values()) - {
        "#27AE60", "#2ECC71", "#3498DB", "#9B59B6", "#E67E22", "#F1C40F", "#FF6B6B",
    }), "a Thymio block's color changed -- the core recolor leaked into Thymio blocks"


def test_no_core_block_still_carries_a_pre_recolor_colour():
    """None of the 12 old per-fine-category hex values (confirmed, before
    this fix, to not even match the old toolbox category colors) should
    remain on any core block."""
    old_colors = {
        "#4A90D9", "#5C68A6", "#5C81A6", "#5CA65C", "#745CA6", "#9966FF",
        "#9B59B6", "#A65C81", "#A6745C", "#FF6B6B", "#FFAB19", "#FFD500",
    }
    colors = _block_body_colors()
    for block in _core_blocks():
        color = colors[block]
        # #9B59B6 and #FFAB19 happen to also be real NEW group colors
        # (Looks was never #9B59B6 -> wait, #9B59B6 is an OLD Drawing
        # color and is NOT reused as any new group color; #FFAB19 IS
        # reused unchanged as the new Control color, since Control's own
        # color didn't need to change) -- only flag a color as "stale"
        # if it's an old value NOT equal to this block's own correct new
        # target, so Control's legitimately-unchanged #FFAB19 isn't a
        # false positive.
        if color in old_colors and color != GROUP_COLORS.get(_group_of_block()[block]):
            pytest.fail(f"{block} still has an old, non-matching color: {color}")
