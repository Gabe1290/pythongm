"""Extension actions must read in the user's language, not the author's.

35 of the IDE's actions come from plugins and folder extensions. Their
display names pass through `tr()` in the action palette and the configure
dialog, so they are translatable -- but for a long time not one of them
appeared in any of the ten catalogues, and the extensions disagreed about
their source language:

* raycast and block world are authored in English, so an English user saw them
  correctly and everyone else saw English;
* the LAN multiplayer extension was authored **French-first** -- display names,
  descriptions and every parameter were French prose -- so a French user saw it
  correctly by accident and **every other language read French**. A German
  teacher opening the palette got "Héberger une partie" and a paragraph of
  French.

Fixed on 2026-09-06 by re-authoring that extension in English (the source
language of the rest of the codebase) and adding the French back as a real
translation, so both audiences improve rather than trading places.

Qt keys a translation by (context, source) and takes the context from the
CONCRETE runtime class, so the same string shown in two places needs an entry
under both contexts -- there is no cross-context fallback. That is what
`CONTEXTS` below pins.
"""
import os
import re
import sys
from xml.sax.saxutils import escape
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6

@pytest.fixture(autouse=True)
def _restore_english_afterwards():
    """Leave the application in English after EVERY test in this file.

    These tests install real translators and switch the app language, which is
    process-global state. Without this, French leaked into the rest of the
    suite and ten unrelated widget tests started asserting against
    "Aucun tutoriel disponible" -- failures that reproduced only when this file
    ran first, which is exactly the kind of order-dependent breakage that
    wastes an afternoon. Restoring unconditionally in teardown is cheaper than
    reasoning about which path installed what.
    """
    yield
    try:
        from PySide6.QtWidgets import QApplication
        from core.language_manager import get_language_manager

        if QApplication.instance() is not None:
            get_language_manager().set_language("en")
    except Exception:
        pass


# Where these strings are displayed: the palette context menu lives on
# ObjectEventsPanel, the configure dialog on ActionConfigDialog.
CONTEXTS = ("ObjectEventsPanel", "ActionConfigDialog")

ACCENTED = re.compile(r"[éèêëàâäçùûüîïôöœ]", re.IGNORECASE)


def _network_actions():
    from events.action_types import ACTION_TYPES
    from events.plugin_loader import load_all_plugins
    from runtime.action_executor import ActionExecutor

    load_all_plugins(ActionExecutor())
    return {n: a for n, a in ACTION_TYPES.items()
            if getattr(a, "category", "") == "Network"}


def test_the_network_actions_are_registered_under_an_english_category():
    """The category is displayed too, and it was 'Réseau' -- French for every
    user, in every language."""
    from events.action_types import ACTION_TYPES

    actions = _network_actions()
    # 15 from multiplayer_lan + 6 from multiplayer_files (Phase 1,
    # docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md) -- both extensions share the
    # "Network" category on purpose (see multiplayer_files/actions.py's
    # own module docstring), so this count grows with either one.
    assert len(actions) == 21, sorted(actions)
    assert not any(getattr(a, "category", "") == "R\u00e9seau"
                   for a in ACTION_TYPES.values()), (
        "the French category name is back")


def test_no_extension_action_carries_french_source_text():
    """Source strings are English across this codebase. An extension authored
    in another language cannot be localized by the catalogues -- it simply
    reaches every user in the author's language."""
    offenders = []
    for name, action in _network_actions().items():
        blobs = {"display_name": action.display_name or "",
                 "description": action.description or ""}
        for param in action.parameters:
            blobs["param %s label" % param.name] = param.display_name or ""
            blobs["param %s help" % param.name] = param.description or ""
        for where, text in blobs.items():
            if ACCENTED.search(text):
                offenders.append("%s.%s: %r" % (name, where, text[:60]))
    assert not offenders, (
        "French text in the action source; it must be English and translated "
        "instead:\n  " + "\n  ".join(offenders))


@pytest.fixture
def french():
    """A live French QTranslator over the compiled catalogue.

    FUNCTION scope, deliberately. As a module fixture it stayed installed for
    the rest of the file, so the all-language test below ran with French
    loaded underneath -- and Qt, consulting translators in reverse install
    order, resolved from French whatever the target language was missing. A
    mutation that deleted "Draw Minimap" from the German catalogue passed the
    whole file and only failed when that one test ran alone. Per-test teardown
    removes the translator before the next test installs its own.
    """
    from PySide6.QtCore import QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    qm = REPO_ROOT / "translations" / "pygm2_fr.qm"
    if not qm.exists():
        pytest.skip("pygm2_fr.qm not compiled")
    translator = QTranslator()
    assert translator.load(str(qm)), "could not load the French catalogue"
    app.installTranslator(translator)
    yield
    app.removeTranslator(translator)


@pytest.mark.parametrize("context", CONTEXTS)
def test_french_users_still_get_french(context, french):
    """The whole point of the change: re-authoring in English must not cost
    French users what they already had. Checked through a live QTranslator
    rather than by reading the .ts, because a string can be present in the
    catalogue and still not resolve -- that is exactly how the `self.ide`
    context bug survived in every language for months."""
    from PySide6.QtCore import QCoreApplication

    actions = _network_actions()
    catalogue = (REPO_ROOT / "translations" / "pygm2_fr.ts").read_text(
        encoding="utf-8")
    missing = []
    for name, action in actions.items():
        source = action.display_name
        # PRESENCE in the catalogue, not "differs from its source". Four
        # strings in this extension -- Port, Mode, X, Y -- are genuinely
        # the same word in French, so a differs-from-source check would
        # call a correct translation a missing one. (It did exactly that
        # on the first run, while also correctly catching two REAL gaps:
        # "Set Network Mode (v1)" and "Host Address" had been English all
        # along, so the French-to-English pass never touched them and no
        # French was ever written for them.)
        # The EXACT element, not a bare substring: a first version
        # searched for the text alone and survived a mutation that
        # renamed the entry to "Host a Game REMOVED", because the
        # original text was still present inside the new one.
        element = "<source>%s</source>" % escape(source)
        if element not in catalogue:
            missing.append("%s (%r)" % (name, source))
    assert not missing, (
        "no entry in the French catalogue for:\n  %s"
        % chr(10).join(missing))

    # Resolving at runtime is a separate claim from being present.
    for name, action in actions.items():
        assert QCoreApplication.translate(context, action.display_name), name


def test_the_french_really_is_french(french):
    """Guards the test above from passing on a translation that is just the
    English copied across."""
    from PySide6.QtCore import QCoreApplication

    translated = QCoreApplication.translate("ObjectEventsPanel", "Host a Game")
    assert translated != "Host a Game"
    assert ACCENTED.search(translated), translated


def test_accents_survive_the_round_trip(french):
    """This is educational software for French-speaking students; a stripped
    accent is a defect, not cosmetics. Byte-level, because a cp1252 console
    makes correct UTF-8 look broken and broken UTF-8 look fine."""
    from PySide6.QtCore import QCoreApplication

    got = QCoreApplication.translate("ActionConfigDialog", "Max players")
    assert got == "Joueurs max"

    host = QCoreApplication.translate("ObjectEventsPanel", "Host a Game")
    assert host == "H\u00e9berger une partie", host.encode("unicode_escape")


def test_the_catalogue_has_no_double_escaping():
    """A translation written with already-escaped entities (&gt;) compiles
    cleanly and shows the user literal '&gt;'. That happened once during the
    zh pass and was only caught by a live lookup."""
    text = (REPO_ROOT / "translations" / "pygm2_fr.ts").read_text(
        encoding="utf-8")
    assert "&amp;gt;" not in text
    assert "&amp;lt;" not in text
    assert "\u00c3\u00a9" not in text, "mojibake (double-encoded UTF-8)"


# --- the whole extension surface, every shipped language --------------------

EXTENSION_CATEGORIES = ("Network", "3D View", "Audio")
SHIPPED = ("de", "es", "fr", "it", "ja", "pt", "ru", "sl", "uk", "zh")


def _extension_actions():
    """Every action contributed by a plugin or folder extension."""
    from events.action_types import ACTION_TYPES
    from events.plugin_loader import load_all_plugins
    from runtime.action_executor import ActionExecutor

    load_all_plugins(ActionExecutor())
    return {n: a for n, a in ACTION_TYPES.items()
            if getattr(a, "category", "") in EXTENSION_CATEGORIES}


def test_there_are_extension_actions_to_check():
    """45, not 35.

    The first count came from "what did load_all_plugins ADD to
    ACTION_TYPES?", which misses check_sound and stop_sound -- both sit in the
    Audio category but are declared statically in core. Filtering by CATEGORY
    is what the user actually sees in the palette, and that difference of two
    was found by this assertion rather than by reading. 37 -> 39 when Block
    World's Tier 8 crafting actions (set_crafting_recipe, craft_item) landed
    (docs/BLOCK_WORLD_CRAFTING_PLAN.md) -- translated into all 10 shipped
    languages the same day, so this count and the i18n coverage below moved
    together rather than the count updating first and coverage lagging. 39 ->
    45 when multiplayer_files' 6 Phase 1 actions landed
    (docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md), same discipline: display names
    translated the same commit, not left to lag."""
    actions = _extension_actions()
    assert len(actions) == 45, sorted(actions)


@pytest.mark.parametrize("lang", SHIPPED)
def test_every_extension_action_name_resolves(lang):
    """The A1 goal: an extension action reads in the user's language.

    Before 2026-09-06 not one of these 35 appeared in any catalogue, so every
    non-English user read English (and, for the LAN extension, French).

    Driven through the real LanguageManager rather than a hand-built
    QTranslator, because that is what the running app uses -- and checked in
    BOTH Qt contexts, since Qt keys by (context, source) with no fallback
    between them.
    """
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication

    from core.language_manager import get_language_manager

    QApplication.instance() or QApplication([])
    manager = get_language_manager()
    previous = getattr(manager, "current_language", "en")
    try:
        manager.set_language(lang)
        unresolved = []
        for name, action in _extension_actions().items():
            source = action.display_name
            for context in CONTEXTS:
                if QCoreApplication.translate(context, source) == source:
                    unresolved.append("%s/%s (%s)" % (context, name, source))
        assert not unresolved, (
            "%s: %d extension action names fall back to English:\n  %s"
            % (lang, len(unresolved), "\n  ".join(unresolved[:12])))
    finally:
        manager.set_language(previous)


def test_a_vanished_entry_does_not_count_as_translated():
    """The trap that made this pass look finished when it was not.

    lrelease DROPS type="vanished" messages from the compiled .qm, so a source
    shadowed only by a vanished duplicate stays untranslated at runtime no
    matter how good the text in the .ts looks. Play Sound / Play Music /
    Stop Music each carried a correct translation marked vanished in five
    languages and had been reaching users in English the whole time.

    Appending a second, live entry did NOT fix it either: two messages with
    the same source in one context do not resolve at all. They had to be
    un-vanished in place.
    """
    import re

    for lang in ("de", "es", "it", "ru", "sl", "uk"):
        for stem in ("pygm2_%s_editors.ts" % lang, "pygm2_%s.ts" % lang):
            path = REPO_ROOT / "translations" / stem
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            block = re.search(
                r"<context>\s*<name>ObjectEventsPanel</name>(.*?)</context>",
                text, re.S)
            if not block:
                continue
            for source in ("Play Sound", "Play Music", "Stop Music"):
                entries = re.findall(
                    r"<message>(?:(?!</message>).)*?<source>" + source
                    + r"</source>.*?</message>", block.group(1), re.S)
                assert len(entries) <= 1, (
                    "%s has %d entries for %r in ObjectEventsPanel; duplicates "
                    "do not resolve" % (stem, len(entries), source))
                for entry in entries:
                    assert 'type="vanished"' not in entry, (
                        "%s: %r is vanished, so lrelease drops it and the user "
                        "sees English" % (stem, source))
