#!/usr/bin/env python3
"""
Action Handlers Package

This package contains modular action handlers organized by category.
Each handler module exports a dictionary of action_name -> handler_function mappings.

The ActionExecutor auto-discovers and registers all handlers from this package.
"""

from typing import Dict, Callable, Any

# Type alias for action handler functions
ActionHandler = Callable[[Any, Any, Dict[str, Any]], Any]

# Registry of all handlers - populated by imports below
ACTION_HANDLERS: Dict[str, ActionHandler] = {}


def register_handlers(handlers: Dict[str, ActionHandler]) -> None:
    """Register a dictionary of action handlers"""
    ACTION_HANDLERS.update(handlers)


# Import all handler modules - each registers its handlers
from runtime.action_handlers.movement_handlers import MOVEMENT_HANDLERS
from runtime.action_handlers.control_handlers import CONTROL_HANDLERS
from runtime.action_handlers.game_handlers import GAME_HANDLERS
from runtime.action_handlers.variable_handlers import VARIABLE_HANDLERS
from runtime.action_handlers.instance_handlers import INSTANCE_HANDLERS
from runtime.action_handlers.sound_handlers import SOUND_HANDLERS
from runtime.action_handlers.draw_handlers import DRAW_HANDLERS
from runtime.action_handlers.score_handlers import SCORE_HANDLERS
from runtime.action_handlers.room_handlers import ROOM_HANDLERS
from runtime.action_handlers.timing_handlers import TIMING_HANDLERS
from runtime.action_handlers.particle_handlers import PARTICLE_HANDLERS
from runtime.action_handlers.extra_handlers import EXTRA_HANDLERS
from runtime.action_handlers.info_handlers import INFO_HANDLERS
from runtime.action_handlers.resource_handlers import RESOURCE_HANDLERS

# Register all handlers
register_handlers(MOVEMENT_HANDLERS)
register_handlers(CONTROL_HANDLERS)
register_handlers(GAME_HANDLERS)
register_handlers(VARIABLE_HANDLERS)
register_handlers(INSTANCE_HANDLERS)
register_handlers(SOUND_HANDLERS)
register_handlers(DRAW_HANDLERS)
register_handlers(SCORE_HANDLERS)
register_handlers(ROOM_HANDLERS)
register_handlers(TIMING_HANDLERS)
register_handlers(PARTICLE_HANDLERS)
register_handlers(EXTRA_HANDLERS)
register_handlers(INFO_HANDLERS)
register_handlers(RESOURCE_HANDLERS)

__all__ = ['ACTION_HANDLERS', 'ActionHandler', 'register_handlers']
