#!/usr/bin/env python3
"""
Widgets package for PyGameMaker IDE
"""

# Import main widgets
from .enhanced_properties_panel import EnhancedPropertiesPanel
from .welcome_tab import WelcomeTab
from .thymio_diagram_widget import ThymioDiagramWidget

# ThymioPlaygroundWindow is imported lazily (on demand) to avoid
# setting SDL_VIDEODRIVER=dummy and importing pygame at IDE startup.
# Use: from widgets.thymio_playground import ThymioPlaygroundWindow

# Aliases for compatibility
PropertiesPanel = EnhancedPropertiesPanel

# Export all
__all__ = [
    'EnhancedPropertiesPanel',
    'WelcomeTab',
    'ThymioDiagramWidget',
    'ThymioPlaygroundWindow',
    'PropertiesPanel',  # Alias
]


def __getattr__(name):
    """Lazy import for ThymioPlaygroundWindow to avoid pygame init at startup."""
    if name == 'ThymioPlaygroundWindow':
        from .thymio_playground import ThymioPlaygroundWindow
        return ThymioPlaygroundWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
