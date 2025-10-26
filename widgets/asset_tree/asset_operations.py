#!/usr/bin/env python3
"""
Asset Operations for PyGameMaker IDE
Handles all asset file operations: import, delete, rename, and project file management
"""

import json
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from PySide6.QtWidgets import QMessageBox, QInputDialog, QDialog
from PySide6.QtCore import Qt

from .asset_dialogs import AssetRenameDialog
from .asset_utils import validate_asset_name, load_project_data, save_project_data


class AssetOperations:
    """Handles all asset file operations - separated from UI concerns"""
    
    def __init__(self, tree_widget):
        self.tree = tree_widget
    
    def import_asset(self, files: List[str], asset_type: str, project_path: str) -> bool:
        """Import asset files into the project using AssetManager"""
        if not project_path or not files:
            return False
        
        # Get AssetManager from parent IDE window
        asset_manager = self._get_asset_manager()
        if not asset_manager:
            print("❌ No AssetManager available")
            QMessageBox.warning(
                self.tree,
                "Import Error",
                "Asset manager is not available. Cannot import assets."
            )
            return False
        
        success_count = 0
        
        for file_path in files:
            try:
                file_path_obj = Path(file_path)
                
                # Use AssetManager to import (this updates the cache automatically)
                asset_data = asset_manager.import_asset(file_path_obj, asset_type)
                
                if asset_data:
                    asset_name = asset_data['name']
                    
                    # Add to tree UI
                    self.tree.add_asset(asset_type, asset_name, asset_data)
                    print(f"✅ Imported {asset_type}: {asset_name}")
                    
                    # Emit signal for UI updates
                    self.tree.asset_imported.emit(asset_name, asset_type, asset_data)
                    print(f"📢 Emitted asset_imported signal for {asset_name}")
                    
                    success_count += 1
                else:
                    print(f"❌ AssetManager failed to import {file_path_obj.name}")
                    
            except Exception as e:
                print(f"❌ Error importing {file_path}: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.warning(
                    self.tree,
                    "Import Error",
                    f"Failed to import {Path(file_path).name}: {str(e)}"
                )
        
        return success_count > 0

    def _get_asset_manager(self):
        """Get AssetManager from parent IDE window"""
        try:
            # Traverse up to find the main IDE window
            parent = self.tree.parent()
            while parent:
                if hasattr(parent, 'asset_manager'):
                    return parent.asset_manager
                parent = parent.parent()
            
            # Alternative: Check if tree has project_manager with asset_manager
            if hasattr(self.tree, 'project_manager') and self.tree.project_manager:
                if hasattr(self.tree.project_manager, 'asset_manager'):
                    return self.tree.project_manager.asset_manager
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting AssetManager: {e}")
            return None
    
    def delete_asset(self, item) -> bool:
        """Delete an asset from both UI and project data"""
        from .asset_tree_item import AssetTreeItem
        
        print("🎯 DELETE_ASSET METHOD CALLED!")
        
        # Work with AssetTreeItem directly
        if not isinstance(item, AssetTreeItem):
            print("❌ Not an AssetTreeItem")
            return False
            
        if item.is_category:
            print("❌ Cannot delete category")
            return False
        
        asset_name = item.asset_name
        asset_category = item.asset_type
        
        print(f"🗑️ DELETE REQUEST: {asset_category}/{asset_name}")
        
        # CHECK: If this is a room, see if it's open in an editor
        parent = self.tree.parent()
        while parent and not hasattr(parent, 'open_editors'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'open_editors'):
            if asset_name in parent.open_editors:
                # Close the editor first
                print(f"⚠️ Asset is open in editor, closing it first...")
                parent.close_editor_by_name(asset_name)
        
        # Confirm deletion with user
        reply = QMessageBox.question(
            self.tree,
            "Delete Asset",
            f"Are you sure you want to delete '{asset_name}' from {asset_category}?\n\nThis will permanently remove the asset and its file.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            print("❌ User cancelled deletion")
            return False
        
        try:
            # Step 1: Remove from project data and file first
            success = self.remove_asset_from_project(asset_category, asset_name)
            
            if success:
                # Step 2: Remove from UI tree
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                    print(f"✅ Removed {asset_name} from UI")
                
                # Step 3: Force refresh to sync everything
                self.tree.force_project_refresh()
                
                # Step 4: Emit signal for other components
                self.tree.assetDeleted.emit(asset_category, asset_name)
                
                print(f"🎉 Successfully deleted: {asset_category}/{asset_name}")
                return True
            else:
                print(f"❌ Failed to delete {asset_name} from project data")
                return False
                
        except Exception as e:
            print(f"❌ Error during deletion: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self.tree,
                "Deletion Error", 
                f"Failed to delete asset: {str(e)}"
            )
            return False
    
    def rename_asset(self, item) -> bool:
        """Rename an asset with complete data update"""
        from .asset_tree_item import AssetTreeItem
        
        if not isinstance(item, AssetTreeItem):
            return False
            
        try:
            asset_data = item.asset_data
            current_name = asset_data['name']
            asset_type = asset_data['asset_type']
            
            print(f"📝 Renaming {asset_type}: {current_name}")
            
            # Show rename dialog
            dialog = AssetRenameDialog(current_name, asset_type, self.tree)
            
            if dialog.exec() != QDialog.Accepted or not dialog.new_name:
                print("❌ Rename cancelled")
                return False
                
            new_name = dialog.new_name
            
            # Validate new name
            is_valid, error_msg = validate_asset_name(new_name)
            if not is_valid:
                QMessageBox.warning(self.tree, "Invalid Name", error_msg)
                return False
            
            # Check if new name already exists
            if self.asset_name_exists(new_name, asset_type):
                QMessageBox.warning(self.tree, "Name Conflict", 
                                f"An asset named '{new_name}' already exists.\n"
                                f"Please choose a different name.")
                return False
            
            # Perform the rename
            success = self.perform_asset_rename(asset_data, new_name)
            
            if success:
                # Get the updated asset data from the project file
                updated_asset_data = self.get_updated_asset_data(new_name, asset_type)
                
                if updated_asset_data:
                    # Update the tree item with ALL the new data (including file paths)
                    item.asset_data = updated_asset_data
                    item.asset_name = new_name
                    
                    # Refresh the visual representation
                    self.refresh_asset_item_after_rename(item, new_name)
                    
                    print(f"✅ Asset renamed: {current_name} → {new_name}")
                    print(f"🔗 Updated paths: {updated_asset_data.get('project_path', 'No path')}")
                    
                    # Emit signal for UI refresh
                    self.tree.asset_renamed.emit(current_name, new_name, asset_type)
                    return True
                else:
                    print("❌ Failed to get updated asset data")
                    return False
                    
            else:
                QMessageBox.critical(self.tree, "Rename Failed", 
                                f"Failed to rename asset '{current_name}'.\n"
                                f"Please check the console for details.")
                return False
                
        except Exception as e:
            print(f"❌ Error renaming asset: {e}")
            QMessageBox.critical(self.tree, "Error", f"Error renaming asset: {e}")
            return False
    
    def remove_asset_from_project(self, asset_category: str, asset_name: str) -> bool:
        """Remove asset from project data and save to file"""
        print(f"🗑️ Removing {asset_category}/{asset_name} from project data...")
        
        # Find the project.json file
        project_file = Path(self.tree.project_path) / "project.json"
        
        if not project_file.exists():
            print(f"❌ Project file not found: {project_file}")
            return False
        
        try:
            print(f"🔍 Modifying project file: {project_file}")
            
            # Load current project data
            project_data = load_project_data(project_file)
            if not project_data:
                return False
            
            # Check if asset exists in data
            assets = project_data.get('assets', {})
            if asset_category not in assets:
                print(f"❌ Category {asset_category} not found")
                return False
                
            if asset_name not in assets[asset_category]:
                print(f"❌ Asset {asset_name} not found in {asset_category}")
                return False
            
            # Get asset info before deleting
            asset_data = assets[asset_category][asset_name]
            print(f"📄 Found asset data: {asset_data.get('project_path', 'No path')}")
            
            # Delete physical file if it exists
            if 'project_path' in asset_data:
                file_path = Path(asset_data['project_path'])
                if file_path.exists():
                    file_path.unlink()
                    print(f"🗑️ Deleted file: {file_path}")
            
            # Remove from project data
            del assets[asset_category][asset_name]
            print(f"✅ Removed {asset_name} from project data")
            
            # CRITICAL: Also remove from AssetManager cache
            parent = self.tree.parent()
            while parent and not hasattr(parent, 'asset_manager'):
                parent = parent.parent()

            if parent and hasattr(parent, 'asset_manager'):
                asset_manager = parent.asset_manager
                if hasattr(asset_manager, 'assets_cache'):
                    if asset_category in asset_manager.assets_cache:
                        if asset_name in asset_manager.assets_cache[asset_category]:
                            del asset_manager.assets_cache[asset_category][asset_name]
                            print(f"✅ Removed {asset_name} from AssetManager cache")

            # Save modified data back to file
            if save_project_data(project_file, project_data):
                print(f"💾 Saved changes to project.json")
                
                # Verify the save worked
                verify_data = load_project_data(project_file)
                if verify_data:
                    verify_assets = verify_data.get('assets', {}).get(asset_category, {})
                    if asset_name in verify_assets:
                        print(f"❌ SAVE FAILED: {asset_name} still in file!")
                        return False
                    else:
                        print(f"✅ VERIFIED: {asset_name} successfully removed from project.json")
                        return True
                return False
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error during deletion: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def perform_asset_rename(self, asset_data: Dict, new_name: str) -> bool:
        """Perform the actual asset rename operation"""
        try:
            project_path = Path(self.tree.project_path)
            project_file = project_path / "project.json"
            
            if not project_file.exists():
                print(f"❌ Project file not found: {project_file}")
                return False
            
            # Load project data
            project_data = load_project_data(project_file)
            if not project_data:
                return False
            
            current_name = asset_data['name']
            asset_type = asset_data['asset_type']
            
            # Get the correct category name (plural)
            category = asset_type + 's' if not asset_type.endswith('s') else asset_type
            
            if category not in project_data.get('assets', {}):
                print(f"❌ Asset category not found: {category}")
                return False
            
            assets = project_data['assets'][category]
            
            if current_name not in assets:
                print(f"❌ Asset not found in project: {current_name}")
                return False
            
            # Get the asset data
            asset_info = assets[current_name].copy()
            
            # Update the asset name in the data
            asset_info['name'] = new_name
            
            # Handle file renaming if the asset has an actual file
            old_file_path = asset_info.get('project_path')
            if old_file_path:
                old_file = Path(old_file_path)
                if old_file.exists():
                    # Create new file path
                    new_file_name = new_name + old_file.suffix
                    new_file_path = old_file.parent / new_file_name
                    
                    # Rename the actual file
                    try:
                        shutil.move(str(old_file), str(new_file_path))
                        print(f"🔗 File renamed: {old_file.name} → {new_file_path.name}")
                        
                        # Update file paths in asset data
                        asset_info['project_path'] = str(new_file_path)
                        if 'file_path' in asset_info:
                            # Update relative path
                            relative_path = new_file_path.relative_to(project_path)
                            asset_info['file_path'] = str(relative_path)
                            
                    except Exception as e:
                        print(f"❌ Error renaming file: {e}")
                        return False
            
            # Remove old asset entry and add new one
            del assets[current_name]
            assets[new_name] = asset_info
            
            # Save the updated project file
            if save_project_data(project_file, project_data):
                print(f"💾 Project file updated with renamed asset")
                return True
            else:
                return False
            
        except Exception as e:
            print(f"❌ Error performing asset rename: {e}")
            return False
    
    def get_updated_asset_data(self, asset_name: str, asset_type: str) -> Optional[Dict]:
        """Get the updated asset data from the project file after rename"""
        try:
            project_file = Path(self.tree.project_path) / "project.json"
            if not project_file.exists():
                return None
            
            project_data = load_project_data(project_file)
            if not project_data:
                return None
            
            # Get the plural form for the category
            category = asset_type + 's' if not asset_type.endswith('s') else asset_type
            assets = project_data.get('assets', {}).get(category, {})
            
            return assets.get(asset_name)
            
        except Exception as e:
            print(f"❌ Error getting updated asset data: {e}")
            return None
    
    def asset_name_exists(self, name: str, asset_type: str) -> bool:
        """Check if an asset name already exists in the same category"""
        try:
            project_file = Path(self.tree.project_path) / "project.json"
            if not project_file.exists():
                return False
            
            project_data = load_project_data(project_file)
            if not project_data:
                return False
            
            # Get the plural form for the category
            category = asset_type + 's' if not asset_type.endswith('s') else asset_type
            assets = project_data.get('assets', {}).get(category, {})
            
            return name in assets
            
        except Exception as e:
            print(f"❌ Error checking asset name: {e}")
            return False
    
    def refresh_asset_item_after_rename(self, item, new_name: str):
        """Refresh the asset item's visual representation after rename"""
        try:
            asset_data = item.asset_data
            asset_type = asset_data.get('asset_type', '')
            
            print(f"🔄 Refreshing asset item visual for: {new_name}")
            
            # Update the asset name in the data
            item.asset_name = new_name
            
            # Use the SAME text-based emoji approach as setup_item()
            if asset_type == "sprite":
                item.setText(0, f"🖼️ {new_name}")
            elif asset_type == "sound":
                item.setText(0, f"🔊 {new_name}")
            elif asset_type == "background":
                item.setText(0, f"🖼️ {new_name}")
            elif asset_type == "object":
                item.setText(0, f"⚙️ {new_name}")
            elif asset_type == "room":
                item.setText(0, f"🏠 {new_name}")
            elif asset_type == "script":
                item.setText(0, f"📜 {new_name}")
            elif asset_type == "font":
                item.setText(0, f"🔤 {new_name}")
            else:
                item.setText(0, new_name)
            
            print(f"✅ Asset item text refreshed for: {new_name}")
            
        except Exception as e:
            print(f"❌ Error refreshing asset item visual: {e}")
    
    def save_asset_to_project(self, asset_name: str, asset_type: str, asset_data: Dict, project_path: str) -> bool:
        """Save asset data to project.json file"""
        try:
            project_file = Path(project_path) / "project.json"
            
            # Load existing project data
            project_data = load_project_data(project_file)
            if project_data is None:
                project_data = {"assets": {}}
            
            # Ensure assets structure exists
            if "assets" not in project_data:
                project_data["assets"] = {}
            
            # Ensure asset type category exists (use plural form)
            if asset_type not in project_data["assets"]:
                project_data["assets"][asset_type] = {}
            
            # Add the asset
            project_data["assets"][asset_type][asset_name] = asset_data
            
            # Save back to file
            if save_project_data(project_file, project_data):
                print(f"✅ Successfully saved asset {asset_name} to project.json")
                return True
            else:
                return False
            
        except Exception as e:
            print(f"❌ ERROR in save_asset_to_project: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_asset_manager_cache(self, asset_name: str, asset_type: str, asset_data: Dict):
        """Update the asset manager's cache - simplified version"""
        print(f"Cache update for {asset_name} - skipping (not required)")
        # Asset import works fine without cache updates
        # This method exists for compatibility but doesn't need to do anything
        pass