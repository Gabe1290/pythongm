#!/usr/bin/env python3
"""
Root conftest.py for PyGameMaker IDE tests
Provides shared fixtures and configuration for all tests
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
from PIL import Image

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'


# ============================================================================
# Qt Application Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def qapp():
    """
    Create a QApplication instance for the entire test session.
    Required for any Qt-based tests.
    """
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    yield app

    # Cleanup
    app.quit()


@pytest.fixture
def qtbot(qapp):
    """
    Provides QtBot for testing Qt widgets and signals.
    Note: Install pytest-qt for full QtBot functionality.
    For basic tests, we provide a minimal implementation.
    """
    try:
        from pytestqt.qtbot import QtBot
        bot = QtBot(qapp)
        yield bot
    except ImportError:
        # Minimal qtbot implementation if pytest-qt not installed
        class MinimalQtBot:
            def __init__(self, app):
                self.app = app
                self._widgets = []

            def addWidget(self, widget):
                """Track widget for cleanup"""
                self._widgets.append(widget)
                return widget

            def waitSignal(self, signal, timeout=1000):
                """Basic signal waiting (simplified)"""
                from PySide6.QtCore import QEventLoop, QTimer
                loop = QEventLoop()
                signal.connect(loop.quit)
                QTimer.singleShot(timeout, loop.quit)
                loop.exec()

            def cleanup(self):
                for widget in self._widgets:
                    widget.deleteLater()
                self._widgets.clear()

        bot = MinimalQtBot(qapp)
        yield bot
        bot.cleanup()


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """
    Create a temporary directory that is automatically cleaned up.
    Returns a Path object.
    """
    tmp = tempfile.mkdtemp()
    tmp_path = Path(tmp)
    yield tmp_path

    # Cleanup
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def project_dir(temp_dir):
    """
    Create a temporary project directory with standard structure.
    """
    project_path = temp_dir / "test_project"
    project_path.mkdir(exist_ok=True)

    # Create standard directories
    for dirname in ["sprites", "sounds", "backgrounds", "objects",
                    "rooms", "scripts", "fonts", "data", "thumbnails"]:
        (project_path / dirname).mkdir(exist_ok=True)

    return project_path


# ============================================================================
# Test Asset Fixtures
# ============================================================================

@pytest.fixture
def sample_image():
    """
    Create a simple test image (PNG) in memory.
    Returns PIL Image object.
    """
    img = Image.new('RGB', (100, 100), color='red')
    return img


@pytest.fixture
def sample_sprite_file(temp_dir):
    """
    Create a temporary sprite image file.
    Returns Path to the file.
    """
    sprite_path = temp_dir / "test_sprite.png"
    img = Image.new('RGB', (64, 64), color='blue')
    img.save(sprite_path)
    return sprite_path


@pytest.fixture
def sample_sound_file(temp_dir):
    """
    Create a minimal WAV file for testing.
    Returns Path to the file.
    """
    sound_path = temp_dir / "test_sound.wav"

    # Create minimal valid WAV file (44 bytes header + 1 sample)
    # This is a mono, 8-bit, 8000Hz WAV with silence
    wav_data = bytes([
        # RIFF header
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x00, 0x00, 0x00,  # File size - 8
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        # fmt chunk
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Chunk size (16)
        0x01, 0x00,              # Audio format (1 = PCM)
        0x01, 0x00,              # Channels (1 = mono)
        0x40, 0x1F, 0x00, 0x00,  # Sample rate (8000)
        0x40, 0x1F, 0x00, 0x00,  # Byte rate
        0x01, 0x00,              # Block align
        0x08, 0x00,              # Bits per sample (8)
        # data chunk
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x01, 0x00, 0x00, 0x00,  # Data size (1 byte)
        0x80,                     # One sample (silence)
    ])

    with open(sound_path, 'wb') as f:
        f.write(wav_data)

    return sound_path


@pytest.fixture
def sample_project_data():
    """
    Returns a sample project.json data structure.
    """
    return {
        "version": "1.0.0",
        "name": "TestProject",
        "created": "2024-01-01T00:00:00",
        "modified": "2024-01-01T00:00:00",
        "settings": {
            "width": 800,
            "height": 600,
            "fps": 60
        },
        "sprites": {},
        "sounds": {},
        "backgrounds": {},
        "objects": {},
        "rooms": {},
        "scripts": {},
        "fonts": {},
        "data": {}
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_asset_manager():
    """
    Create a mock AssetManager for testing components that depend on it.
    """
    from PySide6.QtCore import QObject, Signal

    class MockAssetManager(QObject):
        asset_imported = Signal(str, str, dict)
        asset_deleted = Signal(str, str)
        asset_updated = Signal(str, str, dict)
        status_changed = Signal(str)

        def __init__(self):
            super().__init__()
            self.project_directory = None
            self.assets_cache = {}
            self.thumbnails_cache = {}

        def set_project_directory(self, directory):
            self.project_directory = directory

        def import_asset(self, *args, **kwargs):
            return {"name": "test_asset", "path": "test/path"}

        def delete_asset(self, *args, **kwargs):
            return True

        def get_asset(self, asset_type, asset_name):
            return self.assets_cache.get(f"{asset_type}/{asset_name}")

    return MockAssetManager()


@pytest.fixture
def mock_pygame():
    """
    Mock pygame for tests that don't need actual pygame functionality.
    """
    mock = Mock()
    mock.mixer = Mock()
    mock.mixer.init = Mock()
    mock.mixer.Sound = Mock()
    mock.display = Mock()
    mock.display.set_mode = Mock(return_value=Mock())
    mock.image = Mock()
    mock.image.load = Mock(return_value=Mock())

    return mock


# ============================================================================
# Project Manager Fixtures
# ============================================================================

@pytest.fixture
def project_manager(qapp, mock_asset_manager):
    """
    Create a ProjectManager instance with a mock asset manager.
    """
    from pythongm.core.project_manager import ProjectManager

    pm = ProjectManager(asset_manager=mock_asset_manager)
    yield pm

    # Cleanup
    if pm.auto_save_timer.isActive():
        pm.auto_save_timer.stop()


# ============================================================================
# Asset Manager Fixtures
# ============================================================================

@pytest.fixture
def asset_manager(qapp, project_dir):
    """
    Create an AssetManager instance with a temporary project directory.
    """
    from pythongm.core.asset_manager import AssetManager

    am = AssetManager(project_directory=project_dir)
    yield am

    # Cleanup is handled by temp_dir fixture


# ============================================================================
# Event System Fixtures
# ============================================================================

@pytest.fixture
def event_system(qapp):
    """
    Create an EventSystem instance.
    """
    from pythongm.core.event_system import EventSystem

    es = EventSystem()
    return es


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_project_file(project_path: Path, project_data: dict):
    """
    Helper function to create a project.json file.

    Args:
        project_path: Path to project directory
        project_data: Dictionary of project data
    """
    project_file = project_path / "project.json"
    with open(project_file, 'w') as f:
        import json
        json.dump(project_data, f, indent=2)

    return project_file


# Make helper available to tests
@pytest.fixture
def create_project_file():
    """Fixture that returns the helper function"""
    return create_test_project_file


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """
    Pytest configuration hook.
    Register custom markers.
    """
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (moderate speed)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (slow)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take significant time"
    )
    config.addinivalue_line(
        "markers", "requires_display: Tests requiring X display"
    )
    config.addinivalue_line(
        "markers", "requires_audio: Tests requiring audio system"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection.
    Add markers automatically based on test location.
    """
    for item in items:
        # Add marker based on test location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
