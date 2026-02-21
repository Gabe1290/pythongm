# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PyGameMaker IDE - FULL BUILD with Kivy

This is the FULL build configuration for LOCAL builds only.
Includes Kivy for complete EXE export functionality.

REQUIREMENTS:
  - Must be built on a machine with a GPU (OpenGL 2.0+ support)
  - Windows or macOS with VS Code or terminal access
  - Cannot be built on GitHub Actions (no GPU available)

For CI/GitHub Actions builds, use PyGameMaker.spec (lite version).

See docs/BUILDING.md for complete documentation.

To build:
    pyinstaller PyGameMaker-full.spec

Note: Build time will be longer and executable will be larger (~300-500MB)
due to Kivy and its dependencies being bundled.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Project paths
project_dir = Path(SPECPATH)
main_script = project_dir / 'main.py'

# Application metadata
APP_NAME = 'PyGameMaker'
VERSION = '0.11.0-alpha'

# Collect all PySide6 data files (critical for Qt)
pyside6_datas = collect_data_files('PySide6')

# Collect PySide6 submodules for QtWebEngine
pyside6_hiddenimports = collect_submodules('PySide6')

# Collect Kivy data files and submodules (for EXE export functionality)
kivy_datas = collect_data_files('kivy')
kivy_hiddenimports = collect_submodules('kivy')

# Data files to include
datas = [
    # Translation files (.qm)
    (str(project_dir / 'translations' / '*.qm'), 'translations'),
    # Theme configuration
    (str(project_dir / 'utils' / 'themes.json'), 'utils'),
    # Language flags
    (str(project_dir / 'resources' / 'flags'), 'resources/flags'),
    # Tutorials (HTML files, sample assets, index)
    (str(project_dir / 'Tutorials'), 'Tutorials'),
    # Sample sprites used by tutorials
    (str(project_dir / 'resources' / 'Sprites'), 'resources/Sprites'),
]

# Add PySide6 data files
datas.extend(pyside6_datas)

# Add Kivy data files
datas.extend(kivy_datas)

# Hidden imports that PyInstaller may not detect
hiddenimports = [
    # PySide6 core
    'shiboken6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',

    # QtWebEngine for Blockly visual programming
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebChannel',
    'PySide6.QtNetwork',
    'PySide6.QtPrintSupport',

    # Game runtime
    'pygame',
    'pygame.mixer',
    'pygame.font',
    'pygame.image',
    'pygame.draw',
    'pygame.event',
    'pygame.display',
    'pygame.time',
    'pygame.transform',
    'pygame.sprite',

    # Image processing
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageTk',

    # File watching
    'watchdog',
    'watchdog.observers',
    'watchdog.events',

    # Template engine (for export)
    'jinja2',
    'jinja2.ext',

    # Kivy core (for EXE export)
    'kivy',
    'kivy.app',
    'kivy.uix',
    'kivy.core',
    'kivy.graphics',

    # Standard library modules that may be missed
    'json',
    'pathlib',
    'shutil',
    'hashlib',
    'tempfile',
    'uuid',
    'threading',
    'queue',
    'zipfile',
    'gzip',
    'base64',
    'html',
    'urllib',
    'urllib.request',
    'urllib.parse',
]

# Add all PySide6 submodules
hiddenimports.extend(pyside6_hiddenimports)

# Add all Kivy submodules
hiddenimports.extend(kivy_hiddenimports)

# Analysis configuration
a = Analysis(
    [str(main_script)],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'IPython',
        'notebook',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Create the PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Version info file path (Windows only)
version_file = str(project_dir / 'version_info.txt') if sys.platform == 'win32' else None

# Create the single-file executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX for local builds - slower but smaller exe
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_file,
)
