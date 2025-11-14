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

# Package version
__version__ = "1.0.0"

# Lazy imports to avoid loading Qt during test collection
def __getattr__(name):
    if name == 'PyGameMakerIDE':
        from .ide_window import PyGameMakerIDE
        return PyGameMakerIDE
    elif name in ('EventSystem', 'EventType', 'ActionCategory', 'ActionDefinition',
                   'EventAction', 'GameEvent', 'ActionRegistry', 'event_system',
                   'get_event_system', 'get_action_registry'):
        from . import event_system as es_module
        return getattr(es_module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
    'get_action_registry'
]
