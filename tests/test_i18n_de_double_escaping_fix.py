"""Regression test: de's 4 double-escaped translations from the
2026-08-10 unfinished-translation batch (commit 3928e32).

Found while cross-checking German against Italian for
docs/I18N_UNFINISHED_2026-08-10.md unit 3/7: `pygm2_de_core.ts` had four
<translation> values passed through XML-escaping TWICE (e.g. the real
'&' character in "Export &Aseba (Thymio) code..." was written as the
literal text "&amp;amp;exportieren" instead of "&amp;exportieren"). This
is exactly the double-escaping landmine already documented in
docs/I18N_UNFINISHED_2026-08-10.md and CLAUDE.md's zh session note: it
passes XML validity and `lrelease` silently, and only shows up as a
literal "&lt;h3&gt;"/"&amp;exportieren" string at runtime instead of a
real HTML heading / mnemonic ampersand.

Uses a hand-rolled offscreen QApplication (no qapp fixture), matching
this repo's established audit-regression / i18n-fix convention.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_TS = REPO_ROOT / "translations" / "pygm2_de_core.ts"
CORE_QM = REPO_ROOT / "translations" / "pygm2_de_core.qm"

LICENSE_SOURCE = (
    "<h3>License</h3><p>• <b>Source code:</b> MIT License<br>• "
    "<b>Documentation:</b> Creative Commons Attribution 4.0 (CC BY 4.0)"
    "<br><small>Relicensed from GPLv3 to MIT + CC BY 4.0 to lower the "
    "barrier to reuse for educators, students, and downstream projects. "
    "See the <code>LICENSE</code> and <code>LICENSE-docs</code> files "
    "for full terms.</small></p><p>&copy; Gabriel Thullen, 2025-2026</p>"
)

MNEMONIC_SOURCES = [
    "Export &Aseba (Thymio) code...",
    "Import Open &Roberta XML...",
    "Import &GameMaker .gmk File...",
]


def test_ts_file_has_no_double_escaped_translations():
    content = CORE_TS.read_text(encoding="utf-8")
    assert "&amp;lt;" not in content, "double-escaped '<' survives in pygm2_de_core.ts"
    assert "&amp;gt;" not in content, "double-escaped '>' survives in pygm2_de_core.ts"
    assert "&amp;amp;" not in content, "double-escaped '&' survives in pygm2_de_core.ts"


def test_runtime_license_translation_is_real_html_not_escaped_text():
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    translator = QTranslator()
    assert translator.load(str(CORE_QM)), f"{CORE_QM} failed to load"
    app.installTranslator(translator)
    try:
        resolved = QCoreApplication.translate("PyGameMakerIDE", LICENSE_SOURCE)
        assert resolved.startswith("<h3>Lizenz</h3>"), (
            f"License block still double-escaped: {resolved[:60]!r}"
        )
        assert "&lt;" not in resolved and "&amp;lt;" not in resolved
    finally:
        app.removeTranslator(translator)


def test_runtime_mnemonic_translations_carry_a_real_ampersand():
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    translator = QTranslator()
    assert translator.load(str(CORE_QM)), f"{CORE_QM} failed to load"
    app.installTranslator(translator)
    try:
        for source in MNEMONIC_SOURCES:
            resolved = QCoreApplication.translate("PyGameMakerIDE", source)
            assert "&amp;" not in resolved, (
                f"{source!r} still double-escaped: {resolved!r}"
            )
            assert "&" in resolved, f"{source!r} lost its mnemonic ampersand: {resolved!r}"
    finally:
        app.removeTranslator(translator)
