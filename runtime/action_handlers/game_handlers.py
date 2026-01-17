#!/usr/bin/env python3
"""
Game Action Handlers

Handles game-level actions: messages, room transitions, game control.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_bool,
)

logger = get_logger(__name__)


def handle_show_message(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute show message action."""
    message = params.get("message", "")
    logger.info(f"💬 MESSAGE: {message}")

    if not hasattr(instance, 'pending_messages'):
        instance.pending_messages = []
    instance.pending_messages.append(message)


def handle_restart_room(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute restart room action - resets current level."""
    logger.debug(f"🔄 Restart room requested by {instance.object_name}")
    instance.restart_room_flag = True


def handle_next_room(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute next room action - advances to next level."""
    logger.debug(f"➡️  Next room requested by {instance.object_name}")
    instance.next_room_flag = True


def handle_previous_room(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute previous room action - goes to previous level."""
    logger.debug(f"⬅️  Previous room requested by {instance.object_name}")
    instance.previous_room_flag = True


def handle_goto_room(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Go to a specific room by name."""
    room_name = params.get("room", "")
    transition = params.get("transition", "none")

    if not room_name:
        logger.debug("⚠️ goto_room: No room specified")
        return

    if not ctx.game_runner:
        logger.debug("⚠️ goto_room: No game_runner reference")
        return

    room_list = ctx.game_runner.get_room_list()
    if room_name not in room_list:
        logger.debug(f"⚠️ goto_room: Room '{room_name}' not found")
        return

    instance.goto_room_target = room_name
    instance.goto_room_transition = transition
    logger.debug(f"🚪 Go to room '{room_name}' requested")


def handle_if_next_room_exists(ctx: HandlerContext, instance: Instance, params: Parameters):
    """Check if next room exists - conditional action."""
    if not ctx.game_runner:
        return False

    room_list = ctx.game_runner.get_room_list()
    current_room = ctx.game_runner.current_room

    next_exists = False
    if current_room and room_list:
        try:
            current_index = room_list.index(current_room.name)
            next_exists = (current_index + 1) < len(room_list)
        except ValueError:
            pass

    logger.debug(f"❓ Next room exists: {next_exists}")

    # Handle nested actions (Blockly-style)
    then_actions = params.get('then_actions', [])
    else_actions = params.get('else_actions', [])

    if then_actions or else_actions:
        if next_exists:
            for action in then_actions:
                ctx.execute_action(instance, action)
        else:
            for action in else_actions:
                ctx.execute_action(instance, action)
        return None

    return next_exists


def handle_if_previous_room_exists(ctx: HandlerContext, instance: Instance, params: Parameters):
    """Check if previous room exists - conditional action."""
    if not ctx.game_runner:
        return False

    room_list = ctx.game_runner.get_room_list()
    current_room = ctx.game_runner.current_room

    prev_exists = False
    if current_room and room_list:
        try:
            current_index = room_list.index(current_room.name)
            prev_exists = current_index > 0
        except ValueError:
            pass

    logger.debug(f"❓ Previous room exists: {prev_exists}")

    then_actions = params.get('then_actions', [])
    else_actions = params.get('else_actions', [])

    if then_actions or else_actions:
        if prev_exists:
            for action in then_actions:
                ctx.execute_action(instance, action)
        else:
            for action in else_actions:
                ctx.execute_action(instance, action)
        return None

    return prev_exists


def handle_check_room(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if currently in a specific room."""
    room_name = params.get("room", "")
    not_flag = parse_bool(params.get("not_flag", False))

    if not room_name or not ctx.game_runner or not ctx.game_runner.current_room:
        return not not_flag

    is_in_room = (ctx.game_runner.current_room.name == room_name)
    result = is_in_room if not not_flag else not is_in_room

    logger.debug(f"❓ Check room '{room_name}': result={result}")
    return result


def handle_end_game(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """End the game."""
    logger.debug(f"🛑 End game requested by {instance.object_name}")
    instance.end_game_flag = True


def handle_restart_game(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Restart the game from the beginning."""
    logger.debug(f"🔄 Restart game requested by {instance.object_name}")
    instance.restart_game_flag = True


def handle_sleep(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Pause execution for specified milliseconds."""
    from runtime.action_handlers.base import parse_int
    milliseconds = parse_int(ctx, params.get("milliseconds", 1000), instance, default=1000)

    if ctx.game_runner:
        ctx.game_runner.sleep_until = ctx.game_runner.current_time + milliseconds
    logger.debug(f"💤 Sleep for {milliseconds}ms")


# =============================================================================
# Handler Registry
# =============================================================================

GAME_HANDLERS: Dict[str, Any] = {
    "show_message": handle_show_message,
    "restart_room": handle_restart_room,
    "next_room": handle_next_room,
    "previous_room": handle_previous_room,
    "goto_room": handle_goto_room,
    "if_next_room_exists": handle_if_next_room_exists,
    "if_previous_room_exists": handle_if_previous_room_exists,
    "check_room": handle_check_room,
    "end_game": handle_end_game,
    "restart_game": handle_restart_game,
    "sleep": handle_sleep,
}
