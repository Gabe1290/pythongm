# GM80 Click-to-Expand Fix

**Date:** November 19, 2025
**Issue:** Cannot click on events to expand/collapse actions
**Status:** ✅ **FIXED**

---

## Problem

Users could not **click on event items** to expand/collapse the actions list. The tree items were set to expanded by default, but clicking on them did nothing.

### Expected Behavior
- Click on "Step (1 actions)" → Toggles expand/collapse
- Click on "Collision with Wall (2 actions)" → Toggles expand/collapse

### Actual Behavior
- Clicking on events did nothing
- No visual feedback
- Actions remained in fixed expanded/collapsed state

---

## Root Cause

The tree widget had a `itemDoubleClicked` signal connected, but **no `itemClicked` signal handler**. Users expect **single-click to toggle**, not double-click.

**Missing:**
```python
# No handler for single-click!
self.events_tree.itemClicked.connect(???)
```

---

## Solution

### Added Single-Click Handler (line 56)
```python
self.events_tree.itemClicked.connect(self.on_item_clicked)  # Handle single-click
```

### Created Click Handler Method (lines 317-324)
```python
def on_item_clicked(self, item: QTreeWidgetItem, column: int):
    """Handle single-click - toggle expand/collapse for events"""
    if not item:
        return

    # Only toggle expand/collapse if this is an event item (has children)
    if item.childCount() > 0:
        item.setExpanded(not item.isExpanded())
```

**Logic:**
1. User clicks on an event item
2. Check if item has children (actions)
3. If yes, toggle expanded state
4. Visual feedback: tree expands/collapses

### Updated Double-Click Handler (lines 326-335)
```python
def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
    """Handle double-click - edit actions"""
    if not item:
        return

    item_data = item.data(0, Qt.UserRole)

    if isinstance(item_data, dict) and "action" in item_data:
        # Edit action
        self.edit_action(item)
```

**Changed behavior:**
- **Before:** Double-click toggles expand/collapse
- **After:** Double-click **edits action** (more useful!)

---

## User Experience

### Single-Click (Toggle)
```
User clicks "Step (1 actions)"
└─ Tree toggles expanded/collapsed ✅
```

### Double-Click (Edit)
```
User double-clicks "Set Horizontal Speed"
└─ Action dialog opens for editing ✅
```

### Result
- ✅ **Single-click** = Expand/collapse event
- ✅ **Double-click** = Edit action
- ✅ Intuitive, standard tree widget behavior

---

## Files Modified

**editors/object_editor/gm80_events_panel.py**

**Changes:**
- Line 56: Connected `itemClicked` signal
- Lines 317-324: Added `on_item_clicked()` method
- Lines 326-335: Updated `on_item_double_clicked()` to only edit actions

**Total:** 11 lines added/modified

---

## Testing

**Test Case 1: Click Event Item**
1. Click on "Step (1 actions)"
2. Expected: Tree collapses (actions hidden)
3. Click again
4. Expected: Tree expands (actions visible)

**Test Case 2: Double-Click Action**
1. Double-click "Set Horizontal Speed"
2. Expected: Action dialog opens
3. Can edit parameters
4. Click OK
5. Expected: Dialog closes, changes saved

**Test Case 3: Right-Click**
1. Right-click on event
2. Expected: Context menu appears
3. Can add/remove actions

---

## Summary

Added **single-click to toggle expand/collapse** behavior to event tree items. This provides:

- ✅ Intuitive interaction (click to expand/collapse)
- ✅ Standard tree widget UX
- ✅ Double-click to edit actions
- ✅ Better user experience overall

**✅ Events Now Toggle on Click!**
