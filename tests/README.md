# PyGameMaker IDE - Test Suite

This directory contains automated tests for the PyGameMaker IDE using pytest and pytest-qt.

## Quick Start

### Install test dependencies

```bash
pip install pytest pytest-qt pillow
```

### Run all tests

```bash
# Run from tests directory to avoid root __init__.py issues
cd tests && pytest -v
```

### Run specific test categories

```bash
# Unit tests only (no GUI)
pytest -m "not widget"

# Widget tests only (require Qt)
pytest -m widget

# Integration tests
pytest -m integration

# Run with verbose output
pytest -v
```

## Test Files

| File | Component | Dependencies | Description |
|------|-----------|--------------|-------------|
| `test_config.py` | Config | None | Configuration loading/saving, no Qt required |
| `test_action_executor.py` | ActionExecutor | pygame | Game action execution and expression parsing |
| `test_game_runner.py` | GameRunner | pygame | Game loop, collision detection, room management |
| `test_asset_manager.py` | AssetManager | PySide6, PIL | Asset import/export, thumbnails, caching |
| `test_project_manager.py` | ProjectManager | PySide6 | Project lifecycle, save/load, dirty state |
| `test_widgets.py` | Qt Widgets | PySide6, pytest-qt | UI components, dialogs, panels |
| `test_integration.py` | Integration | PySide6 | End-to-end workflows |
| `test_exporters.py` | Exporters | PySide6, PIL | HTML5 and Kivy export functionality |

## Optional Dependencies

Tests gracefully skip when optional dependencies are not available:

- **PySide6**: Required for Qt widget tests and most IDE components
- **pytest-qt**: Required for interactive widget testing with `qtbot`
- **pygame**: Required for game runtime tests
- **PIL/Pillow**: Required for sprite/image handling tests

## conftest.py - Shared Test Infrastructure

The `conftest.py` file provides centralized test configuration and fixtures.

### Dependency Detection

```python
from conftest import HAS_PYSIDE6, HAS_PYTEST_QT, HAS_PYGAME, HAS_PIL
```

These boolean constants indicate which optional dependencies are available.

### Skip Markers

Pre-configured skip markers for common dependency patterns:

```python
from conftest import skip_without_pyside6, skip_without_pygame

# Skip entire file if PySide6 is not available
pytestmark = skip_without_pyside6

# Skip specific test
@skip_without_pygame
def test_game_loop():
    ...
```

Available markers:
- `skip_without_pyside6` - Skip if PySide6 not installed
- `skip_without_pytest_qt` - Skip if pytest-qt not installed
- `skip_without_qt_widgets` - Skip if PySide6 OR pytest-qt not installed
- `skip_without_pygame` - Skip if pygame not available
- `skip_without_pil` - Skip if PIL/Pillow not installed

### Direct Module Import

When you need to import a module without triggering package `__init__.py` files:

```python
from conftest import import_module_directly

# Import utils/config.py without triggering root __init__.py (which imports PySide6)
config_module = import_module_directly("utils/config.py")
Config = config_module.Config
```

## Fixtures

### Directory Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `temp_dir` | function | Empty temporary directory, cleaned up after test |
| `temp_project_dir` | function | Project directory with structure and project.json |
| `temp_config_dir` | function | Config directory for settings tests |

### Data Fixtures

| Fixture | Description |
|---------|-------------|
| `sample_project_data` | Complete project data dictionary |
| `sample_object_data` | Object definition with events |
| `sample_room_data` | Room definition with instances |
| `sample_sprite_path` | Path to a created 32x32 test PNG |
| `sample_sound_path` | Path to a created test WAV file |

### Mock Fixtures

| Fixture | Description |
|---------|-------------|
| `mock_pygame` | Patches pygame module |
| `mock_qapp` | Mocks QApplication.instance() |
| `mock_file_dialog` | Mocks Qt file dialogs to return fake paths |
| `mock_action_executor` | Mock for action execution |
| `mock_asset_manager` | Mock for asset management |
| `mock_project_manager` | Mock for project management |

### Extended Project Fixtures

| Fixture | Description |
|---------|-------------|
| `project_with_objects` | Project with obj_player, obj_enemy, obj_wall |
| `project_with_rooms` | Project with room_start, room_game, room_end |

## Custom Markers

Register in your tests with:

```python
@pytest.mark.widget
def test_dialog_opens():
    ...

@pytest.mark.slow
def test_full_export():
    ...

@pytest.mark.integration
def test_complete_workflow():
    ...
```

## Test Conventions

### File Organization

- One test file per major component
- Test classes group related tests (e.g., `TestProjectManagerCreation`, `TestProjectManagerLoading`)
- Test methods named `test_<behavior>` or `test_<method>_<scenario>`

### Dependency Handling Pattern

```python
"""
Tests for ComponentX
"""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import skip marker from conftest
from conftest import skip_without_pyside6

# Apply to all tests in file
pytestmark = skip_without_pyside6


class TestComponentX:
    """Test ComponentX functionality"""

    @pytest.fixture
    def component(self):
        """Create component instance"""
        from module.component import ComponentX
        return ComponentX()

    def test_basic_operation(self, component):
        """ComponentX should perform basic operation"""
        result = component.do_something()
        assert result is not None
```

### Importing from Project

Due to the root `__init__.py` importing PySide6, use these patterns:

1. **For PySide6-dependent modules**: Use `skip_without_pyside6` marker
2. **For pure Python modules**: Use `import_module_directly()` helper
3. **For pygame modules**: Use `skip_without_pygame` marker with SDL dummy drivers

### SDL Dummy Drivers

The `conftest.py` automatically sets SDL environment variables before pygame import:

```python
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
```

This allows pygame tests to run in headless CI environments.

## Helper Functions

Available in conftest.py:

```python
from conftest import create_test_sprite, create_test_sound

# Create a test sprite
sprite_path = create_test_sprite(temp_dir / "player.png", size=(64, 64), color=(0, 255, 0, 255))

# Create a test sound
sound_path = create_test_sound(temp_dir / "jump.wav")
```

## Running Tests Locally

### Linux

```bash
# Install Qt dependencies
sudo apt-get install libegl1 libgl1-mesa-glx libxkbcommon0

# Run with virtual display (headless)
xvfb-run -a pytest

# Or set offscreen platform
QT_QPA_PLATFORM=offscreen pytest
```

### Windows

```bash
# Just run pytest directly
pytest
```

### macOS

```bash
# Just run pytest directly
pytest
```

## CI Integration

Tests are designed to run in CI environments:

- Qt tests use offscreen platform (`-platform offscreen`)
- pygame tests use dummy SDL drivers
- Optional dependencies are detected and tests skip gracefully
- No interactive prompts or GUI windows

## Troubleshooting

### "Cannot connect to X server"

Run with virtual display:
```bash
xvfb-run -a pytest
```

Or use offscreen platform:
```bash
QT_QPA_PLATFORM=offscreen pytest
```

### "No module named 'pygame'"

Install pygame:
```bash
pip install pygame
```

### Tests pass locally but fail in CI

Check that:
1. All dependencies are in requirements files
2. Tests don't depend on local file paths
3. Tests don't require network access
4. Display-dependent tests are marked with `@pytest.mark.widget`

### Import errors from root __init__.py

The root `__init__.py` imports PySide6. For tests that don't need Qt:
```python
# Use direct module import
from conftest import import_module_directly
config_module = import_module_directly("utils/config.py")
```

## Adding New Tests

1. Create `test_<component>.py` in the tests directory
2. Import appropriate skip markers from conftest
3. Use shared fixtures where applicable
4. Group related tests in classes
5. Document any new fixtures you add to conftest.py

## Coverage Reports

Generate HTML coverage report:

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

Generate terminal coverage summary:

```bash
pytest --cov=. --cov-report=term-missing
```
