"""Regression test: Polish (pl) translation catalog guard.

Unlike the de/es/fr/it/ru/sl/uk "unfinished" guards (which each filled a
specific historical gap and pin that exact SOURCES list), pygm2_pl.ts was
built from scratch in one arc (docs/POLISH_I18N_PLAN.md Phase 1) covering
every located-active message across all 70 real contexts in one pass, so
there's no fixed gap list to pin -- this test sweeps the whole file
instead: no empty unfinished entries, every message has a real non-empty
translation that differs from the English source (barring documented
cognates), Polish diacritics survive, and a representative sample
resolves through a live QTranslator.

Uses a hand-rolled offscreen QApplication (no qapp fixture), matching
this repo's established audit-regression / i18n-fix convention, so this
runs even without pytest-qt.
"""
import re
from pathlib import Path
from xml.sax.saxutils import unescape

REPO_ROOT = Path(__file__).resolve().parent.parent
TS_PATH = REPO_ROOT / "translations" / "pygm2_pl.ts"
QM_PATH = REPO_ROOT / "translations" / "pygm2_pl.qm"

# Genuine cross-language cognates / deliberately-unchanged strings --
# same category CLAUDE.md and the other i18n guard tests already carve
# out for "v{0}" and (for fr) "Extensions". Three sub-categories, found
# by scanning the whole file for source==translation: (1) bare
# symbol/template strings with no translatable prose ("+", "-", "D",
# coordinate labels like "X:"/"Y:", time abbreviations, bare `{n}`
# placeholder templates); (2) proper nouns (Robot, Thymio, Port is a
# tech term not a name but behaves the same way); (3) borrowed tech
# terms kept as-is in Polish UI text (Sprite, Zoom, Web) and keyboard
# key names kept universal across languages, matching fr's own
# precedent of leaving "Enter"/"Escape"/"Shift"/"Alt" untranslated.
_COGNATE_SOURCES = {
    "v{0}", "{0} ({1})", "+", "-", "D",
    "X:", "Y:",
    "15s", "30s", "1m", "2m", "5m",
    "Robot", "Port:",
    "Web", "Web (HTML5)",
    "🧩 Blockly", "🤖 Thymio", "Thymio",
    "🎮  {0}", "🎨 {0}",
    "{0}: {1}", "{0}\n{1}x{2}", "{0} x {1}",
    "Sprite:", "Sprite: {0}",
    "L: 0", "Zoom: 100%", "Zoom: {0}%",
    "Enter", "Escape", "Shift", "Alt",
}

# A representative sample spanning small/medium contexts, the two huge
# ones (RoomEditor, PyGameMakerIDE), and HTML/entity-heavy content --
# (context, source) pairs, in the raw entity-escaped <source> form.
_SAMPLE = [
    ("SpriteEditor", "Pencil"),
    ("RoomEditor", "Room Editor"),
    ("ThymioPlaygroundWindow", "Thymio Playground"),
    ("ObjectEventsPanel", "Object Events"),
    ("PyGameMakerIDE", "&amp;File"),
    ("PyGameMakerIDE", "E&amp;xit"),
    ("PyGameMakerIDE",
     "Object &apos;{0}&apos; imported successfully!"),
    ("PyGameMakerIDE", "Clean Project"),
]


def _parse_messages(content):
    """Yield (context, source, translation_inner_xml) for every message
    with a <source> tag, across every <context> block in the file."""
    for ctx_body in re.findall(r"<context>(.*?)</context>", content, re.S):
        name = re.search(r"<name>(.*?)</name>", ctx_body).group(1)
        for msg in re.findall(r"<message>(.*?)</message>", ctx_body, re.S):
            srcm = re.search(r"<source>(.*?)</source>", msg, re.S)
            if not srcm:
                continue
            transm = re.search(r"<translation[^>]*>(.*?)</translation>", msg, re.S)
            yield name, srcm.group(1), (transm.group(1) if transm else None)


def test_no_empty_unfinished_entries():
    content = TS_PATH.read_text(encoding="utf-8")
    assert '<translation type="unfinished"></translation>' not in content


def test_every_message_has_a_real_non_empty_translation():
    content = TS_PATH.read_text(encoding="utf-8")
    checked = 0
    for context, source, translation in _parse_messages(content):
        assert translation is not None, f"[{context}] {source!r}: no <translation> tag"
        stripped = translation.strip()
        assert stripped, f"[{context}] {source!r}: translation is empty"
        if source not in _COGNATE_SOURCES:
            assert stripped != source, (
                f"[{context}] {source!r}: translation equals the English source"
            )
        checked += 1
    assert checked == 1565, checked  # +2 Save As "Replace Project?" dialog, +1 HTML5 export crash dialog (2026-10-07)


def test_diacritics_survive():
    """Sanity check that Polish diacritics weren't stripped anywhere in
    the file (CLAUDE.md's accent-integrity rule, extended from French)."""
    content = TS_PATH.read_text(encoding="utf-8")
    diacritics = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
    found = diacritics & set(content)
    assert found, "no Polish diacritics found anywhere in pygm2_pl.ts"
    # Expect the common ones, not just one lonely character.
    assert len(found) >= 6, found


def test_context_and_message_count_matches_fr_reference():
    """pygm2_pl.ts must cover exactly the same (located-active) contexts
    and message count as the fr reference it was built from -- zero
    missing, zero extra (see CLAUDE.md's 2026-10-07 Polish session note)."""
    fr_path = REPO_ROOT / "translations" / "pygm2_fr.ts"
    fr_content = fr_path.read_text(encoding="utf-8")
    fr_contexts = {}
    for ctx_body in re.findall(r"<context>(.*?)</context>", fr_content, re.S):
        name = re.search(r"<name>(.*?)</name>", ctx_body).group(1)
        active = [m for m in re.findall(r"<message>(.*?)</message>", ctx_body, re.S)
                  if "<location" in m]
        if active:
            fr_contexts[name] = len(active)

    pl_content = TS_PATH.read_text(encoding="utf-8")
    pl_contexts = {}
    for ctx_body in re.findall(r"<context>(.*?)</context>", pl_content, re.S):
        name = re.search(r"<name>(.*?)</name>", ctx_body).group(1)
        msgs = re.findall(r"<message>(.*?)</message>", ctx_body, re.S)
        pl_contexts[name] = len(msgs)

    assert pl_contexts == fr_contexts, (
        set(fr_contexts) ^ set(pl_contexts),
        {k: (fr_contexts.get(k), pl_contexts.get(k))
         for k in set(fr_contexts) | set(pl_contexts)
         if fr_contexts.get(k) != pl_contexts.get(k)},
    )


def test_runtime_translate_resolves_sample():
    """SOURCES/_SAMPLE holds each <source>'s literal XML-entity-escaped
    text; the real self.tr() call at runtime sees the UNESCAPED Python
    string, so unescape before calling QCoreApplication.translate (the
    lrelease-decodes-entities landmine documented in
    docs/POLISH_I18N_PLAN.md)."""
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    assert QM_PATH.exists(), f"{QM_PATH} not compiled"
    app = QApplication.instance() or QApplication([])
    translator = QTranslator()
    assert translator.load(str(QM_PATH)), f"{QM_PATH.name} failed to load"
    app.installTranslator(translator)
    try:
        for context, source in _SAMPLE:
            runtime_source = unescape(source, {"&apos;": "'", "&quot;": '"'})
            resolved = QCoreApplication.translate(context, runtime_source)
            assert resolved != runtime_source, (
                f"[{context}] {source!r} did not resolve (still English)"
            )
            assert resolved, f"[{context}] {source!r} resolved empty"
    finally:
        app.removeTranslator(translator)
