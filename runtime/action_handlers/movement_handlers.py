#!/usr/bin/env python3
"""
Movement Action Handlers

Handles all movement-related actions: speed setting, direction, jumping,
wrapping, bouncing, etc.
"""

from typing import Dict, Any
import math

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_int, direction_to_vector, vector_to_direction,
    snap_to_grid, DEFAULT_GRID_SIZE,
)

logger = get_logger(__name__)


# =============================================================================
# Speed and Direction Handlers
# =============================================================================





def handle_move_free(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Move at an exact direction and speed.

    Delegates to the executor's set_direction_speed implementation — same
    semantics, kept as a separate registered handler so action_type
    registration is honoured directly.
    """
    ctx.execute_set_direction_speed_action(instance, params)


def handle_set_speed(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the instance's speed magnitude, preserving its current direction.

    Reads the current direction from the existing (hspeed, vspeed) vector and
    rebuilds the velocity at the new magnitude. If currently stationary,
    direction defaults to 0° (right) so picking a non-zero speed actually
    starts movement.
    """
    speed = parse_float(ctx, params.get("speed", params.get("value", 0)), instance, default=0.0)
    current_direction = vector_to_direction(instance.hspeed, instance.vspeed)
    hspeed, vspeed = direction_to_vector(current_direction, speed)
    instance.hspeed = hspeed
    instance.vspeed = vspeed
    logger.debug(f"  🏃 {instance.object_name} speed={speed} (dir preserved at {current_direction:.1f}°)")


def handle_set_direction(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the instance's direction angle, preserving its current speed magnitude.

    Reads the current speed magnitude from the existing (hspeed, vspeed) vector
    and rebuilds the velocity at the new direction. If currently stationary,
    setting a direction does not start movement (matches GameMaker semantics).
    """
    direction = parse_float(ctx, params.get("direction", params.get("value", 0)), instance, default=0.0)
    current_speed = math.sqrt(instance.hspeed ** 2 + instance.vspeed ** 2)
    hspeed, vspeed = direction_to_vector(direction, current_speed)
    instance.hspeed = hspeed
    instance.vspeed = vspeed
    logger.debug(f"  🧭 {instance.object_name} direction={direction}° (speed preserved at {current_speed:.2f})")





# =============================================================================
# Bounce and Reverse Handlers
# =============================================================================




# =============================================================================
# Physics Handlers
# =============================================================================



# =============================================================================
# Jump/Teleport Handlers
# =============================================================================





# =============================================================================
# Grid Movement Handlers
# =============================================================================






def handle_snap_object_to_grid(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Snap all instances of a named object to the nearest grid position."""
    object_name = params.get("object", "")
    grid_size = parse_int(ctx, params.get("grid_size", DEFAULT_GRID_SIZE), instance, default=DEFAULT_GRID_SIZE)

    if not ctx.game_runner or not ctx.game_runner.current_room:
        return

    for inst in ctx.game_runner.current_room.instances:
        if inst.object_name == object_name:
            inst.x = snap_to_grid(inst.x, grid_size)
            inst.y = snap_to_grid(inst.y, grid_size)
            logger.debug(f"  📐 Snapped {object_name} to grid ({inst.x}, {inst.y})")


def handle_stop_object_movement(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Stop all movement for all instances of a named object."""
    object_name = params.get("object", "")

    if not ctx.game_runner or not ctx.game_runner.current_room:
        return

    for inst in ctx.game_runner.current_room.instances:
        if inst.object_name == object_name:
            inst.hspeed = 0
            inst.vspeed = 0
            logger.debug(f"  🛑 Stopped movement for {object_name}")


# =============================================================================
# Handler Registry
# =============================================================================

MOVEMENT_HANDLERS: Dict[str, Any] = {
    # Speed and direction
    "move_free": handle_move_free,
    "set_speed": handle_set_speed,
    "set_direction": handle_set_direction,

    # Bounce and reverse

    # Physics

    # Jump/teleport

    # Grid movement

    # Cross-object grid movement
    "snap_object_to_grid": handle_snap_object_to_grid,
    "stop_object_movement": handle_stop_object_movement,
}
