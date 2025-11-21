# GM80 Grid Movement System Redesign

**Date:** November 19, 2025
**Issue:** Grid movement overshoots intermittently
**Status:** 🔄 **IN PROGRESS**

---

## Problem Analysis

The current grid movement system has a fundamental flaw:

### Current (Broken) Flow:

```
Frame 0: Player at x=0, press RIGHT
  → Keyboard event: if_on_grid → set_hspeed=4

Frame 1-7: Moving (x=4, 8, 12, ..., 28)
  → Step event: if_on_grid → NO → nothing
  → Movement continues

Frame 8: Player at x=32 (on grid)
  → Step event: if_on_grid → YES → stop_if_no_keys
  → keys_pressed = {"right"} (still set!)
  → OLD: Doesn't stop → OVERSHOOT!
```

### Root Causes:

1. **Keyboard events fire ONCE on KEYDOWN only**
2. **keys_pressed set persists across frames**
3. **stop_if_no_keys checks keys_pressed** (which is still populated)
4. **No mechanism to restart movement** after stopping at grid

---

## Proposed Solution: Two-Phase Movement System

### Phase 1: Stop at EVERY grid position (no exceptions)

### Phase 2: Check if keys are held and restart movement

This creates precise one-grid-cell-at-a-time movement while key is held.

---

## New Logic Flow

### Frame 0: Player at x=0, press RIGHT
```
1. KEYDOWN event → handle_keyboard_press()
2. keys_pressed.add("right")
3. Keyboard event: if_on_grid → YES → set_hspeed=4
4. Player starts moving
```

### Frame 1-7: Moving (x=4, 8, 12, ..., 28)
```
1. Step event: if_on_grid → NO → nothing
2. Movement continues (hspeed=4)
```

### Frame 8: Reached grid (x=32)
```
1. Step event: if_on_grid → YES
2. ALWAYS stop: hspeed=0, vspeed=0
3. Snap to exact grid: x=32.0
4. Check keys_pressed: {"right"} (key still held)
5. If key held AND on grid → set_hspeed=4 again
6. Movement restarts!
```

### Frame 9: Moving again (x=36, 40, ...)
```
1. Step event: if_on_grid → NO
2. Movement continues
```

### Frame 16: Next grid (x=64)
```
1. Stop again
2. Check keys - if held, restart
3. Repeat...
```

---

## Implementation

### Step Event Logic (redesigned)

```python
# Step event for player:
if_on_grid(grid_size=32):
    then_actions:
        1. stop_movement()  # ALWAYS stop at grid
        2. check_keys_and_move(grid_size=32)  # Restart if keys held
```

### New Action: `check_keys_and_move`

```python
def execute_check_keys_and_move_action(self, instance, parameters):
    """Check if movement keys are held and restart movement

    This action should be called AFTER stopping at a grid position.
    If keys are still held, it restarts movement in that direction.

    Parameters:
        grid_size: Grid cell size (for alignment check)
    """
    grid_size = int(parameters.get("grid_size", 32))
    keys_pressed = getattr(instance, 'keys_pressed', set())

    # Only restart if on exact grid position
    on_grid = (instance.x % grid_size == 0) and (instance.y % grid_size == 0)
    if not on_grid:
        return

    # Check which keys are held and set appropriate speed
    if "right" in keys_pressed:
        instance.hspeed = 4
    elif "left" in keys_pressed:
        instance.hspeed = -4
    else:
        instance.hspeed = 0

    if "up" in keys_pressed:
        instance.vspeed = -4
    elif "down" in keys_pressed:
        instance.vspeed = 4
    else:
        instance.vspeed = 0
```

---

## Benefits

✅ **Precise movement**: Player ALWAYS stops at every grid position
✅ **No overshoot**: Movement reset at each grid cell
✅ **Smooth holding**: Holding key continues grid-by-grid movement
✅ **Clean state**: Each grid cell is a decision point
✅ **Predictable**: No race conditions or timing issues

---

## Migration Path

### Current Events (needs changing):

**Step event:**
```json
{
  "action": "if_on_grid",
  "parameters": {
    "grid_size": 32,
    "then_actions": [
      {
        "action": "stop_if_no_keys",  // OLD
        "parameters": {"grid_size": 32}
      }
    ]
  }
}
```

### New Events (recommended):

**Step event:**
```json
{
  "action": "if_on_grid",
  "parameters": {
    "grid_size": 32,
    "then_actions": [
      {
        "action": "stop_movement",  // NEW: Always stop
        "parameters": {}
      },
      {
        "action": "check_keys_and_move",  // NEW: Restart if keys held
        "parameters": {"grid_size": 32}
      }
    ]
  }
}
```

**Keyboard events:** Keep as-is (or remove entirely!)
```json
// Can be empty! Movement handled entirely by step event + check_keys_and_move
```

---

## Alternative: Pure Step-Event Movement

Actually, we might not even need keyboard events! All movement can be handled in step event:

**Step event only:**
```json
{
  "action": "if_on_grid",
  "parameters": {
    "grid_size": 32,
    "then_actions": [
      {
        "action": "check_keys_and_move",  // Check keys and move if held
        "parameters": {"grid_size": 32, "speed": 4}
      }
    ],
    "else_actions": [
      {
        "action": "stop_movement"  // Stop if not on grid (safety)
      }
    ]
  }
}
```

This is simpler and more robust!

---

## Status

- [x] Identified root cause
- [x] Designed new logic
- [ ] Implement `check_keys_and_move` action
- [ ] Update step event in project
- [ ] Test movement
- [ ] Remove old keyboard events (optional)
