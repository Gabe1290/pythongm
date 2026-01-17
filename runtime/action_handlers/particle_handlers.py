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


def handle_create_particle_system(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Create a particle system."""
    depth = parse_int(ctx, params.get("depth", 0), instance, default=0)

    instance._particle_system = {
        'depth': depth,
        'particle_types': {},
        'emitters': {},
        'particles': [],
        'next_type_id': 0,
        'next_emitter_id': 0
    }

    logger.debug(f"✨ Created particle system at depth {depth}")


def handle_destroy_particle_system(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Destroy the particle system."""
    if hasattr(instance, '_particle_system') and instance._particle_system:
        instance._particle_system = None
        logger.debug("💥 Destroyed particle system")


def handle_clear_particles(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Clear all particles from the system."""
    ps = _get_particle_system(instance)
    if ps:
        ps['particles'] = []
        logger.debug("🧹 Cleared all particles")


def handle_create_particle_type(ctx: HandlerContext, instance: Instance, params: Parameters) -> int:
    """Create a particle type definition."""
    ps = _get_particle_system(instance)
    if not ps:
        logger.debug("⚠️ create_particle_type: No particle system exists")
        return -1

    sprite = params.get("sprite", None)
    size_min = parse_float(ctx, params.get("size_min", 1.0), instance, default=1.0)
    size_max = parse_float(ctx, params.get("size_max", 1.0), instance, default=1.0)
    size_increase = parse_float(ctx, params.get("size_increase", 0), instance, default=0.0)
    color = parse_color(params.get("color", "#FFFFFF"))
    alpha = parse_float(ctx, params.get("alpha", 1.0), instance, default=1.0)
    speed_min = parse_float(ctx, params.get("speed_min", 0), instance, default=0.0)
    speed_max = parse_float(ctx, params.get("speed_max", 0), instance, default=0.0)
    direction_min = parse_float(ctx, params.get("direction_min", 0), instance, default=0.0)
    direction_max = parse_float(ctx, params.get("direction_max", 360), instance, default=360.0)
    life_min = parse_int(ctx, params.get("life_min", 100), instance, default=100)
    life_max = parse_int(ctx, params.get("life_max", 100), instance, default=100)

    type_id = ps['next_type_id']
    ps['next_type_id'] += 1

    ps['particle_types'][type_id] = {
        'sprite': sprite,
        'size_min': size_min,
        'size_max': size_max,
        'size_increase': size_increase,
        'color': color,
        'alpha': alpha,
        'speed_min': speed_min,
        'speed_max': speed_max,
        'direction_min': direction_min,
        'direction_max': direction_max,
        'life_min': life_min,
        'life_max': life_max
    }

    instance._last_particle_type_id = type_id
    logger.debug(f"⚙️ Created particle type {type_id}")
    return type_id


def handle_create_emitter(ctx: HandlerContext, instance: Instance, params: Parameters) -> int:
    """Create a particle emitter."""
    ps = _get_particle_system(instance)
    if not ps:
        logger.debug("⚠️ create_emitter: No particle system exists")
        return -1

    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)
    width = parse_int(ctx, params.get("width", 0), instance, default=0)
    height = parse_int(ctx, params.get("height", 0), instance, default=0)
    shape = params.get("shape", "rectangle")

    valid_shapes = ["rectangle", "ellipse", "diamond", "line"]
    if shape not in valid_shapes:
        shape = "rectangle"

    emitter_id = ps['next_emitter_id']
    ps['next_emitter_id'] += 1

    ps['emitters'][emitter_id] = {
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'shape': shape,
        'stream_type': None,
        'stream_count': 0
    }

    instance._last_emitter_id = emitter_id
    logger.debug(f"🌀 Created emitter {emitter_id} at ({x}, {y})")
    return emitter_id


def handle_destroy_emitter(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Destroy a particle emitter."""
    ps = _get_particle_system(instance)
    if not ps:
        return

    emitter_id = getattr(instance, '_last_emitter_id', -1)
    if emitter_id in ps['emitters']:
        del ps['emitters'][emitter_id]
        logger.debug(f"💥 Destroyed emitter {emitter_id}")


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


def handle_burst_particles(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Burst particles (alias for emitter_burst)."""
    handle_emitter_burst(ctx, instance, params)


def handle_stream_particles(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Stream particles (alias for emitter_stream)."""
    handle_emitter_stream(ctx, instance, params)


# =============================================================================
# Handler Registry
# =============================================================================

PARTICLE_HANDLERS: Dict[str, Any] = {
    "create_particle_system": handle_create_particle_system,
    "destroy_particle_system": handle_destroy_particle_system,
    "clear_particles": handle_clear_particles,
    "create_particle_type": handle_create_particle_type,
    "create_emitter": handle_create_emitter,
    "destroy_emitter": handle_destroy_emitter,
    "emitter_burst": handle_emitter_burst,
    "emitter_stream": handle_emitter_stream,
    # Aliases
    "burst_particles": handle_burst_particles,
    "stream_particles": handle_stream_particles,
}
