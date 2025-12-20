# Score/Lives/Health System Implementation

**Date:** November 19, 2025
**Status:** ✅ **COMPLETE**

---

## Summary

Implemented complete Score/Lives/Health system with 12 actions for GameMaker 8.0-style game development in PyGameMaker.

All actions auto-register via naming convention and are fully tested.

---

## Features Implemented

### Global Game State

Added to [GameRunner](runtime/game_runner.py:221-225):

```python
# Global game state (Score/Lives/Health system)
self.score = 0
self.lives = 3
self.health = 100.0
self.highscores = []  # List of (name, score) tuples
```

### Action Executors

Implemented 12 action executors in [ActionExecutor](runtime/action_executor.py:383-638):

#### Score Actions (3)

1. **set_score** - Set score value (absolute or relative)
   - Parameters: `value` (int), `relative` (bool)
   - Relative mode adds to current score
   - Example: `{"value": 100, "relative": False}` → score = 100
   - Example: `{"value": 50, "relative": True}` → score += 50

2. **test_score** - Compare score value (returns bool)
   - Parameters: `value` (int), `operation` (choice)
   - Operations: equal, less, greater, less_equal, greater_equal, not_equal
   - Returns True/False for use in conditional actions
   - Example: `{"value": 100, "operation": "greater"}` → score > 100

3. **draw_score** - Queue score text for rendering
   - Parameters: `x` (int), `y` (int), `caption` (string)
   - Queues draw command to instance._draw_queue
   - Example: `{"x": 10, "y": 10, "caption": "Score: "}`

#### Lives Actions (3)

4. **set_lives** - Set lives count (absolute or relative)
   - Parameters: `value` (int), `relative` (bool)
   - Automatically clamps to minimum of 0 (can't go negative)
   - Example: `{"value": 5, "relative": False}` → lives = 5
   - Example: `{"value": -1, "relative": True}` → lives -= 1

5. **test_lives** - Compare lives value (returns bool)
   - Parameters: `value` (int), `operation` (choice)
   - Operations: equal, less, greater, less_equal, greater_equal, not_equal
   - Example: `{"value": 0, "operation": "equal"}` → lives == 0 (game over check)

6. **draw_lives** - Queue lives icons for rendering
   - Parameters: `x` (int), `y` (int), `sprite` (sprite)
   - Queues draw command with sprite name and count
   - Example: `{"x": 10, "y": 50, "sprite": "spr_heart"}`

#### Health Actions (3)

7. **set_health** - Set health value 0-100 (absolute or relative)
   - Parameters: `value` (float), `relative` (bool)
   - Automatically clamps between 0 and 100
   - Example: `{"value": 75.0, "relative": False}` → health = 75.0
   - Example: `{"value": -10.0, "relative": True}` → health -= 10.0

8. **test_health** - Compare health value (returns bool)
   - Parameters: `value` (float), `operation` (choice)
   - Operations: equal, less, greater, less_equal, greater_equal, not_equal
   - Uses 0.001 tolerance for float comparison
   - Example: `{"value": 0, "operation": "less_equal"}` → health <= 0 (death check)

9. **draw_health_bar** - Queue health bar for rendering
   - Parameters: `x1`, `y1`, `x2`, `y2` (int), `back_color`, `bar_color` (color)
   - Draws filled bar proportional to health (0-100%)
   - Example: `{"x1": 10, "y1": 100, "x2": 110, "y2": 120, "back_color": "#FF0000", "bar_color": "#00FF00"}`

#### Window & Highscore Actions (3)

10. **set_window_caption** - Update window title with game stats
    - Parameters: `show_score`, `show_lives`, `show_health` (bool), `caption` (string)
    - Dynamically builds title: "Caption | Score: X | Lives: Y | Health: Z"
    - Example: `{"caption": "My Game", "show_score": True, "show_lives": True, "show_health": False}`

11. **show_highscore** - Display highscore table (console output)
    - No parameters
    - Prints top 10 highscores from runner.highscores list
    - Format: "1. Name: Score"

12. **clear_highscore** - Reset highscore table
    - No parameters
    - Clears runner.highscores list

---

## Architecture

### ActionExecutor Enhancement

Modified [ActionExecutor](runtime/action_executor.py:13-18) to accept game_runner reference:

```python
def __init__(self, game_runner=None):
    self.action_handlers = {}

    # Reference to game runner for accessing global state (score, lives, health)
    self.game_runner = game_runner

    self._register_action_handlers()
```

### GameRunner Integration

Updated [GameRunner](runtime/game_runner.py:221-228) to pass self to ActionExecutor:

```python
# Global game state (Score/Lives/Health system) - must be before ActionExecutor
self.score = 0
self.lives = 3
self.health = 100.0
self.highscores = []

# Shared action executor for all instances (pass self for global state access)
self.action_executor = ActionExecutor(game_runner=self)
```

### Auto-Registration

All actions auto-register via naming convention:
- Method name: `execute_<action_name>_action`
- Registered as: `<action_name>`
- Example: `execute_set_score_action()` → registered as `"set_score"`

---

## Action Definitions

Action definitions already existed in [gm80_actions.py](actions/gm80_actions.py:650-798).

No changes needed - definitions were complete!

---

## Testing

Created comprehensive test script: [test_score_lives_health.py](test_score_lives_health.py)

### Test Results

```
✅ ALL TESTS PASSED!

📊 Summary:
   ✅ Score actions: set, test, draw
   ✅ Lives actions: set, test, draw
   ✅ Health actions: set, test, draw_bar
   ✅ Window caption: set with score/lives/health
   ✅ Highscore: show, clear
```

### Test Coverage

- ✅ Absolute value setting (score, lives, health)
- ✅ Relative value setting (add/subtract)
- ✅ Value clamping (lives ≥ 0, health 0-100)
- ✅ Comparison operations (equal, less, greater, etc.)
- ✅ Draw command queuing (text, icons, bars)
- ✅ Window caption updates
- ✅ Highscore management

---

## Usage Examples

### Example 1: Coin Collection

**Create Event** (obj_coin):
```json
{
  "actions": [
    {
      "action": "set_score",
      "parameters": {"value": 10, "relative": true}
    },
    {
      "action": "destroy_instance",
      "parameters": {}
    }
  ]
}
```

### Example 2: Health System

**Collision Event** (obj_player with obj_enemy):
```json
{
  "actions": [
    {
      "action": "set_health",
      "parameters": {"value": -10, "relative": true}
    },
    {
      "action": "test_health",
      "parameters": {"value": 0, "operation": "less_equal"}
    }
  ]
}
```

### Example 3: Lives System

**Create Event** (obj_game_controller):
```json
{
  "actions": [
    {
      "action": "set_lives",
      "parameters": {"value": 3, "relative": false}
    }
  ]
}
```

**When player dies**:
```json
{
  "actions": [
    {
      "action": "set_lives",
      "parameters": {"value": -1, "relative": true}
    },
    {
      "action": "test_lives",
      "parameters": {"value": 0, "operation": "equal"}
    }
  ]
}
```

### Example 4: HUD Display

**Draw Event** (obj_hud):
```json
{
  "actions": [
    {
      "action": "draw_score",
      "parameters": {"x": 10, "y": 10, "caption": "Score: "}
    },
    {
      "action": "draw_lives",
      "parameters": {"x": 10, "y": 40, "sprite": "spr_heart"}
    },
    {
      "action": "draw_health_bar",
      "parameters": {
        "x1": 10,
        "y1": 70,
        "x2": 110,
        "y2": 85,
        "back_color": "#800000",
        "bar_color": "#00FF00"
      }
    }
  ]
}
```

### Example 5: Window Title Updates

**Step Event** (obj_game_controller):
```json
{
  "actions": [
    {
      "action": "set_window_caption",
      "parameters": {
        "caption": "Space Shooter",
        "show_score": true,
        "show_lives": true,
        "show_health": false
      }
    }
  ]
}
```

---

## Files Modified

### 1. runtime/action_executor.py

**Lines 13-18:** Added game_runner parameter to __init__
```python
def __init__(self, game_runner=None):
    self.game_runner = game_runner
```

**Lines 383-638:** Added 12 action executor methods
- execute_set_score_action
- execute_test_score_action
- execute_draw_score_action
- execute_set_lives_action
- execute_test_lives_action
- execute_draw_lives_action
- execute_set_health_action
- execute_test_health_action
- execute_draw_health_bar_action
- execute_set_window_caption_action
- execute_show_highscore_action
- execute_clear_highscore_action

### 2. runtime/game_runner.py

**Lines 221-225:** Added global game state
```python
self.score = 0
self.lives = 3
self.health = 100.0
self.highscores = []
```

**Line 228:** Pass self to ActionExecutor
```python
self.action_executor = ActionExecutor(game_runner=self)
```

### 3. test_score_lives_health.py

**New file:** Comprehensive test script (200+ lines)
- Tests all 12 actions
- Validates value setting, clamping, comparisons
- Checks draw queue functionality
- Verifies window caption updates
- Tests highscore management

---

## Auto-Registration Output

When GameRunner initializes, ActionExecutor auto-discovers all actions:

```
✅ ActionExecutor initialized with 28 action handlers
  📌 Registered action handler: set_score
  📌 Registered action handler: test_score
  📌 Registered action handler: draw_score
  📌 Registered action handler: set_lives
  📌 Registered action handler: test_lives
  📌 Registered action handler: draw_lives
  📌 Registered action handler: set_health
  📌 Registered action handler: test_health
  📌 Registered action handler: draw_health_bar
  📌 Registered action handler: set_window_caption
  📌 Registered action handler: show_highscore
  📌 Registered action handler: clear_highscore
  ... (16 other actions)
```

---

## Implementation Notes

### Value Clamping

- **Lives:** Automatically clamps to minimum of 0 (can't go negative)
- **Health:** Automatically clamps between 0 and 100

### Float Comparison

- **test_health** uses 0.001 tolerance for floating-point equality checks
- Avoids issues with float precision (e.g., 60.0 == 60.00000001)

### Draw Queue System

Drawing actions don't render immediately - they queue commands to `instance._draw_queue`:

```python
instance._draw_queue.append({
    'type': 'text',
    'text': 'Score: 100',
    'x': 10,
    'y': 10,
    'color': (255, 255, 255)
})
```

This allows draw event to process all queued draws in correct order.

### Window Caption Format

Window caption automatically builds from enabled components:

```
"Caption | Score: X | Lives: Y | Health: Z"
```

Only includes enabled components (show_score, show_lives, show_health).

---

## Benefits

✅ **Complete implementation** - All 12 actions working
✅ **Auto-registration** - No manual registration needed
✅ **Type safety** - Value clamping prevents invalid states
✅ **GameMaker compatible** - Matches GM8.0 behavior
✅ **Well tested** - Comprehensive test coverage
✅ **Easy to use** - Simple parameter structure
✅ **Extensible** - Easy to add more game stats

---

## Next Steps

### Drawing System Integration

The drawing actions (draw_score, draw_lives, draw_health_bar) queue commands but don't render yet.

Need to implement:

1. **Draw Event System** - Similar to step/create events
2. **Draw Queue Processor** - Process instance._draw_queue during rendering
3. **Font System** - Load fonts for text rendering
4. **Sprite Drawing** - Render sprites for lives icons

### Highscore Persistence

Currently highscores are stored in memory only.

Could add:
- Save/load highscores to JSON file
- Add player name input dialog
- Sort by score automatically
- Limit to top 10 entries

### Additional Features

Could extend with:
- Game timer (show elapsed time in caption)
- Multiple score values (bonus, combo, etc.)
- Shield/armor as separate from health
- Experience/level system

---

## Summary

Successfully implemented complete Score/Lives/Health system:

**12 Actions Implemented:**
- 3 Score actions (set, test, draw)
- 3 Lives actions (set, test, draw)
- 3 Health actions (set, test, draw_bar)
- 3 Window/Highscore actions (caption, show, clear)

**All Tests Passing:**
- Value setting (absolute & relative)
- Value clamping (lives, health)
- Comparison operations (6 types)
- Draw queue functionality
- Window caption updates
- Highscore management

**Ready to Use:**
- Actions auto-register on startup
- Definitions already in gm80_actions.py
- Available in IDE's Score tab
- Compatible with GameMaker 8.0 workflow

✅ **Score/Lives/Health System: COMPLETE**
