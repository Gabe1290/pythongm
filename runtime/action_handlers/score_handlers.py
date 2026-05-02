#!/usr/bin/env python3
"""
Score Action Handlers

Handles score, lives, and health management.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_int, parse_bool,
)

logger = get_logger(__name__)



def handle_if_score(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if score meets condition."""
    value = parse_int(ctx, params.get("value", 0), instance, default=0)
    operation = params.get("operation", "equals")
    not_flag = parse_bool(params.get("not_flag", False))

    score = getattr(ctx.game_runner, 'score', 0) if ctx.game_runner else 0

    if operation == "equals":
        result = score == value
    elif operation == "greater_than":
        result = score > value
    elif operation == "less_than":
        result = score < value
    elif operation == "greater_equal":
        result = score >= value
    elif operation == "less_equal":
        result = score <= value
    else:
        result = score == value

    if not_flag:
        result = not result

    logger.debug(f"  ❓ if_score: {score} {operation} {value} = {result}")
    return result






def handle_if_lives(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if lives meet condition."""
    value = parse_int(ctx, params.get("value", 0), instance, default=0)
    operation = params.get("operation", "equals")
    not_flag = parse_bool(params.get("not_flag", False))

    lives = getattr(ctx.game_runner, 'lives', 3) if ctx.game_runner else 3

    if operation == "equals":
        result = lives == value
    elif operation == "greater_than":
        result = lives > value
    elif operation == "less_than":
        result = lives < value
    elif operation == "greater_equal":
        result = lives >= value
    elif operation == "less_equal":
        result = lives <= value
    else:
        result = lives == value

    if not_flag:
        result = not result

    logger.debug(f"  ❓ if_lives: {lives} {operation} {value} = {result}")
    return result



def handle_draw_lives_images(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw lives as sprite images."""
    from runtime.action_handlers.base import queue_draw_command

    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)
    sprite = params.get("sprite", "")

    lives = getattr(ctx.game_runner, 'lives', 3) if ctx.game_runner else 3

    queue_draw_command(instance, {
        'type': 'lives_images',
        'x': x,
        'y': y,
        'sprite': sprite,
        'count': lives
    })



def handle_if_health(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if health meets condition."""
    value = parse_int(ctx, params.get("value", 0), instance, default=0)
    operation = params.get("operation", "equals")
    not_flag = parse_bool(params.get("not_flag", False))

    health = getattr(ctx.game_runner, 'health', 100) if ctx.game_runner else 100

    if operation == "equals":
        result = health == value
    elif operation == "greater_than":
        result = health > value
    elif operation == "less_than":
        result = health < value
    elif operation == "greater_equal":
        result = health >= value
    elif operation == "less_equal":
        result = health <= value
    else:
        result = health == value

    if not_flag:
        result = not result

    logger.debug(f"  ❓ if_health: {health} {operation} {value} = {result}")
    return result


def handle_draw_health(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw health bar at a position."""
    from runtime.action_handlers.base import queue_draw_command, parse_color

    x1 = parse_int(ctx, params.get("x1", 0), instance, default=0)
    y1 = parse_int(ctx, params.get("y1", 0), instance, default=0)
    x2 = parse_int(ctx, params.get("x2", 100), instance, default=100)
    y2 = parse_int(ctx, params.get("y2", 20), instance, default=20)
    back_color = parse_color(params.get("back_color", "#808080"))
    bar_color = parse_color(params.get("bar_color", "#00FF00"))

    health = getattr(ctx.game_runner, 'health', 100) if ctx.game_runner else 100

    queue_draw_command(instance, {
        'type': 'health_bar',
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'health': health,
        'back_color': back_color,
        'bar_color': bar_color
    })


def handle_set_caption(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the window caption."""
    show_score = parse_bool(params.get("show_score", True))
    show_lives = parse_bool(params.get("show_lives", True))
    show_health = parse_bool(params.get("show_health", True))
    caption = params.get("caption", "")

    if ctx.game_runner:
        ctx.game_runner.caption_settings = {
            'show_score': show_score,
            'show_lives': show_lives,
            'show_health': show_health,
            'caption': caption
        }

    logger.debug(f"  📝 Set caption: '{caption}' (score={show_score}, lives={show_lives}, health={show_health})")





# =============================================================================
# Handler Registry
# =============================================================================

SCORE_HANDLERS: Dict[str, Any] = {
    "if_score": handle_if_score,
    "if_lives": handle_if_lives,
    "draw_lives_images": handle_draw_lives_images,
    "if_health": handle_if_health,
    "draw_health": handle_draw_health,
    "set_caption": handle_set_caption,
    # Test aliases
}
