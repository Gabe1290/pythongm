#!/usr/bin/env python3
"""
Dialogs package for PyGameMaker IDE - Comprehensive version
Contains dialog windows for various IDE operations
"""

# Main dialogs
from .new_project import NewProjectDialog
from .asset_import import AssetImportDialog
from .preferences import PreferencesDialog
from .about import AboutDialog

# Project dialogs
from .project_dialogs import (
    ProjectSettingsDialog,
    OpenProjectDialog, 
    ExportProjectDialog
)

# Import dialogs
from .import_dialogs import ImportAssetsDialog

# Try to import optional dialog modules
try:
    from .sprite_dialogs import SpriteImportDialog, SpriteEditorDialog
except ImportError:
    class SpriteImportDialog: pass
    class SpriteEditorDialog: pass

try:
    from .object_dialogs import ObjectEditorDialog, EventEditorDialog
except ImportError:
    class ObjectEditorDialog: pass
    class EventEditorDialog: pass

try:
    from .room_dialogs import RoomEditorDialog, RoomSettingsDialog
except ImportError:
    class RoomEditorDialog: pass
    class RoomSettingsDialog: pass

try:
    from .export_dialogs import GameExportDialog, BuildSettingsDialog
except ImportError:
    class GameExportDialog: pass
    class BuildSettingsDialog: pass

# Export everything
__all__ = [
    'NewProjectDialog', 'AssetImportDialog', 'PreferencesDialog', 'AboutDialog',
    'ProjectSettingsDialog', 'OpenProjectDialog', 'ExportProjectDialog',
    'ImportAssetsDialog', 'SpriteImportDialog', 'SpriteEditorDialog',
    'ObjectEditorDialog', 'EventEditorDialog', 'RoomEditorDialog', 
    'RoomSettingsDialog', 'GameExportDialog', 'BuildSettingsDialog'
]
