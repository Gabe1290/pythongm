#!/usr/bin/env python3
"""
Asset Tree Item for PyGameMaker IDE
Custom tree widget item for displaying individual game assets
"""

from pathlib import Path
from typing import Dict
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AssetTreeItem(QTreeWidgetItem):
    """Custom tree item for assets"""

    def __init__(self, parent=None, asset_type: str = "", asset_name: str = "", asset_data: Dict = None):
        super().__init__(parent)

        self.asset_type = asset_type
        self.asset_name = asset_name
        self.asset_data = asset_data or {}
        self.is_category = asset_name == ""

        # Create camelCase aliases for compatibility
        self.assetType = asset_type
        self.assetName = asset_name
        self.assetData = asset_data or {}
        self.isCategory = self.is_category

        self.setup_item()

    def setup_item(self):
            """Setup the appearance and properties of the tree item"""
            if self.is_category:
                # Category item with emojis
                self.setText(0, self.asset_type.title())
                self.setFont(0, QFont("", 9, QFont.Weight.Bold))

                # Set category icons with emojis
                icon_map = {
                    "sprites": "🖼️ Sprites",
                    "sounds": "🔊 Sounds",
                    "backgrounds": "🖼️ Backgrounds",
                    "objects": "📦 Objects",
                    "rooms": "🏠 Rooms",
                    "scripts": "📜 Scripts",
                    "fonts": "🔤 Fonts",
                    "data": "📄 Data"
                }

                if self.asset_type in icon_map:
                    self.setText(0, icon_map[self.asset_type])

                # Make categories non-selectable but expandable
                self.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsDropEnabled)

            else:
                # Asset item
                self.setText(0, self.asset_name)

                # Check if asset is imported
                asset_imported = self.asset_data.get('imported', False)

                if asset_imported:
                    # Show imported asset normally with type icons
                    self.setForeground(0, Qt.GlobalColor.black)

                    # Add type-specific icon or thumbnail
                    if self.asset_type == "sprites":
                        # Try to load pre-generated thumbnail (already has first frame for strips)
                        thumb_path = self.asset_data.get('thumbnail', '')
                        file_path = self.asset_data.get('file_path', '')
                        if thumb_path and self.load_sprite_thumbnail(thumb_path):
                            # Thumbnail loaded successfully, just show name
                            self.setText(0, self.asset_name)
                        elif file_path and self.load_sprite_thumbnail(file_path):
                            # Fallback to full sprite if no thumbnail
                            self.setText(0, self.asset_name)
                        else:
                            # Fallback to emoji if image loading fails
                            self.setText(0, f"🖼️ {self.asset_name}")
                    elif self.asset_type == "backgrounds":
                        # Try to load pre-generated thumbnail first
                        thumb_path = self.asset_data.get('thumbnail', '')
                        file_path = self.asset_data.get('file_path', '')
                        if thumb_path and self.load_sprite_thumbnail(thumb_path):
                            # Thumbnail loaded successfully, just show name
                            self.setText(0, self.asset_name)
                        elif file_path and self.load_sprite_thumbnail(file_path):
                            # Fallback to full image if no thumbnail
                            self.setText(0, self.asset_name)
                        else:
                            # Fallback to emoji if image loading fails
                            self.setText(0, f"🖼️ {self.asset_name}")
                    elif self.asset_type == "sounds":
                        self.setText(0, f"🔊 {self.asset_name}")
                    elif self.asset_type == "objects":
                        # Try to load the object's assigned sprite as thumbnail
                        sprite_name = self.asset_data.get('sprite', '')
                        if sprite_name and self.load_object_sprite_thumbnail(sprite_name):
                            # Thumbnail loaded successfully, just show name
                            self.setText(0, self.asset_name)
                        else:
                            # Fallback to emoji if no sprite assigned or loading fails
                            self.setText(0, f"📦 {self.asset_name}")
                    elif self.asset_type == "rooms":
                        self.setText(0, f"🏠 {self.asset_name}")
                    elif self.asset_type == "scripts":
                        self.setText(0, f"📜 {self.asset_name}")
                    elif self.asset_type == "fonts":
                        self.setText(0, f"🔤 {self.asset_name}")
                else:
                    # Show not-imported assets in gray
                    self.setText(0, f"❌ {self.asset_name} (not imported)")
                    self.setForeground(0, Qt.GlobalColor.gray)

                # Make assets selectable and draggable
                self.setFlags(Qt.ItemFlag.ItemIsEnabled |
                            Qt.ItemFlag.ItemIsSelectable |
                            Qt.ItemFlag.ItemIsDragEnabled)

    def load_sprite_thumbnail(self, file_path):
            """Load sprite as thumbnail icon for tree item"""
            try:
                from PySide6.QtGui import QPixmap, QIcon

                if not file_path:
                    return False

                # Get the tree widget to access project path
                tree_widget = self.treeWidget()
                if not tree_widget or not hasattr(tree_widget, 'project_path'):
                    return False

                # Construct absolute path from relative file_path
                project_root = Path(tree_widget.project_path)

                # Handle both relative and absolute paths
                if Path(file_path).is_absolute():
                    abs_path = Path(file_path)
                else:
                    abs_path = project_root / file_path

                if not abs_path.exists():
                    print(f"⚠️ Thumbnail file not found: {abs_path}")
                    return False

                # Load image from disk
                with open(abs_path, 'rb') as f:
                    image_data = f.read()

                pixmap = QPixmap()
                pixmap.loadFromData(image_data)

                if not pixmap.isNull():
                    # Scale to thumbnail size (32x32 for better visibility)
                    scaled_pixmap = pixmap.scaled(
                        32, 32,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.setIcon(0, QIcon(scaled_pixmap))
                    return True
                else:
                    print(f"⚠️ Failed to load pixmap from: {abs_path}")

            except Exception as e:
                print(f"⚠️ Failed to load sprite thumbnail: {e}")

            return False

    def load_object_sprite_thumbnail(self, sprite_name):
        """Load the assigned sprite as thumbnail icon for an object"""
        try:
            from PySide6.QtGui import QPixmap, QIcon
            import json

            if not sprite_name:
                return False

            # Get the tree widget to access project path and asset manager
            tree_widget = self.treeWidget()
            if not tree_widget or not hasattr(tree_widget, 'project_path'):
                return False

            project_root = Path(tree_widget.project_path)

            # Try to get sprite data from asset manager if available
            sprite_file_path = None
            sprite_data = None

            if hasattr(tree_widget, 'project_manager') and tree_widget.project_manager:
                if tree_widget.project_manager.asset_manager:
                    sprite_data = tree_widget.project_manager.asset_manager.get_asset('sprites', sprite_name)
                    if sprite_data:
                        sprite_file_path = sprite_data.get('file_path', '')

            # If asset manager didn't have it, try loading from project.json directly
            if not sprite_data:
                project_file = project_root / "project.json"
                if project_file.exists():
                    try:
                        with open(project_file, 'r') as f:
                            project_data = json.load(f)
                        sprite_data = project_data.get('assets', {}).get('sprites', {}).get(sprite_name)
                        if sprite_data:
                            sprite_file_path = sprite_data.get('file_path', '')
                    except Exception:
                        pass

            # If we still didn't get it, construct the path
            if not sprite_file_path:
                sprite_file_path = f"sprites/{sprite_name}.png"

            # Construct absolute path
            if Path(sprite_file_path).is_absolute():
                abs_path = Path(sprite_file_path)
            else:
                abs_path = project_root / sprite_file_path

            if not abs_path.exists():
                print(f"⚠️ Object sprite thumbnail not found: {abs_path}")
                return False

            # Load image from disk
            pixmap = QPixmap(str(abs_path))

            if not pixmap.isNull():
                # For sprite strips, extract only the first frame
                if sprite_data:
                    animation_type = sprite_data.get('animation_type', 'single')
                    if animation_type in ('strip_h', 'strip_v', 'grid'):
                        frame_width = sprite_data.get('frame_width', pixmap.width())
                        frame_height = sprite_data.get('frame_height', pixmap.height())
                        # Extract first frame (top-left corner)
                        pixmap = pixmap.copy(0, 0, frame_width, frame_height)

                # Scale to thumbnail size (32x32 for consistency)
                scaled_pixmap = pixmap.scaled(
                    32, 32,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setIcon(0, QIcon(scaled_pixmap))
                return True
            else:
                print(f"⚠️ Failed to load pixmap for object sprite: {sprite_name}")

        except Exception as e:
            print(f"⚠️ Failed to load object sprite thumbnail: {e}")

        return False
