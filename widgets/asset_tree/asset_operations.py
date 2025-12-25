#!/usr/bin/env python3
"""
Asset Operations for PyGameMaker IDE
Handles all asset file operations: import, delete, rename, and project file management
"""

import shutil
from pathlib import Path
from typing import List, Dict, Optional
from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon

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
                print("⚠️ Asset is open in editor, closing it first...")
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
                                "Please choose a different name.")
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
                                "Please check the console for details.")
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
            # Check both 'file_path' (sprites/sounds) and 'project_path' (legacy)
            rel_file_path = asset_data.get('file_path') or asset_data.get('project_path')
            print(f"📄 Found asset data: {rel_file_path or 'No path'}")

            # Delete physical file if it exists
            if rel_file_path:
                # Resolve relative path against project directory
                file_path = Path(self.tree.project_path) / rel_file_path
                if file_path.exists():
                    file_path.unlink()
                    print(f"🗑️ Deleted file: {file_path}")

            # Delete thumbnail if it exists
            thumbnail_path = asset_data.get('thumbnail')
            if thumbnail_path:
                thumb_file = Path(self.tree.project_path) / thumbnail_path
                if thumb_file.exists():
                    thumb_file.unlink()
                    print(f"🗑️ Deleted thumbnail: {thumb_file}")

            # Remove from project data
            del assets[asset_category][asset_name]
            print(f"✅ Removed {asset_name} from project data")

            # If deleting a sprite, clear references from objects that use it
            if asset_category == "sprites":
                objects = assets.get("objects", {})
                updated_objects = []
                for obj_name, obj_data in objects.items():
                    if obj_data.get("sprite") == asset_name:
                        obj_data["sprite"] = ""
                        updated_objects.append(obj_name)
                if updated_objects:
                    print(f"🔄 Cleared sprite reference from objects: {', '.join(updated_objects)}")

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

                    # Also update object cache if we cleared sprite references
                    if asset_category == "sprites" and "objects" in asset_manager.assets_cache:
                        for obj_name in updated_objects:
                            if obj_name in asset_manager.assets_cache["objects"]:
                                asset_manager.assets_cache["objects"][obj_name]["sprite"] = ""
                                print(f"✅ Updated {obj_name} in AssetManager cache")

            # Save modified data back to file
            if save_project_data(project_file, project_data):
                print("💾 Saved changes to project.json")

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
            current_name = asset_data['name']
            asset_type = asset_data['asset_type']

            # Get the correct category name (plural)
            category = asset_type + 's' if not asset_type.endswith('s') else asset_type

            # USE PROJECT MANAGER INSTEAD OF DIRECT FILE ACCESS
            if hasattr(self.tree, 'project_manager') and self.tree.project_manager:
                print(f"🔧 Using project_manager to rename: {current_name} → {new_name}")
                success = self.tree.project_manager.rename_asset(category, current_name, new_name)

                if success:
                    print("💾 Project file updated with renamed asset")
                    return True
                else:
                    print("❌ Project manager rename failed")
                    return False

            # FALLBACK: Old direct file method (if project_manager not available)
            print("⚠️  Warning: project_manager not available, using direct file access")
            project_path = Path(self.tree.project_path)
            project_file = project_path / "project.json"

            if not project_file.exists():
                print(f"❌ Project file not found: {project_file}")
                return False

            # Load project data
            project_data = load_project_data(project_file)
            if not project_data:
                return False

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
                print("💾 Project file updated with renamed asset (direct method)")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ Error in perform_asset_rename: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_updated_asset_data(self, asset_name: str, asset_type: str) -> Optional[Dict]:
        """Get the updated asset data after rename"""
        try:
            # First try to get from asset_manager (most up-to-date)
            if hasattr(self.tree, 'project_manager') and self.tree.project_manager:
                if self.tree.project_manager.asset_manager:
                    # Get the plural form for the category
                    category = asset_type + 's' if not asset_type.endswith('s') else asset_type

                    asset_data = self.tree.project_manager.asset_manager.get_asset(category, asset_name)
                    if asset_data:
                        print(f"✅ Got updated asset data from cache: {asset_name}")
                        return asset_data

            # Fallback: read from file
            project_file = Path(self.tree.project_path) / "project.json"
            if not project_file.exists():
                return None

            project_data = load_project_data(project_file)
            if not project_data:
                return None

            # Get the plural form for the category
            category = asset_type + 's' if not asset_type.endswith('s') else asset_type
            assets = project_data.get('assets', {}).get(category, {})

            asset_data = assets.get(asset_name)
            if asset_data:
                print(f"✅ Got updated asset data from file: {asset_name}")

            return asset_data

        except Exception as e:
            print(f"❌ Error getting updated asset data: {e}")
            import traceback
            traceback.print_exc()
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
                print(f"   Asset type from data: '{asset_type}'")
                print(f"   Full asset_data keys: {list(asset_data.keys())}")
                print(f"   file_path in data: {asset_data.get('file_path', 'NOT FOUND')}")

                # Update the asset name in the data
                item.asset_name = new_name

                # For sprites and backgrounds, reload the thumbnail
                if asset_type in ["sprite", "background", "sprites", "backgrounds"]:
                    print("   ✓ Asset type matches sprite/background check")

                    # Build the new file path using the new name
                    project_root = Path(self.tree.project_path)

                    # Try multiple path construction methods
                    file_path = asset_data.get('file_path')

                    if file_path:
                        # Method 1: Use the file_path from asset_data
                        if Path(file_path).is_absolute():
                            new_file_path = Path(file_path)
                        else:
                            new_file_path = project_root / file_path
                        print(f"   Method 1 (from asset_data): {new_file_path}")
                    else:
                        # Method 2: Construct from scratch
                        if asset_type in ["sprite", "sprites"]:
                            asset_folder = "sprites"
                        else:
                            asset_folder = "backgrounds"

                        new_file_path = project_root / "assets" / asset_folder / f"{new_name}.png"
                        print(f"   Method 2 (constructed): {new_file_path}")

                    print(f"   Final path to check: {new_file_path}")
                    print(f"   Path exists: {new_file_path.exists()}")

                    if new_file_path.exists():
                        try:
                            # Clear any existing icon first
                            item.setIcon(0, QIcon())

                            # Force Qt to load fresh from disk
                            with open(new_file_path, 'rb') as f:
                                image_data = f.read()

                            print(f"   Read {len(image_data)} bytes from file")

                            # Load pixmap from the raw data
                            pixmap = QPixmap()
                            pixmap.loadFromData(image_data)

                            print(f"   Pixmap null: {pixmap.isNull()}, size: {pixmap.width()}x{pixmap.height()}")

                            if not pixmap.isNull():
                                # Scale to thumbnail size
                                scaled_pixmap = pixmap.scaled(
                                    32, 32,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation
                                )
                                # Update the icon
                                item.setIcon(0, QIcon(scaled_pixmap))
                                # Set text without emoji since we have thumbnail
                                item.setText(0, new_name)
                                print("   ✅ Thumbnail icon set successfully")
                            else:
                                print("   ⚠️ Pixmap is null after loading")
                                item.setText(0, f"🖼️ {new_name}")
                        except Exception as e:
                            print(f"   ⚠️ Exception loading thumbnail: {e}")
                            import traceback
                            traceback.print_exc()
                            item.setText(0, f"🖼️ {new_name}")
                    else:
                        print("   ⚠️ File does not exist at path")
                        item.setText(0, f"🖼️ {new_name}")
                else:
                    print("   ✗ Asset type did not match sprite/background check")

                    # For other asset types, use emoji approach
                    if asset_type == "sound":
                        item.setText(0, f"🔊 {new_name}")
                    elif asset_type == "object":
                        item.setText(0, f"📦 {new_name}")
                    elif asset_type == "room":
                        item.setText(0, f"🏠 {new_name}")
                    elif asset_type == "script":
                        item.setText(0, f"📜 {new_name}")
                    elif asset_type == "font":
                        item.setText(0, f"🔤 {new_name}")
                    else:
                        item.setText(0, new_name)

                print(f"✅ Asset item text and icon refreshed for: {new_name}")

            except Exception as e:
                print(f"❌ Error refreshing asset item: {e}")
                import traceback
                traceback.print_exc()

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

    def import_sprite_image_for_asset(self, file_path: Path, sprite_name: str) -> bool:
        """Replace/import an image file for an existing sprite asset"""
        try:
            # Get AssetManager
            asset_manager = self._get_asset_manager()
            if not asset_manager:
                QMessageBox.warning(
                    self.tree,
                    "Import Error",
                    "Asset manager is not available."
                )
                return False

            # Use replace_sprite_image to update existing sprite (not create new one)
            result = asset_manager.replace_sprite_image(file_path, sprite_name)

            if result:
                print(f"✅ Successfully replaced image for sprite: {sprite_name}")

                # Update the tree item
                for i in range(self.tree.topLevelItemCount()):
                    category_item = self.tree.topLevelItem(i)
                    if hasattr(category_item, 'asset_type') and category_item.asset_type == 'sprites':
                        for j in range(category_item.childCount()):
                            asset_item = category_item.child(j)
                            if asset_item.asset_name == sprite_name:
                                # Update the item's data
                                asset_item.asset_data = result
                                # Refresh visual (thumbnail)
                                self.refresh_asset_item_after_rename(asset_item, sprite_name)
                                break
                        break

                # Emit signal
                self.tree.asset_imported.emit(sprite_name, 'sprites', result)

                # Save project to persist changes
                if hasattr(self.tree, 'project_manager') and self.tree.project_manager:
                    self.tree.project_manager.save_project()

                return True
            else:
                QMessageBox.warning(
                    self.tree,
                    "Import Failed",
                    "Failed to import the image."
                )
                return False

        except Exception as e:
            print(f"❌ Error importing sprite image: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self.tree,
                "Import Error",
                f"Error importing image: {str(e)}"
            )
            return False
