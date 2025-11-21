# GM80 Grid Movement Overshoot Fix

**Date:** November 19, 2025
**Issue:** Player sometimes moves two grids instead of one (overshoots target position)
**Status:** ✅ **FIXED**

---

## Problem

User reported:
> "There is a slight overshoot when moving on the grid. Sometimes player will move two grids instead of one"

### Observed Behavior

- Player intended to move one grid cell (32 pixels)
- Player sometimes moved two grid cells (64 pixels) instead
- Movement was inconsistent - sometimes correct, sometimes overshooting

---

## Root Causes

The issue had **TWO separate causes**:

### Cause 1: Floating Point Precision in Grid Alignment Check

**Location:** `runtime/action_executor.py` (line 230-232)

**Old Code:**
```python
# Check if position is aligned to grid
x_aligned = (instance.x % grid_size) == 0
y_aligned = (instance.y % grid_size) == 0
on_grid = x_aligned and y_aligned
```

**Problem:**
- Used exact floating-point equality check: `(instance.x % grid_size) == 0`
- Player moves at 4 pixels/frame, grid size is 32 pixels
- After 8 frames: 4 × 8 = 32 pixels (theoretically on grid)
- But due to floating-point arithmetic, position might be 31.999999 or 32.000001
- Exact equality check fails: `31.999999 % 32 != 0`
- Movement continues past grid position → **overshoot!**

**Example:**
```
Frame 7: x = 28.0, hspeed = 4
Frame 8: x = 32.0 (should stop here)
  if_on_grid: 32.0 % 32 == 0 ? → YES (lucky!)

Frame 7: x = 27.9999, hspeed = 4
Frame 8: x = 31.9999 (should stop here)
  if_on_grid: 31.9999 % 32 == 0 ? → NO (floating point error!)
  Movement continues...
Frame 9: x = 35.9999 → overshoot!
```

### Cause 2: Duplicate Step Event Execution

**Location:** `runtime/game_runner.py`

**Old Code:**
```python
def update(self):
    # ... movement code ...

    # Check collision events
    for instance in self.current_room.instances:
        self.check_collision_events(instance, objects_data)

    # Execute step events for all instances
    for instance in self.current_room.instances:
        instance.step()  # ← FIRST EXECUTION

# Main game loop
while self.running:
    self.handle_events()
    self.update()

    # Execute step events for all instances
    for instance in self.current_room.instances:
        instance.step()  # ← SECOND EXECUTION (DUPLICATE!)
```

**Problem:**
- Step events executed **twice per frame**
- Once in `update()` method (line 616)
- Once in main game loop (line 425)
- This doubled the frequency of grid checks and movement updates
- Could cause timing issues with stop logic

---

## Solution

### Fix 1: Add Floating-Point Tolerance to Grid Alignment Check

**File:** `runtime/action_executor.py` (lines 229-249)

```python
def execute_if_on_grid_action(self, instance, parameters: Dict[str, Any]):
    """Check if instance is on grid and execute actions conditionally"""
    grid_size = int(parameters.get("grid_size", 32))
    then_actions = parameters.get("then_actions", [])
    else_actions = parameters.get("else_actions", [])

    # Check if position is aligned to grid (with tolerance for floating point errors)
    # Use small tolerance (0.5 pixels) to account for floating point precision
    tolerance = 0.5
    x_remainder = abs(instance.x % grid_size)
    y_remainder = abs(instance.y % grid_size)

    # Check if close to grid alignment (either near 0 or near grid_size)
    x_aligned = (x_remainder < tolerance) or (x_remainder > grid_size - tolerance)
    y_aligned = (y_remainder < tolerance) or (y_remainder > grid_size - tolerance)
    on_grid = x_aligned and y_aligned

    # If close to grid, snap to exact grid position to prevent drift
    if on_grid:
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size

        for action in then_actions:
            self.execute_action(instance, action)
    else:
        for action in else_actions:
            self.execute_action(instance, action)
```

**How it works:**
1. Instead of exact equality, use **tolerance-based check**
2. Tolerance = 0.5 pixels (half a pixel)
3. Check if position is within 0.5 pixels of grid alignment
4. If x % 32 is < 0.5 OR > 31.5 → considered "on grid"
5. **Immediately snap to exact grid position** to prevent drift

**Example:**
```
Frame 8: x = 31.9999, hspeed = 4
  x_remainder = 31.9999 % 32 = 31.9999
  x_aligned = (31.9999 < 0.5) or (31.9999 > 31.5) → TRUE!
  Snap to grid: x = round(31.9999 / 32) * 32 = 32.0
  Execute then_actions (stop movement)
```

### Fix 2: Remove Duplicate Step Event Execution

**File:** `runtime/game_runner.py` (lines 610-615)

**Before:**
```python
# Check collision events
for instance in self.current_room.instances:
    self.check_collision_events(instance, objects_data)

# Execute step events for all instances
for instance in self.current_room.instances:
    instance.step()  # ← DUPLICATE!
```

**After:**
```python
# Check collision events
for instance in self.current_room.instances:
    self.check_collision_events(instance, objects_data)

# NOTE: Step events are executed in the main game loop, not here
# (see run_game_loop where instance.step() is called)
```

**Result:** Step events now execute **once per frame** (in main game loop only)

---

## Technical Details

### Grid Alignment Logic

The tolerance-based check handles both cases:

**Near 0 (just past grid line):**
- Position: 0.2 pixels past grid line
- Remainder: 0.2 % 32 = 0.2
- Check: 0.2 < 0.5 → **aligned!**

**Near grid_size (just before grid line):**
- Position: 31.8 pixels (0.2 pixels before grid line)
- Remainder: 31.8 % 32 = 31.8
- Check: 31.8 > 31.5 → **aligned!**

### Snap-to-Grid Prevention

After detecting alignment, we **immediately snap** to exact position:
```python
instance.x = round(instance.x / grid_size) * grid_size
```

This prevents floating-point drift from accumulating across multiple movements:
- Without snap: 32.0 → 31.9999 → 31.9998 → 31.9997 (drifts off grid)
- With snap: 32.0 → 32.0 → 32.0 → 32.0 (stays perfectly aligned)

---

## Testing

### Test Case 1: Normal Grid Movement

**Setup:**
- Player at (0, 0)
- Press right arrow (sets hspeed = 4)
- Grid size = 32

**Expected:**
```
Frame 1: x = 0 + 4 = 4
Frame 2: x = 4 + 4 = 8
...
Frame 8: x = 28 + 4 = 32
  if_on_grid: x_remainder = 0.0 < 0.5 → aligned!
  Snap to x = 32.0
  stop_if_no_keys: stop (if key released)
```

**Result:** ✅ Player moves exactly one grid cell

### Test Case 2: Floating-Point Error

**Setup:**
- Player at (27.9999, 0) due to previous drift
- Press right arrow (sets hspeed = 4)

**Expected:**
```
Frame N: x = 27.9999 + 4 = 31.9999
  if_on_grid: x_remainder = 31.9999 > 31.5 → aligned!
  Snap to x = 32.0
  stop_if_no_keys: stop (if key released)
```

**Result:** ✅ Player still moves exactly one grid cell (no overshoot)

### Test Case 3: Multiple Grid Movements

**Setup:**
- Player at (0, 0)
- Hold right arrow for 5 seconds (many grid cells)

**Expected:**
- Every 8 frames, player moves one grid cell
- Position snaps to exact grid alignment each time
- No accumulation of floating-point errors

**Result:** ✅ Consistent one-grid-cell movement throughout

---

## Files Modified

### 1. runtime/action_executor.py

**Lines 229-249:** Updated `execute_if_on_grid_action()` method
- Added floating-point tolerance (0.5 pixels)
- Changed from exact equality to tolerance-based check
- Added automatic snap-to-grid when aligned
- Prevents floating-point drift accumulation

### 2. runtime/game_runner.py

**Lines 614-615:** Removed duplicate step event execution
- Removed `instance.step()` call from `update()` method
- Step events now execute once per frame (in main game loop only)

---

## Impact

**For Users:**
- ✅ Precise grid-based movement
- ✅ No more overshooting
- ✅ Consistent one-grid-cell movement
- ✅ No floating-point drift over time
- ✅ Reliable game feel for grid-based games

**For Developers:**
- Robust floating-point comparison pattern
- Clear separation of concerns (update vs step)
- Automatic drift correction via snap-to-grid
- Extensible tolerance parameter (can be adjusted if needed)

---

## Summary

Fixed grid movement overshoot by:

1. **Added floating-point tolerance** to grid alignment checks
   - Tolerance = 0.5 pixels
   - Accounts for floating-point arithmetic errors
   - Automatically snaps to exact grid position

2. **Removed duplicate step event execution**
   - Step events now execute once per frame
   - Eliminates timing issues

**Before:**
- Exact floating-point equality: `(instance.x % 32) == 0`
- Step events executed twice per frame
- Result: Inconsistent movement, occasional overshoot

**After:**
- Tolerance-based alignment: `x_remainder < 0.5` or `x_remainder > 31.5`
- Step events execute once per frame
- Automatic snap-to-grid prevents drift
- Result: Precise, consistent grid movement

**✅ Grid Movement Now Precise and Reliable!**
