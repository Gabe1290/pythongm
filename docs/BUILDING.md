# Building PyGameMaker

This guide explains how to build standalone executables for PyGameMaker IDE.

## Build Options

There are two build configurations available:

| Configuration | Spec File | Kivy Included | EXE Export | Use Case |
|---------------|-----------|---------------|------------|----------|
| **Lite** | `PyGameMaker.spec` | No | No | GitHub Actions, CI/CD, smaller download |
| **Full** | `PyGameMaker-full.spec` | Yes | Yes | Local builds for complete functionality |

### Lite Build (CI/GitHub Actions)

The lite build excludes Kivy to avoid OpenGL detection issues on headless CI runners. Users of this build can:
- Create and edit projects
- Run games in the IDE preview
- Export to HTML5
- Export to other formats that don't require Kivy

Users **cannot** export to Windows EXE unless they have Python + Kivy installed separately.

### Full Build (Local)

The full build includes Kivy, enabling complete EXE export functionality. This build must be done on a machine with:
- A GPU (or graphics drivers that support OpenGL 2.0+)
- Windows or macOS with VS Code or terminal access

## Prerequisites

### All Platforms

1. Python 3.11 or later
2. Virtual environment (recommended)
3. PyInstaller

### Windows Additional Requirements

- Visual C++ Redistributable (usually pre-installed)
- UPX (optional, for compression) - download from https://upx.github.io/

### macOS Additional Requirements

- Xcode Command Line Tools: `xcode-select --install`

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

### Step 2: Choose Your Build Type

#### Lite Build (faster, smaller, no Kivy)

```bash
pyinstaller PyGameMaker.spec
```

Output: `dist/PyGameMaker.exe` (Windows) or `dist/PyGameMaker` (macOS/Linux)

#### Full Build (slower, larger, includes Kivy)

```bash
pyinstaller PyGameMaker-full.spec
```

Output: Same locations, but with Kivy bundled (~300-500MB)

### Step 3: Test the Build

Run the executable from the `dist/` folder to verify it works correctly.

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

GitHub Actions runners don't have GPUs, so:
- Kivy is excluded (would fail OpenGL detection)
- The resulting executables cannot export to EXE format
- All other functionality works normally

## Build Configuration Details

### PyGameMaker.spec (Lite)

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

### PyGameMaker-full.spec (Full)

```python
# Kivy is NOT in excludes list
# Additional hidden imports for Kivy
hiddenimports.extend([
    'kivy',
    'kivy.app',
    'kivy.uix',
    'kivy.core',
    'kivy.graphics',
])
upx=True  # Enabled for smaller final size
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

| Platform | Lite Build | Full Build |
|----------|------------|------------|
| Windows | ~150-200 MB | ~350-450 MB |
| macOS | ~180-220 MB | ~400-500 MB |
| Linux | ~160-200 MB | ~380-480 MB |

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

- `PyGameMaker.spec` - Lite build configuration
- `PyGameMaker-full.spec` - Full build configuration
- `.github/workflows/build.yml` - CI/CD workflow
- `requirements.txt` - Python dependencies
- `version_info.txt` - Windows version metadata
