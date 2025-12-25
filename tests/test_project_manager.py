"""
Tests for the ProjectManager class - project lifecycle management
"""

import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import centralized dependency detection from conftest
from conftest import skip_without_pyside6

# Skip all tests if PySide6 is not available
pytestmark = skip_without_pyside6


class TestProjectManagerCreation:
    """Test project creation functionality"""

    @pytest.fixture
    def project_manager(self):
        """Create a ProjectManager instance with mocked asset manager"""
        # Import here to avoid Qt initialization issues
        with patch('PySide6.QtCore.QTimer'):
            from core.project_manager import ProjectManager
            mock_asset_manager = MagicMock()
            pm = ProjectManager(asset_manager=mock_asset_manager)
            pm.auto_save_timer = MagicMock()
            return pm

    def test_create_new_project_creates_directory(self, project_manager, temp_dir):
        """create_new_project should create project directory"""
        result = project_manager.create_new_project("TestGame", temp_dir)

        assert result is True
        assert (temp_dir / "TestGame").exists()
        assert (temp_dir / "TestGame").is_dir()

    def test_create_new_project_creates_subdirectories(self, project_manager, temp_dir):
        """create_new_project should create asset subdirectories"""
        project_manager.create_new_project("TestGame", temp_dir)

        project_path = temp_dir / "TestGame"
        expected_dirs = ["sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"]

        for subdir in expected_dirs:
            assert (project_path / subdir).exists(), f"Missing directory: {subdir}"

    def test_create_new_project_creates_project_file(self, project_manager, temp_dir):
        """create_new_project should create project.json"""
        project_manager.create_new_project("TestGame", temp_dir)

        project_file = temp_dir / "TestGame" / "project.json"
        assert project_file.exists()

        with open(project_file) as f:
            data = json.load(f)
        assert data["name"] == "TestGame"

    def test_create_new_project_emits_signal(self, project_manager, temp_dir):
        """create_new_project should emit project_created signal"""
        signal_spy = MagicMock()
        project_manager.project_created.connect(signal_spy)

        project_manager.create_new_project("TestGame", temp_dir)

        signal_spy.assert_called_once()
        args = signal_spy.call_args[0]
        assert args[0] == temp_dir / "TestGame"

    def test_create_new_project_fails_if_exists(self, project_manager, temp_dir):
        """create_new_project should fail if directory exists"""
        (temp_dir / "ExistingGame").mkdir()

        result = project_manager.create_new_project("ExistingGame", temp_dir)

        assert result is False

    def test_create_new_project_updates_current_project(self, project_manager, temp_dir):
        """create_new_project should update current project state"""
        project_manager.create_new_project("TestGame", temp_dir)

        assert project_manager.current_project_path == temp_dir / "TestGame"
        assert project_manager.current_project_data["name"] == "TestGame"
        assert project_manager.is_dirty_flag is False


class TestProjectManagerLoading:
    """Test project loading functionality"""

    @pytest.fixture
    def project_manager(self):
        """Create a ProjectManager instance"""
        with patch('PySide6.QtCore.QTimer'):
            from core.project_manager import ProjectManager
            mock_asset_manager = MagicMock()
            pm = ProjectManager(asset_manager=mock_asset_manager)
            pm.auto_save_timer = MagicMock()
            return pm

    def test_load_project_loads_data(self, project_manager, temp_project_dir):
        """load_project should load project data from file"""
        result = project_manager.load_project(temp_project_dir)

        assert result is True
        assert project_manager.current_project_path == temp_project_dir
        assert project_manager.current_project_data["name"] == "Test Project"

    def test_load_project_emits_signal(self, project_manager, temp_project_dir):
        """load_project should emit project_loaded signal"""
        signal_spy = MagicMock()
        project_manager.project_loaded.connect(signal_spy)

        project_manager.load_project(temp_project_dir)

        signal_spy.assert_called_once()

    def test_load_project_fails_if_no_project_file(self, project_manager, temp_dir):
        """load_project should fail if project.json doesn't exist"""
        result = project_manager.load_project(temp_dir)

        assert result is False

    def test_load_project_updates_asset_manager(self, project_manager, temp_project_dir):
        """load_project should update asset manager"""
        project_manager.load_project(temp_project_dir)

        project_manager.asset_manager.set_project_directory.assert_called_with(temp_project_dir)

    def test_open_project_is_alias_for_load(self, project_manager, temp_project_dir):
        """open_project should be an alias for load_project"""
        result = project_manager.open_project(temp_project_dir)

        assert result is True
        assert project_manager.current_project_path == temp_project_dir


class TestProjectManagerSaving:
    """Test project saving functionality"""

    @pytest.fixture
    def project_manager(self):
        """Create a ProjectManager instance with a loaded project"""
        with patch('PySide6.QtCore.QTimer'):
            from core.project_manager import ProjectManager
            mock_asset_manager = MagicMock()
            pm = ProjectManager(asset_manager=mock_asset_manager)
            pm.auto_save_timer = MagicMock()
            return pm

    def test_save_project_writes_file(self, project_manager, temp_project_dir):
        """save_project should write project data to file"""
        project_manager.load_project(temp_project_dir)
        project_manager.current_project_data["description"] = "Updated description"

        result = project_manager.save_project()

        assert result is True

        with open(temp_project_dir / "project.json") as f:
            data = json.load(f)
        assert data["description"] == "Updated description"

    def test_save_project_clears_dirty_flag(self, project_manager, temp_project_dir):
        """save_project should clear the dirty flag"""
        project_manager.load_project(temp_project_dir)
        project_manager.is_dirty_flag = True

        project_manager.save_project()

        assert project_manager.is_dirty_flag is False

    def test_save_project_emits_signal(self, project_manager, temp_project_dir):
        """save_project should emit project_saved signal"""
        project_manager.load_project(temp_project_dir)
        signal_spy = MagicMock()
        project_manager.project_saved.connect(signal_spy)

        project_manager.save_project()

        signal_spy.assert_called_once()


class TestProjectManagerDirtyState:
    """Test dirty state management"""

    @pytest.fixture
    def project_manager(self):
        """Create a ProjectManager instance"""
        with patch('PySide6.QtCore.QTimer'):
            from core.project_manager import ProjectManager
            mock_asset_manager = MagicMock()
            pm = ProjectManager(asset_manager=mock_asset_manager)
            pm.auto_save_timer = MagicMock()
            return pm

    def test_mark_dirty_sets_flag(self, project_manager, temp_project_dir):
        """mark_dirty should set is_dirty_flag"""
        project_manager.load_project(temp_project_dir)

        project_manager.mark_dirty()

        assert project_manager.is_dirty_flag is True

    def test_mark_dirty_emits_signal(self, project_manager, temp_project_dir):
        """mark_dirty should emit dirty_changed signal"""
        project_manager.load_project(temp_project_dir)
        signal_spy = MagicMock()
        project_manager.dirty_changed.connect(signal_spy)

        project_manager.mark_dirty()

        signal_spy.assert_called_with(True)

    def test_is_dirty_returns_flag_value(self, project_manager, temp_project_dir):
        """is_dirty should return current dirty state"""
        project_manager.load_project(temp_project_dir)

        assert project_manager.is_dirty() is False

        project_manager.mark_dirty()
        assert project_manager.is_dirty() is True

    def test_asset_change_marks_dirty(self, project_manager, temp_project_dir):
        """Asset changes should mark project as dirty"""
        project_manager.load_project(temp_project_dir)

        project_manager.on_asset_changed("sprites", "test_sprite", {})

        assert project_manager.is_dirty() is True


class TestProjectManagerValidation:
    """Test project data validation"""

    @pytest.fixture
    def project_manager(self):
        """Create a ProjectManager instance"""
        with patch('PySide6.QtCore.QTimer'):
            from core.project_manager import ProjectManager
            pm = ProjectManager()
            pm.auto_save_timer = MagicMock()
            return pm

    def test_validate_valid_project(self, project_manager, sample_project_data):
        """_validate_project_data should accept valid data"""
        result = project_manager._validate_project_data(sample_project_data)
        assert result is True

    def test_validate_missing_name(self, project_manager):
        """_validate_project_data should reject data without name"""
        data = {"version": "1.0.0"}
        result = project_manager._validate_project_data(data)
        assert result is False

    def test_validate_empty_data(self, project_manager):
        """_validate_project_data should reject empty data"""
        result = project_manager._validate_project_data({})
        assert result is False

    def test_validate_none_data(self, project_manager):
        """_validate_project_data should reject None gracefully"""
        # The implementation may raise TypeError or return False
        try:
            result = project_manager._validate_project_data(None)
            assert result is False
        except TypeError:
            # Also acceptable - None is not a valid dict
            pass
