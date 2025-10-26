# Kivy Exporter - Critical Bugs Found

**Date:** November 15, 2025
**Status:** ❌ Multiple critical bugs preventing proper grid-based movement

---

## Summary

During testing of the Laby00 game export, several critical bugs were discovered that prevent grid-based movement from working correctly. The player does not stop on grid positions as expected.

---

## Bug #1: Missing Grid Check Action in Keyboard Events ❌

**Problem:** When exporting keyboard events with movement actions, the exporter doesn't include the grid alignment check that GameMaker uses.

**Location:** Keyboard event code generation in `_generate_event_methods()`

**Current Behavior:**
```python
def on_keyboard(self, key, scancode, codepoint, modifier):
    if key == 275:  # right
        self.hspeed = 4.0  # ❌ Starts moving immediately!
```

**Expected Behavior:**
```python
def on_keyboard(self, key, scancode, codepoint, modifier):
    if key == 275:  # right
        if self.is_on_grid():  # ✓ Only start if on grid
            self.hspeed = 4.0
```

**Root Cause:** The keyboard event generator doesn't automatically wrap movement actions with grid checks.

---

## Bug #2: Incorrect `stop_if_no_keys` Action Implementation ✅ FIXED

**Problem:** The `stop_if_no_keys` action checked if the entire keys dictionary was empty instead of checking specific arrow keys.

**Location:** `export/Kivy/kivy_exporter.py` line 1269-1270

**Before:**
```python
elif action_type == 'stop_if_no_keys':
    return "if not self.scene.keys_pressed: self.stop_movement()"
```

**After (FIXED):**
```python
elif action_type == 'stop_if_no_keys':
    return """if not (self.scene.keys_pressed.get(275, False) or self.scene.keys_pressed.get(276, False) or self.scene.keys_pressed.get(273, False) or self.scene.keys_pressed.get(274, False)):
        self.snap_to_grid()
        self.hspeed = 0
        self.vspeed = 0"""
```

**Status:** ✅ Fixed in exporter

---

## Bug #3: Grid Alignment Check Not Wrapping Actions ❌

**Problem:** The `if_on_grid` action exists (line 1250) but doesn't automatically wrap subsequent actions. It just generates `if self.is_on_grid():` without proper indentation handling for the actions that follow.

**Location:** Action block generation

**Current Structure:**
```python
# Action 1: if_on_grid
if self.is_on_grid():
# Action 2: stop_if_no_keys
if not (self.scene.keys_pressed.get...):  # ❌ Not indented under if_on_grid!
```

**Expected Structure:**
```python
# Action 1: if_on_grid (with nested actions)
if self.is_on_grid():
    # Action 2: stop_if_no_keys (properly indented)
    if not (self.scene.keys_pressed.get...):
        self.snap_to_grid()
```

**Root Cause:** The exporter doesn't implement proper block/scope handling for conditional actions like `if_on_grid`, `start_block`, `else_action`.

---

## Bug #4: Keyboard Event Grid Check Missing ❌

**Problem:** Generated keyboard events don't include grid alignment checks before allowing movement.

**Location:** `_generate_keyboard_handler()` method (around line 1034-1060)

**Current Generated Code:**
```python
def on_keyboard(self, key, scancode, codepoint, modifier):
    if key == 275:  # right
        self.hspeed = 4.0
```

**Should Generate:**
```python
def on_keyboard(self, key, scancode, codepoint, modifier):
    if key == 275:  # right
        if self.is_on_grid():
            self.hspeed = 4.0
```

---

## Bug #5: Action Indentation Not Handled ❌

**Problem:** The exporter doesn't properly track indentation levels when generating nested actions (blocks, conditionals, etc.).

**Location:** `_generate_action_code()` method

**Evidence:** Looking at line 1143:
```python
complex_actions = ['if_on_grid', 'if_collision', 'if_key_pressed', 'repeat', 'while']
```

These are marked as "complex" but there's no proper indentation/block handling code.

---

## Recommended Fixes

### Option 1: Quick Fix (Hardcode Grid Movement Logic)

Update keyboard event generation to always include grid checks for movement:

```python
def _generate_keyboard_handler(self, keyboard_events: List[Dict]) -> str:
    # ... existing code ...
    for event in keyboard_events:
        key_name = event.get('key_name', '')
        actions = event.get('actions', [])

        # Check if actions include movement
        has_movement = any(a.get('action_type') in ['set_hspeed', 'set_vspeed', 'move_fixed']
                          for a in actions)

        if has_movement:
            code_lines.append(f"        if self.is_on_grid():")
            action_code = self._generate_action_code(obj_name, actions, event)
            # Indent all action lines
            code_lines.append(f"            {action_code}")
        else:
            action_code = self._generate_action_code(obj_name, actions, event)
            code_lines.append(f"        {action_code}")
```

### Option 2: Proper Fix (Implement Block/Scope Handling)

Implement a proper indentation tracking system:

```python
class ActionCodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.lines = []

    def add_line(self, code):
        indent = "    " * self.indent_level
        self.lines.append(f"{indent}{code}")

    def push_indent(self):
        self.indent_level += 1

    def pop_indent(self):
        self.indent_level = max(0, self.indent_level - 1)
```

Then handle complex actions:
```python
if action_type == 'if_on_grid':
    gen.add_line("if self.is_on_grid():")
    gen.push_indent()
    # Process nested actions
    gen.pop_indent()
```

---

## Workaround for Users

Until these bugs are fixed, users can manually edit the generated `obj_player.py`:

```python
def on_keyboard(self, key, scancode, codepoint, modifier):
    """Handle keyboard press events"""
    if key == 275:  # right
        if self.is_on_grid():  # ✓ Add this check
            self.hspeed = 4.0
    elif key == 276:  # left
        if self.is_on_grid():  # ✓ Add this check
            self.hspeed = -4.0
    elif key == 273:  # up
        if self.is_on_grid():  # ✓ Add this check
            self.vspeed = -4.0
    elif key == 274:  # down
        if self.is_on_grid():  # ✓ Add this check
            self.vspeed = 4.0

def on_update(self, dt):
    """Event handler: step"""
    if self.is_on_grid():  # ✓ Use is_on_grid() instead of modulo
        self.snap_to_grid()  # ✓ Snap to exact position
        if not (self.scene.keys_pressed.get(275, False) or
                self.scene.keys_pressed.get(276, False) or
                self.scene.keys_pressed.get(273, False) or
                self.scene.keys_pressed.get(274, False)):
            self.hspeed = 0
            self.vspeed = 0
```

---

## Testing Checklist

After fixes are applied:

- [ ] Export a project with grid-based movement
- [ ] Player should only start moving when aligned to grid
- [ ] Player should stop on grid when no keys pressed
- [ ] Player should snap to exact grid position when stopping
- [ ] Verify `is_on_grid()` works with tolerance (4.5 pixels)
- [ ] Verify keyboard events include grid checks
- [ ] Verify step events properly check grid alignment

---

## Files Modified So Far

1. ✅ `export/Kivy/kivy_exporter.py` line 1269-1274 - Fixed `stop_if_no_keys` action
2. ✅ `export/Kivy/kivy_exporter.py` line 816-830 - Fixed `is_on_grid()` to use tolerance
3. ❌ Keyboard event generation - Still needs fixing
4. ❌ Action block/indentation handling - Still needs implementation

---

## Impact

**Current State:** Grid-based movement games exported to Kivy are **broken** - players don't stop on grid.

**Affected Projects:** Any game using:
- Grid-based movement (like Pac-Man, Sokoban, roguelikes)
- Step-based movement
- Tile-based games

**Severity:** 🔴 **CRITICAL** - Core feature of GameMaker-style games doesn't work

---

## Next Steps

**Immediate (Quick Fix):**
1. Update keyboard event generator to always add `if self.is_on_grid():` for movement actions
2. Test with Laby00 project
3. Verify player stops on grid

**Long-term (Proper Fix):**
1. Implement proper block/scope/indentation tracking system
2. Support nested conditionals, blocks, and loops
3. Refactor action code generation to use new system
4. Update all complex actions (if_on_grid, start_block, repeat, while, etc.)

---

**Priority:** 🔴 URGENT - Should be fixed before any users rely on Kivy export
