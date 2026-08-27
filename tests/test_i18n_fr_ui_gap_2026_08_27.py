"""Regression test: fr's 167 previously-untranslated live UI strings.

Found by a systematic audit: a fresh `pyside6-lupdate` extraction over the
live source tree, cross-referenced against translations/pygm2_fr.ts
(matching on (context, source), with a fallback to any-context source-text
match to avoid false positives from the known self.ide/PyGameMakerIDE
lupdate misattribution -- see test_self_ide_context_fix.py). 167 of 1496
live strings had no usable French translation anywhere: mostly whole
dialogs that shipped with zero i18n coverage (BlockWorldEditorWindow,
FindReplaceDialog, TrashDialog, OrphanedFilesDialog, TilePaletteDialog,
UnusedAssetsDialog), plus scattered gaps in older contexts.

Two real bugs were found and fixed while filling this gap, both now
covered below:

1. scripts/gen_translation_ts.py's add_partial_context() treated a
   type="vanished" message's source text as "already present", so a live
   string shadowed only by a stale vanished duplicate was silently
   skipped forever (5 of the 167 were caught by this before the tool
   itself was fixed). test_no_vanished_source_shadows_a_live_one guards
   the specific fr.ts symptom; the tool's own logic isn't separately unit
   tested here (no existing precedent for testing the generator tool
   itself -- this test's coverage of pygm2_fr.ts is the practical guard).
2. Six of these strings are called via self.ide.tr(...) in
   core/ide_exporters.py -- the same dead-context pattern documented in
   test_self_ide_context_fix.py, freshly reproduced because lupdate always
   misattributes self.<member>.tr() calls to a synthetic context name
   ("self.ide") it cannot resolve to the runtime class. Filed under the
   real PyGameMakerIDE context instead, matching that fix's precedent.
3. Self-inflicted while translating: 4 mnemonic menu items got their
   translation VALUE written with an already-escaped `&amp;` (copied from
   the source key by habit) instead of a real `&` character --
   TranslationBuilder.add_partial_context's escape() call then
   double-escaped it to `&amp;amp;`, which is valid XML and compiles
   silently but displays the literal text "&amp;projet" instead of a
   working underlined mnemonic. Same class of bug as the zh landmine
   documented in CLAUDE.md. test_no_double_escaped_entities guards this
   for the whole file, not just this batch.

Uses a hand-rolled offscreen QApplication (no qapp fixture), matching this
repo's established audit-regression / i18n-fix convention, so this runs
even without pytest-qt.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TS_PATH = REPO_ROOT / "translations" / "pygm2_fr.ts"
QM_PATH = REPO_ROOT / "translations" / "pygm2_fr.qm"

# (context, source) for all 167 strings this batch filled in. `source` is
# the literal XML-entity-escaped text as it appears between <source> tags.
SOURCES = [
    ('PyGameMakerIDE', '&amp;Find...'),
    ('PyGameMakerIDE', 'Find and &amp;Replace...'),
    ('PyGameMakerIDE', '&amp;Build Game...'),
    ('PyGameMakerIDE', 'Build and &amp;Run'),
    ('PyGameMakerIDE', '&amp;Restore Deleted Assets...'),
    ('PyGameMakerIDE', 'Find &amp;Unused Assets...'),
    ('PyGameMakerIDE', 'Clean &amp;Project'),
    ('PyGameMakerIDE', 'Find &amp;Orphaned Files...'),
    ('PyGameMakerIDE', 'Filter assets…'),
    ('PyGameMakerIDE', 'Could not open sample'),
    ('PyGameMakerIDE', 'Failed to copy the bundled sample to:\n{0}\n\nError:\n{1}'),
    ('PyGameMakerIDE', 'Sample copied to: {0}'),
    ('PyGameMakerIDE', 'Project Too New'),
    ('PyGameMakerIDE', 'This project was made with a newer version of PyGameMaker (format {0}.{1}). Please update PyGameMaker to open it.'),
    ('PyGameMakerIDE', 'Note: {n} action(s) aren&apos;t supported by this export target and were skipped — the exported game will not perform them:\n{actions}'),
    ('PyGameMakerIDE', 'Please open or create a project first before testing an object.'),
    ('PyGameMakerIDE', 'Play Object: {0}'),
    ('PyGameMakerIDE', 'Failed to prepare object test: {0}'),
    ('PyGameMakerIDE', 'Include Assets'),
    ('PyGameMakerIDE', 'Optimize for Release'),
    ('PyGameMakerIDE', 'Include Debug Info'),
    ('PyGameMakerIDE', 'Building Game'),
    ('PyGameMakerIDE', 'Preparing build...'),
    ('PyGameMakerIDE', 'Build Complete'),
    ('PyGameMakerIDE', 'Build Failed'),
    ('PyGameMakerIDE', 'Find is only available in the code editor'),
    ('PyGameMakerIDE', 'Please open a project first.'),
    ('PyGameMakerIDE', 'Restored: {0}'),
    ('PyGameMakerIDE', 'Moved {0} unused asset(s) to Trash'),
    ('PyGameMakerIDE', 'Clean Project'),
    ('PyGameMakerIDE', 'Removed {0} leftover temporary file(s):\n\n{1}'),
    ('PyGameMakerIDE', 'Removed {0} leftover temporary file(s)'),
    ('PyGameMakerIDE', 'Nothing to clean — no leftover temporary files found.'),
    ('PyGameMakerIDE', 'Opened script: {0}'),
    ('PyGameMakerIDE', 'Failed to open script editor: {0}'),
    ('PyGameMakerIDE', 'Opened sound: {0}'),
    ('PyGameMakerIDE', 'Failed to open sound editor: {0}'),
    ('PyGameMakerIDE', 'Opened background: {0}'),
    ('PyGameMakerIDE', 'Failed to open background editor: {0}'),
    ('PyGameMakerIDE', 'Opened font: {0}'),
    ('PyGameMakerIDE', 'Failed to open font editor: {0}'),
    ('OrphanedFilesDialog', 'Orphaned Files'),
    ('OrphanedFilesDialog', 'Physical files under sprites/sounds/backgrounds/fonts/thumbnails that nothing in this project references — usually left behind by a deleted asset entry, or a file copied in by hand. Trashed files can be restored below until permanently removed.'),
    ('OrphanedFilesDialog', 'Found on disk:'),
    ('OrphanedFilesDialog', 'Move Selected to Trash'),
    ('OrphanedFilesDialog', 'Trashed:'),
    ('OrphanedFilesDialog', 'Restore'),
    ('OrphanedFilesDialog', 'Delete Permanently'),
    ('OrphanedFilesDialog', 'Empty'),
    ('OrphanedFilesDialog', 'No orphaned files found.'),
    ('OrphanedFilesDialog', '{0}  —  deleted {1}'),
    ('OrphanedFilesDialog', 'Move to Trash'),
    ('OrphanedFilesDialog', 'Move {0} orphaned file(s) to the trash?'),
    ('OrphanedFilesDialog', 'Restore Failed'),
    ('OrphanedFilesDialog', 'Could not restore &apos;{0}&apos; — a file already exists there. Move or remove it first, then try again.'),
    ('OrphanedFilesDialog', 'Permanently delete &apos;{0}&apos;? This cannot be undone.'),
    ('OrphanedFilesDialog', 'Empty Trash'),
    ('OrphanedFilesDialog', 'Permanently delete every trashed orphaned file? This cannot be undone.'),
    ('BlockWorldEditorWindow', 'Block World'),
    ('BlockWorldEditorWindow', 'Could not load this room&apos;s saved blocks ({0}); starting empty.'),
    ('BlockWorldEditorWindow', 'Block World Editor'),
    ('BlockWorldEditorWindow', 'This room has no project/name to save to.'),
    ('BlockWorldEditorWindow', 'Failed to save blocks:\n{0}'),
    ('BlockWorldEditorWindow', 'Saved to {0}'),
    ('BlockWorldEditorWindow', 'There are no blocks to clear.'),
    ('BlockWorldEditorWindow', 'Clear World'),
    ('BlockWorldEditorWindow', 'Remove every block in this room? This can be undone.'),
    ('BlockWorldEditorWindow', 'WASD fly | middle-drag to look | wheel to pitch | Space/Shift layer up/down | left-click place | right-click / Delete break | Ctrl+Z / Ctrl+Y undo/redo | Ctrl+S save'),
    ('BlockWorldEditorWindow', 'Blocks'),
    ('BlockWorldEditorWindow', 'Save blocks (Ctrl+S)'),
    ('BlockWorldEditorWindow', '🗑️ Clear World'),
    ('BlockWorldEditorWindow', 'Remove every block in this room'),
    ('BlockWorldEditorWindow', 'cell {0}   layer {1}   angle {2:.0f}   pitch {3:+.0f}   block {4}   undo {5}'),
    ('BlockWorldEditorWindow', 'Save changes to this room&apos;s blocks before closing?'),
    ('FindReplaceDialog', 'Find'),
    ('FindReplaceDialog', 'Find:'),
    ('FindReplaceDialog', 'Replace:'),
    ('FindReplaceDialog', 'Case sensitive'),
    ('FindReplaceDialog', 'Whole words'),
    ('FindReplaceDialog', 'Find Next'),
    ('FindReplaceDialog', 'Find Previous'),
    ('FindReplaceDialog', 'Replace'),
    ('FindReplaceDialog', 'Replace All'),
    ('FindReplaceDialog', 'Find and Replace'),
    ('FindReplaceDialog', 'Phrase not found'),
    ('FindReplaceDialog', '%d replacement(s) made'),
    ('TrashDialog', 'Trash'),
    ('TrashDialog', 'Deleted assets stay here until you permanently remove them.'),
    ('TrashDialog', 'Restore'),
    ('TrashDialog', 'Delete Permanently'),
    ('TrashDialog', 'Empty Trash'),
    ('TrashDialog', '{0} / {1}  —  deleted {2}'),
    ('TrashDialog', 'Deleting this cleared a reference in: {0}. Restoring brings the file back but does not re-link that reference automatically.'),
    ('TrashDialog', 'Restore Failed'),
    ('TrashDialog', 'Could not restore &apos;{0}&apos; — an asset with that name already exists. Rename or remove it first, then try again.'),
    ('TrashDialog', 'Permanently delete &apos;{0}&apos;? This cannot be undone.'),
    ('TrashDialog', 'Permanently delete everything in the trash? This cannot be undone.'),
    ('TilePaletteDialog', 'Tilesheet grid'),
    ('TilePaletteDialog', 'Use as tileset'),
    ('TilePaletteDialog', 'H sep:'),
    ('TilePaletteDialog', 'Horizontal gap between tiles, in pixels (set to 1 for sheets with 1-px grid lines)'),
    ('TilePaletteDialog', 'V sep:'),
    ('TilePaletteDialog', 'Vertical gap between tiles, in pixels'),
    ('TilePaletteDialog', 'H offset:'),
    ('TilePaletteDialog', 'Left-edge offset before the first tile column, in pixels'),
    ('TilePaletteDialog', 'V offset:'),
    ('TilePaletteDialog', 'Top-edge offset before the first tile row, in pixels'),
    ('ObjectEventsPanel', 'Paste {0} Actions'),
    ('ObjectEventsPanel', 'Paste Action'),
    ('ObjectEventsPanel', 'Copy {0} Actions'),
    ('ObjectEventsPanel', 'Copy Action'),
    ('ObjectEventsPanel', 'Add Key…'),
    ('ObjectEventsPanel', 'Add Alarm'),
    ('ObjectEventsPanel', 'Cannot add actions directly to &apos;{0}&apos;.\n\nRight-click on {1} and add the action there instead.'),
    ('ObjectEventsPanel', '(empty comment)'),
    ('RoomEditor', 'Open another tile palette (up to {0})'),
    ('RoomEditor', '🧱 Block Edit'),
    ('RoomEditor', 'Edit this room&apos;s Block World voxels'),
    ('RoomEditor', 'Block World'),
    ('RoomEditor', 'Save this room first, so its blocks have a name to save under.'),
    ('RoomEditor', 'Tile palette limit reached ({0})'),
    ('RoomEditor', 'Tile Palette {0}'),
    ('RoomEditor', 'Selected {0} at ({1}, {2}) -- {3} objects stacked here, click again to cycle ({4}/{5})'),
    ('UnusedAssetsDialog', 'Unused Assets'),
    ('UnusedAssetsDialog', 'Assets not referenced by any object, room, or action. Deleted items go to the Trash, not removed permanently. References inside execute_code/execute_script can&apos;t be detected and may cause false positives here. Rooms are listed as &quot;not explicitly navigated to&quot; rather than unused — a starting room is often never referenced by name anywhere, so that alone doesn&apos;t mean it&apos;s safe to delete.'),
    ('UnusedAssetsDialog', 'Move Selected to Trash'),
    ('UnusedAssetsDialog', 'Rooms — not explicitly navigated to ({0})'),
    ('UnusedAssetsDialog', 'No unused assets found.'),
    ('UnusedAssetsDialog', 'Move to Trash'),
    ('UnusedAssetsDialog', 'Move {0} unused asset(s) to the Trash?'),
    ('BackgroundEditor', 'Tile horizontally'),
    ('BackgroundEditor', 'Tile vertically'),
    ('BackgroundEditor', '(image not found)'),
    ('BackgroundEditor', '(could not load image)'),
    ('BackgroundEditor', '(no file)'),
    ('BackgroundEditor', '(unknown)'),
    ('SoundEditor', 'Volume:'),
    ('SoundEditor', 'Loop'),
    ('SoundEditor', '▶ Play'),
    ('SoundEditor', '■ Stop'),
    ('SoundEditor', '(no file)'),
    ('AssetTreeWidget', '🗑️ Delete {0} Selected'),
    ('AssetTreeWidget', '\n  … and {0} more'),
    ('AssetTreeWidget', 'Delete {0} Assets'),
    ('AssetTreeWidget', 'Delete these {0} asset(s)?\n\n{1}\n\nThey will be moved to the project&apos;s trash and can be restored later.'),
    ('FontEditor', 'Font family:'),
    ('FontEditor', 'Bold'),
    ('FontEditor', 'Italic'),
    ('FontEditor', 'The quick brown fox'),
    ('ActionConfigDialog', 'Applies to'),
    ('ActionConfigDialog', 'Self'),
    ('ActionConfigDialog', 'Other'),
    ('GM80ActionDialog', 'Applies to'),
    ('GM80ActionDialog', 'Self'),
    ('GM80ActionDialog', 'Other'),
    ('EnhancedPropertiesPanel', 'Yes'),
    ('EnhancedPropertiesPanel', 'No'),
    ('ObjectEditor', '▶ Play Object'),
    ('ObjectEditor', 'Run this object alone in a small test room'),
    ('ObjectPropertiesPanel', 'Stay destroyed'),
    ('ObjectPropertiesPanel', 'Once destroyed, this object stays gone when the room restarts (resets on a full game restart)'),
    ('PyGameMakerIDE', 'Offline Python Runtime?'),
    ('PyGameMakerIDE', 'This game uses Python code (execute_code), which normally loads its runtime from the internet the first time the exported game is opened.\n\nBundle it into the .html file instead, so the game works with no internet at all (e.g. locked-down school networks)?\n\nAdds about 15-20 MB to the exported file. Needs internet once now, to download and cache it (cached afterwards for future exports).'),
    ('PyGameMakerIDE', 'Exporting Kivy project...'),
    ('PyGameMakerIDE', 'Kivy project exported to:\n{0}'),
    ('PyGameMakerIDE', 'Would you like to open the export directory?'),
    ('PyGameMakerIDE', 'Kivy export complete'),
]

assert len(SOURCES) == 167, len(SOURCES)


def _get_context_block(content, name):
    m = re.search(
        r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
        content, re.S,
    )
    return m.group(0) if m else None


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


def test_no_double_escaped_entities():
    """A translation VALUE must use real unescaped characters (&, <, >,
    ', ") -- TranslationBuilder.add_partial_context's escape() call
    escapes it for you. Writing an already-escaped &amp;/&apos;/&quot;
    (copied from the <source> key by habit) gets double-escaped into
    e.g. &amp;amp;, which is valid XML and compiles silently but displays
    the literal text "&amp;projet" to the user instead of a working
    mnemonic. Whole-file check, not scoped to this batch -- this exact
    bug was found in a pre-existing, unrelated entry (the Aseba/Thymio
    export menu item) while fixing this one, so it's worth guarding
    everywhere, not just SOURCES above."""
    content = TS_PATH.read_text(encoding="utf-8")
    for bad in ("&amp;amp;", "&amp;apos;", "&amp;quot;", "&amp;lt;", "&amp;gt;"):
        assert bad not in content, f"double-escaped entity found: {bad!r}"


def test_no_vanished_source_shadows_a_live_one():
    """A type="vanished" <message> does not count as "the source is
    translated" -- lrelease drops vanished entries from the compiled
    .qm, and (worse) a live and a vanished <message> sharing the same
    <source> text in the same context is undefined/inconsistent at
    compile time in practice (observed: lrelease preferred the dead
    vanished one for several of this batch's entries, silently
    shadowing the real translation, until the stale vanished duplicates
    were deleted rather than left alongside the new active ones)."""
    content = TS_PATH.read_text(encoding="utf-8")
    contexts = re.findall(r"<context>(.*?)</context>", content, re.S)
    for ctx in contexts:
        cname = re.search(r"<name>(.*?)</name>", ctx).group(1)
        messages = re.findall(r"<message>(.*?)</message>", ctx, re.S)
        by_src = {}
        for m in messages:
            srcm = re.search(r"<source>(.*?)</source>", m, re.S)
            if not srcm:
                continue
            by_src.setdefault(srcm.group(1), []).append(m)
        for src, msgs in by_src.items():
            if len(msgs) < 2:
                continue
            vanished = [mm for mm in msgs if 'type="vanished"' in mm]
            active = [mm for mm in msgs if 'type="vanished"' not in mm]
            assert not (vanished and active), (
                f"[{cname}] {src!r}: both an active and a vanished "
                "<message> share this source text"
            )
