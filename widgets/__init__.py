#!/usr/bin/env python3
"""
Widgets package for PyGameMaker IDE
"""

# Import main widgets
from .enhanced_properties_panel import EnhancedPropertiesPanel
from .event_actions import EventActionWidget
from .welcome_tab import WelcomeTab
from .thymio_diagram_widget import ThymioDiagramWidget
from .thymio_playground import ThymioPlaygroundWindow

# Aliases for compatibility
PropertiesPanel = EnhancedPropertiesPanel
EventActionsPanel = EventActionWidget

# Export all
__all__ = [
    'EnhancedPropertiesPanel',
    'EventActionWidget',
    'WelcomeTab',
    'ThymioDiagramWidget',
    'ThymioPlaygroundWindow',
    'PropertiesPanel',  # Alias
    'EventActionsPanel',  # Alias
]
