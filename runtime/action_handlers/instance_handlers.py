#!/usr/bin/env python3
"""
Instance Action Handlers

Handles instance creation, destruction, and manipulation.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_bool,
)

logger = get_logger(__name__)



def handle_create_moving(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Create an instance with initial velocity."""
    object_name = params.get("object", "")
    x = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    y = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    speed = parse_float(ctx, params.get("speed", 4), instance, default=4.0)
    direction = parse_float(ctx, params.get("direction", 0), instance, default=0.0)
    relative = parse_bool(params.get("relative", False))

    if not object_name:
        logger.debug("⚠️ create_moving: No object specified")
        return

    if relative:
        x += instance.x
        y += instance.y

    if not hasattr(instance, 'pending_creates'):
        instance.pending_creates = []

    instance.pending_creates.append({
        'object': object_name,
        'x': x,
        'y': y,
        'speed': speed,
        'direction': direction
    })

    logger.debug(f"  ➕ Queue create moving '{object_name}' at ({x}, {y})")


def handle_create_random(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Create a random instance from a list of objects."""
    import random

    objects = params.get("objects", [])
    x = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    y = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    relative = parse_bool(params.get("relative", False))

    if not objects:
        logger.debug("⚠️ create_random: No objects specified")
        return

    object_name = random.choice(objects)

    if relative:
        x += instance.x
        y += instance.y

    if not hasattr(instance, 'pending_creates'):
        instance.pending_creates = []

    instance.pending_creates.append({
        'object': object_name,
        'x': x,
        'y': y
    })

    logger.debug(f"  🎲 Queue create random '{object_name}' at ({x}, {y})")







def handle_set_color_blend(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set color blending for the instance."""
    from runtime.action_handlers.base import parse_color

    color = parse_color(params.get("color", "#FFFFFF"))
    alpha = parse_float(ctx, params.get("alpha", 1.0), instance, default=1.0)

    instance.image_blend = color
    instance.image_alpha = alpha

    logger.debug(f"  🎨 Set blend: color={color}, alpha={alpha}")


def handle_set_visible(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set instance visibility."""
    visible = parse_bool(params.get("visible", True))
    instance.visible = visible
    logger.debug(f"  👁️ Set visible = {visible}")


def handle_set_solid(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set instance solid property."""
    solid = parse_bool(params.get("solid", True))
    instance.solid = solid
    logger.debug(f"  🧱 Set solid = {solid}")


def handle_set_depth(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set instance drawing depth."""
    depth = parse_float(ctx, params.get("depth", 0), instance, default=0.0)
    relative = parse_bool(params.get("relative", False))

    if relative:
        instance.depth = getattr(instance, 'depth', 0) + depth
    else:
        instance.depth = depth

    logger.debug(f"  📊 Set depth = {instance.depth}")


def handle_set_mask(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the collision mask sprite."""
    sprite = params.get("sprite", "")
    instance.mask_index = sprite if sprite else None
    logger.debug(f"  🎭 Set mask = '{sprite}'")


def handle_set_persistent(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set instance persistence across rooms."""
    persistent = parse_bool(params.get("persistent", True))
    instance.persistent = persistent
    logger.debug(f"  💾 Set persistent = {persistent}")








# =============================================================================
# Handler Registry
# =============================================================================

INSTANCE_HANDLERS: Dict[str, Any] = {
    "create_moving": handle_create_moving,
    "create_random": handle_create_random,
    "set_color_blend": handle_set_color_blend,
    "set_visible": handle_set_visible,
    "set_solid": handle_set_solid,
    "set_depth": handle_set_depth,
    "set_mask": handle_set_mask,
    "set_persistent": handle_set_persistent,
    # Animation
    # Alternate names for compatibility
}
