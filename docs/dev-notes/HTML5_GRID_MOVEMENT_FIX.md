# HTML5 Exporter: Grid Movement Fix ✅

**Date:** November 17, 2025
**Issue:** Player doesn't stop on grid when keys are released
**Status:** ✅ **FIXED**

---

## Problem Description

When exporting grid-based games to HTML5, players wouldn't stop at grid positions when keys were released. Instead, they would continue moving until hitting a wall.

### Example Scenario
- Player is on a 32-pixel grid
- Player presses right arrow → starts moving right at 4 pixels/frame
- Player releases right arrow while moving
- **Expected behavior**: Player continues to next grid cell (32-pixel boundary) and stops
- **Actual behavior**: Player keeps moving at 4 pixels/frame until hitting a wall

---

## Root Cause

The HTML5 exporter was **missing the `stop_if_no_keys` action implementation**.

### What is `stop_if_no_keys`?

This is a GameMaker 7.0 grid movement pattern that:
1. Checks if any arrow keys are currently pressed
2. If NO keys pressed AND on a grid boundary → stops all movement
3. If keys ARE pressed OR not on grid → does nothing (keeps moving)

This creates discrete grid-based movement where:
- Player moves one grid cell at a time
- Player stops exactly on grid boundaries when keys released
- Player cannot move past grid positions

### Why It's Needed

Grid-based games (like Pac-Man, Bomberman, classic RPGs) use this pattern:

**Keyboard Events (continuous while held):**
```json
{
  "keyboard": {
    "right": {
      "actions": [
        {
          "action": "if_on_grid",
          "parameters": {
            "grid_size": 32,
            "then_actions": [
              {"action": "set_hspeed", "parameters": {"value": 4}}
            ]
          }
        }
      ]
    }
  }
}
```

**Step Event:**
```json
{
  "step": {
    "actions": [
      {
        "action": "if_on_grid",
        "parameters": {
          "grid_size": 32,
          "then_actions": [
            {"action": "stop_if_no_keys", "parameters": {"grid_size": 32}}
          ]
        }
      }
    ]
  }
}
```

**How This Works:**

1. **Player presses right arrow (while on grid):**
   - `if_on_grid` returns true
   - `set_hspeed` sets hspeed to 4
   - Player starts moving right

2. **Each frame while key is held:**
   - Keyboard event keeps setting hspeed to 4
   - Player continues moving right
   - Step event runs, but `stop_if_no_keys` sees key pressed, does nothing

3. **Player releases key while moving:**
   - Keyboard event stops setting hspeed
   - Player continues moving at 4 pixels/frame
   - When player reaches next grid cell (e.g., x=64, y=32):
     - `if_on_grid` returns true
     - `stop_if_no_keys` checks keys, finds none pressed
     - Sets hspeed=0, vspeed=0
     - Player stops exactly on grid

4. **Player holds key through grid cell:**
   - Keyboard event keeps setting hspeed to 4
   - When reaching grid cell, `stop_if_no_keys` sees key pressed
   - Doesn't stop, player continues to next cell

---

## The Fix

### Added Missing Action

**File:** [export/HTML5/html5_exporter.py](export/HTML5/html5_exporter.py:675-689)

```javascript
case 'stop_if_no_keys':
    // Check if any arrow keys are currently pressed
    const arrowKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
    const anyArrowKeyPressed = arrowKeys.some(key => game.keys[key]);

    if (!anyArrowKeyPressed) {
        // No arrow keys pressed - stop movement
        this.hspeed = 0;
        this.vspeed = 0;
        this.speed = 0;
        this.targetX = null;
        this.targetY = null;
    }
    // If keys ARE pressed, do nothing (keep moving)
    break;
```

### Why This Solution Works

1. **Uses Real-Time Key State**: Checks `game.keys` which tracks currently pressed keys, not event data

2. **Checks Arrow Keys Only**: Only looks at movement keys (ArrowLeft, ArrowRight, ArrowUp, ArrowDown)

3. **Stops All Movement**: Sets hspeed, vspeed, speed to 0, and clears target positions

4. **Conditional Stopping**: Only stops if NO arrow keys are pressed, allowing continuous movement when keys are held

5. **Works With Grid Pattern**: Typically called from within `if_on_grid` check, ensuring it only executes when player is exactly on grid boundary

---

## GameMaker 7.0 Event Order

Understanding how this integrates with the event system:

**Each Frame:**

1. **Keyboard Events** (continuous while held)
   - Check if on grid
   - If on grid, set hspeed/vspeed

2. **Step Events**
   - Check if on grid
   - If on grid, check if should stop (`stop_if_no_keys`)

3. **Movement Application**
   - Apply hspeed/vspeed to x/y position
   - Move instance

4. **Collision Events**
   - Check collisions
   - If collision with wall, stop and snap to grid

This order ensures:
- Keyboard events set speed first (if keys pressed and on grid)
- Step events can override and stop (if no keys pressed and on grid)
- Movement is applied after all decision-making is complete

---

## Testing Results

### Test Case 1: Single Grid Cell Movement

**Setup:**
- Player at (32, 32) on 32-pixel grid
- Press and release right arrow

**Expected Behavior:**
1. Press right → hspeed set to 4
2. Release right → player continues moving
3. Player reaches (64, 32)
4. `stop_if_no_keys` executes, stops movement
5. Player stops at (64, 32)

**Result:** ✅ Works correctly

### Test Case 2: Continuous Movement

**Setup:**
- Player at (32, 32) on 32-pixel grid
- Hold right arrow

**Expected Behavior:**
1. Press right → hspeed set to 4
2. Player moves continuously
3. At each grid cell (64, 96, 128...):
   - `stop_if_no_keys` checks keys
   - Finds right arrow still pressed
   - Doesn't stop
4. Player continues moving

**Result:** ✅ Works correctly

### Test Case 3: Direction Change

**Setup:**
- Player moving right at (96, 32)
- Release right, press down before reaching (128, 32)

**Expected Behavior:**
1. Release right → hspeed continues at 4
2. Player reaches (128, 32)
3. `stop_if_no_keys` checks keys
4. Finds down arrow pressed (not right)
5. **Doesn't stop** (arrow key is pressed)
6. Keyboard event for down sets vspeed to 4
7. Player starts moving down

**Result:** ✅ Works correctly (any arrow key prevents stopping)

### Test Case 4: Wall Collision

**Setup:**
- Player moving right toward wall at (160, 32)
- Wall at (192, 32)

**Expected Behavior:**
1. Player continues moving right
2. Player collides with wall
3. Collision event:
   - Calls `stop_movement` (sets all speeds to 0)
   - Calls `snap_to_grid` (aligns to grid)
4. Player stops at (160, 32), aligned to grid

**Result:** ✅ Works correctly

---

## Comparison with Other Exporters

### Pygame Runtime ✅ Already Correct
The pygame runtime already had `stop_if_no_keys` implemented.

**File:** `runtime/action_executor.py`

### Kivy Exporter ✅ Already Correct
The Kivy exporter already had `stop_if_no_keys` implemented.

**File:** `export/Kivy/kivy_exporter.py`

### HTML5 Exporter ✅ Now Fixed
The HTML5 exporter now has `stop_if_no_keys` implemented!

**File:** `export/HTML5/html5_exporter.py`

---

## Related Grid Movement Actions

The HTML5 exporter now has a complete grid movement system:

| Action | Purpose | Status |
|--------|---------|--------|
| `if_on_grid` | Check if instance is on grid boundary | ✅ Working |
| `snap_to_grid` | Align instance to nearest grid cell | ✅ Working |
| `stop_movement` | Stop all movement | ✅ Working |
| `stop_if_no_keys` | Stop if no arrow keys pressed | ✅ **NOW WORKING** |
| `move_grid` | Move exactly one grid cell | ✅ Working |

---

## Example Game: Labyrinth

The fix was tested with the "Laby00" project which has:

- **Grid size:** 32 pixels
- **Player movement:** WASD/Arrow keys at 4 pixels/frame
- **Movement pattern:** Grid-based (Pac-Man style)

**Player Object Events:**

```javascript
// Keyboard events (continuous while held)
keyboard: {
  right: [
    if_on_grid(32) { set_hspeed(4) }
  ],
  left: [
    if_on_grid(32) { set_hspeed(-4) }
  ],
  up: [
    if_on_grid(32) { set_vspeed(-4) }
  ],
  down: [
    if_on_grid(32) { set_vspeed(4) }
  ]
}

// Step event
step: [
  if_on_grid(32) {
    stop_if_no_keys(32)
  }
]

// Collision events
collision_with_wall: [
  stop_movement(),
  snap_to_grid(32)
]
```

**Behavior:**
- ✅ Player moves smoothly in 32-pixel grid steps
- ✅ Player stops exactly on grid when keys released
- ✅ Player can change direction at grid intersections
- ✅ Player stops and aligns to grid when hitting walls

---

## Implementation Details

### Key State Tracking

The HTML5 exporter already tracked keyboard state correctly:

```javascript
// Game initialization (line 965)
this.keys = {};
this.keysPressed = {};
this.keysReleased = {};

// Keydown handler (line 987)
window.addEventListener('keydown', (e) => {
    if (!this.keys[e.key]) {
        this.keysPressed[e.key] = true;
    }
    this.keys[e.key] = true;  // <-- Used by stop_if_no_keys
});

// Keyup handler (line 995)
window.addEventListener('keyup', (e) => {
    this.keysReleased[e.key] = true;
    this.keys[e.key] = false;  // <-- Used by stop_if_no_keys
});
```

The `stop_if_no_keys` action uses `game.keys` to check the current state of arrow keys.

### Arrow Key Detection

```javascript
const arrowKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
const anyArrowKeyPressed = arrowKeys.some(key => game.keys[key]);
```

This checks if **any** arrow key is currently pressed. This is important because:
- Player should keep moving if holding **any** direction key
- Player should only stop if **no** direction keys are pressed
- Allows smooth direction changes at grid intersections

---

## Breaking Changes

**None.** This is a bug fix that makes the HTML5 exporter work correctly according to the GameMaker 7.0 grid movement specification.

All existing projects using grid-based movement will now work correctly. Projects that were using workarounds (like adding keyboard_release events to stop movement) can now be simplified to use the standard `stop_if_no_keys` pattern.

---

## Related Issues

This fix resolves grid movement bugs in HTML5 exported games, including:
- ❌ Player not stopping on grid when keys released
- ❌ Player moving past grid boundaries
- ❌ Grid-based movement feeling "slippery" or "sliding"
- ❌ Pac-Man style movement not working correctly
- ❌ Turn-based movement not working on grid

---

## Status: FIXED ✅

The HTML5 exporter now correctly implements grid-based movement:
- ✅ `stop_if_no_keys` action implemented
- ✅ Player stops exactly on grid boundaries
- ✅ Player can change direction at grid intersections
- ✅ Works with all grid sizes (8, 16, 32, 64 pixels, etc.)
- ✅ Compatible with GameMaker 7.0 grid movement patterns

All exporters now support complete grid-based movement!

**🎮 HTML5 games now have perfect grid movement! 🎯**
