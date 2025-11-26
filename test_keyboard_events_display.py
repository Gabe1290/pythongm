#!/usr/bin/env python3
"""Test script to verify keyboard events display logic"""

import json

# Sample events data from obj_player
events_data = {
    "keyboard": {
        "right": {"actions": [{"action": "test1"}]},
        "left": {"actions": [{"action": "test2"}]},
        "up": {"actions": [{"action": "test3"}]},
        "down": {"actions": [{"action": "test4"}]}
    }
}

print("Testing keyboard event display logic:")
print("="*60)

for event_name, event_data in events_data.items():
    if event_name in ["keyboard", "keyboard_press", "keyboard_release"]:
        print(f"\nEvent: {event_name}")

        # Count total keys (this is what the code does)
        key_count = sum(1 for k, v in event_data.items()
                       if isinstance(v, dict) and 'actions' in v)
        print(f"Key count: {key_count}")

        # List all keys that should be displayed
        print("\nKeys that should be displayed:")
        for key_name, key_data in event_data.items():
            if key_name == "actions":
                print(f"  Skipping '{key_name}' (old format)")
                continue

            if isinstance(key_data, dict) and 'actions' in key_data:
                action_count = len(key_data.get('actions', []))
                print(f"  ✓ {key_name}: {action_count} actions")
            else:
                print(f"  ✗ {key_name}: invalid structure")

print("\n" + "="*60)
print("Expected result: 4 keys displayed (right, left, up, down)")
