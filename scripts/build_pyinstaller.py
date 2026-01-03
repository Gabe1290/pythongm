#!/usr/bin/env python3
"""
Build script for creating a standalone PyGameMaker executable using PyInstaller.

Usage:
    python scripts/build_pyinstaller.py [--debug]

Options:
    --debug     Include debug information and console output

This creates a single-file Windows executable (PyGameMaker.exe) with all
dependencies bundled, including:
- PySide6 and QtWebEngine for the IDE interface
- Pygame for game runtime
- All translation files for multi-language support
- Theme configurations and resources
"""

import subprocess
import sys
import shutil
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("ERROR: PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        return False


def clean_build_artifacts(project_dir):
    """Clean previous build artifacts."""
    artifacts = [
        project_dir / 'build',
        project_dir / 'dist',
        project_dir / '__pycache__',
    ]

    for artifact in artifacts:
        if artifact.exists():
            print(f"Cleaning: {artifact}")
            if artifact.is_dir():
                shutil.rmtree(artifact)
            else:
                artifact.unlink()


def build_executable(project_dir, debug=False):
    """Build the PyGameMaker executable."""
    spec_file = project_dir / 'PyGameMaker.spec'

    if not spec_file.exists():
        print(f"ERROR: Spec file not found: {spec_file}")
        return False

    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',  # Clean PyInstaller cache
        '--noconfirm',  # Don't ask for confirmation
    ]

    if debug:
        cmd.append('--log-level=DEBUG')

    cmd.append(str(spec_file))

    print("=" * 60)
    print("Building PyGameMaker with PyInstaller")
    print("=" * 60)
    print()
    print(f"Spec file: {spec_file}")
    print(f"Debug mode: {'Yes' if debug else 'No'}")
    print()

    try:
        result = subprocess.run(cmd, cwd=str(project_dir), check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code: {e.returncode}")
        return False


def main():
    # Parse arguments
    debug = '--debug' in sys.argv

    # Get project directory (parent of scripts folder)
    script_dir = Path(__file__).parent.absolute()
    project_dir = script_dir.parent

    print(f"Project directory: {project_dir}")

    # Change to project directory
    import os
    os.chdir(project_dir)

    # Check requirements
    if not check_pyinstaller():
        sys.exit(1)

    # Check main script exists
    main_script = project_dir / 'main.py'
    if not main_script.exists():
        print(f"ERROR: Main script not found: {main_script}")
        sys.exit(1)

    # Clean previous builds
    print()
    print("Cleaning previous build artifacts...")
    clean_build_artifacts(project_dir)

    # Build
    print()
    if build_executable(project_dir, debug):
        print()
        print("=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)

        exe_path = project_dir / 'dist' / 'PyGameMaker.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Executable: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
        else:
            print(f"Executable should be at: {exe_path}")
    else:
        print()
        print("=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
