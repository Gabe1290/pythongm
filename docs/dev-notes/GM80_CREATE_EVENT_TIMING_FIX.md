# GM80 Create Event Timing Fix

**Date:** November 19, 2025
**Issue:** Create event executed 3 times (once per room during pre-loading)
**Status:** ✅ **FIXED**

---

## Problem

The user reported that the create event was executing **3 times** when the game started, even though only 1 room was active.

### User Observation

> "Why is the Create event executed 3 times?"

My initial (incorrect) response:
> "It's being executed 3 times because you have 3 rooms in your project (room1st, room0, and Room1), and each room has one player instance. When the game loads, it pre-loads all rooms and their instances, so the create event triggers for the player in each room."

### User Correction (Critical!)

> "You have it wrong. The Create event triggers when an instance is created, either **when the room is first displayed** or when an instance is created during the game"

This revealed the fundamental misunderstanding of when create events should fire.

---

## Root Cause

The create event was being triggered in **`set_object_data()`** method, which is called during the initial room **pre-loading phase** (when sprites are assigned to instances).

### Incorrect Flow

```
Game Initialization
└─ load_rooms_without_sprites()
   ├─ Creates GameRoom("room1st") with instances
   ├─ Creates GameRoom("room0") with instances
   └─ Creates GameRoom("Room1") with instances

Pygame Display Ready
└─ load_sprites()

Sprite Assignment
└─ assign_sprites_to_rooms()
   └─ For EACH room (all 3 rooms):
      └─ room.set_sprites_for_instances()
         └─ For each instance in room:
            └─ instance.set_object_data(object_data)
               ├─ Sets object_data
               └─ ❌ EXECUTES CREATE EVENT HERE (WRONG!)

Game Loop Starts
└─ Only room1st is active, but all 3 create events already fired!
```

**Result:** Create events fired for instances in **ALL rooms** during pre-loading, not just the active room.

### GameMaker Behavior

In GameMaker 8.0, the Create event should **ONLY** trigger when:

1. **Room becomes active** (first time room is displayed)
2. **Instance is dynamically created** during gameplay (via `instance_create()`)

It should **NOT** trigger during room pre-loading or when simply setting object data.

---

## Solution

### Fix 1: Remove Create Event from `set_object_data()`

Removed create event trigger from `set_object_data()` in both GameInstance classes:

**runtime/game_runner.py (lines 87-92)**
```python
def set_object_data(self, object_data: dict):
    """Set the object data from project (create event triggered when room becomes active)"""
    self.object_data = object_data

    # NOTE: Create event is NOT triggered here!
    # It's triggered when the room becomes active (in change_room or run_game_loop)
```

**runtime/game_engine.py (lines 81-86)**
```python
def set_object_data(self, object_data: dict):
    """Set the object data from project (create event triggered when room becomes active)"""
    self.object_data = object_data

    # NOTE: Create event is NOT triggered here!
    # It's triggered when the room becomes active (in change_room)
```

### Fix 2: Add Create Event for Starting Room

Added create event execution after sprites are assigned, but **only for the starting room**:

**runtime/game_runner.py (lines 407-411)**
```python
# IMPORTANT: Execute create events for starting room instances
print(f"\n🎬 Triggering create events for starting room: {self.current_room.name}")
for instance in self.current_room.instances:
    if instance.object_data and "events" in instance.object_data:
        self.action_executor.execute_event(instance, "create", instance.object_data["events"])
```

### Fix 3: Keep Create Event in `change_room()`

The `change_room()` method already triggers create events (both files):

**runtime/game_runner.py (lines 750-753)**
```python
# Execute create events for all instances
for instance in self.current_room.instances:
    if instance.object_data and "events" in instance.object_data:
        instance.action_executor.execute_event(instance, "create", instance.object_data["events"])
```

**runtime/game_engine.py (lines 726-729)**
```python
# Execute create events for all instances
for instance in self.current_room.instances:
    if instance.object_data and "events" in instance.object_data:
        instance.action_executor.execute_event(instance, "create", instance.object_data["events"])
```

---

## Corrected Flow

```
Game Initialization
└─ load_rooms_without_sprites()
   ├─ Creates GameRoom("room1st") with instances
   ├─ Creates GameRoom("room0") with instances
   └─ Creates GameRoom("Room1") with instances

Pygame Display Ready
└─ load_sprites()

Sprite Assignment
└─ assign_sprites_to_rooms()
   └─ For EACH room (all 3 rooms):
      └─ room.set_sprites_for_instances()
         └─ For each instance in room:
            └─ instance.set_object_data(object_data)
               └─ Sets object_data (NO EVENT TRIGGER)

Activate Starting Room
└─ For each instance in current_room ONLY:
   └─ ✅ EXECUTE CREATE EVENT (CORRECT!)

Game Loop Starts
└─ Only room1st is active, only room1st create events fired

User Changes Room
└─ change_room("room0")
   └─ For each instance in room0:
      └─ ✅ EXECUTE CREATE EVENT (CORRECT!)
```

**Result:** Create events fire **ONLY** for the active room when it becomes active.

---

## Testing

### Test Case 1: Game Start
1. Start game with project that has 3 rooms
2. Expected: Create event fires **1 time** (for starting room only)
3. Expected: Console shows "🎬 Triggering create events for starting room: room1st"

### Test Case 2: Room Transition
1. Start game
2. Trigger room transition (next room action)
3. Expected: Create event fires again when new room becomes active
4. Expected: Console shows "🚪 Changing to room: room0"

### Test Case 3: Room Restart
1. Start game
2. Trigger room restart action
3. Expected: Create event fires again for all instances in restarted room

---

## Files Modified

### 1. runtime/game_runner.py

**Lines 87-92:** Removed create event from `set_object_data()`
- No longer triggers create event when object data is set
- Added comment explaining when create event is triggered

**Lines 407-411:** Added create event for starting room
- Triggers create events after sprites are assigned
- Only for starting room instances

**Lines 750-753:** Create event in `change_room()` (unchanged)
- Already correctly triggers create events on room transitions

### 2. runtime/game_engine.py

**Lines 81-86:** Removed create event from `set_object_data()`
- Same fix as game_runner.py
- Added comment explaining when create event is triggered

**Lines 726-729:** Create event in `change_room()` (unchanged)
- Already correctly triggers create events on room transitions

---

## Expected Behavior

### Starting Room
```
🎬 Triggering create events for starting room: room1st
🎬 Executing CREATE event for obj_player
   Actions: 1 action(s)
   First action: start_moving_direction
   ➡️ Start Moving Direction: 90° at speed 4.0
      hspeed=0.00, vspeed=-4.00
```

Only **1 create event** fires for the player in the starting room.

### Room Transition
```
🚪 Changing to room: room0
🎬 Executing CREATE event for obj_player
   Actions: 1 action(s)
   First action: start_moving_direction
```

Create event fires again when transitioning to new room.

---

## Impact

**For Users:**
- ✅ Create event fires exactly once per instance when room becomes active
- ✅ No duplicate create events from room pre-loading
- ✅ Room transitions trigger create events correctly
- ✅ GameMaker-compatible behavior

**For Developers:**
- Clear separation between "loading data" and "activating room"
- `set_object_data()` = data assignment only
- `change_room()` = room activation + create events
- `run_game_loop()` = starting room activation + create events

---

## Summary

Fixed create event timing to match proper GameMaker 8.0 behavior:

**Before:**
- Create events fired during room pre-loading (all 3 rooms)
- Create events fired in `set_object_data()` (wrong place)
- Result: 3 create events for 1 player (1 per pre-loaded room)

**After:**
- Create events fire only when room becomes active
- Create events fire in `run_game_loop()` (starting room) and `change_room()` (transitions)
- Result: 1 create event per instance per room activation

**✅ Create Event Timing Now Matches GameMaker 8.0!**
