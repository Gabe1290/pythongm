#!/usr/bin/env python3
# ==============================================================================
# CORE PACKAGE: core/__init__.py
# Location: /project_root/core/__init__.py
# ==============================================================================
"""
Location: core/__init__.py

Core functionality and business logic:
- Project management
- File I/O operations
- Configuration management
- Event system
- Visual programming logic
"""

# Import logging first
from .logger import get_logger, configure_logging, enable_debug, disable_debug

# Import main IDE window
from .ide_window import PyGameMakerIDE

# Import event system components
from .event_system import (
    EventSystem,
    EventType,
    ActionCategory,
    ActionDefinition,
    EventAction,
    GameEvent,
    ActionRegistry,
    event_system,
    get_event_system,
    get_action_registry
)

# Package version
__version__ = "1.0.0-rc.1"

# Export main components
__all__ = [
    'PyGameMakerIDE',
    'EventSystem',
    'EventType',
    'ActionCategory',
    'ActionDefinition',
    'EventAction',
    'GameEvent',
    'ActionRegistry',
    'event_system',
    'get_event_system',
    'get_action_registry',
    'get_logger',
    'configure_logging',
    'enable_debug',
    'disable_debug'
]
