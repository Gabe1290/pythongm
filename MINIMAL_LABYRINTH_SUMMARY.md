# MINIMAL LABYRINTH GAME - EVENTS AND ACTIONS SUMMARY

## Files Modified

1. **event_types.py** - Located in `/events/` directory
2. **action_types.py** - Located in `/events/` directory

---

## EVENTS - Kept All 6 Essential Events ✅

### Object Events (3)
1. **Create** 🎯
   - Executed when the object is first created
   - Use for: Initial setup, setting variables

2. **Step** ⭐
   - Executed every frame
   - Use for: Continuous behavior, checking conditions

3. **Destroy** 💥
   - Executed when the object is destroyed
   - Use for: Cleanup, final actions

### Collision Events (1)
4. **Collision With...** 💥
   - Executed when colliding with another object
   - Requires: Select which object type triggers this
   - Use for: Hitting walls, reaching goals, collecting items

### Input Events (2)
5. **Keyboard** ⌨️
   - Executed while a key is held down
   - Sub-events: left, right, up, down
   - Use for: Continuous movement while holding key

6. **Keyboard Press** 🔘
   - Executed once when a key is first pressed
   - Sub-events: left, right, up, down
   - Use for: Single grid step per key press (recommended for labyrinth)

---

## ACTIONS - Reduced to 6 Essential Actions ✅

### Movement Actions (1)
1. **Move Grid** ⬛
   - Move one grid unit in specified direction
   - Parameters:
     - Direction: left, right, up, down
     - Grid Size: 32 pixels (default)
   - Use for: Player movement in labyrinth

### Control/Logic Actions (1)
2. **If Collision At** 🎯
   - Check for collision at a position and execute actions conditionally
   - Parameters:
     - X Position: Expression like "self.x + 32"
     - Y Position: Expression like "self.y"
     - Object Type: "any" or "solid"
     - Then Actions: List of actions if collision found
     - Else Actions: List of actions if no collision
   - Use for: Advanced movement logic, checking ahead

### Game Control Actions (3)
3. **Show Message** 💬
   - Display a message to the player
   - Parameters:
     - Message: Text to display
   - Use for: Victory messages, instructions

4. **Restart Room** 🔄
   - Restart the current room/level
   - No parameters
   - Use for: Reset button, death condition

5. **Next Room** ➡️
   - Go to the next room/level
   - No parameters
   - Use for: Level completion, reaching goal

### Instance Actions (1)
6. **Destroy Instance** 💀
   - Destroy this object instance
   - No parameters
   - Use for: Removing collectibles, temporary objects

---

## ACTIONS REMOVED (For Expansion Later)

### Movement Actions Removed:
- ❌ Move Fixed (free movement with speed)
- ❌ Set Horizontal Speed
- ❌ Set Vertical Speed
- ❌ Stop Movement
- ❌ Bounce
- ❌ Move to Position
- ❌ Push Object
- ❌ Snap to Grid
- ❌ Set HSpeed
- ❌ Set VSpeed

### Logic Actions Removed:
- ❌ If Position Empty
- ❌ If Place Free

### Instance Actions Removed:
- ❌ Create Instance
- ❌ Transform To Object

### Audio Actions Removed:
- ❌ Play Sound

### Variable Actions Removed:
- ❌ Set Variable

---

## TYPICAL LABYRINTH GAME OBJECTS

### Player Object
**Events:**
- Keyboard Press → left: Move Grid (left, 32)
- Keyboard Press → right: Move Grid (right, 32)
- Keyboard Press → up: Move Grid (up, 32)
- Keyboard Press → down: Move Grid (down, 32)

### Wall Object
**Properties:**
- Solid: ✅ True
- No events needed

### Goal Object
**Events:**
- Collision With "obj_player":
  - Show Message: "Level Complete!"
  - Next Room

### Restart Object (Optional)
**Events:**
- Collision With "obj_player":
  - Restart Room

---

## EXPANDABILITY

To add more features later, simply add more entries to `ACTION_TYPES` dictionary in `action_types.py`:

```python
ACTION_TYPES = {
    # Existing minimal actions...
    
    # Add new action:
    "play_sound": ActionType(
        name="play_sound",
        display_name="Play Sound",
        description="Play a sound effect",
        category="Audio",
        icon="🔊",
        parameters=[...]
    ),
}
```

The framework is fully extensible - you can add:
- More movement actions (smooth movement, physics)
- Audio actions (play sound, stop sound)
- Advanced logic (variables, timers)
- Visual effects (particles, animations)
- And more...

---

## FILE LOCATIONS

Replace these files in your project:
- `/events/event_types.py`
- `/events/action_types.py`

No changes needed to:
- `action_executor.py` (runtime engine)
- `game_runner.py` (game loop)
- `object_events_panel.py` (IDE panel)
- `action_editor.py` (parameter editor)

These files will automatically use the reduced event/action set!
