# Testing Quick Start Guide

This guide will help you get started with the PyGameMaker IDE test suite in under 5 minutes.

## 🚀 Quick Setup (2 minutes)

### 1. Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs:
- pytest (test framework)
- pytest-cov (coverage reporting)
- pytest-qt (Qt widget testing)
- pytest-mock (mocking utilities)
- And other development tools

### 2. Verify Installation

```bash
pytest --version
```

You should see: `pytest 7.4.0` (or higher)

## ✅ Run Your First Tests (1 minute)

### Run all tests:
```bash
pytest
```

Expected output:
```
================ test session starts ================
platform linux -- Python 3.11.0, pytest-7.4.0
collected 150+ items

tests/unit/test_project_manager.py ............ [ 40%]
tests/unit/test_asset_manager.py .............. [ 75%]
tests/unit/test_event_system.py ............... [100%]

================ 150+ passed in 5.23s ================
```

### Run with verbose output:
```bash
pytest -v
```

### Run specific test file:
```bash
pytest tests/unit/test_project_manager.py
```

## 📊 Check Test Coverage (1 minute)

### Generate coverage report:
```bash
pytest --cov=pythongm --cov-report=term-missing
```

### Generate HTML coverage report:
```bash
pytest --cov=pythongm --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage.

## 🎯 Common Commands

### Run only fast unit tests:
```bash
pytest -m unit
```

### Run tests in parallel (faster):
```bash
pytest -n auto
```

### Stop on first failure:
```bash
pytest -x
```

### Run last failed tests:
```bash
pytest --lf
```

### Show print statements:
```bash
pytest -s
```

### Run with debugger on failure:
```bash
pytest --pdb
```

## 📝 Test File Overview

| File | Tests | What It Tests |
|------|-------|---------------|
| `test_project_manager.py` | 60+ | Project creation, loading, saving, dirty tracking |
| `test_asset_manager.py` | 50+ | Asset import, deletion, thumbnails, validation |
| `test_event_system.py` | 40+ | Events, actions, serialization |

## 🔧 Writing Your First Test

Create a new test file: `tests/unit/test_example.py`

```python
import pytest
from pythongm.core.project_manager import ProjectManager

def test_project_manager_exists(project_manager):
    """Test that ProjectManager can be instantiated"""
    assert project_manager is not None

def test_create_project(project_manager, temp_dir):
    """Test creating a new project"""
    result = project_manager.create_project("my_project", str(temp_dir))
    assert result is True
```

Run it:
```bash
pytest tests/unit/test_example.py -v
```

## 🐛 Troubleshooting

### Issue: "No module named 'pythongm'"
**Solution:** Make sure you're in the project root directory

### Issue: "QApplication instance already exists"
**Solution:** Use the `qapp` fixture instead of creating your own:
```python
def test_example(qapp):  # Use this fixture
    # Your test code
```

### Issue: Tests are slow
**Solution:** Run in parallel:
```bash
pytest -n auto
```

## 📚 Next Steps

1. Read the full test documentation: `tests/README.md`
2. Look at existing tests for examples
3. Write tests for your new features
4. Run `pytest --cov` to check coverage

## 🎓 Learning Resources

- **Pytest Docs**: https://docs.pytest.org/
- **pytest-qt Docs**: https://pytest-qt.readthedocs.io/
- **Coverage Docs**: https://coverage.readthedocs.io/

## 💡 Pro Tips

1. **Use fixtures** - Don't repeat setup code
2. **One assertion per test** - Keep tests focused
3. **Clear test names** - Name should describe what it tests
4. **Test edge cases** - Not just happy paths
5. **Keep tests fast** - Mock external dependencies

## ✨ That's It!

You're now ready to write and run tests for PyGameMaker IDE.

For more details, see: `tests/README.md`

Happy testing! 🎉
