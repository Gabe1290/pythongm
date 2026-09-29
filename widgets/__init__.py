#!/usr/bin/env python3
"""
Widgets package for PyGameMaker IDE
"""

# Import main widgets
from .enhanced_properties_panel import EnhancedPropertiesPanel
from .welcome_tab import WelcomeTab
from .thymio_diagram_widget import ThymioDiagramWidget

# ThymioPlaygroundWindow moved to extensions/thymio/playground_window.py
# (docs/THYMIO_EXTENSION_PLAN.md, Stage C3b).
# Use: from extensions.thymio.playground_window import ThymioPlaygroundWindow

# Aliases for compatibility
PropertiesPanel = EnhancedPropertiesPanel

# Export all
__all__ = [
    'EnhancedPropertiesPanel',
    'WelcomeTab',
    'ThymioDiagramWidget',
    'PropertiesPanel',  # Alias
]
