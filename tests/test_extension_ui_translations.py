"""Regression test: the extension-system UI's translation strings.

The 2026-08-09 "Extensions" settings-UI session (PreferencesDialog's
Extensions tab) and the same day's unrecognized-action UI
(ObjectEventsPanel) and missing/not-installed extension warnings
(PyGameMakerIDE, core/ide_window.py) landed 15 self.tr()-wrapped strings
across three contexts, but that work never touched any translation
catalog — confirmed by grepping every translations/*.ts for these
sources before the fix: zero hits in any of the 10 shipped languages.
Found via an offscreen-QApplication screenshot spike of the Preferences
dialog (see CLAUDE.md's matching session note): the Extensions tab
rendered entirely in English under pt/ja/zh selection, while every other
tab in the same dialog was fully translated.

Uses a hand-rolled offscreen QApplication (no qapp fixture), matching
this repo's established audit-regression / self-ide-context-fix
convention, so this runs even without pytest-qt.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANS_DIR = REPO_ROOT / "translations"

# Which .ts/.qm file is actually shipped/loaded for each language, per
# context — de/it/ru/sl/uk ship split files (PreferencesDialog and
# PyGameMakerIDE both live in the "core" group, ObjectEventsPanel in
# "editors"); es/fr/pt/ja/zh ship one monolithic file for everything.
_SPLIT_LANGS = {"de", "it", "ru", "sl", "uk"}
_ALL_LANGS = ["de", "es", "fr", "it", "pt", "ru", "sl", "uk", "ja", "zh"]

_CONTEXT_GROUP = {
    "PreferencesDialog": "core",
    "PyGameMakerIDE": "core",
    "ObjectEventsPanel": "editors",
}


def _ts_path(lang, context):
    if lang in _SPLIT_LANGS:
        return TRANS_DIR / f"pygm2_{lang}_{_CONTEXT_GROUP[context]}.ts"
    return TRANS_DIR / f"pygm2_{lang}.ts"


def _qm_path(lang, context):
    return _ts_path(lang, context).with_suffix(".qm")


# (context, source) for all 15 strings this session added.
SOURCES = [
    ("PreferencesDialog", "Extensions"),
    ("PreferencesDialog",
     "Disabling an extension here takes effect in the IDE after "
     "restarting — extensions register their actions at startup. "
     "Exports already respect this setting immediately, without "
     "needing a restart."),
    ("PreferencesDialog", "No extensions found."),
    ("PreferencesDialog", "Provides: {0}"),
    ("PreferencesDialog", "Installed Extensions"),
    ("PreferencesDialog", "v{0}"),
    ("ObjectEventsPanel",
     "This action needs the '{0}' extension, which is currently "
     "disabled, so it can't be edited here.\n\n"
     "The action itself is unaffected and will be kept exactly as-is "
     "when you save."),
    ("ObjectEventsPanel",
     "This action ('{0}') needs an extension that isn't installed in "
     "this copy of PyGameMaker, so it can't be edited here.\n\n"
     "The action itself is unaffected and will be kept exactly as-is "
     "when you save."),
    ("ObjectEventsPanel", "Extension Action"),
    ("ObjectEventsPanel", "{0} (needs {1})"),
    ("PyGameMakerIDE", "• {name} — needed for: {actions}"),
    ("PyGameMakerIDE", "Disabled extensions"),
    ("PyGameMakerIDE",
     "This project uses features from extensions that are turned off:"
     "\n\n{list}\n\nThose actions won't run and the project may look or "
     "behave wrong. You can enable an extension via Preferences → "
     "Extensions."),
    ("PyGameMakerIDE", "Extensions not installed"),
    ("PyGameMakerIDE",
     "This project was created with extensions that aren't present in "
     "this copy of PyGameMaker:\n\n{list}\n\nAny actions from them will "
     "be skipped, and the project may look or behave wrong. Update "
     "PyGameMaker or add the missing extension folder(s) to restore "
     "them."),
]


def _get_context_block(content, name):
    m = re.search(
        r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
        content, re.S,
    )
    return m.group(0) if m else None


def test_every_source_present_in_every_shipped_language():
    for lang in _ALL_LANGS:
        for context, source in SOURCES:
            path = _ts_path(lang, context)
            content = path.read_text(encoding="utf-8")
            block = _get_context_block(content, context)
            assert block is not None, f"{path.name}: missing {context} context"
            assert f"<source>{source}</source>" in block, (
                f"{path.name} [{context}]: missing source {source!r}"
            )


def test_every_translation_is_non_empty_and_actually_translated():
    """Not just present — not empty, and not a byte-for-byte copy of the
    English source (which would mean a stray placeholder, not a real
    translation)."""
    for lang in _ALL_LANGS:
        for context, source in SOURCES:
            path = _ts_path(lang, context)
            content = path.read_text(encoding="utf-8")
            block = _get_context_block(content, context)
            m = re.search(
                r"<source>" + re.escape(source) + r"</source>\s*"
                r"<translation>(.*?)</translation>",
                block, re.S,
            )
            assert m is not None, f"{path.name} [{context}]: {source!r} has no translation tag"
            translated = m.group(1).strip()
            assert translated, f"{path.name} [{context}]: {source!r} translation is empty"
            # "v{0}" is legitimately identical across every language (a
            # bare version-number prefix), and French's "Extensions" is a
            # genuine cognate (confirmed against wiki/Extensions_fr.md's
            # own page title) — both intentional, not stray copies.
            if source != "v{0}" and not (lang == "fr" and source == "Extensions"):
                assert translated != source, (
                    f"{path.name} [{context}]: {source!r} translation equals the English source"
                )


def test_runtime_translate_resolves_for_every_language():
    """The actual bug this closes: a live QTranslator must resolve each
    string per (context, source), not silently fall back to English."""
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    # Group sources by which .qm file serves them, so each translator is
    # loaded/removed once per (lang, file) pair rather than once per string.
    files_needed = {}
    for context, source in SOURCES:
        for lang in _ALL_LANGS:
            files_needed.setdefault((lang, _qm_path(lang, context)), []).append(
                (context, source))

    for (lang, qm_path), pairs in files_needed.items():
        assert qm_path.exists(), f"{qm_path} not compiled"
        translator = QTranslator()
        assert translator.load(str(qm_path)), f"{qm_path.name} failed to load"
        app.installTranslator(translator)
        try:
            for context, source in pairs:
                resolved = QCoreApplication.translate(context, source)
                is_expected_cognate = source == "v{0}" or (lang == "fr" and source == "Extensions")
                assert resolved != source or is_expected_cognate, (
                    f"{lang}/{qm_path.name} [{context}]: {source!r} did not "
                    f"resolve (still English)"
                )
                assert resolved, f"{lang}/{qm_path.name} [{context}]: {source!r} resolved empty"
        finally:
            app.removeTranslator(translator)
