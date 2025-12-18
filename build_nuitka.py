#!/usr/bin/env python3
"""
Build script for creating a standalone PyGameMaker executable using Nuitka.

Usage:
    python build_nuitka.py [--onefile] [--debug]

Options:
    --onefile   Create a single executable file (slower startup, easier distribution)
    --debug     Include debug information and console output
"""

import subprocess
import sys
import shutil
from pathlib import Path

# Project configuration
APP_NAME = "PyGameMaker"
MAIN_SCRIPT = "main.py"
VERSION = "0.10.0-alpha"

# Directories to include as data
DATA_DIRS = [
    "translations",
    "utils",  # For themes.json
]

# Individual files to include
DATA_FILES = [
    ("utils/themes.json", "utils/"),
]

# Icon file (if exists)
ICON_FILE = "resources/icon.png"


def get_nuitka_command(onefile=False, debug=False):
    """Build the Nuitka command with all necessary options."""

    cmd = [
        sys.executable, "-m", "nuitka",

        # Output settings
        f"--output-filename={APP_NAME}",
        "--standalone",

        # PySide6 plugin (critical for Qt apps)
        "--enable-plugin=pyside6",

        # Disable console for GUI app (unless debug)
        *([] if debug else ["--disable-console"]),

        # Include required modules that may not be auto-detected
        "--include-module=shiboken6",
        "--include-module=pygame",
        "--include-module=PIL",
        "--include-module=watchdog",

        # QtWebEngine support (for Blockly visual programming)
        "--include-module=PySide6.QtWebEngineWidgets",
        "--include-module=PySide6.QtWebEngineCore",
        "--include-module=PySide6.QtWebChannel",

        # Include package data
        "--include-package-data=PySide6",

        # Product information
        f"--product-name={APP_NAME}",
        f"--product-version={VERSION}",
        "--file-description=PyGameMaker IDE - A GameMaker-inspired game development tool",
        "--copyright=PyGameMaker Team",

        # Compilation options
        "--assume-yes-for-downloads",  # Auto-download dependencies
        "--remove-output",  # Clean previous builds
    ]

    # Add onefile option if requested
    if onefile:
        cmd.append("--onefile")
        # Use temp directory for extraction
        if sys.platform == "win32":
            cmd.append("--onefile-tempdir-spec=%TEMP%/pygamemaker")
        else:
            cmd.append("--onefile-tempdir-spec=/tmp/pygamemaker")

    # Add data directories
    for data_dir in DATA_DIRS:
        data_path = Path(data_dir)
        if data_path.exists():
            cmd.append(f"--include-data-dir={data_dir}={data_dir}")

    # Add specific data files
    for src, dest in DATA_FILES:
        if Path(src).exists():
            cmd.append(f"--include-data-files={src}={dest}")

    # Add translation files explicitly (ensure .qm files are included)
    translations_dir = Path("translations")
    if translations_dir.exists():
        for qm_file in translations_dir.glob("*.qm"):
            cmd.append(f"--include-data-files={qm_file}=translations/")

    # Add icon if available
    icon_path = Path(ICON_FILE)
    if icon_path.exists():
        if sys.platform == "win32":
            # Convert PNG to ICO for Windows (would need pillow)
            cmd.append(f"--windows-icon-from-ico={ICON_FILE}")
        elif sys.platform == "linux":
            cmd.append(f"--linux-icon={ICON_FILE}")

    # Add main script
    cmd.append(MAIN_SCRIPT)

    return cmd


def main():
    # Parse arguments
    onefile = "--onefile" in sys.argv
    debug = "--debug" in sys.argv

    print("=" * 60)
    print(f"Building {APP_NAME} with Nuitka")
    print("=" * 60)
    print()
    print(f"Mode: {'Single file' if onefile else 'Standalone folder'}")
    print(f"Debug: {'Yes' if debug else 'No'}")
    print()

    # Check that we're in the right directory
    if not Path(MAIN_SCRIPT).exists():
        print(f"Error: {MAIN_SCRIPT} not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)

    # Build the command
    cmd = get_nuitka_command(onefile=onefile, debug=debug)

    print("Running Nuitka with command:")
    print(" ".join(cmd[:5]) + " ...")
    print()

    # Run Nuitka
    try:
        result = subprocess.run(cmd, check=True)
        print()
        print("=" * 60)
        print("Build completed successfully!")
        print("=" * 60)

        # Show output location
        if onefile:
            if sys.platform == "win32":
                output = f"{APP_NAME}.exe"
            else:
                output = APP_NAME
        else:
            output = f"main.dist/"

        print(f"Output: {output}")

    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print(f"Build failed with exit code {e.returncode}")
        print("=" * 60)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Nuitka not found!")
        print("Install it with: pip install nuitka")
        sys.exit(1)


if __name__ == "__main__":
    main()
