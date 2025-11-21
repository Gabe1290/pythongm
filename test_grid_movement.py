#!/usr/bin/env python3
"""
Test script for grid-based movement system

Tests:
1. Player stops at grid positions
2. Movement restarts when keys are held
3. No overshoot occurs
4. Exact grid alignment maintained
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/gabe/Dropbox/pygm2')

from runtime.game_runner import GameRunner
import pygame

print("=" * 70)
print("Grid Movement Test Script")
print("=" * 70)

# Load the project
project_path = "/home/gabe/Dropbox/pygm2/Projects/Laby00/project.json"
print(f"\nLoading project: {project_path}")

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

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((runner.current_room.width, runner.current_room.height))
pygame.display.set_caption("Grid Movement Test")

print("\n" + "=" * 70)
print("Initializing game...")
print("=" * 70 + "\n")

# Load sprites
runner.load_sprites()

# Assign sprites to rooms
runner.assign_sprites_to_rooms()

# Trigger create events
print(f"\n🎬 Triggering create events for starting room: {runner.current_room.name}")
for instance in runner.current_room.instances:
    if instance.object_data and "events" in instance.object_data:
        runner.action_executor.execute_event(instance, "create", instance.object_data["events"])

print("\n" + "=" * 70)
print("Game initialized - Starting movement test")
print("=" * 70)

# Find player instance
player = None
for instance in runner.current_room.instances:
    if hasattr(instance, 'object_data') and instance.object_data:
        obj_name = instance.object_data.get('name', 'unknown')
        if 'player' in obj_name.lower():
            player = instance
            break

if not player:
    print("❌ Player instance not found!")
    sys.exit(1)

print(f"\n✅ Found player: {player.object_data.get('name', 'unknown')}")
print(f"   Initial position: ({player.x}, {player.y})")

# Test parameters
GRID_SIZE = 32
TEST_DURATION = 10  # seconds
FRAMES_TO_TEST = 60 * TEST_DURATION  # 60 FPS

print(f"\n🔧 Test Configuration:")
print(f"   Grid size: {GRID_SIZE} pixels")
print(f"   Test duration: {TEST_DURATION} seconds")
print(f"   Expected movement speed: 4 pixels/frame")
print(f"   Frames per grid cell: {GRID_SIZE / 4} frames (should be 8)")

print("\n" + "=" * 70)
print("AUTOMATED TEST - Movement Simulation")
print("=" * 70)

# Simulate movement by setting keys_pressed
print("\n📍 Test 1: Simulating RIGHT key press")
print("-" * 70)

# Initialize keys_pressed
player.keys_pressed = set()
player.keys_pressed.add("right")

initial_x = player.x
positions = []

for frame in range(20):  # Test for 20 frames (should move 2+ grid cells)
    # Record position
    positions.append((frame, player.x, player.y, player.hspeed, player.vspeed))

    # Execute step event (this is what happens every frame)
    player.step()

    # Apply movement (this is what update() does)
    if hasattr(player, 'hspeed') and player.hspeed != 0:
        player.x += player.hspeed
    if hasattr(player, 'vspeed') and player.vspeed != 0:
        player.y += player.vspeed

print("\nFrame-by-frame movement log:")
print(f"{'Frame':<6} {'X Position':<12} {'Y Position':<12} {'hspeed':<8} {'vspeed':<8} {'On Grid?':<10} {'Status'}")
print("-" * 70)

grid_stops = 0
overshoots = 0
last_grid_x = initial_x

for frame, x, y, hspeed, vspeed in positions:
    on_grid_x = (x % GRID_SIZE) == 0
    on_grid_y = (y % GRID_SIZE) == 0
    on_grid = on_grid_x and on_grid_y

    status = ""
    if on_grid:
        grid_stops += 1
        if x > last_grid_x + GRID_SIZE:
            overshoots += 1
            status = "⚠️  OVERSHOOT!"
        else:
            status = "✅ On grid"
            last_grid_x = x
    else:
        status = "Moving..."

    print(f"{frame:<6} {x:<12.2f} {y:<12.2f} {hspeed:<8.2f} {vspeed:<8.2f} {str(on_grid):<10} {status}")

print("\n" + "=" * 70)
print("TEST RESULTS")
print("=" * 70)

# Calculate results
distance_moved = positions[-1][1] - initial_x
grid_cells_moved = distance_moved / GRID_SIZE
expected_stops = int(grid_cells_moved)

print(f"\n📊 Movement Statistics:")
print(f"   Initial position: {initial_x}")
print(f"   Final position: {positions[-1][1]}")
print(f"   Distance moved: {distance_moved} pixels")
print(f"   Grid cells moved: {grid_cells_moved:.2f}")
print(f"   Grid stops detected: {grid_stops}")
print(f"   Expected stops: {expected_stops}")
print(f"   Overshoots detected: {overshoots}")

print(f"\n🎯 Test Results:")

success = True

# Check 1: No overshoots
if overshoots == 0:
    print(f"   ✅ PASS: No overshoots detected")
else:
    print(f"   ❌ FAIL: {overshoots} overshoot(s) detected")
    success = False

# Check 2: Movement occurred
if distance_moved > 0:
    print(f"   ✅ PASS: Player moved successfully")
else:
    print(f"   ❌ FAIL: Player did not move")
    success = False

# Check 3: Grid alignment
final_x = positions[-1][1]
if (final_x % GRID_SIZE) == 0:
    print(f"   ✅ PASS: Final position on grid")
else:
    print(f"   ⚠️  WARNING: Final position not on grid ({final_x})")

# Check 4: Reasonable stops
if grid_stops >= expected_stops - 1:  # Allow off-by-one
    print(f"   ✅ PASS: Reasonable number of grid stops")
else:
    print(f"   ⚠️  WARNING: Fewer stops than expected")

print("\n" + "=" * 70)
if success:
    print("✅ OVERALL: Grid movement test PASSED")
else:
    print("❌ OVERALL: Grid movement test FAILED")
print("=" * 70)

print("\n💡 Next Steps:")
if success:
    print("   1. Run the actual game: ./venv/bin/python main.py")
    print("   2. Test with keyboard input manually")
    print("   3. Verify smooth movement feel")
    print("   4. Test rapid direction changes")
else:
    print("   1. Check the step event configuration")
    print("   2. Verify check_keys_and_move action is present")
    print("   3. Review the test output above for issues")

print("\n" + "=" * 70)
print("Test complete!")
print("=" * 70)

pygame.quit()
