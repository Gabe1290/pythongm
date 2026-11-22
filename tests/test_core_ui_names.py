"""The core name tables (config/ui_names, docs/CORE_NAMES_I18N_PLAN.md).

Guards: every table loads and uses only ``core.*`` kinds; every action/event key names a real action
or event (a renamed action must not leave a dead entry); no language holds a French copy; French
keeps its accents; core.ui_names finds the tables without any registration step.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.ui_names import LANGUAGES, all_tables, language_table  # noqa: E402

KINDS = {"core.action", "core.action_description", "core.param", "core.param_description",
         "core.choice", "core.event", "core.event_description", "core.category"}
PRESENT = [lang for lang in LANGUAGES if language_table(lang)]


@pytest.fixture(scope="module")
def registry(request):
    """Every action and event, with every extension on (this machine's config may disable some)."""
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    plugin_loader.is_extension_enabled = lambda folder, default=True: True
    try:
        plugin_loader.load_all_plugins()
        from events.action_types import ACTION_TYPES
        from events.event_types import EVENT_TYPES
        yield dict(ACTION_TYPES), dict(EVENT_TYPES)
    finally:
        plugin_loader.is_extension_enabled = real
        plugin_loader.load_all_plugins()


def test_the_eight_wiki_languages_are_there():
    assert {"fr", "de", "es", "it", "pt", "ru", "sl", "uk"} <= set(PRESENT)


@pytest.mark.parametrize("lang", PRESENT)
def test_only_core_kinds(lang):
    assert set(language_table(lang)) <= KINDS


@pytest.mark.parametrize("lang", PRESENT)
def test_every_key_is_a_real_action_or_event(lang, registry):
    actions, events = registry
    table = language_table(lang)
    for kind in ("core.action", "core.action_description"):
        dead = [k for k in table.get(kind, {}) if k not in actions]
        assert not dead, (lang, kind, dead)
    for kind in ("core.event", "core.event_description"):
        dead = [k for k in table.get(kind, {}) if k not in events]
        assert not dead, (lang, kind, dead)


# Words that really are the same in French and another language (checked, not copies).
SAME_AS_FRENCH = {("pt", "core.event", "alarm")}   # « Alarme »


@pytest.mark.parametrize("lang", [x for x in PRESENT if x != "fr"])
def test_no_french_copies(lang):
    fr, table = language_table("fr"), language_table(lang)
    copies = [(kind, key) for kind, entries in table.items() for key, text in entries.items()
              if len(text) > 3 and text != key and text == fr.get(kind, {}).get(key)
              and (lang, kind, key) not in SAME_AS_FRENCH]
    assert not copies, copies[:10]


def test_french_keeps_its_accents():
    stripped = re.compile(r"\b(Definir|Creer|Detruire|evenement|ecran|deja|apres|precedent|numero|"
                          r"parametre|systeme|Regler|derniere|premiere|reseau|entree)\b", re.IGNORECASE)
    bad = [text for entries in language_table("fr").values() for text in entries.values()
           if stripped.search(text)]
    assert not bad, bad[:10]


def test_ui_name_finds_the_core_tables():
    from core.ui_names import clear_ui_translations, ui_name
    clear_ui_translations()
    assert ui_name("core.action", "set_hspeed", "fr") == "Définir la vitesse horizontale"
    assert ui_name("core.category", "Movement", "de") == language_table("de")["core.category"]["Movement"]
    assert ui_name("core.action", "set_hspeed", "en") == "set_hspeed"   # English: the caller's fallback


def test_all_tables_is_keyed_kind_key_lang():
    merged = all_tables()
    assert merged["core.action"]["set_hspeed"]["fr"] == "Définir la vitesse horizontale"


# Languages whose table is complete (docs/CORE_NAMES_I18N_PLAN.md U4-U7); grows one language per commit.
COMPLETE = ["fr", "de", "es", "it", "pt", "ru", "sl", "uk", "pl", "ja", "zh"]
# Parameter descriptions are shown only by the wiki's action reference (the editor's dialogs show
# parameter labels, not descriptions), so a language with no wiki edition does not need them.
WIKI_LANGUAGES = {"fr", "de", "es", "it", "pt", "ru", "sl", "uk"}
# Choice values shown as they are in every language (operators, digits, axes, micro:bit buttons).
UNTRANSLATED_CHOICES = {"", "!=", "<", "<=", "==", ">", ">=", "0", "1", "2", "3", "4", "5", "6", "7",
                        "2g", "3g", "6g", "8g", "a", "b", "ab", "x", "y", "z"}


def _wanted(actions, events):
    """Everything the Standard panel and the action dialog can show, by kind (micro:bit, Thymio and the
    network events have their own tables)."""
    want = {kind: set() for kind in KINDS}
    for key, a in actions.items():
        if a.category == "micro:bit":
            continue
        want["core.action"].add(key)
        want["core.category"].add(a.category)
        if a.description:
            want["core.action_description"].add(key)
        for p in a.parameters:
            want["core.param"].add(p.display_name)
            if p.description:
                want["core.param_description"].add(p.description)
            if p.name not in ("then_action", "else_action"):
                want["core.choice"].update(str(c) for c in (p.choices or []) if str(c) not in UNTRANSLATED_CHOICES)
    for key, e in events.items():
        if e.category.startswith(("Thymio", "micro")) or e.category == "Network":
            continue
        want["core.event"].add(key)
        want["core.category"].add(e.category)
        if e.description:
            want["core.event_description"].add(key)
    return want


@pytest.mark.parametrize("lang", COMPLETE)
def test_complete_languages_name_everything(lang, registry):
    table = language_table(lang)
    missing = {kind: sorted(keys - set(table.get(kind, {}))) for kind, keys in _wanted(*registry).items()}
    if lang not in WIKI_LANGUAGES:
        missing.pop("core.param_description", None)
    missing = {kind: keys for kind, keys in missing.items() if keys}
    assert not missing, missing


def test_wiki_languages_match_the_wiki_generator():
    """WIKI_LANGUAGES above is the generator's own list (tools/action_ref_i18n.py LANGS)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import action_ref_i18n
    assert set(action_ref_i18n.LANGS) == WIKI_LANGUAGES
