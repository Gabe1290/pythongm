#!/usr/bin/env python3
"""
Add room references to project.json from rooms/ directory.

This tool scans the rooms/ directory for room JSON files and adds
corresponding entries to the project.json assets section.
"""

import json
from pathlib import Path
from collections import OrderedDict
from datetime import datetime
from typing import Tuple, Union


def add_rooms_to_project(project_path: str) -> bool:
    """Add room entries to project.json for all room files in rooms/ directory.

    Args:
        project_path: Path to the project directory

    Returns:
        True if successful, False otherwise
    """

    project_dir = Path(project_path)
    project_file = project_dir / "project.json"
    rooms_dir = project_dir / "rooms"

    if not project_file.exists():
        print(f"❌ Project file not found: {project_file}")
        return False

    if not rooms_dir.exists():
        print(f"❌ Rooms directory not found: {rooms_dir}")
        return False

    # Load project data
    with open(project_file, 'r', encoding='utf-8') as f:
        project_data = json.load(f, object_pairs_hook=OrderedDict)

    # Get existing rooms
    if 'assets' not in project_data:
        project_data['assets'] = OrderedDict()
    if 'rooms' not in project_data['assets']:
        project_data['assets']['rooms'] = OrderedDict()

    rooms = project_data['assets']['rooms']
    existing_rooms = set(rooms.keys())

    # Find all room files
    room_files = sorted(rooms_dir.glob("*.json"))

    print(f"Found {len(room_files)} room files")
    print(f"Existing rooms: {list(existing_rooms)}")

    added = 0
    for room_file in room_files:
        room_name = room_file.stem

        if room_name in existing_rooms:
            print(f"  ⏭️  {room_name} already exists")
            continue

        # Load room data to get metadata
        with open(room_file, 'r', encoding='utf-8') as f:
            room_data = json.load(f)

        # Create room entry (without instances - they're in separate file)
        room_entry = OrderedDict([
            ("name", room_name),
            ("asset_type", "room"),
            ("created", room_data.get("created", datetime.now().isoformat())),
            ("modified", room_data.get("modified", datetime.now().isoformat())),
            ("imported", False),
            ("file_path", ""),
            ("width", room_data.get("width", 640)),
            ("height", room_data.get("height", 480)),
            ("background_color", room_data.get("background_color", "#87CEEB")),
            ("background_image", room_data.get("background_image", "")),
            ("tile_horizontal", room_data.get("tile_horizontal", False)),
            ("tile_vertical", room_data.get("tile_vertical", False)),
            ("instance_count", len(room_data.get("instances", []))),
            ("instances", []),  # Empty - data in separate file
            ("_external_file", f"rooms/{room_name}.json")
        ])

        rooms[room_name] = room_entry
        print(f"  ✅ Added {room_name} ({room_entry['instance_count']} instances)")
        added += 1

    # Sort rooms: 'start' first, then levels in numeric order
    def room_sort_key(name: str) -> Tuple[int, Union[int, str]]:
        """Sort key for room ordering."""
        if name == 'start':
            return (0, 0)
        elif name.startswith('level'):
            try:
                num = int(name.replace('level', ''))
                return (1, num)
            except ValueError:
                return (2, name)
        return (2, name)

    sorted_rooms = OrderedDict()
    for room_name in sorted(rooms.keys(), key=room_sort_key):
        sorted_rooms[room_name] = rooms[room_name]

    project_data['assets']['rooms'] = sorted_rooms

    # Update modified date
    project_data['modified'] = datetime.now().isoformat()

    # Save project file
    with open(project_file, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Added {added} new rooms to project.json")
    print(f"Total rooms: {len(sorted_rooms)}")

    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python add_rooms_to_project.py <project_directory>")
        sys.exit(1)

    add_rooms_to_project(sys.argv[1])
