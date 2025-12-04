#!/usr/bin/env python3
"""
Split translation files by context groups for better manageability.

This script splits monolithic .ts files into smaller, focused translation files
organized by feature/module. Each split file can be independently edited and
compiled.

Usage:
    python scripts/split_translations.py

The script will:
1. Read existing pygm2_XX.ts files from translations/
2. Split them into context-based groups (core, editors, actions, dialogs, blockly)
3. Write new files to translations/ with naming pattern: pygm2_XX_group.ts
4. Original files are preserved (not deleted)
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
from datetime import datetime

# Define context groups - each group becomes a separate .ts file
CONTEXT_GROUPS = {
    'core': [
        'PyGameMakerIDE',
        'PreferencesDialog',
        'AboutDialog',
        'WelcomeTab',
        'EditorStatusWidget',
    ],
    'editors': [
        'RoomEditor',
        'ObjectEditor',
        'BaseEditor',
        'InstanceProperties',
        'MultiActionEditor',
        'EnhancedPropertiesPanel',
        'ObjectPalette',
        'ObjectPropertiesPanel',
    ],
    'actions': [
        'ConditionalActionEditor',
        'ActionConfigDialog',
        'GM80EventsPanel',
        'GM80ActionDialog',
        'EventActionWidget',
    ],
    'dialogs': [
        'ExportProjectDialog',
        'BuildProjectDialog',
        'ImportAssetsDialog',
        'ProjectSettingsDialog',
        'OpenProjectDialog',
        'NewProjectDialog',
        'CreateAssetDialog',
        'AutoSaveSettingsDialog',
        'AssetPropertiesDialog',
        'AssetRenameDialog',
        'AssetTreeWidget',
        'MouseEventSelectorDialog',
        'KeySelectorDialog',
    ],
    'blockly': [
        'BlocklyWidget',
        'BlocklyConfigDialog',
        'BlocklyVisualProgrammingTab',
        'DetachedBlocklyWindow',
    ],
}


def get_group_for_context(context_name: str) -> str:
    """Find which group a context belongs to."""
    for group, contexts in CONTEXT_GROUPS.items():
        if context_name in contexts:
            return group
    return 'misc'  # Fallback for unassigned contexts


def split_ts_file(ts_file: Path, output_dir: Path) -> dict:
    """
    Split a single .ts file into multiple group-based files.

    Returns a dict of {group_name: output_file_path}
    """
    try:
        tree = ET.parse(ts_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"  ❌ Failed to parse {ts_file}: {e}")
        return {}

    # Extract language code from filename (e.g., pygm2_de.ts -> de)
    lang_code = ts_file.stem.split('_')[1]

    # Collect contexts by group
    groups = {group: [] for group in CONTEXT_GROUPS.keys()}
    groups['misc'] = []  # For any unassigned contexts

    for context in root.findall('context'):
        name_elem = context.find('name')
        if name_elem is not None:
            context_name = name_elem.text
            group = get_group_for_context(context_name)
            groups[group].append(context)

    # Create output files for each non-empty group
    output_files = {}

    for group, contexts in groups.items():
        if not contexts:
            continue

        # Create new TS structure
        new_root = ET.Element('TS', {'version': '2.1'})

        for context in contexts:
            new_root.append(context)

        # Write to file
        output_file = output_dir / f"pygm2_{lang_code}_{group}.ts"

        # Create proper XML with declaration
        tree = ET.ElementTree(new_root)
        with open(output_file, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(b'<!DOCTYPE TS>\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)

        # Count messages
        msg_count = sum(len(ctx.findall('message')) for ctx in contexts)
        ctx_count = len(contexts)

        output_files[group] = output_file
        print(f"  ✓ {group}: {ctx_count} contexts, {msg_count} messages -> {output_file.name}")

    return output_files


def main():
    print("=" * 60)
    print("Translation File Splitter")
    print("=" * 60)
    print()

    translations_dir = Path(__file__).parent.parent / 'translations'

    if not translations_dir.exists():
        print(f"❌ Translations directory not found: {translations_dir}")
        return False

    # Find all pygm2_XX.ts files (not already split ones)
    ts_files = [
        f for f in translations_dir.glob('pygm2_*.ts')
        if len(f.stem.split('_')) == 2  # Only pygm2_XX.ts, not pygm2_XX_group.ts
    ]

    if not ts_files:
        print("❌ No translation files found to split")
        return False

    print(f"Found {len(ts_files)} translation file(s) to split:")
    for f in ts_files:
        print(f"  • {f.name}")
    print()

    print("Context groups defined:")
    for group, contexts in CONTEXT_GROUPS.items():
        print(f"  • {group}: {len(contexts)} contexts")
    print()

    # Create backup directory
    backup_dir = translations_dir / 'backup'
    backup_dir.mkdir(exist_ok=True)

    # Process each file
    all_outputs = {}

    for ts_file in ts_files:
        print(f"Processing {ts_file.name}...")

        # Backup original
        backup_file = backup_dir / f"{ts_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ts"
        shutil.copy2(ts_file, backup_file)
        print(f"  📁 Backed up to {backup_file.name}")

        # Split the file
        outputs = split_ts_file(ts_file, translations_dir)
        all_outputs[ts_file.name] = outputs
        print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)

    total_files = sum(len(outputs) for outputs in all_outputs.values())
    print(f"✓ Created {total_files} split translation files")
    print()
    print("Next steps:")
    print("1. Compile split files: python scripts/compile_translations.py")
    print("2. The LanguageManager will automatically load all split files")
    print()
    print("Original files have been preserved. You can delete them after")
    print("verifying the split files work correctly.")

    return True


if __name__ == '__main__':
    main()
