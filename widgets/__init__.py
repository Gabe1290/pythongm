#!/usr/bin/env python3
"""
Widgets package for PyGameMaker IDE
"""

# Import main widgets
from .enhanced_properties_panel import EnhancedPropertiesPanel
from .welcome_tab import WelcomeTab

# ThymioPlaygroundWindow moved to extensions/thymio/playground_window.py
# (docs/THYMIO_EXTENSION_PLAN.md, Stage C3b); ThymioDiagramWidget moved to
# extensions/thymio/diagram_widget.py (Stage C4).
# Use: from extensions.thymio.playground_window import ThymioPlaygroundWindow
# Use: from extensions.thymio.diagram_widget import ThymioDiagramWidget

# Aliases for compatibility
PropertiesPanel = EnhancedPropertiesPanel

# Export all
__all__ = [
    'EnhancedPropertiesPanel',
    'WelcomeTab',
    'PropertiesPanel',  # Alias
]
