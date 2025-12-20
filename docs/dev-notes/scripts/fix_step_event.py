#!/usr/bin/env python3
"""
Fix the obj_player step event to include check_keys_and_move action.

This prevents grid movement overshoot by:
1. Stopping at every grid position (stop_if_no_keys)
2. Checking if keys are held and restarting movement (check_keys_and_move)
"""

import json
import shutil
from pathlib import Path

# Project path
project_file = Path("/home/gabe/Dropbox/pygm2/Projects/Laby00/project.json")

# Backup the original file
backup_file = project_file.with_suffix('.json.backup_step_fix')
shutil.copy2(project_file, backup_file)
print(f"✅ Created backup: {backup_file}")

# Load the project
with open(project_file, 'r') as f:
    project_data = json.load(f)

# Get obj_player
obj_player = project_data['assets']['objects']['obj_player']

# Show current step event
print("\n📋 Current step event:")
if 'step' in obj_player['events']:
    print(json.dumps(obj_player['events']['step'], indent=2))
else:
    print("  (no step event)")

# Fix the step event - add check_keys_and_move action
obj_player['events']['step'] = {
    "actions": [
        {
            "action": "if_on_grid",
            "parameters": {
                "grid_size": 32,
                "then_actions": [
                    {
                        "action": "stop_if_no_keys",
                        "parameters": {
                            "grid_size": 32
                        }
                    },
                    {
                        "action": "check_keys_and_move",
                        "parameters": {
                            "grid_size": 32,
                            "speed": 4.0
                        }
                    }
                ]
            }
        }
    ]
}

print("\n✨ New step event:")
print(json.dumps(obj_player['events']['step'], indent=2))

# Save the fixed project
with open(project_file, 'w') as f:
    json.dump(project_data, f, indent=2)

print(f"\n✅ Fixed project saved to: {project_file}")
print(f"   Backup saved to: {backup_file}")
print("\n🎮 Grid movement should now work without overshoot!")
print("\nThe new logic:")
print("  1. Player reaches grid → STOP (stop_if_no_keys)")
print("  2. Check if keys are held (check_keys_and_move)")
print("  3. If yes → restart movement → move to next grid")
print("  4. Repeat → precise grid-by-grid movement!")
