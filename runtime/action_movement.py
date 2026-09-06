#!/usr/bin/env python3
"""Movement actions for :class:`~runtime.action_executor.ActionExecutor`.

The 18 methods that change where an instance is or how it is travelling:
hspeed/vspeed, speed+direction, gravity and friction, the grid move and its
snap, jump-to (position / start / random), move-towards-point, move-to-contact,
bounce, the two reverses, and wrap-around-room.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 2) as a MIXIN -- see
``runtime/action_drawing.py``'s header for why these are sibling modules rather
than the package layout the plan sketched (35 tests load the engine by file
path, deliberately bypassing ``__init__.py`` so it imports without pygame).

``_set_speed_component`` comes along because it is movement-only: its sole
callers are the hspeed/vspeed setters in this file. The broader helpers these
methods reach through ``self`` -- ``_parse_value``, ``_evaluate_expression``,
``_resolve_target_instances`` -- stay on ``ActionExecutor``, per the plan's
risk callout about helpers with many callers.

``random`` and ``ast`` are imported *inside* two of these methods rather than
at module level; that is how they were written and the move keeps it, so the
import list here stays as light as the engine module's own.
"""

import math
from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


# Vector helpers folded in from the retired runtime/action_handlers/base.py
# (docs/POST_1_0_REFACTOR.md companion teardown). They live here because the
# three actions below are their only callers.
_FULL_CIRCLE_DEGREES = 360


def _direction_to_vector(direction_degrees, speed=1.0):
    """GameMaker convention: 0 deg = right, 90 = up, 180 = left, 270 = down."""
    angle_rad = math.radians(direction_degrees)
    hspeed = math.cos(angle_rad) * speed
    # Negative because screen Y increases downward.
    vspeed = -math.sin(angle_rad) * speed
    return (hspeed, vspeed)


def _vector_to_direction(hspeed, vspeed):
    """Inverse of _direction_to_vector; 0-360 degrees."""
    if hspeed == 0 and vspeed == 0:
        return 0
    return math.degrees(math.atan2(-vspeed, hspeed)) % _FULL_CIRCLE_DEGREES


class MovementMixin:
    """Movement ``execute_*_action`` methods, mixed into ``ActionExecutor``."""

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
        instance._has_intended_move = True
    def _set_speed_component(self, instance, parameters: Dict[str, Any], component: str) -> None:
        # Shared kernel for execute_set_{h,v}speed_action.
        # component is "hspeed" or "vspeed" — also the preferred parameter key.
        action_name = f"set_{component}"
        speed_value = parameters.get(component, parameters.get("value", parameters.get("speed", "0")))
        logger.debug(f"  🔍 {action_name}: raw value = '{speed_value}', _collision_other = {getattr(self, '_collision_other', None)}")
        speed = self._parse_value(str(speed_value), instance)
        logger.debug(f"  🔍 {action_name}: parsed value = {speed}")
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  {action_name}: Invalid speed value '{speed_value}'")
            return
        old_speed = getattr(instance, component)
        setattr(instance, component, speed)
        if old_speed != speed:
            logger.debug(f"  🏃 {instance.object_name} {component}: {old_speed} → {speed}")
    def execute_set_hspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set horizontal speed for smooth movement

        Accepts numbers or variable references like other.hspeed
        """
        self._set_speed_component(instance, parameters, "hspeed")
    def execute_set_vspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set vertical speed for smooth movement

        Accepts numbers or variable references like other.vspeed
        """
        self._set_speed_component(instance, parameters, "vspeed")
    def execute_bounce_action(self, instance, parameters: Dict[str, Any]):
        """Bounce off solid objects by reversing velocity.

        Parameters:
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

        # Values can be expressions (e.g. the identity 'self.gravity' filled
        # in when only one half of the pair is assigned in code — audit H4),
        # matching set_direction_speed.
        direction = self._parse_value(str(direction), instance)
        gravity = self._parse_value(str(gravity), instance)

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

        if not self.game_runner or not self.game_runner.current_room:
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

            for other in self.game_runner.current_room.instances:
                if other is instance:
                    continue

                # Check object type filter. `solid` lives on the object
                # definition (cached on the instance as _cached_object_data),
                # not as a direct GameInstance attribute — reading
                # getattr(other, 'solid', False) here always returned False
                # and let move_to_contact pass through every wall, snapping
                # the mover to max_distance instead of stopping at contact.
                if object_type == "all":
                    should_check = True
                elif object_type == "solid":
                    other_obj_data = getattr(other, '_cached_object_data', None) or {}
                    should_check = bool(other_obj_data.get('solid', False))
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
        # Only move the "other" instance if explicitly requested
        push_other = parameters.get("push_other", False)

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
        """Jump to the starting position (where the instance was created).

        Honors GM's "Applies to" selector via target/target_object — e.g.
        treasure resets every monster to its spawn when the player dies, and
        teleports an eaten scared monster (target "other") home.
        """
        for target_instance in self._resolve_target_instances(instance, parameters):
            start_x = getattr(target_instance, 'xstart', target_instance.x)
            start_y = getattr(target_instance, 'ystart', target_instance.y)
            target_instance.x = start_x
            target_instance.y = start_y
            logger.debug(f"  🏠 {target_instance.object_name} jumped to start "
                         f"position ({start_x}, {start_y})")
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

        # Tolerate stringified lists like `"['down', 'up']"`. The
        # events-panel UI round-trips list-typed action params through
        # a single-line QLineEdit, which serialises a Python list as
        # its repr() rather than as an actual list — without this
        # fallback parsing, monster_ud's `directions: "['down', 'up']"`
        # fell through to direction_map.get("[...]") -> 0 and the
        # monster sat motionless. See samples/maze_3/objects/monster_ud.
        if isinstance(directions, str):
            stripped = directions.strip()
            if stripped.startswith('[') and stripped.endswith(']'):
                try:
                    import ast
                    parsed = ast.literal_eval(stripped)
                    if isinstance(parsed, list):
                        directions = parsed
                except (ValueError, SyntaxError):
                    pass  # not a valid list literal, fall through

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

        # Snap floating-point noise near zero to exact zero. cos(π/2) is
        # 6.12e-17 in float64, not 0 — without this, "press Up" leaves a
        # tiny positive hspeed that downstream sign-tests (e.g. if_can_push:
        # `push_dx = +32 if dx > 0`) interpret as "moving right", causing
        # diagonal block pushes when the player presses a cardinal key.
        if abs(instance.hspeed) < 1e-9:
            instance.hspeed = 0.0
        if abs(instance.vspeed) < 1e-9:
            instance.vspeed = 0.0

        logger.debug(f"   ➡️ Start Moving Direction: {direction}° at speed {speed}")
        logger.debug(f"      hspeed={instance.hspeed:.2f}, vspeed={instance.vspeed:.2f}")
    def execute_snap_to_grid_action(self, instance, parameters: Dict[str, Any]):
        """Snap instance to nearest grid position"""
        grid_size = int(parameters.get("grid_size", 32))

        # Round to nearest grid position
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size

    def execute_stop_movement_action(self, instance, parameters: Dict[str, Any]):
        """Stop all movement by setting speeds to zero"""
        instance.hspeed = 0
        instance.vspeed = 0

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


    def _parse_float(self, value, instance=None, default=0.0):
        """Coerce an action parameter to float, resolving expressions first.

        Folded in from the retired action_handlers/base.py `parse_float`, whose
        `ctx` argument was always this executor.
        """
        if value is None:
            return default
        parsed = (self._parse_value(str(value), instance)
                  if isinstance(value, str) else value)
        try:
            return float(parsed) if parsed is not None else default
        except (ValueError, TypeError):
            return default

    def execute_move_free_action(self, instance, parameters: Dict[str, Any]):
        """Move at an exact direction and speed.

        Delegates to set_direction_speed -- same semantics, kept as its own
        registered action because the UI registers `move_free` by that name.
        """
        self.execute_set_direction_speed_action(instance, parameters)

    def execute_set_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set the speed magnitude, preserving the current direction.

        Reads the direction out of the existing (hspeed, vspeed) vector and
        rebuilds the velocity at the new magnitude. Stationary means direction
        0 (right), so choosing a non-zero speed actually starts movement.
        """
        speed = self._parse_float(
            parameters.get("speed", parameters.get("value", 0)), instance, default=0.0)
        current_direction = _vector_to_direction(instance.hspeed, instance.vspeed)
        hspeed, vspeed = _direction_to_vector(current_direction, speed)
        instance.hspeed = hspeed
        instance.vspeed = vspeed
        logger.debug("  %s speed=%s (dir preserved at %.1f deg)",
                     instance.object_name, speed, current_direction)

    def execute_set_direction_action(self, instance, parameters: Dict[str, Any]):
        """Set the direction angle, preserving the current speed magnitude.

        If currently stationary, setting a direction does NOT start movement --
        that matches GameMaker.
        """
        direction = self._parse_float(
            parameters.get("direction", parameters.get("value", 0)), instance, default=0.0)
        current_speed = math.sqrt(instance.hspeed ** 2 + instance.vspeed ** 2)
        hspeed, vspeed = _direction_to_vector(direction, current_speed)
        instance.hspeed = hspeed
        instance.vspeed = vspeed
        logger.debug("  %s direction=%s deg (speed preserved at %.2f)",
                     instance.object_name, direction, current_speed)
