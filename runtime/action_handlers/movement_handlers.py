#!/usr/bin/env python3
"""
Movement Action Handlers

Handles all movement-related actions: speed setting, direction, jumping,
wrapping, bouncing, etc.
"""

from typing import Dict, Any
import math
import random

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_int, parse_bool,
    direction_to_vector, get_room_dimensions, get_instance_dimensions,
    snap_to_grid, is_on_grid, get_collision_speeds, get_collision_other,
    DEFAULT_GRID_SIZE, DEFAULT_SPEED,
)

logger = get_logger(__name__)


# =============================================================================
# Speed and Direction Handlers
# =============================================================================

def handle_set_hspeed(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set horizontal speed for smooth movement.

    Accepts numbers or variable references like other.hspeed.
    """
    speed_value = params.get("hspeed", params.get("value", params.get("speed", "0")))
    speed = parse_float(ctx, speed_value, instance, default=0.0)

    old_speed = instance.hspeed
    instance.hspeed = speed

    if old_speed != speed:
        logger.debug(f"  🏃 {instance.object_name} hspeed: {old_speed} → {speed}")


def handle_set_vspeed(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set vertical speed for smooth movement.

    Accepts numbers or variable references like other.vspeed.
    """
    speed_value = params.get("vspeed", params.get("value", params.get("speed", "0")))
    speed = parse_float(ctx, speed_value, instance, default=0.0)

    old_speed = instance.vspeed
    instance.vspeed = speed

    if old_speed != speed:
        logger.debug(f"  🏃 {instance.object_name} vspeed: {old_speed} → {speed}")


def handle_stop_movement(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Stop all movement by setting speeds to zero."""
    instance.hspeed = 0
    instance.vspeed = 0


def handle_set_direction_speed(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set exact direction and speed for movement.

    Direction angles (GameMaker standard):
    - 0° = right, 90° = up, 180° = left, 270° = down
    """
    direction = parse_float(ctx, params.get("direction", 0), instance, default=0.0)
    speed = parse_float(ctx, params.get("speed", DEFAULT_SPEED), instance, default=DEFAULT_SPEED)

    hspeed, vspeed = direction_to_vector(direction, speed)
    instance.hspeed = hspeed
    instance.vspeed = vspeed

    logger.debug(f"  🧭 {instance.object_name} set direction={direction}° speed={speed}")
    logger.debug(f"      hspeed={instance.hspeed:.2f}, vspeed={instance.vspeed:.2f}")


def handle_start_moving_direction(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Start moving in a specific direction.

    The 'directions' parameter can be:
    - A list of direction names: ['up', 'down', 'left', 'right', ...]
    - A single numeric angle (degrees)
    - A string direction name
    - An expression like 'other.direction'
    """
    # Direction name to angle mapping
    direction_map = {
        'right': 0, 'up-right': 45, 'up': 90, 'up-left': 135,
        'left': 180, 'down-left': 225, 'down': 270, 'down-right': 315,
        'stop': -1  # Special: stop movement
    }

    directions = params.get("directions", 0)
    direction_expr = params.get("direction_expr", "")
    speed = parse_float(ctx, params.get("speed", DEFAULT_SPEED), instance, default=DEFAULT_SPEED)

    # If direction_expr is provided, use it
    if direction_expr and isinstance(direction_expr, str) and direction_expr.strip():
        directions = direction_expr.strip()

    # Handle different parameter types
    if isinstance(directions, list):
        if len(directions) == 0 and not direction_expr:
            instance.hspeed = 0
            instance.vspeed = 0
            logger.debug("   ➡️ Start Moving Direction: stopped (empty directions)")
            return
        chosen = random.choice(directions)
        if isinstance(chosen, str):
            if '.' in chosen:
                direction = parse_float(ctx, chosen, instance, default=0.0)
            else:
                direction = direction_map.get(chosen.lower(), 0)
        else:
            direction = float(chosen)
    elif isinstance(directions, str):
        # Check if it's an expression
        is_expression = any(op in directions for op in ['.', 'choose(', 'random(', '+', '-', '*', '/'])
        if is_expression and directions.lower() not in direction_map:
            direction = ctx._evaluate_expression(directions, instance)
            if not isinstance(direction, (int, float)):
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

    hspeed, vspeed = direction_to_vector(direction, speed)
    instance.hspeed = hspeed
    instance.vspeed = vspeed

    logger.debug(f"   ➡️ Start Moving Direction: {direction}° at speed {speed}")
    logger.debug(f"      hspeed={instance.hspeed:.2f}, vspeed={instance.vspeed:.2f}")


def handle_move_towards_point(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Move towards a specific point at given speed."""
    target_x = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    target_y = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    speed = parse_float(ctx, params.get("speed", DEFAULT_SPEED), instance, default=DEFAULT_SPEED)

    dx = target_x - instance.x
    dy = target_y - instance.y
    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        instance.hspeed = 0
        instance.vspeed = 0
        logger.debug(f"  🎯 {instance.object_name} already at target ({target_x}, {target_y})")
        return

    dir_x = dx / distance
    dir_y = dy / distance
    instance.hspeed = dir_x * speed
    instance.vspeed = dir_y * speed

    angle = math.degrees(math.atan2(-dy, dx))
    logger.debug(f"  🎯 {instance.object_name} moving towards ({target_x}, {target_y}) at speed {speed}")
    logger.debug(f"      angle={angle:.1f}°, hspeed={instance.hspeed:.2f}, vspeed={instance.vspeed:.2f}")


def handle_move_to_contact(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Move in a direction until touching an object.

    Returns True if contact was made, False if max distance reached.
    """
    direction = parse_float(ctx, params.get("direction", 0), instance, default=0.0)
    max_distance = parse_float(ctx, params.get("max_distance", 1000), instance, default=1000.0)
    object_type = params.get("object", "all")

    if not ctx.game_runner:
        logger.debug("⚠️  move_to_contact: No game runner available")
        return False

    angle_rad = math.radians(direction)
    step_x = math.cos(angle_rad)
    step_y = -math.sin(angle_rad)

    start_x, start_y = instance.x, instance.y
    distance_moved = 0

    while distance_moved < max_distance:
        test_x = instance.x + step_x
        test_y = instance.y + step_y

        collision_found = False
        for other in ctx.game_runner.instances:
            if other is instance:
                continue

            if object_type == "all":
                should_check = True
            elif object_type == "solid":
                should_check = getattr(other, 'solid', False)
            else:
                should_check = getattr(other, 'object_name', '') == object_type

            if not should_check:
                continue

            inst_width, inst_height = get_instance_dimensions(instance)
            other_width, other_height = get_instance_dimensions(other)

            if (test_x < other.x + other_width and
                test_x + inst_width > other.x and
                test_y < other.y + other_height and
                test_y + inst_height > other.y):
                collision_found = True
                break

        if collision_found:
            logger.debug(f"  👉 {instance.object_name} moved to contact at ({instance.x:.1f}, {instance.y:.1f})")
            return True

        instance.x = test_x
        instance.y = test_y
        distance_moved += 1

    logger.debug(f"  👉 {instance.object_name} reached max distance {max_distance}px without contact")
    return False


# =============================================================================
# Bounce and Reverse Handlers
# =============================================================================

def handle_bounce(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Bounce off solid objects by reversing velocity."""
    collision_speeds = get_collision_speeds(ctx)
    hspeed = collision_speeds.get('self_hspeed', instance.hspeed)
    vspeed = collision_speeds.get('self_vspeed', instance.vspeed)
    h_blocked = collision_speeds.get('h_blocked', False)
    v_blocked = collision_speeds.get('v_blocked', False)

    if hspeed == 0 and vspeed == 0:
        logger.debug(f"  ⚠️ {instance.object_name} bounce: no velocity to reverse")
        return

    if h_blocked and v_blocked:
        instance.hspeed = -hspeed
        instance.vspeed = -vspeed
        logger.debug(f"  🏓 {instance.object_name} bounced corner")
    elif h_blocked:
        instance.hspeed = -hspeed
        logger.debug(f"  🏓 {instance.object_name} bounced horizontally")
    elif v_blocked:
        instance.vspeed = -vspeed
        logger.debug(f"  🏓 {instance.object_name} bounced vertically")
    else:
        # Fallback: reverse primary direction
        if abs(hspeed) >= abs(vspeed):
            instance.hspeed = -hspeed
        else:
            instance.vspeed = -vspeed


def handle_reverse_horizontal(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Reverse horizontal movement direction."""
    old_hspeed = instance.hspeed
    instance.hspeed = -instance.hspeed
    logger.debug(f"  ↔️ {instance.object_name} reversed hspeed: {old_hspeed} → {instance.hspeed}")


def handle_reverse_vertical(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Reverse vertical movement direction."""
    old_vspeed = instance.vspeed
    instance.vspeed = -instance.vspeed
    logger.debug(f"  ↕️ {instance.object_name} reversed vspeed: {old_vspeed} → {instance.vspeed}")


# =============================================================================
# Physics Handlers
# =============================================================================

def handle_set_gravity(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set gravity for the instance."""
    direction = parse_float(ctx, params.get("direction", 270), instance, default=270.0)
    gravity = parse_float(ctx, params.get("gravity", 0.5), instance, default=0.5)

    instance.gravity = gravity
    instance.gravity_direction = direction
    logger.debug(f"  ⬇️ {instance.object_name} gravity set to {gravity} at {direction}°")


def handle_set_friction(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set friction for the instance."""
    friction = parse_float(ctx, params.get("friction", 0), instance, default=0.0)
    instance.friction = friction
    logger.debug(f"  🛑 {instance.object_name} friction set to {friction}")


# =============================================================================
# Jump/Teleport Handlers
# =============================================================================

def handle_jump_to_position(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Jump to a specific position instantly.

    Supports expressions like other.x, self.hspeed*8, etc.
    """
    x_value = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    y_value = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    relative = parse_bool(params.get("relative", False))
    push_other = parse_bool(params.get("push_other", True))

    old_x, old_y = instance.x, instance.y

    if relative:
        instance.x += x_value
        instance.y += y_value
        logger.debug(f"  📍 {instance.object_name} jumped relatively by ({x_value}, {y_value})")
    else:
        instance.x = x_value
        instance.y = y_value
        logger.debug(f"  📍 {instance.object_name} jumped to ({instance.x}, {instance.y})")

    # Snap to grid during collision events with push_other
    other = get_collision_other(ctx)
    if push_other and other:
        instance.x = snap_to_grid(instance.x, DEFAULT_GRID_SIZE)
        instance.y = snap_to_grid(instance.y, DEFAULT_GRID_SIZE)
        logger.debug(f"  📐 Snapped to grid: ({instance.x}, {instance.y})")

        # Sokoban-style push
        if relative and (x_value != 0 or y_value != 0):
            other.x = old_x
            other.y = old_y
            other.hspeed = 0
            other.vspeed = 0
            logger.debug(f"  🚶 Pusher {other.object_name} moved to ({old_x}, {old_y})")


def handle_jump_to_start(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Jump to the instance's starting position."""
    start_x = getattr(instance, 'xstart', instance.x)
    start_y = getattr(instance, 'ystart', instance.y)
    instance.x = start_x
    instance.y = start_y
    logger.debug(f"  🏠 {instance.object_name} jumped to start position ({start_x}, {start_y})")


def handle_jump_to_random(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Jump to a random position in the room."""
    snap_h = parse_int(ctx, params.get("snap_h", 1), instance, default=1)
    snap_v = parse_int(ctx, params.get("snap_v", 1), instance, default=1)

    room_width, room_height = get_room_dimensions(ctx)
    inst_width, inst_height = get_instance_dimensions(instance)

    max_x = room_width - inst_width
    max_y = room_height - inst_height

    if snap_h > 1:
        num_positions = max(1, max_x // snap_h)
        new_x = random.randint(0, num_positions) * snap_h
    else:
        new_x = random.randint(0, max(0, int(max_x)))

    if snap_v > 1:
        num_positions = max(1, max_y // snap_v)
        new_y = random.randint(0, num_positions) * snap_v
    else:
        new_y = random.randint(0, max(0, int(max_y)))

    instance.x = float(new_x)
    instance.y = float(new_y)
    logger.debug(f"  🎲 {instance.object_name} jumped to random position ({new_x}, {new_y})")


def handle_wrap_around_room(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Wrap instance to opposite side when leaving room boundaries."""
    horizontal = parse_bool(params.get("horizontal", True), default=True)
    vertical = parse_bool(params.get("vertical", True), default=True)

    room_width, room_height = get_room_dimensions(ctx)
    inst_width, inst_height = get_instance_dimensions(instance)

    wrapped = False

    if horizontal:
        if instance.x + inst_width < 0:
            instance.x = room_width
            wrapped = True
        elif instance.x > room_width:
            instance.x = -inst_width
            wrapped = True

    if vertical:
        if instance.y + inst_height < 0:
            instance.y = room_height
            wrapped = True
        elif instance.y > room_height:
            instance.y = -inst_height
            wrapped = True

    if wrapped:
        logger.debug(f"  🔄 {instance.object_name} wrapped to ({instance.x}, {instance.y})")


# =============================================================================
# Grid Movement Handlers
# =============================================================================

def handle_move_grid(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute grid-based movement (instant snap)."""
    direction = params.get("direction", "right")
    grid_size = parse_int(ctx, params.get("grid_size", DEFAULT_GRID_SIZE), instance, default=DEFAULT_GRID_SIZE)

    dx, dy = 0, 0
    if direction == "right":
        dx = grid_size
    elif direction == "left":
        dx = -grid_size
    elif direction == "up":
        dy = -grid_size
    elif direction == "down":
        dy = grid_size

    instance.intended_x = instance.x + dx
    instance.intended_y = instance.y + dy


def handle_snap_to_grid(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Snap instance to nearest grid position."""
    grid_size = parse_int(ctx, params.get("grid_size", DEFAULT_GRID_SIZE), instance, default=DEFAULT_GRID_SIZE)
    instance.x = snap_to_grid(instance.x, grid_size)
    instance.y = snap_to_grid(instance.y, grid_size)


def handle_if_on_grid(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if instance is on grid - returns True/False for conditional flow."""
    grid_size = parse_int(ctx, params.get("grid_size", DEFAULT_GRID_SIZE), instance, default=DEFAULT_GRID_SIZE)

    if is_on_grid(instance.x, instance.y, grid_size):
        instance.x = snap_to_grid(instance.x, grid_size)
        instance.y = snap_to_grid(instance.y, grid_size)
        return True
    return False


def handle_stop_if_no_keys(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Stop movement when on grid (for precise grid-based movement)."""
    grid_size = parse_int(ctx, params.get("grid_size", DEFAULT_GRID_SIZE), instance, default=DEFAULT_GRID_SIZE)

    instance.hspeed = 0
    instance.vspeed = 0
    instance.x = snap_to_grid(instance.x, grid_size)
    instance.y = snap_to_grid(instance.y, grid_size)


def handle_check_keys_and_move(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Check if movement keys are held and restart movement."""
    grid_size = parse_int(ctx, params.get("grid_size", DEFAULT_GRID_SIZE), instance, default=DEFAULT_GRID_SIZE)
    speed = parse_float(ctx, params.get("speed", DEFAULT_SPEED), instance, default=DEFAULT_SPEED)

    keys_pressed = getattr(instance, 'keys_pressed', set())

    if not is_on_grid(instance.x, instance.y, grid_size, tolerance=0.0):
        return

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


# =============================================================================
# Handler Registry
# =============================================================================

MOVEMENT_HANDLERS: Dict[str, Any] = {
    # Speed and direction
    "set_hspeed": handle_set_hspeed,
    "set_vspeed": handle_set_vspeed,
    "stop_movement": handle_stop_movement,
    "set_direction_speed": handle_set_direction_speed,
    "start_moving_direction": handle_start_moving_direction,
    "move_towards_point": handle_move_towards_point,
    "move_to_contact": handle_move_to_contact,

    # Bounce and reverse
    "bounce": handle_bounce,
    "reverse_horizontal": handle_reverse_horizontal,
    "reverse_vertical": handle_reverse_vertical,

    # Physics
    "set_gravity": handle_set_gravity,
    "set_friction": handle_set_friction,

    # Jump/teleport
    "jump_to_position": handle_jump_to_position,
    "jump_to_start": handle_jump_to_start,
    "jump_to_random": handle_jump_to_random,
    "wrap_around_room": handle_wrap_around_room,

    # Grid movement
    "move_grid": handle_move_grid,
    "snap_to_grid": handle_snap_to_grid,
    "if_on_grid": handle_if_on_grid,
    "stop_if_no_keys": handle_stop_if_no_keys,
    "check_keys_and_move": handle_check_keys_and_move,
}
