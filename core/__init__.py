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

# Import logging first - this is always safe (no GUI dependencies)
from .logger import get_logger, configure_logging, enable_debug, disable_debug

# Package version
__version__ = "1.0.0-rc.1"

from typing import Any, Dict, Optional, Type

# Lazy imports for GUI components to avoid import errors when running without PySide6
# (e.g., during game runtime, testing, or headless operation)
def _lazy_import_gui() -> Optional[Type[Any]]:
    """Import GUI components. Call this only when you need the IDE.

    Returns:
        PyGameMakerIDE class or None if import fails
    """
    global PyGameMakerIDE
    from .ide_window import PyGameMakerIDE
    return PyGameMakerIDE

def _lazy_import_event_system() -> Dict[str, Any]:
    """Import event system components.

    Returns:
        Dictionary of event system classes and singletons
    """
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
    return {
        'EventSystem': EventSystem,
        'EventType': EventType,
        'ActionCategory': ActionCategory,
        'ActionDefinition': ActionDefinition,
        'EventAction': EventAction,
        'GameEvent': GameEvent,
        'ActionRegistry': ActionRegistry,
        'event_system': event_system,
        'get_event_system': get_event_system,
        'get_action_registry': get_action_registry,
    }

# Try to import GUI components immediately if PySide6 is available
# This maintains backward compatibility with existing code
try:
    from .ide_window import PyGameMakerIDE
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
    _GUI_AVAILABLE = True
except ImportError:
    # PySide6 not available - GUI imports will fail if accessed
    _GUI_AVAILABLE = False
    PyGameMakerIDE = None  # type: ignore
    EventSystem = None  # type: ignore
    EventType = None  # type: ignore
    ActionCategory = None  # type: ignore
    ActionDefinition = None  # type: ignore
    EventAction = None  # type: ignore
    GameEvent = None  # type: ignore
    ActionRegistry = None  # type: ignore
    event_system = None  # type: ignore
    get_event_system = None  # type: ignore
    get_action_registry = None  # type: ignore

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
    'disable_debug',
    '_GUI_AVAILABLE',
    '_lazy_import_gui',
    '_lazy_import_event_system',
]
