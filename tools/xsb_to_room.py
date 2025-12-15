#!/usr/bin/env python3
"""
XSB to PyGameMaker Room Converter
Converts Sokoban levels in XSB format to PyGameMaker room JSON files.

XSB Format:
  # = wall
  @ = player (Soko)
  + = player on goal
  $ = box
  * = box on goal
  . = goal (store)
  (space) = floor
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any


def parse_xsb_file(xsb_path: str) -> List[Tuple[int, List[str]]]:
    """Parse XSB file and return list of (level_number, level_lines)

    Supports multiple formats:
    - Lines starting with '; N' for level numbers
    - '---' as level separator
    - Blank lines between levels
    """
    levels = []
    current_level = []
    current_level_num = 1  # Start from 1

    with open(xsb_path, 'r') as f:
        for line in f:
            line = line.rstrip('\n\r')

            # Check for separator line (---)
            if line.strip().startswith('---'):
                # Save previous level if exists
                if current_level:
                    levels.append((current_level_num, current_level))
                    current_level = []
                    current_level_num += 1  # Auto-increment for next level
                continue

            # Check for level number comment
            if line.startswith(';'):
                # Save previous level if exists and we're starting a new numbered level
                comment_text = line.strip('; ').strip()
                try:
                    new_level_num = int(comment_text)
                    # This is a level number - save previous level
                    if current_level:
                        levels.append((current_level_num, current_level))
                        current_level = []
                    current_level_num = new_level_num
                except ValueError:
                    # Just a comment, not a level number - ignore
                    pass
                continue

            # Check if this is level data (contains wall characters)
            if line.strip() and ('#' in line or '@' in line or '$' in line or '.' in line):
                # Level data line
                current_level.append(line)

    # Don't forget last level
    if current_level:
        levels.append((current_level_num, current_level))

    return levels


def xsb_to_room(level_num: int, level_lines: List[str],
                grid_size: int = 32, margin: int = 64) -> Dict[str, Any]:
    """Convert XSB level to PyGameMaker room format"""

    instances = []
    instance_id_counter = 1000000 + level_num * 10000

    # Calculate level dimensions
    max_width = max(len(line) for line in level_lines) if level_lines else 0
    height = len(level_lines)

    # Room dimensions with margin
    room_width = (max_width + 4) * grid_size
    room_height = (height + 4) * grid_size

    # Start position with margin
    start_x = margin
    start_y = margin

    for row, line in enumerate(level_lines):
        for col, char in enumerate(line):
            x = start_x + col * grid_size
            y = start_y + row * grid_size

            if char == '#':
                # Wall
                instances.append(create_instance(
                    instance_id_counter, "obj_wall", x, y
                ))
                instance_id_counter += 1

            elif char == '@':
                # Player (Soko)
                instances.append(create_instance(
                    instance_id_counter, "obj_soko", x, y
                ))
                instance_id_counter += 1

            elif char == '+':
                # Player on goal - need both store and player
                instances.append(create_instance(
                    instance_id_counter, "obj_store", x, y
                ))
                instance_id_counter += 1
                instances.append(create_instance(
                    instance_id_counter, "obj_soko", x, y
                ))
                instance_id_counter += 1

            elif char == '$':
                # Box
                instances.append(create_instance(
                    instance_id_counter, "obj_box", x, y
                ))
                instance_id_counter += 1

            elif char == '*':
                # Box on goal - need store and box_stored
                instances.append(create_instance(
                    instance_id_counter, "obj_store", x, y
                ))
                instance_id_counter += 1
                instances.append(create_instance(
                    instance_id_counter, "obj_box_stored", x, y
                ))
                instance_id_counter += 1

            elif char == '.':
                # Goal (store)
                instances.append(create_instance(
                    instance_id_counter, "obj_store", x, y
                ))
                instance_id_counter += 1

    # Create room data
    room_data = {
        "name": f"level{level_num:02d}",
        "asset_type": "room",
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
        "imported": False,
        "file_path": "",
        "width": room_width,
        "height": room_height,
        "background_color": "#87CEEB",
        "background_image": "",
        "tile_horizontal": False,
        "tile_vertical": False,
        "instances": instances
    }

    return room_data


def create_instance(instance_id: int, object_name: str, x: int, y: int) -> Dict[str, Any]:
    """Create an instance dictionary"""
    return {
        "instance_id": instance_id,
        "object_name": object_name,
        "x": x,
        "y": y,
        "rotation": 0,
        "scale_x": 1.0,
        "scale_y": 1.0,
        "visible": True
    }


def convert_levels(xsb_path: str, output_dir: str, max_levels: int = 50):
    """Convert XSB levels to room JSON files"""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Parsing XSB file: {xsb_path}")
    levels = parse_xsb_file(xsb_path)
    print(f"Found {len(levels)} levels")

    # Convert up to max_levels
    converted = 0
    for level_num, level_lines in levels:
        if converted >= max_levels:
            break

        room_data = xsb_to_room(level_num, level_lines)
        room_name = f"level{level_num:02d}"

        # Save room file
        room_file = output_path / f"{room_name}.json"
        with open(room_file, 'w', encoding='utf-8') as f:
            json.dump(room_data, f, indent=2)

        instance_count = len(room_data['instances'])
        print(f"  Created {room_name}.json ({instance_count} instances)")
        converted += 1

    print(f"\n✅ Converted {converted} levels to {output_path}")
    return converted


def main():
    if len(sys.argv) < 3:
        print("Usage: python xsb_to_room.py <input.xsb> <output_dir> [max_levels]")
        print("Example: python xsb_to_room.py microban.xsb ./rooms 50")
        sys.exit(1)

    xsb_path = sys.argv[1]
    output_dir = sys.argv[2]
    max_levels = int(sys.argv[3]) if len(sys.argv) > 3 else 50

    convert_levels(xsb_path, output_dir, max_levels)


if __name__ == "__main__":
    main()
