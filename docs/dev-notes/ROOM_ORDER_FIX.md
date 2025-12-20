# Room Order Save Fix ✅

**Date:** November 18, 2025
**Issue:** Room order changes not being saved
**Status:** ✅ **FIXED**

---

## Problem Description

When the user reordered rooms in the Asset Tree (using "Move Up", "Move Down", "Move to Top", "Move to Bottom"), the changes appeared in the UI but were not saved to the project file. When running the game, it would use the old room order.

### Example Scenario
- Project has rooms: room1, room2, room3
- User moves room3 to top
- UI shows: room3, room1, room2
- User saves project
- Room order in project.json reverts to: room1, room2, room3
- Game still starts with room1

---

## Root Cause

The issue was in the `project_manager.py` save method. When saving the project:

**File:** [core/project_manager.py](core/project_manager.py:244-253)

**Original Code:**
```python
# Get latest asset data from asset manager
if self.asset_manager:
    print("💾 DEBUG: Getting assets from asset manager...")
    assets_dict = {}
    for asset_type in ['sprites', 'backgrounds', 'sounds', 'objects', 'rooms', 'scripts', 'fonts']:
        assets_of_type = self.asset_manager.get_assets_by_type(asset_type)
        if assets_of_type:
            assets_dict[asset_type] = assets_of_type

    self.current_project_data['assets'] = assets_dict
```

### The Problem

1. **Hardcoded Asset Type Order**: The code iterated through asset types in a fixed order
2. **Rebuilt Assets Dictionary**: Created a NEW `assets_dict` from scratch
3. **Lost OrderedDict**: Even though asset_manager stored rooms as OrderedDict with correct order, rebuilding the dict lost the order information
4. **Overwrote Correct Data**: The rebuilt `assets_dict` overwrote the correctly-ordered data that was set by the room reorder operation

### What Was Happening

```
1. User reorders rooms:
   - asset_tree_widget._reorder_room() updates:
     - project.json file ✅
     - asset_manager.assets_cache['rooms'] ✅
     - project_manager.current_project_data ✅

2. User saves project (or auto-save triggers):
   - project_manager.save_project() rebuilds assets_dict
   - Iterates asset types in hardcoded order
   - Gets each type from asset_manager
   - OVERWRITES current_project_data['assets'] with rebuilt dict ❌
   - Loses the room order that was set in step 1 ❌

3. Result:
   - Room order reverts to whatever order the asset_manager had before reordering
   - Changes appear lost
```

---

## The Fix

### Updated Code

**File:** [core/project_manager.py:244-248](core/project_manager.py#L244-L248)

**Before:**
```python
# Get latest asset data from asset manager
if self.asset_manager:
    print("💾 DEBUG: Getting assets from asset manager...")
    assets_dict = {}
    for asset_type in ['sprites', 'backgrounds', 'sounds', 'objects', 'rooms', 'scripts', 'fonts']:
        assets_of_type = self.asset_manager.get_assets_by_type(asset_type)
        if assets_of_type:
            assets_dict[asset_type] = assets_of_type

    self.current_project_data['assets'] = assets_dict
```

**After:**
```python
# Get latest asset data from asset manager
if self.asset_manager:
    print("💾 DEBUG: Getting assets from asset manager...")
    # Use save_assets_to_project_data to preserve order
    self.asset_manager.save_assets_to_project_data(self.current_project_data)
```

### Why This Works

The `asset_manager.save_assets_to_project_data()` method:

**File:** [core/asset_manager.py:437-451](core/asset_manager.py#L437-L451)

```python
def save_assets_to_project_data(self, project_data: Dict[str, Any]) -> None:
    """Save assets to project JSON data preserving order"""
    from collections import OrderedDict

    # Convert OrderedDict to regular dict for JSON serialization
    # but maintain the order by reconstructing from items()
    assets_for_json = {}
    for asset_type, assets_of_type in self.assets_cache.items():
        if isinstance(assets_of_type, OrderedDict):
            # Preserve order by converting to list of tuples, then back to dict
            assets_for_json[asset_type] = dict(assets_of_type.items())
        else:
            assets_for_json[asset_type] = assets_of_type

    project_data["assets"] = assets_for_json
```

**Key points:**
1. **Iterates through assets_cache directly** - Preserves the order that's already in the cache
2. **Uses dict(items())** - In Python 3.7+, this preserves insertion order
3. **Respects OrderedDict** - Specifically handles OrderedDict types
4. **Single source of truth** - Uses the asset_manager's cache as the authoritative source

---

## How Room Ordering Works Now

### 1. User Reorders Rooms

**File:** [widgets/asset_tree/asset_tree_widget.py:496-567](widgets/asset_tree/asset_tree_widget.py#L496-L567)

```python
def _reorder_room(self, room_name: str, direction):
    """Reorder rooms in project data and save"""
    # 1. Load project.json with order preservation
    with open(project_file, 'r') as f:
        project_data = json.load(f, object_pairs_hook=OrderedDict)

    # 2. Get rooms and current order
    rooms = project_data.get('assets', {}).get('rooms', OrderedDict())
    room_list = list(rooms.keys())

    # 3. Calculate new order
    # ... reordering logic ...

    # 4. Rebuild rooms OrderedDict in new order
    new_rooms = OrderedDict()
    for room_key in room_list:
        new_rooms[room_key] = rooms[room_key]

    project_data['assets']['rooms'] = new_rooms

    # 5. Save to project.json immediately
    with open(project_file, 'w') as f:
        json.dump(project_data, f, indent=2, sort_keys=False)

    # 6. Update asset_manager cache
    ide_window.asset_manager.assets_cache['rooms'] = new_rooms

    # 7. Update project_manager data
    ide_window.project_manager.current_project_data = project_data

    # 8. Mark dirty and save
    ide_window.project_manager.mark_dirty()
    ide_window.project_manager.save_project()
```

### 2. Project Manager Saves

**File:** [core/project_manager.py:233-277](core/project_manager.py#L233-L277)

```python
def _save_to_folder(self, project_path: Optional[Path] = None) -> bool:
    """Save project to folder"""
    # ... setup ...

    # Get latest asset data from asset manager (FIXED)
    if self.asset_manager:
        # Use save_assets_to_project_data to preserve order
        self.asset_manager.save_assets_to_project_data(self.current_project_data)

    # Save to file
    with open(project_file, 'w', encoding='utf-8') as f:
        json.dump(self.current_project_data, f, indent=2,
                  ensure_ascii=False, sort_keys=False)
```

**Key:** `sort_keys=False` ensures JSON doesn't re-sort keys

### 3. Loading Preserves Order

**File:** [core/asset_manager.py:420-430](core/asset_manager.py#L420-L430)

```python
def load_assets_from_project_data(self, project_data: Dict[str, Any]) -> None:
    """Load assets from project JSON data"""
    from collections import OrderedDict

    self.assets_cache = {}
    assets = project_data.get("assets", {})

    # Preserve order for ALL asset types using OrderedDict
    for asset_type, asset_dict in assets.items():
        # Use OrderedDict to preserve insertion order from JSON
        self.assets_cache[asset_type] = OrderedDict(asset_dict)
```

---

## Complete Flow

### Reordering and Saving Flow

```
1. User reorders room
   ↓
2. asset_tree_widget._reorder_room()
   ├─ Reorders rooms in OrderedDict
   ├─ Saves to project.json (with order)
   ├─ Updates asset_manager.assets_cache['rooms'] (with order)
   └─ Updates project_manager.current_project_data (with order)
   ↓
3. project_manager.save_project() called
   ↓
4. project_manager._save_to_folder()
   ├─ Calls asset_manager.save_assets_to_project_data()
   │  └─ Preserves OrderedDict structure
   ├─ Saves to JSON with sort_keys=False
   └─ Room order preserved! ✅
```

### Loading Flow

```
1. Load project.json
   ↓
2. asset_manager.load_assets_from_project_data()
   ├─ Wraps assets in OrderedDict
   └─ Preserves order from JSON
   ↓
3. Room order maintained! ✅
```

---

## Testing

### Test Case 1: Basic Reorder

**Steps:**
1. Create project with 3 rooms: room_a, room_b, room_c
2. Right-click room_c → "Move to Top"
3. Save project
4. Close and reopen project

**Expected:**
- Room order in UI: room_c, room_a, room_b
- Room order in project.json: room_c, room_a, room_b
- Game starts with room_c

**Result:** ✅ Pass

### Test Case 2: Multiple Reorders

**Steps:**
1. Start with: room1, room2, room3, room4
2. Move room4 up → room1, room2, room4, room3
3. Move room2 down → room1, room4, room2, room3
4. Move room1 to bottom → room4, room2, room3, room1
5. Save project
6. Close and reopen

**Expected:**
- Final order: room4, room2, room3, room1
- Order persists across save/load

**Result:** ✅ Pass

### Test Case 3: Edit and Reorder

**Steps:**
1. Start with: room_a, room_b
2. Edit room_a (change background)
3. Move room_b to top
4. Save project
5. Reopen

**Expected:**
- Room order: room_b, room_a
- room_a changes preserved
- Both changes saved

**Result:** ✅ Pass

---

## Technical Details

### OrderedDict vs dict

**Python 3.7+:**
- Regular `dict` maintains insertion order
- `OrderedDict` explicitly guarantees insertion order
- Both work, but `OrderedDict` is more explicit

**Why we use OrderedDict:**
- Explicit intent to preserve order
- Compatible with older Python versions (future-proof)
- Clear signal to other developers

### JSON Serialization

**Key Settings:**
```python
json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=False)
```

- `indent=2` - Pretty formatting
- `ensure_ascii=False` - Allow unicode characters
- `sort_keys=False` - **CRITICAL** - Don't sort keys alphabetically

**Loading:**
```python
json.load(f, object_pairs_hook=OrderedDict)
```

- `object_pairs_hook=OrderedDict` - Preserve order from JSON

---

## Related Code

### Asset Tree Widget

**Room ordering methods:**
- `move_room_up(room_name)` - Move one position up
- `move_room_down(room_name)` - Move one position down
- `move_room_to_top(room_name)` - Move to first position
- `move_room_to_bottom(room_name)` - Move to last position

**Context menu:**
```python
# Right-click room in asset tree shows:
Move Up       (if not first)
Move Down     (if not last)
Move to Top   (if not first)
Move to Bottom (if not last)
```

---

## Breaking Changes

**None.** This is a bug fix that makes room ordering work as expected.

Existing projects will load correctly. Room orders that were "stuck" will now be able to be changed and saved properly.

---

## Future Enhancements

Possible improvements:

### 1. Drag and Drop Reordering
- Drag rooms in asset tree to reorder
- Visual feedback during drag
- Drop between rooms to insert

### 2. Batch Reordering
- Select multiple rooms
- Reorder as group
- Keyboard shortcuts (Ctrl+Up/Down)

### 3. Room Order Dialog
- Separate dialog for managing room order
- List view with up/down buttons
- Preview of current order

### 4. First Room Indicator
- Highlight first room (game starting room)
- Option to set any room as first
- Visual indicator in asset tree

---

## Status: FIXED ✅

Room order changes now:
- ✅ Save correctly to project.json
- ✅ Persist across save/load cycles
- ✅ Work with all reorder operations (up, down, top, bottom)
- ✅ Preserve order when editing other assets
- ✅ Respect the order when running games

**🎮 Room order now works perfectly! 🏠**
