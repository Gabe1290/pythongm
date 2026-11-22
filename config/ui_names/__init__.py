"""Translated names for the core actions, events, parameters, choices and categories
(docs/CORE_NAMES_I18N_PLAN.md).

One module per language (``<lang>.py``) holding ``NAMES = {kind: {key: text}}``. Actions and events
are keyed by their KEY (``set_hspeed``), because two actions can share an English name; parameters,
choices and categories by their English text. Kinds all start with ``core.`` so they never mix with
an extension's own table (Thymio's ``action`` kind is keyed by English name).

``core.ui_names`` loads these on first use; ``tools/action_ref_i18n.py`` builds the wiki's tables
from them, so the editor and the wiki use one vocabulary.
"""
from typing import Dict

# Plain imports, not importlib: a frozen build (PyInstaller / Nuitka) only bundles modules it can
# see being imported. Add a language here when its module exists.
from . import de, es, fr, it, pt, ru, sl, uk

_MODULES = {"fr": fr, "de": de, "es": es, "it": it, "pt": pt, "ru": ru, "sl": sl, "uk": uk}
LANGUAGES = tuple(_MODULES)


def language_table(lang: str) -> Dict[str, Dict[str, str]]:
    """``{kind: {key: text}}`` for one language; empty when the language has no module yet."""
    module = _MODULES.get(lang)
    return getattr(module, "NAMES", {}) if module else {}


def all_tables() -> Dict[str, Dict[str, Dict[str, str]]]:
    """Every language, shaped for ``core.ui_names.register_ui_translations``: ``{kind: {key: {lang: text}}}``."""
    merged: Dict[str, Dict[str, Dict[str, str]]] = {}
    for lang in LANGUAGES:
        for kind, entries in language_table(lang).items():
            table = merged.setdefault(kind, {})
            for key, text in entries.items():
                table.setdefault(key, {})[lang] = text
    return merged
