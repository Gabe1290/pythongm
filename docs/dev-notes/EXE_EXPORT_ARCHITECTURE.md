# EXE Exporter Architecture - Visual Guide

## High-Level Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    PyGameMaker IDE                          │
│                                                             │
│  User clicks: "Export > Windows EXE"                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ExeExporter.export_project()                   │
│                                                             │
│  1. Load project.pgm file                                   │
│  2. Create temporary build directory                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 1: Generate Kivy Game                         │
│          _generate_kivy_game()                              │
│                                                             │
│  ┌───────────────────────────────────────────┐              │
│  │  KivyExporter (from export/Kivy/)         │              │
│  │                                           │              │
│  │  Reads: project.pgm                       │              │
│  │                                           │              │
│  │  Generates:                               │              │
│  │  • game/main.py (Kivy app)                │              │
│  │  • game/objects/base_object.py            │              │
│  │  • game/objects/obj_player.py (etc.)      │              │
│  │  • game/scenes/room0.py (etc.)            │              │
│  │  • game/assets/images/* (sprites)         │              │
│  │  • game/assets/sounds/* (audio)           │              │
│  │  • game/utils.py                          │              │
│  └───────────────────────────────────────────┘              │
│                                                             │
│  Output: Complete Kivy game in build_dir/game/             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 2: Create Launcher Script                     │
│          _create_launcher_script()                          │
│                                                             │
│  Creates: game_launcher.py                                  │
│                                                             │
│  ┌───────────────────────────────────────────┐              │
│  │  Launcher Script Contents:                │              │
│  │                                           │              │
│  │  • Detect PyInstaller frozen mode         │              │
│  │  • Set base_path = sys._MEIPASS           │              │
│  │  • Change directory to game/              │              │
│  │  • Import and run GameApp                 │              │
│  └───────────────────────────────────────────┘              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 3: Create PyInstaller Spec                    │
│          _create_spec_file()                                │
│                                                             │
│  Creates: game.spec                                         │
│                                                             │
│  ┌───────────────────────────────────────────┐              │
│  │  Spec File Configuration:                 │              │
│  │                                           │              │
│  │  Entry Point: game_launcher.py            │              │
│  │                                           │              │
│  │  Data Files:                              │              │
│  │  • ('game', 'game') - entire directory    │              │
│  │                                           │              │
│  │  Hidden Imports:                          │              │
│  │  • kivy, kivy.app, kivy.core.*            │              │
│  │  • kivy.uix.*, kivy.graphics              │              │
│  │  • PIL (Pillow)                           │              │
│  │                                           │              │
│  │  Excludes:                                │              │
│  │  • PySide6, PyQt5/6, tkinter              │              │
│  │  • matplotlib, numpy                      │              │
│  │                                           │              │
│  │  Output: Single EXE (onefile mode)        │              │
│  └───────────────────────────────────────────┘              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 4: Run PyInstaller                            │
│          _run_pyinstaller()                                 │
│                                                             │
│  Command: pyinstaller --clean game.spec                     │
│                                                             │
│  PyInstaller Process:                                       │
│  1. Analyzes dependencies                                   │
│  2. Collects Python files                                   │
│  3. Bundles Kivy libraries                                  │
│  4. Packs game/ directory                                   │
│  5. Compresses with UPX                                     │
│  6. Creates bootloader                                      │
│  7. Generates GameName.exe                                  │
│                                                             │
│  Output: dist/GameName.exe                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 5: Copy to Output Directory                   │
│          _copy_to_output()                                  │
│                                                             │
│  Copies: dist/GameName.exe → output_path/GameName.exe      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               EXE Ready for Distribution!                   │
│                                                             │
│  User can now run: GameName.exe                             │
│  • Standalone (no Python installation needed)              │
│  • Includes full Kivy runtime                               │
│  • 80% GameMaker 7.0 compatible                             │
└─────────────────────────────────────────────────────────────┘
```

## Runtime Execution Flow

```
User Double-Clicks GameName.exe
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  PyInstaller Bootloader Starts                              │
│                                                             │
│  1. Extracts bundled files to temp directory (sys._MEIPASS) │
│  2. Sets up Python environment                              │
│  3. Runs game_launcher.py                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  game_launcher.py Executes                                  │
│                                                             │
│  if getattr(sys, 'frozen', False):                          │
│      base_path = sys._MEIPASS  # Temp extraction dir        │
│                                                             │
│  os.chdir(os.path.join(base_path, 'game'))                  │
│  sys.path.insert(0, game_dir)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Imports: from main import GameApp                          │
│                                                             │
│  Loads game/main.py (generated by KivyExporter)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  GameApp().run()                                            │
│                                                             │
│  ┌─────────────────────────────────────────┐                │
│  │  Kivy App Initialization                │                │
│  │                                         │                │
│  │  1. Create window                       │                │
│  │  2. Load first room/scene               │                │
│  │  3. Create instances                    │                │
│  │  4. Start game loop (60 FPS)            │                │
│  └─────────────────────────────────────────┘                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Game Loop (60 FPS)                                         │
│                                                             │
│  Each Frame:                                                │
│  1. Begin Step events                                       │
│  2. Alarm events                                            │
│  3. Keyboard/Mouse events                                   │
│  4. Normal Step events                                      │
│  5. Movement processing                                     │
│  6. Collision detection                                     │
│  7. End Step events                                         │
│  8. Draw/Render                                             │
│                                                             │
│  (GameMaker 7.0 Event Order)                                │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure Comparison

### Build Directory (Temporary)
```
build_temp_exe/
├── game_launcher.py           ← Created by _create_launcher_script()
├── game.spec                  ← Created by _create_spec_file()
│
├── game/                      ← Generated by KivyExporter
│   ├── main.py
│   ├── utils.py
│   ├── objects/
│   │   ├── base_object.py
│   │   ├── obj_player.py
│   │   └── obj_wall.py
│   ├── scenes/
│   │   ├── room0.py
│   │   └── room1.py
│   └── assets/
│       ├── images/
│       │   ├── spr_player.png
│       │   └── spr_wall.png
│       └── sounds/
│
├── build/                     ← PyInstaller intermediate files
│   └── game/
│       └── (analysis artifacts)
│
└── dist/                      ← PyInstaller output
    └── GameName.exe          ← Final executable
```

### Output Directory (Final)
```
output/
└── GameName.exe              ← Standalone executable (20-50MB)
                                 Contains everything needed to run
```

### EXE Internal Structure (When Running)
```
sys._MEIPASS/ (Temporary extraction directory)
├── game_launcher.pyc
├── python311.dll
├── kivy/ (all Kivy libs)
└── game/
    ├── main.pyc
    ├── utils.pyc
    ├── objects/
    ├── scenes/
    └── assets/
```

## Data Flow: Project → EXE

```
project.pgm (JSON)
      │
      ├── assets: { sprites, sounds, backgrounds }
      ├── objects: { obj_player, obj_wall, ... }
      └── rooms: { room0, room1, ... }
      │
      ▼
KivyExporter.export()
      │
      ├── Generates GameObject classes (Python)
      ├── Generates Scene classes (Python)
      ├── Copies assets to game/assets/
      └── Creates main.py (Kivy app)
      │
      ▼
game/ directory
      │
      ├── main.py (imports scenes.room0)
      ├── scenes/room0.py (imports objects.obj_player)
      ├── objects/obj_player.py (extends GameObject)
      └── assets/images/spr_player.png
      │
      ▼
game_launcher.py
      │
      └── Wrapper that runs main.GameApp()
      │
      ▼
PyInstaller
      │
      ├── Analyzes imports
      ├── Bundles Python + Kivy
      ├── Packs game/ directory
      └── Creates bootloader
      │
      ▼
GameName.exe
      │
      └── Self-contained executable
```

## Key Design Decisions

### 1. Why Use KivyExporter?
```
PRO:
✅ Already implements 80% of GameMaker 7.0
✅ Battle-tested event system
✅ Optimized collision detection
✅ Complete object/room generation
✅ Single source of truth

CON:
❌ Larger file size (Kivy vs pygame)
   → Acceptable tradeoff for completeness
```

### 2. Why PyInstaller?
```
PRO:
✅ Industry standard
✅ Cross-platform (Windows, Linux, Mac)
✅ Single-file EXE mode
✅ Good Kivy support
✅ Active maintenance

ALT: cx_Freeze, Nuitka, py2exe
   → PyInstaller has best Kivy compatibility
```

### 3. Why game_launcher.py?
```
Purpose:
• Handle PyInstaller frozen/unfrozen paths
• Set up working directory
• Import from correct location

Alternative: Direct main.py entry
   → Wouldn't handle sys._MEIPASS correctly
   → Would break asset loading
```

### 4. Why Bundle Everything?
```
Structure:
EXE contains: Python + Kivy + Game Code + Assets

Alternative: Multi-file distribution
   → More complex for users
   → Easier to break
   → No benefit for most games

Trade-off:
Larger EXE (20-50MB) vs Simpler distribution
   → Chose simplicity
```

## Performance Characteristics

### Build Time
```
Small game (10 objects, 5 rooms):   ~30-60 seconds
Medium game (50 objects, 20 rooms): ~60-120 seconds
Large game (100+ objects):          ~120-300 seconds

Breakdown:
• KivyExporter: 10-20%
• PyInstaller analysis: 30-40%
• PyInstaller bundling: 40-50%
• Compression (UPX): 10-20%
```

### EXE Size
```
Base (empty game):           ~20 MB (Kivy + Python)
Per sprite (PNG):            ~10-100 KB
Per sound (WAV/OGG):         ~50-500 KB
Per object class:            ~5-20 KB (code)

Typical game: 25-50 MB
```

### Runtime Performance
```
Startup (first run):  1-2 seconds (extraction)
Startup (subsequent): 0.5-1 second (cached)
Game FPS:             60 FPS (Kivy optimized)
Memory:               50-200 MB (depends on assets)
```

## Comparison: Old vs New

```
┌──────────────────┬─────────────────┬──────────────────┐
│ Feature          │ Old (Pygame)    │ New (Kivy)       │
├──────────────────┼─────────────────┼──────────────────┤
│ Runtime          │ pygame          │ Kivy             │
│ GM Compatibility │ ~20%            │ ~80%             │
│ Event System     │ Basic           │ Complete         │
│ Collision        │ Simple          │ Optimized O(n²/2)│
│ Movement         │ Basic           │ GM 7.0 accurate  │
│ Alarms           │ ❌              │ ✅ (12 per obj)  │
│ Grid System      │ ❌              │ ✅               │
│ Speed/Direction  │ ❌              │ ✅ Bidirectional │
│ Frame-indep      │ ❌              │ ✅ dt-based      │
│ Code Generation  │ Manual          │ KivyExporter     │
│ Maintenance      │ Separate code   │ Shared code      │
│ File Size        │ ~10 MB          │ ~25 MB           │
│ Startup Time     │ Fast (~0.5s)    │ Slower (~1-2s)   │
│ Cross-platform   │ Possible        │ Easy             │
└──────────────────┴─────────────────┴──────────────────┘
```

## Summary

The new EXE exporter architecture:

1. **Leverages KivyExporter** for complete GameMaker 7.0 compatibility
2. **Uses PyInstaller** for professional EXE bundling
3. **Provides standalone distribution** with no dependencies
4. **Maintains same API** for backwards compatibility
5. **Enables future cross-platform** support (Linux/Mac)

The result: A production-ready EXE exporter that delivers 80% GameMaker 7.0 compatibility in a standalone Windows executable.
