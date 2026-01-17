#!/usr/bin/env python3
"""
Sound Action Handlers

Handles sound playback and audio control.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_bool,
)

logger = get_logger(__name__)


def handle_play_sound(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Play a sound effect."""
    sound = params.get("sound", "")
    loop = parse_bool(params.get("loop", False))

    if not sound:
        logger.debug("⚠️ play_sound: No sound specified")
        return

    if not hasattr(instance, 'pending_sounds'):
        instance.pending_sounds = []

    instance.pending_sounds.append({
        'sound': sound,
        'loop': loop,
        'action': 'play'
    })

    logger.debug(f"  🔊 Queue play sound '{sound}' (loop={loop})")


def handle_stop_sound(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Stop a playing sound."""
    sound = params.get("sound", "")

    if not hasattr(instance, 'pending_sounds'):
        instance.pending_sounds = []

    instance.pending_sounds.append({
        'sound': sound,
        'action': 'stop'
    })

    logger.debug(f"  🔇 Queue stop sound '{sound}'")


def handle_stop_all_sounds(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Stop all playing sounds."""
    if not hasattr(instance, 'pending_sounds'):
        instance.pending_sounds = []

    instance.pending_sounds.append({
        'action': 'stop_all'
    })

    logger.debug("  🔇 Queue stop all sounds")


def handle_if_sound_playing(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if a sound is currently playing."""
    sound = params.get("sound", "")
    not_flag = parse_bool(params.get("not_flag", False))

    result = False
    if ctx.game_runner and hasattr(ctx.game_runner, 'playing_sounds'):
        result = sound in ctx.game_runner.playing_sounds

    if not_flag:
        result = not result

    logger.debug(f"  ❓ if_sound_playing: '{sound}' = {result}")
    return result


def handle_set_sound_volume(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the volume for a sound."""
    sound = params.get("sound", "")
    volume = parse_float(ctx, params.get("volume", 1.0), instance, default=1.0)

    if not hasattr(instance, 'pending_sounds'):
        instance.pending_sounds = []

    instance.pending_sounds.append({
        'sound': sound,
        'volume': max(0.0, min(1.0, volume)),
        'action': 'set_volume'
    })

    logger.debug(f"  🔊 Queue set volume for '{sound}' = {volume}")


def handle_check_sound(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if a sound is playing (alias for if_sound_playing)."""
    return handle_if_sound_playing(ctx, instance, params)


# =============================================================================
# Handler Registry
# =============================================================================

SOUND_HANDLERS: Dict[str, Any] = {
    "play_sound": handle_play_sound,
    "stop_sound": handle_stop_sound,
    "stop_all_sounds": handle_stop_all_sounds,
    "if_sound_playing": handle_if_sound_playing,
    "set_sound_volume": handle_set_sound_volume,
    # Aliases
    "check_sound": handle_check_sound,
}
