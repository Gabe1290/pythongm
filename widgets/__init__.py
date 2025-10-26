#!/usr/bin/env python3
"""
Widgets package for PyGameMaker IDE
"""

# Import main widgets
from .enhanced_properties_panel import EnhancedPropertiesPanel
from .event_actions import EventActionWidget
from .welcome_tab import WelcomeTab

# Aliases for compatibility
PropertiesPanel = EnhancedPropertiesPanel
EventActionsPanel = EventActionWidget

# Export all
__all__ = [
    'EnhancedPropertiesPanel',
    'EventActionWidget', 
    'WelcomeTab',
    'PropertiesPanel',  # Alias
    'EventActionsPanel',  # Alias
]