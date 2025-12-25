#!/usr/bin/env python3
"""
Asset Tree Module for PyGameMaker IDE
Refactored asset tree components with better separation of concerns
"""

# Main widget and item classes
from .tree_main import AssetTreeWidget
from .asset_tree_item import AssetTreeItem

# Operations and dialogs
from .asset_operations import AssetOperations
from .asset_dialogs import AssetRenameDialog, AssetPropertiesDialog, CreateAssetDialog

# Utility functions - import commonly used ones at module level
from .asset_utils import (
    validate_asset_name,
    get_asset_icon_emoji,
    sanitize_asset_name,
    get_asset_display_name,
    create_asset_data_template,
    get_asset_categories,
    get_supported_file_extensions,
    get_asset_file_filter
)

# Version info
__version__ = "1.0.0"
__author__ = "PyGameMaker IDE Team"

# Main exports - these are the classes/functions that should be imported
# when someone does: from widgets.asset_tree import AssetTreeWidget, etc.
__all__ = [
    # Main classes
    'AssetTreeWidget',
    'AssetTreeItem',
    'AssetOperations',

    # Dialogs
    'AssetRenameDialog',
    'AssetPropertiesDialog',
    'CreateAssetDialog',

    # Common utility functions
    'validate_asset_name',
    'get_asset_icon_emoji',
    'sanitize_asset_name',
    'get_asset_display_name',
    'create_asset_data_template',
    'get_asset_categories',
    'get_supported_file_extensions',
    'get_asset_file_filter'
]

# Module-level convenience functions
def create_asset_tree_widget(parent=None):
    """
    Convenience function to create a fully configured AssetTreeWidget
    """
    return AssetTreeWidget(parent)

def validate_asset_name_simple(name: str) -> bool:
    """
    Simple boolean validation function
    Returns True if valid, False otherwise
    """
    is_valid, _ = validate_asset_name(name)
    return is_valid
