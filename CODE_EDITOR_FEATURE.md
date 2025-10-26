# Code Editor Feature Implementation ✅

**Date:** November 18, 2025
**Feature:** Code Editor Tab and View Code Checkbox
**Status:** ✅ **IMPLEMENTED**

---

## Overview

The Object Editor now includes:
1. **Code Editor Tab** - View generated Python/Kivy code
2. **View Code Checkbox** - Auto-update code view as you edit events
3. **Proper Code Generation** - Translates visual events to readable Python code

---

## Features Implemented

### 1. Code Editor Tab ✅

**Location:** Object Editor → Center Panel → "💻 Code Editor" tab

**Features:**
- Read-only code view with monospace font
- Syntax-friendly styling (light background, dark text)
- Shows Python/Kivy equivalent of visual events
- Updates automatically when View Code is enabled

**UI:**
```
[📋 Event List] [🎨 Visual Programming] [💻 Code Editor]
                                          ↑ NOW ENABLED
```

### 2. View Code Checkbox ✅

**Location:** Object Editor → Object Properties Panel → Below other checkboxes

**Layout:**
```
Object Properties
┌─────────────────────────┐
│ Sprite: [dropdown]      │
│ ☐ Visible               │
│ ☐ Persistent            │
│ ☐ Solid                 │
│ ☐ View Code  ← NEW!     │
└─────────────────────────┘
```

**Behavior:**
- **Unchecked (default)**: Code editor shows placeholder text
- **Checked**: Automatically generates and displays code
- **Auto-update**: Code regenerates whenever you modify events

### 3. Code Generation System ✅

**Generates Python/Kivy code from visual events:**

#### Example: Keyboard Events

**Visual Events:**
```
Keyboard → Key: W
  └─ Set vspeed: -4

Keyboard → Key: S
  └─ Set vspeed: 4
```

**Generated Code:**
```python
def on_keyboard(self, key, game):
    """Keyboard event - fires while key is held"""
    if key == 'W':
        self.vspeed = -4

    if key == 'S':
        self.vspeed = 4
```

#### Example: Collision Events

**Visual Events:**
```
Collision with obj_diamond
  └─ Destroy Instance (target: other)

Collision with obj_wall
  └─ Stop Movement
  └─ Snap to Grid (32)
```

**Generated Code:**
```python
def on_collision_obj_diamond(self, other, game):
    """Collision with obj_diamond"""
    other.destroy()

def on_collision_obj_wall(self, other, game):
    """Collision with obj_wall"""
    self.hspeed = 0
    self.vspeed = 0
    self.x = round(self.x / 32) * 32
    self.y = round(self.y / 32) * 32
```

#### Example: Step Event with Grid Logic

**Visual Events:**
```
Step
  └─ If On Grid (32)
      └─ Stop If No Keys
```

**Generated Code:**
```python
def step(self, game):
    """Step event - fires every frame"""
    if (self.x % 32 == 0) and (self.y % 32 == 0):
        # Check if any arrow keys are pressed
        if not any(game.keys.get(k) for k in ['left', 'right', 'up', 'down']):
            self.hspeed = 0
            self.vspeed = 0
```

---

## Supported Actions

The code generator handles all major action types:

| Action | Generated Code |
|--------|----------------|
| `set_hspeed` | `self.hspeed = value` |
| `set_vspeed` | `self.vspeed = value` |
| `stop_movement` | `self.hspeed = 0; self.vspeed = 0` |
| `snap_to_grid` | `self.x = round(self.x / grid) * grid; self.y = ...` |
| `destroy_instance (self)` | `self.destroy()` |
| `destroy_instance (other)` | `other.destroy()` |
| `if_on_grid` | `if (self.x % grid == 0) and (self.y % grid == 0):` |
| `stop_if_no_keys` | `if not any(game.keys.get(k) for k in [...]): ...` |
| `show_message` | `print('message')` |
| `next_room` | `game.next_room()` |
| `restart_room` | `game.restart_room()` |

---

## Event Types Supported

### Keyboard Events

**Event Types:**
- `keyboard` - Continuous (while held)
- `keyboard_press` - Once on press
- `keyboard_release` - Once on release

**Generated Methods:**
```python
def on_keyboard(self, key, game):
    """Keyboard event - fires while key is held"""

def on_keyboard_press(self, key, game):
    """Keyboard press event - fires once when key pressed"""

def on_keyboard_release(self, key, game):
    """Keyboard release event - fires once when key released"""
```

### Step Event

```python
def step(self, game):
    """Step event - fires every frame"""
```

### Collision Events

```python
def on_collision_obj_name(self, other, game):
    """Collision with obj_name"""
```

### Mouse Events

```python
def on_mouse_left_press(self, game):
    """Mouse event: mouse_left_press"""
```

---

## How It Works

### 1. User Workflow

**Basic Usage:**
1. Open object in Object Editor
2. Add events and actions in Object Events panel
3. Check "View Code" checkbox
4. Code appears in Code Editor tab
5. As you add/modify events, code updates automatically

**View Code Button (Toolbar):**
- Click "📋 View Code" button in toolbar
- Generates code and switches to Code Editor tab
- Same as checking "View Code" checkbox

### 2. Technical Implementation

#### Files Modified

**[editors/object_editor/object_properties_panel.py](editors/object_editor/object_properties_panel.py:77-90)**
- Added `view_code_checkbox` below existing checkboxes
- Emits `property_changed` signal with `'view_code'` and boolean value

**[editors/object_editor/object_editor_main.py](editors/object_editor/object_editor_main.py)**
- **Line 48**: Initialize `self.view_code_enabled = False`
- **Lines 319-360**: Enable Code Editor tab with proper styling
- **Lines 742-748**: Handle `view_code` property change
- **Lines 881-883**: Auto-update code when events modified
- **Lines 889-1073**: Complete code generation system

#### Code Generation Flow

```
User checks "View Code"
    ↓
on_property_changed('view_code', True)
    ↓
view_generated_code(auto_switch_tab=True)
    ↓
events_panel.get_events_data()
    ↓
For each event:
    _generate_event_code()
        ↓
    For each action:
        _generate_action_code()
    ↓
code_editor.setText(code)
    ↓
Switch to Code Editor tab
```

#### Auto-Update Flow

```
User adds/modifies event
    ↓
events_panel.events_modified.emit()
    ↓
on_events_modified()
    ↓
if view_code_enabled:
    view_generated_code(auto_switch_tab=False)
    ↓
Code updates without switching tabs
```

---

## Code Structure

### Generated Class Structure

```python
# Generated Python/Kivy code for obj_player
# This code is automatically generated from your events

from game.objects.base_object import GameObject

class obj_player(GameObject):
    """Object: obj_player"""

    def on_keyboard(self, key, game):
        """Keyboard event - fires while key is held"""
        if key == 'right':
            self.hspeed = 4
        # ... other keys

    def step(self, game):
        """Step event - fires every frame"""
        if (self.x % 32 == 0) and (self.y % 32 == 0):
            # ... grid logic

    def on_collision_obj_diamond(self, other, game):
        """Collision with obj_diamond"""
        other.destroy()

    # ... other events
```

---

## Benefits

### 1. Learning Tool
- See Python/Kivy equivalent of visual events
- Understand how GameMaker concepts map to code
- Learn programming while using visual editor

### 2. Debugging Aid
- Verify logic visually as code
- Spot issues in event flow
- Understand execution order

### 3. Code Reference
- Copy generated code for custom scripts
- Understand Kivy game object structure
- See how actions translate to code

### 4. Transparency
- No "magic" - see exactly what happens
- Understand the export process
- Bridge between visual and text programming

---

## Limitations

### Read-Only Code
- Generated code is **read-only**
- Cannot edit code directly (future feature)
- Changes must be made through visual events

### Code Accuracy
- Code is representative, not exact
- Actual export may differ slightly
- Shows Python/Kivy equivalent, not GML

### Simplified Representation
- Some complex actions shown as comments
- Plugin actions may show generic representation
- Focus on readability over exact export code

---

## Future Enhancements

Possible improvements:

### 1. Syntax Highlighting
- Color-code Python keywords
- Highlight strings, numbers
- Better visual distinction

### 2. Code Editing
- Edit code directly in Code Editor
- Sync changes back to visual events
- Two-way synchronization

### 3. Copy/Export Code
- Right-click to copy code
- Export as .py file
- Share code snippets

### 4. Code Comparison
- Compare generated code between objects
- See differences when debugging
- Code diff view

### 5. Custom Code Blocks
- Insert custom Python code
- Mix visual and text programming
- Advanced user features

---

## Testing

### Test Case 1: Basic Events

**Setup:**
1. Create object `obj_test`
2. Add keyboard event: W → Set vspeed -4
3. Check "View Code"

**Expected:**
```python
def on_keyboard(self, key, game):
    """Keyboard event - fires while key is held"""
    if key == 'W':
        self.vspeed = -4
```

**Result:** ✅ Pass

### Test Case 2: Auto-Update

**Setup:**
1. Object with existing events
2. Check "View Code"
3. Add new action to event

**Expected:**
- Code updates immediately
- No need to regenerate manually
- Stays on current tab (doesn't switch)

**Result:** ✅ Pass

### Test Case 3: Complex Logic

**Setup:**
1. Create grid movement with if_on_grid
2. Add stop_if_no_keys
3. Check "View Code"

**Expected:**
```python
if (self.x % 32 == 0) and (self.y % 32 == 0):
    if not any(game.keys.get(k) for k in ['left', 'right', 'up', 'down']):
        self.hspeed = 0
        self.vspeed = 0
```

**Result:** ✅ Pass

---

## User Guide

### How to Use View Code

**Step 1: Open Object Editor**
- Double-click object in Asset Tree
- Or create new object

**Step 2: Add Events**
- Click "Add Event" in Object Events panel
- Choose event type
- Add actions to event

**Step 3: Enable View Code**
- Check "View Code" checkbox in Object Properties
- Or click "📋 View Code" toolbar button

**Step 4: View Generated Code**
- Switch to "💻 Code Editor" tab
- Code shows Python/Kivy equivalent
- Code updates as you edit events

**Step 5: Understanding the Code**
- Each event becomes a method
- Actions become Python statements
- Comments explain complex logic

---

## Status: COMPLETE ✅

All features implemented and working:
- ✅ Code Editor tab enabled and functional
- ✅ View Code checkbox added to properties panel
- ✅ Comprehensive code generation for all action types
- ✅ Auto-update when events modified
- ✅ Proper styling and monospace font
- ✅ Handles keyboard, mouse, collision, step events
- ✅ Clean, readable Python/Kivy code output

**🎨 Visual programming just got more transparent! 💻**
