#!/usr/bin/env python3
"""
Resource Action Handlers

Handles dynamic resource loading and replacement.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_int, parse_bool,
)

logger = get_logger(__name__)


def handle_replace_sprite(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Replace a sprite resource with an external image."""
    sprite = params.get("sprite", "")
    filename = params.get("filename", "")
    images = parse_int(ctx, params.get("images", 1), instance, default=1)
    remove_back = parse_bool(params.get("remove_back", False))
    smooth = parse_bool(params.get("smooth", False))
    preload = parse_bool(params.get("preload", True))
    origin_x = parse_int(ctx, params.get("origin_x", 0), instance, default=0)
    origin_y = parse_int(ctx, params.get("origin_y", 0), instance, default=0)

    if ctx.game_runner:
        ctx.game_runner.pending_resource_ops.append({
            'type': 'replace_sprite',
            'sprite': sprite,
            'filename': filename,
            'images': images,
            'remove_back': remove_back,
            'smooth': smooth,
            'preload': preload,
            'origin_x': origin_x,
            'origin_y': origin_y
        })

    logger.debug(f"  🖼️ Replace sprite '{sprite}' with '{filename}'")


def handle_replace_sound(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Replace a sound resource with an external file."""
    sound = params.get("sound", "")
    filename = params.get("filename", "")

    if ctx.game_runner:
        if not hasattr(ctx.game_runner, 'pending_resource_ops'):
            ctx.game_runner.pending_resource_ops = []
        ctx.game_runner.pending_resource_ops.append({
            'type': 'replace_sound',
            'sound': sound,
            'filename': filename
        })

    logger.debug(f"  🔊 Replace sound '{sound}' with '{filename}'")


def handle_replace_background(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Replace a background resource with an external image."""
    background = params.get("background", "")
    filename = params.get("filename", "")

    if ctx.game_runner:
        if not hasattr(ctx.game_runner, 'pending_resource_ops'):
            ctx.game_runner.pending_resource_ops = []
        ctx.game_runner.pending_resource_ops.append({
            'type': 'replace_background',
            'background': background,
            'filename': filename
        })

    logger.debug(f"  🏞️ Replace background '{background}' with '{filename}'")


def handle_replace_font(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Replace a font resource."""
    font = params.get("font", "")
    name = params.get("name", "Arial")
    size = parse_int(ctx, params.get("size", 12), instance, default=12)
    bold = parse_bool(params.get("bold", False))
    italic = parse_bool(params.get("italic", False))

    if ctx.game_runner:
        if not hasattr(ctx.game_runner, 'pending_resource_ops'):
            ctx.game_runner.pending_resource_ops = []
        ctx.game_runner.pending_resource_ops.append({
            'type': 'replace_font',
            'font': font,
            'name': name,
            'size': size,
            'bold': bold,
            'italic': italic
        })

    logger.debug(f"  🔤 Replace font '{font}' with {name} {size}pt")


def handle_define_sprite(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Define a new sprite from file."""
    name = params.get("name", "")
    filename = params.get("filename", "")
    images = parse_int(ctx, params.get("images", 1), instance, default=1)
    origin_x = parse_int(ctx, params.get("origin_x", 0), instance, default=0)
    origin_y = parse_int(ctx, params.get("origin_y", 0), instance, default=0)

    if ctx.game_runner and name:
        if not hasattr(ctx.game_runner, 'pending_resource_ops'):
            ctx.game_runner.pending_resource_ops = []
        ctx.game_runner.pending_resource_ops.append({
            'type': 'define_sprite',
            'name': name,
            'filename': filename,
            'images': images,
            'origin_x': origin_x,
            'origin_y': origin_y
        })

    logger.debug(f"  🖼️ Define sprite '{name}' from '{filename}'")


def handle_define_sound(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Define a new sound from file."""
    name = params.get("name", "")
    filename = params.get("filename", "")

    if ctx.game_runner and name:
        if not hasattr(ctx.game_runner, 'pending_resource_ops'):
            ctx.game_runner.pending_resource_ops = []
        ctx.game_runner.pending_resource_ops.append({
            'type': 'define_sound',
            'name': name,
            'filename': filename
        })

    logger.debug(f"  🔊 Define sound '{name}' from '{filename}'")


def handle_free_sprite(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Free a sprite resource from memory."""
    sprite = params.get("sprite", "")

    if ctx.game_runner:
        if not hasattr(ctx.game_runner, 'pending_resource_ops'):
            ctx.game_runner.pending_resource_ops = []
        ctx.game_runner.pending_resource_ops.append({
            'type': 'free_sprite',
            'sprite': sprite
        })

    logger.debug(f"  🗑️ Free sprite '{sprite}'")


def handle_free_sound(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Free a sound resource from memory."""
    sound = params.get("sound", "")

    if ctx.game_runner:
        if not hasattr(ctx.game_runner, 'pending_resource_ops'):
            ctx.game_runner.pending_resource_ops = []
        ctx.game_runner.pending_resource_ops.append({
            'type': 'free_sound',
            'sound': sound
        })

    logger.debug(f"  🗑️ Free sound '{sound}'")


# =============================================================================
# Handler Registry
# =============================================================================

RESOURCE_HANDLERS: Dict[str, Any] = {
    "replace_sprite": handle_replace_sprite,
    "replace_sound": handle_replace_sound,
    "replace_background": handle_replace_background,
    "replace_font": handle_replace_font,
    "define_sprite": handle_define_sprite,
    "define_sound": handle_define_sound,
    "free_sprite": handle_free_sprite,
    "free_sound": handle_free_sound,
}
