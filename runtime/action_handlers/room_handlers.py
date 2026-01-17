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


def handle_set_room_speed(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the room speed (FPS)."""
    speed = parse_int(ctx, params.get("speed", 30), instance, default=30)

    if ctx.game_runner:
        ctx.game_runner.room_speed = speed

    logger.debug(f"  ⏱️ Set room speed: {speed} FPS")


def handle_set_room_persistent(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set room persistence."""
    persistent = parse_bool(params.get("persistent", True))

    if ctx.game_runner and ctx.game_runner.current_room:
        ctx.game_runner.current_room.persistent = persistent

    logger.debug(f"  💾 Set room persistent: {persistent}")


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


def handle_set_background(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set room background (alias for set_room_background)."""
    handle_set_room_background(ctx, instance, params)


def handle_set_background_color(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set room background color (alias for set_room_background_color)."""
    handle_set_room_background_color(ctx, instance, params)


def handle_enable_views(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Enable or disable views in the room."""
    enable = parse_bool(params.get("enable", True))

    if ctx.game_runner and ctx.game_runner.current_room:
        ctx.game_runner.current_room.views_enabled = enable

    logger.debug(f"  👁️ Views enabled: {enable}")


def handle_set_view(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set view properties."""
    view_index = parse_int(ctx, params.get("view", 0), instance, default=0)
    visible = parse_bool(params.get("visible", True))
    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)
    width = parse_int(ctx, params.get("width", 640), instance, default=640)
    height = parse_int(ctx, params.get("height", 480), instance, default=480)
    port_x = parse_int(ctx, params.get("port_x", 0), instance, default=0)
    port_y = parse_int(ctx, params.get("port_y", 0), instance, default=0)
    port_width = parse_int(ctx, params.get("port_width", 640), instance, default=640)
    port_height = parse_int(ctx, params.get("port_height", 480), instance, default=480)
    object_following = params.get("object", "")
    hborder = parse_int(ctx, params.get("hborder", 32), instance, default=32)
    vborder = parse_int(ctx, params.get("vborder", 32), instance, default=32)

    if ctx.game_runner and ctx.game_runner.current_room:
        room = ctx.game_runner.current_room
        if not hasattr(room, 'views'):
            room.views = {}
        room.views[view_index] = {
            'visible': visible,
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'port_x': port_x,
            'port_y': port_y,
            'port_width': port_width,
            'port_height': port_height,
            'object_following': object_following,
            'hborder': hborder,
            'vborder': vborder
        }

    logger.debug(f"  👁️ Set view[{view_index}]: {width}x{height} at ({x}, {y})")


def handle_set_room_caption(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the room/window caption."""
    caption = params.get("caption", "")

    if ctx.game_runner:
        ctx.game_runner.room_caption = caption

    logger.debug(f"  📝 Set room caption: '{caption}'")


def handle_set_window_caption(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the window caption (alias for set_room_caption)."""
    handle_set_room_caption(ctx, instance, params)


# =============================================================================
# Handler Registry
# =============================================================================

ROOM_HANDLERS: Dict[str, Any] = {
    "set_room_background": handle_set_room_background,
    "set_room_background_color": handle_set_room_background_color,
    "set_room_size": handle_set_room_size,
    "set_room_speed": handle_set_room_speed,
    "set_room_persistent": handle_set_room_persistent,
    "if_room_first": handle_if_room_first,
    "if_room_last": handle_if_room_last,
    # Aliases and additional handlers
    "set_background": handle_set_background,
    "set_background_color": handle_set_background_color,
    "enable_views": handle_enable_views,
    "set_view": handle_set_view,
    "set_room_caption": handle_set_room_caption,
    "set_window_caption": handle_set_window_caption,
}
