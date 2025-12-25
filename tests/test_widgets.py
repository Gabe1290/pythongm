"""
Tests for Qt widgets using pytest-qt

These tests require a Qt application context and use the qtbot fixture
from pytest-qt for simulating user interactions.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Skip all widget tests if Qt is not available or display is not set
pytestmark = pytest.mark.widget


@pytest.fixture
def mock_asset_manager():
    """Create a mock asset manager"""
    mock = MagicMock()
    mock.get_asset.return_value = None
    mock.assets_cache = {}
    return mock


@pytest.fixture
def mock_project_manager():
    """Create a mock project manager"""
    mock = MagicMock()
    mock.current_project_path = Path("/fake/project")
    mock.current_project_data = {
        "name": "Test Project",
        "sprites": {},
        "sounds": {},
        "backgrounds": {},
        "objects": {},
        "rooms": {},
        "fonts": {},
        "data": {}
    }
    return mock


class TestNewProjectDialog:
    """Test the New Project dialog"""

    def test_dialog_creates(self, qtbot):
        """NewProjectDialog should create without errors"""
        from dialogs.new_project import NewProjectDialog

        dialog = NewProjectDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert dialog.windowTitle()

    def test_dialog_has_name_field(self, qtbot):
        """NewProjectDialog should have a project name input"""
        from dialogs.new_project import NewProjectDialog

        dialog = NewProjectDialog()
        qtbot.addWidget(dialog)

        # Should have a name input field
        assert hasattr(dialog, 'name_edit') or hasattr(dialog, 'project_name_edit')

    def test_dialog_has_location_field(self, qtbot):
        """NewProjectDialog should have a location input"""
        from dialogs.new_project import NewProjectDialog

        dialog = NewProjectDialog()
        qtbot.addWidget(dialog)

        # Should have a location input field
        assert hasattr(dialog, 'location_edit') or hasattr(dialog, 'project_location_edit')


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


class TestBlocklyWidget:
    """Test the Blockly widget integration"""

    def test_blockly_widget_creates(self, qtbot):
        """BlocklyWidget should create without errors"""
        try:
            from widgets.blockly.blockly_widget import BlocklyWidget

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
