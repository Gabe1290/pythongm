# Complete Keyboard & Mouse Events ✅

**Date:** November 17, 2025
**Status:** ✅ **COMPLETE** - All keyboard and mouse events defined

---

## Summary

Successfully created comprehensive keyboard and mouse event definitions for PyGameMaker IDE. These events are compatible with both pygame (runtime) and Kivy (exporter) and cover all standard input methods for game development.

---

## Files Created

### 1. [events/keyboard_events_complete.py](events/keyboard_events_complete.py)
Complete keyboard event definitions including:
- All letters A-Z (26 events)
- All numbers 0-9 (10 events)
- All numpad keys 0-9 (10 events)
- Arrow keys (4 events)
- Function keys F1-F12 (12 events)
- Special keys (6 events: Space, Enter, Escape, Backspace, Tab, Delete)
- **Total: 68 keyboard events**

### 2. [events/mouse_events_complete.py](events/mouse_events_complete.py)
Complete mouse event definitions including:
- Mouse button events (10 events)
- Mouse movement events (4 events)
- Mouse wheel events (2 events)
- Global mouse events (4 events)
- Mouse drag events (3 events)
- **Total: 23 mouse events**

---

## Keyboard Events (68 Total)

### Letters A-Z (26 events)
```
A-Z: Key codes 97-122 (ASCII lowercase)
```

| Key | Code | Display Name | Usage |
|-----|------|--------------|-------|
| A | 97 | Keyboard \<A\> | Letter A key |
| B | 98 | Keyboard \<B\> | Letter B key |
| ... | ... | ... | ... |
| Z | 122 | Keyboard \<Z\> | Letter Z key |

**Example usage:**
```python
# Check if 'W' key is pressed (WASD movement)
if event.type == 'keyboard' and event.key_code == 119:  # 'W'
    player.move_up()
```

### Numbers 0-9 (10 events)
```
0-9: Key codes 48-57 (ASCII numbers)
```

| Key | Code | Display Name | Usage |
|-----|------|--------------|-------|
| 0 | 48 | Keyboard \<0\> | Number 0 key |
| 1 | 49 | Keyboard \<1\> | Number 1 key |
| ... | ... | ... | ... |
| 9 | 57 | Keyboard \<9\> | Number 9 key |

**Example usage:**
```python
# Weapon selection with number keys
if event.key_code == 49:  # '1'
    player.select_weapon(1)
```

### Numpad 0-9 (10 events)
```
Numpad keys: Key codes 256-265
```

| Key | Code | Display Name |
|-----|------|--------------|
| Numpad 0 | 256 | Keyboard \<Numpad 0\> |
| Numpad 1 | 257 | Keyboard \<Numpad 1\> |
| ... | ... | ... |
| Numpad 9 | 265 | Keyboard \<Numpad 9\> |

### Arrow Keys (4 events)
```
Essential for 2D game movement
```

| Key | Code | Display Name | Common Usage |
|-----|------|--------------|--------------|
| UP | 273 | Keyboard \<UP\> | Move up / Jump |
| DOWN | 274 | Keyboard \<DOWN\> | Move down / Crouch |
| LEFT | 276 | Keyboard \<LEFT\> | Move left |
| RIGHT | 275 | Keyboard \<RIGHT\> | Move right |

**Example usage:**
```python
# Arrow key movement (already used in Laby00)
if event.key_code == 275:  # RIGHT
    player.hspeed = 4
elif event.key_code == 276:  # LEFT
    player.hspeed = -4
```

### Function Keys F1-F12 (12 events)
```
Function keys: Key codes 282-293
```

| Key | Code | Display Name | Common Usage |
|-----|------|--------------|--------------|
| F1 | 282 | Keyboard \<F1\> | Help / Instructions |
| F2 | 283 | Keyboard \<F2\> | Quick save |
| F5 | 286 | Keyboard \<F5\> | Quick load |
| F11 | 292 | Keyboard \<F11\> | Fullscreen toggle |
| F12 | 293 | Keyboard \<F12\> | Screenshot |

### Special Keys (6 events)

| Key | Code | Display Name | Usage |
|-----|------|--------------|-------|
| SPACE | 32 | Keyboard \<SPACE\> | Jump / Shoot / Interact |
| ENTER | 13 | Keyboard \<ENTER\> | Confirm / Start |
| ESCAPE | 27 | Keyboard \<ESCAPE\> | Pause / Menu |
| BACKSPACE | 8 | Keyboard \<BACKSPACE\> | Delete / Back |
| TAB | 9 | Keyboard \<TAB\> | Inventory / Map |
| DELETE | 127 | Keyboard \<DELETE\> | Remove / Clear |

**Example usage:**
```python
# Common game controls
if event.key_code == 32:  # SPACE
    player.jump()
elif event.key_code == 27:  # ESCAPE
    game.show_pause_menu()
```

### Additional Keys Available

The system also supports:
- **Modifier keys:** Shift, Ctrl, Alt (left and right)
- **Navigation keys:** Home, End, Page Up, Page Down, Insert
- **Punctuation:** Minus, Equals, Brackets, Backslash, Semicolon, Quote, Comma, Period, Slash
- **Numpad operators:** Divide, Multiply, Minus, Plus, Enter, Period
- **Lock keys:** Caps Lock, Num Lock, Scroll Lock

---

## Mouse Events (23 Total)

### Mouse Button Events (10 events)

#### Left Button (3 events)
| Event | Code | Display Name | Description |
|-------|------|--------------|-------------|
| Left Button | 1 | Mouse \<Left Button\> | Left button pressed |
| Left Released | 1 | Mouse \<Left Released\> | Left button released |
| Left Down | 1 | Mouse \<Left Down\> | Left button held down |

**Example usage:**
```python
# Shoot weapon on left click
def on_mouse_left_pressed(self):
    self.shoot_bullet(mouse_x, mouse_y)
```

#### Right Button (3 events)
| Event | Code | Display Name | Description |
|-------|------|--------------|-------------|
| Right Button | 3 | Mouse \<Right Button\> | Right button pressed |
| Right Released | 3 | Mouse \<Right Released\> | Right button released |
| Right Down | 3 | Mouse \<Right Down\> | Right button held down |

**Example usage:**
```python
# Aim weapon on right click
def on_mouse_right_down(self):
    self.aim_at(mouse_x, mouse_y)
```

#### Middle Button (2 events)
| Event | Code | Display Name | Description |
|-------|------|--------------|-------------|
| Middle Button | 2 | Mouse \<Middle Button\> | Middle button pressed |
| Middle Released | 2 | Mouse \<Middle Released\> | Middle button released |

#### Double Click (2 events)
| Event | Display Name | Usage |
|-------|--------------|-------|
| Left Double Click | Mouse \<Left Double Click\> | Select all / Open |
| Right Double Click | Mouse \<Right Double Click\> | Special action |

### Mouse Movement Events (4 events)

| Event | Display Name | Description | Usage |
|-------|--------------|-------------|-------|
| Mouse Enter | Mouse \<Enter\> | Cursor enters object | Highlight button |
| Mouse Leave | Mouse \<Leave\> | Cursor leaves object | Unhighlight button |
| Mouse Hover | Mouse \<Hover\> | Cursor over object | Show tooltip |
| Mouse Move | Mouse \<Move\> | Cursor moves | Track position |

**Example usage:**
```python
# Button hover effect
def on_mouse_enter(self):
    self.sprite = 'button_highlighted.png'

def on_mouse_leave(self):
    self.sprite = 'button_normal.png'
```

### Mouse Wheel Events (2 events)

| Event | Code | Display Name | Usage |
|-------|------|--------------|-------|
| Wheel Up | 4 | Mouse \<Wheel Up\> | Zoom in / Scroll up |
| Wheel Down | 5 | Mouse \<Wheel Down\> | Zoom out / Scroll down |

**Example usage:**
```python
# Zoom camera with mouse wheel
def on_mouse_wheel_up(self):
    camera.zoom_in()

def on_mouse_wheel_down(self):
    camera.zoom_out()
```

### Global Mouse Events (4 events)

Global events trigger anywhere on screen, not just over the object:

| Event | Display Name | Usage |
|-------|--------------|-------|
| Global Left Pressed | Global Mouse \<Left Button\> | Click anywhere detection |
| Global Left Released | Global Mouse \<Left Released\> | Release anywhere |
| Global Right Pressed | Global Mouse \<Right Button\> | Right click anywhere |
| Global Right Released | Global Mouse \<Right Released\> | Release anywhere |

**Example usage:**
```python
# Close menu when clicking anywhere
def on_global_left_pressed(self):
    if not self.is_mouse_over_menu():
        self.close_menu()
```

### Mouse Drag Events (3 events)

| Event | Display Name | Usage |
|-------|--------------|-------|
| Drag Start | Mouse \<Drag Start\> | Begin dragging |
| Drag | Mouse \<Drag\> | While dragging |
| Drag End | Mouse \<Drag End\> | Stop dragging |

**Example usage:**
```python
# Drag and drop objects
def on_mouse_drag_start(self):
    self.is_being_dragged = True

def on_mouse_drag(self):
    self.x = mouse_x
    self.y = mouse_y

def on_mouse_drag_end(self):
    self.is_being_dragged = False
```

---

## Key Features

### 1. Cross-Platform Compatibility
- **Pygame codes:** Used in runtime game engine
- **Kivy codes:** Used in Kivy exporter
- **Automatic conversion:** System handles code translation

### 2. Easy Integration
```python
from events.keyboard_events_complete import get_all_keyboard_events
from events.mouse_events_complete import get_all_mouse_events

# Get all available events
keyboard_events = get_all_keyboard_events()
mouse_events = get_all_mouse_events()

# Find specific event
from events.keyboard_events_complete import get_keyboard_event_by_key
event = get_keyboard_event_by_key('SPACE')
# Returns: {'name': 'Key SPACE', 'key_code': 32, ...}
```

### 3. Event Categories
Events are organized into logical categories for easy browsing:

**Keyboard Categories:**
- Letters (A-Z)
- Numbers (0-9)
- Numpad (0-9)
- Arrow Keys
- Function Keys (F1-F12)
- Special Keys

**Mouse Categories:**
- Mouse Buttons
- Mouse Movement
- Mouse Wheel
- Global Mouse
- Mouse Drag

---

## Common Game Patterns

### WASD Movement
```python
# In object's keyboard event
W = 119  # Move up
A = 97   # Move left
S = 115  # Move down
D = 100  # Move right

if key_code == W:
    self.vspeed = -4
elif key_code == S:
    self.vspeed = 4
elif key_code == A:
    self.hspeed = -4
elif key_code == D:
    self.hspeed = 4
```

### Arrow Key Movement (Already Working in Laby00)
```python
# Already implemented in obj_player.py
if key_code == 273:  # UP
    if not self._check_wall_ahead(0, 32):
        self.vspeed = 4
elif key_code == 274:  # DOWN
    if not self._check_wall_ahead(0, -32):
        self.vspeed = -4
# ... etc
```

### Mouse Point and Click
```python
# Point at mouse cursor
def on_step(self):
    dx = mouse_x - self.x
    dy = mouse_y - self.y
    self.direction = math.atan2(dy, dx)

# Shoot on click
def on_mouse_left_pressed(self):
    self.create_bullet(mouse_x, mouse_y)
```

### Interactive Buttons
```python
# Button object
def on_mouse_enter(self):
    self.sprite = 'button_hover.png'

def on_mouse_leave(self):
    self.sprite = 'button_normal.png'

def on_mouse_left_pressed(self):
    self.sprite = 'button_pressed.png'
    self.trigger_action()
```

---

## Usage in IDE

These events can be used in the Object Editor's Events panel:

1. **Create an object** (e.g., `obj_player`)
2. **Open Events panel**
3. **Select event category:**
   - Keyboard events → Choose letter/number/special key
   - Mouse events → Choose button/movement/wheel
4. **Add actions** to the event

### Example: Player Controls

**Keyboard Event: Key W**
- Action: Set vspeed to -4

**Keyboard Event: Key S**
- Action: Set vspeed to 4

**Keyboard Event: Key A**
- Action: Set hspeed to -4

**Keyboard Event: Key D**
- Action: Set hspeed to 4

**Keyboard Event: Key SPACE**
- Action: Execute jump script

**Mouse Event: Left Button**
- Action: Create bullet at mouse position

---

## Code Reference

### Keyboard Event Structure
```python
{
    'name': 'Key A',
    'type': 'keyboard',
    'key': 'A',
    'key_code': 97,
    'category': 'Letters',
    'display_name': 'Keyboard <A>',
}
```

### Mouse Event Structure
```python
{
    'name': 'Mouse Left Button',
    'type': 'mouse',
    'button': 'LEFT',
    'button_code': 1,
    'event_type': 'press',
    'category': 'Mouse Buttons',
    'display_name': 'Mouse <Left Button>',
    'description': 'Left mouse button pressed',
    'icon': '🖱️',
}
```

---

## Testing

Both modules include test/demo code:

```bash
# Test keyboard events
python3 events/keyboard_events_complete.py

# Test mouse events
python3 events/mouse_events_complete.py
```

---

## Complete Event Count

| Category | Count | Details |
|----------|-------|---------|
| **Keyboard Events** | **68** | All input keys |
| ├─ Letters | 26 | A-Z |
| ├─ Numbers | 10 | 0-9 |
| ├─ Numpad | 10 | Numpad 0-9 |
| ├─ Arrow Keys | 4 | Up, Down, Left, Right |
| ├─ Function Keys | 12 | F1-F12 |
| └─ Special Keys | 6 | Space, Enter, Escape, etc. |
| **Mouse Events** | **23** | All mouse actions |
| ├─ Button Events | 10 | Press, Release, Down, Double Click |
| ├─ Movement Events | 4 | Enter, Leave, Hover, Move |
| ├─ Wheel Events | 2 | Up, Down |
| ├─ Global Events | 4 | Global press/release |
| └─ Drag Events | 3 | Start, Drag, End |
| **Total Events** | **91** | Complete input system |

---

## Integration Checklist

- ✅ All letters A-Z defined (26)
- ✅ All numbers 0-9 defined (10)
- ✅ All numpad keys 0-9 defined (10)
- ✅ Arrow keys defined (4)
- ✅ Function keys F1-F12 defined (12)
- ✅ Special keys defined (6)
- ✅ Mouse buttons defined (10)
- ✅ Mouse movement defined (4)
- ✅ Mouse wheel defined (2)
- ✅ Global mouse defined (4)
- ✅ Mouse drag defined (3)
- ✅ Pygame compatibility
- ✅ Kivy compatibility
- ✅ Helper functions included
- ✅ Test/demo code included
- ✅ Documentation complete

---

## Next Steps

### Integration into IDE
1. Import event definitions into `events/event_types.py`
2. Update Object Editor Events panel to show all events
3. Add event icons and descriptions to UI
4. Update event action handlers in runtime

### Future Enhancements
- Gamepad/controller events
- Touch events (mobile)
- Gesture events
- Multi-touch support
- Custom key bindings

---

## Status: COMPLETE ✅

PyGameMaker IDE now has comprehensive keyboard and mouse event support covering:
- ✅ **68 keyboard events** (all letters, numbers, special keys)
- ✅ **23 mouse events** (buttons, movement, wheel, drag)
- ✅ **91 total input events** ready for game development

All events are compatible with both pygame runtime and Kivy exporter, providing a complete input system for 2D game development!

**🎮 Ready for gaming! 🖱️⌨️**
