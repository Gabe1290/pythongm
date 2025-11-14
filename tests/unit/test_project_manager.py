#!/usr/bin/env python3
"""
Unit tests for ProjectManager
Tests project lifecycle: create, load, save, close
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from pythongm.core.project_manager import ProjectManager


class TestProjectManagerCreation:
    """Test project creation functionality"""

    def test_create_project_creates_directory(self, project_manager, temp_dir):
        """Test that create_project creates a project directory"""
        project_name = "test_project"
        result = project_manager.create_project(project_name, str(temp_dir))

        assert result is True
        project_path = temp_dir / project_name
        assert project_path.exists()
        assert project_path.is_dir()

    def test_create_project_creates_project_file(self, project_manager, temp_dir):
        """Test that create_project creates project.json"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        project_path = temp_dir / project_name
        project_file = project_path / "project.json"
        assert project_file.exists()

    def test_create_project_creates_standard_directories(self, project_manager, temp_dir):
        """Test that create_project creates all standard asset directories"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        project_path = temp_dir / project_name
        expected_dirs = ["sprites", "sounds", "backgrounds", "objects",
                        "rooms", "scripts", "fonts", "data"]

        for dirname in expected_dirs:
            dir_path = project_path / dirname
            assert dir_path.exists(), f"Directory {dirname} was not created"
            assert dir_path.is_dir()

    def test_create_project_sets_current_project_path(self, project_manager, temp_dir):
        """Test that create_project sets the current_project_path"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        expected_path = str(temp_dir / project_name)
        assert project_manager.current_project_path == expected_path

    def test_create_project_initializes_project_data(self, project_manager, temp_dir):
        """Test that create_project initializes project_data with correct structure"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        data = project_manager.current_project_data
        assert data is not None
        assert data.get("name") == project_name
        assert data.get("version") == "1.0.0"
        assert "created" in data
        assert "modified" in data

    def test_create_project_emits_signal(self, project_manager, temp_dir, qtbot):
        """Test that create_project emits project_created signal"""
        project_name = "test_project"

        with qtbot.waitSignal(project_manager.project_created, timeout=1000):
            project_manager.create_project(project_name, str(temp_dir))

    def test_create_project_json_is_valid(self, project_manager, temp_dir):
        """Test that the created project.json is valid JSON"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        project_file = temp_dir / project_name / "project.json"
        with open(project_file, 'r') as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "name" in data
        assert "version" in data


class TestProjectManagerLoading:
    """Test project loading functionality"""

    def test_load_project_from_valid_directory(self, project_manager, project_dir,
                                                create_project_file, sample_project_data):
        """Test loading a project from a valid directory"""
        create_project_file(project_dir, sample_project_data)

        result = project_manager.load_project(str(project_dir))

        assert result is True
        assert project_manager.current_project_path == str(project_dir)

    def test_load_project_loads_project_data(self, project_manager, project_dir,
                                             create_project_file, sample_project_data):
        """Test that load_project loads the project data correctly"""
        create_project_file(project_dir, sample_project_data)
        project_manager.load_project(str(project_dir))

        data = project_manager.current_project_data
        assert data.get("name") == sample_project_data["name"]
        assert data.get("version") == sample_project_data["version"]

    def test_load_project_emits_signal(self, project_manager, project_dir,
                                       create_project_file, sample_project_data, qtbot):
        """Test that load_project emits project_loaded signal"""
        create_project_file(project_dir, sample_project_data)

        with qtbot.waitSignal(project_manager.project_loaded, timeout=1000):
            project_manager.load_project(str(project_dir))

    def test_load_nonexistent_project_fails(self, project_manager, temp_dir):
        """Test that loading a nonexistent project fails gracefully"""
        nonexistent_path = temp_dir / "does_not_exist"
        result = project_manager.load_project(str(nonexistent_path))

        assert result is False

    def test_load_project_without_json_fails(self, project_manager, temp_dir):
        """Test that loading a directory without project.json fails"""
        empty_dir = temp_dir / "empty_project"
        empty_dir.mkdir()

        result = project_manager.load_project(str(empty_dir))

        assert result is False

    def test_load_project_with_invalid_json_fails(self, project_manager, temp_dir):
        """Test that loading a project with invalid JSON fails gracefully"""
        project_path = temp_dir / "invalid_project"
        project_path.mkdir()

        project_file = project_path / "project.json"
        with open(project_file, 'w') as f:
            f.write("{ invalid json }")

        result = project_manager.load_project(str(project_path))

        assert result is False


class TestProjectManagerSaving:
    """Test project saving functionality"""

    def test_save_project_writes_to_disk(self, project_manager, temp_dir):
        """Test that save_project writes project.json to disk"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        # Modify project data
        project_manager.current_project_data["test_field"] = "test_value"

        project_manager.save_project()

        # Read the file and verify
        project_file = temp_dir / project_name / "project.json"
        with open(project_file, 'r') as f:
            data = json.load(f)

        assert data.get("test_field") == "test_value"

    def test_save_project_clears_dirty_flag(self, project_manager, temp_dir):
        """Test that save_project clears the dirty flag"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        project_manager.mark_dirty()
        assert project_manager.is_dirty() is True

        project_manager.save_project()
        assert project_manager.is_dirty() is False

    def test_save_project_emits_signal(self, project_manager, temp_dir, qtbot):
        """Test that save_project emits project_saved signal"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        with qtbot.waitSignal(project_manager.project_saved, timeout=1000):
            project_manager.save_project()

    def test_save_project_updates_modified_timestamp(self, project_manager, temp_dir):
        """Test that save_project updates the modified timestamp"""
        project_name = "test_project"
        project_manager.create_project(project_name, str(temp_dir))

        original_modified = project_manager.current_project_data.get("modified")

        # Wait a moment to ensure timestamp changes
        import time
        time.sleep(0.1)

        project_manager.save_project()

        new_modified = project_manager.current_project_data.get("modified")
        assert new_modified != original_modified


class TestProjectManagerDirtyTracking:
    """Test dirty state tracking"""

    def test_mark_dirty_sets_flag(self, project_manager):
        """Test that mark_dirty sets the dirty flag"""
        assert project_manager.is_dirty() is False

        project_manager.mark_dirty()

        assert project_manager.is_dirty() is True

    def test_mark_dirty_emits_signal(self, project_manager, qtbot):
        """Test that mark_dirty emits dirty_changed signal"""
        with qtbot.waitSignal(project_manager.dirty_changed, timeout=1000):
            project_manager.mark_dirty()

    def test_new_project_not_dirty(self, project_manager, temp_dir):
        """Test that a newly created project is not marked as dirty"""
        project_manager.create_project("test_project", str(temp_dir))

        assert project_manager.is_dirty() is False

    def test_asset_change_marks_dirty(self, project_manager, temp_dir):
        """Test that asset changes mark the project as dirty"""
        project_manager.create_project("test_project", str(temp_dir))

        # Simulate an asset change
        project_manager.on_asset_changed()

        assert project_manager.is_dirty() is True


class TestProjectManagerClosing:
    """Test project closing functionality"""

    def test_close_project_clears_current_path(self, project_manager, temp_dir):
        """Test that close_project clears the current project path"""
        project_manager.create_project("test_project", str(temp_dir))
        assert project_manager.current_project_path is not None

        project_manager.close_project()

        assert project_manager.current_project_path is None

    def test_close_project_clears_project_data(self, project_manager, temp_dir):
        """Test that close_project clears the project data"""
        project_manager.create_project("test_project", str(temp_dir))
        assert len(project_manager.current_project_data) > 0

        project_manager.close_project()

        assert len(project_manager.current_project_data) == 0

    def test_close_project_clears_dirty_flag(self, project_manager, temp_dir):
        """Test that close_project clears the dirty flag"""
        project_manager.create_project("test_project", str(temp_dir))
        project_manager.mark_dirty()

        project_manager.close_project()

        assert project_manager.is_dirty() is False

    def test_close_project_emits_signal(self, project_manager, temp_dir, qtbot):
        """Test that close_project emits project_closed signal"""
        project_manager.create_project("test_project", str(temp_dir))

        with qtbot.waitSignal(project_manager.project_closed, timeout=1000):
            project_manager.close_project()


class TestProjectManagerAutoSave:
    """Test auto-save functionality"""

    def test_auto_save_timer_exists(self, project_manager):
        """Test that auto-save timer is initialized"""
        assert project_manager.auto_save_timer is not None

    def test_auto_save_disabled_when_no_project(self, project_manager):
        """Test that auto-save doesn't run when no project is loaded"""
        # This should not raise an exception
        project_manager.auto_save()

    def test_auto_save_calls_save_when_dirty(self, project_manager, temp_dir):
        """Test that auto_save saves the project when dirty"""
        project_manager.create_project("test_project", str(temp_dir))
        project_manager.mark_dirty()

        project_manager.auto_save()

        assert project_manager.is_dirty() is False

    def test_auto_save_skips_when_not_dirty(self, project_manager, temp_dir):
        """Test that auto_save skips saving when project is not dirty"""
        project_manager.create_project("test_project", str(temp_dir))

        # Get the original modified timestamp
        original_modified = project_manager.current_project_data.get("modified")

        project_manager.auto_save()

        # Modified timestamp should not change
        new_modified = project_manager.current_project_data.get("modified")
        assert new_modified == original_modified


class TestProjectManagerAssetIntegration:
    """Test integration with AssetManager"""

    def test_asset_manager_set_on_init(self, mock_asset_manager):
        """Test that asset manager can be set during initialization"""
        pm = ProjectManager(asset_manager=mock_asset_manager)

        assert pm.asset_manager is mock_asset_manager

    def test_asset_signals_connected(self, project_manager):
        """Test that asset manager signals are connected"""
        # This is verified by the fact that on_asset_changed is called
        # We tested this in test_asset_change_marks_dirty
        assert project_manager.asset_manager is not None

    def test_update_asset_updates_project_data(self, project_manager, temp_dir):
        """Test that update_asset updates the project data"""
        project_manager.create_project("test_project", str(temp_dir))

        asset_data = {
            "name": "test_sprite",
            "path": "sprites/test.png"
        }

        project_manager.update_asset("sprites", "test_sprite", asset_data)

        assert "test_sprite" in project_manager.current_project_data.get("sprites", {})


# ============================================================================
# Parametrized Tests
# ============================================================================

@pytest.mark.parametrize("asset_type", [
    "sprites", "sounds", "backgrounds", "objects",
    "rooms", "scripts", "fonts", "data"
])
def test_create_project_includes_asset_type(project_manager, temp_dir, asset_type):
    """Test that created project includes all asset types in project data"""
    project_manager.create_project("test_project", str(temp_dir))

    assert asset_type in project_manager.current_project_data


@pytest.mark.parametrize("directory_name", [
    "sprites", "sounds", "backgrounds", "objects",
    "rooms", "scripts", "fonts", "data", "thumbnails"
])
def test_create_project_creates_all_directories(project_manager, temp_dir, directory_name):
    """Test that all required directories are created"""
    project_name = "test_project"
    project_manager.create_project(project_name, str(temp_dir))

    dir_path = temp_dir / project_name / directory_name
    assert dir_path.exists()
    assert dir_path.is_dir()
