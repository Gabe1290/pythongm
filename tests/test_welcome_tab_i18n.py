"""Regression test: the Welcome tab's "Close current project" button and
"(current)" tag resolve in every shipped language.

Added alongside the feature itself (the Welcome tab needed a way to close
the open project, and the recent-projects list needed to keep showing the
active project after "Clear recent projects"). Following
test_extension_ui_translations.py's established pattern/landmine: a live
QTranslator loaded straight from each language's .qm is the only check
that actually proves resolution — LanguageManager.set_language() can
short-circuit as a no-op if Config's persisted language already matches
the target, which would make a translation gap look resolved when it
isn't.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANS_DIR = REPO_ROOT / "translations"

# WelcomeTab lives in the "core" split group for de/it/ru/sl/uk; es/fr/pt/
# ja/zh ship one monolithic file for everything.
_SPLIT_LANGS = {"de", "it", "ru", "sl", "uk"}
_ALL_LANGS = ["de", "es", "fr", "it", "pt", "ru", "sl", "uk", "ja", "zh"]

SOURCES = [
    "Close current project",
    "(current)",
]


def _ts_path(lang):
    if lang in _SPLIT_LANGS:
        return TRANS_DIR / f"pygm2_{lang}_core.ts"
    return TRANS_DIR / f"pygm2_{lang}.ts"


def _qm_path(lang):
    return _ts_path(lang).with_suffix(".qm")


def test_every_source_present_in_every_shipped_language():
    import re
    for lang in _ALL_LANGS:
        content = _ts_path(lang).read_text(encoding="utf-8")
        m = re.search(r"<context>\s*<name>WelcomeTab</name>.*?</context>", content, re.S)
        assert m is not None, f"{_ts_path(lang).name}: missing WelcomeTab context"
        block = m.group(0)
        for source in SOURCES:
            assert f"<source>{source}</source>" in block, (
                f"{_ts_path(lang).name}: missing source {source!r}")


def test_every_translation_is_non_empty_and_actually_translated():
    import re
    for lang in _ALL_LANGS:
        content = _ts_path(lang).read_text(encoding="utf-8")
        for source in SOURCES:
            m = re.search(
                r"<source>" + re.escape(source) + r"</source>\s*"
                r"<translation>(.*?)</translation>",
                content, re.S,
            )
            assert m is not None, f"{_ts_path(lang).name}: {source!r} has no translation tag"
            translated = m.group(1).strip()
            assert translated, f"{_ts_path(lang).name}: {source!r} translation is empty"
            assert translated != source, (
                f"{_ts_path(lang).name}: {source!r} translation equals the English source")


def test_runtime_translate_resolves_for_every_language():
    """The actual property worth pinning: a live QTranslator must resolve
    both strings under the WelcomeTab context, not silently fall back to
    English."""
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    for lang in _ALL_LANGS:
        qm_path = _qm_path(lang)
        assert qm_path.exists(), f"{qm_path} not compiled"
        translator = QTranslator()
        assert translator.load(str(qm_path)), f"{qm_path.name} failed to load"
        app.installTranslator(translator)
        try:
            for source in SOURCES:
                resolved = QCoreApplication.translate("WelcomeTab", source)
                assert resolved != source, (
                    f"{lang}/{qm_path.name}: {source!r} did not resolve (still English)")
                assert resolved, f"{lang}/{qm_path.name}: {source!r} resolved empty"
        finally:
            app.removeTranslator(translator)
