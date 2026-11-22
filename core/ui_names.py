"""Translated names for things that are DATA, not literal strings: action, event, parameter and
category names (docs/THYMIO_PANEL_I18N_PLAN.md, U1).

``self.tr(display_name)`` only works when a .ts catalogue happens to hold that exact text in the
displaying class's context, which it mostly does not (measured 2026-11-22: the Standard events panel
translates 49 of 186 action names in French). Extensions supply tables instead, as
``PLUGIN_UI_TRANSLATIONS = {kind: {english: {lang: text}}}``; the plugin loader registers them here.

Kinds in use: ``action``, ``action_description``, ``param``, ``param_description``, ``choice``,
``event``, ``event_description``, ``category`` (extensions, English-keyed), and the ``core.*`` kinds
of ``config/ui_names`` (docs/CORE_NAMES_I18N_PLAN.md), loaded on first lookup. Qt-free; the current
language comes from the LanguageManager unless given.
"""
from typing import Dict, Optional

_TABLES: Dict[str, Dict[str, Dict[str, str]]] = {}
_CORE_LOADED = False


def _ensure_core() -> None:
    """Register config/ui_names once (the core tables), before the first lookup."""
    global _CORE_LOADED
    if _CORE_LOADED:
        return
    _CORE_LOADED = True
    try:
        from config.ui_names import all_tables
    except ImportError:
        return
    register_ui_translations(all_tables())


def register_ui_translations(mapping) -> int:
    """Merge ``{kind: {english: {lang: text}}}``. Later registrations add languages to an existing entry."""
    count = 0
    for kind, entries in (mapping or {}).items():
        table = _TABLES.setdefault(kind, {})
        for english, per_lang in (entries or {}).items():
            table.setdefault(english, {}).update(per_lang or {})
            count += 1
    return count


def _current_language() -> str:
    try:
        from core.language_manager import get_language_manager
        return get_language_manager().get_current_language() or "en"
    except Exception:
        return "en"


def ui_name(kind: str, english, lang: Optional[str] = None):
    """``english`` in the IDE language (or ``lang``), or ``english`` itself when there is no translation."""
    if not isinstance(english, str) or not english:
        return english
    lang = lang or _current_language()
    if lang == "en":
        return english
    _ensure_core()
    return _TABLES.get(kind, {}).get(english, {}).get(lang) or english


def clear_ui_translations() -> None:
    """For tests. The core tables load again on the next lookup."""
    global _CORE_LOADED
    _TABLES.clear()
    _CORE_LOADED = False
