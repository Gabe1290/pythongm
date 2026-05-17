#!/usr/bin/env python3
"""
Base utilities for action handlers.

This module provides common utilities, type definitions, and helper functions
used across all action handler modules.
"""

from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING
import math

from core.logger import get_logger

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
    """Parse a color value to RGB tuple.

    Supports:
    - Hex strings: "#FF0000", "#f00"
    - RGB tuples: (255, 0, 0)
    - Integer values (GameMaker BGR format)

    Args:
        color_value: The color to parse
        default: Fallback RGB tuple

    Returns:
        RGB tuple (r, g, b)
    """
    if color_value is None:
        return default

    if isinstance(color_value, tuple) and len(color_value) >= 3:
        return (int(color_value[0]), int(color_value[1]), int(color_value[2]))

    if isinstance(color_value, str):
        color_str = color_value.strip()
        if color_str.startswith('#'):
            try:
                hex_color = color_str.lstrip('#')
                if len(hex_color) == 3:
                    # Short form: #RGB -> #RRGGBB
                    hex_color = ''.join(c * 2 for c in hex_color)
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
            except (ValueError, IndexError):
                return default

    if isinstance(color_value, int):
        # GameMaker uses BGR format
        b = (color_value >> 16) & 0xFF
        g = (color_value >> 8) & 0xFF
        r = color_value & 0xFF
        return (r, g, b)

    return default






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
