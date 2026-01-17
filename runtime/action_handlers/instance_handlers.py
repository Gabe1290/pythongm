#!/usr/bin/env python3
"""
Instance Action Handlers

Handles instance creation, destruction, and manipulation.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_int, parse_bool,
)

logger = get_logger(__name__)


def handle_create_instance(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Create a new instance of an object."""
    object_name = params.get("object", "")
    x = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    y = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    relative = parse_bool(params.get("relative", False))

    if not object_name:
        logger.debug("⚠️ create_instance: No object specified")
        return

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

    logger.debug(f"  ➕ Queue create '{object_name}' at ({x}, {y})")


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


def handle_destroy_instance(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Destroy the current instance."""
    logger.debug(f"  💥 Destroy requested for {instance.object_name}")
    instance.destroy_flag = True


def handle_destroy_at_position(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Destroy all instances at a position."""
    x = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    y = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    object_type = params.get("object", "all")
    relative = parse_bool(params.get("relative", False))

    if relative:
        x += instance.x
        y += instance.y

    if not hasattr(instance, 'pending_destroys_at'):
        instance.pending_destroys_at = []

    instance.pending_destroys_at.append({
        'x': x,
        'y': y,
        'object': object_type
    })

    logger.debug(f"  💥 Queue destroy at ({x}, {y}) for '{object_type}'")


def handle_change_instance(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Change this instance into a different object type."""
    object_name = params.get("object", "")
    perform_events = parse_bool(params.get("perform_events", True))

    if not object_name:
        logger.debug("⚠️ change_instance: No object specified")
        return

    instance.change_to_object = object_name
    instance.change_perform_events = perform_events

    logger.debug(f"  🔄 Queue change to '{object_name}'")


def handle_set_sprite(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Change the instance's sprite."""
    sprite_name = params.get("sprite", "")
    subimage = parse_int(ctx, params.get("subimage", 0), instance, default=0)
    speed = parse_float(ctx, params.get("speed", 1), instance, default=1.0)

    if not sprite_name:
        logger.debug("⚠️ set_sprite: No sprite specified")
        return

    instance.sprite_name = sprite_name
    instance.image_index = subimage
    instance.image_speed = speed

    logger.debug(f"  🖼️ Set sprite to '{sprite_name}' (subimage={subimage}, speed={speed})")


def handle_transform_sprite(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Transform the instance's sprite (scale, rotate, etc.)."""
    xscale = parse_float(ctx, params.get("xscale", 1), instance, default=1.0)
    yscale = parse_float(ctx, params.get("yscale", 1), instance, default=1.0)
    angle = parse_float(ctx, params.get("angle", 0), instance, default=0.0)
    mirror = parse_bool(params.get("mirror", False))

    instance.image_xscale = xscale
    instance.image_yscale = yscale
    instance.image_angle = angle

    if mirror:
        instance.image_xscale = -abs(instance.image_xscale)

    logger.debug(f"  🔄 Transform: scale=({xscale}, {yscale}), angle={angle}")


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


def handle_set_image_index(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the current animation frame."""
    index = parse_float(ctx, params.get("image_index", params.get("index", 0)), instance, default=0.0)
    instance.image_index = index
    logger.debug(f"  🖼️ Set image_index = {index}")


def handle_set_image_speed(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set animation playback speed."""
    speed = parse_float(ctx, params.get("image_speed", params.get("speed", 1)), instance, default=1.0)
    instance.image_speed = speed
    logger.debug(f"  ⏩ Set image_speed = {speed}")


def handle_start_animation(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Start/resume animation playback."""
    instance.image_speed = 1.0
    logger.debug("  ▶️ Animation started")


def handle_stop_animation(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Stop animation playback."""
    instance.image_speed = 0
    logger.debug("  ⏹️ Animation stopped")


def handle_create_moving_instance(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Create an instance with initial velocity (alternate name)."""
    import math

    object_name = params.get("object", "")
    x = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    y = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    speed = parse_float(ctx, params.get("speed", 4), instance, default=4.0)
    direction = parse_float(ctx, params.get("direction", 0), instance, default=0.0)
    relative = parse_bool(params.get("relative", False))

    if not object_name:
        logger.debug("⚠️ create_moving_instance: No object specified")
        return

    if relative:
        x += instance.x
        y += instance.y

    # Calculate velocity components
    angle_rad = math.radians(direction)
    hspeed = math.cos(angle_rad) * speed
    vspeed = -math.sin(angle_rad) * speed

    if not hasattr(instance, 'pending_creates'):
        instance.pending_creates = []

    instance.pending_creates.append({
        'object': object_name,
        'x': x,
        'y': y,
        'hspeed': hspeed,
        'vspeed': vspeed
    })

    logger.debug(f"  ➕ Queue create moving '{object_name}' at ({x}, {y}) dir={direction}")


def handle_create_random_instance(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Create a random instance from a list (alternate name)."""
    import random

    objects = params.get("objects", params.get("object_list", []))
    x = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    y = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    relative = parse_bool(params.get("relative", False))

    if not objects:
        logger.debug("⚠️ create_random_instance: No objects specified")
        return

    # Handle string list
    if isinstance(objects, str):
        objects = [o.strip() for o in objects.split(',') if o.strip()]

    if not objects:
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


# =============================================================================
# Handler Registry
# =============================================================================

INSTANCE_HANDLERS: Dict[str, Any] = {
    "create_instance": handle_create_instance,
    "create_moving": handle_create_moving,
    "create_random": handle_create_random,
    "destroy_instance": handle_destroy_instance,
    "destroy_at_position": handle_destroy_at_position,
    "change_instance": handle_change_instance,
    "set_sprite": handle_set_sprite,
    "transform_sprite": handle_transform_sprite,
    "set_color_blend": handle_set_color_blend,
    "set_visible": handle_set_visible,
    "set_solid": handle_set_solid,
    "set_depth": handle_set_depth,
    "set_mask": handle_set_mask,
    "set_persistent": handle_set_persistent,
    # Animation
    "set_image_index": handle_set_image_index,
    "set_image_speed": handle_set_image_speed,
    "start_animation": handle_start_animation,
    "stop_animation": handle_stop_animation,
    # Alternate names for compatibility
    "create_moving_instance": handle_create_moving_instance,
    "create_random_instance": handle_create_random_instance,
}
