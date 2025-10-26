# GAME_RUNNER.PY UPDATES FOR SMOOTH MOVEMENT

## Changes Needed

Add speed-based physics and keyboard held event handling to game_runner.py

---

## CHANGE 1: Initialize Speed Properties in GameInstance

**Location:** `GameInstance.__init__()` method (around line 49)

**Add after line 60 (after self.object_data = None):**

```python
        # Speed properties for smooth movement
        self.hspeed = 0.0  # Horizontal speed (pixels per frame)
        self.vspeed = 0.0  # Vertical speed (pixels per frame)
```

---

## CHANGE 2: Add Keyboard Held Event Handling

**Location:** In `handle_events()` method

**Replace the entire handle_events method with:**

```python
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stop_game()
                elif event.key == pygame.K_F1:
                    self.show_debug_info()
                else:
                    # Handle keyboard press events (single press)
                    self.handle_keyboard_press(event.key)
        
        # Handle keyboard held events (continuous)
        self.handle_keyboard_held()
```

---

## CHANGE 3: Add Keyboard Held Handler Method

**Location:** Add new method after `handle_keyboard_press()`

**Add this new method:**

```python
    def handle_keyboard_held(self):
        """Handle keyboard held events (continuous while key is down)"""
        if not self.current_room:
            return
        
        # Get currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Map pygame keys to sub-event keys
        key_checks = {
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
        }
        
        # Check each key and execute corresponding keyboard events
        for pygame_key, sub_key in key_checks.items():
            if keys[pygame_key]:
                # Execute keyboard event for all instances
                for instance in self.current_room.instances:
                    if not instance.object_data:
                        continue
                    
                    events = instance.object_data.get('events', {})
                    
                    # Check for keyboard parent event with sub-events
                    if "keyboard" in events:
                        keyboard_event = events["keyboard"]
                        
                        # Check if it has sub-events for specific keys
                        if isinstance(keyboard_event, dict) and sub_key in keyboard_event:
                            # Execute the sub-event
                            sub_event_data = keyboard_event[sub_key]
                            if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                                for action_data in sub_event_data["actions"]:
                                    instance.action_executor.execute_action(instance, action_data)
```

---

## CHANGE 4: Apply Speed-Based Movement in Update

**Location:** In `update()` method, after handling room transitions

**Add this code after the room transition checks (around line 475):**

```python
        # Apply speed-based movement (smooth continuous movement)
        for instance in self.current_room.instances:
            if hasattr(instance, 'hspeed') and instance.hspeed != 0:
                instance.x += instance.hspeed
            if hasattr(instance, 'vspeed') and instance.vspeed != 0:
                instance.y += instance.vspeed
```

**Full update method should look like this:**

```python
    def update(self):
        """Update game logic"""
        if not self.current_room:
            return
        
        # Get objects data for solid checks
        objects_data = self.project_data.get('assets', {}).get('objects', {})
        
        # Check for room restart/transition flags FIRST
        for instance in self.current_room.instances:
            if hasattr(instance, 'restart_room_flag') and instance.restart_room_flag:
                print("🔄 Restarting room...")
                self.restart_current_room()
                return
            
            if hasattr(instance, 'next_room_flag') and instance.next_room_flag:
                print("➡️  Going to next room...")
                self.goto_next_room()
                return
        
        # Apply speed-based movement (smooth continuous movement)
        for instance in self.current_room.instances:
            if hasattr(instance, 'hspeed') and instance.hspeed != 0:
                instance.x += instance.hspeed
            if hasattr(instance, 'vspeed') and instance.vspeed != 0:
                instance.y += instance.vspeed
        
        # Handle intended movement with collision checking (grid-based)
        for instance in self.current_room.instances:
            if hasattr(instance, 'intended_x') and hasattr(instance, 'intended_y'):
                # Check if movement would collide with solid objects
                can_move = self.check_movement_collision(instance, objects_data)
                
                if can_move:
                    print(f"✅ Movement allowed: {instance.object_name} → ({instance.intended_x}, {instance.intended_y})")
                    instance.x = instance.intended_x
                    instance.y = instance.intended_y
                else:
                    print(f"❌ Movement blocked: {instance.object_name} (hit solid object)")
                
                # Clear intended movement
                delattr(instance, 'intended_x')
                delattr(instance, 'intended_y')
        
        # Check collision events
        for instance in self.current_room.instances:
            self.check_collision_events(instance, objects_data)
        
        # Execute step events for all instances
        for instance in self.current_room.instances:
            instance.step()
```

---

## Summary of Changes

### Events (6 total):
1. ✅ Create
2. ✅ Step
3. ✅ Destroy
4. ✅ Collision With...
5. ✅ **Keyboard** (held down - NEW/RESTORED)
6. ✅ Keyboard Press (single press)

### Actions (10 total):
1. ✅ Move Grid (instant grid movement)
2. ✅ **Set Horizontal Speed** (NEW)
3. ✅ **Set Vertical Speed** (NEW)
4. ✅ **Stop Movement** (NEW)
5. ✅ **Snap to Grid** (NEW)
6. ✅ **If On Grid** (NEW)
7. ✅ If Collision At
8. ✅ Show Message
9. ✅ Restart Room
10. ✅ Next Room
11. ✅ Destroy Instance

---

## Usage Examples

### Example 1: Smooth Movement with Keyboard Hold
```
Object: obj_player
Event: Keyboard → right (held)
  Action: Set Horizontal Speed = 4
Event: Keyboard → left (held)
  Action: Set Horizontal Speed = -4
Event: Step
  Action: If On Grid
    Then: Stop Movement
```

### Example 2: Grid-Based Movement with Keyboard Press
```
Object: obj_player
Event: Keyboard Press → right
  Action: Move Grid (right, 32)
```

### Example 3: Smooth Movement with Collision Stop
```
Object: obj_player
Event: Keyboard → right (held)
  Action: Set Horizontal Speed = 4
Event: Step
  Action: If Collision At (self.x + 32, self.y) with "solid"
    Then: Stop Movement
```

---

## Testing

1. **Test Grid Movement:**
   - Use Keyboard Press + Move Grid
   - Player should move one cell per key press

2. **Test Smooth Movement:**
   - Use Keyboard (held) + Set Horizontal/Vertical Speed
   - Player should move continuously while key is held

3. **Test Grid Detection:**
   - Use If On Grid action in Step event
   - Should detect when player is aligned to grid

4. **Test Speed Stop:**
   - Hold arrow key to move
   - Release key
   - Use Stop Movement in a collision or step event
