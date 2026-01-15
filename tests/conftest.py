"""
PyGameMaker IDE - Pytest Configuration and Fixtures

This module provides shared fixtures for all tests:
- Qt application setup (qtbot)
- Temporary project directories
- Mock assets and configurations
- Centralized dependency detection
- Shared skip markers for optional dependencies
"""

import pytest
import tempfile
import shutil
import json
import os
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

# ============================================================================
# Centralized Dependency Detection
# ============================================================================
# These constants can be imported by test files:
#   from conftest import HAS_PYSIDE6, HAS_PYTEST_QT, HAS_PYGAME

# PySide6 (Qt) detection
try:
    from PySide6.QtCore import QObject  # noqa: F401
    from PySide6.QtWidgets import QApplication  # noqa: F401
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

# pytest-qt detection
try:
    import pytestqt  # noqa: F401
    HAS_PYTEST_QT = True
except ImportError:
    HAS_PYTEST_QT = False

# pygame detection (set dummy drivers before import)
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

try:
    import pygame
    pygame.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
except Exception:
    # pygame.error or other initialization errors
    HAS_PYGAME = False

# PIL/Pillow detection
try:
    from PIL import Image as _PIL_Image  # noqa: F401
    del _PIL_Image  # Only used for detection
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ============================================================================
# Shared Skip Markers
# ============================================================================
# Pre-configured skip markers for common dependency combinations

skip_without_pyside6 = pytest.mark.skipif(
    not HAS_PYSIDE6, reason="PySide6 not installed"
)

skip_without_pytest_qt = pytest.mark.skipif(
    not HAS_PYTEST_QT, reason="pytest-qt not installed"
)

skip_without_qt_widgets = pytest.mark.skipif(
    not (HAS_PYSIDE6 and HAS_PYTEST_QT),
    reason="PySide6 and/or pytest-qt not installed"
)

skip_without_pygame = pytest.mark.skipif(
    not HAS_PYGAME, reason="pygame not available or failed to initialize"
)

skip_without_pil = pytest.mark.skipif(
    not HAS_PIL, reason="PIL/Pillow not installed"
)


# ============================================================================
# Project Path and Import Helpers
# ============================================================================
# Note: We do NOT add project root to sys.path here because the root __init__.py
# imports PySide6. Individual test files should import specific modules directly.

# Project root path (available for test files)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def import_module_directly(module_path: str, module_name: str = None):
    """
    Import a module directly from file path, bypassing package __init__.py files.

    This is useful when you need to import a module but don't want to trigger
    imports in __init__.py files (e.g., the root __init__.py imports PySide6).

    Args:
        module_path: Path to the module file relative to project root
        module_name: Optional name for the module (defaults to filename)

    Returns:
        The imported module

    Example:
        config_module = import_module_directly("utils/config.py")
        Config = config_module.Config
    """
    full_path = PROJECT_ROOT / module_path
    if module_name is None:
        module_name = Path(module_path).stem + "_direct"

    # Temporarily add project root to sys.path so the module can resolve
    # its own imports (e.g., 'from core.logger import get_logger')
    project_root_str = str(PROJECT_ROOT)
    path_added = False
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
        path_added = True

    try:
        spec = importlib.util.spec_from_file_location(module_name, str(full_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        # Remove project root from sys.path if we added it
        if path_added and project_root_str in sys.path:
            sys.path.remove(project_root_str)


# ============================================================================
# Qt Application Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def qapp_args():
    """Arguments passed to QApplication."""
    return ["-platform", "offscreen"]


@pytest.fixture
def mock_qapp(monkeypatch):
    """Mock QApplication for tests that don't need real Qt."""
    mock_app = MagicMock()
    monkeypatch.setattr("PySide6.QtWidgets.QApplication.instance", lambda: mock_app)
    return mock_app


# ============================================================================
# Project and Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmp = tempfile.mkdtemp(prefix="pygm_test_")
    yield Path(tmp)
    # Cleanup after test
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def temp_project_dir(temp_dir):
    """Create a temporary project directory with proper structure."""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()

    # Create standard project subdirectories
    subdirs = ["sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"]
    for subdir in subdirs:
        (project_dir / subdir).mkdir()

    # Create a minimal project.json with required 'assets' key
    project_data = {
        "name": "Test Project",
        "version": "1.0.0",
        "author": "Test Author",
        "description": "A test project",
        "room_order": [],
        "assets": {
            "sprites": {},
            "sounds": {},
            "backgrounds": {},
            "objects": {},
            "rooms": {},
            "fonts": {},
            "data": {}
        },
        "game_settings": {
            "window_width": 800,
            "window_height": 600,
            "fps": 60
        }
    }
    with open(project_dir / "project.json", "w") as f:
        json.dump(project_data, f, indent=2)

    return project_dir


@pytest.fixture
def sample_project_data():
    """Return sample project data for testing."""
    return {
        "name": "Sample Game",
        "version": "0.1.0",
        "author": "Test Developer",
        "description": "A sample game for testing",
        "room_order": ["room_start", "room_game", "room_end"],
        "assets": {
            "sprites": {},
            "sounds": {},
            "backgrounds": {},
            "objects": {},
            "rooms": {},
            "fonts": {},
            "data": {}
        },
        "game_settings": {
            "window_width": 1024,
            "window_height": 768,
            "fps": 60,
            "fullscreen": False
        }
    }


# ============================================================================
# Asset Fixtures
# ============================================================================

@pytest.fixture
def sample_sprite_path(temp_dir):
    """Create a sample sprite image file."""
    from PIL import Image

    sprite_path = temp_dir / "test_sprite.png"
    # Create a simple 32x32 red square
    img = Image.new("RGBA", (32, 32), (255, 0, 0, 255))
    img.save(sprite_path)

    return sprite_path


@pytest.fixture
def sample_object_data():
    """Return sample object data for testing."""
    return {
        "name": "obj_player",
        "sprite": "spr_player",
        "visible": True,
        "solid": False,
        "persistent": False,
        "depth": 0,
        "events": {}
    }


@pytest.fixture
def sample_room_data():
    """Return sample room data for testing."""
    return {
        "name": "room_test",
        "width": 800,
        "height": 600,
        "speed": 60,
        "background_color": "#87CEEB",
        "instances": [],
        "backgrounds": [],
        "views": []
    }


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def temp_config_dir(temp_dir):
    """Create a temporary config directory."""
    config_dir = temp_dir / ".pygamemaker"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_config(temp_config_dir):
    """Create a mock configuration."""
    config_data = {
        "theme": "dark",
        "language": "en",
        "recent_projects": [],
        "window_geometry": {
            "x": 100,
            "y": 100,
            "width": 1200,
            "height": 800
        },
        "editor_settings": {
            "font_size": 12,
            "tab_size": 4,
            "auto_save": True
        }
    }
    config_path = temp_config_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)

    return config_path


# ============================================================================
# Mock Fixtures for External Dependencies
# ============================================================================

@pytest.fixture
def mock_pygame():
    """Mock pygame for tests that don't need real audio/game functionality."""
    with patch.dict(sys.modules, {"pygame": MagicMock()}):
        yield


@pytest.fixture
def mock_file_dialog(monkeypatch):
    """Mock Qt file dialogs to return predefined paths."""
    def mock_get_open_file(*args, **kwargs):
        return ("/fake/path/file.txt", "All Files (*)")

    def mock_get_save_file(*args, **kwargs):
        return ("/fake/path/save.txt", "All Files (*)")

    def mock_get_directory(*args, **kwargs):
        return "/fake/directory"

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        mock_get_open_file
    )
    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getSaveFileName",
        mock_get_save_file
    )
    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getExistingDirectory",
        mock_get_directory
    )


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_sprite(path: Path, size: tuple = (32, 32), color: tuple = (255, 0, 0, 255)):
    """Helper to create a test sprite image."""
    from PIL import Image
    img = Image.new("RGBA", size, color)
    img.save(path)
    return path


def create_test_sound(path: Path):
    """Helper to create a minimal test WAV file."""
    import struct

    # Create a minimal valid WAV file (silence)
    with open(path, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36))  # File size - 8
        f.write(b"WAVE")

        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))  # Chunk size
        f.write(struct.pack("<H", 1))   # Audio format (PCM)
        f.write(struct.pack("<H", 1))   # Channels
        f.write(struct.pack("<I", 44100))  # Sample rate
        f.write(struct.pack("<I", 44100))  # Byte rate
        f.write(struct.pack("<H", 1))   # Block align
        f.write(struct.pack("<H", 8))   # Bits per sample

        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", 0))   # Data size (empty)

    return path


# ============================================================================
# Additional Shared Fixtures
# ============================================================================

@pytest.fixture
def mock_action_executor():
    """Create a mock action executor for tests.

    Common across game_runner, instance, and room tests.
    """
    executor = MagicMock()
    executor.execute_event = MagicMock()
    executor.execute_action = MagicMock()
    executor.execute_collision_event = MagicMock()
    return executor


@pytest.fixture
def mock_asset_manager():
    """Create a mock asset manager for tests.

    Common across widget and editor tests.
    """
    mock = MagicMock()
    mock.get_asset.return_value = None
    mock.assets_cache = {}
    mock.get_supported_formats.return_value = [".png", ".jpg", ".gif"]
    mock.project_directory = None
    return mock


@pytest.fixture
def mock_project_manager():
    """Create a mock project manager for tests.

    Common across widget and editor tests.
    """
    mock = MagicMock()
    mock.current_project_path = Path("/fake/project")
    mock.current_project_data = {
        "name": "Test Project",
        "version": "1.0.0",
        "assets": {
            "sprites": {},
            "sounds": {},
            "backgrounds": {},
            "objects": {},
            "rooms": {},
            "fonts": {},
            "data": {}
        },
        "room_order": [],
        "game_settings": {
            "window_width": 800,
            "window_height": 600,
            "fps": 60
        }
    }
    mock.is_dirty.return_value = False
    mock.is_dirty_flag = False
    return mock


@pytest.fixture
def sample_sound_path(temp_dir):
    """Create a sample WAV sound file."""
    sound_path = temp_dir / "test_sound.wav"
    return create_test_sound(sound_path)


@pytest.fixture
def project_with_objects(temp_project_dir):
    """Create a project with sample objects for testing."""
    project_file = temp_project_dir / "project.json"
    with open(project_file) as f:
        data = json.load(f)

    data["assets"]["objects"] = {
        "obj_player": {
            "name": "obj_player",
            "sprite": "spr_player",
            "visible": True,
            "solid": False,
            "depth": 0,
            "events": {
                "create": {"actions": []},
                "step": {"actions": []}
            }
        },
        "obj_enemy": {
            "name": "obj_enemy",
            "sprite": "spr_enemy",
            "visible": True,
            "solid": True,
            "depth": 10,
            "events": {}
        },
        "obj_wall": {
            "name": "obj_wall",
            "sprite": "spr_wall",
            "visible": True,
            "solid": True,
            "depth": 100,
            "events": {}
        }
    }

    with open(project_file, "w") as f:
        json.dump(data, f, indent=2)

    return temp_project_dir


@pytest.fixture
def project_with_rooms(temp_project_dir):
    """Create a project with sample rooms for testing."""
    project_file = temp_project_dir / "project.json"
    with open(project_file) as f:
        data = json.load(f)

    data["room_order"] = ["room_start", "room_game", "room_end"]
    data["assets"]["rooms"] = {
        "room_start": {
            "name": "room_start",
            "width": 800,
            "height": 600,
            "background_color": "#000000",
            "instances": []
        },
        "room_game": {
            "name": "room_game",
            "width": 1024,
            "height": 768,
            "background_color": "#87CEEB",
            "instances": [
                {"object_name": "obj_player", "x": 100, "y": 400},
                {"object_name": "obj_enemy", "x": 700, "y": 400}
            ]
        },
        "room_end": {
            "name": "room_end",
            "width": 800,
            "height": 600,
            "background_color": "#000000",
            "instances": []
        }
    }

    with open(project_file, "w") as f:
        json.dump(data, f, indent=2)

    return temp_project_dir


# ============================================================================
# pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "widget: mark test as requiring Qt widgets (needs PySide6 and pytest-qt)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
