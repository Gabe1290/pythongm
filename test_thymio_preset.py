#!/usr/bin/env python3
"""
Test Thymio Preset Configuration
Verifies that the Thymio preset filters correctly
"""

import sys
import os

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

from config.blockly_config import BlocklyConfig, PRESETS


def main():
    print("=" * 60)
    print("🤖 Thymio Preset Configuration Test")
    print("=" * 60)
    print()

    # Get Thymio preset
    print("📋 Loading Thymio preset...")
    thymio_config = PRESETS.get("thymio")

    if not thymio_config:
        print("❌ Thymio preset not found!")
        return 1

    print(f"✅ Thymio preset loaded: {thymio_config.preset_name}")
    print()

    # Check enabled blocks
    print(f"📊 Enabled blocks: {len(thymio_config.enabled_blocks)} blocks")
    print()

    # Categorize blocks
    thymio_blocks = [b for b in thymio_config.enabled_blocks if b.startswith('thymio_')]
    control_blocks = [b for b in thymio_config.enabled_blocks if b in ['start_block', 'end_block', 'else']]
    other_blocks = [b for b in thymio_config.enabled_blocks if b not in thymio_blocks and b not in control_blocks]

    print("🤖 Thymio blocks:")
    print(f"   Total: {len(thymio_blocks)} blocks")

    # Count by type
    events = [b for b in thymio_blocks if 'button' in b or 'proximity' in b or 'ground' in b or 'timer' in b or 'tap' in b or 'sound' in b or 'message' in b]
    motors = [b for b in thymio_blocks if 'motor' in b or 'move' in b or 'turn' in b or 'stop' in b]
    leds = [b for b in thymio_blocks if 'led' in b]
    sound = [b for b in thymio_blocks if 'play' in b or b == 'thymio_stop_sound']
    sensors = [b for b in thymio_blocks if 'read' in b or 'if_proximity' in b or 'if_ground' in b or 'if_button' in b]
    timers = [b for b in thymio_blocks if 'set_timer' in b]
    variables = [b for b in thymio_blocks if 'variable' in b]

    print(f"   - Events: {len(events)}")
    print(f"   - Motors: {len(motors)}")
    print(f"   - LEDs: {len(leds)}")
    print(f"   - Sound: {len(sound)}")
    print(f"   - Sensors: {len(sensors)}")
    print(f"   - Timers: {len(timers)}")
    print(f"   - Variables: {len(variables)}")
    print()

    print("🎮 Control flow blocks:")
    print(f"   Total: {len(control_blocks)} blocks")
    for block in sorted(control_blocks):
        print(f"   - {block}")
    print()

    print("📦 Other blocks:")
    print(f"   Total: {len(other_blocks)} blocks")
    for block in sorted(other_blocks):
        print(f"   - {block}")
    print()

    # Check enabled categories
    print(f"📁 Enabled categories: {len(thymio_config.enabled_categories)} categories")
    for category in sorted(thymio_config.enabled_categories):
        print(f"   - {category}")
    print()

    # Verify all Thymio events are included
    expected_events = [
        'thymio_button_forward', 'thymio_button_backward', 'thymio_button_left',
        'thymio_button_right', 'thymio_button_center', 'thymio_any_button',
        'thymio_proximity_update', 'thymio_ground_update',
        'thymio_timer_0', 'thymio_timer_1', 'thymio_tap',
        'thymio_sound_detected', 'thymio_sound_finished', 'thymio_message_received'
    ]

    print("✅ Verification:")
    missing_events = [e for e in expected_events if e not in thymio_config.enabled_blocks]
    if missing_events:
        print(f"   ❌ Missing events: {missing_events}")
        return 1
    else:
        print(f"   ✓ All {len(expected_events)} Thymio events present")

    # Verify all Thymio actions are included
    expected_actions = [
        # Motors
        'thymio_set_motor_speed', 'thymio_move_forward', 'thymio_move_backward',
        'thymio_turn_left', 'thymio_turn_right', 'thymio_stop_motors',
        # LEDs
        'thymio_set_led_top', 'thymio_set_led_bottom_left', 'thymio_set_led_bottom_right',
        'thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off',
        # Sound
        'thymio_play_tone', 'thymio_play_system_sound', 'thymio_stop_sound',
        # Sensors
        'thymio_read_proximity', 'thymio_read_ground', 'thymio_read_button',
        'thymio_if_proximity', 'thymio_if_ground_dark', 'thymio_if_ground_light',
        'thymio_if_button_pressed', 'thymio_if_button_released',
        # Timers
        'thymio_set_timer_period',
        # Variables
        'thymio_set_variable', 'thymio_increase_variable', 'thymio_decrease_variable',
        'thymio_if_variable'
    ]

    missing_actions = [a for a in expected_actions if a not in thymio_config.enabled_blocks]
    if missing_actions:
        print(f"   ❌ Missing actions: {missing_actions}")
        return 1
    else:
        print(f"   ✓ All {len(expected_actions)} Thymio actions present")

    # Verify control flow blocks
    expected_control = ['start_block', 'end_block', 'else']
    missing_control = [c for c in expected_control if c not in thymio_config.enabled_blocks]
    if missing_control:
        print(f"   ❌ Missing control blocks: {missing_control}")
        return 1
    else:
        print(f"   ✓ All {len(expected_control)} control flow blocks present")

    # Verify create event
    if 'event_create' not in thymio_config.enabled_blocks:
        print("   ❌ Missing event_create block")
        return 1
    else:
        print("   ✓ event_create block present")

    print()
    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print()
    print(f"Summary:")
    print(f"  - {len(expected_events)} Thymio events ✓")
    print(f"  - {len(expected_actions)} Thymio actions ✓")
    print(f"  - {len(expected_control)} control flow blocks ✓")
    print(f"  - event_create block ✓")
    print(f"  - Total enabled: {len(thymio_config.enabled_blocks)} blocks")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
