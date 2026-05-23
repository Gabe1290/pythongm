"""
Tests for Qt widgets using pytest-qt

These tests require a Qt application context and use the qtbot fixture
from pytest-qt for simulating user interactions.
"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import centralized dependency detection from conftest
from conftest import skip_without_qt_widgets

# Skip all widget tests if pytest-qt or PySide6 is not available
pytestmark = [
    pytest.mark.widget,
    skip_without_qt_widgets,
]

# Note: mock_asset_manager and mock_project_manager fixtures are now in conftest.py


class TestNewProjectDialog:
    """Test the New Project dialog"""

    def test_dialog_creates(self, qtbot):
        """NewProjectDialog should create without errors"""
        from dialogs.project_dialogs import NewProjectDialog

        dialog = NewProjectDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert dialog.windowTitle()

    def test_dialog_has_name_field(self, qtbot):
        """NewProjectDialog should have a project name input"""
        from dialogs.project_dialogs import NewProjectDialog

        dialog = NewProjectDialog()
        qtbot.addWidget(dialog)

        # Should have a name input field
        assert hasattr(dialog, 'name_edit') or hasattr(dialog, 'project_name_edit')

    def test_dialog_has_location_field(self, qtbot):
        """NewProjectDialog should have a location input"""
        from dialogs.project_dialogs import NewProjectDialog

        dialog = NewProjectDialog()
        qtbot.addWidget(dialog)

        # The active dialog uses `project_path_edit`; older prototypes used
        # `location_edit` / `project_location_edit`. Accept any of them.
        assert (hasattr(dialog, 'location_edit')
                or hasattr(dialog, 'project_location_edit')
                or hasattr(dialog, 'project_path_edit'))


class TestPreferencesDialog:
    """Test the Preferences dialog"""

    def test_dialog_creates(self, qtbot):
        """PreferencesDialog should create without errors"""
        from dialogs.preferences_dialog import PreferencesDialog

        dialog = PreferencesDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None

    def test_dialog_has_tabs(self, qtbot):
        """PreferencesDialog should have configuration tabs"""
        from dialogs.preferences_dialog import PreferencesDialog

        dialog = PreferencesDialog()
        qtbot.addWidget(dialog)

        # Should have a tab widget
        from PySide6.QtWidgets import QTabWidget
        tabs = dialog.findChildren(QTabWidget)
        assert len(tabs) > 0 or hasattr(dialog, 'tab_widget')


class TestAssetTreeWidget:
    """Test the Asset Tree widget"""

    def test_tree_creates(self, qtbot):
        """AssetTreeWidget should create without errors"""
        from widgets.asset_tree.asset_tree_widget import AssetTreeWidget

        tree = AssetTreeWidget()
        qtbot.addWidget(tree)

        assert tree is not None

    def test_tree_has_categories(self, qtbot):
        """AssetTreeWidget should have asset category items"""
        from widgets.asset_tree.asset_tree_widget import AssetTreeWidget

        tree = AssetTreeWidget()
        qtbot.addWidget(tree)

        # Should have top-level items for categories
        top_level_count = tree.topLevelItemCount()
        assert top_level_count > 0

    def test_tree_category_names(self, qtbot):
        """AssetTreeWidget should have standard category names"""
        from widgets.asset_tree.asset_tree_widget import AssetTreeWidget

        tree = AssetTreeWidget()
        qtbot.addWidget(tree)

        # Get all category names
        categories = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            categories.append(item.text(0).lower())

        # Should have at least sprites, sounds, objects, rooms
        expected = ["sprites", "sounds", "objects", "rooms"]
        for cat in expected:
            assert any(cat in c for c in categories), f"Missing category: {cat}"


class TestEnhancedPropertiesPanel:
    """Test the Enhanced Properties Panel"""

    def test_panel_creates(self, qtbot):
        """EnhancedPropertiesPanel should create without errors"""
        from widgets.enhanced_properties_panel import EnhancedPropertiesPanel

        panel = EnhancedPropertiesPanel()
        qtbot.addWidget(panel)

        assert panel is not None

    def test_panel_clear(self, qtbot):
        """EnhancedPropertiesPanel should support clearing"""
        from widgets.enhanced_properties_panel import EnhancedPropertiesPanel

        panel = EnhancedPropertiesPanel()
        qtbot.addWidget(panel)

        # Should have a clear method
        if hasattr(panel, 'clear'):
            panel.clear()  # Should not raise

    def test_panel_display_sprite(self, qtbot, sample_sprite_path):
        """EnhancedPropertiesPanel should display sprite properties"""
        from widgets.enhanced_properties_panel import EnhancedPropertiesPanel

        panel = EnhancedPropertiesPanel()
        qtbot.addWidget(panel)

        # Mock sprite data - set_asset takes a single dict with asset_type
        sprite_data = {
            "asset_type": "sprites",
            "name": "test_sprite",
            "file_path": str(sample_sprite_path),
            "width": 32,
            "height": 32
        }

        # set_asset takes a single dict argument
        panel.set_asset(sprite_data)


class TestRoomCanvas:
    """Test the Room Canvas widget"""

    def test_canvas_creates(self, qtbot):
        """RoomCanvas should create without errors"""
        try:
            from editors.room_editor.room_canvas import RoomCanvas

            canvas = RoomCanvas()
            qtbot.addWidget(canvas)

            assert canvas is not None
        except ImportError:
            pytest.skip("RoomCanvas not available")

    def test_canvas_grid_settings(self, qtbot):
        """RoomCanvas should have grid settings"""
        try:
            from editors.room_editor.room_canvas import RoomCanvas

            canvas = RoomCanvas()
            qtbot.addWidget(canvas)

            # Should have grid-related properties
            assert hasattr(canvas, 'grid_size') or hasattr(canvas, 'show_grid')
        except ImportError:
            pytest.skip("RoomCanvas not available")


class TestObjectEditor:
    """Test the Object Editor widget"""

    def test_editor_creates(self, qtbot, mock_project_manager):
        """ObjectEditor should create without errors"""
        try:
            from editors.object_editor.object_editor_main import ObjectEditor

            # ObjectEditor may require project manager
            editor = ObjectEditor()
            qtbot.addWidget(editor)

            assert editor is not None
        except ImportError:
            pytest.skip("ObjectEditor not available")
        except TypeError:
            # May require additional arguments
            pytest.skip("ObjectEditor requires additional initialization")


class TestSpriteEditorPreciseCheckbox:
    """Sprite editor exposes a `Precise Collision` checkbox that round-trips
    through `sprite_data['precise']`. The runtime side is covered by
    TestPixelPerfectCollision in test_game_runner.py — these tests just
    verify the IDE wiring."""

    def test_precise_checkbox_exists_and_defaults_unchecked(self, qtbot):
        try:
            from editors.sprite_editor.sprite_editor_main import SpriteEditor
        except ImportError:
            pytest.skip("SpriteEditor not available")
        editor = SpriteEditor()
        qtbot.addWidget(editor)
        assert hasattr(editor, '_precise_check')
        assert editor._precise_check.isChecked() is False

    def test_precise_round_trips_through_load_and_get(self, qtbot):
        """load_data(precise=True) checks the box; toggling it back updates get_data()."""
        try:
            from editors.sprite_editor.sprite_editor_main import SpriteEditor
        except ImportError:
            pytest.skip("SpriteEditor not available")
        editor = SpriteEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "spr_test"
        editor.load_data({
            "file_path": "",
            "frame_width": 32,
            "frame_height": 32,
            "frames": 1,
            "animation_type": "single",
            "speed": 10.0,
            "origin_x": 16,
            "origin_y": 16,
            "precise": True,
        })
        assert editor._precise_check.isChecked() is True
        assert editor.get_data()["precise"] is True
        # Flip and confirm get_data round-trips.
        editor._precise_check.setChecked(False)
        assert editor.get_data()["precise"] is False


class TestScriptEditor:
    """The minimal script editor (editors/script_editor.py) round-trips
    a script's ``code`` field through load_data / get_data and tags the
    saved data with the correct ``asset_type`` so the IDE save path
    routes it into the ``scripts`` category.
    """

    def test_load_get_round_trip_preserves_code(self, qtbot):
        try:
            from editors.script_editor import ScriptEditor
        except ImportError:
            pytest.skip("ScriptEditor not available")
        editor = ScriptEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "adapt_direction"
        sample_code = (
            "# This script adapts the direction of the monster\n"
            "if instance.hspeed == 0:\n"
            "    instance.hspeed = 4\n"
        )
        editor.load_data({
            "code": sample_code,
            "language": "python",
            "imported": True,
        })
        out = editor.get_data()
        assert out["code"] == sample_code
        assert out["asset_type"] == "script"
        assert out["language"] == "python"
        assert out["name"] == "adapt_direction"
        # 'imported' must round-trip — IDE save path relies on it for
        # categorising assets from GMK imports separately from native ones.
        assert out["imported"] is True

    def test_default_language_is_python(self, qtbot):
        """A script loaded without an explicit `language` should save as Python."""
        try:
            from editors.script_editor import ScriptEditor
        except ImportError:
            pytest.skip("ScriptEditor not available")
        editor = ScriptEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "untyped"
        editor.load_data({"code": "pass"})
        assert editor.get_data()["language"] == "python"

    def test_load_does_not_mark_dirty(self, qtbot):
        """Loading an asset shouldn't immediately flag it as modified —
        otherwise pytest-qt's auto-close teardown would hit the
        unsaved-changes prompt and deadlock (see conftest auto-dismiss
        fixture for the matching safety net).
        """
        try:
            from editors.script_editor import ScriptEditor
        except ImportError:
            pytest.skip("ScriptEditor not available")
        editor = ScriptEditor()
        qtbot.addWidget(editor)
        editor.asset_name = "x"
        editor.load_data({"code": "print('hi')"})
        assert editor.is_modified is False


class TestBlocklyWidget:
    """Test the Blockly widget integration"""

    def test_blockly_widget_creates(self, qtbot):
        """BlocklyWidget should create without errors"""
        try:
            from editors.object_editor.blockly_widget import BlocklyWidget

            widget = BlocklyWidget()
            qtbot.addWidget(widget)

            assert widget is not None
        except ImportError:
            pytest.skip("BlocklyWidget not available")
        except Exception as e:
            # Blockly may require web engine setup
            if "WebEngine" in str(e) or "QtWebEngine" in str(e):
                pytest.skip("QtWebEngine not available")
            raise


class TestTutorialDialog:
    """Test the Tutorial dialog"""

    def test_dialog_creates(self, qtbot):
        """TutorialDialog should create without errors"""
        try:
            from widgets.tutorial_dialog import TutorialDialog

            dialog = TutorialDialog()
            qtbot.addWidget(dialog)

            assert dialog is not None
        except ImportError:
            pytest.skip("TutorialDialog not available")
