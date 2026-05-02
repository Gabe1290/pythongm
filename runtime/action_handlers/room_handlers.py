#!/usr/bin/env python3
"""
Room Action Handlers

Handles room properties and transitions.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_int, parse_bool, parse_color,
)

logger = get_logger(__name__)


def handle_set_room_background(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the room background."""
    background = params.get("background", "")
    visible = parse_bool(params.get("visible", True))
    foreground = parse_bool(params.get("foreground", False))
    tiled_h = parse_bool(params.get("tiled_h", False))
    tiled_v = parse_bool(params.get("tiled_v", False))
    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)

    if ctx.game_runner and ctx.game_runner.current_room:
        room = ctx.game_runner.current_room
        room.background = {
            'name': background,
            'visible': visible,
            'foreground': foreground,
            'tiled_h': tiled_h,
            'tiled_v': tiled_v,
            'x': x,
            'y': y
        }

    logger.debug(f"  🏞️ Set room background: '{background}'")


def handle_set_room_background_color(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the room background color."""
    color = parse_color(params.get("color", "#C0C0C0"))

    if ctx.game_runner and ctx.game_runner.current_room:
        ctx.game_runner.current_room.background_color = color

    logger.debug(f"  🎨 Set room background color: {color}")


def handle_set_room_size(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the room dimensions."""
    width = parse_int(ctx, params.get("width", 640), instance, default=640)
    height = parse_int(ctx, params.get("height", 480), instance, default=480)

    if ctx.game_runner and ctx.game_runner.current_room:
        ctx.game_runner.current_room.width = width
        ctx.game_runner.current_room.height = height

    logger.debug(f"  📐 Set room size: {width}x{height}")




def handle_if_room_first(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if current room is the first room."""
    not_flag = parse_bool(params.get("not_flag", False))

    result = False
    if ctx.game_runner:
        room_list = ctx.game_runner.get_room_list()
        current_room = ctx.game_runner.current_room
        if current_room and room_list:
            try:
                result = room_list.index(current_room.name) == 0
            except ValueError:
                pass

    if not_flag:
        result = not result

    logger.debug(f"  ❓ if_room_first: {result}")
    return result


def handle_if_room_last(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if current room is the last room."""
    not_flag = parse_bool(params.get("not_flag", False))

    result = False
    if ctx.game_runner:
        room_list = ctx.game_runner.get_room_list()
        current_room = ctx.game_runner.current_room
        if current_room and room_list:
            try:
                result = room_list.index(current_room.name) == len(room_list) - 1
            except ValueError:
                pass

    if not_flag:
        result = not result

    logger.debug(f"  ❓ if_room_last: {result}")
    return result








# =============================================================================
# Handler Registry
# =============================================================================

ROOM_HANDLERS: Dict[str, Any] = {
    "set_room_background": handle_set_room_background,
    "set_room_background_color": handle_set_room_background_color,
    "set_room_size": handle_set_room_size,
    "if_room_first": handle_if_room_first,
    "if_room_last": handle_if_room_last,
    # Aliases and additional handlers
}
