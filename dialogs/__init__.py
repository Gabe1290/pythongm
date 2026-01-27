#!/usr/bin/env python3
"""
Dialogs package for PyGameMaker IDE
"""

# Main dialogs
from .new_project import NewProjectDialog
from .about import AboutDialog
from .preferences_dialog import PreferencesDialog
from .auto_save_dialog import AutoSaveSettingsDialog

# Project dialogs
from .project_dialogs import (
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
    'AboutDialog',
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
