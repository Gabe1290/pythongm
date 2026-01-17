#!/usr/bin/env python3
"""
Draw Action Handlers

Handles all drawing operations: sprites, shapes, text, colors.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_int, parse_bool, parse_color,
    queue_draw_command,
)

logger = get_logger(__name__)


def handle_draw_self(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw the instance's sprite at its position."""
    queue_draw_command(instance, {'type': 'self'})


def handle_draw_sprite(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw a sprite at a position."""
    sprite = params.get("sprite", "")
    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)
    subimage = parse_int(ctx, params.get("subimage", 0), instance, default=0)

    queue_draw_command(instance, {
        'type': 'sprite',
        'sprite': sprite,
        'x': x,
        'y': y,
        'subimage': subimage
    })

    logger.debug(f"  🖼️ Queue draw sprite '{sprite}' at ({x}, {y})")


def handle_draw_background(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw a background image."""
    background = params.get("background", "")
    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)
    tiled = parse_bool(params.get("tiled", False))

    queue_draw_command(instance, {
        'type': 'background',
        'background': background,
        'x': x,
        'y': y,
        'tiled': tiled
    })

    logger.debug(f"  🏞️ Queue draw background '{background}' at ({x}, {y})")


def handle_draw_text(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw text at a position."""
    text = str(params.get("text", ""))
    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)

    color = getattr(instance, 'draw_color', (0, 0, 0))

    queue_draw_command(instance, {
        'type': 'text',
        'text': text,
        'x': x,
        'y': y,
        'color': color
    })

    logger.debug(f"  📝 Queue draw text '{text[:20]}...' at ({x}, {y})")


def handle_draw_text_scaled(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw scaled text."""
    text = str(params.get("text", ""))
    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)
    xscale = parse_float(ctx, params.get("xscale", 1), instance, default=1.0)
    yscale = parse_float(ctx, params.get("yscale", 1), instance, default=1.0)

    color = getattr(instance, 'draw_color', (0, 0, 0))

    queue_draw_command(instance, {
        'type': 'text_scaled',
        'text': text,
        'x': x,
        'y': y,
        'xscale': xscale,
        'yscale': yscale,
        'color': color
    })


def handle_draw_rectangle(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw a rectangle."""
    x1 = parse_int(ctx, params.get("x1", 0), instance, default=0)
    y1 = parse_int(ctx, params.get("y1", 0), instance, default=0)
    x2 = parse_int(ctx, params.get("x2", 100), instance, default=100)
    y2 = parse_int(ctx, params.get("y2", 100), instance, default=100)
    filled = parse_bool(params.get("filled", True))

    color = getattr(instance, 'draw_color', (0, 0, 0))

    queue_draw_command(instance, {
        'type': 'rectangle',
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'filled': filled,
        'color': color
    })

    logger.debug(f"  📦 Queue draw rectangle ({x1}, {y1}) to ({x2}, {y2})")


def handle_draw_gradient_hor(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw a horizontal gradient rectangle."""
    x1 = parse_int(ctx, params.get("x1", 0), instance, default=0)
    y1 = parse_int(ctx, params.get("y1", 0), instance, default=0)
    x2 = parse_int(ctx, params.get("x2", 100), instance, default=100)
    y2 = parse_int(ctx, params.get("y2", 100), instance, default=100)
    color1 = parse_color(params.get("color1", "#000000"))
    color2 = parse_color(params.get("color2", "#FFFFFF"))

    queue_draw_command(instance, {
        'type': 'gradient_hor',
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'color1': color1,
        'color2': color2
    })


def handle_draw_gradient_vert(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw a vertical gradient rectangle."""
    x1 = parse_int(ctx, params.get("x1", 0), instance, default=0)
    y1 = parse_int(ctx, params.get("y1", 0), instance, default=0)
    x2 = parse_int(ctx, params.get("x2", 100), instance, default=100)
    y2 = parse_int(ctx, params.get("y2", 100), instance, default=100)
    color1 = parse_color(params.get("color1", "#000000"))
    color2 = parse_color(params.get("color2", "#FFFFFF"))

    queue_draw_command(instance, {
        'type': 'gradient_vert',
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'color1': color1,
        'color2': color2
    })


def handle_draw_ellipse(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw an ellipse."""
    x1 = parse_int(ctx, params.get("x1", 0), instance, default=0)
    y1 = parse_int(ctx, params.get("y1", 0), instance, default=0)
    x2 = parse_int(ctx, params.get("x2", 100), instance, default=100)
    y2 = parse_int(ctx, params.get("y2", 100), instance, default=100)
    filled = parse_bool(params.get("filled", True))

    color = getattr(instance, 'draw_color', (0, 0, 0))

    queue_draw_command(instance, {
        'type': 'ellipse',
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'filled': filled,
        'color': color
    })


def handle_draw_circle(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw a circle."""
    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)
    radius = parse_int(ctx, params.get("radius", 50), instance, default=50)
    filled = parse_bool(params.get("filled", True))

    color = getattr(instance, 'draw_color', (0, 0, 0))

    queue_draw_command(instance, {
        'type': 'circle',
        'x': x,
        'y': y,
        'radius': radius,
        'filled': filled,
        'color': color
    })


def handle_draw_line(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw a line."""
    x1 = parse_int(ctx, params.get("x1", 0), instance, default=0)
    y1 = parse_int(ctx, params.get("y1", 0), instance, default=0)
    x2 = parse_int(ctx, params.get("x2", 100), instance, default=100)
    y2 = parse_int(ctx, params.get("y2", 100), instance, default=100)

    color = getattr(instance, 'draw_color', (0, 0, 0))

    queue_draw_command(instance, {
        'type': 'line',
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'color': color
    })


def handle_draw_arrow(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw an arrow."""
    x1 = parse_int(ctx, params.get("x1", 0), instance, default=0)
    y1 = parse_int(ctx, params.get("y1", 0), instance, default=0)
    x2 = parse_int(ctx, params.get("x2", 100), instance, default=100)
    y2 = parse_int(ctx, params.get("y2", 100), instance, default=100)
    tip_size = parse_int(ctx, params.get("tip_size", 10), instance, default=10)

    color = getattr(instance, 'draw_color', (0, 0, 0))

    queue_draw_command(instance, {
        'type': 'arrow',
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'tip_size': tip_size,
        'color': color
    })


def handle_set_color(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the blend color and alpha for the sprite.

    Parameters:
        color: Blend color (hex string like "#RRGGBB")
        alpha: Transparency (0.0 = invisible, 1.0 = fully opaque)
    """
    color_param = params.get("color", "#FFFFFF")
    alpha_param = params.get("alpha", 1.0)

    # Parse color value
    color = ctx._parse_value(str(color_param), instance)
    alpha = ctx._parse_value(str(alpha_param), instance)

    # Parse color if it's a hex string
    if isinstance(color, str) and color.startswith('#'):
        try:
            hex_color = color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            instance.image_blend = (r, g, b)
        except (ValueError, IndexError):
            instance.image_blend = (255, 255, 255)
    else:
        instance.image_blend = (255, 255, 255)

    # Parse and clamp alpha
    try:
        alpha = float(alpha) if alpha is not None else 1.0
        alpha = max(0.0, min(1.0, alpha))
    except (ValueError, TypeError):
        alpha = 1.0

    instance.image_alpha = alpha

    # Also set draw_color for drawing primitives
    instance.draw_color = instance.image_blend

    logger.debug(f"  🎨 Set color to {instance.image_blend}, alpha={alpha}")


def handle_set_font(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the font and alignment for text drawing.

    Parameters:
        font: Font name/asset to use
        halign: Horizontal alignment (left, center, right)
        valign: Vertical alignment (top, middle, bottom)
    """
    font_name = ctx._parse_value(params.get("font", ""), instance)
    halign = ctx._parse_value(params.get("halign", "left"), instance)
    valign = ctx._parse_value(params.get("valign", "top"), instance)

    # Store font settings on the instance
    instance.draw_font = font_name if font_name else None
    instance.draw_halign = halign if halign in ('left', 'center', 'right') else 'left'
    instance.draw_valign = valign if valign in ('top', 'middle', 'bottom') else 'top'

    logger.debug(f"  🔤 Set font: '{font_name}', halign={halign}, valign={valign}")


def handle_set_alpha(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the drawing alpha (transparency)."""
    alpha = parse_float(ctx, params.get("alpha", 1.0), instance, default=1.0)
    instance.draw_alpha = max(0.0, min(1.0, alpha))
    logger.debug(f"  👻 Set draw alpha to {instance.draw_alpha}")


def handle_set_fullscreen(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Toggle fullscreen mode."""
    fullscreen = parse_bool(params.get("fullscreen", True))

    if ctx.game_runner:
        ctx.game_runner.fullscreen = fullscreen
    logger.debug(f"  🖥️ Set fullscreen = {fullscreen}")


def handle_draw_scaled_text(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw scaled text (alias for draw_text_scaled)."""
    handle_draw_text_scaled(ctx, instance, params)


def handle_draw_health_bar(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw a health bar at a position."""
    x1 = parse_int(ctx, params.get("x1", 0), instance, default=0)
    y1 = parse_int(ctx, params.get("y1", 0), instance, default=0)
    x2 = parse_int(ctx, params.get("x2", 100), instance, default=100)
    y2 = parse_int(ctx, params.get("y2", 20), instance, default=20)
    back_color = parse_color(params.get("back_color", "#808080"))
    bar_color = parse_color(params.get("bar_color", "#00FF00"))
    amount = parse_float(ctx, params.get("amount", 100), instance, default=100.0)

    queue_draw_command(instance, {
        'type': 'health_bar',
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'health': amount,
        'back_color': back_color,
        'bar_color': bar_color
    })


def handle_fill_color(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Fill the entire screen with a color.

    Parameters:
        color: Fill color (hex string like "#RRGGBB")
    """
    color_param = ctx._parse_value(params.get("color", "#000000"), instance)

    # Parse color if it's a hex string
    if isinstance(color_param, str) and color_param.startswith('#'):
        try:
            hex_color = color_param.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            color = (r, g, b)
        except (ValueError, IndexError):
            color = (0, 0, 0)
    else:
        color = (0, 0, 0)

    queue_draw_command(instance, {
        'type': 'fill',
        'color': color
    })

    logger.debug(f"  🎨 Fill color: {color}")


def handle_create_effect(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Create a visual particle effect.

    Parameters:
        effect: Effect type (explosion, ring, ellipse, firework, smoke, smoke_up, star, spark, flare, cloud, rain, snow)
        x: X position
        y: Y position
        size: Effect size (small, medium, large)
        color: Effect color
    """
    effect_type = ctx._parse_value(params.get("effect", "explosion"), instance)
    x = ctx._parse_value(params.get("x", 0), instance)
    y = ctx._parse_value(params.get("y", 0), instance)
    size = ctx._parse_value(params.get("size", "medium"), instance)
    color_param = ctx._parse_value(params.get("color", "#FFFFFF"), instance)

    try:
        x = int(x) if x is not None else 0
        y = int(y) if y is not None else 0
    except (ValueError, TypeError):
        x, y = 0, 0

    # Parse color
    if isinstance(color_param, str) and color_param.startswith('#'):
        try:
            hex_color = color_param.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            color = (r, g, b)
        except (ValueError, IndexError):
            color = (255, 255, 255)
    else:
        color = (255, 255, 255)

    # Convert size to multiplier
    size_multipliers = {'small': 0.5, 'medium': 1.0, 'large': 2.0}
    size_mult = size_multipliers.get(size, 1.0)

    # Queue effect command for draw event
    queue_draw_command(instance, {
        'type': 'effect',
        'effect_type': effect_type,
        'x': x,
        'y': y,
        'size': size_mult,
        'color': color
    })

    logger.debug(f"  ✨ Create effect '{effect_type}' at ({x}, {y})")


def handle_set_draw_color(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the drawing color (alias for set_color)."""
    handle_set_color(ctx, instance, params)


def handle_set_draw_font(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the drawing font (alias for set_font)."""
    handle_set_font(ctx, instance, params)


# =============================================================================
# Handler Registry
# =============================================================================

DRAW_HANDLERS: Dict[str, Any] = {
    "draw_self": handle_draw_self,
    "draw_sprite": handle_draw_sprite,
    "draw_background": handle_draw_background,
    "draw_text": handle_draw_text,
    "draw_text_scaled": handle_draw_text_scaled,
    "draw_rectangle": handle_draw_rectangle,
    "draw_gradient_hor": handle_draw_gradient_hor,
    "draw_gradient_vert": handle_draw_gradient_vert,
    "draw_ellipse": handle_draw_ellipse,
    "draw_circle": handle_draw_circle,
    "draw_line": handle_draw_line,
    "draw_arrow": handle_draw_arrow,
    "set_color": handle_set_color,
    "set_font": handle_set_font,
    "set_alpha": handle_set_alpha,
    "set_fullscreen": handle_set_fullscreen,
    # Additional aliases and handlers
    "draw_scaled_text": handle_draw_scaled_text,
    "draw_health_bar": handle_draw_health_bar,
    "fill_color": handle_fill_color,
    "create_effect": handle_create_effect,
    "set_draw_color": handle_set_draw_color,
    "set_draw_font": handle_set_draw_font,
}
