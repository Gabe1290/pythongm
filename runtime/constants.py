#!/usr/bin/env python3
"""
Runtime Constants

Centralized constants for the game runtime system.
These values define defaults for sprites, rooms, and game behavior.
"""

from typing import Tuple

# =============================================================================
# Sprite Defaults
# =============================================================================

DEFAULT_SPRITE_WIDTH: int = 32
"""Default width for sprites when image is missing."""

DEFAULT_SPRITE_HEIGHT: int = 32
"""Default height for sprites when image is missing."""

DEFAULT_SPRITE_SPEED: float = 10.0
"""Default animation speed for sprites (frames per second)."""

FALLBACK_SPRITE_COLOR: Tuple[int, int, int] = (255, 100, 100)
"""Color used for placeholder sprites (light red)."""

FALLBACK_SPRITE_BORDER: Tuple[int, int, int] = (0, 0, 0)
"""Border color for placeholder sprites (black)."""

# =============================================================================
# Room Defaults
# =============================================================================

DEFAULT_ROOM_WIDTH: int = 640
"""Default room width in pixels."""

DEFAULT_ROOM_HEIGHT: int = 480
"""Default room height in pixels."""

DEFAULT_WINDOW_WIDTH: int = 800
"""Default game window width in pixels."""

DEFAULT_WINDOW_HEIGHT: int = 600
"""Default game window height in pixels."""

DEFAULT_BACKGROUND_COLOR: Tuple[int, int, int] = (135, 206, 235)
"""Default background color (sky blue)."""

DEFAULT_BACKGROUND_HEX: str = "#87CEEB"
"""Default background color as hex string."""

# =============================================================================
# Grid & Movement Defaults
# =============================================================================

DEFAULT_GRID_SIZE: int = 32
"""Default grid size for snap-to-grid operations."""

DEFAULT_MOVE_STEPS: int = 30
"""Default number of steps for move_towards operations."""

# =============================================================================
# Animation Defaults
# =============================================================================

DEFAULT_FPS: int = 60
"""Default game framerate (frames per second)."""

MIN_ROOM_SPEED: int = 1
"""Minimum room speed (FPS)."""

MAX_ROOM_SPEED: int = 240
"""Maximum room speed (FPS)."""

DEFAULT_ROOM_SPEED: int = 30
"""Default room speed when not specified."""

# =============================================================================
# Auto-save Settings
# =============================================================================

DEFAULT_AUTO_SAVE_INTERVAL_MS: int = 30000
"""Default auto-save interval in milliseconds (30 seconds)."""

# =============================================================================
# Color Parsing Defaults
# =============================================================================

DEFAULT_DRAW_COLOR: Tuple[int, int, int] = (0, 0, 0)
"""Default drawing color (black)."""

DEFAULT_BLEND_COLOR: Tuple[int, int, int] = (255, 255, 255)
"""Default blend/tint color (white)."""

DEFAULT_FILL_COLOR: Tuple[int, int, int] = (0, 0, 0)
"""Default fill color (black)."""

# =============================================================================
# Effect Sizes
# =============================================================================

EFFECT_SIZE_MULTIPLIERS: dict = {
    'small': 0.5,
    'medium': 1.0,
    'large': 2.0,
}
"""Multipliers for effect sizes."""

# =============================================================================
# Score/Lives/Health Defaults
# =============================================================================

DEFAULT_LIVES: int = 3
"""Default number of lives."""

DEFAULT_HEALTH: int = 100
"""Default health value."""

MIN_HEALTH: int = 0
"""Minimum health value."""

MAX_HEALTH: int = 100
"""Maximum health value."""

# =============================================================================
# Alarm Limits
# =============================================================================

MAX_ALARMS: int = 12
"""Maximum number of alarms per instance (0-11)."""

# =============================================================================
# View Defaults
# =============================================================================

DEFAULT_VIEW_BORDER: int = 32
"""Default horizontal/vertical border for view following."""

MAX_VIEWS: int = 8
"""Maximum number of views per room."""
