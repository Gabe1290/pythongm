#!/usr/bin/env python3
"""
Fix the obj_player create event in the project JSON.

Changes the create event from:
  if_on_grid (with corrupted nested actions)
To:
  start_moving_direction (with directions=90, speed=4.0)
"""

import json
import shutil
from pathlib import Path

# Project path
project_file = Path("/home/gabe/Dropbox/pygm2/Projects/Laby00/project.json")

# Backup the original file
backup_file = project_file.with_suffix('.json.backup')
shutil.copy2(project_file, backup_file)
print(f"✅ Created backup: {backup_file}")

# Load the project
with open(project_file, 'r') as f:
    project_data = json.load(f)

# Get obj_player
obj_player = project_data['assets']['objects']['obj_player']

# Show current create event
print("\n📋 Current create event:")
if 'create' in obj_player['events']:
    print(json.dumps(obj_player['events']['create'], indent=2))
else:
    print("  (no create event)")

# Fix the create event
obj_player['events']['create'] = {
    "actions": [
        {
            "action": "start_moving_direction",
            "parameters": {
                "directions": 90,  # Up
                "speed": 4.0
            }
        }
    ]
}

print("\n✨ New create event:")
print(json.dumps(obj_player['events']['create'], indent=2))

# Save the fixed project
with open(project_file, 'w') as f:
    json.dump(project_data, f, indent=2)

print(f"\n✅ Fixed project saved to: {project_file}")
print(f"   Backup saved to: {backup_file}")
print("\n🎮 The player will now start moving upward when created!")
