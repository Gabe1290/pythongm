#!/usr/bin/env python3
"""
Dialogs package for PyGameMaker IDE
"""

# Main dialogs
from .preferences_dialog import PreferencesDialog
from .auto_save_dialog import AutoSaveSettingsDialog

# Project dialogs (NewProjectDialog lives here — the standalone dialogs/new_project.py
# was an unused early prototype and has been removed)
from .project_dialogs import (
    NewProjectDialog,
    ProjectSettingsDialog,
    OpenProjectDialog,
    ExportProjectDialog
)

# Import dialogs
from .import_dialogs import ImportAssetsDialog

# Thymio dialogs
from .thymio_event_selector import ThymioEventSelector
from .thymio_action_selector import ThymioActionSelector
from .thymio_config_dialog import ThymioConfigDialog

# Export everything
__all__ = [
    'NewProjectDialog',
    'PreferencesDialog',
    'AutoSaveSettingsDialog',
    'ProjectSettingsDialog',
    'OpenProjectDialog',
    'ExportProjectDialog',
    'ImportAssetsDialog',
    'ThymioEventSelector',
    'ThymioActionSelector',
    'ThymioConfigDialog',
]
