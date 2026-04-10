#!/usr/bin/env python3
"""
Timing Action Handlers

Handles alarms, timers, and time-based actions.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_int, parse_float, parse_bool,
)

logger = get_logger(__name__)


def handle_set_alarm(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set an alarm to trigger after specified steps."""
    # Accept "alarm_number", "alarm_num", and "alarm" parameter names
    alarm_raw = params.get("alarm_number", params.get("alarm_num", params.get("alarm", 0)))
    alarm_id = parse_int(ctx, alarm_raw, instance, default=0)
    steps = parse_int(ctx, params.get("steps", 30), instance, default=30)
    relative = parse_bool(params.get("relative", False))

    # Validate alarm number
    if alarm_id < 0 or alarm_id > 11:
        logger.warning(f"  ⚠️ set_alarm: Invalid alarm number {alarm_id} (must be 0-11)")
        return

    # Ensure alarm array exists (list of 12, matching game_runner expectations)
    if not hasattr(instance, 'alarm'):
        instance.alarm = [-1] * 12

    if relative:
        current = instance.alarm[alarm_id]
        if current < 0:
            current = 0
        steps = current + steps

    instance.alarm[alarm_id] = steps

    if steps < 0:
        logger.debug(f"  ⏰ Alarm {alarm_id} disabled for {instance.object_name}")
    else:
        logger.debug(f"  ⏰ Set alarm[{alarm_id}] = {steps} steps")


def handle_if_alarm(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if an alarm is active (not fired)."""
    alarm_raw = params.get("alarm_number", params.get("alarm_num", params.get("alarm", 0)))
    alarm_id = parse_int(ctx, alarm_raw, instance, default=0)
    not_flag = parse_bool(params.get("not_flag", False))

    alarm_list = getattr(instance, 'alarm', [-1] * 12)
    result = 0 <= alarm_id < 12 and alarm_list[alarm_id] > 0

    if not_flag:
        result = not result

    logger.debug(f"  ❓ if_alarm[{alarm_id}]: active = {result}")
    return result


def handle_set_timeline(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the timeline for the instance."""
    timeline = params.get("timeline", "")
    position = parse_int(ctx, params.get("position", 0), instance, default=0)
    start = parse_bool(params.get("start", True))
    loop = parse_bool(params.get("loop", False))

    instance.timeline = timeline
    instance.timeline_position = position
    instance.timeline_running = start
    instance.timeline_loop = loop

    logger.debug(f"  📜 Set timeline '{timeline}' at position {position}")


def handle_set_timeline_position(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the timeline position."""
    position = parse_int(ctx, params.get("position", 0), instance, default=0)
    relative = parse_bool(params.get("relative", False))

    if relative:
        instance.timeline_position = getattr(instance, 'timeline_position', 0) + position
    else:
        instance.timeline_position = position

    logger.debug(f"  📜 Set timeline position = {instance.timeline_position}")


def handle_set_timeline_speed(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the timeline speed."""
    speed = parse_float(ctx, params.get("speed", 1.0), instance, default=1.0)

    instance.timeline_speed = speed

    logger.debug(f"  📜 Set timeline speed = {speed}")


def handle_start_timeline(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Start the timeline."""
    instance.timeline_running = True
    logger.debug("  ▶️ Timeline started")


def handle_pause_timeline(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Pause the timeline."""
    instance.timeline_running = False
    logger.debug("  ⏸️ Timeline paused")


def handle_stop_timeline(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Stop the timeline and reset position."""
    instance.timeline_running = False
    instance.timeline_position = 0
    logger.debug("  ⏹️ Timeline stopped")


def handle_set_path(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set a path for the instance to follow."""
    path = params.get("path", "")
    speed = parse_float(ctx, params.get("speed", 4), instance, default=4.0)
    end_action = params.get("end_action", "stop")
    relative = parse_bool(params.get("relative", False))

    instance.path = path
    instance.path_speed = speed
    instance.path_position = 0
    instance.path_end_action = end_action
    instance.path_relative = relative

    if relative:
        instance.path_start_x = instance.x
        instance.path_start_y = instance.y
    else:
        instance.path_start_x = 0
        instance.path_start_y = 0

    logger.debug(f"  🛤️ Set path '{path}' at speed {speed}")


def handle_end_path(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """End the current path."""
    instance.path = None
    instance.path_speed = 0
    logger.debug("  🛤️ Path ended")


def handle_set_path_position(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the path position (0-1)."""
    position = parse_float(ctx, params.get("position", 0), instance, default=0.0)
    position = max(0.0, min(1.0, position))
    instance.path_position = position
    logger.debug(f"  🛤️ Set path position = {position}")


def handle_set_path_speed(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the path following speed."""
    speed = parse_float(ctx, params.get("speed", 4), instance, default=4.0)
    instance.path_speed = speed
    logger.debug(f"  🛤️ Set path speed = {speed}")


# =============================================================================
# Handler Registry
# =============================================================================

TIMING_HANDLERS: Dict[str, Any] = {
    "set_alarm": handle_set_alarm,
    "if_alarm": handle_if_alarm,
    "set_timeline": handle_set_timeline,
    "set_timeline_position": handle_set_timeline_position,
    "set_timeline_speed": handle_set_timeline_speed,
    "start_timeline": handle_start_timeline,
    "pause_timeline": handle_pause_timeline,
    "stop_timeline": handle_stop_timeline,
    "set_path": handle_set_path,
    "end_path": handle_end_path,
    "set_path_position": handle_set_path_position,
    "set_path_speed": handle_set_path_speed,
}
