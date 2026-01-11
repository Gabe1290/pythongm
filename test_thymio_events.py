#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Thymio events are properly loaded
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

from events.event_types import EVENT_TYPES
from events.thymio_events import (
    THYMIO_EVENT_TYPES,
    THYMIO_EVENT_TO_ASEBA,
    THYMIO_BUTTON_TO_KEYBOARD,
    get_thymio_events_by_category,
    get_all_thymio_categories,
    get_aseba_event_name
)

print("=" * 70)
print("THYMIO EVENTS TEST")
print("=" * 70)

print(f"\nTotal events in system: {len(EVENT_TYPES)}")
print(f"Thymio events: {len(THYMIO_EVENT_TYPES)}")

print("\n" + "=" * 70)
print("THYMIO EVENTS BY CATEGORY")
print("=" * 70)

categories = get_all_thymio_categories()

for category in categories:
    events = get_thymio_events_by_category(category)
    print(f"\n{category.upper()}:")
    for event_name, event in sorted(events.items()):
        aseba_event = get_aseba_event_name(event_name)
        print(f"  {event.icon} {event.display_name}")
        print(f"     - Name: {event_name}")
        print(f"     - Aseba: {aseba_event}")
        print(f"     - Description: {event.description}")

print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

# Test that events are in the main dictionary
test_events = [
    "thymio_button_center",
    "thymio_proximity_update",
    "thymio_timer_0",
    "thymio_tap",
    "thymio_any_button"
]

print("\nChecking if key events are registered:")
for event_name in test_events:
    exists = event_name in EVENT_TYPES
    status = "✅" if exists else "❌"
    print(f"  {status} {event_name}")

print("\n" + "=" * 70)
print("EVENT TO ASEBA MAPPING")
print("=" * 70)

print("\nPyGameMaker Event → Aseba Event:")
for pgm_event, aseba_event in sorted(THYMIO_EVENT_TO_ASEBA.items()):
    print(f"  {pgm_event:30} → {aseba_event}")

print("\n" + "=" * 70)
print("KEYBOARD SIMULATION MAPPING")
print("=" * 70)

print("\nThymio Button → Keyboard Key (for simulation):")
for button_event, key in sorted(THYMIO_BUTTON_TO_KEYBOARD.items()):
    print(f"  {button_event:30} → {key}")

print("\n" + "=" * 70)
print("SAMPLE EVENT DETAILS")
print("=" * 70)

# Show details of a sample event
sample = EVENT_TYPES.get("thymio_proximity_update")
if sample:
    print(f"\nEvent: {sample.display_name}")
    print(f"Icon: {sample.icon}")
    print(f"Category: {sample.category}")
    print(f"Description: {sample.description}")
    print(f"Parameters: {sample.parameters if sample.parameters else 'None'}")
    print(f"Aseba mapping: {get_aseba_event_name('thymio_proximity_update')}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
