#!/usr/bin/env python3
"""
Asset Tree Widget for PyGameMaker IDE
Main tree widget for displaying and managing game assets in a hierarchical structure
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Optional
from PySide6.QtWidgets import (QTreeWidget, QMenu, QMessageBox, QInputDialog,
                               QDialog, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QLabel)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from .asset_tree_item import AssetTreeItem


class AssetTreeWidget(QTreeWidget):
    """Main asset tree widget for the PyGameMaker IDE"""
    
    # Signals
    assetSelected = Signal(dict)
    assetDoubleClicked = Signal(dict)
    assetImported = Signal(str, str, dict)
    assetDeleted = Signal(str, str)
    assetRenamed = Signal(str, str, str) # old_name, new_name, asset_type
    
    # camelCase aliases for signals
    asset_selected = assetSelected
    asset_double_clicked = assetDoubleClicked
    asset_imported = assetImported
    asset_deleted = assetDeleted
    asset_renamed = assetRenamed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_path = None
        self.project_manager = None
        self.current_project = None
        
        self.setup_ui()
        self.setup_categories()
        self.setup_connections()

        self.setHeaderLabel("Assets")

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        print("🔧 AssetTreeWidget: Context menu enabled")

    def show_context_menu(self, position):
        """Show right-click context menu for asset management"""
        print(f"🖱️  Context menu requested at position: {position}") 

        item = self.itemAt(position)
        
        if not item:
            print("❌ No item found at click position")
            return
        
        if not hasattr(item, 'asset_data'):
            print("❌ No asset_data found at click position")
            return

        # Check if this is an AssetTreeItem and not a category
        if not isinstance(item, AssetTreeItem):
            print("❌ Not an AssetTreeItem")
            return
            
        if item.is_category:
            print("ℹ️  Right-clicked on category, no deletion allowed")
            return  # Don't allow deletion of categories
        
        print(f"🖱️  Right-click on asset: {item.asset_name} (type: {item.asset_type})")

        # Create context menu
        context_menu = QMenu(self)
        
        # Add delete option for assets
        delete_action = QAction("🗑️ Delete Asset", self)
        delete_action.triggered.connect(lambda: self.delete_asset(item))
        context_menu.addAction(delete_action)

        # Add inspect option for debugging
        inspect_action = QAction("🔍 Inspect Asset", self)
        inspect_action.triggered.connect(lambda: self.show_asset_properties_simple(item))
        context_menu.addAction(inspect_action)

        # Add rename option for assets
        rename_action = QAction("✏️ Rename Asset", self)
        rename_action.triggered.connect(lambda: self.rename_asset(item))
        context_menu.addAction(rename_action)

        context_menu.addSeparator()
        
        properties_action = QAction("⚙️ Properties...", self)
        properties_action.triggered.connect(lambda: self.show_asset_properties_simple(item))
        context_menu.addAction(properties_action)

        print(f"📋 Showing context menu with {len(context_menu.actions())} options")
        context_menu.exec(self.mapToGlobal(position))

    def delete_asset(self, item):
        """Delete an asset from both UI and project data"""
        print(f"🎯 DELETE_ASSET METHOD CALLED!")
        
        # Work with AssetTreeItem directly
        if not isinstance(item, AssetTreeItem):
            print("❌ Not an AssetTreeItem")
            return
            
        if item.is_category:
            print("❌ Cannot delete category")
            return
        
        asset_name = item.asset_name
        asset_category = item.asset_type
        
        print(f"🗑️ DELETE REQUEST: {asset_category}/{asset_name}")
        
        # Confirm deletion with user
        reply = QMessageBox.question(
            self,
            "Delete Asset",
            f"Are you sure you want to delete '{asset_name}' from {asset_category}?\n\nThis will permanently remove the asset and its file.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            print("❌ User cancelled deletion")
            return
        
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
                self.force_project_refresh()
                
                # Step 4: Emit signal for other components
                self.assetDeleted.emit(asset_category, asset_name)
                
                print(f"🎉 Successfully deleted: {asset_category}/{asset_name}")
            else:
                print(f"❌ Failed to delete {asset_name} from project data")
                
        except Exception as e:
            print(f"❌ Error during deletion: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Deletion Error", 
                f"Failed to delete asset: {str(e)}"
            )

    def remove_asset_from_project(self, asset_category, asset_name):
        """Remove asset from project data and save to file - WORKING VERSION"""
        print(f"🗑️ Removing {asset_category}/{asset_name} from project data...")
        
        # Skip unreliable ProjectManager - go straight to direct file approach
        from pathlib import Path
        import json
        
        # Find the project.json file
        project_file = Path.home() / "Documents" / "PyGameMaker Projects" / "project.json"
        
        if not project_file.exists():
            print(f"❌ Project file not found: {project_file}")
            return False
        
        try:
            print(f"🔍 Modifying project file: {project_file}")
            
            # Load current project data
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
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
            
            # Save modified data back to file
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved changes to project.json")
            
            # Verify the save worked by reading the file back
            with open(project_file, 'r', encoding='utf-8') as f:
                verify_data = json.load(f)
            
            verify_assets = verify_data.get('assets', {}).get(asset_category, {})
            if asset_name in verify_assets:
                print(f"❌ SAVE FAILED: {asset_name} still in file!")
                return False
            else:
                print(f"✅ VERIFIED: {asset_name} successfully removed from project.json")
                return True
                
        except Exception as e:
            print(f"❌ Error during deletion: {e}")
            import traceback
            traceback.print_exc()
            return False

    def show_asset_properties_simple(self, item):
        """Simple asset properties for AssetTreeItem"""
        if isinstance(item, AssetTreeItem):
            QMessageBox.information(
                self, 
                "Asset Properties", 
                f"Asset: {item.asset_name}\n"
                f"Type: {item.asset_type}\n"
                f"Imported: {item.asset_data.get('imported', False)}\n\n"
                "Detailed properties dialog will be implemented soon."
            )

    def rename_asset(self, item):
        """Rename an asset with complete data update"""
        try:
            asset_data = item.asset_data
            current_name = asset_data['name']
            asset_type = asset_data['asset_type']
            
            print(f"📝 Renaming {asset_type}: {current_name}")
            
            # Show rename dialog
            dialog = AssetRenameDialog(current_name, asset_type, self)
            
            if dialog.exec_() != QDialog.Accepted or not dialog.new_name:
                print("❌ Rename cancelled")
                return
                
            new_name = dialog.new_name
            
            # Check if new name already exists
            if self.asset_name_exists(new_name, asset_type):
                QMessageBox.warning(self, "Name Conflict", 
                                f"An asset named '{new_name}' already exists.\n"
                                f"Please choose a different name.")
                return
            
            # Perform the rename
            success = self.perform_asset_rename(asset_data, new_name)
            
            if success:
                # IMPORTANT: Get the updated asset data from the project file
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
                    self.asset_renamed.emit(current_name, new_name, asset_type)
                else:
                    print("❌ Failed to get updated asset data")
                    
            else:
                QMessageBox.critical(self, "Rename Failed", 
                                f"Failed to rename asset '{current_name}'.\n"
                                f"Please check the console for details.")
                
        except Exception as e:
            print(f"❌ Error renaming asset: {e}")
            QMessageBox.critical(self, "Error", f"Error renaming asset: {e}")
    
    def refresh_asset_item_after_rename(self, item, new_name):
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

    def get_updated_asset_data(self, asset_name, asset_type):
        """Get the updated asset data from the project file after rename"""
        try:
            project_file = Path(self.project_path) / "project.json"
            if not project_file.exists():
                return None
                
            with open(project_file, 'r') as f:
                project_data = json.load(f)
            
            # Get the plural form for the category
            category = asset_type + 's' if not asset_type.endswith('s') else asset_type
            assets = project_data.get('assets', {}).get(category, {})
            
            return assets.get(asset_name)
            
        except Exception as e:
            print(f"❌ Error getting updated asset data: {e}")
            return None

    def asset_name_exists(self, name, asset_type):
        """Check if an asset name already exists in the same category"""
        try:
            project_file = Path(self.project_path) / "project.json"
            if not project_file.exists():
                return False
                
            with open(project_file, 'r') as f:
                project_data = json.load(f)
            
            # Get the plural form for the category
            category = asset_type + 's' if not asset_type.endswith('s') else asset_type
            assets = project_data.get('assets', {}).get(category, {})
            
            return name in assets
            
        except Exception as e:
            print(f"❌ Error checking asset name: {e}")
            return False

    def perform_asset_rename(self, asset_data, new_name):
        """Perform the actual asset rename operation using project_manager"""
        try:
            current_name = asset_data['name']
            asset_type = asset_data['asset_type']

            # Get the correct category name (plural)
            category = asset_type + 's' if not asset_type.endswith('s') else asset_type

            # Use project_manager for rename (handles references and auto-saves)
            if hasattr(self, 'project_manager') and self.project_manager:
                print(f"🔧 Using project_manager to rename: {current_name} → {new_name}")
                success = self.project_manager.rename_asset(category, current_name, new_name)
                if success:
                    print(f"💾 Project file updated with renamed asset")
                    return True
                else:
                    print(f"❌ Project manager rename failed")
                    return False

            # Fallback to direct file access if project_manager not available
            print(f"⚠️ Warning: project_manager not available, using direct file access")
            project_path = Path(self.project_path)
            project_file = project_path / "project.json"

            if not project_file.exists():
                print(f"❌ Project file not found: {project_file}")
                return False

            # Load project data
            with open(project_file, 'r') as f:
                project_data = json.load(f)

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
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)

            print(f"💾 Project file updated with renamed asset")
            return True

        except Exception as e:
            print(f"❌ Error performing asset rename: {e}")
            return False

    def setup_ui(self):
        """Setup the tree widget UI"""
        self.setHeaderLabel("Assets")
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Hide the header
        self.header().hide()
        
        # Set minimum width
        self.setMinimumWidth(200)
        
        # Enable selection
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
    
    def setup_categories(self):
        """Setup default asset categories"""
        categories = [
            "sprites",
            "sounds", 
            "backgrounds",
            "objects",
            "rooms",
            "scripts",
            "fonts"
        ]
        
        for category in categories:
            category_item = AssetTreeItem(
                parent=self,
                asset_type=category,
                asset_name="",
                asset_data={}
            )
            self.addTopLevelItem(category_item)
        
        # Expand all categories by default
        self.expandAll()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def on_item_clicked(self, item, column):
        """Handle item click"""
        if isinstance(item, AssetTreeItem) and not item.is_category:
            asset_data = {
                'type': item.asset_type,
                'name': item.asset_name,
                'data': item.asset_data
            }
            self.assetSelected.emit(asset_data)
    
    def on_item_double_clicked(self, item, column):
        """Handle item double click"""
        if isinstance(item, AssetTreeItem) and not item.is_category:
            asset_data = {
                'type': item.asset_type,
                'name': item.asset_name,
                'data': item.asset_data
            }
            self.assetDoubleClicked.emit(asset_data)
    
    def import_asset(self, files, asset_type, project_path):
        if not project_path:
            return
        
        import os
        import shutil
        from datetime import datetime
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            asset_name = os.path.splitext(file_name)[0]
            
            # Fix the asset type conversion
            if asset_type == "sprites":
                correct_type = "sprite"
            elif asset_type == "sounds":
                correct_type = "sound"
            elif asset_type == "backgrounds":
                correct_type = "background"
            else:
                correct_type = asset_type.rstrip('s')
            
            # Copy file to project directory
            asset_dir = os.path.join(project_path, asset_type)
            os.makedirs(asset_dir, exist_ok=True)
            
            # Copy the actual file
            dest_path = os.path.join(asset_dir, file_name)
            shutil.copy2(file_path, dest_path)
            
            asset_data = {
                'name': asset_name,
                'asset_type': correct_type,
                'file_path': f"{asset_type}/{file_name}",
                'project_path': dest_path,
                'imported': True,
                'created_date': datetime.now().isoformat()
            }
            
            # Add to tree
            self.add_asset(asset_type, asset_name, asset_data)
            print(f"✅ Imported {correct_type}: {asset_name}")
            
            # Save to project.json
            self.save_asset_to_project(asset_name, asset_type, asset_data, project_path)
            print(f"💾 Saved {asset_name} to project.json")

            # Update the asset manager's cache
            self.update_asset_manager_cache(asset_name, asset_type, asset_data)

    def update_asset_manager_cache(self, asset_name, asset_type, asset_data):
        """Update the asset manager's cache - simplified version"""
        print("Cache update for {asset_name} - skipping (not required)")
        # Asset import works fine without cache updates
        # This method exists for compatibility but doesn't need to do anything

    def save_asset_to_project(self, asset_name, asset_type, asset_data, project_path):
        """Save asset data to project.json file"""
        try:
            import json
            from pathlib import Path
            
            project_file = Path(project_path) / "project.json"
            
            # Load existing project data
            if project_file.exists():
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
            else:
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
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            print(f"✅ Successfully saved asset {asset_name} to project.json")
            return True
            
        except Exception as e:
            print(f"❌ ERROR in save_asset_to_project: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_asset(self, asset_type):
        """Create a new asset of the specified type"""
        name, ok = QInputDialog.getText(
            self, 
            f"Create {asset_type.title()[:-1]}", 
            f"Enter name for new {asset_type[:-1]}:"
        )
        
        if ok and name:
            asset_data = {
                'name': name,
                'type': asset_type[:-1],
                'imported': True,
                'created': True
            }
            self.add_asset(asset_type, name, asset_data)
    
    def add_asset(self, asset_type: str, asset_name: str, asset_data: Dict):
        """Add an asset to the tree"""
        # Find the appropriate category
        category_item = None
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if isinstance(item, AssetTreeItem) and item.asset_type == asset_type:
                category_item = item
                break
        
        if category_item:
            # Create new asset item (assigned to parent via constructor)
            AssetTreeItem(
                parent=category_item,
                asset_type=asset_type,
                asset_name=asset_name,
                asset_data=asset_data
            )

            # Expand the category to show the new asset
            self.expandItem(category_item)
            
            print(f"✅ Added {asset_name} to {asset_type} category")
        else:
            print(f"❌ Could not find {asset_type} category")
    
    def remove_asset(self, asset_type: str, asset_name: str):
        """Remove an asset from the tree"""
        # Find the asset and remove it
        for i in range(self.topLevelItemCount()):
            category_item = self.topLevelItem(i)
            if isinstance(category_item, AssetTreeItem) and category_item.asset_type == asset_type:
                for j in range(category_item.childCount()):
                    asset_item = category_item.child(j)
                    if isinstance(asset_item, AssetTreeItem) and asset_item.asset_name == asset_name:
                        category_item.removeChild(asset_item)
                        print(f"✅ Removed {asset_name} from {asset_type} category")
                        return
        
        print(f"❌ Could not find {asset_name} in {asset_type} category")
    
    def clear_assets(self):
        """Clear all assets but keep categories"""
        for i in range(self.topLevelItemCount()):
            category_item = self.topLevelItem(i)
            if isinstance(category_item, AssetTreeItem) and category_item.is_category:
                # Remove all children
                while category_item.childCount() > 0:
                    category_item.removeChild(category_item.child(0))
    
    def refresh_from_project(self, project_data: Dict):
        """Refresh tree from project data"""
        self.clear_assets()
        
        assets = project_data.get('assets', {})
        
        for asset_type, asset_list in assets.items():
            for asset_name, asset_data in asset_list.items():
                self.add_asset(asset_type, asset_name, asset_data)
        
        print("✅ Asset tree refreshed from project data")
    
    def get_asset_data(self, asset_type: str, asset_name: str) -> Optional[Dict]:
        """Get asset data by type and name"""
        for i in range(self.topLevelItemCount()):
            category_item = self.topLevelItem(i)
            if isinstance(category_item, AssetTreeItem) and category_item.asset_type == asset_type:
                for j in range(category_item.childCount()):
                    asset_item = category_item.child(j)
                    if isinstance(asset_item, AssetTreeItem) and asset_item.asset_name == asset_name:
                        return asset_item.asset_data
        
        return None
    
    def set_project_manager(self, project_manager):
        """Set reference to project manager"""
        self.project_manager = project_manager
    
    def set_current_project(self, project_path: str):
        """Set current project"""
        self.current_project = project_path

    def set_project(self, project_path: str, project_data: Dict):
        """Set project and refresh asset tree"""
        try:
            # ADD THIS LINE to store the project path:
            self.project_path = project_path
            
            self.set_current_project(project_path)
            
            if isinstance(project_data, dict):
                self.refresh_from_project(project_data)
                print(f"✅ Asset tree set to project: {Path(project_path).name}")
            else:
                print("⚠️  Invalid project_data, clearing assets")
                self.clear_assets()
            
        except Exception as e:
            print(f"❌ Error setting project in asset tree: {e}")
            # Fallback - just clear assets
            self.clear_assets()

    def force_project_refresh(self):
        """Force the IDE to refresh from the updated project.json"""
        try:
            # Find project manager and force reload
            parent = self.parent()
            while parent:
                if hasattr(parent, 'project_manager'):
                    project_manager = parent.project_manager
                    current_path = project_manager.get_current_project_path()
                    if current_path:
                        project_manager.load_project(current_path)
                        print("🔄 Forced project manager to reload")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"⚠️ Could not force refresh: {e}")


class AssetRenameDialog(QDialog):
    """Dialog for renaming assets"""
    
    def __init__(self, current_name, asset_type, parent=None):
        super().__init__(parent)
        self.current_name = current_name
        self.asset_type = asset_type
        self.new_name = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"Rename {self.asset_type.title()}")
        self.setFixedSize(400, 150)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Current name label
        current_label = QLabel(f"Current name: <b>{self.current_name}</b>")
        layout.addWidget(current_label)
        
        # New name input
        name_label = QLabel("New name:")
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.current_name)
        self.name_edit.selectAll()
        self.name_edit.setFocus()
        layout.addWidget(self.name_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.accept_rename)
        self.rename_btn.setDefault(True)
        button_layout.addWidget(self.rename_btn)
        
        layout.addLayout(button_layout)
        
        # Connect Enter key to rename
        self.name_edit.returnPressed.connect(self.accept_rename)
        
        # Validate input as user types
        self.name_edit.textChanged.connect(self.validate_name)
        
    def validate_name(self, text):
        """Validate the new name"""
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Check for empty name
        if not text:
            self.rename_btn.setEnabled(False)
            return
        
        # Check for invalid characters (common ones to avoid file system issues)
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in text for char in invalid_chars):
            self.rename_btn.setEnabled(False)
            return
        
        # Check if name changed
        if text == self.current_name:
            self.rename_btn.setEnabled(False)
            return
            
        self.rename_btn.setEnabled(True)
        
    def accept_rename(self):
        """Accept the rename if valid"""
        new_name = self.name_edit.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, "Invalid Name", "Asset name cannot be empty.")
            return
            
        if new_name == self.current_name:
            self.reject()
            return
            
        # Additional validation
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in new_name for char in invalid_chars):
            QMessageBox.warning(self, "Invalid Name", 
                              f"Asset name contains invalid characters.\n"
                              f"Avoid: {' '.join(invalid_chars)}")
            return
            
        self.new_name = new_name
        self.accept()