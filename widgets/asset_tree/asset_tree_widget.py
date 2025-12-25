#!/usr/bin/env python3
"""
Streamlined Asset Tree Widget for PyGameMaker IDE
Core tree widget focusing on UI management and delegating operations
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from PySide6.QtWidgets import QTreeWidget, QMenu, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from .asset_tree_item import AssetTreeItem
from .asset_operations import AssetOperations
from .asset_dialogs import AssetPropertiesDialog


class AssetTreeWidget(QTreeWidget):
    """Streamlined asset tree widget focusing on UI and tree management"""

    # Signals
    assetSelected = Signal(dict)
    assetDoubleClicked = Signal(dict)
    assetImported = Signal(str, str, dict)
    assetDeleted = Signal(str, str)
    assetRenamed = Signal(str, str, str)  # old_name, new_name, asset_type

    # camelCase aliases for backward compatibility
    asset_selected = assetSelected
    asset_double_clicked = assetDoubleClicked
    asset_imported = assetImported
    asset_deleted = assetDeleted
    asset_renamed = assetRenamed

    def __init__(self, parent=None):
        super().__init__(parent)

        # Core properties
        self.project_path = None
        self.project_manager = None
        self.current_project = None

        # Initialize operations handler
        self.operations = AssetOperations(self)

        # Setup UI
        self.setup_ui()
        self.setup_categories()
        self.setup_connections()

        print("🔧 AssetTreeWidget: Initialized with operations handler")

    def setup_ui(self):
        """Setup the tree widget UI"""
        self.setHeaderLabel(self.tr("Assets"))
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
        """Setup default asset categories with separators"""
        categories = [
            ("sprites", self.tr("Sprites")),
            ("sounds", self.tr("Sounds")),
            ("backgrounds", self.tr("Backgrounds")),
            "separator",  # First separator
            ("objects", self.tr("Objects")),
            ("rooms", self.tr("Rooms")),
            "separator",  # Second separator
            ("scripts", self.tr("Scripts")),
            ("fonts", self.tr("Fonts"))
        ]

        for item in categories:
            if item == "separator":
                # Create separator item
                separator_item = self.create_separator_item()
                self.addTopLevelItem(separator_item)
            else:
                category_type, category_display = item
                category_item = AssetTreeItem(
                    parent=self,
                    asset_type=category_type,
                    asset_name="",
                    asset_data={}
                )
                self.addTopLevelItem(category_item)

        # Expand all categories by default (but not separators)
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if hasattr(item, 'is_category') and item.is_category:
                self.expandItem(item)

        # Clear any initial focus/selection to prevent focus rectangle
        self.clearSelection()
        self.setCurrentItem(None)

    def create_separator_item(self):
        """Create a separator item for the asset tree"""
        from PySide6.QtWidgets import QTreeWidgetItem
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont

        separator = QTreeWidgetItem([""])

        # Make it non-selectable and non-interactive
        separator.setFlags(Qt.ItemFlag.NoItemFlags)

        # Set custom styling to make it look like a separator
        separator.setBackground(0, Qt.GlobalColor.transparent)

        # Add a visual line using text
        separator.setText(0, "─" * 50)  # Unicode horizontal line character

        # Center the text and make it smaller
        font = QFont()
        font.setPointSize(6)
        separator.setFont(0, font)
        separator.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)

        # Make it slightly shorter
        separator.setSizeHint(0, self.fontMetrics().boundingRect("A").size())

        return separator

    def setup_connections(self):
        """Setup signal connections"""
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show right-click context menu for asset management"""
        print(f"🖱️ Context menu requested at position: {position}")

        item = self.itemAt(position)
        print(f"   Item at position: {item}")

        if not item:
            print("   ❌ No item found at position")
            return

        print(f"   Item type: {type(item)}")
        print(f"   Is AssetTreeItem: {isinstance(item, AssetTreeItem)}")

        if not isinstance(item, AssetTreeItem):
            print("   ❌ Item is not an AssetTreeItem")
            return

        print(f"   Is category: {item.is_category}")

        # Create context menu
        context_menu = QMenu(self)

        if item.is_category:
            # Category menu - show create and import options
            print(f"   ✅ Showing category menu for: {item.asset_type}")

            # Get singular form for display (remove trailing 's')
            singular_type = item.asset_type.rstrip('s')

            # Create new asset action
            create_action = QAction(self.tr("➕ Create New {0}...").format(singular_type.title()), self)
            create_action.triggered.connect(lambda: self.trigger_create_for_category(item.asset_type))
            context_menu.addAction(create_action)

            # Import asset action (only for sprites, sounds, backgrounds - not rooms/objects)
            if item.asset_type not in ["rooms", "objects"]:
                import_action = QAction(self.tr("📥 Import {0}...").format(item.asset_type.title()), self)
                import_action.triggered.connect(lambda: self.trigger_import_for_category(item.asset_type))
                context_menu.addAction(import_action)

            # Import Package action for rooms and objects
            if item.asset_type in ["rooms", "objects"]:
                singular = "Room" if item.asset_type == "rooms" else "Object"
                import_pkg_action = QAction(self.tr("📦 Import {0} Package...").format(singular), self)
                import_pkg_action.triggered.connect(lambda checked=False, at=item.asset_type: self.import_package(at))
                context_menu.addAction(import_pkg_action)

        else:
            # Asset item menu - show rename, delete, properties
            print(f"   ✅ Showing context menu for: {item.asset_name}")

            # Rename action
            rename_action = QAction(self.tr("✏️ Rename"), self)
            rename_action.triggered.connect(lambda: self.operations.rename_asset(item))
            context_menu.addAction(rename_action)

            # Import Image action for sprites
            if item.asset_type in ["sprite", "sprites"]:
                import_image_action = QAction(self.tr("📥 Import Image..."), self)
                import_image_action.triggered.connect(lambda: self.import_sprite_image(item))
                context_menu.addAction(import_image_action)

                # Configure animation (sprite strip) action
                configure_anim_action = QAction(self.tr("🎬 Configure Animation..."), self)
                configure_anim_action.triggered.connect(lambda: self.configure_sprite_animation(item))
                context_menu.addAction(configure_anim_action)

            # Delete action
            delete_action = QAction(self.tr("🗑️ Delete"), self)
            delete_action.triggered.connect(lambda: self.operations.delete_asset(item))
            context_menu.addAction(delete_action)

            # Export action for objects and rooms
            if item.asset_type in ["object", "objects", "room", "rooms"]:
                context_menu.addSeparator()
                asset_type_plural = "objects" if item.asset_type in ["object", "objects"] else "rooms"
                export_action = QAction(self.tr("📦 Export Package..."), self)
                export_action.triggered.connect(lambda checked=False, at=asset_type_plural, an=item.asset_name: self.export_resource(at, an))
                context_menu.addAction(export_action)

            # Room reordering actions (only for rooms)
            if item.asset_type in ["room", "rooms"]:
                context_menu.addSeparator()

                # Get all rooms to check position
                rooms_category = None
                for i in range(self.topLevelItemCount()):
                    category = self.topLevelItem(i)
                    if isinstance(category, AssetTreeItem) and category.asset_type == 'rooms':
                        rooms_category = category
                        break

                if rooms_category:
                    room_count = rooms_category.childCount()
                    room_index = rooms_category.indexOfChild(item)

                    is_first = (room_index == 0)
                    is_last = (room_index == room_count - 1)

                    # Move Up
                    move_up_action = QAction(self.tr("⬆️ Move Up"), self)
                    move_up_action.setEnabled(not is_first)
                    move_up_action.triggered.connect(lambda: self.move_room_up(item.asset_name))
                    context_menu.addAction(move_up_action)

                    # Move Down
                    move_down_action = QAction(self.tr("⬇️ Move Down"), self)
                    move_down_action.setEnabled(not is_last)
                    move_down_action.triggered.connect(lambda: self.move_room_down(item.asset_name))
                    context_menu.addAction(move_down_action)

                    context_menu.addSeparator()

                    # Move to Top
                    move_top_action = QAction(self.tr("⏫ Move to Top"), self)
                    move_top_action.setEnabled(not is_first)
                    move_top_action.triggered.connect(lambda: self.move_room_to_top(item.asset_name))
                    context_menu.addAction(move_top_action)

                    # Move to Bottom
                    move_bottom_action = QAction(self.tr("⏬ Move to Bottom"), self)
                    move_bottom_action.setEnabled(not is_last)
                    move_bottom_action.triggered.connect(lambda: self.move_room_to_bottom(item.asset_name))
                    context_menu.addAction(move_bottom_action)

            context_menu.addSeparator()

            # Properties action
            properties_action = QAction(self.tr("⚙️ Properties..."), self)
            properties_action.triggered.connect(lambda: self.show_asset_properties(item))
            context_menu.addAction(properties_action)

        print("   📋 Executing menu at global position")
        context_menu.exec(self.mapToGlobal(position))
        print("   ✅ Menu closed")

    def trigger_create_for_category(self, asset_type: str):
        """Trigger create dialog for a specific asset category"""
        print(f"➕ Create requested for category: {asset_type}")

        # Get the parent IDE window to access the create functionality
        parent = self.parent()
        while parent and not hasattr(parent, 'create_asset'):
            parent = parent.parent()

        if parent and hasattr(parent, 'create_asset'):
            # Call the parent's create_asset method with the asset type
            parent.create_asset(asset_type)
        else:
            # Fallback: try to create locally if method exists
            if hasattr(self, 'create_asset'):
                self.create_asset(asset_type)
            else:
                print("⚠️ Could not find parent with create_asset method")
                QMessageBox.information(
                    self,
                    self.tr("Create Asset"),
                    self.tr("Asset creation for {0} is not yet implemented.").format(asset_type)
                )

    def trigger_import_for_category(self, asset_type: str):
        """Trigger import dialog for a specific asset category"""
        print(f"📥 Import requested for category: {asset_type}")

        # Get the parent IDE window to access the import functionality
        parent = self.parent()
        while parent and not hasattr(parent, 'import_assets'):
            parent = parent.parent()

        if parent and hasattr(parent, 'import_assets'):
            parent.import_assets(asset_type)
        else:
            print("⚠️ Could not find parent with import_assets method")
            QMessageBox.information(
                self,
                self.tr("Import Assets"),
                self.tr("Please use the File menu to import {0}").format(asset_type)
            )

    def show_asset_properties(self, item):
        """Show detailed asset properties dialog"""
        if isinstance(item, AssetTreeItem) and not item.is_category:
            dialog = AssetPropertiesDialog(item.asset_data, self)
            dialog.exec()

    def import_sprite_image(self, item):
        """Import an image for a sprite asset"""
        if not isinstance(item, AssetTreeItem) or item.is_category:
            return

        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path

        sprite_name = item.asset_name

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Image for Sprite '{0}'").format(sprite_name),
            str(Path.home()),
            self.tr("Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)")
        )

        if not file_path:
            return

        # Use the operations handler to import
        if self.operations.import_sprite_image_for_asset(Path(file_path), sprite_name):
            # Refresh the tree to show the new thumbnail
            self.force_project_refresh()
            QMessageBox.information(
                self,
                self.tr("Success"),
                self.tr("Image imported successfully for sprite '{0}'").format(sprite_name)
            )

    def configure_sprite_animation(self, item):
        """Open the sprite strip configuration dialog"""
        if not isinstance(item, AssetTreeItem) or item.is_category:
            return

        sprite_name = item.asset_name
        sprite_data = item.asset_data

        if not sprite_data:
            QMessageBox.warning(
                self,
                self.tr("No Sprite Data"),
                self.tr("Could not load sprite data for '{0}'").format(sprite_name)
            )
            return

        # Get the sprite image path
        file_path = sprite_data.get('file_path', '')
        if not file_path:
            QMessageBox.warning(
                self,
                self.tr("No Image"),
                self.tr("Sprite '{0}' has no image file. Please import an image first.").format(sprite_name)
            )
            return

        # Build full path
        from pathlib import Path
        if self.project_path:
            full_path = Path(self.project_path) / file_path
        else:
            full_path = Path(file_path)

        if not full_path.exists():
            QMessageBox.warning(
                self,
                self.tr("Image Not Found"),
                self.tr("Could not find image file: {0}").format(str(full_path))
            )
            return

        # Open the sprite strip dialog
        from dialogs.sprite_strip_dialog import SpriteStripDialog
        dialog = SpriteStripDialog(str(full_path), sprite_name, self)

        if dialog.exec():
            # Get the configuration
            config = dialog.get_configuration()

            # Update sprite data through asset manager
            if self.project_manager and hasattr(self.project_manager, 'asset_manager'):
                asset_manager = self.project_manager.asset_manager
                asset_manager.update_sprite_animation(
                    sprite_name,
                    frames=config['frames'],
                    frame_width=config['frame_width'],
                    frame_height=config['frame_height'],
                    speed=config['speed'],
                    animation_type=config['animation_type']
                )

                # Refresh the tree
                self.force_project_refresh()

                QMessageBox.information(
                    self,
                    self.tr("Animation Configured"),
                    self.tr("Sprite '{0}' configured with {1} frames at {2} FPS").format(
                        sprite_name, config['frames'], config['speed']
                    )
                )

    def export_resource(self, asset_type: str, asset_name: str):
        """Export a resource (object or room) with dependencies"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        from utils.resource_packager import ResourcePackager

        # Get project path
        if not self.project_path:
            QMessageBox.warning(self, self.tr("No Project"), self.tr("No project is currently loaded"))
            return

        project_path = Path(self.project_path)

        # Determine file extension and filter
        if asset_type == 'objects':
            extension = '.gmobj'
            file_filter = "GameMaker Objects (*.gmobj)"
            singular = "object"
        elif asset_type == 'rooms':
            extension = '.gmroom'
            file_filter = "GameMaker Rooms (*.gmroom)"
            singular = "room"
        else:
            return

        # Ask user where to save
        default_filename = f"{asset_name}{extension}"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Export {0}").format(singular.title()),
            str(Path.home() / default_filename),
            file_filter
        )

        if file_path:
            output_path = Path(file_path)

            # Export based on type
            if asset_type == 'objects':
                success = ResourcePackager.export_object(project_path, asset_name, output_path)
            else:  # rooms
                success = ResourcePackager.export_room(project_path, asset_name, output_path)

            if success:
                QMessageBox.information(
                    self,
                    self.tr("Export Successful"),
                    self.tr("{0} '{1}' exported to:\n{2}").format(singular.title(), asset_name, output_path)
                )
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Export Failed"),
                    self.tr("Failed to export {0} '{1}'").format(singular, asset_name)
                )

    def import_package(self, asset_type: str):
        """Import a package file (.gmroom or .gmobj) into the project"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        from utils.resource_packager import ResourcePackager

        # Get project path
        if not self.project_path:
            QMessageBox.warning(self, self.tr("No Project"), self.tr("No project is currently loaded"))
            return

        project_path = Path(self.project_path)

        # Determine file filter based on asset type
        if asset_type == 'objects':
            file_filter = "GameMaker Objects (*.gmobj);;All Files (*)"
            singular = "object"
        elif asset_type == 'rooms':
            file_filter = "GameMaker Rooms (*.gmroom);;All Files (*)"
            singular = "room"
        else:
            return

        # Ask user for file to import
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import {0} Package").format(singular.title()),
            str(Path.home()),
            file_filter
        )

        if file_path:
            package_path = Path(file_path)

            # Import based on type
            if asset_type == 'objects':
                result = ResourcePackager.import_object(package_path, project_path)
            else:  # rooms
                result = ResourcePackager.import_room(package_path, project_path)

            if result:
                # Refresh the asset tree
                self.force_project_refresh()

                QMessageBox.information(
                    self,
                    self.tr("Import Successful"),
                    self.tr("{0} '{1}' imported successfully!").format(singular.title(), result)
                )
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Import Failed"),
                    self.tr("Failed to import {0} package").format(singular)
                )

    def on_item_clicked(self, item, column):
        """Handle item click"""
        if isinstance(item, AssetTreeItem) and not item.is_category:
            asset_data = {
                'asset_type': item.asset_type,
                'name': item.asset_name,
                'data': item.asset_data
            }
            self.assetSelected.emit(asset_data)

    def on_item_double_clicked(self, item, column):
        """Handle item double click"""
        if isinstance(item, AssetTreeItem) and not item.is_category:
            asset_data = {
                'asset_type': item.asset_type,
                'name': item.asset_name,
                'data': item.asset_data
            }
            self.assetDoubleClicked.emit(asset_data)

    # Asset management methods - delegate to operations handler
    def import_asset(self, files: List[str], asset_type: str, project_path: str):
        """Import asset files - delegates to operations handler"""
        return self.operations.import_asset(files, asset_type, project_path)

    def delete_asset(self, item):
        """Delete an asset - delegates to operations handler"""
        return self.operations.delete_asset(item)

    def rename_asset(self, item):
        """Rename an asset - delegates to operations handler"""
        return self.operations.rename_asset(item)

    def create_asset(self, asset_type: str):
        """Create a new asset of the specified type"""
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(
            self,
            self.tr("Create {0}").format(asset_type.title()[:-1]),
            self.tr("Enter name for new {0}:").format(asset_type[:-1])
        )

        if ok and name:
            from .asset_utils import create_asset_data_template
            asset_data = create_asset_data_template(name, asset_type)
            self.add_asset(asset_type, name, asset_data)

    # Tree management methods
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

    def remove_asset(self, asset_type: str, asset_name: str):
        """Remove an asset from the tree"""
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
        """Refresh tree from project data maintaining room order"""
        self.clear_assets()

        assets = project_data.get('assets', {})

        # Add all assets (including rooms) using the standard add_asset method
        for asset_type, asset_list in assets.items():
            for asset_name, asset_data in asset_list.items():
                self.add_asset(asset_type, asset_name, asset_data)

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

    # Room ordering methods
    def get_room_list(self):
        """Get ordered list of room names from project data"""
        try:
            project_file = Path(self.project_path) / "project.json"
            if not project_file.exists():
                return []

            with open(project_file, 'r') as f:
                project_data = json.load(f)

            rooms = project_data.get('assets', {}).get('rooms', {})
            return list(rooms.keys())
        except Exception:
            return []

    def move_room_up(self, room_name: str):
        """Move a room up in the order"""
        self._reorder_room(room_name, -1)

    def move_room_down(self, room_name: str):
        """Move a room down in the order"""
        self._reorder_room(room_name, 1)

    def move_room_to_top(self, room_name: str):
        """Move a room to the top of the list"""
        self._reorder_room(room_name, 'top')

    def move_room_to_bottom(self, room_name: str):
        """Move a room to the bottom of the list"""
        self._reorder_room(room_name, 'bottom')

    def _reorder_room(self, room_name: str, direction):
        """Reorder rooms in project data and save"""
        print(f"🔧 DEBUG: _reorder_room called with room_name='{room_name}', direction={direction}")
        try:
            from collections import OrderedDict

            project_file = Path(self.project_path) / "project.json"
            if not project_file.exists():
                print(f"❌ DEBUG: project.json not found at {project_file}")
                return

            # Load project data with order preservation
            with open(project_file, 'r') as f:
                project_data = json.load(f, object_pairs_hook=OrderedDict)

            rooms = project_data.get('assets', {}).get('rooms', OrderedDict())
            room_list = list(rooms.keys())
            print(f"🔍 DEBUG: Current room order (before reorder): {room_list}")

            if room_name not in room_list:
                print(f"❌ DEBUG: room_name '{room_name}' not found in room_list")
                return

            current_index = room_list.index(room_name)
            print(f"🔍 DEBUG: Current index of '{room_name}': {current_index}")

            # Remove from current position
            room_list.remove(room_name)

            # Calculate new position
            if direction == 'top':
                new_index = 0
            elif direction == 'bottom':
                new_index = len(room_list)
            else:  # numeric offset
                new_index = max(0, min(current_index + direction, len(room_list)))

            # Insert at new position
            room_list.insert(new_index, room_name)
            print(f"🔍 DEBUG: New room order (after reorder): {room_list}")

            # Rebuild rooms OrderedDict in new order
            new_rooms = OrderedDict()
            for room_key in room_list:
                new_rooms[room_key] = rooms[room_key]

            project_data['assets']['rooms'] = new_rooms
            print(f"🔍 DEBUG: Built new_rooms OrderedDict with keys: {list(new_rooms.keys())}")

            # Save project back to file with order preservation
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2, sort_keys=False)

            print(f"✅ Saved new room order to project.json: {room_list}")

            # Find the IDE parent window
            ide_window = self.parent()
            while ide_window and not hasattr(ide_window, 'current_project_data'):
                ide_window = ide_window.parent()

            if ide_window:
                print("🔍 DEBUG: Found IDE window")

                # CRITICAL: Update the asset manager's cache directly
                if hasattr(ide_window, 'asset_manager'):
                    print("🔍 DEBUG: IDE has asset_manager attribute")
                    if ide_window.asset_manager:
                        print("🔍 DEBUG: asset_manager is not None")
                        if hasattr(ide_window.asset_manager, 'assets_cache'):
                            print("🔍 DEBUG: asset_manager has assets_cache attribute")
                            # Update the cache with the new room order
                            ide_window.asset_manager.assets_cache['rooms'] = new_rooms
                            print("✅ Updated asset manager cache with new room order")
                            print(f"🔍 DEBUG: New cache room order: {list(new_rooms.keys())}")
                        else:
                            print("❌ DEBUG: asset_manager does NOT have assets_cache attribute")
                    else:
                        print("❌ DEBUG: asset_manager is None")
                else:
                    print("❌ DEBUG: IDE does NOT have asset_manager attribute")

                # Update the IDE's project data
                ide_window.current_project_data = project_data

                # Update the project manager's data
                if hasattr(ide_window, 'project_manager'):
                    ide_window.project_manager.current_project_data = project_data
                    ide_window.project_manager.mark_dirty()

                    # Force save to ensure asset manager syncs
                    if ide_window.project_manager.save_project():
                        print("✅ Project saved with new room order")

                # Refresh the entire asset tree from the updated data
                self.refresh_from_project(project_data)

                # Update status
                if hasattr(ide_window, 'update_status'):
                    ide_window.update_status(f"Reordered room: {room_name}")
            else:
                print("❌ DEBUG: Could not find IDE window")
                # Fallback to local refresh if we can't find IDE
                self._refresh_room_display()

        except Exception as e:
            print(f"Error reordering room: {e}")
            import traceback
            traceback.print_exc()

    def _refresh_room_display(self):
        """Refresh the room category in the tree after reordering"""
        try:
            # Find rooms category
            rooms_category = None
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                if isinstance(item, AssetTreeItem) and item.asset_type == "rooms":
                    rooms_category = item
                    break

            if not rooms_category:
                return

            # Get current room data
            room_list = self.get_room_list()

            # Store expansion state
            was_expanded = self.isItemExpanded(rooms_category)

            # Clear and rebuild room items
            while rooms_category.childCount() > 0:
                rooms_category.removeChild(rooms_category.child(0))

            # Load project data for room details
            project_file = Path(self.project_path) / "project.json"
            with open(project_file, 'r') as f:
                project_data = json.load(f)

            rooms_data = project_data.get('assets', {}).get('rooms', {})

            # Add rooms in order without position numbers
            for room_name in room_list:
                if room_name in rooms_data:
                    room_data = rooms_data[room_name]
                    AssetTreeItem(
                        parent=rooms_category,
                        asset_type="rooms",
                        asset_name=room_name,
                        asset_data=room_data
                    )

            # Restore expansion state
            if was_expanded:
                self.expandItem(rooms_category)

        except Exception as e:
            print(f"Error refreshing room display: {e}")

    # Project management methods
    def set_project(self, project_path: str, project_data: Dict):
        """Set project and refresh asset tree"""
        try:
            self.project_path = project_path
            self.set_current_project(project_path)

            # DEBUG: Check room order when receiving project data
            rooms = project_data.get('assets', {}).get('rooms', {})
            print(f"DEBUG asset_tree set_project: room order = {list(rooms.keys())}")

            if isinstance(project_data, dict):
                self.refresh_from_project(project_data)
            else:
                print("⚠️ Invalid project_data, clearing assets")
                self.clear_assets()

        except Exception:
            self.clear_assets()

    def set_current_project(self, project_path: str):
        """Set current project"""
        self.current_project = project_path

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

    # Compatibility methods for existing code
    def update_asset_manager_cache(self, asset_name: str, asset_type: str, asset_data: Dict):
        """Compatibility method - delegates to operations"""
        self.operations.update_asset_manager_cache(asset_name, asset_type, asset_data)

    def save_asset_to_project(self, asset_name: str, asset_type: str, asset_data: Dict, project_path: str) -> bool:
        """Compatibility method - delegates to operations"""
        return self.operations.save_asset_to_project(asset_name, asset_type, asset_data, project_path)

    def get_asset_absolute_path(self, asset_data: Dict) -> Optional[str]:
        """Get absolute path for an asset - needed for image preview functionality"""
        try:
            # Try project_path first (full absolute path)
            if 'project_path' in asset_data:
                asset_path = Path(asset_data['project_path'])
                if asset_path.exists():
                    return str(asset_path)

            # Try relative path with project root
            if 'file_path' in asset_data and self.project_path:
                asset_path = Path(self.project_path) / asset_data['file_path']
                if asset_path.exists():
                    return str(asset_path)

            # Try name-based path construction for imported assets
            if self.project_path and 'name' in asset_data and 'asset_type' in asset_data:
                asset_name = asset_data['name']
                asset_type = asset_data['asset_type']

                # Convert singular to plural for directory name
                type_map = {
                    'sprite': 'sprites',
                    'sound': 'sounds',
                    'background': 'backgrounds',
                    'object': 'objects',
                    'room': 'rooms',
                    'script': 'scripts',
                    'font': 'fonts'
                }
                plural_type = type_map.get(asset_type, asset_type + 's')

                # Common image extensions to try
                extensions = ['.png', '.jpg', '.jpeg', '.gi', '.bmp']

                for ext in extensions:
                    asset_path = Path(self.project_path) / plural_type / f"{asset_name}{ext}"
                    if asset_path.exists():
                        return str(asset_path)

            return None

        except Exception:
            import traceback
            traceback.print_exc()
            return None

    def get_selected_asset(self):
        """Get the currently selected asset data"""
        current = self.currentItem()
        if isinstance(current, AssetTreeItem) and not current.is_category:
            return {
                'type': current.asset_type,
                'name': current.asset_name,
                'data': current.asset_data
            }
        return None
