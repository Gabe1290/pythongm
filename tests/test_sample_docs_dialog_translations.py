"""Regression for docs/DEFERRED_GAPS_2026_PLAN.md Tier 2.1: pt/ja/zh were
each missing the entire SampleDocsDialog translation context (3 messages)
plus the "Sample guides" WelcomeTab button label -- confirmed via a real
context diff against pygm2_fr.ts, not the originally-logged "26 of 48"
estimate (which turned out to be a miscount; the real gap was these 4
messages). A live QTranslator is the strongest available proof without a
running GUI (matches this repo's established i18n verification pattern)."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTranslator, QCoreApplication
    HAS_QT = True
except ImportError:
    HAS_QT = False

pytestmark = pytest.mark.skipif(not HAS_QT, reason="PySide6 not available")

LANGS = ["pt", "ja", "zh"]

EXPECTED = {
    "WelcomeTab": ["\U0001F4D6  Sample guides"],
    "SampleDocsDialog": [
        "Sample guides",
        "_No bundled samples were found in this build._",
        "_No documentation is bundled for **{0}**._",
    ],
}


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


@pytest.mark.parametrize("lang", LANGS)
def test_sample_docs_dialog_context_present_in_ts_source(lang):
    content = (REPO_ROOT / "translations" / f"pygm2_{lang}.ts").read_text(encoding="utf-8")
    assert "<name>SampleDocsDialog</name>" in content
    for src in EXPECTED["SampleDocsDialog"]:
        assert f"<source>{src}</source>" in content, (lang, src)
    for src in EXPECTED["WelcomeTab"]:
        assert f"<source>{src}</source>" in content, (lang, src)


@pytest.mark.parametrize("lang", LANGS)
def test_messages_resolve_via_live_qtranslator_and_differ_from_english(qapp, lang):
    translator = QTranslator()
    qm_path = str(REPO_ROOT / "translations" / f"pygm2_{lang}.qm")
    assert translator.load(qm_path), f"failed to load {qm_path}"
    qapp.installTranslator(translator)
    try:
        for context, sources in EXPECTED.items():
            for src in sources:
                resolved = QCoreApplication.translate(context, src)
                assert resolved, (lang, context, src)
                assert resolved != src, (lang, context, src, "did not translate")
    finally:
        qapp.removeTranslator(translator)
