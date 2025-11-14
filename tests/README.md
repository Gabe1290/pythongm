# PyGameMaker IDE - Test Suite Documentation

This directory contains the comprehensive test suite for PyGameMaker IDE.

## 📁 Directory Structure

```
tests/
├── README.md                  # This file
├── conftest.py               # Root fixtures and configuration
├── __init__.py
│
├── unit/                     # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_project_manager.py    # 60+ tests for ProjectManager
│   ├── test_asset_manager.py      # 50+ tests for AssetManager
│   └── test_event_system.py       # 40+ tests for EventSystem
│
├── integration/              # Integration tests (cross-component)
│   ├── __init__.py
│   └── (to be added)
│
├── e2e/                      # End-to-end tests (full workflows)
│   ├── __init__.py
│   └── (to be added)
│
└── fixtures/                 # Test data and fixtures
    ├── conftest.py          # Fixture-specific configuration
    ├── sample_projects/     # Sample project directories
    └── test_assets/         # Sample images, sounds, etc.
```

---

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Verify installation:**
   ```bash
   pytest --version
   ```

### Running Tests

#### Run all tests:
```bash
pytest
```

#### Run specific test file:
```bash
pytest tests/unit/test_project_manager.py
```

#### Run specific test class:
```bash
pytest tests/unit/test_project_manager.py::TestProjectManagerCreation
```

#### Run specific test:
```bash
pytest tests/unit/test_project_manager.py::TestProjectManagerCreation::test_create_project_creates_directory
```

#### Run with verbose output:
```bash
pytest -v
```

#### Run with coverage:
```bash
pytest --cov=pythongm --cov-report=html
```

#### Run only unit tests:
```bash
pytest -m unit
```

#### Run tests in parallel (faster):
```bash
pytest -n auto
```

---

## 📊 Test Categories

Tests are organized using pytest markers:

- **`@pytest.mark.unit`** - Fast, isolated unit tests
- **`@pytest.mark.integration`** - Multi-component integration tests
- **`@pytest.mark.e2e`** - End-to-end workflow tests
- **`@pytest.mark.slow`** - Tests that take significant time
- **`@pytest.mark.requires_display`** - Tests requiring X display
- **`@pytest.mark.requires_audio`** - Tests requiring audio system

### Running by Category

```bash
# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# Only tests that don't require display
pytest -m "not requires_display"
```

---

## 📝 Test Coverage Summary

### Current Coverage

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| ProjectManager | 60+ | ~90% | ✅ Complete |
| AssetManager | 50+ | ~85% | ✅ Complete |
| EventSystem | 40+ | ~80% | ✅ Complete |
| GameEngine | 0 | 0% | ⏳ Pending |
| ActionExecutor | 0 | 0% | ⏳ Pending |
| VisualCodeGenerator | 0 | 0% | ⏳ Pending |
| HTML5Exporter | 0 | 0% | ⏳ Pending |

### Target Coverage Goals

- **Critical modules** (ProjectManager, AssetManager, GameEngine): 90%+
- **High-priority modules** (EventSystem, ActionExecutor): 80%+
- **Overall codebase**: 80-85%

---

## 🧪 Writing Tests

### Test File Naming

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*` (e.g., `TestProjectManager`)
- Test functions: `test_*` (e.g., `test_create_project`)

### Example Test

```python
import pytest
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
```

### Using Fixtures

Common fixtures available in `conftest.py`:

```python
def test_example(
    qapp,              # QApplication instance
    qtbot,             # QtBot for Qt testing
    temp_dir,          # Temporary directory (auto-cleanup)
    project_dir,       # Project directory with structure
    sample_sprite_file, # Test sprite image
    sample_sound_file,  # Test sound file
    project_manager,   # ProjectManager instance
    asset_manager,     # AssetManager instance
    event_system       # EventSystem instance
):
    # Your test code here
    pass
```

### Parametrized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("asset_type", [
    "sprites", "sounds", "backgrounds", "objects"
])
def test_asset_types(asset_manager, asset_type):
    """Test different asset types"""
    # Test logic here
    pass
```

### Testing Qt Signals

```python
def test_signal_emission(project_manager, qtbot):
    """Test that a signal is emitted"""
    with qtbot.waitSignal(project_manager.project_created, timeout=1000):
        project_manager.create_project("test", "/tmp")
```

---

## 🔧 Fixtures Reference

### Application Fixtures

- **`qapp`** - QApplication instance (session scope)
- **`qtbot`** - QtBot for widget/signal testing

### Directory Fixtures

- **`temp_dir`** - Temporary directory (auto-cleanup)
- **`project_dir`** - Project directory with standard structure

### Asset Fixtures

- **`sample_image`** - PIL Image object
- **`sample_sprite_file`** - Path to test sprite PNG
- **`sample_sound_file`** - Path to test WAV file
- **`multiple_test_images`** - Dict of various image formats

### Data Fixtures

- **`sample_project_data`** - Sample project.json structure
- **`complete_sample_project`** - Full project with assets

### Component Fixtures

- **`project_manager`** - ProjectManager instance
- **`asset_manager`** - AssetManager instance
- **`event_system`** - EventSystem instance
- **`mock_asset_manager`** - Mock AssetManager for testing
- **`mock_pygame`** - Mock pygame for headless testing

### Helper Fixtures

- **`create_project_file`** - Function to create project.json

---

## 🐛 Debugging Tests

### Run with debugger:
```bash
pytest --pdb
```

### Show print statements:
```bash
pytest -s
```

### Show local variables on failure:
```bash
pytest --showlocals
```

### Run last failed tests only:
```bash
pytest --lf
```

### Run failed tests first:
```bash
pytest --ff
```

### Stop on first failure:
```bash
pytest -x
```

### Increase verbosity:
```bash
pytest -vv
```

---

## 📈 Coverage Reports

### Generate HTML coverage report:
```bash
pytest --cov=pythongm --cov-report=html
open htmlcov/index.html  # View in browser
```

### Terminal coverage report:
```bash
pytest --cov=pythongm --cov-report=term-missing
```

### XML coverage (for CI):
```bash
pytest --cov=pythongm --cov-report=xml
```

---

## 🔄 Continuous Integration

Tests run automatically on:
- Every push to any branch
- Every pull request
- Scheduled daily runs

See `.github/workflows/tests.yml` for CI configuration.

### CI Environment

- Python versions: 3.9, 3.10, 3.11
- Operating systems: Ubuntu, Windows, macOS
- Headless display: Xvfb (Linux)
- Coverage: Uploaded to Codecov

---

## 📋 Test Checklist

When adding a new feature:

- [ ] Write unit tests for new functions/classes
- [ ] Write integration tests for cross-component features
- [ ] Add parametrized tests for multiple scenarios
- [ ] Test error conditions and edge cases
- [ ] Ensure all signals are tested
- [ ] Test serialization/deserialization
- [ ] Verify file I/O operations
- [ ] Test with different OS paths
- [ ] Update this README if needed
- [ ] Ensure coverage stays above 80%

---

## 🎯 Test Priorities

### Phase 1: Core Managers (✅ Complete)
- [x] ProjectManager (60+ tests)
- [x] AssetManager (50+ tests)
- [x] EventSystem (40+ tests)

### Phase 2: Runtime (⏳ Next)
- [ ] GameEngine (20 tests planned)
- [ ] ActionExecutor (20 tests planned)
- [ ] GameRunner (10 tests planned)

### Phase 3: Visual Programming (⏳ Pending)
- [ ] VisualCodeGenerator (12 tests planned)
- [ ] VisualNode (12 tests planned)
- [ ] VisualCanvas (15 tests planned)

### Phase 4: Export & UI (⏳ Pending)
- [ ] HTML5Exporter (8 tests planned)
- [ ] IDEWindow (15 tests planned)

### Phase 5: Integration (⏳ Pending)
- [ ] Project lifecycle integration
- [ ] Asset workflow integration
- [ ] Game execution integration
- [ ] Visual programming integration

---

## 🤝 Contributing Tests

### Guidelines

1. **Write clear test names** - Test name should describe what it tests
2. **One assertion per test** - Keep tests focused
3. **Use fixtures** - Don't repeat setup code
4. **Test edge cases** - Not just happy paths
5. **Add docstrings** - Explain what each test does
6. **Keep tests fast** - Mock external dependencies
7. **Avoid flaky tests** - Tests should be deterministic

### Example Pull Request Checklist

- [ ] All new code has tests
- [ ] All tests pass locally
- [ ] Coverage hasn't decreased
- [ ] Tests follow naming conventions
- [ ] Fixtures are reused where possible
- [ ] Documentation updated

---

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [PySide6 Testing Guide](https://doc.qt.io/qtforpython/testing.html)

---

## 🆘 Troubleshooting

### Common Issues

**Issue: "QApplication instance already exists"**
```bash
# Solution: Use the qapp fixture instead of creating your own
def test_example(qapp):  # This provides QApplication
    pass
```

**Issue: "Display not found" on CI**
```bash
# Solution: Tests automatically use SDL_VIDEODRIVER=dummy
# If needed, add @pytest.mark.requires_display
```

**Issue: "Pygame mixer not initialized"**
```bash
# Solution: Use mock_pygame fixture or ensure pygame.mixer.init()
# is called before tests
```

**Issue: Tests are slow**
```bash
# Solution: Run in parallel
pytest -n auto

# Or skip slow tests
pytest -m "not slow"
```

---

## 📊 Statistics

- **Total Tests**: 150+
- **Estimated Runtime**: ~2 minutes (unit tests)
- **Code Coverage**: ~50% (target: 80%)
- **Lines of Test Code**: ~3,000+
- **Test Files**: 3 (more planned)

---

**Last Updated**: 2024-11-14
**Maintainer**: PyGameMaker IDE Team
