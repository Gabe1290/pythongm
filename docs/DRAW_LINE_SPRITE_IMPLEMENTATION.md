# Drawing Actions Implementation - draw_line and draw_sprite

**Date:** 2026-01-14
**Status:** ✅ COMPLETED
**Actions Implemented:** 2 drawing actions

---

## Summary

Successfully implemented two additional drawing actions for PyGameMaker:

1. **draw_line** - Draw lines between two points ✅ NEW
2. **draw_sprite** - Draw sprites at specified positions (not just from sprite component) ✅ NEW

These actions enable custom line drawing and flexible sprite rendering in the draw event, completing the medium-priority drawing actions for the 1.0 release.

---

## Implementation Details

### 1. Draw Line (`draw_line`)

**Purpose:** Draw a line between two points

**Parameters:**
- `x1` (float): Start X coordinate (default: 0)
- `y1` (float): Start Y coordinate (default: 0)
- `x2` (float): End X coordinate (default: 100)
- `y2` (float): End Y coordinate (default: 100)

**Features:**
- Expression support for all parameters
- Uses current draw color from `instance.draw_color`
- Queues command to `_draw_queue` for draw event processing
- 1-pixel line width

**Returns:** None (queues draw command)

**Example Usage:**
```python
# Basic line
{
    "action": "draw_line",
    "parameters": {
        "x1": 10,
        "y1": 20,
        "x2": 100,
        "y2": 200
    }
}
```

**With Expressions (from instance to cursor):**
```python
{
    "action": "draw_line",
    "parameters": {
        "x1": "self.x",
        "y1": "self.y",
        "x2": "mouse_x",
        "y2": "mouse_y"
    }
}
```

**Use Cases:**
- Draw connections between objects
- Laser beams or projectile paths
- Debug visualization (pathfinding, line of sight)
- Grid lines and guides
- Custom UI elements (dividers, borders)
- Trajectory indicators
- Graph/chart rendering

**Implementation:**
- Queues command to `instance._draw_queue`
- Processed by `GameRunner._draw_line()` during rendering
- Uses `pygame.draw.line()` for rendering
- Line width = 1 pixel

---

### 2. Draw Sprite (`draw_sprite`)

**Purpose:** Draw a sprite at a specified position (independent of object's sprite component)

**Parameters:**
- `sprite` (string): Name of the sprite to draw (required)
- `x` (float): X coordinate (default: 0)
- `y` (float): Y coordinate (default: 0)
- `subimage` (int): Frame index for animated sprites (default: 0)

**Features:**
- Draw any sprite at any position
- Independent of object's sprite component
- Expression support for all parameters
- Supports animated sprites via frame index
- Sprite lookup from `GameRunner.sprites` dictionary
- Handles both single-frame and multi-frame sprites

**Returns:** None (queues draw command)

**Example Usage:**
```python
# Draw a specific sprite
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_player",
        "x": 100,
        "y": 200,
        "subimage": 0
    }
}
```

**Draw animated sprite (specific frame):**
```python
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_explosion",
        "x": "self.x",
        "y": "self.y",
        "subimage": 3  # Frame 3 of the animation
    }
}
```

**Draw multiple sprites in custom positions:**
```python
# In draw event
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_shadow",
        "x": "self.x",
        "y": "self.y + 5",
        "subimage": 0
    }
},
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_character",
        "x": "self.x",
        "y": "self.y",
        "subimage": "self.animation_frame"
    }
}
```

**Use Cases:**
- Draw shadows or effects under/over objects
- Custom animation control
- Draw UI sprites (icons, cursors, indicators)
- Inventory rendering (draw item sprites)
- Particle effects with sprites
- Draw multiple sprites per object
- Custom layering (draw sprite at different depth)
- Preview sprites before spawning objects

**Implementation:**
- Queues command to `instance._draw_queue`
- Processed by `GameRunner._draw_sprite()` during rendering
- Looks up sprite from `self.sprites` dictionary
- Handles animated sprites via `sprite.frames` list
- Falls back to `sprite.surface` for single-frame sprites
- Uses `screen.blit()` for rendering

---

## Files Modified

### 1. `/runtime/action_executor.py`
**Changes:**
- Added `execute_draw_line_action()` method (35 lines)
- Added `execute_draw_sprite_action()` method (30 lines)
- Total: 65 lines of new code

**Location:** Lines 2447-2511 (DRAWING ACTIONS section)

### 2. `/runtime/game_runner.py`
**Changes:**
- Added `line` case to `_process_draw_queue()` (lines 510-512)
- Added `sprite` case to `_process_draw_queue()` (lines 514-516)
- Added `_draw_line()` helper method (lines 621-630, 10 lines)
- Added `_draw_sprite()` helper method (lines 632-656, 25 lines)
- Total: 39 lines of new code

### 3. `/actions/draw_actions.py`
**Changes:**
- Removed `implemented=False` from `draw_line` definition (line 112)
- Removed `implemented=False` from `draw_sprite` definition (line 23)

---

## Draw Queue System

Both drawing actions use the same queuing system as existing draw actions:

### How It Works:

1. **Action Execution** - Draw actions queue commands:
```python
instance._draw_queue.append({
    'type': 'line',
    'x1': 10,
    'y1': 20,
    'x2': 100,
    'y2': 200,
    'color': (255, 0, 0)
})
```

2. **Queue Processing** - During draw event, `GameRunner` processes queue:
```python
def _process_draw_queue(self, screen):
    for cmd in self._draw_queue:
        if cmd['type'] == 'line':
            self._draw_line(screen, cmd)
        elif cmd['type'] == 'sprite':
            self._draw_sprite(screen, cmd)
    self._draw_queue = []  # Clear after processing
```

3. **Rendering** - Helper methods use pygame to draw:
```python
def _draw_line(self, screen, cmd):
    pygame.draw.line(screen, cmd['color'],
                     (cmd['x1'], cmd['y1']),
                     (cmd['x2'], cmd['y2']), 1)

def _draw_sprite(self, screen, cmd):
    sprite = self.sprites[cmd['sprite_name']]
    if len(sprite.frames) > 0:
        frame = sprite.frames[cmd['subimage'] % len(sprite.frames)]
        screen.blit(frame, (cmd['x'], cmd['y']))
    else:
        screen.blit(sprite.surface, (cmd['x'], cmd['y']))
```

---

## Testing

### Test File: `test_draw_line_sprite.py`

**Test Coverage:**

#### draw_line (3 tests) ✅ ALL PASSED
- ✅ Basic line drawing between two points
- ✅ Line with expression parameters
- ✅ Default parameters

#### draw_sprite (4 tests) ✅ ALL PASSED
- ✅ Basic sprite drawing
- ✅ Sprite with expression parameters
- ✅ Default parameters
- ✅ Animated sprite with frame index

#### Integration (1 test) ✅ PASSED
- ✅ Multiple drawing commands in sequence (line, sprite, line)

**All 8 tests PASSED** ✅

---

## Auto-Discovery System

Both actions are automatically registered via ActionExecutor's auto-discovery:

```
✅ ActionExecutor initialized with 67 action handlers
  📌 Registered action handler: draw_line
  📌 Registered action handler: draw_sprite
```

Action count increased from **65 to 67 registered handlers**!

---

## Impact on 1.0 Release Roadmap

### Before Implementation
- Drawing Actions: 2 medium-priority actions missing
- Missing: draw_line, draw_sprite (flexible)
- Limited ability to draw custom lines and position sprites

### After Implementation
- Drawing Actions: **2 medium-priority actions completed**
- Status: Ready for custom line drawing and flexible sprite rendering
- Roadmap Impact: Removes **MEDIUM priority** blockers for 1.0 release

---

## Game Use Cases

### 1. Line of Sight Indicator
```python
# Draw event - show where player is aiming
{
    "action": "set_draw_color",
    "parameters": {"color": "#FF0000"}  # Red
},
{
    "action": "draw_line",
    "parameters": {
        "x1": "self.x",
        "y1": "self.y",
        "x2": "mouse_x",
        "y2": "mouse_y"
    }
}
```

### 2. Connection Between Objects
```python
# Draw event - draw line to target
{
    "action": "set_draw_color",
    "parameters": {"color": "#00FF00"}  # Green
},
{
    "action": "draw_line",
    "parameters": {
        "x1": "self.x",
        "y1": "self.y",
        "x2": "self.target.x",
        "y2": "self.target.y"
    }
}
```

### 3. Shadow Effect with Sprites
```python
# Draw event - draw shadow under character
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_shadow",
        "x": "self.x",
        "y": "self.y + 5",  # Slightly below
        "subimage": 0
    }
},
# Then draw the character normally (via sprite component)
```

### 4. Custom Animation Control
```python
# Draw event - manually control animation
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_character",
        "x": "self.x",
        "y": "self.y",
        "subimage": "self.custom_frame"
    }
}
```

### 5. Inventory Grid
```python
# Draw event - draw inventory items
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_item_sword",
        "x": 100,
        "y": 100,
        "subimage": 0
    }
},
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_item_potion",
        "x": 150,
        "y": 100,
        "subimage": 0
    }
}
```

### 6. Path Visualization
```python
# Draw event - show path to target
{
    "action": "set_draw_color",
    "parameters": {"color": "#FFFF00"}  # Yellow
},
# Draw multiple line segments
{
    "action": "draw_line",
    "parameters": {
        "x1": "self.x",
        "y1": "self.y",
        "x2": "self.path[0].x",
        "y2": "self.path[0].y"
    }
},
{
    "action": "draw_line",
    "parameters": {
        "x1": "self.path[0].x",
        "y1": "self.path[0].y",
        "x2": "self.path[1].x",
        "y2": "self.path[1].y"
    }
}
```

### 7. UI Cursor
```python
# Draw event - custom cursor sprite
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_cursor",
        "x": "mouse_x - 16",  # Center on cursor
        "y": "mouse_y - 16",
        "subimage": 0
    }
}
```

---

## Technical Notes

### Color System (for draw_line)
- Drawing color set via `set_draw_color` action
- Color stored on instance: `instance.draw_color`
- RGB tuple format: `(255, 0, 0)` for red
- Hex color support: `"#FF0000"` → `(255, 0, 0)`
- Default color: `(0, 0, 0)` black

### Sprite System (for draw_sprite)
- Sprites loaded into `GameRunner.sprites` dictionary
- Sprite names must match asset names in project
- Animated sprites stored as `sprite.frames` list
- Single-frame sprites use `sprite.surface` directly
- Frame index wraps using modulo (prevents index errors)

### Coordinate System
- Screen coordinates: Top-left is (0, 0)
- X increases to the right
- Y increases downward
- Lines specified by start (x1, y1) and end (x2, y2) points
- Sprites drawn with top-left corner at (x, y)

### Expression Parsing
- All numeric parameters support expressions
- Can reference `self.x`, `self.y`, `mouse_x`, `mouse_y`, etc.
- Math operations: `+`, `-`, `*`, `/`
- Example: `"self.x + 10"` evaluates to instance.x + 10

### Performance
- Drawing actions queue commands (O(1) operation)
- All drawing happens in one batch during render
- Efficient for multiple draw commands per frame
- No immediate rendering overhead
- Sprite lookup is O(1) via dictionary

### Error Handling
- draw_sprite: Warns if sprite not found in dictionary
- draw_sprite: Warns if sprite has no surface to draw
- Line drawing: Converts coordinates to int to prevent errors

---

## Next Steps

With these drawing actions complete, the drawing system is ready for production use. Additional enhancements could include:

1. **Line Width Parameter** (LOW) - draw_line with customizable width
2. **draw_arrow** (LOW) - Draw arrows with arrowheads
3. **Advanced Sprite Effects** (LOW) - Rotation, scaling, alpha for draw_sprite
4. **draw_sprite_ext** (LOW) - Extended sprite drawing with transformation

---

## Conclusion

✅ Successfully implemented 2 medium-priority drawing actions
✅ All tests passing (8/8)
✅ Auto-discovery integration working
✅ Draw queue system extended
✅ Ready for use in games
✅ Comprehensive documentation with examples

**Status:** Production-ready for PyGameMaker 1.0

**Total New Handlers:** 67 (was 65)
**Total New Code:** 104 lines (65 in action_executor.py, 39 in game_runner.py)

---

## Action Handler Summary

| Action | Status | Lines | Tests |
|--------|--------|-------|-------|
| draw_line | ✅ IMPLEMENTED | 35 | 3/3 ✅ |
| draw_sprite | ✅ IMPLEMENTED | 30 | 4/4 ✅ |
| **Total** | **2/2 Complete** | **65** | **7/7 ✅** |

Plus 1 integration test (multiple commands) ✅

---

## Drawing Actions Now Available in PyGameMaker

Users can now create:
- ➖ Lines for connections, lasers, paths, and debug visualization
- 🖼️ Flexible sprite rendering independent of object sprite components
- 🎨 Custom layering and effects
- 🎯 UI elements with precise sprite positioning
- 📊 Custom graphs and visualizations

**PyGameMaker drawing system continues to expand!** 🎨

---

## Comparison with GameMaker Studio

### draw_line
**GameMaker Studio:**
```gml
draw_set_color(c_red);
draw_line(x1, y1, x2, y2);
```

**PyGameMaker:**
```json
{
    "action": "set_draw_color",
    "parameters": {"color": "#FF0000"}
},
{
    "action": "draw_line",
    "parameters": {
        "x1": 10, "y1": 20,
        "x2": 100, "y2": 200
    }
}
```

✅ Feature parity achieved!

### draw_sprite
**GameMaker Studio:**
```gml
draw_sprite(spr_player, 0, x, y);
```

**PyGameMaker:**
```json
{
    "action": "draw_sprite",
    "parameters": {
        "sprite": "spr_player",
        "x": 100,
        "y": 200,
        "subimage": 0
    }
}
```

✅ Feature parity achieved!

---

## Medium Priority Drawing Actions Status

| Action | Status | Priority |
|--------|--------|----------|
| draw_text | ✅ COMPLETED | MEDIUM |
| draw_rectangle | ✅ COMPLETED | MEDIUM |
| draw_ellipse | ✅ COMPLETED | MEDIUM |
| draw_line | ✅ COMPLETED | MEDIUM |
| draw_sprite | ✅ COMPLETED | MEDIUM |

**All medium-priority drawing actions are now complete!** 🎉
