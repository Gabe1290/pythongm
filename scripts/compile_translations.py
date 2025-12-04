#!/usr/bin/env python3
"""
Compile all .ts translation files to .qm binary format.

This script finds all .ts files in the translations/ directory and compiles
them using lrelease. It supports both monolithic files (pygm2_XX.ts) and
split files (pygm2_XX_group.ts).

Usage:
    python scripts/compile_translations.py
"""

import subprocess
import sys
from pathlib import Path


def find_lrelease() -> str:
    """Find the lrelease command, trying various locations."""
    # Check venv and local PySide6 locations FIRST (most reliable)
    script_dir = Path(__file__).parent.parent
    home_dir = Path.home()

    pyside_candidates = [
        # User-local PySide6 installations
        home_dir / '.local' / 'lib' / 'python3.11' / 'site-packages' / 'PySide6' / 'lrelease',
        home_dir / '.local' / 'lib' / 'python3.12' / 'site-packages' / 'PySide6' / 'lrelease',
        home_dir / '.local' / 'lib' / 'python3.10' / 'site-packages' / 'PySide6' / 'lrelease',
        # Project venv
        script_dir / 'venv' / 'bin' / 'pyside6-lrelease',
        script_dir / 'venv' / 'lib' / 'python3.12' / 'site-packages' / 'PySide6' / 'lrelease',
        script_dir / 'venv' / 'lib' / 'python3.11' / 'site-packages' / 'PySide6' / 'lrelease',
        script_dir / 'venv_py312' / 'Scripts' / 'pyside6-lrelease.exe',
        script_dir / 'venv_py312' / 'Lib' / 'site-packages' / 'PySide6' / 'lrelease.exe',
    ]

    for path in pyside_candidates:
        if path.exists():
            return str(path)

    # Fall back to system commands
    candidates = [
        'lrelease-qt6',
        'pyside6-lrelease',
        'lrelease',  # Last resort, may be broken Qt5 wrapper
    ]

    for cmd in candidates:
        try:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Verify it actually works
                test = subprocess.run([cmd, '--help'], capture_output=True, text=True)
                if test.returncode == 0:
                    return cmd
        except FileNotFoundError:
            continue

    return None


def compile_ts_file(ts_file: Path, lrelease_cmd: str) -> bool:
    """Compile a single .ts file to .qm format."""
    qm_file = ts_file.with_suffix('.qm')

    try:
        result = subprocess.run(
            [lrelease_cmd, str(ts_file), '-qm', str(qm_file)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True
        else:
            print(f"  ❌ lrelease failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Translation Compiler")
    print("=" * 60)
    print()

    # Find lrelease
    lrelease_cmd = find_lrelease()
    if not lrelease_cmd:
        print("❌ Could not find lrelease command!")
        print("   Install PySide6 or Qt development tools.")
        sys.exit(1)

    print(f"Using lrelease: {lrelease_cmd}")
    print()

    translations_dir = Path(__file__).parent.parent / 'translations'

    if not translations_dir.exists():
        print(f"❌ Translations directory not found: {translations_dir}")
        sys.exit(1)

    # Find all .ts files (excluding backups)
    ts_files = [
        f for f in translations_dir.glob('pygm2_*.ts')
        if 'backup' not in str(f)
    ]

    if not ts_files:
        print("❌ No translation files found to compile")
        sys.exit(1)

    print(f"Found {len(ts_files)} translation file(s):")
    print()

    success_count = 0
    fail_count = 0

    for ts_file in sorted(ts_files):
        print(f"Compiling {ts_file.name}...", end=' ')

        if compile_ts_file(ts_file, lrelease_cmd):
            print("✓")
            success_count += 1
        else:
            fail_count += 1

    print()
    print("=" * 60)
    print(f"✓ Compiled: {success_count}")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count}")
    print("=" * 60)

    return fail_count == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
