#!/usr/bin/env python3
"""
Extract translatable strings from Python source files using pylupdate6.

This script runs pylupdate6 to extract all tr() strings from the codebase
and generates .ts files. It can generate either monolithic files or split
files by context group.

Usage:
    python scripts/extract_translations.py [--split] [languages...]

Options:
    --split     Generate split files by context group instead of monolithic files
    languages   Language codes to generate (default: de fr it uk)

Examples:
    python scripts/extract_translations.py              # Update de, fr, it, uk (monolithic)
    python scripts/extract_translations.py --split      # Update de, fr, it, uk (split)
    python scripts/extract_translations.py de           # Update only German
    python scripts/extract_translations.py --split de   # Update German, split files
"""

import subprocess
import sys
import tempfile
from pathlib import Path

# Default languages to update
DEFAULT_LANGUAGES = ['de', 'fr', 'it', 'uk']


def find_pylupdate() -> str:
    """Find the pylupdate6 command."""
    candidates = [
        'pylupdate6',
        'pyside6-lupdate',
    ]

    script_dir = Path(__file__).parent.parent
    venv_candidates = [
        script_dir / 'venv' / 'bin' / 'pyside6-lupdate',
        script_dir / 'venv' / 'lib' / 'python3.12' / 'site-packages' / 'PySide6' / 'lupdate',
        script_dir / 'venv_py312' / 'Scripts' / 'pyside6-lupdate.exe',
    ]

    for venv_path in venv_candidates:
        if venv_path.exists():
            return str(venv_path)

    for cmd in candidates:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return cmd
        except FileNotFoundError:
            continue

    return None


def get_source_files(base_dir: Path) -> list:
    """Get all Python source files to scan for translations."""
    source_dirs = ['core', 'editors', 'dialogs', 'widgets', 'utils']
    files = []

    for src_dir in source_dirs:
        dir_path = base_dir / src_dir
        if dir_path.exists():
            files.extend(dir_path.glob('**/*.py'))

    # Also include main.py
    main_py = base_dir / 'main.py'
    if main_py.exists():
        files.append(main_py)

    return sorted(files)


def run_pylupdate(pylupdate_cmd: str, source_files: list, output_ts: Path) -> bool:
    """Run pylupdate to extract strings to a .ts file."""
    # Create a temporary .pro file for pylupdate
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pro', delete=False) as f:
        f.write("SOURCES = \\\n")
        for i, src in enumerate(source_files):
            if i < len(source_files) - 1:
                f.write(f"    {src} \\\n")
            else:
                f.write(f"    {src}\n")
        f.write(f"\nTRANSLATIONS = {output_ts}\n")
        pro_file = f.name

    try:
        result = subprocess.run(
            [pylupdate_cmd, pro_file],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  ❌ pylupdate failed: {result.stderr}")
            return False

        return True

    finally:
        Path(pro_file).unlink(missing_ok=True)


def main():
    print("=" * 60)
    print("Translation String Extractor")
    print("=" * 60)
    print()

    # Parse arguments
    args = sys.argv[1:]
    split_mode = '--split' in args
    if split_mode:
        args.remove('--split')

    languages = args if args else DEFAULT_LANGUAGES

    # Find pylupdate
    pylupdate_cmd = find_pylupdate()
    if not pylupdate_cmd:
        print("❌ Could not find pylupdate6/pyside6-lupdate!")
        print("   Install PySide6: pip install PySide6")
        sys.exit(1)

    print(f"Using pylupdate: {pylupdate_cmd}")
    print(f"Languages: {', '.join(languages)}")
    print(f"Mode: {'split files' if split_mode else 'monolithic files'}")
    print()

    base_dir = Path(__file__).parent.parent
    translations_dir = base_dir / 'translations'
    translations_dir.mkdir(exist_ok=True)

    # Get source files
    source_files = get_source_files(base_dir)
    print(f"Found {len(source_files)} source files")
    print()

    # Generate .ts files for each language
    for lang in languages:
        print(f"Extracting strings for {lang}...")

        if split_mode:
            # For split mode, we still extract to monolithic first,
            # then use split_translations.py to split
            output_ts = translations_dir / f"pygm2_{lang}.ts"
        else:
            output_ts = translations_dir / f"pygm2_{lang}.ts"

        if run_pylupdate(pylupdate_cmd, source_files, output_ts):
            print(f"  ✓ Created {output_ts.name}")
        else:
            print(f"  ✗ Failed for {lang}")

    print()
    print("=" * 60)
    print("Next steps:")
    if split_mode:
        print("1. Run: python scripts/split_translations.py")
        print("2. Translate the split .ts files")
        print("3. Run: python scripts/compile_translations.py")
    else:
        print("1. Translate the .ts files")
        print("2. Run: python scripts/compile_translations.py")
    print("=" * 60)


if __name__ == '__main__':
    main()
