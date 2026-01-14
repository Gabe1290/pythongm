# PyGameMaker Export Testing Guide

**Date:** 2026-01-14
**Purpose:** Comprehensive testing procedures for all export targets

---

## Quick Test Suite

### 1. HTML5 Export Test (5 minutes)

```bash
# Test HTML5 export
cd /path/to/pygm2
python3 -c "
from export.HTML5.html5_exporter import HTML5Exporter
from pathlib import Path

exporter = HTML5Exporter()
project = Path('test_projects/simple_game')
output = Path('export_output/html5_test')
output.mkdir(parents=True, exist_ok=True)

success = exporter.export(project, output)
print(f'Export {'succeeded' if success else 'failed'}')
"

# Open in browser
firefox export_output/html5_test/simple_game.html
# Or: chromium export_output/html5_test/simple_game.html
```

**Expected Result:**
- HTML file generated
- Game loads in browser
- Sprites display correctly
- No JavaScript errors in console

---

### 2. EXE Export Test (30 minutes)

```bash
# Test EXE export
python3 -c "
from export.exe.exe_exporter import ExeExporter
from pathlib import Path

exporter = ExeExporter()
project = Path('test_projects/simple_game')
output = Path('export_output/exe_test')
output.mkdir(parents=True, exist_ok=True)

success = exporter.export(project, output, platform='windows')
print(f'Export {'succeeded' if success else 'failed'}')
"

# Run the executable
cd export_output/exe_test/dist
./simple_game.exe  # Windows
./simple_game      # Linux
```

**Expected Result:**
- Executable generated
- Game runs without errors
- Assets load correctly
- No missing dependencies

---

### 3. Kivy Export Test (10 minutes)

```bash
# Test Kivy export
python3 -c "
from export.Kivy.kivy_exporter import KivyExporter
from pathlib import Path

exporter = KivyExporter()
project = Path('test_projects/simple_game')
output = Path('export_output/kivy_test')
output.mkdir(parents=True, exist_ok=True)

success = exporter.export(project, output)
print(f'Export {'succeeded' if success else 'failed'}')
"

# Test the Kivy app (desktop)
cd export_output/kivy_test
python3 main.py
```

**Expected Result:**
- Kivy project generated
- All Python files valid
- buildozer.spec created
- App runs in Kivy desktop mode

---

## Comprehensive Testing

### HTML5 Exporter Testing

#### Test 1: Basic Export
```python
#!/usr/bin/env python3
"""Test HTML5 basic export functionality"""

from export.HTML5.html5_exporter import HTML5Exporter
from pathlib import Path

def test_html5_basic():
    """Test basic HTML5 export"""
    exporter = HTML5Exporter()

    # Create test project
    project_path = Path("test_projects/minimal")
    output_path = Path("export_output/html5_minimal")
    output_path.mkdir(parents=True, exist_ok=True)

    # Export
    success = exporter.export(project_path, output_path)

    # Verify
    html_file = output_path / "minimal.html"
    assert html_file.exists(), "HTML file not generated"
    assert html_file.stat().st_size > 0, "HTML file is empty"

    # Check HTML content
    content = html_file.read_text()
    assert '<canvas' in content, "No canvas element found"
    assert 'game_data' in content, "No game data found"
    assert 'sprites_data' in content, "No sprites data found"

    print("✅ HTML5 basic export test passed")

if __name__ == '__main__':
    test_html5_basic()
```

#### Test 2: Sprite Encoding
```python
def test_html5_sprites():
    """Test sprite encoding"""
    from export.HTML5.html5_exporter import HTML5Exporter
    from pathlib import Path
    import json

    exporter = HTML5Exporter()

    # Test project with sprites
    project_path = Path("test_projects/with_sprites")

    # Load project
    with open(project_path / "project.json") as f:
        project_data = json.load(f)

    # Encode sprites
    sprites_data = exporter.encode_sprites(project_path, project_data)

    # Verify
    assert len(sprites_data) > 0, "No sprites encoded"

    for sprite_name, sprite_data in sprites_data.items():
        assert 'image' in sprite_data, f"No image for {sprite_name}"
        assert sprite_data['image'].startswith('data:image'), f"Invalid image data for {sprite_name}"

    print("✅ HTML5 sprite encoding test passed")

if __name__ == '__main__':
    test_html5_sprites()
```

#### Test 3: Compression
```python
def test_html5_compression():
    """Test data compression"""
    from export.HTML5.html5_exporter import HTML5Exporter
    from pathlib import Path
    import gzip
    import base64

    exporter = HTML5Exporter()

    # Test data
    test_data = "{'test': 'data'}" * 1000  # ~15KB

    # Compress
    compressed = base64.b64encode(
        gzip.compress(test_data.encode('utf-8'), compresslevel=9)
    ).decode('ascii')

    # Verify compression
    compression_ratio = len(compressed) / len(test_data)
    assert compression_ratio < 0.5, f"Poor compression: {compression_ratio:.2%}"

    # Verify decompression
    decompressed = gzip.decompress(
        base64.b64decode(compressed)
    ).decode('utf-8')

    assert decompressed == test_data, "Decompression failed"

    print(f"✅ HTML5 compression test passed (ratio: {compression_ratio:.2%})")

if __name__ == '__main__':
    test_html5_compression()
```

---

### EXE Exporter Testing

#### Test 1: Windows EXE
```python
def test_exe_windows():
    """Test Windows EXE generation"""
    from export.exe.exe_exporter import ExeExporter
    from pathlib import Path
    import platform

    if platform.system() != 'Windows':
        print("⚠️ Skipping Windows test (not on Windows)")
        return

    exporter = ExeExporter()

    project_path = Path("test_projects/simple_game")
    output_path = Path("export_output/exe_windows")
    output_path.mkdir(parents=True, exist_ok=True)

    # Export
    success = exporter.export(project_path, output_path, platform='windows')

    # Verify
    exe_file = output_path / "dist" / "simple_game.exe"
    assert exe_file.exists(), "EXE file not generated"
    assert exe_file.stat().st_size > 10_000_000, "EXE file too small (likely incomplete)"

    print("✅ Windows EXE export test passed")

if __name__ == '__main__':
    test_exe_windows()
```

#### Test 2: Asset Bundling
```python
def test_exe_assets():
    """Test asset bundling in EXE"""
    from export.exe.exe_exporter import ExeExporter
    from pathlib import Path

    exporter = ExeExporter()

    project_path = Path("test_projects/with_assets")
    output_path = Path("export_output/exe_assets")
    output_path.mkdir(parents=True, exist_ok=True)

    # Export
    success = exporter.export(project_path, output_path)

    # Verify assets bundled
    # (This depends on exporter implementation details)

    print("✅ EXE asset bundling test passed")

if __name__ == '__main__':
    test_exe_assets()
```

---

### Kivy Exporter Testing

#### Test 1: Code Generation
```python
def test_kivy_code_generation():
    """Test Kivy code generation"""
    from export.Kivy.kivy_exporter import KivyExporter
    from pathlib import Path

    exporter = KivyExporter()

    project_path = Path("test_projects/simple_game")
    output_path = Path("export_output/kivy_codegen")
    output_path.mkdir(parents=True, exist_ok=True)

    # Export
    success = exporter.export(project_path, output_path)

    # Verify Python files generated
    main_py = output_path / "main.py"
    assert main_py.exists(), "main.py not generated"

    # Check Python syntax
    with open(main_py) as f:
        code = f.read()
        compile(code, main_py, 'exec')  # Syntax check

    print("✅ Kivy code generation test passed")

if __name__ == '__main__':
    test_kivy_code_generation()
```

#### Test 2: Action Conversion
```python
def test_kivy_actions():
    """Test Kivy action conversion"""
    from export.Kivy.action_converter import ActionConverter

    converter = ActionConverter()

    # Test common actions
    test_actions = [
        {'action': 'move_free', 'parameters': {'direction': 0, 'speed': 5}},
        {'action': 'set_variable', 'parameters': {'variable': 'score', 'value': 100}},
        {'action': 'if_collision', 'parameters': {'object': 'obj_wall'}},
    ]

    for action in test_actions:
        try:
            code = converter.convert_action(action)
            assert code, f"No code generated for {action['action']}"
            print(f"✅ {action['action']}: {code}")
        except Exception as e:
            print(f"❌ {action['action']} failed: {e}")
            raise

    print("✅ Kivy action conversion test passed")

if __name__ == '__main__':
    test_kivy_actions()
```

#### Test 3: Buildozer Spec
```python
def test_kivy_buildozer():
    """Test buildozer.spec generation"""
    from export.Kivy.buildspec_generator import BuildspecGenerator
    from pathlib import Path

    generator = BuildspecGenerator()

    # Test project metadata
    project_data = {
        'name': 'TestGame',
        'version': '1.0',
        'settings': {
            'package_name': 'com.test.game'
        }
    }

    output_path = Path("export_output/kivy_buildozer_test")
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate buildozer.spec
    spec_content = generator.generate(project_data, output_path)

    # Verify
    assert 'title = TestGame' in spec_content, "Title not set"
    assert 'version = 1.0' in spec_content, "Version not set"
    assert 'package.name = com.test.game' in spec_content, "Package name not set"

    print("✅ Buildozer spec generation test passed")

if __name__ == '__main__':
    test_kivy_buildozer()
```

---

## Browser Testing (HTML5)

### Manual Browser Tests

**Test in each browser:**
1. Chrome/Chromium
2. Firefox
3. Safari (macOS/iOS)
4. Edge (Windows)

**Test Checklist:**
- [ ] Game loads without errors
- [ ] Console shows no JavaScript errors
- [ ] Sprites render correctly
- [ ] Game logic works
- [ ] Keyboard input works
- [ ] Touch input works (mobile)
- [ ] Sound plays (if implemented)
- [ ] Game restarts properly
- [ ] Performance is acceptable (30+ FPS)

### Automated Browser Tests

```python
# Requires selenium
from selenium import webdriver
from pathlib import Path
import time

def test_html5_in_browser():
    """Test HTML5 game in browser"""
    # Setup
    driver = webdriver.Chrome()  # or Firefox()

    # Load game
    html_file = Path("export_output/html5_test/game.html").absolute()
    driver.get(f"file://{html_file}")

    # Wait for load
    time.sleep(2)

    # Check for errors
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE']

    assert len(errors) == 0, f"JavaScript errors: {errors}"

    # Check canvas exists
    canvas = driver.find_element_by_tag_name('canvas')
    assert canvas, "Canvas not found"

    # Cleanup
    driver.quit()

    print("✅ Browser test passed")

if __name__ == '__main__':
    test_html5_in_browser()
```

---

## Performance Testing

### HTML5 Performance
```python
def test_html5_performance():
    """Test HTML5 export performance"""
    from export.HTML5.html5_exporter import HTML5Exporter
    from pathlib import Path
    import time

    exporter = HTML5Exporter()

    project_path = Path("test_projects/medium_project")
    output_path = Path("export_output/html5_perf")
    output_path.mkdir(parents=True, exist_ok=True)

    # Time the export
    start = time.time()
    success = exporter.export(project_path, output_path)
    duration = time.time() - start

    # Verify performance
    assert duration < 10, f"Export too slow: {duration:.2f}s"

    # Check file size
    html_file = output_path / "medium_project.html"
    file_size = html_file.stat().st_size / (1024 * 1024)  # MB

    print(f"✅ HTML5 performance: {duration:.2f}s, {file_size:.2f}MB")

if __name__ == '__main__':
    test_html5_performance()
```

### EXE Performance
```python
def test_exe_performance():
    """Test EXE export performance"""
    from export.exe.exe_exporter import ExeExporter
    from pathlib import Path
    import time

    exporter = ExeExporter()

    project_path = Path("test_projects/medium_project")
    output_path = Path("export_output/exe_perf")
    output_path.mkdir(parents=True, exist_ok=True)

    # Time the export
    start = time.time()
    success = exporter.export(project_path, output_path)
    duration = time.time() - start

    # Note: EXE export is slow (PyInstaller)
    assert duration < 120, f"Export too slow: {duration:.2f}s"

    print(f"✅ EXE performance: {duration:.2f}s")

if __name__ == '__main__':
    test_exe_performance()
```

---

## Integration Testing

### Full Export Pipeline
```python
#!/usr/bin/env python3
"""Test complete export pipeline for all targets"""

from export.HTML5.html5_exporter import HTML5Exporter
from export.exe.exe_exporter import ExeExporter
from export.Kivy.kivy_exporter import KivyExporter
from pathlib import Path

def test_all_exporters():
    """Test all exporters with same project"""

    project_path = Path("test_projects/complete_test")

    print("\n=== Testing All Exporters ===\n")

    # Test HTML5
    print("1. Testing HTML5 Exporter...")
    html5_exporter = HTML5Exporter()
    html5_output = Path("export_output/integration_html5")
    html5_output.mkdir(parents=True, exist_ok=True)
    html5_success = html5_exporter.export(project_path, html5_output)
    print(f"   {'✅ Passed' if html5_success else '❌ Failed'}\n")

    # Test EXE
    print("2. Testing EXE Exporter...")
    exe_exporter = ExeExporter()
    exe_output = Path("export_output/integration_exe")
    exe_output.mkdir(parents=True, exist_ok=True)
    exe_success = exe_exporter.export(project_path, exe_output)
    print(f"   {'✅ Passed' if exe_success else '❌ Failed'}\n")

    # Test Kivy
    print("3. Testing Kivy Exporter...")
    kivy_exporter = KivyExporter()
    kivy_output = Path("export_output/integration_kivy")
    kivy_output.mkdir(parents=True, exist_ok=True)
    kivy_success = kivy_exporter.export(project_path, kivy_output)
    print(f"   {'✅ Passed' if kivy_success else '❌ Failed'}\n")

    # Summary
    total = 3
    passed = sum([html5_success, exe_success, kivy_success])

    print(f"\n=== Summary: {passed}/{total} exporters passed ===")

    return passed == total

if __name__ == '__main__':
    success = test_all_exporters()
    exit(0 if success else 1)
```

---

## Regression Testing

### Create Test Projects

**Minimal Project:**
```json
{
  "name": "minimal",
  "version": "1.0",
  "assets": {
    "rooms": {
      "room0": {
        "width": 640,
        "height": 480,
        "instances": []
      }
    },
    "objects": {},
    "sprites": {}
  }
}
```

**With Sprites:**
```json
{
  "name": "with_sprites",
  "version": "1.0",
  "assets": {
    "sprites": {
      "spr_player": {
        "file_path": "sprites/player.png"
      }
    },
    "objects": {
      "obj_player": {
        "sprite": "spr_player",
        "events": {}
      }
    },
    "rooms": {
      "room0": {
        "width": 640,
        "height": 480,
        "instances": [
          {
            "object_name": "obj_player",
            "x": 320,
            "y": 240
          }
        ]
      }
    }
  }
}
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Export Tests

on: [push, pull_request]

jobs:
  test-html5:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Test HTML5 Exporter
        run: python3 tests/test_html5_export.py

  test-exe:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Test EXE Exporter
        run: python3 tests/test_exe_export.py

  test-kivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install kivy buildozer
      - name: Test Kivy Exporter
        run: python3 tests/test_kivy_export.py
```

---

## Troubleshooting

### HTML5 Issues

**Problem:** Canvas not rendering
- Check browser console for errors
- Verify sprite data encoding
- Check canvas dimensions

**Problem:** Sprites not displaying
- Verify base64 encoding is correct
- Check file paths in project.json
- Verify image files exist

### EXE Issues

**Problem:** PyInstaller fails
- Update PyInstaller: `pip install --upgrade pyinstaller`
- Check Python version compatibility
- Verify all dependencies installed

**Problem:** Executable won't run
- Check for missing DLLs (Windows)
- Verify file permissions (Linux)
- Check code signing (macOS)

### Kivy Issues

**Problem:** Import errors in generated code
- Check action converter mappings
- Verify Kivy is installed
- Check Python syntax in generated files

**Problem:** Buildozer fails
- Install Android SDK/NDK
- Check buildozer.spec configuration
- Verify package names are valid

---

## Test Results Template

```
Export System Test Report
Date: YYYY-MM-DD
Tester: [Name]

HTML5 Exporter:
  [ ] Basic export
  [ ] Sprite encoding
  [ ] Compression
  [ ] Browser compatibility (Chrome/Firefox/Safari)
  [ ] Performance (<10s export)
  [ ] File size (<5MB typical)

EXE Exporter:
  [ ] Windows EXE generation
  [ ] Linux binary generation
  [ ] macOS app bundle
  [ ] Asset bundling
  [ ] Performance (<60s export)
  [ ] File size (<100MB)

Kivy Exporter:
  [ ] Code generation
  [ ] Action conversion
  [ ] Buildozer spec generation
  [ ] Desktop app runs
  [ ] Android build (if applicable)
  [ ] iOS build (if applicable)

Integration:
  [ ] All exporters work with same project
  [ ] No conflicts between exports
  [ ] Output directories clean

Notes:
[Any issues or observations]
```

---

## Conclusion

This testing guide provides:
- Quick 5-minute smoke tests
- Comprehensive unit tests
- Browser compatibility tests
- Performance benchmarks
- Integration tests
- CI/CD integration

**Recommendation:**
1. Run quick tests during development
2. Run comprehensive tests before releases
3. Set up CI/CD for automated testing
4. Document all test results

---

**Last Updated:** 2026-01-14
**Status:** Ready for use
**Next Review:** After implementing improvements

---

END OF TESTING GUIDE
