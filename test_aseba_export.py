#!/usr/bin/env python3
"""
Test Aseba Exporter
Creates a sample Thymio project and exports it to Aseba format
"""

import sys
import os

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

import json
from pathlib import Path
from export.Aseba.aseba_exporter import AsebaExporter


def create_test_project():
    """Create a complete test project with Thymio obstacle avoider"""

    project = {
        "name": "Thymio Obstacle Avoider",
        "version": "0.11.0",
        "settings": {
            "window_title": "Thymio Obstacle Avoider",
            "window_width": 800,
            "window_height": 600,
            "room_speed": 60
        },
        "assets": {
            "sprites": {},
            "objects": {
            "thymio_robot": {
                "object_name": "thymio_robot",
                "sprite": "",
                "is_thymio": True,
                "events": {
                    "create": {
                        "actions": [
                            {
                                "action": "thymio_set_variable",
                                "parameters": {"variable": "moving", "value": "0"}
                            },
                            {
                                "action": "thymio_set_variable",
                                "parameters": {"variable": "speed", "value": "200"}
                            },
                            {
                                "action": "thymio_set_led_top",
                                "parameters": {"red": "0", "green": "32", "blue": "0"}
                            },
                            {
                                "action": "thymio_set_timer_period",
                                "parameters": {"timer_id": "0", "period": "100"}
                            }
                        ]
                    },
                    "thymio_button_forward": {
                        "actions": [
                            {
                                "action": "thymio_set_variable",
                                "parameters": {"variable": "moving", "value": "1"}
                            },
                            {
                                "action": "thymio_play_tone",
                                "parameters": {"frequency": "440", "duration": "30"}
                            }
                        ]
                    },
                    "thymio_button_center": {
                        "actions": [
                            {
                                "action": "thymio_set_variable",
                                "parameters": {"variable": "moving", "value": "0"}
                            },
                            {
                                "action": "thymio_stop_motors",
                                "parameters": {}
                            },
                            {
                                "action": "thymio_leds_off",
                                "parameters": {}
                            }
                        ]
                    },
                    "thymio_proximity_update": {
                        "actions": [
                            # Check if moving
                            {
                                "action": "thymio_if_variable",
                                "parameters": {"variable": "moving", "comparison": "==", "value": "1"}
                            },
                            {
                                "action": "start_block",
                                "parameters": {}
                            },
                            # Check center proximity sensor
                            {
                                "action": "thymio_if_proximity",
                                "parameters": {"sensor_index": "2", "threshold": "2000", "comparison": ">"}
                            },
                            {
                                "action": "start_block",
                                "parameters": {}
                            },
                            # Obstacle detected - turn left
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
                            },
                            {
                                "action": "else",
                                "parameters": {}
                            },
                            {
                                "action": "start_block",
                                "parameters": {}
                            },
                            # No obstacle - move forward
                            {
                                "action": "thymio_move_forward",
                                "parameters": {"speed": "200"}
                            },
                            {
                                "action": "thymio_set_led_top",
                                "parameters": {"red": "0", "green": "32", "blue": "0"}
                            },
                            {
                                "action": "end_block",
                                "parameters": {}
                            },
                            {
                                "action": "end_block",
                                "parameters": {}
                            }
                        ]
                    },
                    "thymio_timer_0": {
                        "actions": [
                            {
                                "action": "thymio_if_variable",
                                "parameters": {"variable": "moving", "comparison": "==", "value": "1"}
                            },
                            {
                                "action": "start_block",
                                "parameters": {}
                            },
                            {
                                "action": "thymio_increase_variable",
                                "parameters": {"variable": "counter", "amount": "1"}
                            },
                            {
                                "action": "end_block",
                                "parameters": {}
                            }
                        ]
                    }
                }
            }
        }
        },
        "rooms": {
            "room_main": {
                "room_name": "room_main",
                "width": 800,
                "height": 600,
                "background_color": "#323232",
                "instances": [
                    {
                        "id": "thymio_1",
                        "object_name": "thymio_robot",
                        "x": 400,
                        "y": 300,
                        "is_thymio": True
                    }
                ]
            }
        }
    }

    return project


def main():
    print("=" * 60)
    print("🤖 Thymio Aseba Exporter Test")
    print("=" * 60)
    print()

    # Create test project
    print("📝 Creating test project...")
    project = create_test_project()

    # Save test project to file
    test_project_path = Path("test_thymio_project.json")
    with open(test_project_path, 'w', encoding='utf-8') as f:
        json.dump(project, f, indent=2)
    print(f"✅ Test project saved: {test_project_path}")
    print()

    # Create exporter
    print("🔧 Creating Aseba exporter...")
    exporter = AsebaExporter()
    print("✅ Exporter created")
    print()

    # Export to Aseba
    print("🚀 Exporting to Aseba format...")
    output_dir = Path("export_output")
    output_dir.mkdir(exist_ok=True)

    try:
        exporter.export(str(test_project_path), str(output_dir))
        print()
        print("=" * 60)
        print("✅ Export Complete!")
        print("=" * 60)
        print()

        # Show generated files
        print("📁 Generated files:")
        aesl_files = list(output_dir.glob("*.aesl"))
        readme_files = list(output_dir.glob("README_*.txt"))

        for file in aesl_files:
            print(f"   • {file.name} ({file.stat().st_size} bytes)")
        for file in readme_files:
            print(f"   • {file.name} ({file.stat().st_size} bytes)")
        print()

        # Show preview of generated AESL code
        if aesl_files:
            aesl_file = aesl_files[0]
            print(f"📄 Preview of {aesl_file.name}:")
            print("-" * 60)
            with open(aesl_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Show first 50 lines
                lines = content.split('\n')
                preview_lines = min(50, len(lines))
                for i, line in enumerate(lines[:preview_lines], 1):
                    print(f"{i:3d} | {line}")
                if len(lines) > preview_lines:
                    print(f"... ({len(lines) - preview_lines} more lines)")
            print("-" * 60)
            print()
            print(f"📊 Total lines: {len(lines)}")
            print()

        # Show README preview
        if readme_files:
            readme_file = readme_files[0]
            print(f"📖 {readme_file.name}:")
            print("-" * 60)
            with open(readme_file, 'r', encoding='utf-8') as f:
                print(f.read())
            print("-" * 60)

        print()
        print("✨ Test completed successfully!")
        print()

        if aesl_files:
            print("Next steps:")
            print("1. Open Aseba Studio")
            print(f"2. Load {aesl_files[0].name} from the export_output folder")
            print("3. Connect to your Thymio robot")
            print("4. Click 'Load' to upload the program")
            print("5. Press the forward button on Thymio to start!")

        return 0

    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
