#!/usr/bin/env python3
"""Particle-system and timeline actions for
:class:`~runtime.action_executor.ActionExecutor`.

The sixteen methods behind the two features added in Tier 5: the particle
system (create/destroy the system, define a particle type, create/destroy an
emitter, burst and stream, clear, plus the legacy ``create_effect``) and
timelines (set, position, speed, start, pause, stop). ``_spawn_particles`` is
the shared worker ``burst`` and ``stream`` both call, and the per-frame
emitter update in the engine mirrors it.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 6) as a MIXIN -- see
``runtime/action_drawing.py``'s header for why these are sibling modules rather
than the package layout the plan sketched.

The most self-contained cluster in File 4 so far: it touches **no** ``self``
state at all and reaches only ``_parse_value`` on the base. Everything it
mutates lives on the instance it was handed (``instance._particle_system`` /
``instance.timeline_*``), which is also why the HTML5 and Kivy exporters could
mirror it action-for-action.

``random`` is imported inside ``_spawn_particles`` rather than at module level;
the move keeps it there, so this module stays as import-light as the engine.
"""

import math
from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


class ParticleTimelineMixin:
    """Particle-system and timeline ``execute_*_action`` methods."""

    def execute_create_effect_action(self, instance, parameters: Dict[str, Any]):
        """Create a visual particle effect

        Parameters:
            effect: Effect type (explosion, ring, ellipse, firework, smoke, smoke_up, star, spark, flare, cloud, rain, snow)
            x: X position
            y: Y position
            size: Effect size (small, medium, large)
            color: Effect color
        """
        effect_type = self._parse_value(parameters.get("effect", "explosion"), instance)
        x = self._parse_value(parameters.get("x", 0), instance)
        y = self._parse_value(parameters.get("y", 0), instance)
        size = self._parse_value(parameters.get("size", "medium"), instance)
        color_param = self._parse_value(parameters.get("color", "#FFFFFF"), instance)

        try:
            x = int(x) if x is not None else 0
            y = int(y) if y is not None else 0
        except (ValueError, TypeError):
            x, y = 0, 0

        # Parse color
        if isinstance(color_param, str) and color_param.startswith('#'):
            try:
                hex_color = color_param.lstrip('#')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                color = (r, g, b)
            except (ValueError, IndexError):
                color = (255, 255, 255)
        else:
            color = (255, 255, 255)

        # Convert size to multiplier
        size_multipliers = {'small': 0.5, 'medium': 1.0, 'large': 2.0}
        size_mult = size_multipliers.get(size, 1.0)

        # Queue effect command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'effect',
            'effect_type': effect_type,
            'x': x,
            'y': y,
            'size': size_mult,
            'color': color
        })

        logger.debug(f"✨ Queued create_effect: {effect_type} at ({x}, {y}), size={size}, color={color}")
    def execute_create_particle_system_action(self, instance, parameters: Dict[str, Any]):
        """Create a particle system

        Parameters:
            depth: Drawing depth for the particle system

        Creates a new particle system attached to the instance. Each instance
        can have one active particle system.
        """
        depth = self._parse_value(parameters.get("depth", 0), instance)

        try:
            depth = int(depth) if depth is not None else 0
        except (ValueError, TypeError):
            depth = 0

        # Initialize particle system on instance
        if not hasattr(instance, '_particle_system'):
            instance._particle_system = None

        instance._particle_system = {
            'depth': depth,
            'particle_types': {},  # id -> particle type definition
            'emitters': {},  # id -> emitter definition
            'particles': [],  # active particles
            'next_type_id': 0,
            'next_emitter_id': 0
        }

        logger.debug(f"✨ Created particle system at depth {depth}")
    def execute_destroy_particle_system_action(self, instance, parameters: Dict[str, Any]):
        """Destroy the particle system

        Removes the particle system from the instance, clearing all particles
        and emitters.
        """
        if hasattr(instance, '_particle_system') and instance._particle_system:
            instance._particle_system = None
            logger.debug("💥 Destroyed particle system")
        else:
            logger.debug("⚠️ destroy_particle_system: No particle system exists")
    def execute_clear_particles_action(self, instance, parameters: Dict[str, Any]):
        """Clear all particles from the particle system

        Removes all active particles but keeps the particle types and emitters.
        """
        if hasattr(instance, '_particle_system') and instance._particle_system:
            instance._particle_system['particles'] = []
            logger.debug("🧹 Cleared all particles")
        else:
            logger.debug("⚠️ clear_particles: No particle system exists")
    def execute_create_particle_type_action(self, instance, parameters: Dict[str, Any]):
        """Create a particle type definition

        Parameters:
            sprite: Sprite to use for particles
            size_min, size_max: Size range
            size_increase: Size change per step
            color: Particle color
            alpha: Transparency
            speed_min, speed_max: Speed range
            direction_min, direction_max: Direction angle range
            life_min, life_max: Lifetime in steps

        Returns:
            The particle type ID (stored on instance)
        """
        if not hasattr(instance, '_particle_system') or not instance._particle_system:
            logger.debug("⚠️ create_particle_type: No particle system exists")
            return -1

        sprite = parameters.get("sprite", None)
        size_min = self._parse_value(parameters.get("size_min", 1.0), instance)
        size_max = self._parse_value(parameters.get("size_max", 1.0), instance)
        size_increase = self._parse_value(parameters.get("size_increase", 0), instance)
        color_param = self._parse_value(parameters.get("color", "#FFFFFF"), instance)
        alpha = self._parse_value(parameters.get("alpha", 1.0), instance)
        speed_min = self._parse_value(parameters.get("speed_min", 0), instance)
        speed_max = self._parse_value(parameters.get("speed_max", 0), instance)
        direction_min = self._parse_value(parameters.get("direction_min", 0), instance)
        direction_max = self._parse_value(parameters.get("direction_max", 360), instance)
        life_min = self._parse_value(parameters.get("life_min", 100), instance)
        life_max = self._parse_value(parameters.get("life_max", 100), instance)

        # Parse numeric values
        try:
            size_min = float(size_min) if size_min is not None else 1.0
            size_max = float(size_max) if size_max is not None else 1.0
            size_increase = float(size_increase) if size_increase is not None else 0
            alpha = float(alpha) if alpha is not None else 1.0
            speed_min = float(speed_min) if speed_min is not None else 0
            speed_max = float(speed_max) if speed_max is not None else 0
            direction_min = float(direction_min) if direction_min is not None else 0
            direction_max = float(direction_max) if direction_max is not None else 360
            life_min = int(life_min) if life_min is not None else 100
            life_max = int(life_max) if life_max is not None else 100
        except (ValueError, TypeError):
            pass

        # Parse color
        if isinstance(color_param, str) and color_param.startswith('#'):
            try:
                hex_color = color_param.lstrip('#')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                color = (r, g, b)
            except (ValueError, IndexError):
                color = (255, 255, 255)
        else:
            color = (255, 255, 255)

        # Get next type ID
        type_id = instance._particle_system['next_type_id']
        instance._particle_system['next_type_id'] += 1

        # Store particle type
        instance._particle_system['particle_types'][type_id] = {
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

        # Store the last created type ID for easy access
        instance._last_particle_type_id = type_id

        logger.debug(f"⚙️ Created particle type {type_id}: sprite={sprite}, size={size_min}-{size_max}, life={life_min}-{life_max}")
        return type_id
    def execute_create_emitter_action(self, instance, parameters: Dict[str, Any]):
        """Create a particle emitter

        Parameters:
            x, y: Position of emitter center
            width, height: Emitter area dimensions
            shape: Emitter shape (rectangle, ellipse, diamond, line)

        Returns:
            The emitter ID (stored on instance)
        """
        if not hasattr(instance, '_particle_system') or not instance._particle_system:
            logger.debug("⚠️ create_emitter: No particle system exists")
            return -1

        x = self._parse_value(parameters.get("x", 0), instance)
        y = self._parse_value(parameters.get("y", 0), instance)
        width = self._parse_value(parameters.get("width", 0), instance)
        height = self._parse_value(parameters.get("height", 0), instance)
        shape = self._parse_value(parameters.get("shape", "rectangle"), instance)

        try:
            x = int(x) if x is not None else 0
            y = int(y) if y is not None else 0
            width = int(width) if width is not None else 0
            height = int(height) if height is not None else 0
        except (ValueError, TypeError):
            x, y, width, height = 0, 0, 0, 0

        # Validate shape
        valid_shapes = ["rectangle", "ellipse", "diamond", "line"]
        if shape not in valid_shapes:
            shape = "rectangle"

        # Get next emitter ID
        emitter_id = instance._particle_system['next_emitter_id']
        instance._particle_system['next_emitter_id'] += 1

        # Store emitter
        instance._particle_system['emitters'][emitter_id] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'shape': shape,
            'stream_type': None,  # particle type for streaming
            'stream_count': 0  # particles per step (0 = not streaming)
        }

        # Store the last created emitter ID for easy access
        instance._last_emitter_id = emitter_id

        logger.debug(f"🌀 Created emitter {emitter_id}: pos=({x}, {y}), size=({width}x{height}), shape={shape}")
        return emitter_id
    def execute_destroy_emitter_action(self, instance, parameters: Dict[str, Any]):
        """Destroy a particle emitter

        Removes the most recently created emitter, or does nothing if none exist.
        """
        if not hasattr(instance, '_particle_system') or not instance._particle_system:
            logger.debug("⚠️ destroy_emitter: No particle system exists")
            return

        # Destroy the last created emitter
        if hasattr(instance, '_last_emitter_id') and instance._last_emitter_id is not None:
            emitter_id = instance._last_emitter_id
            if emitter_id in instance._particle_system['emitters']:
                del instance._particle_system['emitters'][emitter_id]
                logger.debug(f"💥 Destroyed emitter {emitter_id}")
            instance._last_emitter_id = None
        else:
            logger.debug("⚠️ destroy_emitter: No emitter to destroy")
    def execute_burst_particles_action(self, instance, parameters: Dict[str, Any]):
        """Emit a burst of particles once

        Parameters:
            particle_type: The particle type ID to emit
            number: Number of particles to emit
        """
        if not hasattr(instance, '_particle_system') or not instance._particle_system:
            logger.debug("⚠️ burst_particles: No particle system exists")
            return

        particle_type = self._parse_value(parameters.get("particle_type", 0), instance)
        number = self._parse_value(parameters.get("number", 10), instance)

        try:
            particle_type = int(particle_type) if particle_type is not None else 0
            number = int(number) if number is not None else 10
        except (ValueError, TypeError):
            particle_type, number = 0, 10

        # Check if particle type exists
        if particle_type not in instance._particle_system['particle_types']:
            logger.debug(f"⚠️ burst_particles: Particle type {particle_type} not found")
            return

        # Check if we have an emitter to burst from
        if not hasattr(instance, '_last_emitter_id') or instance._last_emitter_id is None:
            logger.debug("⚠️ burst_particles: No emitter available")
            return

        emitter_id = instance._last_emitter_id
        if emitter_id not in instance._particle_system['emitters']:
            logger.debug(f"⚠️ burst_particles: Emitter {emitter_id} not found")
            return

        emitter = instance._particle_system['emitters'][emitter_id]
        ptype = instance._particle_system['particle_types'][particle_type]

        self._spawn_particles(instance, emitter, ptype, number)

        logger.debug(f"💥 Burst {number} particles of type {particle_type} from emitter {emitter_id}")
    def _spawn_particles(self, instance, emitter: Dict[str, Any], ptype: Dict[str, Any], number: int) -> None:
        """Spawn ``number`` particles from ``emitter`` using ``ptype``'s
        random ranges. Shared by burst_particles (once) and the per-frame
        streaming-emitter update in game_runner.py (continuous) so both
        paths sample particle position/size/speed/direction/life exactly
        the same way (runtime/game_runner.py's step loop, see
        _update_instance_particles)."""
        import random

        for _ in range(number):
            # Random position within emitter area
            if emitter['shape'] == 'rectangle':
                px = emitter['x'] + random.uniform(-emitter['width']/2, emitter['width']/2)
                py = emitter['y'] + random.uniform(-emitter['height']/2, emitter['height']/2)
            elif emitter['shape'] == 'ellipse':
                angle = random.uniform(0, 360)
                radius_x = random.uniform(0, emitter['width']/2)
                radius_y = random.uniform(0, emitter['height']/2)
                px = emitter['x'] + radius_x * math.cos(math.radians(angle))
                py = emitter['y'] + radius_y * math.sin(math.radians(angle))
            elif emitter['shape'] == 'diamond':
                t = random.uniform(-1, 1)
                s = random.uniform(-1, 1) * (1 - abs(t))
                px = emitter['x'] + t * emitter['width']/2
                py = emitter['y'] + s * emitter['height']/2
            else:  # line
                t = random.uniform(-0.5, 0.5)
                px = emitter['x'] + t * emitter['width']
                py = emitter['y']

            # Random particle properties
            size = random.uniform(ptype['size_min'], ptype['size_max'])
            speed = random.uniform(ptype['speed_min'], ptype['speed_max'])
            direction = random.uniform(ptype['direction_min'], ptype['direction_max'])
            life = random.randint(ptype['life_min'], ptype['life_max'])

            particle = {
                'x': px,
                'y': py,
                'size': size,
                'size_increase': ptype['size_increase'],
                'speed': speed,
                'direction': direction,
                'life': life,
                'max_life': life,
                'sprite': ptype['sprite'],
                'color': ptype['color'],
                'alpha': ptype['alpha']
            }
            instance._particle_system['particles'].append(particle)
    def execute_stream_particles_action(self, instance, parameters: Dict[str, Any]):
        """Set up continuous particle emission

        Parameters:
            particle_type: The particle type ID to emit
            number: Number of particles to emit per step (0 to stop)
        """
        if not hasattr(instance, '_particle_system') or not instance._particle_system:
            logger.debug("⚠️ stream_particles: No particle system exists")
            return

        particle_type = self._parse_value(parameters.get("particle_type", 0), instance)
        number = self._parse_value(parameters.get("number", 1), instance)

        try:
            particle_type = int(particle_type) if particle_type is not None else 0
            number = int(number) if number is not None else 1
        except (ValueError, TypeError):
            particle_type, number = 0, 1

        # Check if particle type exists
        if particle_type not in instance._particle_system['particle_types']:
            logger.debug(f"⚠️ stream_particles: Particle type {particle_type} not found")
            return

        # Check if we have an emitter to stream from
        if not hasattr(instance, '_last_emitter_id') or instance._last_emitter_id is None:
            logger.debug("⚠️ stream_particles: No emitter available")
            return

        emitter_id = instance._last_emitter_id
        if emitter_id not in instance._particle_system['emitters']:
            logger.debug(f"⚠️ stream_particles: Emitter {emitter_id} not found")
            return

        # Set up streaming on emitter
        instance._particle_system['emitters'][emitter_id]['stream_type'] = particle_type
        instance._particle_system['emitters'][emitter_id]['stream_count'] = number

        logger.debug(f"🌊 Stream {number} particles/step of type {particle_type} from emitter {emitter_id}")
    def execute_set_timeline_action(self, instance, parameters: Dict[str, Any]):
        """Set the timeline for an instance

        Parameters:
            timeline: The timeline resource name to use

        Sets the timeline_index property on the instance.
        """
        timeline = parameters.get("timeline", None)

        # Initialize timeline properties if not present
        if not hasattr(instance, 'timeline_index'):
            instance.timeline_index = None
        if not hasattr(instance, 'timeline_position'):
            instance.timeline_position = 0
        if not hasattr(instance, 'timeline_speed'):
            instance.timeline_speed = 1.0
        if not hasattr(instance, 'timeline_running'):
            instance.timeline_running = False

        instance.timeline_index = timeline

        # Reset position when setting a new timeline
        instance.timeline_position = 0

        logger.debug(f"⏱️ Set timeline to '{timeline}'")
    def execute_set_timeline_position_action(self, instance, parameters: Dict[str, Any]):
        """Set the timeline position

        Parameters:
            position: The position in the timeline (in steps)
            relative: If True, add to current position instead of setting absolute
        """
        position = self._parse_value(parameters.get("position", 0), instance)
        relative = parameters.get("relative", False)

        if isinstance(relative, str):
            relative = relative.lower() in ('true', '1', 'yes')

        try:
            position = int(position) if position is not None else 0
        except (ValueError, TypeError):
            position = 0

        # Initialize timeline_position if not present
        if not hasattr(instance, 'timeline_position'):
            instance.timeline_position = 0

        if relative:
            instance.timeline_position += position
        else:
            instance.timeline_position = position

        # Ensure position is not negative
        if instance.timeline_position < 0:
            instance.timeline_position = 0

        logger.debug(f"⏱️ Set timeline position to {instance.timeline_position} (relative={relative})")
    def execute_set_timeline_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set the timeline playback speed

        Parameters:
            speed: The speed multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)
        """
        speed = self._parse_value(parameters.get("speed", 1.0), instance)

        try:
            speed = float(speed) if speed is not None else 1.0
        except (ValueError, TypeError):
            speed = 1.0

        # Initialize timeline_speed if not present
        if not hasattr(instance, 'timeline_speed'):
            instance.timeline_speed = 1.0

        instance.timeline_speed = speed

        logger.debug(f"⏱️ Set timeline speed to {speed}")
    def execute_start_timeline_action(self, instance, parameters: Dict[str, Any]):
        """Start timeline playback

        Begins or resumes playback of the instance's timeline from the current position.
        """
        # Initialize timeline_running if not present
        if not hasattr(instance, 'timeline_running'):
            instance.timeline_running = False

        instance.timeline_running = True

        logger.debug("▶️ Started timeline playback")
    def execute_pause_timeline_action(self, instance, parameters: Dict[str, Any]):
        """Pause timeline playback

        Pauses the timeline at the current position. Can be resumed with start_timeline.
        """
        # Initialize timeline_running if not present
        if not hasattr(instance, 'timeline_running'):
            instance.timeline_running = False

        instance.timeline_running = False

        logger.debug("⏸️ Paused timeline")
    def execute_stop_timeline_action(self, instance, parameters: Dict[str, Any]):
        """Stop and reset the timeline

        Stops playback and resets the timeline position to 0.
        """
        # Initialize timeline properties if not present
        if not hasattr(instance, 'timeline_running'):
            instance.timeline_running = False
        if not hasattr(instance, 'timeline_position'):
            instance.timeline_position = 0

        instance.timeline_running = False
        instance.timeline_position = 0

        logger.debug("⏹️ Stopped and reset timeline")
