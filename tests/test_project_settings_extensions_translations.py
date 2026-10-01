"""Regression test: ProjectSettingsDialog's two new Extensions-section
strings (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 5b) are present,
non-empty, and actually resolve through a real QTranslator in all 10
shipped languages. Same pattern as test_extension_ui_translations.py's
2026-08-09 PreferencesDialog fix.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANS_DIR = REPO_ROOT / "translations"

_SPLIT_LANGS = {"de", "it", "ru", "sl", "uk"}
_ALL_LANGS = ["de", "es", "fr", "it", "pt", "ru", "sl", "uk", "ja", "zh"]

CONTEXT = "ProjectSettingsDialog"
SOURCES = ["Extensions", "used by {0} action(s)"]


def _ts_path(lang):
    if lang in _SPLIT_LANGS:
        return TRANS_DIR / f"pygm2_{lang}_dialogs.ts"
    return TRANS_DIR / f"pygm2_{lang}.ts"


def _qm_path(lang):
    return _ts_path(lang).with_suffix(".qm")


def _get_context_block(content, name):
    m = re.search(
        r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
        content, re.S,
    )
    return m.group(0) if m else None


def test_every_source_present_in_every_shipped_language():
    for lang in _ALL_LANGS:
        path = _ts_path(lang)
        content = path.read_text(encoding="utf-8")
        block = _get_context_block(content, CONTEXT)
        assert block is not None, f"{path.name}: missing {CONTEXT} context"
        for source in SOURCES:
            assert f"<source>{source}</source>" in block, (
                f"{path.name} [{CONTEXT}]: missing source {source!r}")


def test_every_translation_is_non_empty_and_actually_translated():
    for lang in _ALL_LANGS:
        path = _ts_path(lang)
        content = path.read_text(encoding="utf-8")
        block = _get_context_block(content, CONTEXT)
        for source in SOURCES:
            m = re.search(
                r"<source>" + re.escape(source) + r"</source>\s*"
                r"<translation>(.*?)</translation>",
                block, re.S,
            )
            assert m is not None, f"{path.name} [{CONTEXT}]: {source!r} has no translation tag"
            translated = m.group(1).strip()
            assert translated, f"{path.name} [{CONTEXT}]: {source!r} translation is empty"
            # French's "Extensions" is a genuine cognate (same exception
            # test_extension_ui_translations.py already carves out for the
            # identical source text under a different context).
            if not (lang == "fr" and source == "Extensions"):
                assert translated != source, (
                    f"{path.name} [{CONTEXT}]: {source!r} translation equals the English source")


def test_runtime_translate_resolves_for_every_language():
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
                resolved = QCoreApplication.translate(CONTEXT, source)
                is_cognate = lang == "fr" and source == "Extensions"
                assert resolved != source or is_cognate, (
                    f"{lang}/{qm_path.name} [{CONTEXT}]: {source!r} did not resolve")
                assert resolved, f"{lang}/{qm_path.name} [{CONTEXT}]: {source!r} resolved empty"
        finally:
            app.removeTranslator(translator)
