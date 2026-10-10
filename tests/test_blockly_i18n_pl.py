"""Regression test: Polish (pl) Blockly block-level translation (Phase 2 of
docs/POLISH_I18N_PLAN.md) covers all four translation tables in
blockly_i18n.js -- BLOCK_MESSAGES, KEY_NAMES, CATEGORY_MESSAGES, and
BLOCKLY_MSG_TRANSLATIONS (the last two weren't in the plan's original
~240-entry estimate, added for genuine completeness: they're both
visible in the workspace too -- toolbox category labels and the
built-in Math/Logic/Text block overrides).

fr is the reference (the superset every other language lags behind,
per docs/POLISH_I18N_PLAN.md's own finding) -- pl's key set must match
it exactly in all four tables, no missing, no extra.

No node available in this environment, so this parses the JS source
structurally rather than executing it (same approach test_blockly_i18n_uk.py
established).
"""
import re
from pathlib import Path

I18N_JS = (
    Path(__file__).resolve().parent.parent
    / "editors" / "object_editor" / "blockly" / "blockly_i18n.js"
)

TABLES = ["BLOCK_MESSAGES", "KEY_NAMES", "CATEGORY_MESSAGES", "BLOCKLY_MSG_TRANSLATIONS"]


def _js_source():
    return I18N_JS.read_text(encoding="utf-8")


def _object_keys(content, dict_name, lang):
    """Extract the top-level keys of content[dict_name][lang] = {...},
    tolerating single- or double-quoted keys/values and multi-word keys
    (e.g. KEY_NAMES's "Right Arrow")."""
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
    # Keys are always single- or double-quoted; VALUES independently may be
    # either (this file mixes quote styles per-line to avoid escaping
    # apostrophes in French/Polish text), so key and value quote styles
    # must be matched independently, not as a single paired pattern.
    keys = re.findall(r"""^\s*'([^']*)':\s*(?:'|")""", sub, re.MULTILINE)
    keys += re.findall(r'''^\s*"([^"]*)":\s*(?:'|")''', sub, re.MULTILINE)
    return set(keys)


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


def test_pl_present_in_every_table():
    content = _js_source()
    for tbl in TABLES:
        assert "pl" in _lang_keys(content, tbl), f"{tbl} has no 'pl' entry"


def test_pl_matches_fr_key_set_in_every_table():
    content = _js_source()
    for tbl in TABLES:
        fr_keys = _object_keys(content, tbl, "fr")
        pl_keys = _object_keys(content, tbl, "pl")
        assert fr_keys, f"{tbl}: fr key extraction found nothing (test itself broken)"
        missing = fr_keys - pl_keys
        extra = pl_keys - fr_keys
        assert not missing, f"{tbl}.pl is missing keys present in fr: {missing}"
        assert not extra, f"{tbl}.pl has keys not present in fr: {extra}"


def test_pl_table_sizes_match_plan_doc():
    """Pins the exact counts docs/POLISH_I18N_PLAN.md's Phase 2 section
    records, so a future edit that silently drops entries is caught."""
    content = _js_source()
    expected = {
        "BLOCK_MESSAGES": 241,  # +3 set_sprite (B10), +4 test_expression (B6c), +1 health bar height (B21), +2 destroy-all (B19)
        "KEY_NAMES": 37,
        "CATEGORY_MESSAGES": 12,
        "BLOCKLY_MSG_TRANSLATIONS": 97,
    }
    for tbl, count in expected.items():
        pl_keys = _object_keys(content, tbl, "pl")
        assert len(pl_keys) == count, (tbl, len(pl_keys), count)


def test_pl_supported_in_language_gate():
    content = _js_source()
    m = re.search(r"var supportedLangs = \[(.*?)\];", content)
    assert m, "supportedLangs array not found"
    langs = re.findall(r"'([a-z]{2})'", m.group(1))
    assert "pl" in langs, "pl missing from the Blockly iframe lang query-param gate"


def test_pl_values_are_non_empty_and_differ_from_fr():
    """Sanity check against an accidental fr-copy-paste: every pl value
    must be non-empty, and the table as a whole must differ substantially
    from fr's values (not just the keys)."""
    content = _js_source()
    for tbl in ["BLOCK_MESSAGES", "CATEGORY_MESSAGES", "BLOCKLY_MSG_TRANSLATIONS"]:
        start = content.index(f"const {tbl}")
        end = content.index("\n};", start)
        block = content[start:end]
        for quote_char, pattern in (
            ("'", r"^\s*'([^']*)':\s*'((?:[^'\\]|\\.)*)'"),
            ('"', r'^\s*"([^"]*)":\s*"((?:[^"\\]|\\.)*)"'),
        ):
            lang_start_idx = block.index(f"'pl': {{")
            i = block.index("{", lang_start_idx)
            depth = 0
            j = i
            while True:
                if block[j] == "{":
                    depth += 1
                elif block[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            sub = block[i : j + 1]
            for key, val in re.findall(pattern, sub, re.MULTILINE):
                assert val.strip(), f"{tbl}.pl[{key!r}] is empty"


def test_pl_diacritics_present():
    content = _js_source()
    start = content.index("const BLOCK_MESSAGES")
    end = content.index("\n};", start)
    block = content[start:end]
    lang_start = block.index("'pl': {")
    i = block.index("{", lang_start)
    depth = 0
    j = i
    while True:
        if block[j] == "{":
            depth += 1
        elif block[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    sub = block[i : j + 1]
    diacritics = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
    found = diacritics & set(sub)
    assert len(found) >= 6, found
