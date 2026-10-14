# Building PyGameMaker

This guide explains how to build standalone executables for PyGameMaker IDE.

## Build Options

There is one spec file, `PyGameMaker.spec` — the same one GitHub Actions
uses and the same one a local build should use. It excludes Kivy purely to
avoid OpenGL-detection failures and bloat on headless CI runners; a
`PyGameMaker-full.spec` with Kivy bundled in used to exist but was removed
(see git history) once it stopped doing anything useful — see the next
section for why.

### A packaged IDE build cannot export games to a native executable (EXE/Linux/macOS), lite or full

This is **not** a Kivy limitation and bundling Kivy back in would not fix
it. Since 2026-08-17, native desktop game export (`export/desktop/
pygame_desktop_exporter.py`) freezes the real `runtime/game_runner.py`
engine via PyInstaller, invoked as `sys.executable -m PyInstaller ...` —
and inside ANY PyInstaller-frozen build of the IDE, `sys.executable` IS
the frozen PyGameMaker binary itself, not a real Python interpreter, so
that command cannot run PyInstaller at all (the IDE now detects this and
refuses up front with an explanation, rather than hanging and failing
with a misleading error).

A packaged/portable PyGameMaker build (anything built from
`PyGameMaker.spec`, including every binary GitHub Actions publishes) can:
- Create and edit projects
- Run games in the IDE preview (Test Game)
- Export to HTML5 — this needs nothing installed and works from any build
- Export to Android/iOS, which still use the separate Kivy-based pipeline
  (`export/Kivy/`) and have their own dependency checks

To export a game to a native Windows/Linux/macOS executable, **run
PyGameMaker from its source checkout** instead of a packaged build (see
"Building Locally" below for the same virtual-environment setup, or just
`pip install -r requirements.txt && python main.py` without building
anything) — the IDE's own `sys.executable` is then a real Python, which
`-m PyInstaller` can run normally.

## Prerequisites

### All Platforms

1. Python 3.11 or later
2. Virtual environment (recommended)
3. PyInstaller

### Windows Additional Requirements

- Visual C++ Redistributable (usually pre-installed)
- UPX (optional, for compression) - download from https://upx.github.io/

### macOS Additional Requirements

- Xcode Command Line Tools (provides `lipo`, `codesign`, and other build utilities):
  ```bash
  xcode-select --install
  ```
  **Note:** This is required both for building PyGameMaker itself and for
  exporting games as macOS .app bundles. On managed Macs where you cannot
  run this command, ask your IT administrator to install the Command Line Tools.

### Linux Additional Requirements

```bash
sudo apt-get install -y \
    libegl1 \
    libxkbcommon0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-keysyms1 \
    libxcb-shape0 \
    libasound2-dev \
    libgl1-mesa-dev
```

## Building Locally

### Step 1: Set Up Environment

```bash
# Clone the repository
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

### Step 2: Build

```bash
pyinstaller PyGameMaker.spec
```

Output: `dist/PyGameMaker.exe` (Windows) or `dist/PyGameMaker` (macOS/Linux)

### Step 3: Test the Build

Run the executable from the `dist/` folder to verify it works correctly.
Remember that this packaged build — like every PyGameMaker binary GitHub
Actions publishes — cannot itself export a game to a native executable
(see "A packaged IDE build cannot export games..." above); that's expected,
not a bug to chase here.

## GitHub Actions (Automated Builds)

The repository includes a GitHub Actions workflow (`.github/workflows/build.yml`) that automatically builds for:
- Windows (x64)
- macOS Intel (x64)
- macOS Apple Silicon (ARM64)
- Linux (x64)

### Triggering a Build

1. **Manual trigger**: Go to Actions → Build → Run workflow
2. **On release**: Creating a GitHub release automatically triggers builds

### Build Artifacts

- **Manual builds**: Creates a draft release with all platform binaries
- **Release builds**: Attaches binaries to the release

### CI Build Limitations

GitHub Actions runners don't have GPUs, so Kivy is excluded (would fail
OpenGL detection) — this only affects the IDE's own Android/iOS export
support, not native desktop game export, which no packaged build can do
regardless (see "A packaged IDE build cannot export games..." above). All
other functionality works normally.

## Build Configuration Details

### PyGameMaker.spec

```python
excludes=[
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'IPython',
    'notebook',
    'jupyter',
    'kivy',           # Excluded for CI builds
    'kivy_deps',
    'kivy_deps.angle',
    'kivy_deps.glew',
    'kivy_deps.sdl2',
]
upx=False  # Disabled for faster CI builds
```

## Troubleshooting

### "OpenGL version (2.0) NOT found" on CI

This is expected on GitHub Actions runners. Use the lite build (`PyGameMaker.spec`) for CI.

### Build takes over an hour

Check if UPX is enabled. UPX compression on large Qt applications can be very slow. For faster builds during development, set `upx=False` in the spec file.

### Missing DLLs on Windows

Ensure Visual C++ Redistributable is installed. The PyInstaller output should bundle all necessary DLLs.

### "ModuleNotFoundError" at runtime

Add the missing module to `hiddenimports` in the spec file. PyInstaller sometimes misses dynamically imported modules.

### macOS app won't open ("damaged" or "unidentified developer")

The app isn't code-signed. Users need to:
1. Right-click → Open (first time only), or
2. System Preferences → Security & Privacy → Open Anyway

For distribution, consider code signing with an Apple Developer certificate.

### Linux executable won't run

1. Make it executable: `chmod +x PyGameMaker`
2. Install required system libraries (see Prerequisites)

## Build Size Reference

Approximate sizes (may vary by version):

| Platform | Size |
|----------|------|
| Windows | ~150-200 MB |
| macOS | ~180-220 MB |
| Linux | ~160-200 MB |

## Distributing Builds

### Windows

Distribute the `.exe` file directly. Consider:
- Code signing for Windows SmartScreen trust
- Creating an installer with NSIS or Inno Setup

### macOS

The build creates an app bundle. For distribution:
1. Zip the app: `zip -r PyGameMaker-macOS.zip PyGameMaker.app`
2. Consider notarization for Gatekeeper approval

### Linux

Create a tarball:
```bash
cd dist && tar -czvf PyGameMaker-Linux.tar.gz PyGameMaker
```

Consider creating:
- AppImage for universal Linux distribution
- .deb package for Debian/Ubuntu
- .rpm package for Fedora/RHEL

## Version Information (Windows)

The Windows build uses `version_info.txt` for executable metadata. Update this file before release builds to set:
- File version
- Product version
- Company name
- File description
- Copyright

## Related Files

- `PyGameMaker.spec` - Build configuration
- `.github/workflows/build.yml` - CI/CD workflow
- `requirements.txt` - Python dependencies
- `version_info.txt` - Windows version metadata
