# Export System Architecture

**Last Updated:** November 21, 2025
**Status:** ✅ Clean (duplicates removed)

---

## Overview

The PyGameMaker export system converts IDE projects into deployable formats for different platforms. The system supports three export targets:

1. **Kivy** - Mobile deployment (Android/iOS)
2. **HTML5** - Web deployment
3. **EXE** - Standalone executable (Windows/Linux/Mac)

---

## Directory Structure

```
export/
├── __init__.py                    # Export module initialization
├── EXPORT_ARCHITECTURE.md         # This file
│
├── Kivy/                          # Mobile export (Kivy/Buildozer)
│   ├── __init__.py
│   ├── kivy_exporter.py          # Main Kivy exporter class
│   ├── action_converter.py       # Converts GM actions to Kivy code
│   ├── code_generator.py         # Generates Python/Kivy code
│   ├── asset_bundler.py          # Bundles assets for mobile
│   ├── buildspec_generator.py    # Generates buildozer.spec
│   └── project_adapter.py        # Adapts project structure
│
├── HTML5/                         # Web export (HTML5/JavaScript)
│   ├── __init__.py
│   └── html5_exporter.py         # Main HTML5 exporter class
│
└── exe/                           # Executable export (PyInstaller)
    ├── __init__.py
    └── exe_exporter.py            # Main EXE exporter class
```

---

## Export Targets

### 1. Kivy Exporter (`export.Kivy.kivy_exporter.KivyExporter`)

**Purpose:** Export PyGameMaker projects to Kivy for mobile deployment

**Target Platforms:**
- Android (via Buildozer)
- iOS (via Buildozer)
- Desktop (Kivy app)

**Key Features:**
- Converts GameMaker events/actions to Kivy Python code
- Handles sprite/sound asset bundling
- Generates buildozer.spec for mobile compilation
- Supports touch input and mobile-specific features

**Output Structure:**
```
exported_project/
├── main.py                 # Kivy application entry point
├── game_engine.py          # Converted game logic
├── assets/                 # Bundled game assets
│   ├── sprites/
│   ├── sounds/
│   └── backgrounds/
├── buildozer.spec          # Buildozer configuration
└── requirements.txt        # Python dependencies
```

**Usage:**
```python
from export.Kivy.kivy_exporter import KivyExporter

exporter = KivyExporter()
exporter.export(project_path, output_dir)
```

**Key Components:**

1. **`action_converter.py`**
   - Converts GM8.0 actions to Kivy/Python code
   - Handles movement, collision, sound, etc.

2. **`code_generator.py`**
   - Generates properly indented Python code
   - Manages code blocks (if/else/loops)

3. **`asset_bundler.py`**
   - Copies and optimizes assets for mobile
   - Handles sprite atlases, sound compression

4. **`buildspec_generator.py`**
   - Generates buildozer.spec configuration
   - Sets app name, version, permissions

5. **`project_adapter.py`**
   - Adapts PyGameMaker project structure to Kivy format
   - Handles project metadata conversion

---

### 2. HTML5 Exporter (`export.HTML5.html5_exporter.HTML5Exporter`)

**Purpose:** Export PyGameMaker projects to HTML5/JavaScript for web deployment

**Target Platforms:**
- Web browsers (Chrome, Firefox, Safari, Edge)
- Progressive Web Apps (PWA)

**Key Features:**
- Converts Python game logic to JavaScript
- Uses HTML5 Canvas for rendering
- Web Audio API for sound
- Touch and keyboard input support

**Output Structure:**
```
exported_project/
├── index.html              # Main HTML page
├── game.js                 # Converted game logic (JavaScript)
├── engine.js               # HTML5 game engine
├── assets/                 # Game assets
│   ├── sprites/
│   ├── sounds/
│   └── backgrounds/
└── style.css               # Optional styling
```

**Usage:**
```python
from export.HTML5.html5_exporter import HTML5Exporter

exporter = HTML5Exporter()
exporter.export(project_path, output_dir)
```

---

### 3. EXE Exporter (`export.exe.exe_exporter.ExeExporter`)

**Purpose:** Export PyGameMaker projects to standalone executables

**Target Platforms:**
- Windows (.exe)
- Linux (AppImage/binary)
- macOS (.app bundle)

**Key Features:**
- Uses PyInstaller to bundle Python + Pygame
- Creates single-file or directory executables
- Includes all dependencies (Python runtime, libraries)
- Optional icon and version info

**Output:**
```
exported_project/
├── game.exe                # Windows executable
├── game                    # Linux executable
├── Game.app/               # macOS app bundle
└── _internal/              # PyInstaller bundled files (if not --onefile)
```

**Usage:**
```python
from export.exe.exe_exporter import ExeExporter

exporter = ExeExporter()
exporter.export(project_path, output_dir, platform='windows')
```

**Dependencies:**
- PyInstaller
- Pygame
- Project dependencies

---

## Common Export Workflow

All exporters follow this general pattern:

```
1. Load Project
   ├─ Read project.json
   ├─ Validate project structure
   └─ Parse assets

2. Convert Game Logic
   ├─ Parse events/actions
   ├─ Convert to target language (Python/JS)
   └─ Generate engine code

3. Bundle Assets
   ├─ Copy sprites, sounds, backgrounds
   ├─ Optimize for target platform
   └─ Generate asset manifest

4. Generate Configuration
   ├─ Create platform-specific config
   ├─ Set metadata (name, version)
   └─ Configure build settings

5. Build/Package
   ├─ Run platform build tools (optional)
   ├─ Create distributable package
   └─ Verify output
```

---

## Exporter Base API

All exporters should implement this interface:

```python
class BaseExporter(QObject):
    """Base class for all exporters"""

    # Signals
    export_started = Signal()
    export_progress = Signal(int, str)  # progress%, status_message
    export_completed = Signal(str)      # output_path
    export_failed = Signal(str)         # error_message

    def export(self, project_path: Path, output_dir: Path, **options) -> bool:
        """
        Export project to target format

        Args:
            project_path: Path to .pygm project
            output_dir: Where to export
            **options: Platform-specific options

        Returns:
            True if successful, False otherwise
        """
        pass

    def validate_project(self, project_data: dict) -> bool:
        """Validate project is exportable"""
        pass

    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        pass
```

---

## Cleanup History

### November 21, 2025 - Export Module Cleanup

**Removed Files:**
- `kivy_exporter.bak.py` (39K, Nov 13)
- `kivy_exporter.bak2.py` (42K, Nov 13)
- `kivy_exporter.bak3.py` (42K, Nov 13)
- `kivy_exporter.bak4.py` (42K, Nov 13)
- `kivy_exporter.rollback.py` (43K, Nov 13)
- `kivy_exporter-new actions-does-not-work.py` (42K, Nov 13)
- `kivy_exporter (Copie en conflit de SEMLOG-GTH-0001 2025-11-17).py` (44K, Nov 13)
- `action_converter.bak2.py` (12K, Nov 13)
- `action_converter.bak4.py` (13K, Nov 13)

**Backup Location:**
`.cleanup_backup/export_cleanup_20251121_110429/`

**Canonical Versions:**
- `kivy_exporter.py` (65K, Nov 17 22:07) ✅
- `action_converter.py` (16K, Nov 13 17:18) ✅

**Reason for Cleanup:**
Removed duplicate backup files created manually instead of using git version control. All backup files were older versions with bugs or incomplete features.

---

## Future Improvements

### High Priority
- [ ] Create automated tests for each exporter
- [ ] Add export validation (test exported builds)
- [ ] Implement progress reporting UI
- [ ] Add export presets (Debug/Release configs)

### Medium Priority
- [ ] Add export to Steam (via Steamworks SDK)
- [ ] Add export to itch.io (via Butler)
- [ ] Optimize asset bundling (compression, atlases)
- [ ] Add code obfuscation options

### Low Priority
- [ ] Add custom export plugins API
- [ ] Support for console platforms (Switch, Xbox, PS5)
- [ ] Add cloud build service integration

---

## Troubleshooting

### Kivy Exporter Issues

**Problem:** Buildozer fails with "Command not found"
**Solution:** Install Buildozer: `pip install buildozer`

**Problem:** Android permissions not working
**Solution:** Check `buildspec_generator.py` - update Android permissions list

**Problem:** Converted code has syntax errors
**Solution:** Check `action_converter.py` - likely missing action handler

### HTML5 Exporter Issues

**Problem:** JavaScript syntax errors
**Solution:** Verify Python-to-JS conversion in `html5_exporter.py`

**Problem:** Assets not loading
**Solution:** Check paths are relative in generated `game.js`

### EXE Exporter Issues

**Problem:** PyInstaller fails to bundle
**Solution:** Check PyInstaller version: `pip install --upgrade pyinstaller`

**Problem:** Executable is huge (>100MB)
**Solution:** Use `--onefile` and `--strip` options

**Problem:** Antivirus flags executable
**Solution:** Sign the executable with code signing certificate

---

## Development Guidelines

### Adding a New Action to Kivy Exporter

1. Open `export/Kivy/action_converter.py`
2. Add action handler method:
   ```python
   def convert_my_action(self, action_data: dict) -> str:
       """Convert my_action to Kivy code"""
       param = action_data.get('parameters', {}).get('param')
       return f"self.my_action({param})"
   ```
3. Update action mapping if needed
4. Test with sample project

### Creating a New Exporter

1. Create directory: `export/NewTarget/`
2. Create `__init__.py` and `new_target_exporter.py`
3. Implement `BaseExporter` interface
4. Add to `export/__init__.py`:
   ```python
   from .NewTarget.new_target_exporter import NewTargetExporter
   ```
5. Add tests in `tests/export/test_new_target.py`
6. Document in this file

---

## Version Control Best Practices

**❌ DON'T:**
- Create `.bak`, `.bak2`, `.old` files manually
- Use "conflicted copy" files
- Keep broken/non-working versions in the repo

**✅ DO:**
- Use git branches for experimental features: `git checkout -b feature/new-exporter`
- Use git tags for stable versions: `git tag v1.0.0`
- Use git stash for temporary changes: `git stash save "WIP: exporter refactor"`
- Commit working versions: `git commit -m "Add Kivy action converter"`

**Example Workflow:**
```bash
# Start new feature
git checkout -b feature/improve-kivy-exporter

# Make changes, test, commit
git add export/Kivy/kivy_exporter.py
git commit -m "Improve Kivy action conversion"

# If you need to try something risky
git stash save "Current progress"
# ... experiment ...
git stash pop  # Restore if experiment failed

# Merge when done
git checkout main
git merge feature/improve-kivy-exporter
```

---

## Contact & Support

For export-related issues:
- Check troubleshooting section above
- Review exporter source code
- Check project issues: https://github.com/your-repo/pygm2/issues

For new export targets:
- Propose on GitHub Discussions
- Follow "Creating a New Exporter" guidelines
- Submit PR with tests and documentation

---

**END OF DOCUMENTATION**
