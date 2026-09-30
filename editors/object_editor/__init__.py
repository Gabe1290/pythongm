#!/usr/bin/env python3
"""
Object Editor Package
"""

from .object_editor_main import ObjectEditor
from .object_properties_panel import ObjectPropertiesPanel
from .events import ObjectEventsPanel
from .object_actions_formatter import ActionParametersFormatter

# The Thymio events panel moved to extensions/thymio/object_editor_panel.py
# (docs/THYMIO_EXTENSION_PLAN.md, Stage E1).
# Use: from extensions.thymio.object_editor_panel import ThymioEventsPanel

__all__ = [
    'ObjectEditor',
    'ObjectPropertiesPanel',
    'ObjectEventsPanel',
    'ActionParametersFormatter',
]
