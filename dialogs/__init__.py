#!/usr/bin/env python3
"""
Dialogs package for PyGameMaker IDE
"""

# Main dialogs
from .preferences_dialog import PreferencesDialog
from .auto_save_dialog import AutoSaveSettingsDialog

# Project dialogs (NewProjectDialog lives here — the standalone dialogs/new_project.py
# was an unused early prototype and has been removed; ExportProjectDialog
# was retired 2026-07-12 in favour of the registry-driven export dialog)
from .project_dialogs import (
    NewProjectDialog,
    ProjectSettingsDialog,
)

# Import dialogs
from .import_dialogs import ImportAssetsDialog

# Thymio dialogs moved to extensions/thymio/dialogs/
# (docs/THYMIO_EXTENSION_PLAN.md, Stage C6).
# Use: from extensions.thymio.dialogs.thymio_event_selector import ThymioEventSelector
# Use: from extensions.thymio.dialogs.thymio_action_selector import ThymioActionSelector
# Use: from extensions.thymio.dialogs.thymio_config_dialog import ThymioConfigDialog

# Export everything
__all__ = [
    'NewProjectDialog',
    'PreferencesDialog',
    'AutoSaveSettingsDialog',
    'ProjectSettingsDialog',
    'ImportAssetsDialog',
]
