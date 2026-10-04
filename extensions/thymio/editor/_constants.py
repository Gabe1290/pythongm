#!/usr/bin/env python3
"""Shared constants for :class:`ThymioPlaygroundWindow` and its mixins.

Extracted verbatim from ``extensions/thymio/playground_window.py``
(``docs/PROJECT_STATUS.md``'s Thymio-extraction follow-up: splitting that
1,249-line window into mixins). Lives in its own module, not in the
window's own file, because the window imports its mixins at class-
definition time and several mixins need these constants -- importing them
back from ``playground_window`` would be a circular import (the window
module would still be mid-import, with these names not yet bound, at the
point a mixin tried to import them).
"""
from enum import Enum, auto

# Playground constants
DEFAULT_PLAYGROUND_WIDTH = 800
DEFAULT_PLAYGROUND_HEIGHT = 600
FPS = 60

# Size presets (name, width, height)
SIZE_PRESETS = [
    ("Small (400x300)", 400, 300),
    ("Medium (800x600)", 800, 600),
    ("Large (1200x900)", 1200, 900),
    ("Wide (1000x500)", 1000, 500),
    ("Square (600x600)", 600, 600),
]

# Colors
COLOR_BACKGROUND = (240, 240, 240)  # Light gray
COLOR_OBSTACLE = (100, 80, 80)       # Dark red-brown
COLOR_LINE = (30, 30, 30)            # Near black for line following
COLOR_GRID = (220, 220, 220)         # Light gray grid
COLOR_SELECTION = (0, 120, 255)      # Blue selection highlight
COLOR_PREVIEW = (100, 100, 255, 128) # Semi-transparent preview

# Minimum size for obstacles/lines
MIN_ELEMENT_SIZE = 10


class EditMode(Enum):
    """Edit modes for the playground"""
    SELECT = auto()      # Select and move/delete elements
    OBSTACLE = auto()    # Place rectangular obstacles
    LINE = auto()        # Draw line segments for line following
