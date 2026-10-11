# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PyGameMaker IDE - LITE BUILD (CI/GitHub Actions)

This is the LITE build configuration used by GitHub Actions.
Kivy is EXCLUDED because CI runners don't have GPUs (OpenGL detection fails).

For a FULL build with Kivy (enables EXE export), use PyGameMaker-full.spec
on a local machine with a GPU (Windows or macOS with VS Code).

See docs/BUILDING.md for complete documentation.

To build:
    pyinstaller PyGameMaker.spec
"""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules


def _exclude_shadowing_runtime_libs(binaries):
    """Drop PyInstaller-bundled copies of libstdc++/libgcc_s and the glib
    family from the Linux build so the system's own copies are used instead.

    Real classroom crash, 2026-10-10: a user's compiled Linux build died the
    instant they opened the Blockly tab. Terminal output showed the actual
    chain: PyInstaller's bundled (older) libstdc++.so.6 sits in the onefile's
    extraction dir, which is searched before the system's real libstdc++ --
    so when Mesa's Intel GPU driver stack tried to dlopen libigdgmm.so.12 (its
    buffer-manager lib), it resolved against the bundled, too-old libstdc++
    and failed ("version GLIBCXX_3.4.32 not found"). With Mesa's driver unable
    to load, EGL/OpenGL context creation failed outright ("EGL not available",
    "Failed to create RHI for backend: OpenGL"), and the Blockly tab -- the
    one thing in this app that embeds a QWebEngineView, which needs an
    RHI-backed window to composite into -- took the whole window's render
    surface down with it (window vanishes; process lingers as a dead icon).
    Fixed for libstdc++/libgcc_s (v1.5.1).

    The SAME log line also showed unrelated system GIO modules failing:

        libdconfsettings.so: undefined symbol: g_assertion_message_cmpint
        libgvfscommon.so: undefined symbol: g_task_set_static_name

    This is the identical shadowing bug, one layer down the dependency
    graph: PyInstaller also bundles its own libglib-2.0/libgio-2.0/
    libgobject-2.0/libgmodule-2.0 (pulled in transitively by a Qt plugin,
    e.g. the networkinformation backend's libqglib.so), and those system
    GIO modules -- which the system's own GLib discovers and dlopen()s by
    scanning its modules directory at runtime, so they're never bundled by
    us at all -- resolve against the bundled, shadowing copy instead of the
    real system one they were actually compiled against. Confirmed still
    present in a v1.5.2 build (which only fixed libstdc++), so this was
    never actually fixed, just a second instance of the same mechanism
    hiding behind the first one's fix. Same safety argument as libstdc++:
    GLib keeps strict runtime back-compat, and a symbol a loader expects but
    the bundled copy lacks is itself the evidence the system copy is the
    newer, correct one to prefer.

    These GIO modules are desktop-integration conveniences (GSettings/dconf
    backend, GVFS trash/remote-mount support in file dialogs), not core app
    functionality -- losing them is a confirmed real (if mostly cosmetic)
    bug, not a theoretical one, so excluding the shadowing copy outright is
    worth it even though the failure mode itself is fairly benign.
    """
    excluded_prefixes = (
        'libstdc++.so', 'libgcc_s.so',
        'libglib-2.0.so', 'libgio-2.0.so', 'libgobject-2.0.so', 'libgmodule-2.0.so',
    )
    return [
        b for b in binaries
        if not os.path.basename(b[0]).startswith(excluded_prefixes)
    ]

# Project paths
project_dir = Path(SPECPATH)
main_script = project_dir / 'main.py'

# Application metadata
APP_NAME = 'PyGameMaker'
VERSION = '1.5.5'

# Collect all PySide6 data files (critical for Qt)
pyside6_datas = collect_data_files('PySide6')

# Collect PySide6 submodules for QtWebEngine
pyside6_hiddenimports = collect_submodules('PySide6')

# Data files to include
datas = [
    # Translation files (.qm)
    (str(project_dir / 'translations' / '*.qm'), 'translations'),
    # Theme configuration
    (str(project_dir / 'utils' / 'themes.json'), 'utils'),
    # App icon: the IDE window icon (main.py) and the HTML5 export's
    # fallback PWA icon (export/HTML5/html5_exporter.py).
    (str(project_dir / 'resources' / 'icon.*'), 'resources'),
]

# Add PySide6 data files
datas.extend(pyside6_datas)

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

    # Hardened XML parsing (Open Roberta importer)
    'defusedxml',
    'defusedxml.ElementTree',

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
        # Exclude Kivy - causes OpenGL detection issues on CI runners
        # and adds significant bloat. Kivy exports can be done separately.
        'kivy',
        'kivy_deps',
        'kivy_deps.angle',
        'kivy_deps.glew',
        'kivy_deps.sdl2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

a.binaries = _exclude_shadowing_runtime_libs(a.binaries)

# Add directory trees to datas (Tree works in all PyInstaller versions,
# unlike raw directory paths in datas which require PyInstaller 6.0+).
# Guard each with exists() so CI builds don't fail when directories are gitignored.
for _dir, _prefix in [
    ('Tutorials', 'Tutorials'),
    ('resources/flags', 'resources/flags'),
    ('resources/Sprites', 'resources/Sprites'),
    ('templates', 'templates'),
    ('editors/object_editor/blockly', 'editors/object_editor/blockly'),
    # Bundled sample projects (read-only at runtime — users must Save As
    # to a writable location before editing).
    ('samples', 'samples'),
    # Folder extensions (raycast 2.5D, block world, LAN multiplayer) and
    # single-file plugins (audio actions) are discovered and loaded OFF
    # DISK at runtime by events/plugin_loader.get_app_root() — which points
    # at sys._MEIPASS in a frozen build. Without these two trees the
    # packaged app loads zero extensions/plugins and every action they
    # contribute (network host/join, play_sound, the 2.5D renderer, ...)
    # silently does nothing.
    ('extensions', 'extensions'),
    ('plugins', 'plugins'),
    # HTML5 export: HTML5Exporter() reads engine.js / game_template.html and
    # the vendored pako.min.js the moment it is constructed. Without these
    # the packaged IDE's "Export as HTML5..." died on a FileNotFoundError
    # with no dialog at all (classroom report, 2026-10-07).
    ('export/HTML5/templates', 'export/HTML5/templates'),
    ('resources/vendor', 'resources/vendor'),
]:
    _path = project_dir / _dir
    if _path.is_dir():
        # Don't ship stale bytecode / caches alongside the real sources.
        a.datas += Tree(str(_path), prefix=_prefix,
                        excludes=['__pycache__', '*.pyc', '*.pyo'])

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
    upx=False,  # Disabled - UPX on large Qt apps is extremely slow
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_file,
    icon=str(project_dir / 'resources' / 'icon.ico') if sys.platform == 'win32' else None,
)

# macOS: wrap the onefile executable in a proper .app bundle so it gets a
# Dock/Finder icon and a display name. EXE()'s own icon= param only affects
# Windows .exe file icons; macOS icons require a BUNDLE with an .icns.
if sys.platform == 'darwin':
    icns_path = project_dir / 'resources' / 'icon.icns'
    app = BUNDLE(
        exe,
        name=f'{APP_NAME}.app',
        icon=str(icns_path) if icns_path.exists() else None,
        bundle_identifier='com.pygamemaker.ide',
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleVersion': VERSION,
            'CFBundleShortVersionString': VERSION,
            'NSHighResolutionCapable': True,
        },
    )
