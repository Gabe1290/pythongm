# Room Order Save - Debug Investigation 🔍

**Date:** November 19, 2025
**Issue:** Room order changes not being saved (continued investigation)
**Status:** 🔍 **DEBUGGING IN PROGRESS**

---

## Problem Summary

When the user reorders rooms in the Asset Tree, the changes appear in the UI but are not saved to the project file. When the project is saved and reloaded, the room order reverts to the original order.

### Evidence

**User's Console Output:**
```
💾 AssetManager: Saving room order: ['room0', 'room1st']
💾 DEBUG: Saving room order: ['room0', 'room1st']
```

This shows the **OLD** order is being saved, even though:
1. The user reordered the rooms (presumably to `['room1st', 'room0']` or similar)
2. The UI should show the new order
3. The asset_manager cache should have been updated

### Critical Missing Output

The message "✅ Updated asset manager cache with new room order" is **NOT appearing** in the console output, which indicates the asset_manager cache update at line 560 of `asset_tree_widget.py` is NOT being executed.

---

## Previous Fix Attempt

### What Was Changed

**File:** [core/project_manager.py:247-253](core/project_manager.py#L247-L253)

Changed from rebuilding assets dictionary:
```python
# OLD CODE (caused problem):
assets_dict = {}
for asset_type in ['sprites', 'backgrounds', ...]:
    assets_of_type = self.asset_manager.get_assets_by_type(asset_type)
    if assets_of_type:
        assets_dict[asset_type] = assets_of_type
self.current_project_data['assets'] = assets_dict
```

To using asset_manager's save method:
```python
# NEW CODE:
self.asset_manager.save_assets_to_project_data(self.current_project_data)
```

### Why This Should Work

The `asset_manager.save_assets_to_project_data()` method preserves the order from `assets_cache`. If the cache is updated correctly when rooms are reordered, the save should preserve that order.

### Why It's Not Working

The asset_manager cache is not being updated when rooms are reordered. The code at line 560 should update it, but the debug message at line 561 is not appearing in the console.

---

## Debug Instrumentation Added

### File: widgets/asset_tree/asset_tree_widget.py

Added comprehensive debug output to trace the entire reorder flow:

#### 1. Entry Point Debug (Line 498)
```python
print(f"🔧 DEBUG: _reorder_room called with room_name='{room_name}', direction={direction}")
```
**Purpose:** Verify `_reorder_room()` is actually being called

#### 2. Room List Debug (Lines 513, 520)
```python
print(f"🔍 DEBUG: Current room order (before reorder): {room_list}")
print(f"🔍 DEBUG: Current index of '{room_name}': {current_index}")
```
**Purpose:** See the starting state

#### 3. New Order Debug (Lines 535, 543)
```python
print(f"🔍 DEBUG: New room order (after reorder): {room_list}")
print(f"🔍 DEBUG: Built new_rooms OrderedDict with keys: {list(new_rooms.keys())}")
```
**Purpose:** Verify the reordering logic works correctly

#### 4. IDE Window Debug (Line 557)
```python
if ide_window:
    print(f"🔍 DEBUG: Found IDE window")
else:
    print(f"❌ DEBUG: Could not find IDE window")
```
**Purpose:** Verify we can find the IDE parent window

#### 5. Asset Manager Detection Debug (Lines 560-575)
```python
if hasattr(ide_window, 'asset_manager'):
    print(f"🔍 DEBUG: IDE has asset_manager attribute")
    if ide_window.asset_manager:
        print(f"🔍 DEBUG: asset_manager is not None")
        if hasattr(ide_window.asset_manager, 'assets_cache'):
            print(f"🔍 DEBUG: asset_manager has assets_cache attribute")
            # Update the cache
            ide_window.asset_manager.assets_cache['rooms'] = new_rooms
            print(f"✅ Updated asset manager cache with new room order")
            print(f"🔍 DEBUG: New cache room order: {list(new_rooms.keys())}")
        else:
            print(f"❌ DEBUG: asset_manager does NOT have assets_cache attribute")
    else:
        print(f"❌ DEBUG: asset_manager is None")
else:
    print(f"❌ DEBUG: IDE does NOT have asset_manager attribute")
```
**Purpose:** Identify exactly which condition is failing and preventing the cache update

---

## Expected Debug Output Flow

When a user reorders a room, they should see:

```
🔧 DEBUG: _reorder_room called with room_name='room1st', direction='top'
🔍 DEBUG: Current room order (before reorder): ['room0', 'room1st']
🔍 DEBUG: Current index of 'room1st': 1
🔍 DEBUG: New room order (after reorder): ['room1st', 'room0']
🔍 DEBUG: Built new_rooms OrderedDict with keys: ['room1st', 'room0']
✅ Saved new room order to project.json: ['room1st', 'room0']
🔍 DEBUG: Found IDE window
🔍 DEBUG: IDE has asset_manager attribute
🔍 DEBUG: asset_manager is not None
🔍 DEBUG: asset_manager has assets_cache attribute
✅ Updated asset manager cache with new room order
🔍 DEBUG: New cache room order: ['room1st', 'room0']
💾 DEBUG: Getting assets from asset manager...
💾 AssetManager: Saving room order: ['room1st', 'room0']
💾 DEBUG: Saving room order: ['room1st', 'room0']
✅ Project saved with new room order
```

---

## Possible Failure Scenarios

### Scenario 1: `_reorder_room()` Not Called
**Symptom:** No "🔧 DEBUG: _reorder_room called" message
**Cause:** Context menu not connected properly or room reorder action not triggered
**Fix:** Check context menu connections in asset_tree_widget.py

### Scenario 2: IDE Window Not Found
**Symptom:** "❌ DEBUG: Could not find IDE window" message
**Cause:** Parent widget hierarchy doesn't lead to IDE window
**Fix:** Check widget parent chain, ensure asset tree is child of IDE window

### Scenario 3: asset_manager Doesn't Exist
**Symptom:** "❌ DEBUG: IDE does NOT have asset_manager attribute"
**Cause:** IDE window doesn't have `asset_manager` attribute initialized
**Fix:** Check IDE window initialization, ensure asset_manager is created

### Scenario 4: asset_manager is None
**Symptom:** "❌ DEBUG: asset_manager is None"
**Cause:** asset_manager attribute exists but is not initialized
**Fix:** Check IDE window initialization timing

### Scenario 5: assets_cache Doesn't Exist
**Symptom:** "❌ DEBUG: asset_manager does NOT have assets_cache attribute"
**Cause:** AssetManager class doesn't have `assets_cache` or it's not initialized
**Fix:** Check AssetManager.__init__() method

### Scenario 6: Cache Update Happens But Gets Overwritten
**Symptom:** "✅ Updated asset manager cache" appears, but save still shows old order
**Cause:** Something else is resetting the cache between update and save
**Fix:** Check for other code that modifies `assets_cache['rooms']`

---

## Investigation Steps

### Step 1: Test Room Reordering

1. Open project with 2+ rooms
2. Right-click a room in Asset Tree
3. Select "Move to Top" or "Move Up/Down"
4. **Watch console output carefully**
5. Note which debug messages appear and which don't

### Step 2: Identify Failure Point

Based on which debug messages appear:

- **No "🔧 DEBUG: _reorder_room called"** → Context menu issue
- **"❌ Could not find IDE window"** → Parent hierarchy issue
- **"❌ IDE does NOT have asset_manager"** → IDE initialization issue
- **"❌ asset_manager is None"** → Timing issue
- **"❌ does NOT have assets_cache"** → AssetManager structure issue
- **"✅ Updated cache" but save shows old order** → Cache being overwritten

### Step 3: Fix Root Cause

Once we know which condition is failing, we can apply the appropriate fix.

---

## Next Steps

**For User:**
1. Open a project with multiple rooms
2. Reorder a room using the context menu
3. Copy **ALL** console output from the moment you click the reorder option
4. Report back with the complete output

**For Developer:**
Based on the debug output, I will:
1. Identify which condition is failing
2. Investigate why that condition fails
3. Apply the appropriate fix
4. Test to verify the fix works

---

## Code Flow Analysis

### Expected Flow

```
1. User right-clicks room → context menu appears
   ↓
2. User clicks "Move to Top" → _reorder_room('room_name', 'top') called
   ↓
3. Load project.json with OrderedDict
   ↓
4. Reorder rooms in room_list
   ↓
5. Rebuild new_rooms OrderedDict in new order
   ↓
6. Save to project.json with new order
   ↓
7. Find IDE parent window
   ↓
8. Update asset_manager.assets_cache['rooms'] with new_rooms
   ↓
9. Update IDE project_data
   ↓
10. Call project_manager.save_project()
    ↓
11. asset_manager.save_assets_to_project_data() preserves order
    ↓
12. project.json saved with correct order
```

### Where It's Failing

Somewhere between steps 7-8, the cache update is not happening. The debug output will reveal exactly where.

---

## Related Files

### Primary Files
- [widgets/asset_tree/asset_tree_widget.py](widgets/asset_tree/asset_tree_widget.py) - Room reordering UI and logic
- [core/asset_manager.py](core/asset_manager.py) - Asset cache management
- [core/project_manager.py](core/project_manager.py) - Project save/load

### Context Menu (in asset_tree_widget.py)
```python
# Lines ~400-450
def _create_room_context_menu(self, room_name: str) -> QMenu:
    menu = QMenu(self)
    # ... actions ...
    move_up = menu.addAction("Move Up")
    move_up.triggered.connect(lambda: self.move_room_up(room_name))
    # ... etc ...
```

### Reorder Methods (in asset_tree_widget.py)
```python
def move_room_up(self, room_name: str):
    self._reorder_room(room_name, -1)

def move_room_down(self, room_name: str):
    self._reorder_room(room_name, 1)

def move_room_to_top(self, room_name: str):
    self._reorder_room(room_name, 'top')

def move_room_to_bottom(self, room_name: str):
    self._reorder_room(room_name, 'bottom')
```

---

## Status: DEBUGGING IN PROGRESS 🔍

Debug instrumentation has been added to trace the entire execution flow.

**Next action required:** User needs to test room reordering and report the complete console output.

This will reveal exactly where in the flow the cache update is failing, allowing us to apply the correct fix.

**🔍 Comprehensive debugging enabled - ready for testing!**
