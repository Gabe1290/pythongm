#!/usr/bin/env python3
"""The ``play_sound`` fallback handler.

This module used to carry the legacy audio action names too --
``stop_all_sounds``, ``set_sound_volume``, ``if_sound_playing``. Those went on
2026-09-06: with the "do we keep pre-modern action names?" question answered
no (too few legacy projects to justify it), none of them had a producer
anywhere in the IDE, the samples, the importer or the Blockly config.

``play_sound`` is NOT legacy and stays. It is a shadowed fallback for the
plugin-owned action in ``plugins/audio_actions.py``: that plugin's
``register_custom_action`` overwrites this entry whenever plugins load, so in a
normal run this code never executes. It matters when they have not -- a
CLI/test import, or a packaged build whose ``plugins/`` directory failed to
resolve -- where without it a sample calling ``play_sound`` would hit an
unregistered action rather than a merely silent one.
``docs/POST_1_0_REFACTOR.md``'s teardown says of this handler: "leave it
regardless", and deleting it did in fact break
``test_export_feature_matrix.py``'s "runtime covers every sample action" check.
"""

from typing import Dict, Any
from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_bool,
)


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


SOUND_HANDLERS = {
    "play_sound": handle_play_sound,
}
