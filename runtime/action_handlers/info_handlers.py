#!/usr/bin/env python3
"""
Info Action Handlers

Handles information display actions.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_int, parse_bool, parse_color,
    queue_draw_command,
)

logger = get_logger(__name__)


def handle_display_info(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Display game information dialog."""
    title = params.get("title", "Game Information")
    text = params.get("text", "")

    if ctx.game_runner:
        ctx.game_runner.pending_info_dialog = {
            'title': title,
            'text': text
        }

    logger.debug(f"  ℹ️ Display info: '{title}'")


def handle_show_game_info(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show the game's built-in information."""
    if ctx.game_runner:
        ctx.game_runner.show_game_info_flag = True

    logger.debug("  ℹ️ Show game info requested")


def handle_draw_game_info(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw game information on screen."""
    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)

    queue_draw_command(instance, {
        'type': 'game_info',
        'x': x,
        'y': y
    })


def handle_show_message_ext(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show extended message with buttons."""
    message = params.get("message", "")
    button1 = params.get("button1", "OK")
    button2 = params.get("button2", "")
    button3 = params.get("button3", "")

    if ctx.game_runner:
        ctx.game_runner.pending_message_ext = {
            'message': message,
            'buttons': [b for b in [button1, button2, button3] if b]
        }

    logger.debug(f"  💬 Extended message: '{message[:30]}...'")


def handle_show_question(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Show a yes/no question dialog."""
    question = params.get("question", "")

    if ctx.game_runner:
        ctx.game_runner.pending_question = question
        # Return will be determined by game runner after dialog
        return True

    logger.debug(f"  ❓ Question: '{question}'")
    return True  # Default to yes


def handle_get_string(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show an input dialog for string input."""
    message = params.get("message", "")
    default = params.get("default", "")
    variable = params.get("variable", "")

    if ctx.game_runner and variable:
        ctx.game_runner.pending_input = {
            'type': 'string',
            'message': message,
            'default': default,
            'variable': variable,
            'instance': instance
        }

    logger.debug(f"  📝 Get string: '{message}'")


def handle_get_number(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show an input dialog for number input."""
    message = params.get("message", "")
    default = params.get("default", 0)
    variable = params.get("variable", "")

    if ctx.game_runner and variable:
        ctx.game_runner.pending_input = {
            'type': 'number',
            'message': message,
            'default': default,
            'variable': variable,
            'instance': instance
        }

    logger.debug(f"  🔢 Get number: '{message}'")


def handle_show_debug_message(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show debug message in console."""
    message = params.get("message", "")
    logger.info(f"🐛 {message}")


def handle_show_error(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show an error message."""
    message = params.get("message", "")
    abort = parse_bool(params.get("abort", False))

    if ctx.game_runner:
        ctx.game_runner.pending_error = {
            'message': message,
            'abort': abort
        }

    logger.error(f"❌ ERROR: {message}")


# =============================================================================
# Handler Registry
# =============================================================================

INFO_HANDLERS: Dict[str, Any] = {
    "display_info": handle_display_info,
    "show_game_info": handle_show_game_info,
    "draw_game_info": handle_draw_game_info,
    "show_message_ext": handle_show_message_ext,
    "show_question": handle_show_question,
    "get_string": handle_get_string,
    "get_number": handle_get_number,
    "show_debug_message": handle_show_debug_message,
    "show_error": handle_show_error,
}
