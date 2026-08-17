#!/usr/bin/env python3
"""Resolve `<param>_translations` dicts at EXPORT time.

The IDE lets an author attach translations to any string action parameter,
stored beside it as `<param>_translations = {lang: text}` (see
`events/action_editor.py`). The desktop runtime honours those at play time
(`ActionExecutor.localize_param`).

**The export engines do not, and deliberately are not being taught to.**
`engine.js`'s `show_message` reads `params.message` only, and `export/Kivy/`
has no notion of translations at all. Rather than add the same feature to two
more hand-written engines -- and then keep three copies honest -- the exporter
resolves the translation *into* the plain parameter and drops the dict. The
exported game then contains ordinary strings in one language and cannot
possibly disagree with the desktop about what they say.

That also answers the objection recorded in
`tests/test_raycast_2_sample.py`: translating a sample used to mean it
"behaves differently on every export target", which was true while the
targets ignored the dicts. Resolving at export time is what makes it false.

Nothing here is raycast- or sample-specific: it is a generic walk over
whatever the project happens to contain.
"""
from typing import Any

TRANSLATIONS_SUFFIX = "_translations"


def resolve_translations(node: Any, language: str) -> Any:
    """Return a copy of `node` with every translation dict resolved.

    For each `<param>_translations` mapping found anywhere in the structure:
    replace `<param>` with the entry for `language` when there is a non-empty
    one, and drop the `_translations` key either way.

    `language` of "en" (or empty) resolves nothing but still strips the dicts,
    so an English export carries no dead weight and every target sees the same
    shape of data. This mirrors the runtime's rule that the base value *is*
    the English string, so an `en` entry is redundant.
    """
    if isinstance(node, list):
        return [resolve_translations(item, language) for item in node]
    if not isinstance(node, dict):
        return node

    out = {}
    for key, value in node.items():
        if key.endswith(TRANSLATIONS_SUFFIX) and isinstance(value, dict):
            continue                     # dropped; applied to its base below
        out[key] = resolve_translations(value, language)

    lang = (language or "en").strip()
    for key, value in node.items():
        if not key.endswith(TRANSLATIONS_SUFFIX) or not isinstance(value, dict):
            continue
        base = key[:-len(TRANSLATIONS_SUFFIX)]
        if not base:
            continue
        if lang and lang != "en":
            translated = value.get(lang)
            if translated:               # empty string keeps the English
                out[base] = translated
    return out


def count_translation_dicts(node: Any) -> int:
    """How many translation dicts `node` still contains.

    Used by the exporters to log what they resolved, and by tests to assert
    that an exported project carries none -- a leftover dict would mean some
    string silently stayed English on that target.
    """
    if isinstance(node, list):
        return sum(count_translation_dicts(i) for i in node)
    if not isinstance(node, dict):
        return 0
    total = sum(1 for k, v in node.items()
                if k.endswith(TRANSLATIONS_SUFFIX) and isinstance(v, dict))
    return total + sum(count_translation_dicts(v) for v in node.values())
