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



def handle_set_fullscreen(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Toggle fullscreen mode."""
    fullscreen = parse_bool(params.get("fullscreen", True))

    if ctx.game_runner:
        ctx.game_runner.fullscreen = fullscreen
    logger.debug(f"  🖥️ Set fullscreen = {fullscreen}")








# =============================================================================
# Handler Registry
# =============================================================================

DRAW_HANDLERS: Dict[str, Any] = {
    "draw_self": handle_draw_self,
    "draw_text_scaled": handle_draw_text_scaled,
    "draw_gradient_hor": handle_draw_gradient_hor,
    "draw_gradient_vert": handle_draw_gradient_vert,
    "set_font": handle_set_font,
    "set_fullscreen": handle_set_fullscreen,
    # Additional aliases and handlers
}
