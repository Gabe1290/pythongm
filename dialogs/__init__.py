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
]