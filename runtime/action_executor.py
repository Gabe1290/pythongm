#!/usr/bin/env python3
"""
Action Execution Engine - WITH GRID SNAPPING
Converts visual actions into runtime behavior
"""

from typing import Dict, Any
from core.logger import get_logger
logger = get_logger(__name__)

class ActionExecutor:
    """Executes visual actions during gameplay with auto-discovery"""

    def __init__(self, game_runner=None):
        # Action handlers dictionary - auto-populated via discovery
        self.action_handlers = {}

        # Reference to game runner for accessing global state (score, lives, health)
        self.game_runner = game_runner

        # Auto-discover all action handler methods
        self._register_action_handlers()

        logger.info(f"✅ ActionExecutor initialized with {len(self.action_handlers)} action handlers")

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

                # Skip if no action name (e.g., "execute_action" -> "")
                if not action_name:
                    continue

                # Get the method
                method = getattr(self, attr_name)

                # Verify it's callable
                if callable(method):
                    self.action_handlers[action_name] = method
                    logger.debug(f"  📌 Registered action handler: {action_name}")

    def register_custom_action(self, action_name: str, handler_func):
        """Register a custom action handler dynamically (for plugins)

        Args:
            action_name: The action name (e.g., 'play_sound')
            handler_func: A function with signature (instance, parameters) -> None
        """
        self.action_handlers[action_name] = handler_func
        logger.info(f"  🔌 Registered custom action: {action_name}")

    def execute_event(self, instance, event_name: str, events_data: Dict[str, Any]):
        """Execute all actions in an event"""
        if event_name not in events_data:
            return

        event_data = events_data[event_name]
        actions = event_data.get("actions", [])

        # DEBUG: Show which event is being executed
        if event_name == "create":
            obj_name = getattr(instance, 'object_name', instance.__class__.__name__)
            logger.debug(f"🎬 Executing CREATE event for {obj_name}")
            logger.debug(f"   Actions: {len(actions)} action(s)")
            if actions:
                logger.debug(f"   First action: {actions[0].get('action', 'unknown')}")

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
            logger.warning(f"⚠️ Repeat: Invalid times value '{times_param}', defaulting to 1")
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

            logger.debug(f"🔁 Repeat block {times} times ({len(block_actions)} actions)")
            for iteration in range(times):
                self.execute_action_list(instance, block_actions)

            return end_block_index + 1
        else:
            # Repeat a single action
            single_action = actions[next_index]
            logger.debug(f"🔁 Repeat '{next_action}' {times} times")
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
            logger.debug(f"⚠️ Action missing 'action' field: {action_data}")
            return None

        # Apply action name aliases
        if action_name in self.ACTION_ALIASES:
            action_name = self.ACTION_ALIASES[action_name]

        if action_name not in self.action_handlers:
            logger.error(f"❌ Unknown action: {action_name}")
            logger.debug(f"   Available actions: {', '.join(sorted(self.action_handlers.keys()))}")
            return None

        # Validate instance has required attributes for this action
        if not self._validate_action_requirements(instance, action_name):
            logger.debug(f"⚠️ Instance missing requirements for action '{action_name}'")
            return None

        # Execute the action with error handling
        try:
            result = self.action_handlers[action_name](instance, parameters)
            return result  # Return result for conditional flow
        except AttributeError as e:
            logger.debug(f"❌ Attribute error in action {action_name}: {e}")
            logger.debug("   Instance may be missing required attributes")
            return None
        except Exception as e:
            logger.error(f"❌ Error executing action {action_name}: {e}")
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
                logger.debug(f"   Missing attribute: {attr}")
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
        logger.debug(f"  🔍 set_hspeed: raw value = '{speed_value}', _collision_other = {getattr(self, '_collision_other', None)}")
        speed = self._parse_value(str(speed_value), instance)
        logger.debug(f"  🔍 set_hspeed: parsed value = {speed}")
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  set_hspeed: Invalid speed value '{speed_value}'")
            return
        old_speed = instance.hspeed
        instance.hspeed = speed
        # Only print when speed changes
        if old_speed != speed:
            logger.debug(f"  🏃 {instance.object_name} hspeed: {old_speed} → {speed}")

    def execute_set_vspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set vertical speed for smooth movement

        Accepts numbers or variable references like other.vspeed
        """
        # Accept 'vspeed', 'value', or 'speed' parameters
        speed_value = parameters.get("vspeed", parameters.get("value", parameters.get("speed", "0")))
        logger.debug(f"  🔍 set_vspeed: raw value = '{speed_value}', _collision_other = {getattr(self, '_collision_other', None)}")
        speed = self._parse_value(str(speed_value), instance)
        logger.debug(f"  🔍 set_vspeed: parsed value = {speed}")
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  set_vspeed: Invalid speed value '{speed_value}'")
            return
        old_speed = instance.vspeed
        instance.vspeed = speed
        # Only print when speed changes
        if old_speed != speed:
            logger.debug(f"  🏃 {instance.object_name} vspeed: {old_speed} → {speed}")

    def execute_stop_movement_action(self, instance, parameters: Dict[str, Any]):
        """Stop all movement by setting speeds to zero"""
        instance.hspeed = 0
        instance.vspeed = 0

    def execute_bounce_action(self, instance, parameters: Dict[str, Any]):
        """Bounce off solid objects by reversing velocity.

        Parameters:
            precise: If True, uses more accurate collision detection (not implemented yet)
            against: "solid" to bounce off all solid objects, or specific object name

        For simple bouncing, this reverses the velocity component based on
        which direction was blocked. If both directions are blocked (corner),
        both components are reversed.
        """
        # Get speeds and blocked flags from collision info
        collision_speeds = getattr(self, '_collision_speeds', {})
        hspeed = collision_speeds.get('self_hspeed', instance.hspeed)
        vspeed = collision_speeds.get('self_vspeed', instance.vspeed)
        h_blocked = collision_speeds.get('h_blocked', False)
        v_blocked = collision_speeds.get('v_blocked', False)

        if hspeed != 0 or vspeed != 0:
            # Use blocked flags to determine which components to reverse
            if h_blocked and v_blocked:
                # Corner collision - reverse both components
                instance.hspeed = -hspeed
                instance.vspeed = -vspeed
                logger.debug(f"  🏓 {instance.object_name} bounced corner, hspeed: {hspeed} → {instance.hspeed}, vspeed: {vspeed} → {instance.vspeed}")
            elif h_blocked:
                # Only horizontal blocked - reverse horizontal
                instance.hspeed = -hspeed
                logger.debug(f"  🏓 {instance.object_name} bounced horizontally, hspeed: {hspeed} → {instance.hspeed}")
            elif v_blocked:
                # Only vertical blocked - reverse vertical
                instance.vspeed = -vspeed
                logger.debug(f"  🏓 {instance.object_name} bounced vertically, vspeed: {vspeed} → {instance.vspeed}")
            else:
                # Fallback: no flags, use legacy behavior (primary direction)
                if abs(hspeed) >= abs(vspeed):
                    instance.hspeed = -hspeed
                    logger.debug(f"  🏓 {instance.object_name} bounced horizontally (fallback), hspeed: {hspeed} → {instance.hspeed}")
                else:
                    instance.vspeed = -vspeed
                    logger.debug(f"  🏓 {instance.object_name} bounced vertically (fallback), vspeed: {vspeed} → {instance.vspeed}")
        else:
            logger.debug(f"  ⚠️ {instance.object_name} bounce: no velocity to reverse")

    def execute_set_gravity_action(self, instance, parameters: Dict[str, Any]):
        """Set gravity for the instance

        Parameters:
            direction: Direction of gravity in degrees (270 = down, 90 = up)
            gravity: Gravity strength (acceleration per frame)
        """
        direction = parameters.get("direction", 270)
        gravity = parameters.get("gravity", 0.5)

        try:
            direction = float(direction)
            gravity = float(gravity)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  set_gravity: Invalid values direction={direction}, gravity={gravity}")
            return

        instance.gravity = gravity
        instance.gravity_direction = direction
        logger.debug(f"  ⬇️ {instance.object_name} gravity set to {gravity} at {direction}°")

    def execute_set_friction_action(self, instance, parameters: Dict[str, Any]):
        """Set friction for the instance

        Parameters:
            friction: Friction amount (speed reduction per frame)
        """
        friction = parameters.get("friction", 0)

        try:
            friction = float(friction)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  set_friction: Invalid friction value '{friction}'")
            return

        instance.friction = friction
        logger.debug(f"  🛑 {instance.object_name} friction set to {friction}")

    def execute_set_direction_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set exact direction and speed for movement

        Direction angles (GameMaker standard):
        - 0° = right
        - 90° = up
        - 180° = left
        - 270° = down

        Parameters:
            direction: Direction in degrees (0-360)
            speed: Movement speed
        """
        import math

        direction = parameters.get("direction", 0)
        speed = parameters.get("speed", 4.0)

        # Parse values (can be expressions)
        direction = self._parse_value(str(direction), instance)
        speed = self._parse_value(str(speed), instance)

        try:
            direction = float(direction)
            speed = float(speed)
        except (ValueError, TypeError):
            logger.warning(f"⚠️ set_direction_speed: Invalid values direction={direction}, speed={speed}")
            return

        # Convert angle to radians (GameMaker uses degrees, 0° is right, 90° is up)
        angle_rad = math.radians(direction)

        # Calculate horizontal and vertical speed components
        # Note: In screen coordinates, y increases downward, so we negate sin
        instance.hspeed = math.cos(angle_rad) * speed
        instance.vspeed = -math.sin(angle_rad) * speed

        logger.debug(f"  🧭 {instance.object_name} set direction={direction}° speed={speed}")
        logger.debug(f"      hspeed={instance.hspeed:.2f}, vspeed={instance.vspeed:.2f}")

    def execute_move_towards_point_action(self, instance, parameters: Dict[str, Any]):
        """Move towards a specific point at given speed

        Parameters:
            x: Target X coordinate
            y: Target Y coordinate
            speed: Movement speed

        This calculates the direction from current position to target and sets
        hspeed/vspeed to move in that direction at the specified speed.
        """
        import math

        target_x = parameters.get("x", 0)
        target_y = parameters.get("y", 0)
        speed = parameters.get("speed", 4.0)

        # Parse values (can be expressions)
        target_x = self._parse_value(str(target_x), instance)
        target_y = self._parse_value(str(target_y), instance)
        speed = self._parse_value(str(speed), instance)

        try:
            target_x = float(target_x)
            target_y = float(target_y)
            speed = float(speed)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  move_towards_point: Invalid values x={target_x}, y={target_y}, speed={speed}")
            return

        # Calculate direction to target
        dx = target_x - instance.x
        dy = target_y - instance.y

        # Calculate distance to target
        distance = math.sqrt(dx*dx + dy*dy)

        if distance == 0:
            # Already at target, stop movement
            instance.hspeed = 0
            instance.vspeed = 0
            logger.debug(f"  🎯 {instance.object_name} already at target ({target_x}, {target_y})")
            return

        # Calculate normalized direction vector
        dir_x = dx / distance
        dir_y = dy / distance

        # Set speed components
        instance.hspeed = dir_x * speed
        instance.vspeed = dir_y * speed

        # Calculate angle for display
        angle = math.degrees(math.atan2(-dy, dx))  # Negative dy for screen coordinates

        logger.debug(f"  🎯 {instance.object_name} moving towards ({target_x}, {target_y}) at speed {speed}")
        logger.debug(f"      angle={angle:.1f}°, hspeed={instance.hspeed:.2f}, vspeed={instance.vspeed:.2f}")

    def execute_move_to_contact_action(self, instance, parameters: Dict[str, Any]):
        """Move in a direction until touching an object

        Parameters:
            direction: Direction to move in degrees (0=right, 90=up, 180=left, 270=down)
            max_distance: Maximum distance to move in pixels
            object: Object type to stop at ("all" for any object, "solid" for solid objects, or specific object name)

        This moves the instance pixel-by-pixel in the specified direction until:
        - It touches the specified object type, OR
        - It reaches max_distance

        Returns True if contact was made, False if max distance reached
        """
        import math

        direction = parameters.get("direction", 0)
        max_distance = parameters.get("max_distance", 1000)
        object_type = parameters.get("object", "all")

        # Parse values
        direction = self._parse_value(str(direction), instance)
        max_distance = self._parse_value(str(max_distance), instance)

        try:
            direction = float(direction)
            max_distance = float(max_distance)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  move_to_contact: Invalid values direction={direction}, max_distance={max_distance}")
            return False

        if not self.game_runner:
            logger.debug("⚠️  move_to_contact: No game runner available")
            return False

        # Calculate movement vector (1 pixel per step)
        angle_rad = math.radians(direction)
        step_x = math.cos(angle_rad)
        step_y = -math.sin(angle_rad)  # Negative for screen coordinates

        # Store starting position
        start_x = instance.x
        start_y = instance.y
        distance_moved = 0

        # Move pixel by pixel until contact or max distance
        while distance_moved < max_distance:
            # Try moving one pixel
            test_x = instance.x + step_x
            test_y = instance.y + step_y

            # Check if this position would cause a collision
            collision_found = False

            for other in self.game_runner.instances:
                if other is instance:
                    continue

                # Check object type filter
                if object_type == "all":
                    should_check = True
                elif object_type == "solid":
                    should_check = getattr(other, 'solid', False)
                else:
                    should_check = (getattr(other, 'object_name', '') == object_type)

                if not should_check:
                    continue

                # Simple bounding box collision check at test position
                # Get instance bounds at test position
                inst_width = getattr(instance, '_cached_width', 32)
                inst_height = getattr(instance, '_cached_height', 32)

                # Get other instance bounds
                other_width = getattr(other, '_cached_width', 32)
                other_height = getattr(other, '_cached_height', 32)

                # Check collision
                if (test_x < other.x + other_width and
                    test_x + inst_width > other.x and
                    test_y < other.y + other_height and
                    test_y + inst_height > other.y):
                    collision_found = True
                    break

            if collision_found:
                # Stop at current position (before collision)
                logger.debug(f"  👉 {instance.object_name} moved to contact at ({instance.x:.1f}, {instance.y:.1f})")
                logger.debug(f"      direction={direction}°, distance={distance_moved:.1f}px")
                return True

            # No collision, move to test position
            instance.x = test_x
            instance.y = test_y
            distance_moved += 1

        # Reached max distance without contact
        logger.debug(f"  👉 {instance.object_name} reached max distance {max_distance}px without contact")
        logger.debug(f"      moved from ({start_x:.1f}, {start_y:.1f}) to ({instance.x:.1f}, {instance.y:.1f})")
        return False

    def execute_reverse_horizontal_action(self, instance, parameters: Dict[str, Any]):
        """Reverse horizontal movement direction"""
        old_hspeed = instance.hspeed
        instance.hspeed = -instance.hspeed
        logger.debug(f"  ↔️ {instance.object_name} reversed hspeed: {old_hspeed} → {instance.hspeed}")

    def execute_reverse_vertical_action(self, instance, parameters: Dict[str, Any]):
        """Reverse vertical movement direction"""
        old_vspeed = instance.vspeed
        instance.vspeed = -instance.vspeed
        logger.debug(f"  ↕️ {instance.object_name} reversed vspeed: {old_vspeed} → {instance.vspeed}")

    def execute_wrap_around_room_action(self, instance, parameters: Dict[str, Any]):
        """Wrap instance to opposite side when leaving room

        Parameters:
            horizontal: Wrap horizontally (default True)
            vertical: Wrap vertically (default True)
        """
        horizontal = parameters.get("horizontal", True)
        vertical = parameters.get("vertical", True)

        if not self.game_runner or not self.game_runner.current_room:
            return

        room_width = self.game_runner.current_room.width
        room_height = self.game_runner.current_room.height

        # Get sprite dimensions for accurate wrapping
        sprite_width = getattr(instance, '_cached_width', 32)
        sprite_height = getattr(instance, '_cached_height', 32)

        wrapped = False
        if horizontal:
            if instance.x + sprite_width < 0:
                instance.x = room_width
                wrapped = True
            elif instance.x > room_width:
                instance.x = -sprite_width
                wrapped = True

        if vertical:
            if instance.y + sprite_height < 0:
                instance.y = room_height
                wrapped = True
            elif instance.y > room_height:
                instance.y = -sprite_height
                wrapped = True

        if wrapped:
            logger.debug(f"  🔄 {instance.object_name} wrapped to ({instance.x}, {instance.y})")

    def execute_jump_to_position_action(self, instance, parameters: Dict[str, Any]):
        """Jump to a specific position instantly

        Supports expressions like other.x, self.hspeed*8, etc.
        With 'relative' option, adds to current position instead of setting absolute.
        With 'push_other' option (default True in collision), moves the 'other' instance
        to this instance's current position (Sokoban-style push behavior).
        """
        x_expr = str(parameters.get("x", "0"))
        y_expr = str(parameters.get("y", "0"))
        relative = parameters.get("relative", False)
        # By default, move the "other" instance (pusher) to fill the gap in collision events
        push_other = parameters.get("push_other", True)

        # Store current position before moving (for push_other feature)
        old_x = instance.x
        old_y = instance.y

        # Debug: Show stored collision speeds
        collision_speeds = getattr(self, '_collision_speeds', {})
        if collision_speeds:
            logger.debug(f"  🔍 jump_to_position: Using collision speeds: {collision_speeds}")

        # Evaluate X expression
        try:
            x_value = self._parse_value(x_expr, instance)
            logger.debug(f"  🔍 X expression '{x_expr}' evaluated to: {x_value}")
            if x_value is None or isinstance(x_value, str):
                x_value = 0
            x_value = float(x_value)
        except Exception as e:
            logger.error(f"⚠️ Error evaluating X expression '{x_expr}': {e}")
            x_value = 0.0

        # Evaluate Y expression
        try:
            y_value = self._parse_value(y_expr, instance)
            logger.debug(f"  🔍 Y expression '{y_expr}' evaluated to: {y_value}")
            if y_value is None or isinstance(y_value, str):
                y_value = 0
            y_value = float(y_value)
        except Exception as e:
            logger.error(f"⚠️ Error evaluating Y expression '{y_expr}': {e}")
            y_value = 0.0

        # Apply position
        if relative:
            instance.x += x_value
            instance.y += y_value
            logger.debug(f"  📍 {instance.object_name} jumped relatively by ({x_value}, {y_value}) → ({instance.x}, {instance.y})")
        else:
            instance.x = x_value
            instance.y = y_value
            logger.debug(f"  📍 {instance.object_name} jumped to ({instance.x}, {instance.y})")

        # Snap to grid after jump only during collision events with push_other
        # This is important for grid-based games like Sokoban but not for general use
        if push_other and hasattr(self, '_collision_other') and self._collision_other:
            grid_size = 32
            instance.x = round(instance.x / grid_size) * grid_size
            instance.y = round(instance.y / grid_size) * grid_size
            logger.debug(f"  📐 Snapped to grid: ({instance.x}, {instance.y})")

        # Sokoban-style push: move the "other" instance (pusher) to fill the gap
        # This only happens during collision events when push_other is True
        if push_other and hasattr(self, '_collision_other') and self._collision_other:
            other = self._collision_other
            # Only move other if instance actually moved (relative jump with non-zero values)
            if relative and (x_value != 0 or y_value != 0):
                other.x = old_x
                other.y = old_y
                # Stop the pusher's movement
                other.hspeed = 0
                other.vspeed = 0
                logger.debug(f"  🚶 Pusher {other.object_name} moved to ({old_x}, {old_y}) and stopped")

    def execute_jump_to_start_action(self, instance, parameters: Dict[str, Any]):
        """Jump to the instance's starting position (where it was created)

        This restores the instance to its original position when it was first placed in the room.
        """
        # Get start position (stored when instance is created)
        start_x = getattr(instance, 'xstart', instance.x)
        start_y = getattr(instance, 'ystart', instance.y)

        instance.x = start_x
        instance.y = start_y

        logger.debug(f"  🏠 {instance.object_name} jumped to start position ({start_x}, {start_y})")

    def execute_jump_to_random_action(self, instance, parameters: Dict[str, Any]):
        """Jump to a random position in the room

        Parameters:
            snap_h: Horizontal snap grid (default 1 = no snap)
            snap_v: Vertical snap grid (default 1 = no snap)
        """
        import random

        snap_h = int(parameters.get("snap_h", 1))
        snap_v = int(parameters.get("snap_v", 1))

        # Get room dimensions
        room_width = 640
        room_height = 480
        if self.game_runner and self.game_runner.current_room:
            room_width = self.game_runner.current_room.width
            room_height = self.game_runner.current_room.height

        # Get instance dimensions
        width = getattr(instance, '_cached_width', 32)
        height = getattr(instance, '_cached_height', 32)

        # Generate random position within room bounds
        max_x = room_width - width
        max_y = room_height - height

        if snap_h > 1:
            # Snap to horizontal grid
            num_positions_h = max(1, max_x // snap_h)
            new_x = random.randint(0, num_positions_h) * snap_h
        else:
            new_x = random.randint(0, max(0, int(max_x)))

        if snap_v > 1:
            # Snap to vertical grid
            num_positions_v = max(1, max_y // snap_v)
            new_y = random.randint(0, num_positions_v) * snap_v
        else:
            new_y = random.randint(0, max(0, int(max_y)))

        instance.x = float(new_x)
        instance.y = float(new_y)

        logger.debug(f"  🎲 {instance.object_name} jumped to random position ({new_x}, {new_y})")

    def execute_wrap_around_room_action(self, instance, parameters: Dict[str, Any]):
        """Wrap instance to opposite side when leaving room boundaries

        Parameters:
            horizontal: Wrap horizontally (default True)
            vertical: Wrap vertically (default True)
        """
        horizontal = parameters.get("horizontal", True)
        vertical = parameters.get("vertical", True)

        # Get room dimensions
        room_width = 640
        room_height = 480
        if self.game_runner and self.game_runner.current_room:
            room_width = self.game_runner.current_room.width
            room_height = self.game_runner.current_room.height

        # Get instance dimensions
        width = getattr(instance, '_cached_width', 32)
        height = getattr(instance, '_cached_height', 32)

        wrapped = False

        # Horizontal wrapping
        if horizontal:
            if instance.x + width < 0:
                # Exited left side - wrap to right
                instance.x = room_width
                wrapped = True
            elif instance.x > room_width:
                # Exited right side - wrap to left
                instance.x = -width
                wrapped = True

        # Vertical wrapping
        if vertical:
            if instance.y + height < 0:
                # Exited top - wrap to bottom
                instance.y = room_height
                wrapped = True
            elif instance.y > room_height:
                # Exited bottom - wrap to top
                instance.y = -height
                wrapped = True

        if wrapped:
            logger.debug(f"  🔄 {instance.object_name} wrapped to ({instance.x}, {instance.y})")

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
                    logger.debug("   ➡️ Start Moving Direction: stopped (empty directions)")
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
            # Check if it's an expression (like other.direction, self.direction, choose(...), random(...))
            is_expression = (
                '.' in directions or
                'choose(' in directions or
                'random(' in directions or
                'irandom(' in directions or
                '+' in directions or
                '-' in directions or
                '*' in directions or
                '/' in directions
            )
            if is_expression and directions.lower() not in direction_map:
                direction = self._evaluate_expression(directions, instance)
                if not isinstance(direction, (int, float)):
                    logger.debug(f"   ⚠️ Could not evaluate direction expression: {directions}")
                    direction = 0
            else:
                direction = direction_map.get(directions.lower(), 0)
        else:
            direction = float(directions)

        # Handle 'stop' direction
        if direction == -1:
            instance.hspeed = 0
            instance.vspeed = 0
            logger.debug("   ➡️ Start Moving Direction: stopped")
            return

        # Convert angle to radians (GameMaker uses degrees, 0° is right, 90° is up)
        angle_rad = math.radians(direction)

        # Calculate horizontal and vertical speed components
        # Note: In screen coordinates, y increases downward, so we negate sin
        instance.hspeed = math.cos(angle_rad) * speed
        instance.vspeed = -math.sin(angle_rad) * speed

        # DEBUG
        logger.debug(f"   ➡️ Start Moving Direction: {direction}° at speed {speed}")
        logger.debug(f"      hspeed={instance.hspeed:.2f}, vspeed={instance.vspeed:.2f}")

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
            logger.debug(f"  🔍 if_collision: Using collision speeds: {collision_speeds}")

        # Evaluate X offset expression using _parse_value
        try:
            x_offset = self._parse_value(x_expr, instance)
            logger.debug(f"  🔍 X expression '{x_expr}' evaluated to: {x_offset}")
            if x_offset is None or isinstance(x_offset, str):
                x_offset = 0
            x_offset = float(x_offset)
        except Exception as e:
            logger.error(f"⚠️ Error evaluating X expression '{x_expr}': {e}")
            x_offset = 0.0

        # Evaluate Y offset expression using _parse_value
        try:
            y_offset = self._parse_value(y_expr, instance)
            logger.debug(f"  🔍 Y expression '{y_expr}' evaluated to: {y_offset}")
            if y_offset is None or isinstance(y_offset, str):
                y_offset = 0
            y_offset = float(y_offset)
        except Exception as e:
            logger.error(f"⚠️ Error evaluating Y expression '{y_expr}': {e}")
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
            logger.debug("  ⚠️ if_collision: game_runner is None! Cannot check collisions.")

        # Apply NOT flag
        result = not has_collision if not_flag else has_collision

        logger.debug(f"  ❓ if_collision at ({check_x}, {check_y}) for '{object_type}': collision={has_collision}, not_flag={not_flag}, result={result}")

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

    def execute_if_object_exists_action(self, instance, parameters: Dict[str, Any]):
        """Check if any instance of an object type exists in the room

        Parameters:
            object: The object type to check for
            not_flag: If True, returns True when object does NOT exist

        Returns True if condition is met (for conditional flow), False otherwise.
        """
        object_type = parameters.get("object", "")
        not_flag = parameters.get("not_flag", False)

        if not object_type:
            logger.debug("  ⚠️ if_object_exists: No object type specified")
            return False

        # Count instances of the specified object type
        exists = False
        if self.game_runner and self.game_runner.current_room:
            for room_instance in self.game_runner.current_room.instances:
                if room_instance.object_name == object_type:
                    exists = True
                    break

        # Apply NOT flag
        result = not exists if not_flag else exists

        logger.debug(f"  ❓ if_object_exists: '{object_type}' exists={exists}, not_flag={not_flag}, result={result}")

        return result

    # ==================== GAME ACTIONS ====================

    def execute_show_message_action(self, instance, parameters: Dict[str, Any]):
        """Execute show message action"""
        message = parameters.get("message", "")
        logger.info(f"💬 MESSAGE: {message}")

        # Store message for game runner to display
        if not hasattr(instance, 'pending_messages'):
            instance.pending_messages = []
        instance.pending_messages.append(message)

    def execute_restart_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute restart room action - resets current level"""
        logger.debug(f"🔄 Restart room requested by {instance.object_name}")
        instance.restart_room_flag = True

    def execute_next_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute next room action - advances to next level"""
        logger.debug(f"➡️  Next room requested by {instance.object_name}")
        instance.next_room_flag = True

    def execute_previous_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute previous room action - goes to previous level"""
        logger.debug(f"⬅️  Previous room requested by {instance.object_name}")
        instance.previous_room_flag = True

    def execute_if_next_room_exists_action(self, instance, parameters: Dict[str, Any]):
        """Check if next room exists

        This is a conditional action:
        - Returns True if next room exists (next action will execute)
        - Returns False if no next room (next action will be skipped)

        Also supports nested then_actions/else_actions for Blockly-style conditionals.
        """
        if not self.game_runner:
            logger.warning("⚠️  Warning: if_next_room_exists requires game_runner reference")
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

        logger.debug(f"❓ Next room exists: {next_exists}")

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
            logger.warning("⚠️  Warning: if_previous_room_exists requires game_runner reference")
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

        logger.debug(f"❓ Previous room exists: {prev_exists}")

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

        # Handle GameMaker-style functions before evaluation
        import random as random_module

        # random(n) - returns random float from 0 to n (exclusive)
        def gm_random(n):
            return random_module.random() * n

        # irandom(n) - returns random integer from 0 to n (inclusive)
        def gm_irandom(n):
            return random_module.randint(0, int(n))

        # choose(a, b, c, ...) - returns one of the arguments randomly
        def gm_choose(*args):
            return random_module.choice(args)

        # Replace function calls with Python equivalents
        expr_substituted = re.sub(r'\brandom\s*\(', 'gm_random(', expr_substituted)
        expr_substituted = re.sub(r'\birandom\s*\(', 'gm_irandom(', expr_substituted)
        expr_substituted = re.sub(r'\bchoose\s*\(', 'gm_choose(', expr_substituted)

        # Try to evaluate the expression safely
        try:
            # Allow safe characters plus function calls
            if re.match(r'^[\d\s\+\-\*\/\%\(\)\.\,a-zA-Z_]+$', expr_substituted):
                # Create safe namespace with only allowed functions
                safe_namespace = {
                    'gm_random': gm_random,
                    'gm_irandom': gm_irandom,
                    'gm_choose': gm_choose,
                }
                result = eval(expr_substituted, {"__builtins__": {}}, safe_namespace)
                return result
            else:
                logger.debug(f"⚠️ Unsafe expression: {expr_substituted}")
                return 0
        except Exception as e:
            logger.error(f"⚠️ Error evaluating expression '{expr_str}': {e}")
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
            scope: "sel" for instance variable, "other" for collision other, "global" for global variable
            relative: If True, add to current value instead of replacing
        """
        variable = parameters.get("variable", "")
        value_str = parameters.get("value", "0")
        scope = parameters.get("scope", "sel")
        relative = parameters.get("relative", False)

        if not variable:
            logger.debug("⚠️  set_variable: No variable name specified")
            return

        # Parse the value
        value = self._parse_value(value_str, instance)

        if scope == "global":
            if not self.game_runner:
                logger.debug("⚠️  set_variable: Cannot access global variables without game_runner")
                return

            if relative:
                current = self.game_runner.global_variables.get(variable, 0)
                try:
                    value = current + value
                except TypeError:
                    logger.debug(f"⚠️  set_variable: Cannot add {type(value)} to {type(current)}")
                    return

            self.game_runner.global_variables[variable] = value
            logger.debug(f"🌐 Global variable '{variable}' = {value}")

        elif scope == "other":
            # Get the "other" instance from collision context
            other = getattr(self, '_collision_other', None)
            if not other:
                logger.debug("⚠️  set_variable: 'other' scope only available in collision events")
                return

            if relative:
                current = getattr(other, variable, 0)
                try:
                    value = current + value
                except TypeError:
                    logger.debug(f"⚠️  set_variable: Cannot add {type(value)} to {type(current)}")
                    return

            setattr(other, variable, value)
            logger.debug(f"📝 Other instance variable '{variable}' = {value}")

        else:  # scope == "sel"
            if relative:
                current = getattr(instance, variable, 0)
                try:
                    value = current + value
                except TypeError:
                    logger.debug(f"⚠️  set_variable: Cannot add {type(value)} to {type(current)}")
                    return

            setattr(instance, variable, value)
            logger.debug(f"📝 Instance variable '{variable}' = {value}")

    def execute_test_variable_action(self, instance, parameters: Dict[str, Any]):
        """Test an instance or global variable

        Returns True if condition met, False otherwise

        Parameters:
            variable: Variable name
            value: Value to compare against
            scope: "sel" for instance variable, "other" for collision other, "global" for global variable
            operation: Comparison operator (equal, less, greater, etc.)
        """
        variable = parameters.get("variable", "")
        value_str = parameters.get("value", "0")
        scope = parameters.get("scope", "sel")
        operation = parameters.get("operation", "equal")

        if not variable:
            logger.debug("⚠️  test_variable: No variable name specified")
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
                logger.debug("⚠️  test_variable: 'other' scope only available in collision events")
                return False
            current = getattr(other, variable, 0)
        else:  # scope == "sel"
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

        scope_label = "other" if scope == "other" else ("global" if scope == "global" else "sel")
        logger.debug(f"❓ Test {scope_label}.{variable} ({current}) {operation} {compare_value}: {result}")
        return result

    # ==================== ALARM ACTIONS ====================

    def execute_set_alarm_action(self, instance, parameters: Dict[str, Any]):
        """Set an alarm to trigger after N steps

        Parameters:
            alarm_number (or alarm): Which alarm (0-11)
            steps: Number of steps until alarm triggers (-1 to disable)
            relative: If True, add to current alarm value
        """
        # Accept both "alarm_number" and "alarm" parameter names for flexibility
        alarm_number = parameters.get("alarm_number", parameters.get("alarm", 0))
        alarm_number = int(alarm_number)
        steps_param = parameters.get("steps", "30")
        relative = parameters.get("relative", False)

        # Validate alarm number
        if alarm_number < 0 or alarm_number > 11:
            logger.warning(f"⚠️ set_alarm: Invalid alarm number {alarm_number} (must be 0-11)")
            return

        # Parse steps (can be a number or variable)
        steps = self._parse_value(str(steps_param), instance)
        if not isinstance(steps, (int, float)):
            logger.warning(f"⚠️ set_alarm: Invalid steps value '{steps_param}', defaulting to 30")
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
            logger.debug(f"⏰ Alarm {alarm_number} disabled for {instance.object_name}")
        else:
            logger.debug(f"⏰ Alarm {alarm_number} set to {steps} steps for {instance.object_name}")

    # ==================== SCORE/LIVES/HEALTH ACTIONS ====================

    def execute_set_score_action(self, instance, parameters: Dict[str, Any]):
        """Set the score value"""
        if not self.game_runner:
            logger.warning("⚠️  Warning: set_score requires game_runner reference")
            return

        value = int(parameters.get("value", 0))
        relative = parameters.get("relative", False)

        if relative:
            self.game_runner.score += value
        else:
            self.game_runner.score = value

        # Auto-enable score in caption when score is used
        self.game_runner.show_score_in_caption = True

        logger.debug(f"🏆 Score set to: {self.game_runner.score}")

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
            logger.warning("⚠️  Warning: set_lives requires game_runner reference")
            return

        value = int(parameters.get("value", 3))
        relative = parameters.get("relative", False)

        old_lives = self.game_runner.lives

        if relative:
            self.game_runner.lives += value
        else:
            self.game_runner.lives = value

        # Ensure lives doesn't go negative
        self.game_runner.lives = max(0, self.game_runner.lives)

        # Auto-enable lives in caption when lives are used
        self.game_runner.show_lives_in_caption = True

        logger.debug(f"❤️  Lives set to: {self.game_runner.lives}")

        # Trigger no_more_lives event if lives just reached 0
        if old_lives > 0 and self.game_runner.lives <= 0:
            logger.debug("💀 No more lives! Triggering no_more_lives event...")
            self.game_runner.trigger_no_more_lives_event(instance)

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
            logger.warning("⚠️  Warning: set_health requires game_runner reference")
            return

        value = float(parameters.get("value", 100))
        relative = parameters.get("relative", False)

        old_health = self.game_runner.health

        if relative:
            self.game_runner.health += value
        else:
            self.game_runner.health = value

        # Clamp health between 0 and 100
        self.game_runner.health = max(0, min(100, self.game_runner.health))

        # Auto-enable health in caption when health is used
        self.game_runner.show_health_in_caption = True

        logger.debug(f"💚 Health set to: {self.game_runner.health}")

        # Trigger no_more_health event if health just reached 0
        if old_health > 0 and self.game_runner.health <= 0:
            logger.debug("💔 No more health! Triggering no_more_health event...")
            self.game_runner.trigger_no_more_health_event(instance)

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

        logger.debug(f"🪟 Caption settings updated: score={self.game_runner.show_score_in_caption}, "
              f"lives={self.game_runner.show_lives_in_caption}, health={self.game_runner.show_health_in_caption}")

    def execute_show_highscore_action(self, instance, parameters: Dict[str, Any]):
        """Show highscore table dialog

        Parameters:
            background: Background color (hex string like "#FFFFDD")
            new_color: Color for new entry (hex string)
            other_color: Color for other entries (hex string)
            allow_new_entry: Whether to prompt for name if score qualifies (default True)
        """
        if not self.game_runner:
            return

        # Parse color parameters (GameMaker uses BGR format, we use RGB)
        def hex_to_rgb(hex_str, default):
            if not hex_str:
                return default
            try:
                hex_str = hex_str.lstrip('#')
                return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            except:
                return default

        background = hex_to_rgb(parameters.get('background'), (255, 255, 220))
        new_color = hex_to_rgb(parameters.get('new_color'), (255, 0, 0))
        other_color = hex_to_rgb(parameters.get('other_color'), (0, 0, 0))
        allow_new_entry = parameters.get('allow_new_entry', True)

        logger.debug(f"🏆 Show highscore action - current score: {self.game_runner.score}")

        # Show the dialog
        self.game_runner.show_highscore_dialog(
            background_color=background,
            new_color=new_color,
            other_color=other_color,
            allow_name_entry=allow_new_entry
        )

    def execute_clear_highscore_action(self, instance, parameters: Dict[str, Any]):
        """Clear highscore table"""
        if not self.game_runner:
            return

        self.game_runner.clear_highscores()

    # ==================== GAME CONTROL ACTIONS ====================

    def execute_end_game_action(self, instance, parameters: Dict[str, Any]):
        """End the game and close the window"""
        if not self.game_runner:
            return

        logger.debug("🚪 Ending game...")
        self.game_runner.running = False

    def execute_restart_game_action(self, instance, parameters: Dict[str, Any]):
        """Restart the game from the first room"""
        if not self.game_runner:
            return

        logger.debug("🔄 Restart game requested...")
        # Set flag for game loop to handle the restart
        # This ensures the room is properly recreated with fresh instances
        instance.restart_game_flag = True

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
            'sel': instance,
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
            logger.error(f"⚠️  Error executing custom code: {e}")
            import traceback
            traceback.print_exc()

    def execute_execute_script_action(self, instance, parameters: Dict[str, Any]):
        """Execute a script from the project's scripts assets

        Parameters:
            script: Name of the script to execute
            arg0-arg4: Optional arguments to pass to the script

        The script code has access to:
        - self/sel/instance: the current instance
        - game: the game runner object
        - argument0-argument4: the passed arguments
        - All Python built-ins
        """
        script_name = parameters.get('script', '')

        if not script_name:
            logger.debug("⚠️ execute_script: No script specified")
            return

        if not self.game_runner or not self.game_runner.project_data:
            logger.debug("⚠️ execute_script: No game_runner or project data")
            return

        # Get the script from project data
        scripts_data = self.game_runner.project_data.get('assets', {}).get('scripts', {})
        script_data = scripts_data.get(script_name)

        if not script_data:
            logger.warning(f"⚠️ execute_script: Script '{script_name}' not found")
            return

        code = script_data.get('code', '')

        if not code or not code.strip():
            logger.debug(f"⚠️ execute_script: Script '{script_name}' has no code")
            return

        # Parse arguments (up to 5: arg0-arg4)
        arguments = []
        for i in range(5):
            arg_key = f'arg{i}'
            arg_value = parameters.get(arg_key, '')
            if arg_value != '':
                # Parse the argument value (could be a number, string, or variable reference)
                parsed_value = self._parse_value(str(arg_value), instance)
                arguments.append(parsed_value)
            else:
                arguments.append(None)

        # Create execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'sel': instance,
            'game': self.game_runner,
            'instance': instance,
            # Add common modules for convenience
            'math': __import__('math'),
            'random': __import__('random'),
            # GameMaker-style argument variables
            'argument0': arguments[0],
            'argument1': arguments[1],
            'argument2': arguments[2],
            'argument3': arguments[3],
            'argument4': arguments[4],
            'argument_count': sum(1 for a in arguments if a is not None),
        }

        exec_locals = {}

        try:
            logger.debug(f"📜 Executing script: {script_name}")
            # Execute the script code
            exec(code, exec_globals, exec_locals)

            # Apply any changes to instance variables from locals
            for key, value in exec_locals.items():
                if not key.startswith('__'):
                    setattr(instance, key, value)

        except Exception as e:
            logger.error(f"⚠️ Error executing script '{script_name}': {e}")
            import traceback
            traceback.print_exc()

    # ==================== INSTANCE ACTIONS ====================

    def execute_destroy_instance_action(self, instance, parameters: Dict[str, Any]):
        """Execute destroy instance action

        Parameters:
            target: "self"/"sel" or "other" - which instance to destroy
        """
        target = parameters.get("target", "self")

        if target == "other" and hasattr(self, '_collision_other') and self._collision_other:
            # Destroy the other instance in a collision context
            logger.debug(f"💀 Destroying other instance: {self._collision_other.object_name}")
            self._collision_other.to_destroy = True
        else:
            # Destroy self (default behavior) - accept both "self" and "sel"
            logger.debug(f"💀 Destroying instance: {instance.object_name}")
            instance.to_destroy = True

    def execute_create_instance_action(self, instance, parameters: Dict[str, Any]):
        """Create a new instance of an object at a specified position

        Parameters:
            object: The object type to create
            x: X position for the new instance
            y: Y position for the new instance
            relative: If True, position is relative to current instance
        """
        object_name = parameters.get("object", "")
        x_param = parameters.get("x", 0)
        y_param = parameters.get("y", 0)
        relative = parameters.get("relative", False)

        if not object_name:
            logger.debug("⚠️ create_instance: No object specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ create_instance: No game_runner reference")
            return

        # Parse position values (can be expressions)
        x = self._parse_value(str(x_param), instance)
        y = self._parse_value(str(y_param), instance)

        try:
            x = float(x) if x is not None else 0.0
            y = float(y) if y is not None else 0.0
        except (ValueError, TypeError):
            x = 0.0
            y = 0.0

        # Apply relative positioning
        if relative:
            x = instance.x + x
            y = instance.y + y

        # Get the object's data
        objects_data = self.game_runner.project_data.get('assets', {}).get('objects', {})
        if object_name not in objects_data:
            logger.debug(f"⚠️ create_instance: Object '{object_name}' not found")
            return

        object_data = objects_data[object_name]

        # Import GameInstance locally to avoid circular imports
        from runtime.game_runner import GameInstance

        # Create new instance
        instance_data = {
            'object_name': object_name,
            'x': x,
            'y': y,
            'instance_id': id(object_data) + int(x * 1000) + int(y * 1000000)  # Generate unique ID
        }

        new_instance = GameInstance(
            object_name,
            x,
            y,
            instance_data,
            action_executor=self
        )

        # Set up the new instance with object data and sprite
        new_instance.set_object_data(object_data)

        # Get sprite for the new instance
        sprite_name = object_data.get('sprite', '')
        if sprite_name and sprite_name in self.game_runner.sprites:
            new_instance.set_sprite(self.game_runner.sprites[sprite_name])

        # Add to current room
        if self.game_runner.current_room:
            self.game_runner.current_room.instances.append(new_instance)
            self.game_runner.current_room._add_to_grid(new_instance)

            # Execute create event for the new instance
            events = object_data.get('events', {})
            if 'create' in events:
                self.execute_event(new_instance, 'create', events)

            logger.debug(f"➕ Created instance of '{object_name}' at ({x}, {y})")
        else:
            logger.debug("⚠️ create_instance: No current room to add instance to")

    def execute_change_instance_action(self, instance, parameters: Dict[str, Any]):
        """Change instance into a different object type

        This is like destroying the current instance and creating a new one
        of a different type at the same position.

        Parameters:
            object: The new object type to change into
            perform_events: Whether to execute destroy/create events (default True)
            target: "sel" or "other" - which instance to change (default "sel")
        """
        new_object_name = parameters.get("object", "")
        perform_events = parameters.get("perform_events", True)
        target = parameters.get("target", "sel")

        if not new_object_name:
            logger.debug("⚠️ change_instance: No object specified")
            return

        # Determine which instance to change
        if target == "other" and hasattr(self, '_collision_other') and self._collision_other:
            target_instance = self._collision_other
        else:
            target_instance = instance

        logger.debug(f"🔄 Changing {target_instance.object_name} into {new_object_name}")

        # Get the game runner to access objects data and room
        if not self.game_runner:
            logger.debug("⚠️ change_instance: No game_runner reference")
            return

        # Get the new object's data
        objects_data = self.game_runner.project_data.get('assets', {}).get('objects', {})
        if new_object_name not in objects_data:
            logger.debug(f"⚠️ change_instance: Object '{new_object_name}' not found")
            return

        new_object_data = objects_data[new_object_name]

        # Execute destroy event if requested
        if perform_events and target_instance.object_data:
            events = target_instance.object_data.get('events', {})
            if 'destroy' in events:
                logger.debug(f"  💥 Executing destroy event for {target_instance.object_name}")
                self.execute_event(target_instance, 'destroy', events)

        # Store current position and properties
        old_x = target_instance.x
        old_y = target_instance.y

        # Change the object type
        target_instance.object_name = new_object_name
        # Use set_object_data to properly update cached fields (_cached_object_data, _collision_targets)
        target_instance.set_object_data(new_object_data)

        # Update sprite if the new object has a different one
        sprite_name = new_object_data.get('sprite', '')
        if sprite_name and sprite_name in self.game_runner.sprites:
            # Use set_sprite to properly update cached dimensions (_cached_width, _cached_height)
            target_instance.set_sprite(self.game_runner.sprites[sprite_name])
            logger.debug(f"  🖼️ Updated sprite to: {sprite_name}")

        # Reset collision tracking for the changed instance
        if hasattr(target_instance, '_active_collisions'):
            target_instance._active_collisions = set()
        if hasattr(target_instance, '_collision_cooldowns'):
            target_instance._collision_cooldowns = {}

        # Execute create event for new object type if requested
        if perform_events:
            events = new_object_data.get('events', {})
            if 'create' in events:
                logger.debug(f"  🎬 Executing create event for {new_object_name}")
                self.execute_event(target_instance, 'create', events)

        logger.debug(f"  ✅ Changed to {new_object_name} at ({old_x}, {old_y})")

    # ==================== DRAWING ACTIONS ====================

    def execute_set_draw_color_action(self, instance, parameters: Dict[str, Any]):
        """Set the drawing color for subsequent draw operations

        Parameters:
            color: Color in hex format (e.g., "#FF0000" for red)
        """
        color = parameters.get("color", "#000000")

        # Parse hex color to RGB tuple
        def hex_to_rgb(hex_str):
            if not hex_str:
                return (0, 0, 0)
            hex_str = hex_str.lstrip('#')
            try:
                return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            except:
                return (0, 0, 0)

        rgb_color = hex_to_rgb(color)

        # Store drawing color on instance for draw events
        instance.draw_color = rgb_color

        # Also store on game runner for global access
        if self.game_runner:
            self.game_runner.draw_color = rgb_color

        logger.debug(f"🎨 Set drawing color to {color} ({rgb_color}) for {instance.object_name}")

    def execute_draw_text_action(self, instance, parameters: Dict[str, Any]):
        """Draw text at specified position

        Parameters:
            x: X coordinate (default: instance.x)
            y: Y coordinate (default: instance.y)
            text: Text string to draw (supports expressions)
        """
        import pygame

        # Parse parameters with expression support
        x = self._parse_value(parameters.get("x", instance.x), instance)
        y = self._parse_value(parameters.get("y", instance.y), instance)
        text = str(self._parse_value(parameters.get("text", ""), instance))

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'text',
            'x': x,
            'y': y,
            'text': text,
            'color': color
        })

        logger.debug(f"📝 Queued draw_text: '{text}' at ({x}, {y}) with color {color}")

    def execute_draw_rectangle_action(self, instance, parameters: Dict[str, Any]):
        """Draw a rectangle (filled or outlined)

        Parameters:
            x1: Left X coordinate
            y1: Top Y coordinate
            x2: Right X coordinate
            y2: Bottom Y coordinate
            filled: True for filled, False for outline (default: True)
        """
        import pygame

        # Parse parameters with expression support
        x1 = self._parse_value(parameters.get("x1", 0), instance)
        y1 = self._parse_value(parameters.get("y1", 0), instance)
        x2 = self._parse_value(parameters.get("x2", 100), instance)
        y2 = self._parse_value(parameters.get("y2", 100), instance)
        filled = self._parse_value(parameters.get("filled", True), instance)

        # Convert to boolean if string
        if isinstance(filled, str):
            filled = filled.lower() in ('true', '1', 'yes')

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'rectangle',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'filled': filled,
            'color': color
        })

        fill_type = "filled" if filled else "outline"
        logger.debug(f"📐 Queued draw_rectangle: {fill_type} rect ({x1}, {y1}) to ({x2}, {y2}) with color {color}")

    def execute_draw_ellipse_action(self, instance, parameters: Dict[str, Any]):
        """Draw an ellipse or circle (filled or outlined)

        Parameters:
            x1: Left X coordinate
            y1: Top Y coordinate
            x2: Right X coordinate
            y2: Bottom Y coordinate
            filled: True for filled, False for outline (default: True)
        """
        import pygame

        # Parse parameters with expression support
        x1 = self._parse_value(parameters.get("x1", 0), instance)
        y1 = self._parse_value(parameters.get("y1", 0), instance)
        x2 = self._parse_value(parameters.get("x2", 100), instance)
        y2 = self._parse_value(parameters.get("y2", 100), instance)
        filled = self._parse_value(parameters.get("filled", True), instance)

        # Convert to boolean if string
        if isinstance(filled, str):
            filled = filled.lower() in ('true', '1', 'yes')

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'ellipse',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'filled': filled,
            'color': color
        })

        fill_type = "filled" if filled else "outline"
        logger.debug(f"⭕ Queued draw_ellipse: {fill_type} ellipse ({x1}, {y1}) to ({x2}, {y2}) with color {color}")

    def execute_draw_line_action(self, instance, parameters: Dict[str, Any]):
        """Draw a line between two points

        Parameters:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
        """
        import pygame

        # Parse parameters with expression support
        x1 = self._parse_value(parameters.get("x1", 0), instance)
        y1 = self._parse_value(parameters.get("y1", 0), instance)
        x2 = self._parse_value(parameters.get("x2", 100), instance)
        y2 = self._parse_value(parameters.get("y2", 100), instance)

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'line',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'color': color
        })

        logger.debug(f"➖ Queued draw_line: from ({x1}, {y1}) to ({x2}, {y2}) with color {color}")

    def execute_draw_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Draw a sprite at specified position

        Parameters:
            sprite: Name of the sprite to draw
            x: X coordinate (default: 0)
            y: Y coordinate (default: 0)
            subimage: Frame index for animated sprites (default: 0)
        """
        import pygame

        # Parse parameters with expression support
        sprite_name = self._parse_value(parameters.get("sprite", ""), instance)
        x = self._parse_value(parameters.get("x", 0), instance)
        y = self._parse_value(parameters.get("y", 0), instance)
        subimage = self._parse_value(parameters.get("subimage", 0), instance)

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'sprite',
            'sprite_name': sprite_name,
            'x': x,
            'y': y,
            'subimage': subimage
        })

        logger.debug(f"🖼️ Queued draw_sprite: '{sprite_name}' at ({x}, {y}) frame {subimage}")

    # ==================== AUDIO ACTIONS ====================

    def execute_stop_sound_action(self, instance, parameters: Dict[str, Any]):
        """Stop playing a specific sound

        Parameters:
            sound: The sound name to stop
        """
        sound_name = parameters.get("sound", "")

        if not sound_name:
            logger.debug("⚠️ stop_sound: No sound specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ stop_sound: No game_runner reference")
            return

        # Get the sound from the asset manager
        if hasattr(self.game_runner, 'sounds') and sound_name in self.game_runner.sounds:
            sound = self.game_runner.sounds[sound_name]
            if hasattr(sound, 'stop'):
                sound.stop()
                logger.debug(f"🔇 Stopped sound: {sound_name}")
            else:
                # Try pygame.mixer.stop for all sounds
                import pygame
                pygame.mixer.stop()
                logger.debug(f"🔇 Stopped all sounds (trying to stop: {sound_name})")
        else:
            logger.debug(f"⚠️ stop_sound: Sound '{sound_name}' not found")

    # ==================== ROOM CONFIGURATION ACTIONS ====================

    def execute_set_room_caption_action(self, instance, parameters: Dict[str, Any]):
        """Set room/window caption text

        Parameters:
            caption: Caption text to display
        """
        if not self.game_runner:
            logger.debug("⚠️ set_room_caption: No game_runner reference")
            return

        # Get caption directly (no expression parsing for text)
        caption = str(parameters.get("caption", ""))

        # Update the window caption
        self.game_runner.window_caption = caption

        # Update the display caption immediately
        self.game_runner.update_caption()

        logger.debug(f"🏷️ Set room caption: '{caption}'")

    def execute_set_room_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set game speed (frames per second)

        Parameters:
            speed: Target FPS (default: 30)
        """
        if not self.game_runner:
            logger.debug("⚠️ set_room_speed: No game_runner reference")
            return

        # Parse speed with expression support
        speed = self._parse_value(parameters.get("speed", 30), instance)

        try:
            speed = int(speed)
            if speed < 1:
                speed = 1
            if speed > 240:
                speed = 240  # Cap at reasonable maximum
        except (ValueError, TypeError):
            speed = 30

        # Update the game FPS
        self.game_runner.fps = speed

        logger.debug(f"⏱️ Set room speed: {speed} FPS")

    def execute_set_background_color_action(self, instance, parameters: Dict[str, Any]):
        """Set room background color

        Parameters:
            color: Background color (hex string like "#87CEEB")
            show_color: Whether to display the color (default: True)
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ set_background_color: No current room")
            return

        # Parse parameters
        color_str = parameters.get("color", "#000000")
        show_color = parameters.get("show_color", True)

        # Convert to boolean if string
        if isinstance(show_color, str):
            show_color = show_color.lower() in ('true', '1', 'yes')

        # Parse color
        color_rgb = self._parse_color(color_str)

        # Update room background color
        self.game_runner.current_room.background_color = color_rgb

        # If show_color is False, we could hide the background, but for now just update the color
        # (GameMaker's "show_color" typically controls whether solid color or image is displayed)

        logger.debug(f"🎨 Set background color: {color_str} → {color_rgb}, show={show_color}")

    def execute_set_background_action(self, instance, parameters: Dict[str, Any]):
        """Set room background image with tiling and scrolling options

        Parameters:
            background: Background/sprite name to use
            visible: Show background (default: True)
            foreground: Draw in front of objects (default: False)
            tiled_h: Tile horizontally (default: False)
            tiled_v: Tile vertically (default: False)
            hspeed: Horizontal scroll speed (default: 0)
            vspeed: Vertical scroll speed (default: 0)
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ set_background: No current room")
            return

        # Parse parameters
        background_name = str(self._parse_value(parameters.get("background", ""), instance))
        visible = self._parse_value(parameters.get("visible", True), instance)
        foreground = self._parse_value(parameters.get("foreground", False), instance)
        tiled_h = self._parse_value(parameters.get("tiled_h", False), instance)
        tiled_v = self._parse_value(parameters.get("tiled_v", False), instance)
        hspeed = self._parse_value(parameters.get("hspeed", 0), instance)
        vspeed = self._parse_value(parameters.get("vspeed", 0), instance)

        # Convert booleans
        if isinstance(visible, str):
            visible = visible.lower() in ('true', '1', 'yes')
        if isinstance(foreground, str):
            foreground = foreground.lower() in ('true', '1', 'yes')
        if isinstance(tiled_h, str):
            tiled_h = tiled_h.lower() in ('true', '1', 'yes')
        if isinstance(tiled_v, str):
            tiled_v = tiled_v.lower() in ('true', '1', 'yes')

        # Look up the background/sprite
        import pygame
        from pathlib import Path

        background_surface = None

        # Try to load from sprites or backgrounds
        if hasattr(self.game_runner, 'sprites') and background_name in self.game_runner.sprites:
            sprite = self.game_runner.sprites[background_name]
            if sprite.surface:
                background_surface = sprite.surface
        elif hasattr(self.game_runner, 'project_data'):
            # Try to load from backgrounds in project data
            backgrounds = self.game_runner.project_data.get('assets', {}).get('backgrounds', {})
            if background_name in backgrounds:
                bg_data = backgrounds[background_name]
                file_path = bg_data.get('file_path', '')
                if file_path:
                    full_path = self.game_runner.project_path / file_path
                    if full_path.exists():
                        try:
                            background_surface = pygame.image.load(str(full_path)).convert()
                        except Exception as e:
                            logger.error(f"⚠️ Error loading background '{background_name}': {e}")

        if background_surface and visible:
            # Update room background
            self.game_runner.current_room.background_surface = background_surface
            self.game_runner.current_room.background_image_name = background_name
            self.game_runner.current_room.tile_horizontal = tiled_h
            self.game_runner.current_room.tile_vertical = tiled_v

            # Note: foreground, hspeed, vspeed would require additional room properties
            # For now, we'll just acknowledge them
            logger.debug(f"🖼️ Set background: '{background_name}', visible={visible}, "
                  f"tiled_h={tiled_h}, tiled_v={tiled_v}, foreground={foreground}")

            if hspeed != 0 or vspeed != 0:
                logger.debug(f"   Scroll speed: h={hspeed}, v={vspeed} (scrolling not yet implemented)")
        elif not visible:
            # Clear background
            self.game_runner.current_room.background_surface = None
            logger.debug(f"🖼️ Background hidden")
        else:
            logger.debug(f"⚠️ set_background: Background '{background_name}' not found")

    def _parse_color(self, color_str: str) -> tuple:
        """Parse color string to RGB tuple (helper method)"""
        if isinstance(color_str, tuple):
            return color_str

        if isinstance(color_str, str) and color_str.startswith('#'):
            try:
                hex_color = color_str.lstrip('#')
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (r, g, b)
            except (ValueError, IndexError):
                pass

        # Default to black
        return (0, 0, 0)

    # ==================== CONTROL ACTIONS (Additional) ====================

    def execute_test_chance_action(self, instance, parameters: Dict[str, Any]):
        """Test a random probability (1 in N chance)

        Parameters:
            sides: Number of sides on the dice (default 6)

        Returns True if the random roll succeeds (1/N probability)
        """
        import random

        sides = parameters.get("sides", 6)
        try:
            sides = int(sides)
            if sides < 1:
                sides = 1
        except (ValueError, TypeError):
            sides = 6

        # Roll the dice - success if we roll a 1 (1/N chance)
        roll = random.randint(1, sides)
        result = (roll == 1)

        logger.debug(f"🎲 Test chance (1 in {sides}): rolled {roll}, result={result}")
        return result

    def execute_test_expression_action(self, instance, parameters: Dict[str, Any]):
        """Test/evaluate a GML-style expression

        Parameters:
            expression: String expression to evaluate (can access instance variables)

        Returns True if expression evaluates to truthy value, False otherwise

        Supported expressions:
        - Variable comparisons: "x < 100", "score >= 1000"
        - Math expressions: "x + y > 200", "hspeed * 2 < 10"
        - Boolean expressions: "lives > 0 and health > 50"
        - Instance properties: "self.x", "self.y", "self.hspeed"
        """
        expression = parameters.get("expression", "")

        if not expression or not expression.strip():
            logger.debug("⚠️  test_expression: Empty expression")
            return False

        try:
            # Build safe namespace for evaluation
            namespace = {
                # Instance properties
                'self': instance,
                'x': instance.x,
                'y': instance.y,
                'hspeed': getattr(instance, 'hspeed', 0),
                'vspeed': getattr(instance, 'vspeed', 0),
                'speed': getattr(instance, 'speed', 0),
                'direction': getattr(instance, 'direction', 0),
                'image_index': getattr(instance, 'image_index', 0),
                'image_speed': getattr(instance, 'image_speed', 1.0),

                # Game state (if available)
                'score': getattr(self.game_runner, 'score', 0) if self.game_runner else 0,
                'lives': getattr(self.game_runner, 'lives', 0) if self.game_runner else 0,
                'health': getattr(self.game_runner, 'health', 100) if self.game_runner else 100,

                # Room info (if available)
                'room_width': getattr(self.game_runner.current_room, 'width', 0) if self.game_runner and self.game_runner.current_room else 0,
                'room_height': getattr(self.game_runner.current_room, 'height', 0) if self.game_runner and self.game_runner.current_room else 0,

                # Math functions
                'abs': abs,
                'min': min,
                'max': max,
                'round': round,

                # Custom instance variables
                **{k: v for k, v in instance.__dict__.items() if not k.startswith('_')}
            }

            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, namespace)

            # Convert to boolean
            result_bool = bool(result)

            logger.debug(f"📝 Test expression '{expression}' = {result} (bool: {result_bool})")
            return result_bool

        except Exception as e:
            logger.error(f"⚠️  test_expression: Error evaluating '{expression}': {e}")
            return False

    def execute_test_question_action(self, instance, parameters: Dict[str, Any]):
        """Show a yes/no question dialog to the user

        Parameters:
            question: Question text to display

        Returns True if user clicks Yes, False if user clicks No

        This displays a modal dialog with Yes/No buttons.
        """
        question = parameters.get("question", "Continue?")

        try:
            from PySide6.QtWidgets import QMessageBox, QApplication

            # Check if QApplication exists
            if QApplication.instance() is None:
                logger.debug(f"⚠️  test_question: No QApplication, defaulting to True for '{question}'")
                return True

            # Create message box
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Question")
            msg_box.setText(question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            msg_box.setIcon(QMessageBox.Question)

            # Show dialog and get result
            result = msg_box.exec()
            answer = (result == QMessageBox.Yes)

            logger.debug(f"❔ Question: '{question}' → {'Yes' if answer else 'No'}")
            return answer

        except ImportError:
            # Fallback for environments without Qt (like testing)
            logger.debug(f"⚠️  test_question: Qt not available, defaulting to True for '{question}'")
            return True
        except Exception as e:
            logger.error(f"⚠️  test_question: Error showing dialog: {e}")
            return True

    def execute_test_instance_count_action(self, instance, parameters: Dict[str, Any]):
        """Test the number of instances of a specific object type

        Parameters:
            object: Object type name to count
            number: Number to compare against
            operation: Comparison operator (equal, less, greater, less_equal, greater_equal, not_equal)

        Returns True if condition is met, False otherwise

        Example:
            - Check if there are exactly 5 enemies: object="obj_enemy", number=5, operation="equal"
            - Check if there are less than 10 bullets: object="obj_bullet", number=10, operation="less"
        """
        object_type = parameters.get("object", "")
        target_count = parameters.get("number", 0)
        operation = parameters.get("operation", "equal")

        if not object_type:
            logger.debug("⚠️  test_instance_count: No object type specified")
            return False

        try:
            target_count = int(target_count)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  test_instance_count: Invalid number '{target_count}'")
            return False

        # Count instances of this object type
        if not self.game_runner or not hasattr(self.game_runner, 'instances'):
            logger.debug("⚠️  test_instance_count: No game runner or instances available")
            return False

        # Count instances matching the object type
        actual_count = sum(1 for inst in self.game_runner.instances
                          if getattr(inst, 'object_name', '') == object_type)

        # Perform comparison
        result = False
        if operation == "equal":
            result = (actual_count == target_count)
        elif operation == "less":
            result = (actual_count < target_count)
        elif operation == "greater":
            result = (actual_count > target_count)
        elif operation == "less_equal":
            result = (actual_count <= target_count)
        elif operation == "greater_equal":
            result = (actual_count >= target_count)
        elif operation == "not_equal":
            result = (actual_count != target_count)
        else:
            logger.debug(f"⚠️  test_instance_count: Unknown operation '{operation}'")
            return False

        logger.debug(f"🔢 Test instance count: {object_type} count={actual_count} {operation} {target_count} → {result}")
        return result

    # ==================== ANIMATION ACTIONS ====================

    def execute_set_image_index_action(self, instance, parameters: Dict[str, Any]):
        """Set the current animation frame"""
        frame = parameters.get("frame", 0)
        try:
            frame = int(frame)
        except (ValueError, TypeError):
            frame = 0

        instance.image_index = float(frame)
        logger.debug(f"🎬 Set image_index to {frame} for {instance.object_name}")

    def execute_set_image_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set the animation speed multiplier"""
        speed = parameters.get("speed", 1.0)
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            speed = 1.0

        instance.image_speed = speed
        logger.debug(f"⏩ Set image_speed to {speed} for {instance.object_name}")

    def execute_stop_animation_action(self, instance, parameters: Dict[str, Any]):
        """Stop the sprite animation"""
        instance.image_speed = 0.0
        logger.debug(f"⏸️ Stopped animation for {instance.object_name}")

    def execute_start_animation_action(self, instance, parameters: Dict[str, Any]):
        """Start/resume the sprite animation"""
        instance.image_speed = 1.0
        logger.debug(f"▶️ Started animation for {instance.object_name}")

    def execute_set_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Set the sprite for an instance or modify current sprite animation

        Parameters:
            sprite: Sprite name to use, or "<self>" to keep current sprite
            subimage: Frame index to set (-1 = don't change)
            speed: Animation speed to set (-1 = don't change)

        When sprite is "<self>", only the animation properties (subimage, speed)
        are modified without changing the sprite. This allows stopping/starting
        animation on the current sprite.
        """
        sprite_name = parameters.get("sprite", "<self>")
        subimage = parameters.get("subimage", -1)
        speed = parameters.get("speed", -1)

        # Parse values (can be expressions)
        try:
            subimage = int(self._parse_value(str(subimage), instance))
        except (ValueError, TypeError):
            subimage = -1

        try:
            speed = float(self._parse_value(str(speed), instance))
        except (ValueError, TypeError):
            speed = -1

        # Handle sprite change (unless <self>)
        if sprite_name != "<self>" and sprite_name:
            if self.game_runner and sprite_name in self.game_runner.sprites:
                instance.set_sprite(self.game_runner.sprites[sprite_name])
                logger.debug(f"🖼️ Set sprite to '{sprite_name}' for {instance.object_name}")
            else:
                logger.debug(f"⚠️ set_sprite: Sprite '{sprite_name}' not found")

        # Handle subimage (frame index)
        if subimage >= 0:
            instance.image_index = float(subimage)
            logger.debug(f"🎬 Set image_index to {subimage} for {instance.object_name}")

        # Handle animation speed (only print when value changes)
        if speed >= 0:
            old_speed = getattr(instance, 'image_speed', 1.0)
            if old_speed != speed:
                instance.image_speed = speed
                if speed == 0:
                    logger.debug(f"⏸️ Stopped animation for {instance.object_name}")
                else:
                    logger.debug(f"⏩ Set image_speed to {speed} for {instance.object_name}")
            else:
                instance.image_speed = speed  # Still set it, just don't print

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
            logger.debug(f"  ⚠️ Event '{event_name}' not found in events_data. Available: {list(events_data.keys())}")
            return

        event_data = events_data[event_name]
        actions = event_data.get("actions", [])

        if not actions:
            logger.debug(f"  ⚠️ No actions defined for event '{event_name}'")
            return

        logger.debug(f"  🎬 Executing {len(actions)} action(s) for {event_name}")

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
            result = self.handle_collision_action(instance, action_data, other_instance)

            # Check if this was a conditional action that returned False
            if result is False:
                skip_next = True
                condition_was_false = True
            elif result is True:
                condition_was_false = False

            i += 1

    def handle_collision_action(self, instance, action_data: Dict[str, Any], other_instance):
        """Execute a collision action with knowledge of both self and other

        This method has a different signature (3 params) than standard action handlers,
        so it's named differently to avoid auto-registration.

        Returns:
            - True/False for conditional actions
            - None for regular actions
        """
        action_name = action_data.get("action")
        parameters = action_data.get("parameters", {})

        if action_name == "destroy_instance":
            target = parameters.get("target", "self")

            if target in ("self", "sel"):
                logger.debug(f"  💀 Destroying instance: {instance.object_name}")
                instance.to_destroy = True
            elif target == "other":
                logger.debug(f"  💀 Destroying other instance: {other_instance.object_name}")
                other_instance.to_destroy = True
            return None
        else:
            # For all other actions, use the regular action executor
            return self.execute_action(instance, action_data)
