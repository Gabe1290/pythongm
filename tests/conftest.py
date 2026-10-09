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

# Every individual test file in this repo defensively does this same
# sys.path.insert for itself (so `from utils.config import ...`-style
# repo-relative imports resolve regardless of CWD at invocation time), but
# conftest.py itself never did -- harmless as long as pytest always runs
# from the repo root (plain `python -m pytest`'s own sys.path[0] insertion
# covers it then), which is how every local session in this repo's history
# happened to invoke it. CI's actual jobs run `cd tests && pytest ...`
# (.github/workflows/tests.yml), so CWD is tests/ at invocation and the
# repo root was never on sys.path at all -- invisible locally, and it broke
# every CI job the moment this file gained its first module-level
# repo-relative import (the Config-isolation block below): "ModuleNotFoundError:
# No module named 'utils'" raised while loading conftest.py itself, which
# aborts the whole pytest session before a single test can even collect.
# Reproduced locally with `cd tests && pytest test_config.py` (CI's own
# first command) before fixing this.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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


@pytest.fixture(autouse=True, scope="session")
def _quit_pygame_at_session_end():
    """pygame.init() above has no matching pygame.quit() anywhere in this
    repo (confirmed by grep) -- SDL's subsystems were only ever torn down
    by whatever implicit cleanup runs at interpreter shutdown, not pygame's
    own documented quit() path. Added as a plausible mitigation for a CI
    crash (see _gc_collect_after_every_test below) -- CONFIRMED NOT
    SUFFICIENT on its own: the crash still reproduced on the next CI run
    with this fixture already in place. Left in anyway since it's still
    the documented-correct lifecycle and genuinely harmless (only runs
    after every test has already finished), but it is not, by itself,
    the fix."""
    yield
    if HAS_PYGAME:
        pygame.quit()


@pytest.fixture(autouse=True)
def _gc_collect_after_every_test():
    """Diagnostic, not a fix -- and deliberately OPT-IN via
    PYGM_GC_COLLECT_PER_TEST, not a blanket autouse fixture. A CI run
    (tests.yml's unit-tests job, Python 3.10) aborts with `munmap_chunk():
    invalid pointer` (SIGABRT) only after every test in the batch has
    already passed, with `-X faulthandler` showing nothing more specific
    than "Garbage-collecting" / "<no Python frame>" -- i.e. some earlier
    test corrupts the heap, but the crash only surfaces much later,
    during the interpreter's own final gc.collect() at shutdown, by which
    point the actual offending test is impossible to identify from the
    log. Forcing a real gc.collect() after every single test turns
    "crashes once, generically, at process exit" into "crashes right
    after the test that actually caused it" -- the specific test name at
    the point of the abort IS the diagnosis.

    Gated behind the env var because a first attempt at making this
    autouse-always (no gate) produced one (non-reproducing on 3 immediate
    retries) spurious error in tests/test_blockly_block_audit_roundtrip.py
    when run in combination with test_raycast_view.py -- i.e. the
    unconditional version is itself a plausible source of NEW flakiness
    around that file's QWebEngineView (already documented there as
    fragile: "creating more than one QWebEngineView per pytest process
    segfaults here"). The unit-tests CI job that actually has the crash
    never touches QWebEngineView at all, so this only needs to run there
    -- set by tests.yml's unit-tests step, never globally, so local runs
    and the separate widget-tests (Qt) job are both unaffected."""
    yield
    if os.environ.get("PYGM_GC_COLLECT_PER_TEST"):
        import gc
        gc.collect()


# PIL/Pillow detection
try:
    from PIL import Image as _PIL_Image  # noqa: F401
    del _PIL_Image  # Only used for detection
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ============================================================================
# Isolate Config from the developer's real ~/.pygamemaker/config.json
# ============================================================================
# utils/config.py's Config is a class-level singleton (Config._config_data),
# and its module runs `Config.load()` at IMPORT time -- the very first
# `import utils.config` anywhere (events/plugin_loader.py, widgets/
# welcome_tab.py, ...) reads the developer's real config file before any
# fixture gets a chance to run. Left alone, the test suite sees -- and can
# write back to -- that real file: a developer's own settings (e.g.
# extensions disabled by default for students) leak into what hundreds of
# tests see when they call events.plugin_loader.load_all_plugins(), which
# consults Config for each extension's enabled/disabled override, caching the
# result in a module-level singleton (plugin_loader._shared_loader) for the
# rest of the process -- so whichever Config state existed at the FIRST call
# anywhere sticks for the whole run. This bit a real session (2026-10-01): a
# personal "extensions off" preference on disk made ~200 unrelated tests fail
# with missing actions/presets/asset types, genuinely reproducing on a
# byte-for-byte clean `main` checkout.
#
# A fixture is too late: several test files (test_doom_hud.py,
# test_raycast_action_registration.py, test_raycast_export_parity.py, ...)
# call load_all_plugins() at module scope -- it runs the moment pytest
# IMPORTS that module during collection, before any fixture (even a
# session-scoped autouse one) has run. conftest.py itself, by contrast, is
# always imported before pytest collects any test module in its directory,
# so redirecting Config here as plain module-level code -- not inside a
# fixture -- is the only place guaranteed to run first. Config.load() against
# a nonexistent path returns clean defaults (no "extensions" key at all), so
# every extension's is_extension_enabled() check falls through to its
# manifest default (normally True) regardless of what the developer has
# configured for their own IDE. Any test's Config.set()/.save() during the
# run only ever touches the temp file from here on -- the developer's real
# config is never read or written by a test run again. The matching
# session-scoped fixture below only restores the real path afterward, for
# cleanliness; by the time it runs the redirect above has already done the
# job that actually matters.
#
# tests/test_config.py is unaffected: it loads utils/config.py as its own
# separate module via import_module_directly (its own docstring explains
# why), so its Config class is a different object from the one redirected
# here, and it already repoints _config_file itself per test class.
from utils.config import Config as _Config

_real_config_file = _Config._config_file
_isolated_config_dir = Path(tempfile.mkdtemp(prefix="pygm_test_config_"))
_Config._config_file = _isolated_config_dir / "config.json"
_Config.load()  # populates clean defaults; the temp file doesn't exist yet


@pytest.fixture(autouse=True, scope="session")
def _restore_real_config_file_at_session_end():
    yield
    _Config._config_file = _real_config_file
    shutil.rmtree(_isolated_config_dir, ignore_errors=True)


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
# Auto-dismiss modal dialogs during widget tests
# ============================================================================
# pytest-qt's `qtbot.addWidget(...)` registers a widget for teardown via
# `widget.close()`. When that close path triggers a modal dialog (the
# editor's "Save changes?" prompt is the common case), there is no user
# in CI to click it and the test session deadlocks until --timeout fires.
#
# Patch the three QMessageBox class methods that block on user input
# (`question`, `information`, `warning`) so they auto-return a safe
# default without showing a dialog. Tests that explicitly need to drive
# a dialog can monkeypatch over this fixture themselves.

if HAS_PYSIDE6:
    @pytest.fixture(autouse=True)
    def _auto_dismiss_qmessagebox(monkeypatch, request):
        """Auto-dismiss any QMessageBox during widget-test setup/teardown.

        Only active when the test is marked `widget` (or a fixture
        registers a qtbot-tracked widget); other tests run untouched.
        """
        if 'widget' not in request.keywords and 'qtbot' not in request.fixturenames:
            return
        from PySide6.QtWidgets import QMessageBox

        # Discard preserves "close anyway" semantics for the unsaved-changes
        # prompt. For information/warning, the only sensible default is Ok.
        def auto_discard(*args, **kwargs):
            return QMessageBox.StandardButton.Discard

        def auto_ok(*args, **kwargs):
            return QMessageBox.StandardButton.Ok

        monkeypatch.setattr(QMessageBox, 'question', staticmethod(auto_discard))
        monkeypatch.setattr(QMessageBox, 'information', staticmethod(auto_ok))
        monkeypatch.setattr(QMessageBox, 'warning', staticmethod(auto_ok))
        monkeypatch.setattr(QMessageBox, 'critical', staticmethod(auto_ok))


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
    with open(project_dir / "project.json", "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

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
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

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
    with open(project_file, encoding="utf-8") as f:
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

    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return temp_project_dir


@pytest.fixture
def project_with_rooms(temp_project_dir):
    """Create a project with sample rooms for testing."""
    project_file = temp_project_dir / "project.json"
    with open(project_file, encoding="utf-8") as f:
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

    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
