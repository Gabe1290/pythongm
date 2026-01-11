#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Thymio actions are properly loaded
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from actions import GM80_ALL_ACTIONS, THYMIO_ACTIONS

print("=" * 70)
print("THYMIO ACTIONS TEST")
print("=" * 70)

print(f"\nTotal actions in system: {len(GM80_ALL_ACTIONS)}")
print(f"Thymio actions: {len(THYMIO_ACTIONS)}")

print("\n" + "=" * 70)
print("THYMIO ACTIONS LIST")
print("=" * 70)

# Group actions by category
categories = {}
for action_name, action_def in THYMIO_ACTIONS.items():
    category = action_def.category
    if category not in categories:
        categories[category] = []
    categories[category].append(action_def)

# Print actions by category
for category, actions in sorted(categories.items()):
    print(f"\n{category.upper().replace('_', ' ')}:")
    for action in sorted(actions, key=lambda a: a.name):
        params_str = ", ".join([p.name for p in action.parameters])
        print(f"  {action.icon} {action.display_name}")
        print(f"     - Name: {action.name}")
        print(f"     - Parameters: {params_str if params_str else 'None'}")
        print(f"     - Description: {action.description}")

print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

# Test that actions are in the main dictionary
test_actions = [
    "thymio_set_motor_speed",
    "thymio_move_forward",
    "thymio_set_led_top",
    "thymio_play_tone",
    "thymio_if_proximity",
    "thymio_set_timer_period"
]

print("\nChecking if key actions are registered:")
for action_name in test_actions:
    exists = action_name in GM80_ALL_ACTIONS
    status = "✅" if exists else "❌"
    print(f"  {status} {action_name}")

print("\n" + "=" * 70)
print("SAMPLE ACTION DETAILS")
print("=" * 70)

# Show details of a sample action
sample = GM80_ALL_ACTIONS.get("thymio_set_motor_speed")
if sample:
    print(f"\nAction: {sample.display_name}")
    print(f"Icon: {sample.icon}")
    print(f"Category: {sample.category}")
    print(f"Tab: {sample.tab}")
    print(f"Description: {sample.description}")
    print(f"Parameters:")
    for param in sample.parameters:
        print(f"  - {param.display_name} ({param.type})")
        print(f"    Default: {param.default}")
        print(f"    Description: {param.description}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
