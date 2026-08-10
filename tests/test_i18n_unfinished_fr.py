"""Regression test: fr's 47 previously-unfinished translations.

Part of closing the gap docs/I18N_UNFINISHED_2026-08-10.md scoped after
the extension-UI translation fix (commit 051de39) found German wasn't
alone in carrying never-completed `<translation type="unfinished">`
entries. fr was the smallest of the seven affected languages (47 active
entries, single monolithic pygm2_fr.ts) and the first tackled.

Uses a hand-rolled offscreen QApplication (no qapp fixture), matching
this repo's established audit-regression / i18n-fix convention, so this
runs even without pytest-qt.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TS_PATH = REPO_ROOT / "translations" / "pygm2_fr.ts"
QM_PATH = REPO_ROOT / "translations" / "pygm2_fr.qm"

# (context, source) for all 47 strings this batch filled in.
SOURCES = [
    ("AssetTreeWidget",
     "No project loaded.\nUse File → New Project or File → Open Project to begin."),
    ("BaseBlockConfigDialog", "Select None"),
    ("BaseEditor", "🪟 Float"),
    ("BaseEditor", "Open this editor in its own window"),
    ("BlocklyWidget", "Error loading Blockly"),
    ("FloatableEditorMixin", "Return this editor to the IDE&apos;s tab strip"),
    ("FloatableEditorMixin", "🪟 Float"),
    ("FloatableEditorMixin", "Open this editor in its own window"),
    ("ObjectEditor", "Edit mode: changes apply automatically as you type"),
    ("ObjectEditor", "No event methods found in the code"),
    ("ObjectEditor", "{0} events"),
    ("PlaygroundEditor", "🪟 Float"),
    ("PlaygroundEditor", "Open this editor in its own window"),
    ("PyGameMakerIDE", "Floated: {0}"),
    ("PyGameMakerIDE", "Reattached: {0}"),
    ("PyGameMakerIDE", "Window mode: Tabbed"),
    ("PyGameMakerIDE", "Window mode: Floating"),
    ("PyGameMakerIDE", "⧉ Floating"),
    ("PyGameMakerIDE",
     "Window mode: Floating. Click to switch all editors back into tabs "
     "(use this if a floating window has been dragged off-screen)."),
    ("PyGameMakerIDE", "⊞ Tabbed"),
    ("PyGameMakerIDE",
     "Window mode: Tabbed. Click to pop every editor out into its own window."),
    ("PyGameMakerIDE", "Export &amp;Aseba (Thymio) code..."),
    ("PyGameMakerIDE", "New Project (Ctrl+N)"),
    ("PyGameMakerIDE", "Open Project (Ctrl+O)"),
    ("PyGameMakerIDE", "Save Project (Ctrl+S)"),
    ("PyGameMakerIDE", "Test Game (F5)"),
    ("PyGameMakerIDE", "Debug Game (F6)"),
    ("PyGameMakerIDE", "Export Game…"),
    ("PyGameMakerIDE", "Import Sprite…"),
    ("PyGameMakerIDE", "Import Sound…"),
    ("PyGameMakerIDE", "Tabbed"),
    ("PyGameMakerIDE", "Toggle between Tabbed and Floating editor layouts"),
    ("PyGameMakerIDE", "Exporting Aseba code..."),
    ("PyGameMakerIDE", "Aseba Export Failed"),
    ("PyGameMakerIDE", "Failed to export Aseba code:\n\n{0}"),
    ("PyGameMakerIDE", "Aseba export failed"),
    ("PyGameMakerIDE", "Aseba Export"),
    ("PyGameMakerIDE",
     "No Thymio objects found in this project, so no Aseba code was "
     "generated. Add a Thymio object to the project and try again."),
    ("PyGameMakerIDE", "Aseba export: nothing to export"),
    ("PyGameMakerIDE", "Aseba export complete"),
    ("PyGameMakerIDE", "Aseba Export Complete"),
    ("PyGameMakerIDE",
     "Aseba .aesl files written to:\n{0}\n\nWould you like to open the output folder?"),
    ("RoomEditor", "🪟 Float"),
    ("RoomEditor", "Open this editor in its own window"),
    ("SpriteEditor", "Precise Collision"),
    ("SpriteEditor",
     "Enable pixel-perfect collision for this sprite. Static-only: "
     "rotated or scaled instances fall back to AABB."),
    ("TutorialDialog", "Select a tutorial and click Open (or double-click):"),
]

assert len(SOURCES) == 47, len(SOURCES)


def _get_context_block(content, name):
    m = re.search(
        r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
        content, re.S,
    )
    return m.group(0) if m else None


def test_no_empty_unfinished_entries_remain():
    content = TS_PATH.read_text(encoding="utf-8")
    assert '<translation type="unfinished"></translation>' not in content


def test_every_source_has_a_real_non_empty_translation():
    content = TS_PATH.read_text(encoding="utf-8")
    for context, source in SOURCES:
        block = _get_context_block(content, context)
        assert block is not None, f"missing {context} context"
        m = re.search(
            r"<source>" + re.escape(source) + r"</source>\s*"
            r"<translation>(.*?)</translation>",
            block, re.S,
        )
        assert m is not None, f"[{context}] {source!r}: no real <translation> tag"
        translated = m.group(1).strip()
        assert translated, f"[{context}] {source!r}: translation is empty"
        assert translated != source, (
            f"[{context}] {source!r}: translation equals the English source"
        )


def test_runtime_translate_resolves_every_string():
    """SOURCES holds each <source>'s literal XML-entity-escaped text (for
    the regex tests above); the real self.tr() call at runtime sees the
    UNESCAPED Python string (an XML artifact, not part of the actual
    source), so unescape before calling QCoreApplication.translate."""
    from xml.sax.saxutils import unescape
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    translator = QTranslator()
    assert translator.load(str(QM_PATH)), f"{QM_PATH.name} failed to load"
    app.installTranslator(translator)
    try:
        for context, source in SOURCES:
            runtime_source = unescape(source, {"&apos;": "'", "&quot;": '"'})
            resolved = QCoreApplication.translate(context, runtime_source)
            assert resolved != runtime_source, (
                f"[{context}] {source!r} did not resolve (still English)"
            )
            assert resolved, f"[{context}] {source!r} resolved empty"
    finally:
        app.removeTranslator(translator)
