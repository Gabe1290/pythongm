#!/usr/bin/env python3
"""
Action Handlers Package

This package contains modular action handlers organized by category.
Each handler module exports a dictionary of action_name -> handler_function mappings.

The ActionExecutor auto-discovers and registers all handlers from this package.
Any action name already covered by an ``ActionExecutor.execute_*_action`` method
takes priority and the modular handler for it is skipped (see
``ActionExecutor._register_action_handlers`` Phase 2).

Only the handful of handlers below have a real producer (the IDE action
palette / Blockly config / the Python code parser / bundled samples); the
category modules whose actions had no producer anywhere were removed
2026-09-03 as part of the ``docs/POST_1_0_REFACTOR.md`` teardown.
"""

from typing import Dict, Callable, Any

# Type alias for action handler functions
ActionHandler = Callable[[Any, Any, Dict[str, Any]], Any]

# Registry of all handlers - populated by imports below
ACTION_HANDLERS: Dict[str, ActionHandler] = {}


def register_handlers(handlers: Dict[str, ActionHandler]) -> None:
    """Register a dictionary of action handlers"""
    ACTION_HANDLERS.update(handlers)


# Import the live handler modules - each registers its handlers
from runtime.action_handlers.movement_handlers import MOVEMENT_HANDLERS
from runtime.action_handlers.control_handlers import CONTROL_HANDLERS
from runtime.action_handlers.variable_handlers import VARIABLE_HANDLERS
from runtime.action_handlers.sound_handlers import SOUND_HANDLERS

# Register all handlers
register_handlers(MOVEMENT_HANDLERS)
register_handlers(CONTROL_HANDLERS)
register_handlers(VARIABLE_HANDLERS)
register_handlers(SOUND_HANDLERS)

__all__ = ['ACTION_HANDLERS', 'ActionHandler', 'register_handlers']
