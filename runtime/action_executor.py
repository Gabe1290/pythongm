#!/usr/bin/env python3
"""
Action Execution Engine - WITH GRID SNAPPING
Converts visual actions into runtime behavior
"""

import math
from typing import Dict, Any, List, Optional

class ActionExecutor:
    """Executes visual actions during gameplay with auto-discovery"""

    def __init__(self, game_runner=None):
        # Action handlers dictionary - auto-populated via discovery
        self.action_handlers = {}

        # Reference to game runner for accessing global state (score, lives, health)
        self.game_runner = game_runner

        # Auto-discover all action handler methods
        self._register_action_handlers()

        print(f"✅ ActionExecutor initialized with {len(self.action_handlers)} action handlers")

    def _register_action_handlers(self):
        """Automatically discover and register action handler methods

        Any method named execute_*_action will be automatically registered
        as a handler for the action name (the part between execute_ and _action)

        Example: execute_move_grid_action -> handles "move_grid" action
        """
        for attr_name in dir(self):
            # Look for methods matching the pattern execute_*_action
            if attr_name.startswith('execute_') and attr_name.endswith('_action'):
                # Extract action name: execute_move_grid_action -> move_grid
                action_name = attr_name[8:-7]  # Remove 'execute_' and '_action'

                # Get the method
                method = getattr(self, attr_name)

                # Verify it's callable
                if callable(method):
                    self.action_handlers[action_name] = method
                    print(f"  📌 Registered action handler: {action_name}")

    def register_custom_action(self, action_name: str, handler_func):
        """Register a custom action handler dynamically (for plugins)

        Args:
            action_name: The action name (e.g., 'play_sound')
            handler_func: A function with signature (instance, parameters) -> None
        """
        self.action_handlers[action_name] = handler_func
        print(f"  🔌 Registered custom action: {action_name}")
    
    def execute_event(self, instance, event_name: str, events_data: Dict[str, Any]):
        """Execute all actions in an event"""
        if event_name not in events_data:
            return

        event_data = events_data[event_name]
        actions = event_data.get("actions", [])

        # DEBUG: Show which event is being executed
        if event_name == "create":
            print(f"🎬 Executing CREATE event for {instance.__class__.__name__}")
            print(f"   Actions: {len(actions)} action(s)")
            if actions:
                print(f"   First action: {actions[0].get('action', 'unknown')}")

        # Execute actions with conditional flow support
        self.execute_action_list(instance, actions)

    def execute_action_list(self, instance, actions: list):
        """Execute a list of actions with conditional flow support

        GM80-style conditionals: test actions set skip_next flag to skip following action(s)
        """
        i = 0
        skip_next = False
        condition_was_false = False  # Track if original condition was false

        while i < len(actions):
            action_data = actions[i]
            action_name = action_data.get("action", "")

            # Handle else action (supports both else_action and else_block)
            if action_name in ("else_action", "else_block", "else"):
                # If the condition was false, we skipped the "then" part, so execute the "else" part
                # If the condition was true, we executed the "then" part, so skip the "else" part
                skip_next = not condition_was_false
                i += 1
                continue

            # Handle start_block - if we're skipping, skip the entire block
            if action_name in ("start_block", "start"):
                if skip_next:
                    # Skip until matching end_block
                    block_depth = 1
                    i += 1
                    while i < len(actions) and block_depth > 0:
                        next_action = actions[i].get("action", "")
                        if next_action in ("start_block", "start"):
                            block_depth += 1
                        elif next_action in ("end_block", "end"):
                            block_depth -= 1
                        i += 1
                    skip_next = False
                    condition_was_false = True  # Block was skipped
                    continue
                i += 1
                continue

            # Handle end_block - reset conditional state
            if action_name in ("end_block", "end"):
                skip_next = False
                condition_was_false = False
                i += 1
                continue

            # Skip this action if skip_next is set (for single actions)
            if skip_next:
                skip_next = False
                i += 1
                continue

            # Handle repeat action specially
            if action_name == "repeat":
                i = self._handle_repeat_action(instance, actions, i, action_data)
                continue

            # Execute the action
            result = self.execute_action(instance, action_data)

            # Check if this was a conditional action that returned False
            # Conditional actions return True/False, regular actions return None
            if result is False:
                skip_next = True
                condition_was_false = True
            elif result is True:
                condition_was_false = False

            i += 1

    def _handle_repeat_action(self, instance, actions: list, current_index: int, action_data: dict) -> int:
        """Handle the repeat action - executes following action(s) N times

        Returns the index to continue from after the repeated actions
        """
        parameters = action_data.get("parameters", {})
        times_param = parameters.get("times", "1")

        # Parse the times parameter (can be a number or variable)
        times = self._parse_value(str(times_param), instance)
        if not isinstance(times, (int, float)):
            print(f"⚠️ Repeat: Invalid times value '{times_param}', defaulting to 1")
            times = 1
        times = int(times)

        if times <= 0:
            # Skip the next action(s) entirely
            next_index = current_index + 1
            if next_index < len(actions):
                next_action = actions[next_index].get("action", "")
                if next_action == "start_block":
                    # Skip the entire block
                    return self._find_matching_end_block(actions, next_index) + 1
                else:
                    # Skip just the next action
                    return next_index + 1
            return current_index + 1

        # Find the actions to repeat
        next_index = current_index + 1
        if next_index >= len(actions):
            return next_index

        next_action = actions[next_index].get("action", "")

        if next_action == "start_block":
            # Repeat a block of actions
            end_block_index = self._find_matching_end_block(actions, next_index)
            block_actions = actions[next_index + 1:end_block_index]  # Actions between { and }

            print(f"🔁 Repeat block {times} times ({len(block_actions)} actions)")
            for iteration in range(times):
                self.execute_action_list(instance, block_actions)

            return end_block_index + 1
        else:
            # Repeat a single action
            single_action = actions[next_index]
            print(f"🔁 Repeat '{next_action}' {times} times")
            for iteration in range(times):
                self.execute_action(instance, single_action)

            return next_index + 1

    def _find_matching_end_block(self, actions: list, start_block_index: int) -> int:
        """Find the index of the matching end_block for a start_block"""
        depth = 1
        i = start_block_index + 1

        while i < len(actions) and depth > 0:
            action_name = actions[i].get("action", "")
            if action_name == "start_block":
                depth += 1
            elif action_name in ("end_block", "end"):
                depth -= 1
            i += 1

        return i - 1  # Return the index of the end_block
    
    # Action name aliases for compatibility between different naming conventions
    ACTION_ALIASES = {
        "display_message": "show_message",
        "message": "show_message",
        "goto_next_room": "next_room",
        "goto_previous_room": "previous_room",
        "goto_room": "next_room",  # Will be handled specially if room_name param exists
    }

    def execute_action(self, instance, action_data: Dict[str, Any]):
        """Execute a single action with validation

        Returns:
            - True if action is a conditional that evaluated to True
            - False if action is a conditional that evaluated to False
            - None for non-conditional actions
        """
        action_name = action_data.get("action", "")
        parameters = action_data.get("parameters", {})

        if not action_name:
            print(f"⚠️ Action missing 'action' field: {action_data}")
            return None

        # Apply action name aliases
        if action_name in self.ACTION_ALIASES:
            action_name = self.ACTION_ALIASES[action_name]

        if action_name not in self.action_handlers:
            print(f"❌ Unknown action: {action_name}")
            print(f"   Available actions: {', '.join(sorted(self.action_handlers.keys()))}")
            return None

        # Validate instance has required attributes for this action
        if not self._validate_action_requirements(instance, action_name):
            print(f"⚠️ Instance missing requirements for action '{action_name}'")
            return None

        # Execute the action with error handling
        try:
            result = self.action_handlers[action_name](instance, parameters)
            return result  # Return result for conditional flow
        except AttributeError as e:
            print(f"❌ Attribute error in action {action_name}: {e}")
            print(f"   Instance may be missing required attributes")
            return None
        except Exception as e:
            print(f"❌ Error executing action {action_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _validate_action_requirements(self, instance, action_name: str) -> bool:
        """Validate that instance has required attributes for an action

        Returns:
            True if instance meets requirements, False otherwise
        """
        # Define required attributes for each action category
        requirements = {
            # Movement actions need position and speed attributes
            "move_grid": ["x", "y"],
            "set_hspeed": ["hspeed"],
            "set_vspeed": ["vspeed"],
            "stop_movement": ["hspeed", "vspeed"],
            "start_moving_direction": ["hspeed", "vspeed"],

            # Grid actions need position
            "snap_to_grid": ["x", "y"],
            "if_on_grid": ["x", "y"],
            "stop_if_no_keys": ["x", "y", "hspeed", "vspeed"],
            "check_keys_and_move": ["x", "y", "hspeed", "vspeed"],

            # Most actions work with any instance
            "show_message": [],
            "restart_room": [],
            "next_room": [],
            "destroy_instance": [],
            "if_collision_at": ["x", "y"],
        }

        # Get required attributes for this action
        required_attrs = requirements.get(action_name, [])

        # Check if instance has all required attributes
        for attr in required_attrs:
            if not hasattr(instance, attr):
                print(f"   Missing attribute: {attr}")
                return False

        return True
    
    # ==================== GRID-BASED MOVEMENT ====================
    
    def execute_move_grid_action(self, instance, parameters: Dict[str, Any]):
        """Execute grid-based movement (instant snap)"""
        direction = parameters.get("direction", "right")
        grid_size = int(parameters.get("grid_size", 32))
        
        # Calculate movement based on direction
        dx, dy = 0, 0
        if direction == "right":
            dx = grid_size
        elif direction == "left":
            dx = -grid_size
        elif direction == "up":
            dy = -grid_size
        elif direction == "down":
            dy = grid_size
        
        # Store intended movement for collision checking by game_runner
        instance.intended_x = instance.x + dx
        instance.intended_y = instance.y + dy
    
    # ==================== SPEED-BASED MOVEMENT ====================
    
    def execute_set_hspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set horizontal speed for smooth movement

        Accepts numbers or variable references like other.hspeed
        """
        # Accept 'hspeed', 'value', or 'speed' parameters
        speed_value = parameters.get("hspeed", parameters.get("value", parameters.get("speed", "0")))
        print(f"  🔍 set_hspeed: raw value = '{speed_value}', _collision_other = {getattr(self, '_collision_other', None)}")
        speed = self._parse_value(str(speed_value), instance)
        print(f"  🔍 set_hspeed: parsed value = {speed}")
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            print(f"⚠️  set_hspeed: Invalid speed value '{speed_value}'")
            return
        old_speed = instance.hspeed
        instance.hspeed = speed
        # Only print when speed changes
        if old_speed != speed:
            print(f"  🏃 {instance.object_name} hspeed: {old_speed} → {speed}")

    def execute_set_vspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set vertical speed for smooth movement

        Accepts numbers or variable references like other.vspeed
        """
        # Accept 'vspeed', 'value', or 'speed' parameters
        speed_value = parameters.get("vspeed", parameters.get("value", parameters.get("speed", "0")))
        print(f"  🔍 set_vspeed: raw value = '{speed_value}', _collision_other = {getattr(self, '_collision_other', None)}")
        speed = self._parse_value(str(speed_value), instance)
        print(f"  🔍 set_vspeed: parsed value = {speed}")
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            print(f"⚠️  set_vspeed: Invalid speed value '{speed_value}'")
            return
        old_speed = instance.vspeed
        instance.vspeed = speed
        # Only print when speed changes
        if old_speed != speed:
            print(f"  🏃 {instance.object_name} vspeed: {old_speed} → {speed}")
    
    def execute_stop_movement_action(self, instance, parameters: Dict[str, Any]):
        """Stop all movement by setting speeds to zero"""
        instance.hspeed = 0
        instance.vspeed = 0

    def execute_jump_to_position_action(self, instance, parameters: Dict[str, Any]):
        """Jump to a specific position instantly

        Supports expressions like other.x, self.hspeed*8, etc.
        With 'relative' option, adds to current position instead of setting absolute.
        """
        x_expr = str(parameters.get("x", "0"))
        y_expr = str(parameters.get("y", "0"))
        relative = parameters.get("relative", False)

        # Debug: Show stored collision speeds
        collision_speeds = getattr(self, '_collision_speeds', {})
        if collision_speeds:
            print(f"  🔍 jump_to_position: Using collision speeds: {collision_speeds}")

        # Evaluate X expression
        try:
            x_value = self._parse_value(x_expr, instance)
            print(f"  🔍 X expression '{x_expr}' evaluated to: {x_value}")
            if x_value is None or isinstance(x_value, str):
                x_value = 0
            x_value = float(x_value)
        except Exception as e:
            print(f"⚠️ Error evaluating X expression '{x_expr}': {e}")
            x_value = 0.0

        # Evaluate Y expression
        try:
            y_value = self._parse_value(y_expr, instance)
            print(f"  🔍 Y expression '{y_expr}' evaluated to: {y_value}")
            if y_value is None or isinstance(y_value, str):
                y_value = 0
            y_value = float(y_value)
        except Exception as e:
            print(f"⚠️ Error evaluating Y expression '{y_expr}': {e}")
            y_value = 0.0

        # Apply position
        if relative:
            instance.x += x_value
            instance.y += y_value
            print(f"  📍 {instance.object_name} jumped relatively by ({x_value}, {y_value}) → ({instance.x}, {instance.y})")
        else:
            instance.x = x_value
            instance.y = y_value
            print(f"  📍 {instance.object_name} jumped to ({instance.x}, {instance.y})")

    def execute_start_moving_direction_action(self, instance, parameters: Dict[str, Any]):
        """Start moving in a specific direction

        Direction angles (GameMaker standard):
        - 0° = right
        - 90° = up
        - 180° = left
        - 270° = down

        The 'directions' parameter can be:
        - A list of direction names: ['up', 'down', 'left', 'right', 'up-left', etc.]
        - A single numeric angle (degrees)
        - A string direction name
        - An expression like 'other.direction' or 'self.direction'
        """
        import math
        import random

        # Direction name to angle mapping
        direction_map = {
            'right': 0,
            'up-right': 45,
            'up': 90,
            'up-left': 135,
            'left': 180,
            'down-left': 225,
            'down': 270,
            'down-right': 315,
            'stop': -1  # Special: stop movement
        }

        directions = parameters.get("directions", 0)
        direction_expr = parameters.get("direction_expr", "")
        speed_param = parameters.get("speed", 4.0)

        # Parse speed (supports expressions like other.speed)
        speed = self._parse_value(str(speed_param), instance)
        if not isinstance(speed, (int, float)):
            speed = 4.0
        speed = float(speed)

        # If direction_expr is provided, use it instead of directions buttons
        if direction_expr and isinstance(direction_expr, str) and direction_expr.strip():
            directions = direction_expr.strip()

        # Handle different parameter types
        if isinstance(directions, list):
            if len(directions) == 0:
                # Empty list with no expression = stop
                if not direction_expr:
                    instance.hspeed = 0
                    instance.vspeed = 0
                    print(f"   ➡️ Start Moving Direction: stopped (empty directions)")
                    return
            # Pick random direction from list
            chosen = random.choice(directions)
            if isinstance(chosen, str):
                # Check if it's an expression (contains '.')
                if '.' in chosen:
                    direction = self._parse_value(chosen, instance)
                    if not isinstance(direction, (int, float)):
                        direction = 0
                else:
                    direction = direction_map.get(chosen.lower(), 0)
            else:
                direction = float(chosen)
        elif isinstance(directions, str):
            # Check if it's an expression (like other.direction, self.direction)
            if '.' in directions and directions.lower() not in direction_map:
                direction = self._parse_value(directions, instance)
                if not isinstance(direction, (int, float)):
                    print(f"   ⚠️ Could not evaluate direction expression: {directions}")
                    direction = 0
            else:
                direction = direction_map.get(directions.lower(), 0)
        else:
            direction = float(directions)

        # Handle 'stop' direction
        if direction == -1:
            instance.hspeed = 0
            instance.vspeed = 0
            print(f"   ➡️ Start Moving Direction: stopped")
            return

        # Convert angle to radians (GameMaker uses degrees, 0° is right, 90° is up)
        angle_rad = math.radians(direction)

        # Calculate horizontal and vertical speed components
        # Note: In screen coordinates, y increases downward, so we negate sin
        instance.hspeed = math.cos(angle_rad) * speed
        instance.vspeed = -math.sin(angle_rad) * speed

        # DEBUG
        print(f"   ➡️ Start Moving Direction: {direction}° at speed {speed}")
        print(f"      hspeed={instance.hspeed:.2f}, vspeed={instance.vspeed:.2f}")

    # ==================== GRID UTILITIES ====================
    
    def execute_snap_to_grid_action(self, instance, parameters: Dict[str, Any]):
        """Snap instance to nearest grid position"""
        grid_size = int(parameters.get("grid_size", 32))
        
        # Round to nearest grid position
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size
    
    def execute_if_on_grid_action(self, instance, parameters: Dict[str, Any]):
        """Check if instance is on grid - returns True/False for conditional flow

        Works like other if_ actions - use with start_block/end_block for multiple actions.

        Logic:
        1. Check if instance is CLOSE to grid (with tolerance for floating point errors)
        2. If close, SNAP to exact grid position first
        3. Return True if on grid, False otherwise
        """
        grid_size = int(parameters.get("grid_size", 32))

        # STEP 1: Check if position is close to grid alignment (with tolerance)
        # Use small tolerance (0.5 pixels) to account for floating point precision
        tolerance = 0.5
        x_remainder = abs(instance.x % grid_size)
        y_remainder = abs(instance.y % grid_size)

        # Check if close to grid alignment (either near 0 or near grid_size)
        x_close_to_grid = (x_remainder < tolerance) or (x_remainder > grid_size - tolerance)
        y_close_to_grid = (y_remainder < tolerance) or (y_remainder > grid_size - tolerance)
        close_to_grid = x_close_to_grid and y_close_to_grid

        # STEP 2: If close to grid, snap to EXACT grid position FIRST
        if close_to_grid:
            instance.x = round(instance.x / grid_size) * grid_size
            instance.y = round(instance.y / grid_size) * grid_size

        # STEP 3: Now check if on exact grid (should be true after snapping)
        x_on_grid = (instance.x % grid_size) == 0
        y_on_grid = (instance.y % grid_size) == 0
        on_grid = x_on_grid and y_on_grid

        # Return True/False for conditional flow (like other if_ actions)
        return on_grid
    
    def execute_stop_if_no_keys_action(self, instance, parameters: Dict[str, Any]):
        """Stop movement when on grid (for precise grid-based movement)

        NEW LOGIC (Nov 19, 2025 - Fix overshoot issue):
        - ALWAYS stop movement when this action executes
        - This action is called from step event when player reaches grid
        - Prevents overshoot by forcing stop at every grid position
        - Keyboard events will restart movement on next frame if key still held
        - This creates precise one-grid-cell-at-a-time movement

        Old logic checked if keys were pressed, but this caused overshoot
        because keyboard events fire continuously while key is held.

        Parameters:
            grid_size: Grid cell size (default 32)
        """
        grid_size = int(parameters.get("grid_size", 32))

        # ALWAYS stop movement - don't check keys_pressed
        # This ensures player stops at EVERY grid position
        instance.hspeed = 0
        instance.vspeed = 0

        # Ensure exact grid alignment
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size

    def execute_check_keys_and_move_action(self, instance, parameters: Dict[str, Any]):
        """Check if movement keys are held and restart movement

        This creates precise grid-by-grid movement:
        1. Player stops at every grid position (via stop_if_no_keys)
        2. This action checks if keys are still held
        3. If yes, restart movement in that direction
        4. Player moves to next grid, stops, repeat

        This prevents overshoot while allowing smooth continuous movement
        when keys are held.

        Parameters:
            grid_size: Grid cell size (default 32)
            speed: Movement speed in pixels/frame (default 4)
        """
        grid_size = int(parameters.get("grid_size", 32))
        speed = float(parameters.get("speed", 4.0))

        # Get which keys are currently held down
        keys_pressed = getattr(instance, 'keys_pressed', set())

        # Only restart movement if on exact grid position
        on_grid = (instance.x % grid_size == 0) and (instance.y % grid_size == 0)
        if not on_grid:
            return

        # Set speed based on held keys (priority: horizontal over vertical)
        if "right" in keys_pressed:
            instance.hspeed = speed
            instance.vspeed = 0
        elif "left" in keys_pressed:
            instance.hspeed = -speed
            instance.vspeed = 0
        elif "up" in keys_pressed:
            instance.hspeed = 0
            instance.vspeed = -speed
        elif "down" in keys_pressed:
            instance.hspeed = 0
            instance.vspeed = speed
        # else: no keys pressed, movement already stopped by stop_if_no_keys

    # ==================== CONTROL ACTIONS ====================

    def execute_if_collision_action(self, instance, parameters: Dict[str, Any]):
        """Execute collision check (GameMaker-style)

        Supports:
        - 'any': Check for collision with any object
        - 'solid': Check for collision with solid objects only
        - specific object name: Check for collision with that object type

        X and Y can be expressions like "other.hspeed*8" or plain numbers.

        Returns True if condition is met (next action executes), False otherwise.
        """
        x_expr = str(parameters.get("x", "0"))
        y_expr = str(parameters.get("y", "0"))
        object_type = parameters.get("object", "any")
        not_flag = parameters.get("not_flag", False)

        # Debug: Show stored collision speeds
        collision_speeds = getattr(self, '_collision_speeds', {})
        if collision_speeds:
            print(f"  🔍 if_collision: Using collision speeds: {collision_speeds}")

        # Evaluate X offset expression using _parse_value
        try:
            x_offset = self._parse_value(x_expr, instance)
            print(f"  🔍 X expression '{x_expr}' evaluated to: {x_offset}")
            if x_offset is None or isinstance(x_offset, str):
                x_offset = 0
            x_offset = float(x_offset)
        except Exception as e:
            print(f"⚠️ Error evaluating X expression '{x_expr}': {e}")
            x_offset = 0.0

        # Evaluate Y offset expression using _parse_value
        try:
            y_offset = self._parse_value(y_expr, instance)
            print(f"  🔍 Y expression '{y_expr}' evaluated to: {y_offset}")
            if y_offset is None or isinstance(y_offset, str):
                y_offset = 0
            y_offset = float(y_offset)
        except Exception as e:
            print(f"⚠️ Error evaluating Y expression '{y_expr}': {e}")
            y_offset = 0.0

        # Calculate check position
        check_x = instance.x + x_offset
        check_y = instance.y + y_offset

        # Perform the collision check using game_runner
        # Exclude the "other" instance from collision events (e.g., when rock checks for
        # collisions while being pushed by explorer, don't count the explorer itself)
        has_collision = False
        exclude_instance = getattr(self, '_collision_other', None)
        if self.game_runner:
            has_collision = self.game_runner.check_collision_at_position(
                instance, check_x, check_y, object_type, exclude_instance
            )
        else:
            print(f"  ⚠️ if_collision: game_runner is None! Cannot check collisions.")

        # Apply NOT flag
        result = not has_collision if not_flag else has_collision

        print(f"  ❓ if_collision at ({check_x}, {check_y}) for '{object_type}': collision={has_collision}, not_flag={not_flag}, result={result}")

        return result

    def execute_if_collision_at_action(self, instance, parameters: Dict[str, Any]):
        """Execute collision check with conditional actions"""
        x_expr = parameters.get("x", "self.x")
        y_expr = parameters.get("y", "self.y")
        object_type = parameters.get("object_type", parameters.get("object", "any"))
        then_actions = parameters.get("then_actions", [])
        else_actions = parameters.get("else_actions", [])

        # Store collision check for game_runner to process
        if not hasattr(instance, 'collision_checks'):
            instance.collision_checks = []

        instance.collision_checks.append({
            'x': x_expr,
            'y': y_expr,
            'object_type': object_type,
            'then_actions': then_actions,
            'else_actions': else_actions
        })
    
    # ==================== GAME ACTIONS ====================
    
    def execute_show_message_action(self, instance, parameters: Dict[str, Any]):
        """Execute show message action"""
        message = parameters.get("message", "")
        print(f"💬 MESSAGE: {message}")
        
        # Store message for game runner to display
        if not hasattr(instance, 'pending_messages'):
            instance.pending_messages = []
        instance.pending_messages.append(message)
    
    def execute_restart_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute restart room action - resets current level"""
        print(f"🔄 Restart room requested by {instance.object_name}")
        instance.restart_room_flag = True
    
    def execute_next_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute next room action - advances to next level"""
        print(f"➡️  Next room requested by {instance.object_name}")
        instance.next_room_flag = True

    def execute_previous_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute previous room action - goes to previous level"""
        print(f"⬅️  Previous room requested by {instance.object_name}")
        instance.previous_room_flag = True

    def execute_if_next_room_exists_action(self, instance, parameters: Dict[str, Any]):
        """Check if next room exists

        This is a conditional action:
        - Returns True if next room exists (next action will execute)
        - Returns False if no next room (next action will be skipped)

        Also supports nested then_actions/else_actions for Blockly-style conditionals.
        """
        if not self.game_runner:
            print("⚠️  Warning: if_next_room_exists requires game_runner reference")
            return False

        room_list = self.game_runner.get_room_list()
        current_room = self.game_runner.current_room

        next_exists = False
        if current_room and room_list:
            try:
                current_index = room_list.index(current_room.name)
                next_exists = (current_index + 1) < len(room_list)
            except ValueError:
                pass

        print(f"❓ Next room exists: {next_exists}")

        # If there are nested actions (Blockly-style), execute them
        then_actions = parameters.get('then_actions', [])
        else_actions = parameters.get('else_actions', [])

        if then_actions or else_actions:
            if next_exists:
                for action in then_actions:
                    self.execute_action(instance, action)
            else:
                for action in else_actions:
                    self.execute_action(instance, action)
            return None  # Don't affect next action flow

        # Return result for GM80-style conditional flow
        return next_exists

    def execute_if_previous_room_exists_action(self, instance, parameters: Dict[str, Any]):
        """Check if previous room exists

        This is a conditional action:
        - Returns True if previous room exists (next action will execute)
        - Returns False if no previous room (next action will be skipped)

        Also supports nested then_actions/else_actions for Blockly-style conditionals.
        """
        if not self.game_runner:
            print("⚠️  Warning: if_previous_room_exists requires game_runner reference")
            return False

        room_list = self.game_runner.get_room_list()
        current_room = self.game_runner.current_room

        prev_exists = False
        if current_room and room_list:
            try:
                current_index = room_list.index(current_room.name)
                prev_exists = current_index > 0
            except ValueError:
                pass

        print(f"❓ Previous room exists: {prev_exists}")

        # If there are nested actions (Blockly-style), execute them
        then_actions = parameters.get('then_actions', [])
        else_actions = parameters.get('else_actions', [])

        if then_actions or else_actions:
            if prev_exists:
                for action in then_actions:
                    self.execute_action(instance, action)
            else:
                for action in else_actions:
                    self.execute_action(instance, action)
            return None  # Don't affect next action flow

        # Return result for GM80-style conditional flow
        return prev_exists

    # ==================== VARIABLE ACTIONS ====================

    def _parse_value(self, value_str: str, instance=None):
        """Parse a value string into appropriate type (number, string, or expression result)

        Supports:
        - Numbers: 42, 3.14, -5
        - Booleans: true, false
        - Strings: "hello", 'world'
        - Variable references: hspeed, my_var
        - Scoped references: self.hspeed, other.hspeed, global.my_var
        """
        if not isinstance(value_str, str):
            return value_str

        value_str = value_str.strip()

        # Try to parse as integer
        try:
            return int(value_str)
        except ValueError:
            pass

        # Try to parse as float
        try:
            return float(value_str)
        except ValueError:
            pass

        # Check for boolean
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # Check for scoped variable references (self.var, other.var, global.var)
        if '.' in value_str and not value_str.startswith('"') and not value_str.startswith("'"):
            parts = value_str.split('.', 1)
            if len(parts) == 2:
                scope, var_name = parts
                scope = scope.lower()

                # Get stored collision speeds (if in a collision event)
                collision_speeds = getattr(self, '_collision_speeds', {})

                if scope == 'self' and instance:
                    # For collision events, use stored collision speed if available
                    if var_name == 'hspeed' and 'self_hspeed' in collision_speeds:
                        return collision_speeds['self_hspeed']
                    elif var_name == 'vspeed' and 'self_vspeed' in collision_speeds:
                        return collision_speeds['self_vspeed']
                    elif hasattr(instance, var_name):
                        return getattr(instance, var_name)
                    # Special handling for 'direction' - compute from hspeed/vspeed
                    elif var_name == 'direction':
                        import math
                        hspeed = collision_speeds.get('self_hspeed', getattr(instance, 'hspeed', 0))
                        vspeed = collision_speeds.get('self_vspeed', getattr(instance, 'vspeed', 0))
                        if hspeed == 0 and vspeed == 0:
                            return 0  # No movement, default to right
                        # GameMaker convention: 0° = right, 90° = up
                        # vspeed is negated because screen y increases downward
                        return math.degrees(math.atan2(-vspeed, hspeed)) % 360
                elif scope == 'other':
                    # For collision events, use stored collision speed if available
                    if var_name == 'hspeed' and 'other_hspeed' in collision_speeds:
                        return collision_speeds['other_hspeed']
                    elif var_name == 'vspeed' and 'other_vspeed' in collision_speeds:
                        return collision_speeds['other_vspeed']
                    else:
                        other = getattr(self, '_collision_other', None)
                        if other:
                            if hasattr(other, var_name):
                                return getattr(other, var_name)
                            # Special handling for 'direction' - compute from hspeed/vspeed
                            elif var_name == 'direction':
                                import math
                                hspeed = collision_speeds.get('other_hspeed', getattr(other, 'hspeed', 0))
                                vspeed = collision_speeds.get('other_vspeed', getattr(other, 'vspeed', 0))
                                if hspeed == 0 and vspeed == 0:
                                    return 0  # No movement, default to right
                                # GameMaker convention: 0° = right, 90° = up
                                # vspeed is negated because screen y increases downward
                                return math.degrees(math.atan2(-vspeed, hspeed)) % 360
                elif scope == 'global' and self.game_runner:
                    if var_name in self.game_runner.global_variables:
                        return self.game_runner.global_variables[var_name]

        # Check for simple variable reference (no dot)
        if instance and not value_str.startswith('"') and not value_str.startswith("'"):
            # Try to get instance variable
            if hasattr(instance, value_str):
                return getattr(instance, value_str)
            # Try global variable
            if self.game_runner and value_str in self.game_runner.global_variables:
                return self.game_runner.global_variables[value_str]

        # Check if this is an arithmetic expression (contains operators)
        if any(op in value_str for op in ['*', '+', '-', '/', '%']) and not value_str.startswith('"'):
            # Evaluate arithmetic expression
            return self._evaluate_expression(value_str, instance)

        # Return as string (strip quotes if present)
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]

        return value_str

    def _evaluate_expression(self, expr_str: str, instance=None):
        """Evaluate an arithmetic expression with variable substitution

        Supports expressions like:
        - other.hspeed*8
        - self.x + 32
        - other.vspeed * -1
        - hspeed*16 (bare variable names treated as self.)
        """
        import re

        # Replace scoped variable references with their values (self.x, other.hspeed, etc.)
        def replace_scoped_var(match):
            var_ref = match.group(0)
            value = self._get_variable_value(var_ref, instance)
            if value is not None:
                return str(value)
            return var_ref

        # Pattern to match scoped variable references like self.x, other.hspeed, etc.
        scoped_var_pattern = r'(self|other|global)\.\w+'
        expr_substituted = re.sub(scoped_var_pattern, replace_scoped_var, expr_str)

        # Replace bare variable names (hspeed, vspeed, x, y, etc.) with their instance values
        def replace_bare_var(match):
            var_name = match.group(0)
            # Skip if it's a number or already processed
            if var_name.isdigit():
                return var_name
            # Check if instance has this attribute
            if instance and hasattr(instance, var_name):
                # For collision speeds, check stored values first
                collision_speeds = getattr(self, '_collision_speeds', {})
                if var_name == 'hspeed' and 'self_hspeed' in collision_speeds:
                    return str(collision_speeds['self_hspeed'])
                elif var_name == 'vspeed' and 'self_vspeed' in collision_speeds:
                    return str(collision_speeds['self_vspeed'])
                return str(getattr(instance, var_name))
            return var_name

        # Pattern to match bare variable names (word characters not preceded by a dot)
        # Only match words that aren't already part of a scoped reference
        bare_var_pattern = r'(?<![.\w])\b([a-zA-Z_]\w*)\b(?!\s*\.)'
        expr_substituted = re.sub(bare_var_pattern, replace_bare_var, expr_substituted)

        # Try to evaluate the expression safely
        try:
            # Only allow safe characters for eval
            if re.match(r'^[\d\s\+\-\*\/\%\(\)\.]+$', expr_substituted):
                result = eval(expr_substituted)
                return result
            else:
                print(f"⚠️ Unsafe expression: {expr_substituted}")
                return 0
        except Exception as e:
            print(f"⚠️ Error evaluating expression '{expr_str}': {e}")
            return 0

    def _get_variable_value(self, var_ref: str, instance=None):
        """Get the value of a variable reference like self.x, other.hspeed

        For collision events, uses stored collision speeds (captured at collision time)
        instead of current speeds which may have been modified by other collision handlers.
        """
        if '.' not in var_ref:
            return None

        parts = var_ref.split('.', 1)
        if len(parts) != 2:
            return None

        scope, var_name = parts
        scope = scope.lower()

        if scope == 'self' and instance:
            # For collision events, use stored collision speed if available
            collision_speeds = getattr(self, '_collision_speeds', {})
            if var_name == 'hspeed' and 'self_hspeed' in collision_speeds:
                return collision_speeds['self_hspeed']
            elif var_name == 'vspeed' and 'self_vspeed' in collision_speeds:
                return collision_speeds['self_vspeed']
            elif hasattr(instance, var_name):
                return getattr(instance, var_name)
        elif scope == 'other':
            # For collision events, use stored collision speed if available
            collision_speeds = getattr(self, '_collision_speeds', {})
            if var_name == 'hspeed' and 'other_hspeed' in collision_speeds:
                return collision_speeds['other_hspeed']
            elif var_name == 'vspeed' and 'other_vspeed' in collision_speeds:
                return collision_speeds['other_vspeed']
            else:
                other = getattr(self, '_collision_other', None)
                if other and hasattr(other, var_name):
                    return getattr(other, var_name)
        elif scope == 'global' and self.game_runner:
            if var_name in self.game_runner.global_variables:
                return self.game_runner.global_variables[var_name]

        return 0  # Default to 0 for unknown variables

    def execute_set_variable_action(self, instance, parameters: Dict[str, Any]):
        """Set an instance or global variable

        Parameters:
            variable: Variable name
            value: Value to set (number, string, or expression)
            scope: "self" for instance variable, "other" for collision other, "global" for global variable
            relative: If True, add to current value instead of replacing
        """
        variable = parameters.get("variable", "")
        value_str = parameters.get("value", "0")
        scope = parameters.get("scope", "self")
        relative = parameters.get("relative", False)

        if not variable:
            print("⚠️  set_variable: No variable name specified")
            return

        # Parse the value
        value = self._parse_value(value_str, instance)

        if scope == "global":
            if not self.game_runner:
                print("⚠️  set_variable: Cannot access global variables without game_runner")
                return

            if relative:
                current = self.game_runner.global_variables.get(variable, 0)
                try:
                    value = current + value
                except TypeError:
                    print(f"⚠️  set_variable: Cannot add {type(value)} to {type(current)}")
                    return

            self.game_runner.global_variables[variable] = value
            print(f"🌐 Global variable '{variable}' = {value}")

        elif scope == "other":
            # Get the "other" instance from collision context
            other = getattr(self, '_collision_other', None)
            if not other:
                print("⚠️  set_variable: 'other' scope only available in collision events")
                return

            if relative:
                current = getattr(other, variable, 0)
                try:
                    value = current + value
                except TypeError:
                    print(f"⚠️  set_variable: Cannot add {type(value)} to {type(current)}")
                    return

            setattr(other, variable, value)
            print(f"📝 Other instance variable '{variable}' = {value}")

        else:  # scope == "self"
            if relative:
                current = getattr(instance, variable, 0)
                try:
                    value = current + value
                except TypeError:
                    print(f"⚠️  set_variable: Cannot add {type(value)} to {type(current)}")
                    return

            setattr(instance, variable, value)
            print(f"📝 Instance variable '{variable}' = {value}")

    def execute_test_variable_action(self, instance, parameters: Dict[str, Any]):
        """Test an instance or global variable

        Returns True if condition met, False otherwise

        Parameters:
            variable: Variable name
            value: Value to compare against
            scope: "self" for instance variable, "other" for collision other, "global" for global variable
            operation: Comparison operator (equal, less, greater, etc.)
        """
        variable = parameters.get("variable", "")
        value_str = parameters.get("value", "0")
        scope = parameters.get("scope", "self")
        operation = parameters.get("operation", "equal")

        if not variable:
            print("⚠️  test_variable: No variable name specified")
            return False

        # Get current value based on scope
        if scope == "global":
            if not self.game_runner:
                return False
            current = self.game_runner.global_variables.get(variable, 0)
        elif scope == "other":
            # Get the "other" instance from collision context
            other = getattr(self, '_collision_other', None)
            if not other:
                print("⚠️  test_variable: 'other' scope only available in collision events")
                return False
            current = getattr(other, variable, 0)
        else:  # scope == "self"
            current = getattr(instance, variable, 0)

        # Parse comparison value
        compare_value = self._parse_value(value_str, instance)

        # Perform comparison
        try:
            if operation == "equal":
                result = current == compare_value
            elif operation == "less":
                result = current < compare_value
            elif operation == "greater":
                result = current > compare_value
            elif operation == "less_equal":
                result = current <= compare_value
            elif operation == "greater_equal":
                result = current >= compare_value
            elif operation == "not_equal":
                result = current != compare_value
            else:
                result = False
        except TypeError:
            # Can't compare these types
            result = False

        scope_label = "other" if scope == "other" else ("global" if scope == "global" else "self")
        print(f"❓ Test {scope_label}.{variable} ({current}) {operation} {compare_value}: {result}")
        return result

    # ==================== ALARM ACTIONS ====================

    def execute_set_alarm_action(self, instance, parameters: Dict[str, Any]):
        """Set an alarm to trigger after N steps

        Parameters:
            alarm_number: Which alarm (0-11)
            steps: Number of steps until alarm triggers (-1 to disable)
            relative: If True, add to current alarm value
        """
        alarm_number = int(parameters.get("alarm_number", 0))
        steps_param = parameters.get("steps", "30")
        relative = parameters.get("relative", False)

        # Validate alarm number
        if alarm_number < 0 or alarm_number > 11:
            print(f"⚠️ set_alarm: Invalid alarm number {alarm_number} (must be 0-11)")
            return

        # Parse steps (can be a number or variable)
        steps = self._parse_value(str(steps_param), instance)
        if not isinstance(steps, (int, float)):
            print(f"⚠️ set_alarm: Invalid steps value '{steps_param}', defaulting to 30")
            steps = 30
        steps = int(steps)

        # Ensure instance has alarm array
        if not hasattr(instance, 'alarm'):
            instance.alarm = [-1] * 12

        if relative:
            current = instance.alarm[alarm_number]
            if current < 0:
                current = 0  # If disabled, treat as 0
            steps = current + steps

        instance.alarm[alarm_number] = steps

        if steps < 0:
            print(f"⏰ Alarm {alarm_number} disabled for {instance.object_name}")
        else:
            print(f"⏰ Alarm {alarm_number} set to {steps} steps for {instance.object_name}")

    # ==================== SCORE/LIVES/HEALTH ACTIONS ====================

    def execute_set_score_action(self, instance, parameters: Dict[str, Any]):
        """Set the score value"""
        if not self.game_runner:
            print("⚠️  Warning: set_score requires game_runner reference")
            return

        value = int(parameters.get("value", 0))
        relative = parameters.get("relative", False)

        if relative:
            self.game_runner.score += value
        else:
            self.game_runner.score = value

        # Auto-enable score in caption when score is used
        self.game_runner.show_score_in_caption = True

        print(f"🏆 Score set to: {self.game_runner.score}")

    def execute_test_score_action(self, instance, parameters: Dict[str, Any]):
        """Test score value and execute conditional actions

        Returns True if condition met, False otherwise
        """
        if not self.game_runner:
            return False

        value = int(parameters.get("value", 0))
        operation = parameters.get("operation", "equal")

        current_score = self.game_runner.score

        # Evaluate comparison
        result = False
        if operation == "equal":
            result = current_score == value
        elif operation == "less":
            result = current_score < value
        elif operation == "greater":
            result = current_score > value
        elif operation == "less_equal":
            result = current_score <= value
        elif operation == "greater_equal":
            result = current_score >= value
        elif operation == "not_equal":
            result = current_score != value

        return result

    def execute_draw_score_action(self, instance, parameters: Dict[str, Any]):
        """Draw score on screen (queued for draw event)"""
        if not self.game_runner:
            return

        x = int(parameters.get("x", 0))
        y = int(parameters.get("y", 0))
        caption = parameters.get("caption", "Score: ")

        # Store draw command for rendering
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'text',
            'text': f"{caption}{self.game_runner.score}",
            'x': x,
            'y': y,
            'color': (255, 255, 255)
        })

    def execute_set_lives_action(self, instance, parameters: Dict[str, Any]):
        """Set the lives value"""
        if not self.game_runner:
            print("⚠️  Warning: set_lives requires game_runner reference")
            return

        value = int(parameters.get("value", 3))
        relative = parameters.get("relative", False)

        if relative:
            self.game_runner.lives += value
        else:
            self.game_runner.lives = value

        # Ensure lives doesn't go negative
        self.game_runner.lives = max(0, self.game_runner.lives)

        # Auto-enable lives in caption when lives are used
        self.game_runner.show_lives_in_caption = True

        print(f"❤️  Lives set to: {self.game_runner.lives}")

    def execute_test_lives_action(self, instance, parameters: Dict[str, Any]):
        """Test lives value and execute conditional actions"""
        if not self.game_runner:
            return False

        value = int(parameters.get("value", 0))
        operation = parameters.get("operation", "equal")

        current_lives = self.game_runner.lives

        # Evaluate comparison
        result = False
        if operation == "equal":
            result = current_lives == value
        elif operation == "less":
            result = current_lives < value
        elif operation == "greater":
            result = current_lives > value
        elif operation == "less_equal":
            result = current_lives <= value
        elif operation == "greater_equal":
            result = current_lives >= value
        elif operation == "not_equal":
            result = current_lives != value

        return result

    def execute_draw_lives_action(self, instance, parameters: Dict[str, Any]):
        """Draw lives as sprite images"""
        if not self.game_runner:
            return

        x = int(parameters.get("x", 0))
        y = int(parameters.get("y", 0))
        sprite_name = parameters.get("sprite", "")

        # Queue lives drawing
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'lives',
            'count': self.game_runner.lives,
            'x': x,
            'y': y,
            'sprite': sprite_name
        })

    def execute_set_health_action(self, instance, parameters: Dict[str, Any]):
        """Set health value (0-100)"""
        if not self.game_runner:
            print("⚠️  Warning: set_health requires game_runner reference")
            return

        value = float(parameters.get("value", 100))
        relative = parameters.get("relative", False)

        if relative:
            self.game_runner.health += value
        else:
            self.game_runner.health = value

        # Clamp health between 0 and 100
        self.game_runner.health = max(0, min(100, self.game_runner.health))

        # Auto-enable health in caption when health is used
        self.game_runner.show_health_in_caption = True

        print(f"💚 Health set to: {self.game_runner.health}")

    def execute_test_health_action(self, instance, parameters: Dict[str, Any]):
        """Test health value and execute conditional actions"""
        if not self.game_runner:
            return False

        value = float(parameters.get("value", 0))
        operation = parameters.get("operation", "equal")

        current_health = self.game_runner.health

        # Evaluate comparison
        result = False
        if operation == "equal":
            result = abs(current_health - value) < 0.001  # Float comparison tolerance
        elif operation == "less":
            result = current_health < value
        elif operation == "greater":
            result = current_health > value
        elif operation == "less_equal":
            result = current_health <= value
        elif operation == "greater_equal":
            result = current_health >= value
        elif operation == "not_equal":
            result = abs(current_health - value) >= 0.001

        return result

    def execute_draw_health_bar_action(self, instance, parameters: Dict[str, Any]):
        """Draw health as a bar"""
        if not self.game_runner:
            return

        x1 = int(parameters.get("x1", 0))
        y1 = int(parameters.get("y1", 0))
        x2 = int(parameters.get("x2", 100))
        y2 = int(parameters.get("y2", 20))
        back_color = parameters.get("back_color", "#FF0000")
        bar_color = parameters.get("bar_color", "#00FF00")

        # Queue health bar drawing
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'health_bar',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'health': self.game_runner.health,
            'back_color': back_color,
            'bar_color': bar_color
        })

    def execute_set_window_caption_action(self, instance, parameters: Dict[str, Any]):
        """Set game window caption settings (score/lives/health display)"""
        if not self.game_runner:
            return

        # Update caption display settings on game_runner
        self.game_runner.show_score_in_caption = parameters.get("show_score", True)
        self.game_runner.show_lives_in_caption = parameters.get("show_lives", True)
        self.game_runner.show_health_in_caption = parameters.get("show_health", False)
        self.game_runner.window_caption = parameters.get("caption", "")

        print(f"🪟 Caption settings updated: score={self.game_runner.show_score_in_caption}, "
              f"lives={self.game_runner.show_lives_in_caption}, health={self.game_runner.show_health_in_caption}")

    def execute_show_highscore_action(self, instance, parameters: Dict[str, Any]):
        """Show highscore table (placeholder implementation)"""
        if not self.game_runner:
            return

        print("🥇 Highscore table:")
        if not self.game_runner.highscores:
            print("  (empty)")
        else:
            for i, (name, score) in enumerate(self.game_runner.highscores[:10], 1):
                print(f"  {i}. {name}: {score}")

    def execute_clear_highscore_action(self, instance, parameters: Dict[str, Any]):
        """Clear highscore table"""
        if not self.game_runner:
            return

        self.game_runner.highscores = []
        print("🧹 Highscore table cleared")

    # ==================== CODE EXECUTION ACTIONS ====================

    def execute_execute_code_action(self, instance, parameters: Dict[str, Any]):
        """Execute custom Python code

        Provides access to:
        - self: the current instance
        - game: the game runner object
        - All Python built-ins
        """
        code = parameters.get('code', '')

        if not code or not code.strip():
            return

        # Create execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'self': instance,
            'game': self.game_runner,
            'instance': instance,  # Alternative name
            # Add common modules for convenience
            'math': __import__('math'),
            'random': __import__('random'),
        }

        exec_locals = {}

        try:
            # Execute the code
            exec(code, exec_globals, exec_locals)

            # Apply any changes to instance variables from locals
            for key, value in exec_locals.items():
                if not key.startswith('__'):
                    setattr(instance, key, value)

        except Exception as e:
            print(f"⚠️  Error executing custom code: {e}")
            import traceback
            traceback.print_exc()

    # ==================== INSTANCE ACTIONS ====================

    def execute_destroy_instance_action(self, instance, parameters: Dict[str, Any]):
        """Execute destroy instance action

        Parameters:
            target: "self" or "other" - which instance to destroy
        """
        target = parameters.get("target", "self")

        if target == "other" and hasattr(self, '_collision_other') and self._collision_other:
            # Destroy the other instance in a collision context
            print(f"💀 Destroying other instance: {self._collision_other.object_name}")
            self._collision_other.to_destroy = True
        else:
            # Destroy self (default behavior)
            print(f"💀 Destroying instance: {instance.object_name}")
            instance.to_destroy = True

    def execute_collision_event(self, instance, event_name: str, events_data: Dict[str, Any], other_instance, collision_speeds=None):
        """Execute collision event with context about the other instance

        Args:
            instance: The instance whose collision event is being executed
            event_name: Name of the collision event (e.g., "collision_with_wall")
            events_data: Dict of all events for the instance
            other_instance: The other instance involved in the collision
            collision_speeds: Dict with speeds captured at collision time:
                - self_hspeed, self_vspeed: This instance's speeds at collision
                - other_hspeed, other_vspeed: Other instance's speeds at collision
        """
        if event_name not in events_data:
            return

        event_data = events_data[event_name]
        actions = event_data.get("actions", [])

        # Store reference to other instance for collision-specific actions
        self._collision_other = other_instance

        # Store collision speeds so they can be accessed via other.hspeed etc.
        # These are the speeds at the moment of collision, before any events modified them
        self._collision_speeds = collision_speeds or {}

        # Use execute_action_list for proper conditional flow support
        self.execute_collision_action_list(instance, actions, other_instance)

        # Clean up
        self._collision_other = None
        self._collision_speeds = {}

    def execute_collision_action_list(self, instance, actions: list, other_instance):
        """Execute collision actions with conditional flow support"""
        i = 0
        skip_next = False
        condition_was_false = False

        while i < len(actions):
            action_data = actions[i]
            action_name = action_data.get("action", "")

            # Handle else action (supports both else_action and else_block)
            if action_name in ("else_action", "else_block", "else"):
                skip_next = not condition_was_false
                i += 1
                continue

            # Handle start_block - if we're skipping, skip the entire block
            if action_name in ("start_block", "start"):
                if skip_next:
                    # Skip until matching end_block
                    block_depth = 1
                    i += 1
                    while i < len(actions) and block_depth > 0:
                        next_action = actions[i].get("action", "")
                        if next_action in ("start_block", "start"):
                            block_depth += 1
                        elif next_action in ("end_block", "end"):
                            block_depth -= 1
                        i += 1
                    skip_next = False
                    condition_was_false = True  # Block was skipped
                    continue
                i += 1
                continue

            # Handle end_block
            if action_name in ("end_block", "end"):
                skip_next = False
                condition_was_false = False
                i += 1
                continue

            # Skip this action if skip_next is set (for single actions)
            if skip_next:
                skip_next = False
                i += 1
                continue

            # Execute the action
            result = self.execute_collision_action(instance, action_data, other_instance)

            # Check if this was a conditional action that returned False
            if result is False:
                skip_next = True
                condition_was_false = True
            elif result is True:
                condition_was_false = False

            i += 1

    def execute_collision_action(self, instance, action_data: Dict[str, Any], other_instance):
        """Execute a collision action with knowledge of both self and other

        Returns:
            - True/False for conditional actions
            - None for regular actions
        """
        action_name = action_data.get("action")
        parameters = action_data.get("parameters", {})

        if action_name == "destroy_instance":
            target = parameters.get("target", "self")

            if target == "self":
                instance.to_destroy = True
            elif target == "other":
                other_instance.to_destroy = True
            return None
        else:
            # For all other actions, use the regular action executor
            return self.execute_action(instance, action_data)