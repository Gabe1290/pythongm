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

            # Handle end_block - reset conditional state
            if action_name in ("end_block", "end"):
                skip_next = False
                condition_was_false = False
                i += 1
                continue

            # Skip this action if skip_next is set
            if skip_next:
                # Skip one action and reset (unless we hit another else/end_block)
                skip_next = False
                i += 1
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
        """Set horizontal speed for smooth movement"""
        # Accept both 'value' (from IDE) and 'speed' (legacy) parameters
        speed = float(parameters.get("value", parameters.get("speed", 0)))
        old_speed = instance.hspeed
        instance.hspeed = speed
        # Only print when speed changes
        if old_speed != speed:
            print(f"  🏃 {instance.object_name} hspeed: {old_speed} → {speed}")
    
    def execute_set_vspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set vertical speed for smooth movement"""
        # Accept both 'value' (from IDE) and 'speed' (legacy) parameters
        speed = float(parameters.get("value", parameters.get("speed", 0)))
        old_speed = instance.vspeed
        instance.vspeed = speed
        # Only print when speed changes
        if old_speed != speed:
            print(f"  🏃 {instance.object_name} vspeed: {old_speed} → {speed}")
    
    def execute_stop_movement_action(self, instance, parameters: Dict[str, Any]):
        """Stop all movement by setting speeds to zero"""
        instance.hspeed = 0
        instance.vspeed = 0

    def execute_start_moving_direction_action(self, instance, parameters: Dict[str, Any]):
        """Start moving in a specific direction

        Direction angles (GameMaker standard):
        - 0° = right
        - 90° = up
        - 180° = left
        - 270° = down
        """
        import math

        direction = float(parameters.get("directions", 0))  # Note: parameter name is "directions" (plural)
        speed = float(parameters.get("speed", 4.0))

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
        """Check if instance is on grid and execute actions conditionally

        Logic:
        1. Check if instance is CLOSE to grid (with tolerance for floating point errors)
        2. If close, SNAP to exact grid position first
        3. Then execute actions (movement will start from exact grid position)
        """
        grid_size = int(parameters.get("grid_size", 32))
        then_actions = parameters.get("then_actions", [])
        else_actions = parameters.get("else_actions", [])

        # DEBUG: Check if then_actions is a string (corrupted data)
        if isinstance(then_actions, str):
            print(f"⚠️ WARNING: then_actions is a string, not a list!")
            print(f"   Value: {then_actions[:100]}...")
            print(f"   This indicates corrupted event data in the JSON")
            return

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

        # STEP 4: Execute actions based on grid alignment
        if on_grid:
            # Execute then_actions - player is now at EXACT grid position
            for action in then_actions:
                self.execute_action(instance, action)
        else:
            # Execute else_actions - player is not on grid
            for action in else_actions:
                self.execute_action(instance, action)
    
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
    
    def execute_if_collision_at_action(self, instance, parameters: Dict[str, Any]):
        """Execute collision check with conditional actions"""
        x_expr = parameters.get("x", "self.x")
        y_expr = parameters.get("y", "self.y")
        object_type = parameters.get("object_type", "any")
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

    def execute_collision_event(self, instance, event_name: str, events_data: Dict[str, Any], other_instance):
        """Execute collision event with context about the other instance"""
        if event_name not in events_data:
            return

        event_data = events_data[event_name]
        actions = event_data.get("actions", [])

        # Store reference to other instance for collision-specific actions
        self._collision_other = other_instance

        # Use execute_action_list for proper conditional flow support
        self.execute_collision_action_list(instance, actions, other_instance)

        # Clean up
        self._collision_other = None

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

            # Handle end_block
            if action_name in ("end_block", "end"):
                skip_next = False
                condition_was_false = False
                i += 1
                continue

            # Skip this action if skip_next is set
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