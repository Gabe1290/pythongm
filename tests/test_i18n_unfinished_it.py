"""Regression test: it's 151 previously-unfinished translations.

Part of closing the gap docs/I18N_UNFINISHED_2026-08-10.md — third
executed slice (unit 3/7), after fr and de. Covers the shared
~148-string gap common to de/it/ru/sl/uk (see the plan doc), routed
across it's 6 split translation files. Several strings turned out to
already have a real Italian translation sitting in a SISTER split file
under the same (context, source) pair (BlocklyVisualProgrammingTab /
BlocklyWidget duplicated across blockly.ts and misc.ts; VisualScriptingArea
/ ActionListWidget duplicated across actions.ts and editors.ts) — those
were reused verbatim rather than re-translated, for wording consistency.

While cross-checking against German for meaning, found and fixed (in a
separate prior commit) 4 double-escaped translations that had landed in
de's own batch (a real bug, not an it issue) — this file's own values
are checked against the same double-escaping pattern below.

Uses a hand-rolled offscreen QApplication (no qapp fixture), matching
this repo's established audit-regression / i18n-fix convention, so this
runs even without pytest-qt.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANS_DIR = REPO_ROOT / "translations"

FILES = {
    "core": TRANS_DIR / "pygm2_it_core.ts",
    "editors": TRANS_DIR / "pygm2_it_editors.ts",
    "actions": TRANS_DIR / "pygm2_it_actions.ts",
    "blockly": TRANS_DIR / "pygm2_it_blockly.ts",
    "dialogs": TRANS_DIR / "pygm2_it_dialogs.ts",
    "misc": TRANS_DIR / "pygm2_it_misc.ts",
}

# (group, context, source) for all 151 strings this batch filled in.
SOURCES = [
    ("core", "PreferencesDialog", "IDE Edition"),
    ("core", "PreferencesDialog", "Edition:"),
    ("core", "PreferencesDialog",
     "The edition controls which tutorials are shown and the default\n"
     "block preset for new projects. Existing projects are not affected."),
    ("core", "PreferencesDialog", "General"),
    ("core", "PyGameMakerIDE",
     "&lt;h3&gt;License&lt;/h3&gt;&lt;p&gt;• &lt;b&gt;Source code:&lt;/b&gt; "
     "MIT License&lt;br&gt;• &lt;b&gt;Documentation:&lt;/b&gt; Creative "
     "Commons Attribution 4.0 (CC BY 4.0)&lt;br&gt;&lt;small&gt;Relicensed "
     "from GPLv3 to MIT + CC BY 4.0 to lower the barrier to reuse for "
     "educators, students, and downstream projects. See the "
     "&lt;code&gt;LICENSE&lt;/code&gt; and &lt;code&gt;LICENSE-docs&lt;/code&gt; "
     "files for full terms.&lt;/small&gt;&lt;/p&gt;&lt;p&gt;&amp;copy; "
     "Gabriel Thullen, 2025-2026&lt;/p&gt;"),
    ("core", "PyGameMakerIDE", "Opened playground: {0}"),
    ("core", "PyGameMakerIDE", "Failed to open playground editor: {0}"),
    ("core", "PyGameMakerIDE", "Floated: {0}"),
    ("core", "PyGameMakerIDE", "Reattached: {0}"),
    ("core", "PyGameMakerIDE", "Window mode: Tabbed"),
    ("core", "PyGameMakerIDE", "Window mode: Floating"),
    ("core", "PyGameMakerIDE", "⧉ Floating"),
    ("core", "PyGameMakerIDE",
     "Window mode: Floating. Click to switch all editors back into tabs "
     "(use this if a floating window has been dragged off-screen)."),
    ("core", "PyGameMakerIDE", "⊞ Tabbed"),
    ("core", "PyGameMakerIDE",
     "Window mode: Tabbed. Click to pop every editor out into its own window."),
    ("core", "PyGameMakerIDE", "Failed to open object editor:\n\n{0}"),
    ("core", "PyGameMakerIDE", "Opened sprite: {0}"),
    ("core", "PyGameMakerIDE", "Failed to open sprite editor: {0}"),
    ("core", "PyGameMakerIDE", "Export &amp;Aseba (Thymio) code..."),
    ("core", "PyGameMakerIDE", "Import Open &amp;Roberta XML..."),
    ("core", "PyGameMakerIDE", "Import &amp;GameMaker .gmk File..."),
    ("core", "PyGameMakerIDE", "Import Open Roberta XML"),
    ("core", "PyGameMakerIDE", "Open Roberta XML (*.xml)"),
    ("core", "PyGameMakerIDE", "Select Output Directory for Imported Project"),
    ("core", "PyGameMakerIDE", "Importing Open Roberta program..."),
    ("core", "PyGameMakerIDE", "\n\nWarnings:\n"),
    ("core", "PyGameMakerIDE",
     "Project &apos;{0}&apos; imported successfully!\nEvents: {1}, Actions: {2}{3}"),
    ("core", "PyGameMakerIDE", "Roberta import complete: {0}"),
    ("core", "PyGameMakerIDE", "Failed to import Open Roberta XML:\n{0}"),
    ("core", "PyGameMakerIDE", "Roberta import failed"),
    ("core", "PyGameMakerIDE", "Import GameMaker File"),
    ("core", "PyGameMakerIDE", "GameMaker Files (*.gmk)"),
    ("core", "PyGameMakerIDE", "Could not create output folder:\n{0}"),
    ("core", "PyGameMakerIDE", "Importing GameMaker file..."),
    ("core", "PyGameMakerIDE", "(no details)"),
    ("core", "PyGameMakerIDE", "Failed to import {0}:\n\n{1}"),
    ("core", "PyGameMakerIDE", "GMK import failed"),
    ("core", "PyGameMakerIDE", "(empty project)"),
    ("core", "PyGameMakerIDE", "\n  ...and {0} more"),
    ("core", "PyGameMakerIDE", "Imported &apos;{0}&apos; to:\n{1}\n\n{2}{3}"),
    ("core", "PyGameMakerIDE", "GMK import complete: {0}"),
    ("core", "PyGameMakerIDE", "New Project (Ctrl+N)"),
    ("core", "PyGameMakerIDE", "Open Project (Ctrl+O)"),
    ("core", "PyGameMakerIDE", "Save Project (Ctrl+S)"),
    ("core", "PyGameMakerIDE", "Test Game (F5)"),
    ("core", "PyGameMakerIDE", "Debug Game (F6)"),
    ("core", "PyGameMakerIDE", "Export Game…"),
    ("core", "PyGameMakerIDE", "Import Sprite…"),
    ("core", "PyGameMakerIDE", "Import Sound…"),
    ("core", "PyGameMakerIDE", "Tabbed"),
    ("core", "PyGameMakerIDE", "Toggle between Tabbed and Floating editor layouts"),
    ("core", "PyGameMakerIDE", "macOS Application (.app) - ✅ Available"),
    ("core", "PyGameMakerIDE", "macOS Application (.app) - ⚠️ Requires macOS"),
    ("core", "PyGameMakerIDE", "Android Package (.apk) - ✅ Available"),
    ("core", "PyGameMakerIDE", "Android Package (.apk) - ✅ Available (via WSL)"),
    ("core", "PyGameMakerIDE", "Android Package (.apk) - ⚠️ Requires WSL (not detected)"),
    ("core", "PyGameMakerIDE", "Android Package (.apk) - ⚠️ Requires Linux or macOS"),
    ("core", "PyGameMakerIDE", "iOS App (.ipa) - ✅ Available (macOS only)"),
    ("core", "PyGameMakerIDE", "iOS App (.ipa) - ⚠️ Requires macOS with Xcode"),
    ("core", "PyGameMakerIDE", "This export format is not yet available."),
    ("core", "PyGameMakerIDE", "Export cancelled"),
    ("core", "PyGameMakerIDE", "Building iOS App"),
    ("core", "PyGameMakerIDE", "Preparing iOS export..."),
    ("core", "PyGameMakerIDE", "iOS Export Complete"),
    ("core", "PyGameMakerIDE", "iOS Export Failed"),
    ("core", "PyGameMakerIDE", "Open the output folder?"),
    ("core", "PyGameMakerIDE", "iOS export cancelled"),
    ("core", "PyGameMakerIDE", "Exporting Aseba code..."),
    ("core", "PyGameMakerIDE", "Aseba Export Failed"),
    ("core", "PyGameMakerIDE", "Failed to export Aseba code:\n\n{0}"),
    ("core", "PyGameMakerIDE", "Aseba export failed"),
    ("core", "PyGameMakerIDE", "Aseba Export"),
    ("core", "PyGameMakerIDE",
     "No Thymio objects found in this project, so no Aseba code was "
     "generated. Add a Thymio object to the project and try again."),
    ("core", "PyGameMakerIDE", "Aseba export: nothing to export"),
    ("core", "PyGameMakerIDE", "Aseba export complete"),
    ("core", "PyGameMakerIDE", "Aseba Export Complete"),
    ("core", "PyGameMakerIDE",
     "Aseba .aesl files written to:\n{0}\n\nWould you like to open the output folder?"),
    ("core", "PyGameMakerIDE", "Cancelling..."),

    ("editors", "ActionListWidget", "Actions are now managed through the Events panel"),
    ("editors", "BackgroundLayersDialog", "Background Layers"),
    ("editors", "BackgroundLayersDialog", "Background {0}"),
    ("editors", "BackgroundLayersDialog", "Layer:"),
    ("editors", "BackgroundLayersDialog", "Layer Properties"),
    ("editors", "BackgroundLayersDialog", "Foreground:"),
    ("editors", "BackgroundLayersDialog", "Image:"),
    ("editors", "BackgroundLayersDialog", "Stretch:"),
    ("editors", "BackgroundLayersDialog", "Tile H:"),
    ("editors", "BackgroundLayersDialog", "Tile V:"),
    ("editors", "BaseEditor", "🪟 Float"),
    ("editors", "BaseEditor", "Open this editor in its own window"),
    ("editors", "BaseEditor", "Auto-saved: {0}"),
    ("editors", "EnhancedPropertiesPanel", "Backgrounds:"),
    ("editors", "ObjectEditor",
     "Blockly visual programming is not available.\n\nError: {0}"),
    ("editors", "ObjectEditor", "Edit mode: changes apply automatically as you type"),
    ("editors", "ObjectEditor", "No event methods found in the code"),
    ("editors", "ObjectEditor", "{0} events"),
    ("editors", "ObjectEventsPanel", "🤖 Thymio Events"),
    ("editors", "ObjectEventsPanel", "🤖 Visual Selector..."),
    ("editors", "ObjectEventsPanel", "Alarm Event Exists"),
    ("editors", "ObjectEventsPanel", "Alarm {0} event already exists."),
    ("editors", "ObjectEventsPanel",
     "Cannot add actions directly to Alarm.\n\nPlease add actions to a "
     "specific alarm number instead:\nRight-click on Alarm 0, Alarm 1, etc."),
    ("editors", "ObjectEventsPanel", "Error"),
    ("editors", "ObjectEventsPanel", "Could not open action editor: {0}"),
    ("editors", "RoomEditor", "Tile Palette..."),
    ("editors", "RoomEditor", "↔ Shift All"),
    ("editors", "RoomEditor", "Shift all instances by an X/Y offset"),
    ("editors", "RoomEditor", "🪟 Float"),
    ("editors", "RoomEditor", "Open this editor in its own window"),
    ("editors", "RoomEditor", "Shift All"),
    ("editors", "RoomEditor", "No instances to shift."),
    ("editors", "RoomEditor", "Shift All Instances"),
    ("editors", "RoomEditor", "X offset:"),
    ("editors", "RoomEditor", "Y offset:"),
    ("editors", "RoomEditor", "Shifted all instances by ({0}, {1})"),
    ("editors", "RoomEditor", "Tile selected - Click in room to paint"),
    ("editors", "RoomEditor", "Tile mode cleared"),

    ("actions", "VisualScriptingArea",
     "Visual scripting is now managed through the Events panel"),

    ("blockly", "BlocklyWidget", "Error loading Blockly"),
    ("blockly", "DetachedBlocklyWindow", "Visual Block Programming (Detached)"),

    ("dialogs", "AssetTreeWidget",
     "No project loaded.\nUse File → New Project or File → Open Project to begin."),
    ("dialogs", "AssetTreeWidget", "Playgrounds"),
    ("dialogs", "AssetTreeWidget", "💾 Export as PNG…"),
    ("dialogs", "AssetTreeWidget", "📋 Duplicate"),
    ("dialogs", "AssetTreeWidget", "Sprite &apos;{0}&apos; has no image file."),
    ("dialogs", "AssetTreeWidget", "File Not Found"),
    ("dialogs", "AssetTreeWidget", "Image file not found: {0}"),
    ("dialogs", "AssetTreeWidget", "Export Sprite as PNG"),
    ("dialogs", "AssetTreeWidget", "PNG Images (*.png)"),
    ("dialogs", "AssetTreeWidget", "Failed to export: {0}"),
    ("dialogs", "NewProjectDialog", "Empty Project"),
    ("dialogs", "NewProjectDialog", "With Game Over Screen"),
    ("dialogs", "NewProjectDialog", "Template:"),
    ("dialogs", "TutorialDialog", "Select a tutorial and click Open (or double-click):"),
    ("dialogs", "TutorialDialog", "Open"),

    ("misc", "BlocklyVisualProgrammingTab",
     "Editor is detached. Close the detached window to return it here."),
    ("misc", "BlocklyVisualProgrammingTab", "📥 Attach"),
    ("misc", "BlocklyVisualProgrammingTab", "Return editor to the tab"),
    ("misc", "BlocklyVisualProgrammingTab", "⬜ Detach"),
    ("misc", "BlocklyVisualProgrammingTab", "Open Blockly editor in a separate window"),
    ("misc", "BlocklyWidget", "⬜ Detach"),
    ("misc", "BlocklyWidget", "Open Blockly editor in a separate window"),
    ("misc", "BlocklyWidget", "Drag blocks from the toolbox on the left to create game logic!"),
    ("misc", "BlocklyWidget", "Error loading Blockly"),
    ("misc", "BlocklyWidget", "Blocks updated - {0} events"),
    ("misc", "BlocklyWidget", "No events to load"),
    ("misc", "BlocklyWidget", "Loaded {0} events as blocks"),
    ("misc", "BlocklyWidget", "Loaded {0} events - some may not have block equivalents"),
    ("misc", "BlocklyWidget", "Configuration applied: {0} blocks, {1} categories"),
    ("misc", "ObjectPropertiesPanel", "&lt;no parent&gt;"),
    ("misc", "ObjectPropertiesPanel", "Parent object (inherits collision events)"),
    ("misc", "ObjectPropertiesPanel", "Parent:"),
]

assert len(SOURCES) == 151, len(SOURCES)

# "Open Roberta XML (*.xml)" is a deliberately-untranslated file-dialog
# filter (proper name + literal glob pattern), same exception de made.
_COGNATES = {
    ("core", "PyGameMakerIDE", "Open Roberta XML (*.xml)"),
}


def _get_context_block(content, name):
    m = re.search(
        r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
        content, re.S,
    )
    return m.group(0) if m else None


def test_no_empty_unfinished_entries_remain():
    for path in FILES.values():
        content = path.read_text(encoding="utf-8")
        assert '<translation type="unfinished"></translation>' not in content, path.name


def test_no_double_escaped_translations():
    """The de batch (commit 3928e32) shipped 4 double-escaped values
    (fixed separately) -- guard the it batch against the same mistake."""
    for path in FILES.values():
        content = path.read_text(encoding="utf-8")
        assert "&amp;amp;" not in content, f"double-escaped '&' in {path.name}"
        assert "&amp;lt;" not in content, f"double-escaped '<' in {path.name}"
        assert "&amp;gt;" not in content, f"double-escaped '>' in {path.name}"


def test_every_source_has_a_real_non_empty_translation():
    contents = {g: p.read_text(encoding="utf-8") for g, p in FILES.items()}
    for group, context, source in SOURCES:
        block = _get_context_block(contents[group], context)
        assert block is not None, f"[{group}] missing {context} context"
        m = re.search(
            r"<source>" + re.escape(source) + r"</source>\s*"
            r"<translation>(.*?)</translation>",
            block, re.S,
        )
        assert m is not None, f"[{group}/{context}] {source!r}: no real <translation> tag"
        translated = m.group(1).strip()
        assert translated, f"[{group}/{context}] {source!r}: translation is empty"
        if (group, context, source) not in _COGNATES:
            assert translated != source, (
                f"[{group}/{context}] {source!r}: translation equals the English source"
            )


def test_runtime_translate_resolves_every_string():
    """SOURCES holds each <source>'s literal XML-entity-escaped text (for
    the regex tests above); the real self.tr() call at runtime sees the
    UNESCAPED Python string, so unescape before calling
    QCoreApplication.translate (same landmine as the fr/de batches)."""
    from xml.sax.saxutils import unescape
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    qm_by_group = {g: p.with_suffix(".qm") for g, p in FILES.items()}
    for group, path in qm_by_group.items():
        assert path.exists(), f"{path} not compiled"
        translator = QTranslator()
        assert translator.load(str(path)), f"{path.name} failed to load"
        app.installTranslator(translator)
        try:
            for g, context, source in SOURCES:
                if g != group:
                    continue
                runtime_source = unescape(source, {"&apos;": "'", "&quot;": '"'})
                resolved = QCoreApplication.translate(context, runtime_source)
                is_cognate = (g, context, source) in _COGNATES
                assert resolved != runtime_source or is_cognate, (
                    f"[{group}/{context}] {source!r} did not resolve (still English)"
                )
                assert resolved, f"[{group}/{context}] {source!r} resolved empty"
                assert "&amp;" not in resolved, (
                    f"[{group}/{context}] {source!r} resolved double-escaped: {resolved!r}"
                )
        finally:
            app.removeTranslator(translator)
