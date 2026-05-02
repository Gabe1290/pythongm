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
    "sleep": handle_sleep,
}
