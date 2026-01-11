#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Thymio Integration with GameRunner
Creates a minimal project with a Thymio robot and tests it
"""

import sys
import json
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Create a minimal test project
test_project_data = {
    "name": "Thymio Integration Test",
    "version": "1.0.0",
    "settings": {
        "window_width": 800,
        "window_height": 600,
        "room_speed": 60,
        "fullscreen": False,
        "interpolate": False,
        "score": 0,
        "lives": 3,
        "health": 100,
        "room_order": ["room_test"]
    },
    "assets": {
        "sprites": {},
        "sounds": {},
        "backgrounds": {},
        "objects": {
            "thymio_robot": {
                "sprite": "",
                "visible": True,
                "solid": False,
                "depth": 0,
                "persistent": False,
                "parent": "",
                "mask": "",
                "is_thymio": True,
                "events": {
                    "create": {
                        "actions": [
                            {
                                "action": "thymio_set_led_top",
                                "parameters": {
                                    "red": "32",
                                    "green": "0",
                                    "blue": "0"
                                }
                            }
                        ]
                    },
                    "thymio_button_forward": {
                        "actions": [
                            {
                                "action": "thymio_move_forward",
                                "parameters": {"speed": "200"}
                            },
                            {
                                "action": "thymio_set_led_top",
                                "parameters": {"red": "0", "green": "32", "blue": "0"}
                            }
                        ]
                    },
                    "thymio_button_center": {
                        "actions": [
                            {
                                "action": "thymio_stop_motors",
                                "parameters": {}
                            },
                            {
                                "action": "thymio_set_led_top",
                                "parameters": {"red": "32", "green": "0", "blue": "0"}
                            }
                        ]
                    },
                    "thymio_proximity_update": {
                        "actions": [
                            {
                                "action": "thymio_if_proximity",
                                "parameters": {
                                    "sensor_index": "2",
                                    "threshold": "2000",
                                    "comparison": ">"
                                }
                            },
                            {
                                "action": "start_block",
                                "parameters": {}
                            },
                            {
                                "action": "thymio_turn_left",
                                "parameters": {"speed": "300"}
                            },
                            {
                                "action": "thymio_set_led_top",
                                "parameters": {"red": "32", "green": "16", "blue": "0"}
                            },
                            {
                                "action": "end_block",
                                "parameters": {}
                            }
                        ]
                    }
                }
            },
            "obj_wall": {
                "sprite": "",
                "visible": True,
                "solid": True,
                "depth": 0,
                "persistent": False,
                "parent": "",
                "mask": "",
                "events": {}
            }
        },
        "rooms": {
            "room_test": {
                "name": "room_test",
                "width": 800,
                "height": 600,
                "speed": 60,
                "persistent": False,
                "background_color": "#323232",
                "creation_code": "",
                "instances": [
                    {
                        "id": "thymio_1",
                        "object_name": "thymio_robot",
                        "x": 400,
                        "y": 300,
                        "creation_code": "",
                        "is_thymio": True
                    },
                    {
                        "id": "wall_1",
                        "object_name": "obj_wall",
                        "x": 100,
                        "y": 100,
                        "creation_code": ""
                    },
                    {
                        "id": "wall_2",
                        "object_name": "obj_wall",
                        "x": 700,
                        "y": 100,
                        "creation_code": ""
                    }
                ]
            }
        }
    }
}

# Save test project
test_dir = Path("C:/Users/gthul/Dropbox/pygm2/test_thymio_project")
test_dir.mkdir(exist_ok=True)

project_file = test_dir / "project.json"
with open(project_file, 'w') as f:
    json.dump(test_project_data, f, indent=2)

print(f"✅ Created test project at: {project_file}")

# Now run the game
from runtime.game_runner import GameRunner

print("\n" + "=" * 70)
print("STARTING THYMIO INTEGRATION TEST")
print("=" * 70)
print("\nControls:")
print("  Arrow Up: Move forward (Button Forward)")
print("  Space: Stop motors (Button Center)")
print("  ESC: Quit")
print("\nRobot will detect obstacles and turn left automatically!")
print("\n" + "=" * 70 + "\n")

runner = GameRunner(str(project_file))
runner.run()

print("\n✅ Test complete!")
