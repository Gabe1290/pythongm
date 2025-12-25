"""
PyGameMaker IDE - Pytest Configuration and Fixtures

This module provides shared fixtures for all tests:
- Qt application setup (qtbot)
- Temporary project directories
- Mock assets and configurations
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure the project root is in the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


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

    # Create a minimal project.json
    project_data = {
        "name": "Test Project",
        "version": "1.0.0",
        "author": "Test Author",
        "description": "A test project",
        "room_order": [],
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
