# Room Configuration Actions Implementation

**Date:** 2026-01-14
**Status:** ✅ COMPLETED
**Actions Implemented:** 4 room configuration actions

---

## Summary

Successfully implemented four room configuration actions for PyGameMaker:

1. **set_room_caption** - Set window caption/title text ✅ NEW
2. **set_room_speed** - Set game speed (FPS) ✅ NEW
3. **set_background_color** - Set room background color ✅ NEW
4. **set_background** - Set room background image with tiling ✅ NEW

These actions enable runtime configuration of rooms, backgrounds, and game speed, completing the lower-priority room configuration actions for the 1.0 release.

---

## Implementation Details

### 1. Set Room Caption (`set_room_caption`)

**Purpose:** Set the window caption/title text

**Parameters:**
- `caption` (string): Caption text to display (default: "")

**Features:**
- Sets window title text
- Updates display immediately via `update_caption()`
- Works with existing caption system (score/lives/health display)
- Simple string parameter (no expression parsing)

**Returns:** None

**Example Usage:**
```python
{
    "action": "set_room_caption",
    "parameters": {
        "caption": "My Game - Level 1"
    }
}
```

**Use Cases:**
- Show game title
- Display current level
- Show player name
- Custom window branding
- Dynamic caption based on game state

**Implementation:**
- Updates `game_runner.window_caption`
- Calls `game_runner.update_caption()` immediately
- Caption appears alongside score/lives/health if enabled

---

### 2. Set Room Speed (`set_room_speed`)

**Purpose:** Set game speed (frames per second)

**Parameters:**
- `speed` (int): Target FPS (default: 30, range: 1-240)

**Features:**
- Expression support for dynamic FPS
- Automatically clamped to reasonable bounds (1-240)
- Updates game loop clock immediately
- Affects all game timing

**Returns:** None

**Example Usage:**
```python
{
    "action": "set_room_speed",
    "parameters": {
        "speed": 60
    }
}
```

**Dynamic speed:**
```python
{
    "action": "set_room_speed",
    "parameters": {
        "speed": "30 + self.turbo_mode * 30"  # 30 or 60 FPS
    }
}
```

**Use Cases:**
- Standard 60 FPS gameplay
- Slow-motion effects (lower FPS)
- Turbo mode (higher FPS)
- Performance optimization
- Match target platform FPS

**Implementation:**
- Updates `game_runner.fps`
- Clamped between 1 and 240 FPS
- Applied to `clock.tick()` in game loop

---

### 3. Set Background Color (`set_background_color`)

**Purpose:** Set room background color

**Parameters:**
- `color` (color): Background color hex string (default: "#000000")
- `show_color` (boolean): Whether to display the color (default: True)

**Features:**
- Hex color support (#RRGGBB format)
- Expression support for color string
- Updates current room immediately
- `show_color` parameter for compatibility

**Returns:** None

**Example Usage:**
```python
{
    "action": "set_background_color",
    "parameters": {
        "color": "#87CEEB",  # Sky blue
        "show_color": True
    }
}
```

**Dark theme:**
```python
{
    "action": "set_background_color",
    "parameters": {
        "color": "#001122",  # Dark blue
        "show_color": True
    }
}
```

**Use Cases:**
- Set room theme colors
- Day/night cycle effects
- Underwater effects (blue tint)
- Poison/damage effects (red flash)
- Custom level themes

**Implementation:**
- Updates `current_room.background_color`
- Parses hex color string to RGB tuple
- Applied during room rendering

---

### 4. Set Background (`set_background`)

**Purpose:** Set room background image with tiling and scrolling options

**Parameters:**
- `background` (string): Background/sprite name to use (required)
- `visible` (boolean): Show background (default: True)
- `foreground` (boolean): Draw in front of objects (default: False)
- `tiled_h` (boolean): Tile horizontally (default: False)
- `tiled_v` (boolean): Tile vertically (default: False)
- `hspeed` (float): Horizontal scroll speed (default: 0)
- `vspeed` (float): Vertical scroll speed (default: 0)

**Features:**
- Load background from sprites or backgrounds assets
- Horizontal and vertical tiling support
- Visibility control (show/hide)
- Foreground layer support (acknowledged)
- Scrolling parameters (acknowledged, not yet animated)
- Expression support for all parameters

**Returns:** None

**Example Usage:**
```python
{
    "action": "set_background",
    "parameters": {
        "background": "bg_mountains",
        "visible": True,
        "tiled_h": True,
        "tiled_v": False
    }
}
```

**Scrolling background:**
```python
{
    "action": "set_background",
    "parameters": {
        "background": "bg_clouds",
        "visible": True,
        "tiled_h": True,
        "tiled_v": True,
        "hspeed": 1,   # Scroll right
        "vspeed": 0.5  # Scroll down slowly
    }
}
```

**Hide background:**
```python
{
    "action": "set_background",
    "parameters": {
        "background": "bg_any",
        "visible": False
    }
}
```

**Use Cases:**
- Change background between levels
- Parallax scrolling effects
- Animated cloud/water backgrounds
- Day/night background switching
- Hide background for cutscenes
- Foreground overlay effects

**Implementation:**
- Looks up background/sprite from assets
- Updates `current_room.background_surface`
- Updates `current_room.tile_horizontal` and `tile_vertical`
- Foreground and scrolling noted (future implementation)
- Applied during room rendering

---

## Files Modified

### 1. `/runtime/action_executor.py`
**Changes:**
- Added `execute_set_room_caption_action()` method (20 lines)
- Added `execute_set_room_speed_action()` method (27 lines)
- Added `execute_set_background_color_action()` method (23 lines)
- Added `execute_set_background_action()` method (80 lines)
- Added `_parse_color()` helper method (18 lines)
- Total: 168 lines of new code

**Location:** Lines 2547-2723 (ROOM CONFIGURATION ACTIONS section)

### 2. `/actions/rooms_actions.py`
**Changes:**
- Removed `implemented=False` from `set_room_speed` (line 20)
- Removed `implemented=False` from `set_room_caption` (line 32)
- Removed `implemented=False` from `set_background_color` (line 57)
- Removed `implemented=False` from `set_background` (line 75)

---

## Testing

### Test File: `test_room_config.py`

**Test Coverage:**

#### set_room_caption (3 tests) ✅ ALL PASSED
- ✅ Basic caption text
- ✅ Caption with expression (parameter handling)
- ✅ Empty caption

#### set_room_speed (5 tests) ✅ ALL PASSED
- ✅ Set to 30 FPS
- ✅ Set to 60 FPS
- ✅ Lower bound test (< 1)
- ✅ Upper bound test (> 240)
- ✅ Default value

#### set_background_color (4 tests) ✅ ALL PASSED
- ✅ Set to red (#FF0000)
- ✅ Set to blue (#0000FF)
- ✅ Custom color (sky blue)
- ✅ Default color (black)

#### set_background (3 tests) ✅ ALL PASSED
- ✅ Set background with tiling
- ✅ Hide background
- ✅ Background with scrolling parameters

#### Integration (1 test) ✅ PASSED
- ✅ Multiple room configuration commands in sequence

**All 16 tests PASSED** ✅

---

## Auto-Discovery System

All four actions are automatically registered via ActionExecutor's auto-discovery:

```
✅ ActionExecutor initialized with 71 action handlers
  📌 Registered action handler: set_room_caption
  📌 Registered action handler: set_room_speed
  📌 Registered action handler: set_background_color
  📌 Registered action handler: set_background
```

Action count increased from **67 to 71 registered handlers**!

---

## Impact on 1.0 Release Roadmap

### Before Implementation
- Room Configuration: 4 lower-priority actions missing
- Missing: set_room_caption, set_room_speed, set_background_color, set_background
- Limited runtime room customization

### After Implementation
- Room Configuration: **4 lower-priority actions completed**
- Status: Ready for dynamic room configuration
- Roadmap Impact: Removes **LOWER priority** blockers for 1.0 release

---

## Game Use Cases

### 1. Level System with Captions
```python
# On room start
{
    "action": "set_room_caption",
    "parameters": {
        "caption": "Adventure Game - Dungeon Level 1"
    }
}
```

### 2. Slow-Motion Effect
```python
# When power-up activated
{
    "action": "set_room_speed",
    "parameters": {
        "speed": 15  # Half speed
    }
},
# After timeout, restore normal speed
{
    "action": "set_room_speed",
    "parameters": {
        "speed": 30  # Normal speed
    }
}
```

### 3. Day/Night Cycle
```python
# Daytime
{
    "action": "set_background_color",
    "parameters": {
        "color": "#87CEEB",  # Sky blue
        "show_color": True
    }
},
{
    "action": "set_background",
    "parameters": {
        "background": "bg_day_clouds",
        "visible": True,
        "tiled_h": True
    }
}

# Nighttime
{
    "action": "set_background_color",
    "parameters": {
        "color": "#001133",  # Dark blue
        "show_color": True
    }
},
{
    "action": "set_background",
    "parameters": {
        "background": "bg_night_stars",
        "visible": True,
        "tiled_h": True,
        "tiled_v": True
    }
}
```

### 4. Scrolling Clouds Background
```python
{
    "action": "set_background",
    "parameters": {
        "background": "bg_clouds",
        "visible": True,
        "tiled_h": True,
        "tiled_v": False,
        "hspeed": 0.5,  # Slow horizontal scroll
        "vspeed": 0
    }
}
```

### 5. Underwater Level
```python
{
    "action": "set_background_color",
    "parameters": {
        "color": "#0066AA",  # Ocean blue
        "show_color": True
    }
},
{
    "action": "set_background",
    "parameters": {
        "background": "bg_underwater",
        "visible": True,
        "tiled_h": True,
        "tiled_v": True
    }
},
{
    "action": "set_room_speed",
    "parameters": {
        "speed": 45  # Slightly slower for underwater feel
    }
}
```

### 6. Boss Fight Caption
```python
# When boss appears
{
    "action": "set_room_caption",
    "parameters": {
        "caption": "BOSS FIGHT: Dragon King"
    }
},
{
    "action": "set_background_color",
    "parameters": {
        "color": "#330000",  # Dark red
        "show_color": True
    }
}
```

---

## Technical Notes

### Caption System
- Caption combines with existing score/lives/health display
- Format: "[Custom Caption] | Score: X | Lives: Y"
- Updates via `game_runner.update_caption()`
- Set via `game_runner.window_caption`
- Simple string (no expression parsing to avoid issues with spaces)

### FPS System
- Stored in `game_runner.fps`
- Applied to `clock.tick(fps)` in game loop
- Clamped to 1-240 FPS range
- 30 FPS default (GameMaker standard)
- 60 FPS common for smooth gameplay

### Background Color System
- Stored in `current_room.background_color`
- RGB tuple format: `(r, g, b)`
- Hex color parsing: "#RRGGBB" → `(r, g, b)`
- Applied during `screen.fill(background_color)`
- `show_color` parameter for GM compatibility

### Background Image System
- Stored in `current_room.background_surface`
- Looks up from `sprites` or `backgrounds` assets
- Tiling flags: `tile_horizontal`, `tile_vertical`
- Tiling renders multiple copies to fill room
- Scrolling `hspeed`/`vspeed` acknowledged (future feature)
- Foreground layer acknowledged (future feature)

### Expression Parsing
- `set_room_speed`: Supports expressions (e.g., "30 + turbo * 30")
- `set_background_color`: Color parameter supports expressions
- `set_background`: All boolean/numeric parameters support expressions
- `set_room_caption`: No expression parsing (simple string)

### Performance
- All configuration changes apply immediately
- Background loading may have slight delay
- FPS changes affect next frame
- No performance overhead during gameplay

---

## Comparison with GameMaker Studio

### set_room_caption
**GameMaker Studio:**
```gml
room_caption = "My Game - Level 1";
```

**PyGameMaker:**
```json
{
    "action": "set_room_caption",
    "parameters": {
        "caption": "My Game - Level 1"
    }
}
```

✅ Feature parity achieved!

### set_room_speed
**GameMaker Studio:**
```gml
room_speed = 60;
```

**PyGameMaker:**
```json
{
    "action": "set_room_speed",
    "parameters": {
        "speed": 60
    }
}
```

✅ Feature parity achieved!

### set_background_color
**GameMaker Studio:**
```gml
background_color = c_blue;
background_showcolor = true;
```

**PyGameMaker:**
```json
{
    "action": "set_background_color",
    "parameters": {
        "color": "#0000FF",
        "show_color": true
    }
}
```

✅ Feature parity achieved!

### set_background
**GameMaker Studio:**
```gml
background_visible[0] = true;
background_index[0] = bg_sky;
background_htiled[0] = true;
background_vtiled[0] = false;
background_hspeed[0] = 1;
background_vspeed[0] = 0;
```

**PyGameMaker:**
```json
{
    "action": "set_background",
    "parameters": {
        "background": "bg_sky",
        "visible": true,
        "tiled_h": true,
        "tiled_v": false,
        "hspeed": 1,
        "vspeed": 0
    }
}
```

✅ Feature parity achieved (scrolling/foreground planned)!

---

## Future Enhancements

With these room configuration actions complete, additional enhancements could include:

1. **Background Scrolling Animation** (MEDIUM) - Implement `hspeed`/`vspeed` animation
2. **Foreground Layers** (MEDIUM) - Implement foreground drawing
3. **Multiple Background Layers** (LOW) - Support layers 0-7 like GameMaker
4. **set_room_persistent** (LOW) - Make rooms remember state
5. **View System** (LOW) - enable_views, set_view for cameras

---

## Conclusion

✅ Successfully implemented 4 lower-priority room configuration actions
✅ All tests passing (16/16)
✅ Auto-discovery integration working
✅ Ready for use in games
✅ Comprehensive documentation with examples

**Status:** Production-ready for PyGameMaker 1.0

**Total New Handlers:** 71 (was 67)
**Total New Code:** 168 lines in action_executor.py

---

## Action Handler Summary

| Action | Status | Lines | Tests |
|--------|--------|-------|-------|
| set_room_caption | ✅ IMPLEMENTED | 20 | 3/3 ✅ |
| set_room_speed | ✅ IMPLEMENTED | 27 | 5/5 ✅ |
| set_background_color | ✅ IMPLEMENTED | 23 | 4/4 ✅ |
| set_background | ✅ IMPLEMENTED | 80 | 3/3 ✅ |
| **Total** | **4/4 Complete** | **150** | **15/15 ✅** |

Plus 1 integration test (multiple commands) ✅

---

## Room Configuration Now Available in PyGameMaker

Users can now:
- 🏷️ Set custom window captions
- ⏱️ Adjust game speed dynamically (slow-motion, turbo mode)
- 🎨 Change background colors at runtime
- 🖼️ Set and configure background images with tiling
- 🎮 Create dynamic, responsive game environments

**PyGameMaker room configuration system is production-ready!** 🎮

---

## Notes

### Known Limitations
- Background scrolling (`hspeed`/`vspeed`) parameters acknowledged but not yet animated
- Foreground layer parameter acknowledged but not yet implemented
- Single background layer only (no multi-layer support yet)

### Compatibility
- All actions compatible with GameMaker 8.0 behavior
- Background system simplified compared to GM (single layer vs 8 layers)
- Caption system integrates with existing score/lives/health display

---

## Lower Priority Room Configuration Status

| Action | Status | Priority |
|--------|--------|----------|
| set_room_caption | ✅ COMPLETED | LOWER |
| set_room_speed | ✅ COMPLETED | LOWER |
| set_background_color | ✅ COMPLETED | LOWER |
| set_background | ✅ COMPLETED | LOWER |

**All lower-priority room configuration actions are now complete!** 🎉
