"""
PyGameMaker Runtime System

Handles game execution and testing. The runtime package provides:
- GameRunner: Main game loop and rendering
- ActionExecutor: Executes game actions
- CollisionMixin: Collision detection utilities
- InputMixin: Keyboard and mouse input handling
- constants: Centralized game defaults

Note: GameRunner requires pygame and is lazily imported to allow
action_executor and action_handlers to be imported without pygame.
"""

from typing import Any, Optional, Type

# Import constants (always safe, no pygame dependency)
from .constants import (
    DEFAULT_SPRITE_WIDTH,
    DEFAULT_SPRITE_HEIGHT,
    DEFAULT_ROOM_WIDTH,
    DEFAULT_ROOM_HEIGHT,
    DEFAULT_GRID_SIZE,
    DEFAULT_FPS,
)

# Lazy import to avoid requiring pygame for action_executor imports
try:
    from .game_runner import GameRunner
    _PYGAME_AVAILABLE = True
except ImportError:
    GameRunner: Optional[Type[Any]] = None  # type: ignore
    _PYGAME_AVAILABLE = False

# These can be imported without pygame
try:
    from .collision_system import CollisionMixin, get_bounding_box, boxes_overlap
except ImportError:
    CollisionMixin = None  # type: ignore
    get_bounding_box = None  # type: ignore
    boxes_overlap = None  # type: ignore

try:
    from .input_handler import InputMixin
except ImportError:
    InputMixin = None  # type: ignore

__all__ = [
    # Main classes
    'GameRunner',
    # Mixins
    'CollisionMixin',
    'InputMixin',
    # Utilities
    'get_bounding_box',
    'boxes_overlap',
    # Constants
    'DEFAULT_SPRITE_WIDTH',
    'DEFAULT_SPRITE_HEIGHT',
    'DEFAULT_ROOM_WIDTH',
    'DEFAULT_ROOM_HEIGHT',
    'DEFAULT_GRID_SIZE',
    'DEFAULT_FPS',
    # Flags
    '_PYGAME_AVAILABLE',
]
