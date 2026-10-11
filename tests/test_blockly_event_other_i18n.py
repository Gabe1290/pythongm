"""Regression test: the Blockly `event_other` block ("Other event:") had its
dropdown options (Game Start, Outside Room, ...) hardcoded in English with no
translation at all, unlike the block's own prefix/tooltip text which already
went through getBlockMessage() -- a real classroom report (French user,
Tutorial 15 "Fruit Fusion", 2026-10-11): the dropdown stayed English even with
the IDE set to French.

Mirrors the structural-parsing approach of test_blockly_i18n_pl.py /
test_blockly_i18n_uk.py (no node available in this environment).
"""
import re
from pathlib import Path

I18N_JS = (
    Path(__file__).resolve().parent.parent
    / "editors" / "object_editor" / "blockly" / "blockly_i18n.js"
)
WORKSPACE_HTML = (
    Path(__file__).resolve().parent.parent
    / "editors" / "object_editor" / "blockly" / "blockly_workspace.html"
)

LANGS = ["fr", "pl", "de", "it", "uk"]  # the languages BLOCK_MESSAGES supports
EVENT_NAMES = [
    "game_start", "game_end", "room_start", "room_end", "begin_step",
    "end_step", "draw_gui", "outside_room", "intersect_boundary",
    "no_more_lives", "no_more_health", "animation_end",
]


def _object_keys(content, dict_name, lang):
    start = content.index(f"const {dict_name}")
    end = content.index("\n};", start)
    block = content[start:end]
    lang_start = block.index(f"'{lang}': {{")
    i = block.index("{", lang_start)
    start_i = i
    depth = 0
    while True:
        if block[i] == "{":
            depth += 1
        elif block[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    sub = block[start_i : i + 1]
    keys = re.findall(r"""^\s*'([^']*)':\s*(?:'|")""", sub, re.MULTILINE)
    keys += re.findall(r'''^\s*"([^"]*)":\s*(?:'|")''', sub, re.MULTILINE)
    return set(keys)


def test_every_language_has_prefix_and_tooltip():
    content = I18N_JS.read_text(encoding="utf-8")
    for lang in LANGS:
        keys = _object_keys(content, "BLOCK_MESSAGES", lang)
        assert "event_other_prefix" in keys, f"{lang} missing event_other_prefix"
        assert "event_other_tooltip" in keys, f"{lang} missing event_other_tooltip"


def test_every_language_has_all_twelve_dropdown_options():
    content = I18N_JS.read_text(encoding="utf-8")
    for lang in LANGS:
        keys = _object_keys(content, "BLOCK_MESSAGES", lang)
        for name in EVENT_NAMES:
            key = f"event_other_opt_{name}"
            assert key in keys, f"{lang} missing {key}"


def test_no_language_has_an_empty_translation():
    """Catches a key present with an accidental empty string value, which
    the key-set check above wouldn't notice."""
    content = I18N_JS.read_text(encoding="utf-8")
    for lang in LANGS:
        start = content.index(f"const BLOCK_MESSAGES")
        end = content.index("\n};", start)
        block = content[start:end]
        lang_start = block.index(f"'{lang}': {{")
        i = block.index("{", lang_start)
        depth = 0
        start_i = i
        while True:
            if block[i] == "{":
                depth += 1
            elif block[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        sub = block[start_i : i + 1]
        for name in EVENT_NAMES:
            m = re.search(
                rf"""'event_other_opt_{name}':\s*(['"])(.*?)\1,""", sub
            )
            assert m, f"{lang}: event_other_opt_{name} not parseable"
            assert m.group(2).strip(), f"{lang}: event_other_opt_{name} is empty"


def test_dropdown_values_are_the_literal_event_names():
    """The VALUE half of each dropdown pair must stay the untranslated
    event name (it's what getEventType()/createEventBlock round-trip on) --
    only the LABEL half may be translated."""
    html = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = html.index("Blockly.Blocks['event_other']")
    end = html.index("};", start)
    block = html[start:end]
    for name in EVENT_NAMES:
        assert f'"{name}"]' in block, (
            f"event_other's option list no longer carries the literal value {name!r}"
        )


def test_block_definition_resolves_labels_through_get_block_message():
    """Mutation guard: the init() function must actually call
    getBlockMessage('event_other_opt_' + ..., lang) per option, not just
    have translations sitting unused in blockly_i18n.js."""
    html = WORKSPACE_HTML.read_text(encoding="utf-8")
    start = html.index("Blockly.Blocks['event_other']")
    end = html.index("};", start)
    block = html[start:end]
    assert "getBlockMessage('event_other_opt_' + opt[1], lang)" in block
    assert "getBlockMessage('event_other_prefix', lang)" in block
    assert "getBlockMessage('event_other_tooltip', lang)" in block
