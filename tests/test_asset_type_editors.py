"""The three new minimal asset-type editors (editors/sound_editor.py,
background_editor.py, font_editor.py) — closes the TODO.md "Generic
asset-type editor fallback" item for sounds/backgrounds/fonts, the three
asset types core/ide_window.py's on_asset_double_clicked previously fell
through to "No editor registered for asset type ..." for.

Same round-trip / no-dirty-on-load pattern as TestScriptEditor in
tests/test_widgets.py, which these editors deliberately mirror in design
(a thin form over BaseEditor, not a re-import surface).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


class TestSoundEditor:
    def test_load_get_round_trip(self, qtbot):
        from editors.sound_editor import SoundEditor
        editor = SoundEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "snd_swap"
        editor.load_data({
            "file_path": "sounds/snd_swap.wav",
            "volume": 0.6,
            "loop": True,
            "length": 0.42,
            "imported": True,
        })
        out = editor.get_data()
        assert out["asset_type"] == "sound"
        assert out["name"] == "snd_swap"
        assert out["volume"] == 0.6
        assert out["loop"] is True
        # Untouched fields (file_path, length, imported) round-trip verbatim.
        assert out["file_path"] == "sounds/snd_swap.wav"
        assert out["length"] == 0.42
        assert out["imported"] is True

    def test_defaults_for_minimal_template(self, qtbot):
        """A brand-new asset created via the tree's generic
        create_asset_data_template has no volume/loop keys at all —
        the editor must not crash and must save sane defaults."""
        from editors.sound_editor import SoundEditor
        editor = SoundEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "snd_new"
        editor.load_data({"name": "snd_new", "asset_type": "sound", "imported": False})
        out = editor.get_data()
        assert out["volume"] == 1.0
        assert out["loop"] is False

    def test_load_does_not_mark_dirty(self, qtbot):
        from editors.sound_editor import SoundEditor
        editor = SoundEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "x"
        editor.load_data({"file_path": "sounds/x.wav", "volume": 1.0, "loop": False})
        assert editor.is_modified is False

    def test_field_edit_marks_dirty(self, qtbot):
        from editors.sound_editor import SoundEditor
        editor = SoundEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "x"
        editor.load_data({"file_path": "sounds/x.wav", "volume": 1.0, "loop": False})
        editor.volume_spin.setValue(0.3)
        assert editor.is_modified is True


class TestBackgroundEditor:
    def test_load_get_round_trip(self, qtbot):
        from editors.background_editor import BackgroundEditor
        editor = BackgroundEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "bg_main"
        editor.load_data({
            "file_path": "backgrounds/bg_main.png",
            "width": 800,
            "height": 600,
            "tile_horizontal": True,
            "tile_vertical": False,
            "imported": True,
        })
        out = editor.get_data()
        assert out["asset_type"] == "background"
        assert out["name"] == "bg_main"
        assert out["tile_horizontal"] is True
        assert out["tile_vertical"] is False
        assert out["width"] == 800 and out["height"] == 600

    def test_defaults_for_minimal_template(self, qtbot):
        from editors.background_editor import BackgroundEditor
        editor = BackgroundEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "bg_new"
        editor.load_data({"name": "bg_new", "asset_type": "background"})
        out = editor.get_data()
        assert out["tile_horizontal"] is False
        assert out["tile_vertical"] is False

    def test_missing_image_file_does_not_crash(self, qtbot):
        """No project_path and a nonexistent file_path — the preview must
        degrade to a text placeholder, not raise."""
        from editors.background_editor import BackgroundEditor
        editor = BackgroundEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "bg_missing"
        editor.load_data({"file_path": "backgrounds/does_not_exist.png"})
        assert "not found" in editor.preview_label.text().lower()

    def test_load_does_not_mark_dirty(self, qtbot):
        from editors.background_editor import BackgroundEditor
        editor = BackgroundEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "x"
        editor.load_data({"file_path": "backgrounds/x.png"})
        assert editor.is_modified is False


class TestFontEditor:
    def test_load_get_round_trip(self, qtbot):
        from editors.font_editor import FontEditor
        editor = FontEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "fnt_title"
        editor.load_data({
            "font_name": "Consolas",
            "size": 24,
            "bold": True,
            "italic": False,
            "charset": "ascii",
        })
        out = editor.get_data()
        assert out["asset_type"] == "font"
        assert out["name"] == "fnt_title"
        assert out["font_name"] == "Consolas"
        assert out["size"] == 24
        assert out["bold"] is True
        assert out["italic"] is False
        assert out["charset"] == "ascii"  # preserved verbatim, no widget for it

    def test_defaults_for_minimal_template(self, qtbot):
        from editors.font_editor import FontEditor
        editor = FontEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "fnt_new"
        editor.load_data({"name": "fnt_new", "asset_type": "font"})
        out = editor.get_data()
        assert out["font_name"] == "Arial"
        assert out["size"] == 12
        assert out["bold"] is False
        assert out["charset"] == "ascii"

    def test_load_does_not_mark_dirty(self, qtbot):
        from editors.font_editor import FontEditor
        editor = FontEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "x"
        editor.load_data({"font_name": "Arial", "size": 12})
        assert editor.is_modified is False


class TestAssetEditorDispatchWiring:
    """core/ide_window.py's on_asset_double_clicked / _canonical_category —
    static source checks (no full IDEWindow instantiation needed) that the
    three new asset types are actually wired into the dispatch, not just
    that the editor classes exist in isolation."""

    def _source(self):
        return Path("core/ide_window.py").read_text(encoding="utf-8")

    def test_double_click_dispatch_covers_new_types(self):
        src = self._source()
        assert "self.open_sound_editor(asset_name, asset_info)" in src
        assert "self.open_background_editor(asset_name, asset_info)" in src
        assert "self.open_font_editor(asset_name, asset_info)" in src

    def test_canonical_category_maps_singular_forms(self):
        """Without this, renaming an open sound/background/font asset would
        compute a mismatched editor key ('sound:x' vs the registered
        'sounds:x') and silently fail to update the open tab."""
        src = self._source()
        assert "'sound': 'sounds'" in src
        assert "'background': 'backgrounds'" in src
        assert "'font': 'fonts'" in src
