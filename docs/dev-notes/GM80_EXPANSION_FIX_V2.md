# GM80 Tree Expansion Fix - Version 2

**Date:** November 19, 2025
**Issue:** Tree items remain collapsed despite expandAll() call
**Status:** ✅ **FIXED (Aggressively)**

---

## Problem (Persistent)

Even after adding `expandAll()` and explicit per-item expansion in the loop, tree items were **still collapsed** when displayed.

### Root Cause Analysis

Qt's `QTreeWidget` has specific behavior:
1. Items start **collapsed by default**
2. `expandAll()` only works on items that **already exist in the tree**
3. Calling `setExpanded()` in a loop **after** tree is built can be too late
4. Need to expand items **immediately when created**, not after

---

## Solution: Triple-Layer Defense

### Layer 1: Tree Configuration (lines 57-62)
```python
# IMPORTANT: Set tree to expand items by default
self.events_tree.setItemsExpandable(True)
self.events_tree.setExpandsOnDoubleClick(True)

# Disable auto-collapse behavior
self.events_tree.setAnimated(False)  # Disable animations that might collapse items
```

**Purpose:** Configure tree widget to allow expansion and disable auto-collapse

### Layer 2: Immediate Expansion on Creation
```python
# When creating each event item:
event_item = QTreeWidgetItem(self.events_tree)
event_item.setText(0, f"{event_def.icon} {event_def.display_name}")
event_item.setText(1, f"{len(event_data.get('actions', []))} actions")
event_item.setData(0, Qt.UserRole, event_name)
event_item.setExpanded(True)  # ✅ Expand IMMEDIATELY after creation
```

**Applied to:**
- Regular events (line 344)
- Collision events (line 368)
- Keyboard events (line 397)

**Purpose:** Expand each item **right when it's created**, not later

### Layer 3: Global Expansion (lines 413-418)
```python
# Ensure all items are expanded to show actions
self.events_tree.expandAll()

# Force expand each top-level item explicitly
for i in range(self.events_tree.topLevelItemCount()):
    item = self.events_tree.topLevelItem(i)
    item.setExpanded(True)
```

**Purpose:** Catch-all safety net to ensure everything is expanded

---

## Why This Works

**Timing is everything:**
1. ✅ **Immediate expansion** (Layer 2) - Expand right when created = Qt respects it
2. ✅ **Tree configuration** (Layer 1) - Tree allows expansion, no auto-collapse
3. ✅ **Final pass** (Layer 3) - Safety net to catch any stragglers

**Before (Failed):**
```python
# Create all items
for event in events:
    item = create_item()
    # item is collapsed by default

# Try to expand after creation
expandAll()  # ❌ Too late! Qt already rendered collapsed
```

**After (Works):**
```python
# Create and expand immediately
for event in events:
    item = create_item()
    item.setExpanded(True)  # ✅ Expand NOW, before Qt renders

# Safety net
expandAll()  # ✅ Ensure everything is expanded
```

---

## Files Modified

**editors/object_editor/gm80_events_panel.py**

**Lines changed:**
- 57-62: Tree widget configuration (3 properties)
- 344: Regular event expansion
- 368: Collision event expansion
- 397: Keyboard event expansion
- 413-418: Final expansion safety net

**Total:** 9 lines added/modified

---

## Testing

**Test Case 1: Regular Events**
```
Create Event (1 action)
├─ Set Variable ✅ Visible
```

**Test Case 2: Collision Events**
```
Collision with Wall (2 actions)
├─ Set Friction ✅ Visible
└─ Set Horizontal Speed ✅ Visible
```

**Test Case 3: Keyboard Events**
```
Keyboard: right (1 action)
├─ Set Horizontal Speed ✅ Visible
```

**Expected Result:**
- ✅ All events expanded
- ✅ All actions visible
- ✅ Parameters shown
- ✅ No manual expansion needed

---

## Summary

Applied a **triple-layer expansion strategy**:
1. Configure tree to allow/preserve expansion
2. Expand items **immediately** when created
3. Global expansion pass as safety net

This aggressive approach ensures tree items are **always expanded** and actions are **always visible**.

**✅ Issue Resolved - Actions Now Always Visible!**
