# PyGameMaker IDE - Test Suite

This directory contains automated tests for the PyGameMaker IDE using pytest and pytest-qt.

## Quick Start

### Install test dependencies

```bash
pip install -r requirements-test.txt
```

### Run all tests

```bash
pytest
```

### Run specific test categories

```bash
# Unit tests only (fast, no GUI)
pytest -m "not widget"

# Widget tests only (require Qt display)
pytest -m widget

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html
```

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── test_config.py        # Tests for Config class (utils/config.py)
├── test_project_manager.py   # Tests for ProjectManager (core/project_manager.py)
├── test_asset_manager.py     # Tests for AssetManager (core/asset_manager.py)
├── test_widgets.py       # Qt widget tests (require display)
└── README.md             # This file
```

## Test Categories (Markers)

Tests are categorized using pytest markers:

- **`unit`** - Fast unit tests that don't require Qt or display
- **`widget`** - Widget/UI tests that require Qt application context
- **`integration`** - Slower integration tests
- **`slow`** - Tests that take a long time to run

### Examples

```bash
# Run only unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"

# Run widget tests with visible window (for debugging)
QT_QPA_PLATFORM=xcb pytest -m widget
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

## Writing New Tests

### Unit Tests

```python
# tests/test_my_module.py

import pytest
from pathlib import Path

class TestMyClass:
    def test_basic_functionality(self, temp_dir):
        # Use fixtures from conftest.py
        from my_module import MyClass
        obj = MyClass()
        assert obj.do_something() == expected_result
```

### Widget Tests

```python
# tests/test_my_widget.py

import pytest

pytestmark = pytest.mark.widget  # Mark all tests as widget tests

class TestMyWidget:
    def test_widget_creates(self, qtbot):
        from my_module import MyWidget
        widget = MyWidget()
        qtbot.addWidget(widget)
        assert widget is not None

    def test_button_click(self, qtbot):
        from my_module import MyWidget
        widget = MyWidget()
        qtbot.addWidget(widget)

        # Simulate button click
        qtbot.mouseClick(widget.my_button, Qt.LeftButton)

        assert widget.was_clicked
```

## Fixtures

Common fixtures are defined in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `temp_dir` | Temporary directory that's cleaned up after test |
| `temp_project_dir` | Temporary project with proper structure |
| `sample_sprite_path` | Creates a sample PNG sprite |
| `sample_project_data` | Sample project.json data |
| `mock_config` | Temporary config file |
| `mock_pygame` | Mocks pygame for headless testing |
| `mock_file_dialog` | Mocks Qt file dialogs |

## CI/CD Pipeline

Tests run automatically on GitHub Actions:

- **On every push** to `main` or `develop`
- **On every pull request** to `main` or `develop`

The pipeline includes:

1. **Unit Tests** - Run on Python 3.10, 3.11, 3.12
2. **Widget Tests** - Run with Xvfb virtual display
3. **Integration Tests** - Full test suite with coverage
4. **Windows Tests** - Cross-platform validation (main branch only)
5. **Code Quality** - Flake8 linting

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

Install all dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Tests pass locally but fail in CI

Check that:
1. All dependencies are in requirements files
2. Tests don't depend on local file paths
3. Tests don't require network access
4. Display-dependent tests are marked with `@pytest.mark.widget`

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
