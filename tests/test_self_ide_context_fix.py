"""Regression test: the dead "self.ide" translation context.

self.ide.tr(...) calls in core/ide_exporters.py resolve at runtime under
the context "PyGameMakerIDE" (the real class of self.ide, set via
`self.ide = ide_window` where ide_window is a PyGameMakerIDE instance —
see core/ide_window.py), NOT the literal "self.ide" text some
hand-authored .ts entries used. A translation filed under a "self.ide"
context is therefore never consulted by Qt at runtime; every shipped
language (de/it/es/ru/sl/uk/fr) carried 24 such messages as dead weight,
18 of which had no working translation anywhere (the other 6 happened to
already exist, correctly, under the real PyGameMakerIDE context from
core/ide_window.py's own self.tr() calls).

Fixed by moving each language's already-translated, previously-missing
messages into the PyGameMakerIDE context of whichever file is actually
shipped for that language (split pygm2_<lang>_core.ts for de/it/ru/sl/uk,
monolithic pygm2_<lang>.ts for es/fr) and deleting the now-redundant
self.ide context from the fixed file.

Uses a hand-rolled offscreen QApplication (no qapp fixture) so this runs
even without pytest-qt, matching this repo's audit-regression convention.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANS_DIR = REPO_ROOT / "translations"

# File that's actually shipped/loaded for each fixed language.
SHIPPED_TS = {
    "de": TRANS_DIR / "pygm2_de_core.ts",
    "it": TRANS_DIR / "pygm2_it_core.ts",
    "ru": TRANS_DIR / "pygm2_ru_core.ts",
    "sl": TRANS_DIR / "pygm2_sl_core.ts",
    "uk": TRANS_DIR / "pygm2_uk_core.ts",
    "es": TRANS_DIR / "pygm2_es.ts",
    "fr": TRANS_DIR / "pygm2_fr.ts",
}

SHIPPED_QM = {
    "de": TRANS_DIR / "pygm2_de_core.qm",
    "it": TRANS_DIR / "pygm2_it_core.qm",
    "ru": TRANS_DIR / "pygm2_ru_core.qm",
    "sl": TRANS_DIR / "pygm2_sl_core.qm",
    "uk": TRANS_DIR / "pygm2_uk_core.qm",
    "es": TRANS_DIR / "pygm2_es.qm",
    "fr": TRANS_DIR / "pygm2_fr.qm",
}

# A few of the 18 previously-missing source strings, enough to confirm the
# move landed without re-listing all 18 in every assertion.
SAMPLE_SOURCES = [
    "Select Export Directory",
    "Export Project as Zip",
    "Loading project from zip...",
    "Failed to load",
]


def _get_context_block(content, name):
    m = re.search(
        r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
        content, re.S,
    )
    return m.group(0) if m else None


def test_self_ide_context_absent_from_shipped_files():
    for lang, path in SHIPPED_TS.items():
        content = path.read_text(encoding="utf-8")
        assert "<name>self.ide</name>" not in content, (
            f"{path.name}: dead 'self.ide' context should have been removed"
        )


def test_pygamemakerIDE_context_has_ide_exporters_strings():
    for lang, path in SHIPPED_TS.items():
        content = path.read_text(encoding="utf-8")
        block = _get_context_block(content, "PyGameMakerIDE")
        assert block is not None, f"{path.name}: missing PyGameMakerIDE context"
        for source in SAMPLE_SOURCES:
            assert f"<source>{source}</source>" in block, (
                f"{path.name}: PyGameMakerIDE context missing {source!r}"
            )
        assert "core/ide_exporters.py" in block, (
            f"{path.name}: PyGameMakerIDE context missing ide_exporters.py locations"
        )


def test_moved_messages_have_real_non_vanished_translations():
    for lang, path in SHIPPED_TS.items():
        content = path.read_text(encoding="utf-8")
        block = _get_context_block(content, "PyGameMakerIDE")
        for source in SAMPLE_SOURCES:
            m = re.search(
                r"<source>" + re.escape(source) + r"</source>\s*"
                r"<translation>(.*?)</translation>",
                block, re.S,
            )
            assert m is not None, f"{path.name}: {source!r} has no translation tag"
            assert m.group(1).strip(), f"{path.name}: {source!r} translation is empty"


def test_runtime_self_tr_resolves_via_real_class_context():
    """The actual bug: self.ide.tr(x) must resolve x, not fall back to English."""
    from PySide6.QtWidgets import QApplication, QMainWindow
    from PySide6.QtCore import QTranslator

    app = QApplication.instance() or QApplication([])

    class PyGameMakerIDE(QMainWindow):
        pass

    for lang, qm_path in SHIPPED_QM.items():
        if not qm_path.exists():
            continue
        translator = QTranslator()
        loaded = translator.load(str(qm_path))
        assert loaded, f"{qm_path.name} failed to load"
        app.installTranslator(translator)
        try:
            window = PyGameMakerIDE()
            result = window.tr("Select Export Directory")
            assert result != "Select Export Directory", (
                f"{lang}: self.tr() still falls back to English — fix regressed"
            )
        finally:
            app.removeTranslator(translator)
