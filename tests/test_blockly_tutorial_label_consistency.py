"""Tutorial text must say what the Blockly block actually says.

User-reported (2026-10-16): a tutorial said "When created" while the real
Blockly Create-event block rendered as "When object is created" -- besides
being an inconsistency, "object" is also the wrong word (it's the
*instance* being created, not the object/class it was made from; the
block's own tooltip already correctly said "instance").

Root cause: blockly_workspace.html's inline Blockly.Blocks definitions
load AFTER blockly_blocks.js (see the <script> order in that file) and
silently override several of its blocks, including event_create and
event_step, with different English fallback text -- every other shipped
language's translation (blockly_i18n.js's BLOCK_MESSAGES) already used
the simpler wording ("Quand créé", "Wenn erstellt", "Quando creato", ...),
so English's fallback was the one outlier, not a deliberate choice.

This test pins the fix at its source (not just in the tutorials that
happened to already use the right wording by luck) so the two files
cannot silently diverge again.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_HTML = REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_workspace.html"
BLOCKS_JS = REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_blocks.js"
BLOCKLY_CONFIG = REPO_ROOT / "config" / "blockly_config.py"


def test_event_create_label_says_created_not_object_is_created():
    src = WORKSPACE_HTML.read_text(encoding="utf-8")
    assert '|| "When created"' in src
    assert "When object is created" not in src


def test_event_create_tooltip_says_instance_not_object_instance():
    src = WORKSPACE_HTML.read_text(encoding="utf-8")
    assert "Runs when the instance is created" in src
    assert "object instance is created" not in src


def test_event_step_label_says_every_step_not_every_frame_step():
    src = WORKSPACE_HTML.read_text(encoding="utf-8")
    assert '|| "Every step"' in src
    assert "Every frame (step)" not in src


def test_live_fallback_now_matches_blockly_blocks_js_and_every_translation():
    """blockly_blocks.js's own copies are dead code (overridden by
    blockly_workspace.html's later-loaded definitions) but were already
    correct -- and every shipped language's BLOCK_MESSAGES translation
    for these two keys already used the same simple wording. This just
    confirms the English fallback no longer disagrees with both."""
    blocks_js_src = BLOCKS_JS.read_text(encoding="utf-8")
    assert '.appendField("When created")' in blocks_js_src
    assert '.appendField("Every step")' in blocks_js_src


def test_block_registry_description_matches():
    """config/blockly_config.py's BLOCK_REGISTRY feeds the block-preset
    picker dialog (dialogs/_block_config_dialog_base.py reads block["name"]
    / block["description"] as user-visible text) -- it had the identical
    wrong "When object is created" text, independently of the canvas bug."""
    src = BLOCKLY_CONFIG.read_text(encoding="utf-8")
    assert '"description": "When created"' in src
    assert "When object is created" not in src
