#!/usr/bin/env python3
"""
Test if create event is executing properly
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/gabe/Dropbox/pygm2')

from runtime.game_runner import GameRunner

print("=" * 60)
print("Testing Create Event Execution")
print("=" * 60)

# Load the project
project_path = "/home/gabe/Dropbox/pygm2/Projects/Laby00/project.json"
print(f"\nLoading project: {project_path}")

# Create a game runner with project path
runner = GameRunner(project_path)

if not runner.project_data:
    print("❌ Failed to load project!")
    sys.exit(1)

print("✅ Project loaded successfully")

# Find starting room
starting_room = runner.find_starting_room()
if not starting_room:
    print("❌ No rooms found in project")
    sys.exit(1)

print(f"✅ Starting room: {starting_room}")
runner.current_room = runner.rooms[starting_room]

# Initialize pygame (required before loading sprites)
import pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

print("\n" + "=" * 60)
print("Loading sprites and triggering create events...")
print("=" * 60 + "\n")

# Load sprites
runner.load_sprites()

# Assign sprites to rooms (this will set object_data but NOT trigger create events)
runner.assign_sprites_to_rooms()

# Now manually trigger create events for starting room (simulating what run_game_loop does)
print(f"\n🎬 Triggering create events for starting room: {runner.current_room.name}")
for instance in runner.current_room.instances:
    if instance.object_data and "events" in instance.object_data:
        runner.action_executor.execute_event(instance, "create", instance.object_data["events"])

print("\n" + "=" * 60)
print("Game initialized - check output above for create event debug messages")
print("=" * 60)

# Check if player has speed set
if hasattr(runner, 'instances'):
    for instance in runner.instances:
        if hasattr(instance, 'object_data') and instance.object_data:
            obj_name = instance.object_data.get('name', 'unknown')
            if 'player' in obj_name.lower():
                print(f"\n✅ Found player instance: {obj_name}")
                print(f"   Position: ({instance.x}, {instance.y})")
                if hasattr(instance, 'hspeed'):
                    print(f"   Horizontal speed: {instance.hspeed}")
                if hasattr(instance, 'vspeed'):
                    print(f"   Vertical speed: {instance.vspeed}")
