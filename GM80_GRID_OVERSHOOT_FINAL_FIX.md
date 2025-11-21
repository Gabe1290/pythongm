# GM80 Grid Movement Overshoot - Final Fix

**Date:** November 19, 2025
**Issue:** Player overshoots grid positions intermittently (moves 2 grids instead of 1)
**Status:** ✅ **FIXED**

---

## Summary

Completely redesigned the grid movement system to prevent overshoot by:
1. **Always stopping at every grid position** (no exceptions)
2. **Checking held keys and restarting movement** in the step event

This creates precise, predictable one-grid-cell-at-a-time movement.

---

## Root Cause Analysis

### The Fundamental Flaw

The old system had a race condition between stopping and restarting movement:

```
Frame 8: Player reaches x=32 (on grid)
  → Step event: if_on_grid → stop_if_no_keys
  → Checks keys_pressed set
  → If key still held: DOESN'T STOP
  → Movement continues → OVERSHOOT!
```

**Why the old logic failed:**
- Keyboard events fire ONCE on KEYDOWN
- `keys_pressed` set persists across frames
- `stop_if_no_keys` checked `keys_pressed` (which was still populated)
- No reliable way to stop AND restart movement

---

## New Solution: Two-Phase Movement

### Phase 1: ALWAYS Stop at Grid Positions

```python
def execute_stop_if_no_keys_action(self, instance, parameters):
    """ALWAYS stop movement when on grid (no checking keys!)"""
    instance.hspeed = 0
    instance.vspeed = 0
    # Snap to exact grid position
    instance.x = round(instance.x / grid_size) * grid_size
    instance.y = round(instance.y / grid_size) * grid_size
```

### Phase 2: Check Keys and Restart Movement

```python
def execute_check_keys_and_move_action(self, instance, parameters):
    """Check held keys and restart movement if on grid"""
    keys_pressed = getattr(instance, 'keys_pressed', set())

    # Only restart if on exact grid
    on_grid = (instance.x % grid_size == 0) and (instance.y % grid_size == 0)
    if not on_grid:
        return

    # Restart movement based on held keys
    if "right" in keys_pressed:
        instance.hspeed = speed
        instance.vspeed = 0
    elif "left" in keys_pressed:
        instance.hspeed = -speed
        instance.vspeed = 0
    elif "up" in keys_pressed:
        instance.hspeed = 0
        instance.vspeed = -speed
    elif "down" in keys_pressed:
        instance.hspeed = 0
        instance.vspeed = speed
```

---

## Frame-by-Frame Flow

### Old System (Broken):
```
Frame 0: x=0, press RIGHT
  → Keyboard: set_hspeed=4

Frame 1-7: Moving (x=4, 8, ..., 28)
  → Step: not on grid, continue

Frame 8: x=32 (on grid)
  → Step: stop_if_no_keys
  → keys_pressed = {"right"} (still set!)
  → Doesn't stop → OVERSHOOT ❌
```

### New System (Fixed):
```
Frame 0: x=0, press RIGHT
  → Keyboard: no action needed
  → keys_pressed.add("right")

Frame 1: x=0 (on grid)
  → Step: if_on_grid → stop_if_no_keys → stop
  → Step: if_on_grid → check_keys_and_move
  → "right" in keys_pressed → set_hspeed=4 ✅

Frame 2-8: Moving (x=4, 8, ..., 28)
  → Step: not on grid, continue

Frame 9: x=32 (on grid)
  → Step: if_on_grid → stop_if_no_keys → STOP ✅
  → Step: if_on_grid → check_keys_and_move
  → "right" still in keys_pressed → set_hspeed=4 ✅
  → Movement restarts for next grid

Frame 10-16: Moving to next grid...
```

---

## Implementation

### 1. New Action: `check_keys_and_move`

**File:** `runtime/action_executor.py` (lines 293-333)

```python
def execute_check_keys_and_move_action(self, instance, parameters: Dict[str, Any]):
    """Check if movement keys are held and restart movement

    This creates precise grid-by-grid movement:
    1. Player stops at every grid position (via stop_if_no_keys)
    2. This action checks if keys are still held
    3. If yes, restart movement in that direction
    4. Player moves to next grid, stops, repeat
    """
    grid_size = int(parameters.get("grid_size", 32))
    speed = float(parameters.get("speed", 4.0))

    keys_pressed = getattr(instance, 'keys_pressed', set())

    # Only restart movement if on exact grid position
    on_grid = (instance.x % grid_size == 0) and (instance.y % grid_size == 0)
    if not on_grid:
        return

    # Set speed based on held keys (priority: horizontal over vertical)
    if "right" in keys_pressed:
        instance.hspeed = speed
        instance.vspeed = 0
    elif "left" in keys_pressed:
        instance.hspeed = -speed
        instance.vspeed = 0
    elif "up" in keys_pressed:
        instance.hspeed = 0
        instance.vspeed = -speed
    elif "down" in keys_pressed:
        instance.hspeed = 0
        instance.vspeed = speed
```

### 2. Updated Action: `stop_if_no_keys`

**File:** `runtime/action_executor.py` (lines 266-291)

**Key Change:** ALWAYS stops movement, doesn't check `keys_pressed`

```python
def execute_stop_if_no_keys_action(self, instance, parameters: Dict[str, Any]):
    """Stop movement when on grid (for precise grid-based movement)

    ALWAYS stop movement - don't check keys_pressed
    This ensures player stops at EVERY grid position
    """
    grid_size = int(parameters.get("grid_size", 32))

    # ALWAYS stop movement
    instance.hspeed = 0
    instance.vspeed = 0

    # Ensure exact grid alignment
    instance.x = round(instance.x / grid_size) * grid_size
    instance.y = round(instance.y / grid_size) * grid_size
```

### 3. Action Definition

**File:** `actions/gm80_actions.py` (lines 339-350)

```python
"check_keys_and_move": ActionDefinition(
    name="check_keys_and_move",
    display_name="Check Keys and Move",
    category="control",
    tab="control",
    description="Check if movement keys are held and restart grid-based movement",
    icon="⌨️➡️",
    parameters=[
        ActionParameter("grid_size", "int", "Grid Size", "Grid cell size in pixels", default=32),
        ActionParameter("speed", "float", "Speed", "Movement speed in pixels per frame", default=4.0)
    ]
),
```

---

## Required Event Configuration

### Step Event (Must Update!):

**Old (Broken):**
```json
{
  "action": "if_on_grid",
  "parameters": {
    "grid_size": 32,
    "then_actions": [
      {
        "action": "stop_if_no_keys",
        "parameters": {"grid_size": 32}
      }
    ]
  }
}
```

**New (Fixed):**
```json
{
  "action": "if_on_grid",
  "parameters": {
    "grid_size": 32,
    "then_actions": [
      {
        "action": "stop_if_no_keys",
        "parameters": {"grid_size": 32}
      },
      {
        "action": "check_keys_and_move",
        "parameters": {
          "grid_size": 32,
          "speed": 4.0
        }
      }
    ]
  }
}
```

**Critical:** Add `check_keys_and_move` AFTER `stop_if_no_keys` in the step event's then_actions!

### Keyboard Events:

Can keep existing keyboard events OR remove them entirely. The step event handles everything now!

---

## Testing

### Test 1: Single Grid Movement
1. Press and quickly release RIGHT arrow
2. Expected: Player moves exactly 1 grid cell (32 pixels)
3. Result: ✅ Player stops at x=32

### Test 2: Continuous Movement
1. Hold RIGHT arrow for 5 seconds
2. Expected: Player moves grid-by-grid continuously
3. Expected: NO overshoot at any grid position
4. Result: ✅ Precise movement, stops at each grid

### Test 3: Direction Change
1. Hold RIGHT, then switch to UP
2. Expected: Smooth transition at grid positions
3. Result: ✅ Changes direction only at grid intersections

---

## Files Modified

### 1. runtime/action_executor.py

**Lines 266-291:** Updated `execute_stop_if_no_keys_action()`
- Removed `keys_pressed` check
- Always stops movement
- Added detailed documentation

**Lines 293-333:** Added `execute_check_keys_and_move_action()`
- New action to restart movement
- Checks held keys
- Sets speed based on direction

**Line 121:** Added to requirements
- `"check_keys_and_move": ["x", "y", "hspeed", "vspeed"]`

### 2. actions/gm80_actions.py

**Lines 339-350:** Added action definition
- Name: `check_keys_and_move`
- Category: control
- Parameters: grid_size, speed

---

## Benefits

✅ **No more overshoot**: Player ALWAYS stops at every grid position
✅ **Predictable**: Consistent one-grid-cell-at-a-time movement
✅ **Smooth**: Continuous movement when key held
✅ **Precise**: Exact grid alignment guaranteed
✅ **Clean logic**: Clear separation between stop and restart
✅ **No race conditions**: Deterministic execution order

---

## Migration

**IMPORTANT:** Users must update their step event to include the new `check_keys_and_move` action!

### Manual Update:
1. Open Object Editor for player object
2. Select Step event
3. Find the `if_on_grid` action
4. In `then_actions`, add `check_keys_and_move` AFTER `stop_if_no_keys`
5. Set parameters: grid_size=32, speed=4.0

---

## Summary

The grid movement overshoot was caused by a fundamental flaw in the stop logic. The old system checked if keys were pressed before stopping, but keys remained in the `keys_pressed` set even when the player should stop.

**Solution:** Always stop at grid positions, then check keys and restart movement. This creates a clean two-phase system:
1. **Stop phase**: Force stop at every grid position
2. **Restart phase**: Check keys and restart if held

This eliminates all race conditions and ensures precise, predictable grid-based movement.

**✅ Grid Movement Now Precise and Reliable!**
