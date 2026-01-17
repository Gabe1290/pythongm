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
    alarm_id = parse_int(ctx, params.get("alarm", 0), instance, default=0)
    steps = parse_int(ctx, params.get("steps", 30), instance, default=30)
    relative = parse_bool(params.get("relative", False))

    # Ensure alarm array exists
    if not hasattr(instance, 'alarms'):
        instance.alarms = {}

    if relative:
        current = instance.alarms.get(alarm_id, 0)
        instance.alarms[alarm_id] = max(0, current + steps)
    else:
        instance.alarms[alarm_id] = max(0, steps)

    logger.debug(f"  ⏰ Set alarm[{alarm_id}] = {instance.alarms[alarm_id]} steps")


def handle_if_alarm(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if an alarm is active (not fired)."""
    alarm_id = parse_int(ctx, params.get("alarm", 0), instance, default=0)
    not_flag = parse_bool(params.get("not_flag", False))

    alarms = getattr(instance, 'alarms', {})
    result = alarm_id in alarms and alarms[alarm_id] > 0

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
