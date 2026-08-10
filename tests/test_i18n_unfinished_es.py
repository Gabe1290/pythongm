"""Regression test: es's 309 previously-unfinished translations.

Part of closing the gap docs/I18N_UNFINISHED_2026-08-10.md — seventh
and final executed slice (unit 7/7), after fr, de, it, ru, sl, and uk.
es is the largest and most independent of the seven languages: only
~132 of its 309 unfinished entries overlapped the ~148-string list
shared by de/it/ru/sl/uk (PreferencesDialog + PyGameMakerIDE, almost
entirely); the other ~177 are es-specific gaps in contexts none of the
other six languages' batches ever touched (the Thymio Playground editor,
the Sprite Editor, and several smaller view/block/tile config dialogs).
The plan doc's original count (294) was stale by the time this session
picked it up — re-counted directly against the file (309) before
starting, and corrected here rather than forcing the old number.

Landed in 5 stages (own commits each, per this repo's session-limit
discipline), since es ships as a single monolithic pygm2_es.ts (unlike
the other six split-shipping languages):
1. PreferencesDialog + PyGameMakerIDE (78, the shared-list portion)
2. AssetTreeWidget/BackgroundLayersDialog/BaseEditor/BlocklyWidget/
   EnhancedPropertiesPanel/NewProjectDialog/ObjectEditor/
   ObjectEventsPanel/ObjectPropertiesPanel/RoomEditor/TutorialDialog (63)
3. The Thymio Playground editor: PlaygroundColorManager/PlaygroundEditor/
   PlaygroundElementProperties/PlaygroundRunnerWindow/
   PlaygroundToolPalette (62, entirely es-specific)
4. SpriteEditor (58, entirely es-specific)
5. ViewConfigDialog/BaseBlockConfigDialog/TilePaletteDialog/
   FrameTimeline/ResizeCanvasDialog/FloatableEditorMixin/
   ForegroundBackgroundSwatch/ActionConfigDialog/ColorPaletteWidget/
   KeySelectorDialog/TileGridWidget (48)

Landmine found during stage 5: BaseBlockConfigDialog's "Preset:" has an
<extracomment> tag between <source> and <translation> that a naive
"<source>...</source>\\n<translation ...>" string match skips over --
the initial per-context count (47) silently missed it; re-derived with
a comment-tolerant scan before translating and it lined up with the
robust file-wide total (48). Worth remembering for any future .ts
surgery: don't assume <translation> immediately follows </source>.

Uses a hand-rolled offscreen QApplication (no qapp fixture), matching
this repo's established audit-regression / i18n-fix convention, so this
runs even without pytest-qt.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TS_PATH = REPO_ROOT / "translations" / "pygm2_es.ts"
QM_PATH = REPO_ROOT / "translations" / "pygm2_es.qm"

# (context, source) for all 309 strings this batch filled in.
SOURCES = [
    ('PreferencesDialog', 'IDE Edition'),
    ('PreferencesDialog', 'Edition:'),
    ('PreferencesDialog',
     'The edition controls which tutorials are shown and the default\n'
     'block preset for new projects. Existing projects are not affected.'),
    ('PreferencesDialog', 'General'),
    ('PyGameMakerIDE',
     '&lt;h3&gt;License&lt;/h3&gt;&lt;p&gt;• &lt;b&gt;Source code:&lt;/b&gt; '
     'MIT License&lt;br&gt;• &lt;b&gt;Documentation:&lt;/b&gt; Creative '
     'Commons Attribution 4.0 (CC BY 4.0)&lt;br&gt;&lt;small&gt;Relicensed '
     'from GPLv3 to MIT + CC BY 4.0 to lower the barrier to reuse for '
     'educators, students, and downstream projects. See the '
     '&lt;code&gt;LICENSE&lt;/code&gt; and &lt;code&gt;LICENSE-docs&lt;/code&gt; '
     'files for full terms.&lt;/small&gt;&lt;/p&gt;&lt;p&gt;&amp;copy; '
     'Gabriel Thullen, 2025-2026&lt;/p&gt;'),
    ('PyGameMakerIDE', 'Opened playground: {0}'),
    ('PyGameMakerIDE', 'Failed to open playground editor: {0}'),
    ('PyGameMakerIDE', 'Floated: {0}'),
    ('PyGameMakerIDE', 'Reattached: {0}'),
    ('PyGameMakerIDE', 'Window mode: Tabbed'),
    ('PyGameMakerIDE', 'Window mode: Floating'),
    ('PyGameMakerIDE', '⧉ Floating'),
    ('PyGameMakerIDE',
     'Window mode: Floating. Click to switch all editors back into tabs '
     '(use this if a floating window has been dragged off-screen).'),
    ('PyGameMakerIDE', '⊞ Tabbed'),
    ('PyGameMakerIDE',
     'Window mode: Tabbed. Click to pop every editor out into its own window.'),
    ('PyGameMakerIDE', 'Failed to open object editor:\n\n{0}'),
    ('PyGameMakerIDE', 'Opened sprite: {0}'),
    ('PyGameMakerIDE', 'Failed to open sprite editor: {0}'),
    ('PyGameMakerIDE', 'Export &amp;Aseba (Thymio) code...'),
    ('PyGameMakerIDE', 'Import Open &amp;Roberta XML...'),
    ('PyGameMakerIDE', 'Import &amp;GameMaker .gmk File...'),
    ('PyGameMakerIDE', 'Import Open Roberta XML'),
    ('PyGameMakerIDE', 'Open Roberta XML (*.xml)'),
    ('PyGameMakerIDE', 'Select Output Directory for Imported Project'),
    ('PyGameMakerIDE', 'Importing Open Roberta program...'),
    ('PyGameMakerIDE', '\n\nWarnings:\n'),
    ('PyGameMakerIDE',
     'Project &apos;{0}&apos; imported successfully!\nEvents: {1}, Actions: {2}{3}'),
    ('PyGameMakerIDE', 'Roberta import complete: {0}'),
    ('PyGameMakerIDE', 'Failed to import Open Roberta XML:\n{0}'),
    ('PyGameMakerIDE', 'Roberta import failed'),
    ('PyGameMakerIDE', 'Import GameMaker File'),
    ('PyGameMakerIDE', 'GameMaker Files (*.gmk)'),
    ('PyGameMakerIDE', 'Could not create output folder:\n{0}'),
    ('PyGameMakerIDE', 'Importing GameMaker file...'),
    ('PyGameMakerIDE', '(no details)'),
    ('PyGameMakerIDE', 'Failed to import {0}:\n\n{1}'),
    ('PyGameMakerIDE', 'GMK import failed'),
    ('PyGameMakerIDE', '(empty project)'),
    ('PyGameMakerIDE', '\n  ...and {0} more'),
    ('PyGameMakerIDE', 'Imported &apos;{0}&apos; to:\n{1}\n\n{2}{3}'),
    ('PyGameMakerIDE', 'GMK import complete: {0}'),
    ('PyGameMakerIDE', 'New Project (Ctrl+N)'),
    ('PyGameMakerIDE', 'Open Project (Ctrl+O)'),
    ('PyGameMakerIDE', 'Save Project (Ctrl+S)'),
    ('PyGameMakerIDE', 'Test Game (F5)'),
    ('PyGameMakerIDE', 'Debug Game (F6)'),
    ('PyGameMakerIDE', 'Export Game…'),
    ('PyGameMakerIDE', 'Import Sprite…'),
    ('PyGameMakerIDE', 'Import Sound…'),
    ('PyGameMakerIDE', 'Tabbed'),
    ('PyGameMakerIDE', 'Toggle between Tabbed and Floating editor layouts'),
    ('PyGameMakerIDE', 'macOS Application (.app) - ✅ Available'),
    ('PyGameMakerIDE', 'macOS Application (.app) - ⚠️ Requires macOS'),
    ('PyGameMakerIDE', 'Android Package (.apk) - ✅ Available'),
    ('PyGameMakerIDE', 'Android Package (.apk) - ✅ Available (via WSL)'),
    ('PyGameMakerIDE', 'Android Package (.apk) - ⚠️ Requires WSL (not detected)'),
    ('PyGameMakerIDE', 'Android Package (.apk) - ⚠️ Requires Linux or macOS'),
    ('PyGameMakerIDE', 'iOS App (.ipa) - ✅ Available (macOS only)'),
    ('PyGameMakerIDE', 'iOS App (.ipa) - ⚠️ Requires macOS with Xcode'),
    ('PyGameMakerIDE', 'This export format is not yet available.'),
    ('PyGameMakerIDE', 'Export cancelled'),
    ('PyGameMakerIDE', 'Building iOS App'),
    ('PyGameMakerIDE', 'Preparing iOS export...'),
    ('PyGameMakerIDE', 'iOS Export Complete'),
    ('PyGameMakerIDE', 'iOS Export Failed'),
    ('PyGameMakerIDE', 'Open the output folder?'),
    ('PyGameMakerIDE', 'iOS export cancelled'),
    ('PyGameMakerIDE', 'Exporting Aseba code...'),
    ('PyGameMakerIDE', 'Aseba Export Failed'),
    ('PyGameMakerIDE', 'Failed to export Aseba code:\n\n{0}'),
    ('PyGameMakerIDE', 'Aseba export failed'),
    ('PyGameMakerIDE', 'Aseba Export'),
    ('PyGameMakerIDE',
     'No Thymio objects found in this project, so no Aseba code was '
     'generated. Add a Thymio object to the project and try again.'),
    ('PyGameMakerIDE', 'Aseba export: nothing to export'),
    ('PyGameMakerIDE', 'Aseba export complete'),
    ('PyGameMakerIDE', 'Aseba Export Complete'),
    ('PyGameMakerIDE',
     'Aseba .aesl files written to:\n{0}\n\nWould you like to open the output folder?'),
    ('PyGameMakerIDE', 'Cancelling...'),
    ('AssetTreeWidget',
     'No project loaded.\nUse File → New Project or File → Open Project to begin.'),
    ('AssetTreeWidget', 'Playgrounds'),
    ('AssetTreeWidget', '💾 Export as PNG…'),
    ('AssetTreeWidget', '📋 Duplicate'),
    ('AssetTreeWidget', 'Sprite &apos;{0}&apos; has no image file.'),
    ('AssetTreeWidget', 'File Not Found'),
    ('AssetTreeWidget', 'Image file not found: {0}'),
    ('AssetTreeWidget', 'Export Sprite as PNG'),
    ('AssetTreeWidget', 'PNG Images (*.png)'),
    ('AssetTreeWidget', 'Failed to export: {0}'),
    ('BackgroundLayersDialog', 'Background Layers'),
    ('BackgroundLayersDialog', 'Background {0}'),
    ('BackgroundLayersDialog', 'Layer:'),
    ('BackgroundLayersDialog', 'Layer Properties'),
    ('BackgroundLayersDialog', 'Foreground:'),
    ('BackgroundLayersDialog', 'Image:'),
    ('BackgroundLayersDialog', 'Stretch:'),
    ('BackgroundLayersDialog', 'Tile H:'),
    ('BackgroundLayersDialog', 'Tile V:'),
    ('BackgroundLayersDialog', 'H Speed:'),
    ('BackgroundLayersDialog', 'V Speed:'),
    ('BaseEditor', '🪟 Float'),
    ('BaseEditor', 'Open this editor in its own window'),
    ('BaseEditor', '↶ Undo {0}'),
    ('BaseEditor', '↷ Redo {0}'),
    ('BaseEditor', 'Auto-saved: {0}'),
    ('BlocklyWidget', 'Error loading Blockly'),
    ('EnhancedPropertiesPanel', 'Configure...'),
    ('EnhancedPropertiesPanel', 'Backgrounds:'),
    ('NewProjectDialog', 'Empty Project'),
    ('NewProjectDialog', 'With Game Over Screen'),
    ('NewProjectDialog', 'Template:'),
    ('ObjectEditor', 'Blockly visual programming is not available.\n\nError: {0}'),
    ('ObjectEditor', 'Edit mode: changes apply automatically as you type'),
    ('ObjectEditor', 'No event methods found in the code'),
    ('ObjectEditor', '{0} events'),
    ('ObjectEventsPanel', '{0} Collision With...'),
    ('ObjectEventsPanel', '🤖 Thymio Events'),
    ('ObjectEventsPanel', '🤖 Visual Selector...'),
    ('ObjectEventsPanel', 'The Keyboard &lt;No Key&gt; event already exists.'),
    ('ObjectEventsPanel', 'Alarm Event Exists'),
    ('ObjectEventsPanel', 'Alarm {0} event already exists.'),
    ('ObjectEventsPanel', 'Remove {0} Event'),
    ('ObjectEventsPanel', '❌ NOT Colliding with {0}'),
    ('ObjectEventsPanel',
     'Cannot add actions directly to Alarm.\n\nPlease add actions to a '
     'specific alarm number instead:\nRight-click on Alarm 0, Alarm 1, etc.'),
    ('ObjectEventsPanel', 'Could not open action editor: {0}'),
    ('ObjectPropertiesPanel', '&lt;no parent&gt;'),
    ('ObjectPropertiesPanel', 'Parent object (inherits collision events)'),
    ('ObjectPropertiesPanel', 'Parent:'),
    ('RoomEditor', 'Tile Palette...'),
    ('RoomEditor', '↔ Shift All'),
    ('RoomEditor', 'Shift all instances by an X/Y offset'),
    ('RoomEditor', '🪟 Float'),
    ('RoomEditor', 'Open this editor in its own window'),
    ('RoomEditor', 'Shift All'),
    ('RoomEditor', 'No instances to shift.'),
    ('RoomEditor', 'Shift All Instances'),
    ('RoomEditor', 'X offset:'),
    ('RoomEditor', 'Y offset:'),
    ('RoomEditor', 'Shifted all instances by ({0}, {1})'),
    ('RoomEditor', 'Tile selected - Click in room to paint'),
    ('RoomEditor', 'Tile mode cleared'),
    ('TutorialDialog', 'Select a tutorial and click Open (or double-click):'),
    ('PlaygroundColorManager', 'Colors'),
    ('PlaygroundColorManager', 'Add color'),
    ('PlaygroundColorManager', 'Remove color'),
    ('PlaygroundColorManager', 'Add Color'),
    ('PlaygroundColorManager', 'Color name:'),
    ('PlaygroundColorManager', 'A color named &apos;{}&apos; already exists.'),
    ('PlaygroundColorManager', 'Edit Color'),
    ('PlaygroundEditor', 'Playground Editor'),
    ('PlaygroundEditor', 'Save playground (Ctrl+S)'),
    ('PlaygroundEditor', 'Undo'),
    ('PlaygroundEditor', 'Toggle grid display'),
    ('PlaygroundEditor', 'Snap'),
    ('PlaygroundEditor', ' Thickness: '),
    ('PlaygroundEditor', 'Default wall thickness for drag-to-draw'),
    ('PlaygroundEditor', ' Block: '),
    ('PlaygroundEditor', 'Block size for block-paint mode'),
    ('PlaygroundEditor', 'Color for painted blocks'),
    ('PlaygroundEditor', 'Arena Settings'),
    ('PlaygroundEditor', 'Configure arena dimensions and background'),
    ('PlaygroundEditor', '▶ Run'),
    ('PlaygroundEditor', 'Simulate the playground with linked robot code'),
    ('PlaygroundEditor', 'Export .playground'),
    ('PlaygroundEditor', 'Export as Aseba .playground file'),
    ('PlaygroundEditor', '🪟 Float'),
    ('PlaygroundEditor', 'Open this editor in its own window'),
    ('PlaygroundEditor', 'Select Ground Texture'),
    ('PlaygroundEditor', 'Images (*.png *.jpg *.jpeg *.bmp)'),
    ('PlaygroundEditor', 'Texture Error'),
    ('PlaygroundEditor', 'Could not copy texture:\n{}'),
    ('PlaygroundEditor', '(none)'),
    ('PlaygroundEditor', 'Clear'),
    ('PlaygroundEditor', 'Ground texture:'),
    ('PlaygroundEditor', 'Run Failed'),
    ('PlaygroundEditor', 'Error launching simulator:\n{}'),
    ('PlaygroundEditor', 'Export Playground'),
    ('PlaygroundEditor', 'Aseba Playground (*.playground)'),
    ('PlaygroundEditor', 'Playground exported to:\n{}'),
    ('PlaygroundEditor', 'Error exporting playground:\n{}'),
    ('PlaygroundElementProperties', 'No Selection'),
    ('PlaygroundElementProperties', 'Wall'),
    ('PlaygroundElementProperties', 'Angle:'),
    ('PlaygroundElementProperties', 'Color:'),
    ('PlaygroundElementProperties', 'Pushable'),
    ('PlaygroundElementProperties', 'Robot'),
    ('PlaygroundElementProperties', 'Port:'),
    ('PlaygroundElementProperties', 'Code:'),
    ('PlaygroundElementProperties',
     'Which Thymio object&apos;s code to run when simulating'),
    ('PlaygroundElementProperties', 'Wall Properties'),
    ('PlaygroundElementProperties', 'Robot Properties'),
    ('PlaygroundRunnerWindow', 'Playground - Running'),
    ('PlaygroundRunnerWindow', 'Running: {} robots, {} walls'),
    ('PlaygroundRunnerWindow', 'Reset'),
    ('PlaygroundRunnerWindow',
     'Arrow keys / Space = all robots; click a robot&apos;s button = that '
     'robot only. The linked object&apos;s code runs automatically.'),
    ('PlaygroundRunnerWindow', 'Resume'),
    ('PlaygroundToolPalette', 'Tools'),
    ('PlaygroundToolPalette', 'Select and move elements'),
    ('PlaygroundToolPalette', 'Wall'),
    ('PlaygroundToolPalette', 'Click to place walls'),
    ('PlaygroundToolPalette', 'Robot'),
    ('PlaygroundToolPalette', 'Click to place robots'),
    ('PlaygroundToolPalette', 'Block'),
    ('PlaygroundToolPalette', 'Paint cube blocks on a grid (Minecraft-style)'),
    ('SpriteEditor', 'Pencil'),
    ('SpriteEditor', 'Draw pixels (P)'),
    ('SpriteEditor', 'Eraser'),
    ('SpriteEditor', 'Erase pixels (E)'),
    ('SpriteEditor', 'Picker'),
    ('SpriteEditor', 'Pick color from canvas (I)'),
    ('SpriteEditor', 'Fill'),
    ('SpriteEditor', 'Flood fill area (G)'),
    ('SpriteEditor', 'Draw line (L)'),
    ('SpriteEditor', 'Rect'),
    ('SpriteEditor', 'Draw rectangle (R)'),
    ('SpriteEditor', 'Ellipse'),
    ('SpriteEditor', 'Draw ellipse (O)'),
    ('SpriteEditor', 'Rectangle selection (S)'),
    ('SpriteEditor', 'Select tool from list'),
    ('SpriteEditor', 'Size:'),
    ('SpriteEditor', 'Brush / line width in pixels'),
    ('SpriteEditor', 'Origin'),
    ('SpriteEditor', 'Origin preset'),
    ('SpriteEditor', 'Top-Left'),
    ('SpriteEditor', 'Top-Center'),
    ('SpriteEditor', 'Center'),
    ('SpriteEditor', 'Center-Bottom'),
    ('SpriteEditor', 'Bottom-Left'),
    ('SpriteEditor', 'Bottom-Right'),
    ('SpriteEditor', 'Custom'),
    ('SpriteEditor', 'Origin X coordinate'),
    ('SpriteEditor', 'Origin Y coordinate'),
    ('SpriteEditor', 'Precise Collision'),
    ('SpriteEditor',
     'Enable pixel-perfect collision for this sprite. Static-only: rotated '
     'or scaled instances fall back to AABB.'),
    ('SpriteEditor', 'Filled'),
    ('SpriteEditor', 'Toggle filled shapes'),
    ('SpriteEditor', 'Mirror H'),
    ('SpriteEditor', 'Mirror V'),
    ('SpriteEditor', 'Resize'),
    ('SpriteEditor', 'Toggle pixel grid'),
    ('SpriteEditor', 'Zoom Out'),
    ('SpriteEditor', 'Zoom In'),
    ('SpriteEditor', 'Export PNG…'),
    ('SpriteEditor', 'Tool: {0}'),
    ('SpriteEditor', 'Scale to {0}x{1}'),
    ('SpriteEditor', 'Resize Canvas to {0}x{1}'),
    ('SpriteEditor', 'Copied selection'),
    ('SpriteEditor', 'Cut selection'),
    ('SpriteEditor', 'Pasted from clipboard'),
    ('SpriteEditor', 'Copy\tCtrl+C'),
    ('SpriteEditor', 'Cut\tCtrl+X'),
    ('SpriteEditor', 'Paste\tCtrl+V'),
    ('SpriteEditor', 'Delete\tDel'),
    ('SpriteEditor', 'Deselect\tEsc'),
    ('SpriteEditor', 'Select All'),
    ('SpriteEditor', 'Export as PNG…'),
    ('SpriteEditor', 'Export as PNG'),
    ('SpriteEditor', 'PNG Images (*.png)'),
    ('SpriteEditor', 'Exported: {0}'),
    ('SpriteEditor', 'Failed to export PNG.'),
    ('SpriteEditor', 'No frames in sprite'),
    ('SpriteEditor', 'Failed to save sprite: {0}'),
    ('ViewConfigDialog', 'View Configuration'),
    ('ViewConfigDialog', 'View {0}'),
    ('ViewConfigDialog', 'View:'),
    ('ViewConfigDialog', 'View in Room'),
    ('ViewConfigDialog', 'Port on Screen'),
    ('ViewConfigDialog', 'Object Following'),
    ('ViewConfigDialog', 'Follow:'),
    ('ViewConfigDialog', 'H Border:'),
    ('ViewConfigDialog', 'V Border:'),
    ('ViewConfigDialog', 'H Speed:'),
    ('ViewConfigDialog', 'V Speed:'),
    ('BaseBlockConfigDialog', 'Preset:'),
    ('BaseBlockConfigDialog', 'Block'),
    ('BaseBlockConfigDialog', 'Description'),
    ('BaseBlockConfigDialog', 'Select All'),
    ('BaseBlockConfigDialog', 'Select None'),
    ('BaseBlockConfigDialog', '{0} blocks'),
    ('BaseBlockConfigDialog', 'Requires: {0}'),
    ('BaseBlockConfigDialog', '⚠️ Warning: Some blocks are missing dependencies:\n{0}'),
    ('BaseBlockConfigDialog', 'Missing Dependencies'),
    ('TilePaletteDialog', 'Tile Palette'),
    ('TilePaletteDialog', 'Tileset:'),
    ('TilePaletteDialog', 'Tile W:'),
    ('TilePaletteDialog', 'H:'),
    ('TilePaletteDialog', 'Layer:'),
    ('TilePaletteDialog', 'Clear Tile'),
    ('TilePaletteDialog', '(none)'),
    ('FrameTimeline', '+'),
    ('FrameTimeline', 'Add frame'),
    ('FrameTimeline', 'D'),
    ('FrameTimeline', 'Duplicate frame'),
    ('FrameTimeline', '-'),
    ('FrameTimeline', 'Delete frame'),
    ('ResizeCanvasDialog', 'Resize / Scale'),
    ('ResizeCanvasDialog', 'Current size: {0} x {1}'),
    ('ResizeCanvasDialog', 'Mode'),
    ('ResizeCanvasDialog', 'Scale Image (stretch content to new size)'),
    ('ResizeCanvasDialog', 'Resize Canvas (keep content, add/crop space)'),
    ('ResizeCanvasDialog', 'Anchor'),
    ('FloatableEditorMixin', 'Return this editor to the IDE&apos;s tab strip'),
    ('FloatableEditorMixin', '🪟 Float'),
    ('FloatableEditorMixin', 'Open this editor in its own window'),
    ('ForegroundBackgroundSwatch', 'Foreground Color'),
    ('ForegroundBackgroundSwatch', 'Background Color'),
    ('ActionConfigDialog', 'Number or expression'),
    ('ColorPaletteWidget', 'Swap foreground/background'),
    ('KeySelectorDialog', '{0} ({1})'),
    ('TileGridWidget', 'No tileset'),
]

assert len(SOURCES) == 309, len(SOURCES)
assert len(set(SOURCES)) == 309, "duplicate (context, source) entries"

# Genuine Spanish/universal cognates -- translation legitimately equals
# the (unescaped) English source, not a stray untranslated copy.
_COGNATES = {
    ("PreferencesDialog", "General"),
    ("PyGameMakerIDE", "Open Roberta XML (*.xml)"),
    ("PlaygroundElementProperties", "Color:"),
    ("PlaygroundElementProperties", "Robot"),
    ("PlaygroundToolPalette", "Robot"),
    ("TilePaletteDialog", "H:"),
    ("FrameTimeline", "+"),
    ("FrameTimeline", "D"),
    ("FrameTimeline", "-"),
    ("KeySelectorDialog", "{0} ({1})"),
}


def _get_context_blocks(content, name):
    return re.findall(
        r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
        content, re.S,
    )


def test_no_empty_unfinished_entries_remain():
    content = TS_PATH.read_text(encoding="utf-8")
    assert '<translation type="unfinished"></translation>' not in content


def test_no_double_escaped_translations():
    """Guard against the double-escaping bug found in the de batch
    (commit 3928e32, fixed separately) -- a value passed through XML
    escaping twice passes XML validity and lrelease silently and only
    shows up as literal '&lt;'/'&amp;' text at runtime."""
    content = TS_PATH.read_text(encoding="utf-8")
    assert "&amp;amp;" not in content, "double-escaped '&' in pygm2_es.ts"
    assert "&amp;lt;" not in content, "double-escaped '<' in pygm2_es.ts"
    assert "&amp;gt;" not in content, "double-escaped '>' in pygm2_es.ts"


def test_every_source_has_a_real_non_empty_translation():
    content = TS_PATH.read_text(encoding="utf-8")
    for context, source in SOURCES:
        blocks = _get_context_blocks(content, context)
        assert blocks, f"missing {context} context"
        m = None
        for block in blocks:
            m = re.search(
                r"<source>" + re.escape(source) + r"</source>\s*"
                r"(?:<extracomment>.*?</extracomment>\s*)?"
                r"<translation>(.*?)</translation>",
                block, re.S,
            )
            if m:
                break
        assert m is not None, f"[{context}] {source!r}: no real <translation> tag"
        translated = m.group(1).strip()
        assert translated, f"[{context}] {source!r}: translation is empty"
        if (context, source) not in _COGNATES:
            assert translated != source, (
                f"[{context}] {source!r}: translation equals the English source"
            )


def test_runtime_translate_resolves_every_string():
    """SOURCES holds each <source>'s literal XML-entity-escaped text (for
    the regex tests above); the real self.tr() call at runtime sees the
    UNESCAPED Python string, so unescape before calling
    QCoreApplication.translate (same landmine as every prior batch)."""
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
            is_cognate = (context, source) in _COGNATES
            assert resolved != runtime_source or is_cognate, (
                f"[{context}] {source!r} did not resolve (still English)"
            )
            assert resolved, f"[{context}] {source!r} resolved empty"
            assert "&amp;" not in resolved, (
                f"[{context}] {source!r} resolved double-escaped: {resolved!r}"
            )
    finally:
        app.removeTranslator(translator)
