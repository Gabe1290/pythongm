# Testing Preset Checklist

This checklist covers all events and actions available in the "Testing (Validated Only)" Blockly preset.
Use this to systematically verify that each feature works correctly in the runtime.

## Test Project Setup

Before testing, create a simple project with:
- [ ] At least 2 rooms (Room1, Room2) for room navigation testing
- [ ] An object with a sprite (e.g., "obj_player" with "spr_player")
- [ ] A solid wall object (e.g., "obj_wall" with "spr_wall", marked as solid)
- [ ] A collectible object (e.g., "obj_coin" with "spr_coin")

---

## EVENTS

### Create Event
- [ ] Add Create event to obj_player
- [ ] Add an action (e.g., set_hspeed to 0)
- [ ] Verify action executes when game starts
- [ ] Verify action executes when instance is created dynamically

### Step Event
- [ ] Add Step event to obj_player
- [ ] Add an action that runs every frame (e.g., snap_to_grid)
- [ ] Verify action executes continuously during gameplay
- [ ] Verify step event runs at correct frame rate

### Keyboard (Held) Event
- [ ] Add Keyboard > Arrow Keys > UP event
- [ ] Add set_vspeed action with value -4
- [ ] Test: Hold UP key, verify continuous movement
- [ ] Add Keyboard > Arrow Keys > DOWN event
- [ ] Add set_vspeed action with value 4
- [ ] Test: Hold DOWN key, verify continuous movement
- [ ] Add Keyboard > Arrow Keys > LEFT event
- [ ] Add set_hspeed action with value -4
- [ ] Test: Hold LEFT key, verify continuous movement
- [ ] Add Keyboard > Arrow Keys > RIGHT event
- [ ] Add set_hspeed action with value 4
- [ ] Test: Hold RIGHT key, verify continuous movement

### No Key Event
- [ ] Add Keyboard > No Key event
- [ ] Add stop_movement action
- [ ] Test: Release all keys, verify movement stops

### Collision Event
- [ ] Add Collision with obj_wall event to obj_player
- [ ] Add stop_movement action
- [ ] Test: Move player into wall, verify collision stops movement
- [ ] Add Collision with obj_coin event to obj_player
- [ ] Add destroy_instance action (target: other)
- [ ] Test: Move player into coin, verify coin is destroyed

---

## MOVEMENT ACTIONS

### Set Horizontal Speed (set_hspeed)
- [ ] Set hspeed to positive value (e.g., 4) - verify moves right
- [ ] Set hspeed to negative value (e.g., -4) - verify moves left
- [ ] Set hspeed to 0 - verify horizontal movement stops
- [ ] Test with expression (e.g., "other.hspeed") in collision event

### Set Vertical Speed (set_vspeed)
- [ ] Set vspeed to positive value (e.g., 4) - verify moves down
- [ ] Set vspeed to negative value (e.g., -4) - verify moves up
- [ ] Set vspeed to 0 - verify vertical movement stops
- [ ] Test with expression (e.g., "other.vspeed") in collision event

### Stop Movement (stop_movement)
- [ ] Add to No Key event - verify stops when keys released
- [ ] Add to Collision event - verify stops on collision
- [ ] Verify both hspeed and vspeed become 0

### Snap to Grid (snap_to_grid)
- [ ] Set grid size to 32
- [ ] Move instance off-grid, trigger snap
- [ ] Verify instance aligns to nearest 32x32 grid position
- [ ] Test with different grid sizes (16, 64)

### Jump to Position (jump_to_position)
- [ ] Jump to absolute position (x=100, y=100)
- [ ] Verify instance teleports to exact position
- [ ] Jump with relative=true (x=32, y=0)
- [ ] Verify instance moves 32 pixels right from current position
- [ ] Test with expressions (x="self.x + 32")

### Jump to Start Position (jump_to_start)
- [ ] Move instance away from starting position
- [ ] Trigger jump_to_start action
- [ ] Verify instance returns to original room placement position

### Jump to Random Position (jump_to_random)
- [ ] Trigger action multiple times
- [ ] Verify instance moves to different random positions
- [ ] Test with snap_h=32, snap_v=32
- [ ] Verify positions align to 32x32 grid

### If On Grid (if_on_grid)
- [ ] Place instance on grid (e.g., x=64, y=64)
- [ ] Add if_on_grid check followed by an action
- [ ] Verify action executes when on grid
- [ ] Move instance off grid (e.g., x=65, y=64)
- [ ] Verify action does NOT execute when off grid

---

## INSTANCE ACTIONS

### Destroy Instance (destroy_instance)
- [ ] Test target="self" - verify current instance is destroyed
- [ ] Test target="other" in collision event - verify other instance destroyed
- [ ] Verify destroyed instance disappears from room
- [ ] Verify destroyed instance no longer processes events

### Create Instance (create_instance)
- [ ] Create instance at absolute position (x=200, y=200)
- [ ] Verify new instance appears at correct position
- [ ] Verify new instance has correct sprite
- [ ] Test with relative=true (creates relative to current instance)
- [ ] Verify create event runs for newly created instance
- [ ] Create multiple instances, verify all appear

---

## ROOM ACTIONS

### Next Room (next_room)
- [ ] Trigger action in Room1
- [ ] Verify game transitions to Room2
- [ ] Verify Room2 loads correctly with all instances

### Previous Room (previous_room)
- [ ] Start in Room2, trigger action
- [ ] Verify game transitions back to Room1
- [ ] Verify Room1 loads correctly

### Restart Room (restart_room)
- [ ] Move player, collect coins, etc.
- [ ] Trigger restart_room action
- [ ] Verify room resets to initial state
- [ ] Verify all instances return to original positions
- [ ] Verify destroyed instances reappear

### If Next Room Exists (if_next_room_exists)
- [ ] In Room1 (not last room): verify condition is TRUE
- [ ] Add action after condition, verify it executes
- [ ] In Room2 (last room): verify condition is FALSE
- [ ] Verify following action does NOT execute

### If Previous Room Exists (if_previous_room_exists)
- [ ] In Room1 (first room): verify condition is FALSE
- [ ] Verify following action does NOT execute
- [ ] In Room2 (not first room): verify condition is TRUE
- [ ] Add action after condition, verify it executes

---

## CONDITIONAL FLOW TESTING

### Single Action Conditionals
- [ ] if_on_grid + single action - verify skip works
- [ ] if_next_room_exists + single action - verify skip works
- [ ] if_previous_room_exists + single action - verify skip works

### Block Conditionals (Start Block / End Block)
- [ ] if_on_grid + Start Block + multiple actions + End Block
- [ ] Verify all actions in block execute when condition TRUE
- [ ] Verify all actions in block skip when condition FALSE

### Else Block
- [ ] if_on_grid + action + else + alternative action
- [ ] When on grid: verify first action runs, else action skips
- [ ] When off grid: verify first action skips, else action runs

---

## EDGE CASES & ERROR HANDLING

### Invalid Parameters
- [ ] create_instance with non-existent object name
- [ ] Verify warning message, no crash
- [ ] jump_to_position with invalid expression
- [ ] Verify fallback to 0, no crash

### Boundary Conditions
- [ ] Create instance at room edge (x=0, y=0)
- [ ] Create instance outside room bounds
- [ ] Jump to random in very small room
- [ ] Next room when already in last room (should do nothing)
- [ ] Previous room when already in first room (should do nothing)

### Multiple Instances
- [ ] Create multiple instances of same object
- [ ] Verify each has independent position/speed
- [ ] Destroy one instance, verify others unaffected
- [ ] Collision between two moving instances

### Keyboard Event Edge Cases
- [ ] Press multiple arrow keys simultaneously
- [ ] Verify correct priority/behavior
- [ ] Rapidly press and release keys
- [ ] Verify no stuck movement

---

## PERFORMANCE TESTING

- [ ] Create 50+ instances with step events
- [ ] Verify acceptable frame rate
- [ ] Rapid create/destroy cycles
- [ ] Verify no memory leaks or slowdown

---

## NOTES

Record any bugs or unexpected behavior here:

```
Date: ___________
Issue:
Steps to reproduce:
Expected:
Actual:
```

---

## SIGN-OFF

- [ ] All events tested and working
- [ ] All actions tested and working
- [ ] Conditional flow working correctly
- [ ] Edge cases handled gracefully
- [ ] Performance acceptable

Tester: _______________
Date: _______________
