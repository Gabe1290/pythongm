# GM80 Missing Actions Fix

**Date:** November 19, 2025
**Issue:** Actions not visible in Object Editor events tree
**Status:** ✅ **FIXED**

---

## Problem

When loading a project with events, the tree showed correct action **counts** but the actual action items were **invisible**:

### User Report:
- **Keyboard events:** "no actions visible" (but game works)
- **Step event:** "says 1 action but not shown"
- **Collision with Wall:** "says 2 actions but only displays one action"
- **Create:** OK
- **Collision with diamond:** OK

---

## Root Cause

The issue had **THREE separate causes**:

### Cause 1: Wrong Handler Order for Keyboard Events

The keyboard event handler was placed AFTER the regular event handler in the if/elif chain. Since `get_event("keyboard")` returns a valid event definition, keyboard events were caught by the regular handler which tried to get actions from `event_data.get('actions', [])`. But keyboard events store actions in a nested structure: `{"right": {"actions": [...]}}`, not directly under the event.

**Result:** Keyboard event showed "0 actions" because the regular handler couldn't find actions at the top level.

**Fix:** Moved keyboard event check to FIRST position in the if/elif chain (before regular events).

### Cause 2: Missing Action Definitions

The project used custom actions that were **not defined** in `gm80_actions.py`:
- `if_on_grid` - Control action for grid-based movement
- `stop_if_no_keys` - Control action to stop when no keys pressed
- `stop_movement` - Movement action to stop all motion

When `get_action(action_name)` was called for these actions, it returned `None`, causing the `if action_def:` check to fail and skip creating the action tree item.

**Evidence from project.json:**
```json
{
  "keyboard": {
    "right": {
      "actions": [
        {
          "action": "if_on_grid",  // ❌ NOT DEFINED
          "parameters": {
            "grid_size": 32,
            "then_actions": [...]
          }
        }
      ]
    }
  },
  "step": {
    "actions": [
      {
        "action": "if_on_grid",  // ❌ NOT DEFINED
        "parameters": {...}
      }
    ]
  },
  "collision_with_obj_wall": {
    "actions": [
      {
        "action": "stop_movement",  // ❌ NOT DEFINED
        "parameters": {}
      },
      {
        "action": "snap_to_grid",  // ✅ DEFINED
        "parameters": {"grid_size": 32}
      }
    ]
  }
}
```

**Result:**
- Action count: 1 (counts from JSON)
- Actions displayed: 0 (because `get_action()` returns None)

### Cause 3: Missing Parameters in Collision Events

The collision event handler was not displaying action parameters, making it appear as if parameters were missing.

**Code comparison:**

**Regular events (lines 360-364):** ✅ Parameters displayed
```python
params = action_data.get("parameters", {})
if params:
    param_str = ", ".join(f"{k}={v}" for k, v in params.items())
    action_item.setText(1, param_str)
```

**Collision events (old code):** ❌ Parameters missing
```python
action_item = QTreeWidgetItem(event_item)
action_item.setText(0, f"{action_def.icon} {action_def.display_name}")
action_item.setData(0, Qt.UserRole, action_data)
# No parameter display!
```

---

## Solution

### Fix 1: Reorder Event Handler Priority

Changed the order of event type checks in `refresh_display()` method ([gm80_events_panel.py](editors/object_editor/gm80_events_panel.py#L344-L378)):

**Before (broken):**
```python
for event_name, event_data in self.current_events_data.items():
    event_def = get_event(event_name)

    if event_def:  # ❌ Keyboard caught here
        # Regular event handler
        # Looks for actions at event_data['actions']
        # But keyboard has nested structure!
    elif event_name.startswith("collision_with_"):
        # Collision handler
    elif event_name in ["keyboard", ...]:  # ❌ Never reached!
        # Keyboard handler
```

**After (fixed):**
```python
for event_name, event_data in self.current_events_data.items():
    # ✅ Check keyboard FIRST
    if event_name in ["keyboard", "keyboard_press", "keyboard_release"]:
        # Handle nested structure: {"right": {"actions": [...]}}
        for key_name, key_data in event_data.items():
            # Create separate tree items for each key
    elif event_name.startswith("collision_with_"):
        # Collision handler
    else:
        # Regular event handler (fallback)
        event_def = get_event(event_name)
```

### Fix 2: Add Missing Action Definitions

Added three new action definitions to `gm80_actions.py` (lines 307-338):

```python
"stop_movement": ActionDefinition(
    name="stop_movement",
    display_name="Stop Movement",
    category="movement",
    tab="move",
    description="Stop all movement (set speed to 0)",
    icon="🛑",
    parameters=[]
),
"if_on_grid": ActionDefinition(
    name="if_on_grid",
    display_name="If On Grid",
    category="control",
    tab="control",
    description="Execute actions if aligned to grid",
    icon="⊞",
    parameters=[
        ActionParameter("grid_size", "int", "Grid Size", "Grid cell size in pixels", default=32),
        ActionParameter("then_actions", "actions", "Then Actions", "Actions to execute if on grid", default=[])
    ]
),
"stop_if_no_keys": ActionDefinition(
    name="stop_if_no_keys",
    display_name="Stop If No Keys",
    category="control",
    tab="control",
    description="Stop movement if no arrow keys are pressed",
    icon="⌨️🛑",
    parameters=[
        ActionParameter("grid_size", "int", "Grid Size", "Grid to snap to when stopping", default=32)
    ]
),
```

**Why these actions:**
- `stop_movement` - Essential for collision response (stops object when hitting wall)
- `if_on_grid` - Common pattern for grid-based games (only allow actions when aligned)
- `stop_if_no_keys` - Keyboard control helper (stop when player releases keys)

### Fix 3: Add Parameters to Collision Events

Updated collision event handler in `gm80_events_panel.py` (lines 384-388):

```python
# Add actions
for action_data in event_data.get("actions", []):
    action_def = get_action(action_data["action"])
    if action_def:
        action_item = QTreeWidgetItem(event_item)
        action_item.setText(0, f"{action_def.icon} {action_def.display_name}")

        # Format parameters
        params = action_data.get("parameters", {})
        if params:
            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
            action_item.setText(1, param_str)

        action_item.setData(0, Qt.UserRole, action_data)
```

---

## Expected Result

### Before (Broken):
```
Events Tree:
├─ ⌨️ Keyboard (0 actions)                ← Says 0 actions (wrong!)
├─ ⚡ Step (1 action)                      ← Says 1 action
│                                          ← But nothing shown!
└─ 💥 Collision with obj_wall (2 actions) ← Says 2 actions
   └─ ⚡ Snap to Grid                      ← Only 1 shown!
```

### After (Fixed):
```
Events Tree:
├─ ⌨️ Keyboard (4 keys)                                ✅ Parent event
│  ├─ right (1 action)                                 ✅ Grouped by key
│  │  └─ ⊞ If On Grid (grid_size=32, ...)
│  ├─ left (1 action)
│  │  └─ ⊞ If On Grid (grid_size=32, ...)
│  ├─ up (1 action)
│  │  └─ ⊞ If On Grid (grid_size=32, ...)
│  └─ down (1 action)
│     └─ ⊞ If On Grid (grid_size=32, ...)
├─ ⚡ Step (1 action)
│  └─ ⊞ If On Grid (grid_size=32, then_actions=[...])  ✅
└─ 💥 Collision with obj_wall (2 actions)
   ├─ 🛑 Stop Movement                                  ✅
   └─ ⚡ Snap to Grid (grid_size=32)                    ✅
```

---

## Files Modified

### 1. actions/gm80_actions.py
**Lines 307-338:** Added 3 new action definitions
- `stop_movement` - Stop all movement
- `if_on_grid` - Conditional grid alignment check
- `stop_if_no_keys` - Stop when no keys pressed

### 2. editors/object_editor/gm80_events_panel.py

**Lines 344-388:** Reordered event handler priority with hierarchical structure
- Keyboard events checked FIRST (before regular events)
- Creates parent "Keyboard" item with child items for each key
- Hierarchical structure: Keyboard → keys (right, left, up, down) → actions
- Handles nested action structure properly

**Lines 396-400:** Added parameter display to collision events
- Format parameters as `key=value` string
- Display in column 1 of tree item

---

## Testing

**Test Project:** `/home/gabe/Dropbox/pygm2/Projects/Laby00/project.json`

**Test Object:** `obj_player`

**Test Events:**
1. **Keyboard: right** - Should show "If On Grid" action with parameters
2. **Keyboard: left** - Should show "If On Grid" action with parameters
3. **Step** - Should show "If On Grid" action with nested actions
4. **Collision with obj_wall** - Should show both "Stop Movement" and "Snap to Grid"

**Expected:**
- ✅ All actions visible
- ✅ All parameters shown
- ✅ Action counts match displayed items
- ✅ Tree items expanded by default

---

## Impact

**For Users:**
- ✅ All actions now visible in event tree
- ✅ Keyboard events grouped hierarchically with collapsible parent
- ✅ Individual keys shown as children (right, left, up, down)
- ✅ Grid-based movement actions supported
- ✅ Collision event parameters displayed
- ✅ No more "ghost actions" (count but not shown)
- ✅ Cleaner, more organized event tree structure

**For Developers:**
- Clean action definitions with proper parameters
- Consistent parameter display across all event types
- Extensible pattern for adding custom actions

---

## Summary

Fixed missing actions in Object Editor by:
1. **Reordering event handlers** - Keyboard events checked FIRST to prevent being caught by regular event handler
2. **Adding missing action definitions** - `if_on_grid`, `stop_if_no_keys`, `stop_movement` for grid-based movement
3. **Adding parameter display** - Collision events now show action parameters

This resolves the issue where:
- Keyboard events showed "0 actions" (now shows hierarchical structure with grouped keys)
- Action counts were correct but actions were invisible (now all actions display properly)
- Parameters were missing from collision events (now displayed)
- Event tree was cluttered with multiple top-level keyboard items (now organized under parent)

**✅ All Actions Now Visible and Properly Displayed!**
