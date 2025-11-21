# Create Event Fix - Summary

**Date:** November 19, 2025
**Status:** ✅ **COMPLETE**

---

## What Was Fixed

The create event was executing **3 times** (once per pre-loaded room) instead of **1 time** (only for the active room).

---

## Root Cause

Create events were being triggered in `set_object_data()` during the room **pre-loading phase**, causing them to fire for ALL room instances even though only one room was active.

---

## Solution

1. **Removed** create event trigger from `set_object_data()` in both:
   - [runtime/game_runner.py](runtime/game_runner.py#L87-L92)
   - [runtime/game_engine.py](runtime/game_engine.py#L81-L86)

2. **Added** create event trigger for starting room after sprites are loaded:
   - [runtime/game_runner.py](runtime/game_runner.py#L407-L411)

3. **Kept** create event trigger in `change_room()` for room transitions (unchanged)

---

## Test Results

**Before Fix:**
```
🎬 Executing CREATE event for obj_player (room1st)
🎬 Executing CREATE event for obj_player (room0)
🎬 Executing CREATE event for obj_player (Room1)
```
❌ **3 create events** (all pre-loaded rooms)

**After Fix:**
```
🎬 Triggering create events for starting room: room1st
🎬 Executing CREATE event for GameInstance
   Actions: 1 action(s)
   First action: start_moving_direction
   ➡️ Start Moving Direction: 90.0° at speed 4.0
      hspeed=0.00, vspeed=-4.00
```
✅ **1 create event** (starting room only)

---

## GameMaker Behavior Matched

Create events now fire ONLY when:
1. **Room becomes active** (first time displayed)
2. **Instance is dynamically created** during gameplay

They do NOT fire during room pre-loading.

---

## Files Modified

1. **runtime/game_runner.py**
   - Lines 87-92: Removed create event from `set_object_data()`
   - Lines 407-411: Added create event for starting room

2. **runtime/game_engine.py**
   - Lines 81-86: Removed create event from `set_object_data()`

---

## Documentation

- [GM80_CREATE_EVENT_TIMING_FIX.md](GM80_CREATE_EVENT_TIMING_FIX.md) - Full technical documentation
- [test_create_event.py](test_create_event.py) - Test script

---

**✅ Create Event Timing Now Correct!**
