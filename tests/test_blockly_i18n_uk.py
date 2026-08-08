"""Regression test: Ukrainian Blockly block-text translations were a complete
BLOCK_MESSAGES set, but pasted under CATEGORY_MESSAGES['uk'] instead of
BLOCK_MESSAGES['uk'] -- getBlockMessage('event_create', 'uk') always fell
through to the English default because BLOCK_MESSAGES had no 'uk' entry at
all, even though a full translated set sat unreachable one object over.
Found while investigating Section L (Tutorials i18n); fixed by relocating
the content. No node available in this environment, so this parses the JS
source structurally rather than executing it (same approach used for the
raycast extension's JS surgery).
"""

import re
from pathlib import Path

I18N_JS = (
    Path(__file__).resolve().parent.parent
    / "editors" / "object_editor" / "blockly" / "blockly_i18n.js"
)


def _js_source():
    return I18N_JS.read_text(encoding="utf-8")


def _object_keys(content, dict_name, lang):
    """Extract the top-level keys of content[dict_name][lang] = {...}."""
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
    return set(re.findall(r"^\s*'([a-zA-Z0-9_/]+)':", sub, re.MULTILINE))


def _lang_keys(content, dict_name):
    start = content.index(f"const {dict_name}")
    end = content.index("\n};", start)
    block = content[start:end]
    return re.findall(r"^    '([a-z]{2})': \{", block, re.MULTILINE)


def test_braces_balance():
    content = _js_source()
    depth = 0
    for ch in content:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        assert depth >= 0, "unbalanced closing brace in blockly_i18n.js"
    assert depth == 0


def test_block_messages_has_ukrainian():
    content = _js_source()
    assert "uk" in _lang_keys(content, "BLOCK_MESSAGES")


def test_block_messages_uk_matches_de_key_set():
    content = _js_source()
    de_keys = _object_keys(content, "BLOCK_MESSAGES", "de")
    uk_keys = _object_keys(content, "BLOCK_MESSAGES", "uk")
    missing = de_keys - uk_keys
    assert not missing, f"BLOCK_MESSAGES.uk is missing keys present in de: {missing}"


def test_block_messages_uk_has_event_create():
    content = _js_source()
    uk_keys = _object_keys(content, "BLOCK_MESSAGES", "uk")
    assert "event_create" in uk_keys
    assert "if_can_push_tooltip" in uk_keys


def test_category_messages_uk_only_has_category_names():
    content = _js_source()
    uk_keys = _object_keys(content, "CATEGORY_MESSAGES", "uk")
    expected = {
        "Events", "Movement", "Timing", "Drawing", "Score/Lives/Health",
        "Instance", "Room", "Values", "Sound", "Output", "Math", "Logic",
    }
    assert uk_keys == expected, (
        "CATEGORY_MESSAGES.uk should hold only the 12 toolbox category "
        f"names, not block-message keys; got {uk_keys}"
    )
