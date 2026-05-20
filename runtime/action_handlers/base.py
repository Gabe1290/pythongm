#!/usr/bin/env python3
"""
Base utilities for action handlers.

This module provides common utilities, type definitions, and helper functions
used across all action handler modules.
"""

from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING
import math

from core.logger import get_logger
from utils.color import to_rgb255

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

# Type aliases for clarity
Parameters = Dict[str, Any]
Instance = Any  # Game instance object
HandlerContext = 'ActionExecutor'  # The executor provides context

# Common constants (re-exported from runtime.constants)
DEFAULT_SPEED = 4.0
MAX_COLOR_VALUE = 255
FULL_CIRCLE_DEGREES = 360




def parse_float(ctx: HandlerContext, value: Any, instance: Instance = None,
                default: float = 0.0) -> float:
    """Parse a value to float, with fallback to default.

    Args:
        ctx: The ActionExecutor instance
        value: Value to parse (can be string expression, number, etc.)
        instance: Game instance for variable resolution
        default: Fallback value if parsing fails

    Returns:
        Float value
    """
    if value is None:
        return default

    parsed = ctx._parse_value(str(value), instance) if isinstance(value, str) else value

    try:
        return float(parsed) if parsed is not None else default
    except (ValueError, TypeError):
        return default


def parse_int(ctx: HandlerContext, value: Any, instance: Instance = None,
              default: int = 0) -> int:
    """Parse a value to int, with fallback to default.

    Args:
        ctx: The ActionExecutor instance
        value: Value to parse
        instance: Game instance for variable resolution
        default: Fallback value if parsing fails

    Returns:
        Integer value
    """
    if value is None:
        return default

    parsed = ctx._parse_value(str(value), instance) if isinstance(value, str) else value

    try:
        return int(parsed) if parsed is not None else default
    except (ValueError, TypeError):
        return default


def parse_bool(value: Any, default: bool = False) -> bool:
    """Parse a value to boolean.

    Args:
        value: Value to parse
        default: Fallback value

    Returns:
        Boolean value
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)


def parse_color(color_value: Any, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
    """Parse a color value to an ``(r, g, b)`` 0-255 tuple.

    Delegates to :func:`utils.color.to_rgb255`. Kept as the name action
    handlers import so the many existing call sites don't need to change;
    see ``utils/color.py`` for the Kivy-flavoured counterpart.
    """
    return to_rgb255(color_value, default)






def direction_to_vector(direction_degrees: float, speed: float = 1.0) -> Tuple[float, float]:
    """Convert direction angle to velocity vector.

    GameMaker convention:
    - 0° = right
    - 90° = up
    - 180° = left
    - 270° = down

    Args:
        direction_degrees: Angle in degrees
        speed: Speed magnitude

    Returns:
        Tuple of (hspeed, vspeed)
    """
    angle_rad = math.radians(direction_degrees)
    hspeed = math.cos(angle_rad) * speed
    vspeed = -math.sin(angle_rad) * speed  # Negative because screen Y increases downward
    return (hspeed, vspeed)


def vector_to_direction(hspeed: float, vspeed: float) -> float:
    """Convert velocity vector to direction angle.

    Args:
        hspeed: Horizontal speed
        vspeed: Vertical speed

    Returns:
        Direction in degrees (0-360)
    """
    if hspeed == 0 and vspeed == 0:
        return 0
    # Negate vspeed because screen Y increases downward
    return math.degrees(math.atan2(-vspeed, hspeed)) % FULL_CIRCLE_DEGREES






def snap_to_grid(value: float, grid_size: int) -> float:
    """Snap a value to the nearest grid position.

    Args:
        value: The value to snap
        grid_size: Grid cell size

    Returns:
        Snapped value
    """
    return round(value / grid_size) * grid_size




def queue_draw_command(instance: Instance, command: Dict[str, Any]) -> None:
    """Queue a drawing command for the instance's draw event.

    Args:
        instance: The game instance
        command: Drawing command dictionary
    """
    if not hasattr(instance, '_draw_queue'):
        instance._draw_queue = []
    instance._draw_queue.append(command)




def get_collision_other(ctx: HandlerContext) -> Optional[Instance]:
    """Get the 'other' instance from a collision event.

    Args:
        ctx: The ActionExecutor instance

    Returns:
        The other instance, or None if not in a collision event
    """
    return getattr(ctx, '_collision_other', None)
