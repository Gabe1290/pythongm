#!/usr/bin/env python3
"""
Action Execution Engine
Converts visual actions into runtime behavior
"""

import math
import time
from typing import Dict, Any, List, Optional, Tuple

class ActionExecutor:
    """Executes visual actions during gameplay"""
    
    def __init__(self):
        self.action_handlers = {
            "delay_action": self.execute_delay_action_action,
            "move": self.execute_move_action,
            "set_variable": self.execute_set_variable_action,
            "destroy_instance": self.execute_destroy_instance_action,
            "bounce": self.execute_bounce_action,
            "stop_movement": self.execute_stop_movement_action,
            "play_sound": self.execute_play_sound_action,
            "create_instance": self.execute_create_instance_action,
            "set_horizontal_speed": self.execute_set_horizontal_speed_action,
            "set_vertical_speed": self.execute_set_vertical_speed_action,
            "move_grid": self.execute_move_grid_action,
            "if_instance_count": self.execute_if_instance_count_action,
            "change_room": self.execute_change_room_action,
            "if_condition": self.execute_if_condition_action,
            "if_variable_equals": self.execute_if_variable_equals_action,
            "show_message": self.execute_show_message_action,
            "next_room": self.execute_next_room_action,
            "previous_room": self.execute_previous_room_action,
            "if_next_room_exists": self.execute_if_next_room_exists_action,
            "if_previous_room_exists": self.execute_if_previous_room_exists_action,
            "transform_to": self.execute_transform_to_action,
            "push_object": self.execute_push_object_action,
            "snap_to_grid": self.execute_snap_to_grid_action,
            "if_place_free": self.execute_if_place_free_action,
            "move_to_position": self.execute_move_to_position_action,
            "if_collision_at": self.execute_if_collision_at_action,
            "set_hspeed": self.execute_set_hspeed_action,
            "set_vspeed": self.execute_set_vspeed_action
        }
        self.room_instances = []
        self.sprites = {}  # ADD THIS
        self.objects_data = {} 
        self.game_runner = None  # ADD - will be set by game_runner

    def execute_delay_action_action(self, instance, parameters: Dict[str, Any]):
        """Set an alarm that executes an action after N frames"""
        frames = int(parameters.get("frames", 60))
        then_action = parameters.get("then_action", "")
        room_name = parameters.get("room_name", "")
        
        # Handle special room navigation values
        if then_action == "change_room" and room_name:
            if room_name == "__next__":
                # Will change to next room
                then_action = "next_room"
                parameters = {}  # Clear room_name
            elif room_name == "__prev__":
                # Will change to previous room  
                then_action = "previous_room"
                parameters = {}
            elif room_name == "__current__":
                # Restart current room
                if hasattr(self, 'game_runner') and self.game_runner and self.game_runner.current_room:
                    room_name = self.game_runner.current_room.name
                    parameters["room_name"] = room_name
        
        # Create alarm data with the action to execute
        alarm_id = len(instance.alarms) if hasattr(instance, 'alarms') else 0
        
        if not hasattr(instance, 'alarms'):
            instance.alarms = {}
        
        # Build the action to execute when alarm fires
        action_to_execute = {
            "action": then_action,
            "parameters": parameters
        }
        
        instance.alarms[alarm_id] = {
            'frames': frames,
            'action': action_to_execute
        }
        
        print(f"Set alarm {alarm_id} for {frames} frames, will execute: {then_action}")

    def execute_event(self, instance, event_name: str, events_data: Dict[str, Any]):
        """Execute all actions in an event"""
        if event_name not in events_data:
            return
            
        event_data = events_data[event_name]
        actions = event_data.get("actions", [])
        
        for action_data in actions:
            self.execute_action(instance, action_data)
    
    def execute_event_actions(self, instance, actions: List[Dict[str, Any]]):
        """Execute a list of actions directly"""
        # Check if we have collision context
        other = getattr(instance, '_collision_other', None)
        
        for action_data in actions:
            self.execute_action(instance, action_data, other=other)

    def execute_action(self, instance, action_data: Dict[str, Any], other=None):
        """Execute a single action with optional 'other' context"""
        action_name = action_data.get("action")
        parameters = action_data.get("parameters", {})
        
        if action_name in self.action_handlers:
            try:
                # Pass 'other' to action handlers that need it
                self.action_handlers[action_name](instance, parameters, other)
            except TypeError:
                # Fallback for handlers that don't accept 'other' yet
                self.action_handlers[action_name](instance, parameters)
            except Exception as e:
                print(f"Error executing action {action_name}: {e}")
        else:
            print(f"Unknown action: {action_name}")
    
    def execute_move_action(self, instance, parameters: Dict[str, Any], other=None):
        """Execute move action with relative support"""
        direction = parameters.get("direction", "right")
        speed = parameters.get("speed", 4)
        relative = parameters.get("relative", False)
        
        print(f"🏃 MOVE ACTION: {instance.object_name} direction={direction}, speed={speed}, relative={relative}")
        
        # Convert direction names to degrees
        direction_map = {
            "right": 0,
            "up": 90, 
            "left": 180,
            "down": 270,
            "up-right": 45,
            "up-left": 135,
            "down-right": 315,
            "down-left": 225
        }
        
        direction_degrees = direction_map.get(direction, 0)
        
        if relative:
            # Add to current speed/direction (more complex - combine vectors)
            import math
            current_dx = instance.speed * math.cos(math.radians(instance.direction)) if instance.speed > 0 else 0
            current_dy = -instance.speed * math.sin(math.radians(instance.direction)) if instance.speed > 0 else 0
            
            add_dx = speed * math.cos(math.radians(direction_degrees))
            add_dy = -speed * math.sin(math.radians(direction_degrees))
            
            new_dx = current_dx + add_dx
            new_dy = current_dy + add_dy
            
            new_speed = math.sqrt(new_dx**2 + new_dy**2)
            if new_speed > 0:
                new_direction = math.degrees(math.atan2(-new_dy, new_dx))
                if new_direction < 0:
                    new_direction += 360
                instance.direction = new_direction
            instance.speed = new_speed
        else:
            # Absolute movement - replace current speed/direction
            instance.direction = direction_degrees
            instance.speed = speed
        
        print(f"✅ RESULT: {instance.object_name} now has speed={instance.speed}, direction={instance.direction}")
    
    def execute_set_variable_action(self, instance, parameters: Dict[str, Any], other=None):
        """Execute set variable action"""
        variable_name = parameters.get("variable_name", "temp")
        value = parameters.get("value", "0")
        
        # Try to convert value to number if possible
        try:
            if "." in str(value):
                value = float(value)
            else:
                value = int(value)
        except (ValueError, TypeError):
            pass  # Keep as string
        
        # Set variable on instance
        setattr(instance, variable_name, value)
        print(f"Set {instance.object_name}.{variable_name} = {value}")

    def execute_destroy_instance_action(self, instance, parameters: Dict[str, Any], other=None):
        """Execute destroy instance action"""
        instance.to_destroy = True
        print(f"Marked {instance.object_name} for destruction")

    def execute_bounce_action(self, instance, parameters: Dict[str, Any]):
        """Execute bounce based on bounce_type parameter"""
        current_time = getattr(instance, 'last_bounce_time', 0)
        import time
        now = time.time()
        
        if now - current_time < 0.1:
            return
            
        instance.last_bounce_time = now
        bounce_type = parameters.get("bounce_type", "bounce")
        old_direction = instance.direction
        
        if bounce_type == "horizontal":
            # Bounce off vertical walls (reverse horizontal component)
            instance.direction = 180 - instance.direction
        elif bounce_type == "vertical":
            # Bounce off horizontal walls (reverse vertical component)
            instance.direction = 360 - instance.direction
        elif bounce_type == "reverse":
            # Complete 180° reversal
            instance.direction = (instance.direction + 180) % 360
        else:  # "bounce" - smart auto-detect (not used with automatic collision handling)
            # This would require collision direction info
            # For now, just do reverse as fallback
            instance.direction = (instance.direction + 180) % 360
        
        instance.direction = instance.direction % 360
        
        print(f"Bounced {instance.object_name} ({bounce_type}): {old_direction}° → {instance.direction}°")

    def execute_stop_movement_action(self, instance, parameters: Dict[str, Any]):
        """Execute stop movement action"""
        instance.speed = 0.0
        print(f"Stopped {instance.object_name} movement")

    def execute_play_sound_action(self, instance, parameters: Dict[str, Any]):
        """Execute play sound action"""
        sound_name = parameters.get("sound_name", "sound1")
        print(f"Playing sound: {sound_name} (sound system not implemented)")

    def execute_create_instance_action(self, instance, parameters: Dict[str, Any]):
        """Execute create instance action - actually creates the instance"""
        object_name = parameters.get("object_name", "obj_object1")
        x_offset = float(parameters.get("x_offset", 0))
        y_offset = float(parameters.get("y_offset", 0))
        execute_create_event = parameters.get("execute_create_event", True)
        
        new_x = instance.x + x_offset
        new_y = instance.y + y_offset
        
        print(f"Creating {object_name} at ({new_x}, {new_y})")
        
        # Import GameInstance from game_runner
        from runtime.game_runner import GameInstance
        
        # Create the new instance
        instance_data = {
            'object_name': object_name,
            'x': new_x,
            'y': new_y,
            'visible': True,
            'rotation': 0,
            'scale_x': 1.0,
            'scale_y': 1.0
        }
        
        new_instance = GameInstance(object_name, new_x, new_y, instance_data)
        
        # Set up object data if available
        if hasattr(self, 'objects_data') and object_name in self.objects_data:
            new_instance.object_data = self.objects_data[object_name]
            
            # Set sprite
            sprite_name = self.objects_data[object_name].get('sprite', '')
            if hasattr(self, 'sprites') and sprite_name in self.sprites:
                new_instance.sprite = self.sprites[sprite_name]
        
        # Pass sprites and objects_data to new instance's action executor
        new_instance.action_executor.sprites = self.sprites
        new_instance.action_executor.objects_data = self.objects_data
        new_instance.action_executor.room_instances = self.room_instances
        new_instance.action_executor.game_runner = self.game_runner
        
        # Add to room instances
        if hasattr(self, 'room_instances'):
            self.room_instances.append(new_instance)
        
        # Execute Create event if requested
        if execute_create_event and new_instance.object_data and "events" in new_instance.object_data:
            new_instance.action_executor.execute_event(new_instance, "create", new_instance.object_data["events"])
            print(f"Executed Create event for {object_name}")
        
        return new_instance
    
    def execute_transform_to_action(self, instance, parameters: Dict[str, Any]):
        """Transform instance to a different object type"""
        new_object_name = parameters.get("object_name", "obj_box_store")
        
        print(f"🔄 TRANSFORM: {instance.object_name} -> {new_object_name}")
        
        # Store current position
        old_x = instance.x
        old_y = instance.y
        
        # Mark old instance for destruction
        instance.to_destroy = True
        
        # Remove from room instances immediately
        try:
            if hasattr(self, 'room_instances') and instance in self.room_instances:
                self.room_instances.remove(instance)
                print(f"  ✓ Removed old {instance.object_name}")
        except ValueError:
            pass
        
        # Create new instance at same position
        new_instance_data = {
            'object_name': new_object_name,
            'x': old_x,
            'y': old_y,
            'visible': True,
            'rotation': 0,
            'scale_x': 1.0,
            'scale_y': 1.0
        }
        
        # Import GameInstance
        from runtime.game_runner import GameInstance
        
        # Create the new instance
        new_instance = GameInstance(new_object_name, old_x, old_y, new_instance_data)
        
        # Set up object data if available
        if hasattr(self, 'objects_data') and new_object_name in self.objects_data:
            new_instance.object_data = self.objects_data[new_object_name]
            
            # Set sprite
            sprite_name = self.objects_data[new_object_name].get('sprite', '')
            if hasattr(self, 'sprites') and sprite_name in self.sprites:
                new_instance.sprite = self.sprites[sprite_name]
                print(f"  ✓ Set sprite: {sprite_name}")
        
        # Pass context to new instance's action executor
        new_instance.action_executor.sprites = self.sprites
        new_instance.action_executor.objects_data = self.objects_data
        new_instance.action_executor.room_instances = self.room_instances
        new_instance.action_executor.game_runner = self.game_runner
        
        # Add to room instances
        if hasattr(self, 'room_instances'):
            self.room_instances.append(new_instance)
            print(f"  ✓ Created {new_object_name} at ({old_x}, {old_y})")
        
        # Execute Create event for new instance
        if new_instance.object_data and "events" in new_instance.object_data:
            new_instance.action_executor.execute_event(new_instance, "create", new_instance.object_data["events"])
            print(f"  ✓ Executed Create event for {new_object_name}")
        
        return new_instance

    def check_collision_at_position(self, instance, new_x: float, new_y: float, exclude_list=None) -> bool:
        """Check if instance would collide with solid objects at given position"""
        if not self.room_instances:
            return False
        
        # Allow passing an exclude list for more complex checks
        if exclude_list is None:
            exclude_list = [instance]
        elif instance not in exclude_list:
            exclude_list.append(instance)
        
        # Get collision rect for the instance at new position
        collision_rect = self.get_collision_rect_at_position(instance, new_x, new_y)
        
        # Check against all solid objects
        for other in self.room_instances:
            if other in exclude_list or other.to_destroy:
                continue
            
            # Only check solid objects
            if not other.object_data or not other.object_data.get('solid', False):
                continue
            
            # Get other's collision rect
            other_rect = self.get_collision_rect_at_position(other, other.x, other.y)
            
            # Check collision with small buffer for precision
            if self.rects_overlap(collision_rect, other_rect, buffer=1):
                return True
        
        return False

    def check_grid_collision(self, instance, grid_x: float, grid_y: float, grid_size: int = 32) -> Dict[str, Any]:
        """
        Check if a grid position is blocked and return detailed collision info
        Returns: {'blocked': bool, 'objects': list, 'solid_objects': list}
        """
        result = {
            'blocked': False,
            'objects': [],
            'solid_objects': [],
            'pushable_objects': []
        }
        
        if not self.room_instances:
            return result
        
        # Define grid cell bounds with tolerance
        tolerance = grid_size * 0.4  # 40% of grid size for detection
        
        for other in self.room_instances:
            if other == instance or other.to_destroy:
                continue
            
            # Check if other object is within this grid cell
            dx = abs(other.x - grid_x)
            dy = abs(other.y - grid_y)
            
            if dx < tolerance and dy < tolerance:
                result['objects'].append(other)
                
                # Check if it's solid
                if other.object_data and other.object_data.get('solid', False):
                    result['solid_objects'].append(other)
                    result['blocked'] = True
                
                # Check if it's pushable (for puzzle games)
                if other.object_name in ['obj_box', 'obj_crate', 'obj_pushable']:
                    result['pushable_objects'].append(other)
        
        return result

    def get_collision_rect_at_position(self, instance, x: float, y: float) -> Dict[str, float]:
        """Get collision rectangle for an instance at a specific position"""
        # Use sprite size if available, otherwise default
        if hasattr(instance, 'sprite') and instance.sprite:
            width = instance.sprite.width
            height = instance.sprite.height
        else:
            width = getattr(instance, 'collision_width', 32)
            height = getattr(instance, 'collision_height', 32)
        
        # Shrink collision box slightly for better game feel
        collision_margin = 2  # pixels to shrink on each side
        
        return {
            'x': x + collision_margin,
            'y': y + collision_margin,
            'width': width - (collision_margin * 2),
            'height': height - (collision_margin * 2)
        }

    def rects_overlap(self, rect1: Dict[str, float], rect2: Dict[str, float], buffer: float = 0) -> bool:
        """Check if two rectangles overlap with optional buffer"""
        return (rect1['x'] < rect2['x'] + rect2['width'] - buffer and
                rect1['x'] + rect1['width'] - buffer > rect2['x'] and
                rect1['y'] < rect2['y'] + rect2['height'] - buffer and
                rect1['y'] + rect1['height'] - buffer > rect2['y'])

    def check_collision_in_direction(self, instance, direction: str, distance: float = 32) -> Optional[object]:
        """Check for collision in a specific direction from instance"""
        check_x, check_y = instance.x, instance.y
        
        # Calculate check position based on direction
        if direction == "up":
            check_y -= distance
        elif direction == "down":
            check_y += distance
        elif direction == "left":
            check_x -= distance
        elif direction == "right":
            check_x += distance
        elif direction == "facing":
            # Use instance's current direction
            import math
            rad = math.radians(instance.direction)
            check_x += math.cos(rad) * distance
            check_y -= math.sin(rad) * distance
        
        # Check for collision at that position
        collision_rect = self.get_collision_rect_at_position(instance, check_x, check_y)
        
        for other in self.room_instances:
            if other == instance or other.to_destroy:
                continue
            
            other_rect = self.get_collision_rect_at_position(other, other.x, other.y)
            
            if self.rects_overlap(collision_rect, other_rect):
                return other
        
        return None

    def handle_movement_collision(self, instance, dx: float, dy: float) -> Tuple[float, float]:
        """
        Handle collision for continuous movement (not grid-based)
        Returns adjusted (dx, dy) that avoids collision
        """
        if dx == 0 and dy == 0:
            return dx, dy
        
        # Try full movement first
        new_x = instance.x + dx
        new_y = instance.y + dy
        
        if not self.check_collision_at_position(instance, new_x, new_y):
            return dx, dy  # No collision, return original movement
        
        # Try horizontal movement only
        if dx != 0 and not self.check_collision_at_position(instance, instance.x + dx, instance.y):
            return dx, 0  # Can move horizontally but not vertically
        
        # Try vertical movement only
        if dy != 0 and not self.check_collision_at_position(instance, instance.x, instance.y + dy):
            return 0, dy  # Can move vertically but not horizontally
        
        # Can't move at all
        return 0, 0
    
    def execute_set_horizontal_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set horizontal speed component with collision checking"""
        speed = parameters.get("speed", 0)
        
        # Predict next position
        next_x = instance.x + speed
        next_y = instance.y
        
        # Check if movement would cause collision
        if self.check_collision_at_position(instance, next_x, next_y):
            # Stop horizontal movement
            speed = 0
        
        # Get current vertical component
        import math
        current_vertical = -instance.speed * math.sin(math.radians(instance.direction)) if instance.speed > 0 else 0
        
        # Calculate new speed and direction
        horizontal = speed
        vertical = current_vertical
        
        # Calculate magnitude and direction
        new_speed = math.sqrt(horizontal**2 + vertical**2)
        if new_speed > 0:
            # Calculate angle (0=right, 90=up, 180=left, 270=down)
            new_direction = math.degrees(math.atan2(-vertical, horizontal))
            if new_direction < 0:
                new_direction += 360
            
            instance.speed = new_speed
            instance.direction = new_direction
        else:
            instance.speed = 0

    def execute_set_vertical_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set vertical speed component with collision checking"""
        speed = parameters.get("speed", 0)
        
        # Predict next position
        next_x = instance.x
        next_y = instance.y + speed
        
        # Check if movement would cause collision
        if self.check_collision_at_position(instance, next_x, next_y):
            # Stop vertical movement
            speed = 0
        
        # Get current horizontal component  
        import math
        current_horizontal = instance.speed * math.cos(math.radians(instance.direction)) if instance.speed > 0 else 0
        
        # Calculate new speed and direction
        horizontal = current_horizontal
        vertical = speed
        
        # Calculate magnitude and direction
        new_speed = math.sqrt(horizontal**2 + vertical**2)
        if new_speed > 0:
            # Calculate angle (0=right, 90=up, 180=left, 270=down)
            new_direction = math.degrees(math.atan2(-vertical, horizontal))
            if new_direction < 0:
                new_direction += 360
            
            instance.speed = new_speed
            instance.direction = new_direction
        else:
            instance.speed = 0

    def execute_move_grid_action(self, instance, parameters: Dict[str, Any], other=None):
        """Enhanced grid movement - PURE MOVEMENT, no game logic"""
        # Don't start new movement if already moving
        if hasattr(instance, 'target_x') and instance.target_x is not None:
            return
        if hasattr(instance, 'target_y') and instance.target_y is not None:
            return
        
        direction = parameters.get("direction", "right")
        grid_size = parameters.get("grid_size", 32)
        check_collision = parameters.get("check_collision", True)
        
        # Snap current position to grid first
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size
        
        # Calculate target position
        target_x = instance.x
        target_y = instance.y
        
        direction_offsets = {
            "left": (-grid_size, 0),
            "right": (grid_size, 0),
            "up": (0, -grid_size),
            "down": (0, grid_size)
        }
        
        if direction in direction_offsets:
            offset_x, offset_y = direction_offsets[direction]
            target_x += offset_x
            target_y += offset_y
        else:
            print(f"Unknown grid movement direction: {direction}")
            return
        
        # Check for collisions if enabled
        if check_collision:
            collision_info = self.check_grid_collision(instance, target_x, target_y, grid_size)
            
            if collision_info['blocked']:
                print(f"Grid move {direction} blocked for {instance.object_name} by solid object")
                
                # Trigger collision events with the blocking objects
                for other in collision_info['solid_objects']:
                    self.trigger_collision_event(instance, other)
                return
        
        # Set target for smooth grid movement
        instance.target_x = target_x
        instance.target_y = target_y
        print(f"Grid move {direction}: {instance.object_name} moving to ({target_x}, {target_y})")

    def trigger_collision_event(self, instance1, instance2):
        """Trigger collision event between two instances"""
        if not instance1.object_data or "events" not in instance1.object_data:
            return
        
        events = instance1.object_data["events"]
        
        # Check for specific collision event with this object type
        specific_collision = f"collision_with_{instance2.object_name}"
        if specific_collision in events:
            actions = events[specific_collision].get("actions", [])
            for action_data in actions:
                self.execute_action(instance1, action_data)
            print(f"Executed {specific_collision} event for {instance1.object_name}")
            return
        
        # Check for general collision event
        if "collision" in events:
            actions = events["collision"].get("actions", [])
            for action_data in actions:
                # Pass collision context in parameters
                if "parameters" not in action_data:
                    action_data["parameters"] = {}
                action_data["parameters"]["collision_with"] = instance2.object_name
                self.execute_action(instance1, action_data)
            print(f"Executed general collision event for {instance1.object_name}")

    def execute_conditional_action(self, instance, action_name: str, parameters: Dict[str, Any]):
        """Execute a conditional action with parameters"""
        if action_name in self.action_handlers:
            self.action_handlers[action_name](instance, parameters)
        else:
            # Try to execute as a standard action
            action_data = {
                "action": action_name,
                "parameters": parameters
            }
            self.execute_action(instance, action_data)
    
    def count_instances(self, object_name: str) -> int:
        """Count instances of a specific object type"""
        if not hasattr(self, 'room_instances'):
            return 0
        
        count = sum(1 for inst in self.room_instances 
                    if inst.object_name == object_name and not inst.to_destroy)
        return count
    
    def execute_if_instance_count_action(self, instance, parameters: Dict[str, Any]):
        """Check instance count and execute conditional actions"""
        object_name = parameters.get("object_name", "obj_box")
        operator = parameters.get("operator", "==")
        count_value = int(parameters.get("count", 0))
        then_action = parameters.get("then_action", "")
        
        # Count instances
        actual_count = self.count_instances(object_name)
        
        print(f"Instance count check: {object_name} count={actual_count}, checking {operator} {count_value}")
        
        # Evaluate condition
        condition_met = False
        if operator == "==":
            condition_met = actual_count == count_value
        elif operator == "!=":
            condition_met = actual_count != count_value
        elif operator == "<":
            condition_met = actual_count < count_value
        elif operator == ">":
            condition_met = actual_count > count_value
        elif operator == "<=":
            condition_met = actual_count <= count_value
        elif operator == ">=":
            condition_met = actual_count >= count_value
        
        if condition_met:
            print(f"✅ Condition met! Executing: {then_action}")
            
            # Execute the then_action with proper parameters
            if then_action == "change_room":
                # Pass room_name directly from parameters
                room_name = parameters.get("room_name", "Room01")
                print(f"DEBUG: Extracted room_name = {room_name}")
                self.execute_action(instance, {
                    "action": "change_room",
                    "parameters": {"room_name": room_name}
                })
            else:
                # For other actions, execute without extra parameters
                self.execute_action(instance, {
                    "action": then_action,
                    "parameters": {}
                })
        else:
            print(f"❌ Condition not met: {actual_count} {operator} {count_value} is False")

    def execute_change_room_action(self, instance, parameters: Dict[str, Any]):
        """Change to a different room"""
        room_name = parameters.get("room_name", "Room01")
        
        print(f"Changing to room: {room_name}")
        
        # Call game_runner's change_room method
        if hasattr(self, 'game_runner') and self.game_runner:
            self.game_runner.change_room(room_name)
        else:
            print("Error: game_runner not available for room change")

    def count_instances(self, object_name: str) -> int:
        """Count instances of a specific object type"""
        if not hasattr(self, 'room_instances'):
            return 0
        
        count = sum(1 for inst in self.room_instances 
                    if inst.object_name == object_name and not inst.to_destroy)
        return count
    
    def execute_if_variable_equals_action(self, instance, parameters: Dict[str, Any]):
        """Check if variable equals value, then execute action"""
        variable_name = parameters.get("variable_name", "soko_active")
        expected_value = parameters.get("value", "1")
        then_action = parameters.get("then_action", "")
        
        # Get variable from instance
        actual_value = str(getattr(instance, variable_name, ""))
        
        if actual_value == expected_value:
            # Execute nested action with all parameters passed through
            if then_action == "if_instance_count":
                self.execute_if_instance_count_action(instance, parameters)
            elif then_action:
                self.execute_action(instance, {
                    "action": then_action,
                    "parameters": parameters
                })
    
    def execute_if_condition_action(self, instance, parameters: Dict[str, Any]):
        """Execute conditional logic with nested action lists"""
        condition_type = parameters.get("condition_type", "instance_count")
        condition_met = False
        
        if condition_type == "instance_count":
            object_name = parameters.get("object_name", "")
            operator = parameters.get("operator", "==")
            target_value = parameters.get("value", 0)
            
            # Count instances
            count = sum(1 for inst in self.room_instances 
                    if inst.object_name == object_name and not inst.to_destroy)
            
            # Evaluate condition
            if operator == "==":
                condition_met = count == target_value
            elif operator == "!=":
                condition_met = count != target_value
            elif operator == "<":
                condition_met = count < target_value
            elif operator == ">":
                condition_met = count > target_value
            elif operator == "<=":
                condition_met = count <= target_value
            elif operator == ">=":
                condition_met = count >= target_value
            
            print(f"Condition check: {object_name} count={count} {operator} {target_value} = {condition_met}")
        
        # Execute appropriate action list
        if condition_met:
            then_actions = parameters.get("then_actions", [])
            if then_actions:
                print(f"Executing {len(then_actions)} THEN actions")
                for action_data in then_actions:
                    self.execute_action(instance, action_data)
        else:
            else_actions = parameters.get("else_actions", [])
            if else_actions:
                print(f"Executing {len(else_actions)} ELSE actions")
                for action_data in else_actions:
                    self.execute_action(instance, action_data)

    def execute_show_message_action(self, instance, parameters: Dict[str, Any]):
        """Execute show message action - displays a message box"""
        message = parameters.get("message", "Message")
        title = parameters.get("title", "Message")
        button_text = parameters.get("button_text", "OK")
        pause_game = parameters.get("pause_game", True)
        
        print(f"SHOW MESSAGE: {title} - {message}")
    
        # Get game runner reference
        if hasattr(self, 'game_runner') and self.game_runner:
            # Call the show_message_box method on game_runner
            self.game_runner.show_message_box(message, title, button_text, pause_game)
        else:
            # Fallback - just print to console
            print(f"[MESSAGE BOX - {title}]: {message}")

    def get_room_list(self):
        """Get ordered list of rooms from game runner"""
        if hasattr(self, 'game_runner') and self.game_runner:
            return list(self.game_runner.rooms.keys())
        return []

    def get_current_room_index(self):
        """Get index of current room in room list"""
        if hasattr(self, 'game_runner') and self.game_runner and self.game_runner.current_room:
            room_list = self.get_room_list()
            current_room_name = self.game_runner.current_room.name
            if current_room_name in room_list:
                return room_list.index(current_room_name)
        return -1

    def execute_next_room_action(self, instance, parameters: Dict[str, Any]):
        """Go to the next room in the room list"""
        room_list = self.get_room_list()
        current_index = self.get_current_room_index()
        
        if current_index >= 0 and current_index < len(room_list) - 1:
            next_room = room_list[current_index + 1]
            print(f"Going to next room: {next_room}")
            if hasattr(self, 'game_runner') and self.game_runner:
                self.game_runner.change_room(next_room)
        else:
            print("No next room available")

    def execute_previous_room_action(self, instance, parameters: Dict[str, Any]):
        """Go to the previous room in the room list"""
        room_list = self.get_room_list()
        current_index = self.get_current_room_index()
        
        if current_index > 0:
            previous_room = room_list[current_index - 1]
            print(f"Going to previous room: {previous_room}")
            if hasattr(self, 'game_runner') and self.game_runner:
                self.game_runner.change_room(previous_room)
        else:
            print("No previous room available")

    def execute_if_next_room_exists_action(self, instance, parameters: Dict[str, Any]):
        """Check if next room exists and execute appropriate action"""
        room_list = self.get_room_list()
        current_index = self.get_current_room_index()
        
        has_next = current_index >= 0 and current_index < len(room_list) - 1
        
        if has_next:
            then_action = parameters.get("then_action", "next_room")
            print(f"Next room exists, executing: {then_action}")
            
            if then_action == "next_room":
                self.execute_next_room_action(instance, {})
            elif then_action == "show_message":
                next_room_name = room_list[current_index + 1]
                self.execute_show_message_action(instance, {
                    "message": f"Next room is: {next_room_name}",
                    "title": "Next Room Available",
                    "button_text": "OK"
                })
            else:
                self.execute_action(instance, {
                    "action": then_action,
                    "parameters": {}
                })
        else:
            else_action = parameters.get("else_action", "show_message")
            print(f"No next room, executing: {else_action}")
            
            if else_action == "show_message":
                self.execute_show_message_action(instance, {
                    "message": "This is the last room!",
                    "title": "No Next Room",
                    "button_text": "OK"
                })
            elif else_action == "change_room":
                else_room = parameters.get("else_room", "Room01")
                self.execute_change_room_action(instance, {
                    "room_name": else_room
                })
            elif else_action != "nothing":
                self.execute_action(instance, {
                    "action": else_action,
                    "parameters": {}
                })

    def execute_if_previous_room_exists_action(self, instance, parameters: Dict[str, Any]):
        """Check if previous room exists and execute appropriate action"""
        room_list = self.get_room_list()
        current_index = self.get_current_room_index()
        
        has_previous = current_index > 0
        
        if has_previous:
            then_action = parameters.get("then_action", "previous_room")
            print(f"Previous room exists, executing: {then_action}")
            
            if then_action == "previous_room":
                self.execute_previous_room_action(instance, {})
            elif then_action == "show_message":
                previous_room_name = room_list[current_index - 1]
                self.execute_show_message_action(instance, {
                    "message": f"Previous room is: {previous_room_name}",
                    "title": "Previous Room Available",
                    "button_text": "OK"
                })
            else:
                self.execute_action(instance, {
                    "action": then_action,
                    "parameters": {}
                })
        else:
            else_action = parameters.get("else_action", "show_message")
            print(f"No previous room, executing: {else_action}")
            
            if else_action == "show_message":
                self.execute_show_message_action(instance, {
                    "message": "This is the first room!",
                    "title": "No Previous Room",
                    "button_text": "OK"
                })
            elif else_action == "change_room":
                else_room = parameters.get("else_room", "Room01")
                self.execute_change_room_action(instance, {
                    "room_name": else_room
                })
            elif else_action != "nothing":
                self.execute_action(instance, {
                    "action": else_action,
                    "parameters": {}
                })

    def resolve_value(self, value: Any, instance, other=None) -> Any:
        """
        Resolve a value that might contain property references
        
        Supports:
        - self.x, self.y, self.hspeed, self.vspeed, self.speed, self.direction
        - other.x, other.y, other.hspeed, other.vspeed, other.speed, other.direction
        - Literal values: 32, "hello", 5.5
        - Expressions: "self.x + 32", "self.x + other.hspeed", "self.y + self.vspeed * 2"
        """
        if not isinstance(value, str):
            return value  # Literal number/bool
        
        # Remove whitespace
        value = value.strip()
        
        # Try to parse as number first
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Check for simple property references (no operators)
        if value.startswith('self.') and not any(op in value for op in ['+', '-', '*', '/', '(', ')']):
            property_name = value[5:]  # Remove 'self.'
            result = getattr(instance, property_name, 0)
            print(f"    Resolved {value} = {result}")
            return result
        
        elif value.startswith('other.') and not any(op in value for op in ['+', '-', '*', '/', '(', ')']):
            if other is None:
                print(f"⚠️ Warning: 'other' not available in this context")
                return 0
            property_name = value[6:]  # Remove 'other.'
            result = getattr(other, property_name, None)
            print(f"    Resolved {value} = {result}")
            return result if result is not None else 0
        
        # Check for expressions (self.x + 32, etc.)
        elif 'self.' in value or 'other.' in value:
            try:
                # Replace self.* references
                eval_str = value
                import re
                
                # Replace self.* references
                for match in re.finditer(r'self\.(\w+)', value):
                    prop = match.group(1)
                    val = getattr(instance, prop, 0)
                    eval_str = eval_str.replace(f'self.{prop}', str(val))
                
                # Replace other.* references
                if other:
                    for match in re.finditer(r'other\.(\w+)', value):
                        prop = match.group(1)
                        val = getattr(other, prop, 0)
                        eval_str = eval_str.replace(f'other.{prop}', str(val))
                
                # Evaluate the expression safely (restricted builtins)
                result = eval(eval_str, {"__builtins__": {}}, {})
                print(f"    Resolved expression '{value}' = {result}")
                return result
            except Exception as e:
                print(f"⚠️ Error evaluating expression '{value}': {e}")
                return 0
        
        # Return as string
        return value

    def execute_push_object_action(self, instance, parameters: Dict[str, Any], other=None):
        """Push another object in a direction - checks for ALL objects at destination"""
        target = parameters.get("target", "other")
        direction = parameters.get("direction", "right")
        distance = parameters.get("distance", 32)
        check_collision = parameters.get("check_collision", True)
        
        # Resolve distance (might be expression)
        distance = self.resolve_value(distance, instance, other)
        
        print(f"PUSH_OBJECT: {instance.object_name} pushing {target} {direction} by {distance}px")
        
        # Get target object
        target_obj = None
        if target == "other" and other:
            target_obj = other
        elif target == "self":
            target_obj = instance
        
        if not target_obj:
            print(f"  ⚠️ No target object to push")
            return False
        
        # Calculate push offset
        dx, dy = 0, 0
        if direction == "right": dx = distance
        elif direction == "left": dx = -distance
        elif direction == "up": dy = -distance
        elif direction == "down": dy = distance
        
        new_x = target_obj.x + dx
        new_y = target_obj.y + dy
        
        # Check if destination is free
        if check_collision:
            # Check if any OTHER object (except pusher and target) is at destination
            destination_blocked = False
            
            for obj in self.room_instances:
                # Skip pusher, target, and destroyed objects
                if obj == instance or obj == target_obj or obj.to_destroy:
                    continue
                
                # Check if this object is at the destination position
                if abs(obj.x - new_x) < 16 and abs(obj.y - new_y) < 16:
                    # Found an object at destination!
                    # Block if it's solid OR if it's a pushable object (box, crate, etc.)
                    if (obj.object_data and obj.object_data.get('solid', False)) or \
                    obj.object_name in ['obj_box', 'obj_crate', 'obj_pushable', 'obj_box_store']:
                        print(f"  ❌ Cannot push - destination blocked by {obj.object_name}")
                        destination_blocked = True
                        break
            
            if not destination_blocked:
                # Move the object
                target_obj.x = new_x
                target_obj.y = new_y
                print(f"  ✅ Pushed {target_obj.object_name} to ({new_x}, {new_y})")
                
                # Check for collisions at the new position
                for obj in self.room_instances:
                    if obj == target_obj or obj == instance or obj.to_destroy:
                        continue
                    
                    # Check if target object is now colliding with another object
                    if abs(obj.x - new_x) < 16 and abs(obj.y - new_y) < 16:
                        print(f"  🎯 COLLISION: {target_obj.object_name} hit {obj.object_name}")
                        # Trigger collision event on the pushed object
                        self.trigger_collision_event(target_obj, obj)
                
                return True
            else:
                return False
        else:
            target_obj.x = new_x
            target_obj.y = new_y
            print(f"  ✅ Pushed {target_obj.object_name} to ({new_x}, {new_y}) (no collision check)")
            return True    

    def execute_snap_to_grid_action(self, instance, parameters: Dict[str, Any], other=None):
        """Snap instance to nearest grid position"""
        grid_size = int(parameters.get("grid_size", 32))
        
        old_x, old_y = instance.x, instance.y
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size
        
        print(f"SNAP_TO_GRID: {instance.object_name} ({old_x}, {old_y}) → ({instance.x}, {instance.y})")

    def execute_if_place_free_action(self, instance, parameters: Dict[str, Any], other=None):
        """Check if a position is collision-free (with expression support)"""
        x_expr = parameters.get("x", "self.x")
        y_expr = parameters.get("y", "self.y")
        then_action = parameters.get("then_action", "")
        else_action = parameters.get("else_action", "")
        
        # Resolve coordinates using expression evaluator
        x = self.resolve_value(x_expr, instance, other)
        y = self.resolve_value(y_expr, instance, other)
        
        print(f"IF_PLACE_FREE: Checking position ({x}, {y})")
        print(f"  Expression X: '{x_expr}' = {x}")
        print(f"  Expression Y: '{y_expr}' = {y}")
        
        # Check if position is free
        is_free = not self.check_collision_at_position(instance, x, y)
        
        print(f"  Position is {'FREE' if is_free else 'BLOCKED'}")
        
        # Execute appropriate action
        if is_free and then_action:
            self.execute_action(instance, {"action": then_action, "parameters": parameters}, other)
        elif not is_free and else_action:
            self.execute_action(instance, {"action": else_action, "parameters": parameters}, other)

    def execute_move_to_position_action(self, instance, parameters: Dict[str, Any], other=None):
        """Move instance to a specific position"""
        x_str = parameters.get("x", "self.x")
        y_str = parameters.get("y", "self.y")
        smooth = parameters.get("smooth", False)
        
        # Resolve coordinates
        new_x = self.resolve_value(x_str, instance, other)
        new_y = self.resolve_value(y_str, instance, other)
        
        print(f"MOVE_TO_POSITION: {instance.object_name} → ({new_x}, {new_y}), smooth={smooth}")
        
        if smooth:
            # Use grid movement animation
            instance.target_x = new_x
            instance.target_y = new_y
        else:
            # Instant movement
            instance.x = new_x
            instance.y = new_y

    def execute_if_collision_at_action(self, instance, parameters: Dict[str, Any], other=None):
        """Check for collision at a position (with expression support) - supports multiple actions"""
        x_expr = parameters.get("x", "self.x + 32")
        y_expr = parameters.get("y", "self.y")
        object_type = parameters.get("object_type", "any")
        then_actions = parameters.get("then_actions", [])
        else_actions = parameters.get("else_actions", [])
        
        # Resolve coordinates using expression evaluator
        check_x = self.resolve_value(x_expr, instance, other)
        check_y = self.resolve_value(y_expr, instance, other)
        
        print(f"IF_COLLISION_AT: {instance.object_name} checking position ({check_x}, {check_y}) for type: {object_type}")
        
        # Check for collision
        collision_found = False
        colliding_object = None
        
        for obj in self.room_instances:
            if obj == instance or obj.to_destroy:
                continue
            
            # Check if this object is at the check position
            if abs(obj.x - check_x) < 16 and abs(obj.y - check_y) < 16:
                # Check object type filter
                if object_type == "any":
                    collision_found = True
                    colliding_object = obj
                    break
                elif object_type == "solid":  # ← ADD THIS
                    # Check if object is solid
                    if obj.object_data and obj.object_data.get('solid', False):
                        collision_found = True
                        colliding_object = obj
                        print(f"  Found solid object: {obj.object_name}")
                        break
                elif obj.object_name == object_type:
                    collision_found = True
                    colliding_object = obj
                    break
        
        print(f"  Collision {'FOUND' if collision_found else 'NOT FOUND'}")
        
        # Execute appropriate actions
        if collision_found and then_actions:
            print(f"  Executing {len(then_actions)} THEN actions")
            
            # Pass the colliding object as 'other' context
            instance._collision_other = colliding_object
            
            for action_data in then_actions:
                self.execute_action(instance, action_data, colliding_object)
            
            instance._collision_other = None
            
        elif not collision_found and else_actions:
            print(f"  Executing {len(else_actions)} ELSE actions")
            
            for action_data in else_actions:
                self.execute_action(instance, action_data, other)

    def execute_set_hspeed_action(self, instance, parameters: Dict[str, Any], other=None):
        """Set horizontal speed component"""
        speed_str = parameters.get("speed", "0")
        speed = self.resolve_value(speed_str, instance, other)
        
        instance.hspeed = float(speed)
        print(f"SET_HSPEED: {instance.object_name}.hspeed = {instance.hspeed}")

    def execute_set_vspeed_action(self, instance, parameters: Dict[str, Any], other=None):
        """Set vertical speed component"""
        speed_str = parameters.get("speed", "0")
        speed = self.resolve_value(speed_str, instance, other)
        
        instance.vspeed = float(speed)
        print(f"SET_VSPEED: {instance.object_name}.vspeed = {instance.vspeed}")