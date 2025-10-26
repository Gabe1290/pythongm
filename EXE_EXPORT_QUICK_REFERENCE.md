# EXE Exporter - Quick Reference Guide

## File Location
```
/home/gabe/Dropbox/pygm2/export/exe/exe_exporter.py
```

## Quick Start

### Basic Usage
```python
from export.exe.exe_exporter import ExeExporter

exporter = ExeExporter()

# Connect progress signals (optional)
exporter.progress_update.connect(lambda pct, msg: print(f"{pct}%: {msg}"))
exporter.export_complete.connect(lambda ok, msg: print(f"Done: {msg}"))

# Export
success = exporter.export_project(
    project_path='/path/to/game.pgm',
    output_path='/path/to/output',
    settings={
        'include_debug': False,  # Hide console
        'optimize': True,        # Enable UPX
        'icon_path': None,       # Optional .ico file
    }
)
```

## Settings Dictionary

```python
settings = {
    # Console Window
    'include_debug': False,     # True = show console, False = windowed only

    # Optimization
    'optimize': True,           # True = enable UPX compression

    # Icon (Optional)
    'icon_path': 'path/to/icon.ico',  # Windows .ico file
}
```

## Progress Signals

### progress_update (int, str)
```python
# Emitted during export
# Parameters: (percentage, status_message)

exporter.progress_update.connect(on_progress)

def on_progress(percent, message):
    print(f"[{percent}%] {message}")
```

### export_complete (bool, str)
```python
# Emitted when export finishes
# Parameters: (success, message)

exporter.export_complete.connect(on_complete)

def on_complete(success, message):
    if success:
        print(f"Success: {message}")
    else:
        print(f"Failed: {message}")
```

## Progress Stages

| Percent | Stage |
|---------|-------|
| 10% | Checking PyInstaller |
| 20% | Creating build directory |
| 30% | Generating Kivy game |
| 50% | Creating launcher script |
| 60% | Creating PyInstaller spec |
| 70% | Building executable |
| 90% | Copying to output |
| 95% | Cleanup |
| 100% | Complete |

## Requirements

### Python Packages
```bash
pip install pyinstaller>=5.0
pip install kivy>=2.1.0
pip install Pillow>=9.0
```

### Check Requirements
```python
# PyInstaller
import subprocess
result = subprocess.run(['pyinstaller', '--version'], capture_output=True)
print(f"PyInstaller: {result.stdout.decode()}")

# Kivy
import kivy
print(f"Kivy: {kivy.__version__}")

# Pillow
from PIL import Image
print(f"Pillow: {Image.__version__}")
```

## Output

### Directory Structure
```
output_path/
└── GameName.exe         # Standalone executable
```

### EXE Properties
- **Size**: 25-50 MB (includes Python + Kivy + game)
- **Dependencies**: None (standalone)
- **Platform**: Windows (x64)
- **Console**: Optional (set via include_debug)

## Error Handling

### Common Errors

#### "PyInstaller not found"
```bash
# Install PyInstaller
pip install pyinstaller
```

#### "Failed to generate Kivy game"
```python
# Check KivyExporter manually
from export.Kivy.kivy_exporter import KivyExporter
exporter = KivyExporter(project_data, project_dir, output_dir)
success = exporter.export()
```

#### "PyInstaller build failed"
```bash
# Run PyInstaller manually with verbose output
cd build_temp_exe
pyinstaller --clean --debug all game.spec
```

### Debug Mode
```python
# Enable debug mode to see console output
settings = {
    'include_debug': True,  # Shows console window
}

# Build directory will NOT be cleaned up
# Check: project_dir/build_temp_exe/
```

## Method Reference

### ExeExporter.export_project()
```python
def export_project(
    self,
    project_path: str,      # Path to .pgm file
    output_path: str,       # Output directory
    settings: Dict          # Settings dict
) -> bool:                  # Returns success
```

### Internal Methods
```python
# Check if PyInstaller is available
_check_pyinstaller() -> bool

# Create temporary build directory
_create_build_directory() -> Path

# Generate Kivy game using KivyExporter
_generate_kivy_game(build_dir: Path) -> bool

# Create launcher script
_create_launcher_script(build_dir: Path) -> Path

# Create PyInstaller spec file
_create_spec_file(build_dir: Path, launcher_script: Path) -> Path

# Run PyInstaller
_run_pyinstaller(spec_file: Path) -> bool

# Copy output to final location
_copy_to_output(build_dir: Path)

# Clean up temporary files
_cleanup(build_dir: Path)
```

## Integration Example (Qt UI)

```python
from PySide6.QtWidgets import QPushButton, QProgressBar, QLabel
from PySide6.QtCore import QThread
from export.exe.exe_exporter import ExeExporter

class ExportWorker(QThread):
    def __init__(self, project_path, output_path, settings):
        super().__init__()
        self.project_path = project_path
        self.output_path = output_path
        self.settings = settings
        self.exporter = ExeExporter()

        # Connect signals to update UI
        self.exporter.progress_update.connect(self.on_progress)
        self.exporter.export_complete.connect(self.on_complete)

    def run(self):
        self.exporter.export_project(
            self.project_path,
            self.output_path,
            self.settings
        )

    def on_progress(self, percent, message):
        # Update progress bar and label
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def on_complete(self, success, message):
        if success:
            self.show_success_dialog(message)
        else:
            self.show_error_dialog(message)

# Usage
worker = ExportWorker(project_path, output_path, settings)
worker.start()
```

## Command-Line Tool

```python
#!/usr/bin/env python3
"""
Command-line EXE exporter
"""
import sys
import json
from pathlib import Path
from export.exe.exe_exporter import ExeExporter

def main():
    if len(sys.argv) < 3:
        print("Usage: python export_exe.py <project.pgm> <output_dir>")
        sys.exit(1)

    project_path = sys.argv[1]
    output_path = sys.argv[2]

    exporter = ExeExporter()

    # Print progress
    exporter.progress_update.connect(
        lambda p, m: print(f"[{p:3d}%] {m}")
    )

    # Export
    success = exporter.export_project(
        project_path,
        output_path,
        {'include_debug': False, 'optimize': True}
    )

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

Save as `export_exe.py` and run:
```bash
python export_exe.py game.pgm output/
```

## Testing Checklist

- [ ] PyInstaller is installed
- [ ] Kivy is installed
- [ ] Project file (.pgm) exists
- [ ] Output directory is writable
- [ ] At least 100MB free disk space
- [ ] Test with small project first
- [ ] Enable debug mode for troubleshooting
- [ ] Test exported EXE on clean Windows machine

## Performance Tips

### Build Speed
- Use SSD for build directory
- Disable antivirus during build
- Close other applications
- Use optimize=True for smaller files

### EXE Size
- Remove unused assets from project
- Compress images before import
- Use .ogg instead of .wav for sounds
- Consider multi-file mode (future feature)

## Troubleshooting

### Build Takes Forever
```python
# Check PyInstaller version
pyinstaller --version

# Update if needed
pip install --upgrade pyinstaller
```

### EXE Won't Run
```python
# Enable debug mode to see errors
settings = {'include_debug': True}

# Check dependencies
# Run from command line to see error messages
```

### Missing Assets
```python
# Verify assets are in project directory
# Check project.pgm file paths
# Ensure assets were exported by KivyExporter
```

### Antivirus Blocking
```python
# Code sign the EXE (requires certificate)
# Add exception to antivirus
# Upload to VirusTotal to check for false positives
```

## See Also

- **Full Documentation**: `/home/gabe/Dropbox/pygm2/EXE_EXPORTER_KIVY_REWRITE.md`
- **Architecture Guide**: `/home/gabe/Dropbox/pygm2/EXE_EXPORT_ARCHITECTURE.md`
- **KivyExporter**: `/home/gabe/Dropbox/pygm2/export/Kivy/kivy_exporter.py`
- **PyInstaller Docs**: https://pyinstaller.org/

## Support

For issues or questions:
1. Check debug output (enable include_debug)
2. Verify all requirements are installed
3. Test with minimal project
4. Check PyInstaller logs in build directory
