"""
Tests for the Config class - configuration management

Note: We use importlib to load config.py directly because:
1. The root __init__.py imports PySide6 which may not be available
2. utils/__init__.py imports PIL which adds unnecessary dependencies
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import importlib.util

# Get project root without adding it to sys.path (to avoid triggering __init__.py)
project_root = Path(__file__).parent.parent.resolve()

# Import Config directly from file
config_path = project_root / "utils" / "config.py"
spec = importlib.util.spec_from_file_location("config_module", str(config_path))
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
Config = config_module.Config


class TestConfigBasics:
    """Test basic Config functionality"""

    @pytest.fixture(autouse=True)
    def setup_config(self, temp_dir):
        """Setup a clean config for each test"""
        # Reset Config state
        Config._config_data = {}
        Config._config_file = temp_dir / ".pygamemaker" / "config.json"
        Config._config_file.parent.mkdir(parents=True, exist_ok=True)
        yield
        # Cleanup
        Config._config_data = {}

    def test_load_creates_defaults_when_no_file(self, temp_dir):
        """Config.load() should create default config when no file exists"""
        config = Config.load()

        assert config is not None
        assert "version" in config
        assert "recent_projects" in config
        assert isinstance(config["recent_projects"], list)

    def test_save_creates_file(self, temp_dir):
        """Config.save() should create config file"""
        Config._config_data = {"test_key": "test_value"}
        result = Config.save()

        assert result is True
        assert Config._config_file.exists()

        # Verify file contents
        with open(Config._config_file) as f:
            saved_data = json.load(f)
        assert saved_data["test_key"] == "test_value"

    def test_get_returns_value(self):
        """Config.get() should return stored values"""
        Config._config_data = {"my_key": "my_value"}

        assert Config.get("my_key") == "my_value"

    def test_get_returns_default_for_missing_key(self):
        """Config.get() should return default for missing keys"""
        Config._config_data = {}

        assert Config.get("missing_key", "default") == "default"
        assert Config.get("missing_key") is None

    def test_set_stores_value(self):
        """Config.set() should store JSON-serializable values"""
        Config._config_data = {}
        Config.set("new_key", "new_value")

        assert Config._config_data["new_key"] == "new_value"

    def test_set_rejects_non_serializable(self):
        """Config.set() should skip non-JSON-serializable values"""
        Config._config_data = {}

        # Mock object that isn't JSON serializable
        mock_obj = MagicMock()
        Config.set("bad_key", mock_obj)

        assert "bad_key" not in Config._config_data


class TestConfigRecentProjects:
    """Test recent projects functionality"""

    @pytest.fixture(autouse=True)
    def setup_config(self, temp_dir):
        """Setup a clean config for each test"""
        Config._config_data = {"recent_projects": []}
        Config._config_file = temp_dir / ".pygamemaker" / "config.json"
        Config._config_file.parent.mkdir(parents=True, exist_ok=True)
        yield
        Config._config_data = {}

    def test_get_recent_projects_returns_list(self):
        """get_recent_projects() should return a list"""
        result = Config.get_recent_projects()
        assert isinstance(result, list)

    def test_add_recent_project_adds_to_list(self):
        """add_recent_project() should add project to beginning of list"""
        Config.add_recent_project("/path/to/project1")
        Config.add_recent_project("/path/to/project2")

        recent = Config.get_recent_projects()
        assert len(recent) == 2
        assert recent[0] == "/path/to/project2"  # Most recent first
        assert recent[1] == "/path/to/project1"

    def test_add_recent_project_moves_existing_to_top(self):
        """add_recent_project() should move existing project to top"""
        Config.add_recent_project("/path/to/project1")
        Config.add_recent_project("/path/to/project2")
        Config.add_recent_project("/path/to/project1")  # Re-add first project

        recent = Config.get_recent_projects()
        assert len(recent) == 2
        assert recent[0] == "/path/to/project1"  # Now at top

    def test_add_recent_project_limits_to_ten(self):
        """add_recent_project() should keep only last 10 projects"""
        for i in range(15):
            Config.add_recent_project(f"/path/to/project{i}")

        recent = Config.get_recent_projects()
        assert len(recent) == 10
        assert recent[0] == "/path/to/project14"  # Most recent


class TestConfigWindowSettings:
    """Test window configuration"""

    @pytest.fixture(autouse=True)
    def setup_config(self, temp_dir):
        """Setup a clean config for each test"""
        Config._config_data = {}
        Config._config_file = temp_dir / ".pygamemaker" / "config.json"
        Config._config_file.parent.mkdir(parents=True, exist_ok=True)
        yield
        Config._config_data = {}

    def test_get_window_config_returns_defaults(self):
        """get_window_config() should return sensible defaults"""
        window_config = Config.get_window_config()

        assert "width" in window_config
        assert "height" in window_config
        assert window_config["width"] > 0
        assert window_config["height"] > 0

    def test_set_window_config_stores_values(self):
        """set_window_config() should store window geometry"""
        Config.set_window_config(width=1920, height=1080, x=50, y=50, maximized=True)

        window_config = Config.get_window_config()
        assert window_config["width"] == 1920
        assert window_config["height"] == 1080
        assert window_config["x"] == 50
        assert window_config["y"] == 50
        assert window_config["maximized"] is True


class TestConfigEditorSettings:
    """Test editor configuration"""

    @pytest.fixture(autouse=True)
    def setup_config(self, temp_dir):
        """Setup a clean config for each test"""
        Config._config_data = {}
        Config._config_file = temp_dir / ".pygamemaker" / "config.json"
        Config._config_file.parent.mkdir(parents=True, exist_ok=True)
        yield
        Config._config_data = {}

    def test_get_editor_config_returns_defaults(self):
        """get_editor_config() should return sensible defaults"""
        editor_config = Config.get_editor_config()

        assert "auto_save_enabled" in editor_config
        assert "show_grid" in editor_config
        assert "grid_size" in editor_config
        assert editor_config["grid_size"] > 0

    def test_set_editor_config_updates_values(self):
        """set_editor_config() should update editor settings"""
        Config.set_editor_config(grid_size=64, snap_to_grid=False)

        editor_config = Config.get_editor_config()
        assert editor_config["grid_size"] == 64
        assert editor_config["snap_to_grid"] is False


class TestConfigCleanForJson:
    """Test JSON cleaning functionality"""

    def test_clean_config_removes_qt_objects(self):
        """_clean_config_for_json should remove Qt objects"""
        mock_qt_obj = MagicMock()
        mock_qt_obj.__class__.__name__ = "QByteArray"

        data = {"normal_key": "value", "qt_key": mock_qt_obj}
        cleaned = Config._clean_config_for_json(data)

        assert "normal_key" in cleaned
        assert "qt_key" not in cleaned

    def test_clean_config_preserves_primitives(self):
        """_clean_config_for_json should preserve JSON primitives"""
        data = {
            "string": "hello",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        cleaned = Config._clean_config_for_json(data)

        assert cleaned == data

    def test_clean_config_handles_nested_structures(self):
        """_clean_config_for_json should clean nested structures"""
        mock_obj = MagicMock()
        mock_obj.__class__.__name__ = "QWidget"

        data = {
            "level1": {
                "level2": {
                    "good": "value",
                    "bad": mock_obj
                }
            }
        }
        cleaned = Config._clean_config_for_json(data)

        assert cleaned["level1"]["level2"]["good"] == "value"
        assert "bad" not in cleaned["level1"]["level2"]
