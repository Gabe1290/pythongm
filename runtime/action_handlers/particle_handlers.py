#!/usr/bin/env python3
"""
Particle System Action Handlers

Handles particle systems, particle types, and emitters.
"""

from typing import Dict, Any
import random

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_int, parse_float, parse_color,
)

logger = get_logger(__name__)


def _get_particle_system(instance: Instance) -> dict:
    """Get or create particle system for instance."""
    if not hasattr(instance, '_particle_system') or not instance._particle_system:
        return None
    return instance._particle_system








def handle_emitter_burst(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Emit a burst of particles."""
    ps = _get_particle_system(instance)
    if not ps:
        return

    emitter_id = parse_int(ctx, params.get("emitter", -1), instance, default=-1)
    if emitter_id == -1:
        emitter_id = getattr(instance, '_last_emitter_id', -1)

    type_id = parse_int(ctx, params.get("particle_type", -1), instance, default=-1)
    if type_id == -1:
        type_id = getattr(instance, '_last_particle_type_id', -1)

    count = parse_int(ctx, params.get("count", 10), instance, default=10)

    if emitter_id not in ps['emitters'] or type_id not in ps['particle_types']:
        return

    emitter = ps['emitters'][emitter_id]
    ptype = ps['particle_types'][type_id]

    for _ in range(count):
        # Random position within emitter
        px = emitter['x'] + random.uniform(0, emitter['width'])
        py = emitter['y'] + random.uniform(0, emitter['height'])

        ps['particles'].append({
            'x': px,
            'y': py,
            'type': type_id,
            'life': random.randint(ptype['life_min'], ptype['life_max']),
            'max_life': ptype['life_max'],
            'size': random.uniform(ptype['size_min'], ptype['size_max']),
            'speed': random.uniform(ptype['speed_min'], ptype['speed_max']),
            'direction': random.uniform(ptype['direction_min'], ptype['direction_max'])
        })

    logger.debug(f"💥 Emitter {emitter_id} burst {count} particles of type {type_id}")


def handle_emitter_stream(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set emitter to stream particles continuously."""
    ps = _get_particle_system(instance)
    if not ps:
        return

    emitter_id = parse_int(ctx, params.get("emitter", -1), instance, default=-1)
    if emitter_id == -1:
        emitter_id = getattr(instance, '_last_emitter_id', -1)

    type_id = parse_int(ctx, params.get("particle_type", -1), instance, default=-1)
    if type_id == -1:
        type_id = getattr(instance, '_last_particle_type_id', -1)

    count = parse_int(ctx, params.get("count", 1), instance, default=1)

    if emitter_id in ps['emitters']:
        ps['emitters'][emitter_id]['stream_type'] = type_id
        ps['emitters'][emitter_id]['stream_count'] = count
        logger.debug(f"🌊 Emitter {emitter_id} streaming {count} particles/step")




# =============================================================================
# Handler Registry
# =============================================================================

PARTICLE_HANDLERS: Dict[str, Any] = {
    "emitter_burst": handle_emitter_burst,
    "emitter_stream": handle_emitter_stream,
    # Aliases
}
