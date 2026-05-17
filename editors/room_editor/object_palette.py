#!/usr/bin/env python3
"""
Object Palette widget for Room Editor
Displays available objects for placement in the room
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPixmap

from core.logger import get_logger
from .object_render import object_color, create_default_sprite
logger = get_logger(__name__)


class ObjectPalette(QWidget):
    """Widget for selecting objects to place"""

    object_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.available_objects = {}
        self.project_path = None
        self.project_data = None
        self.sprite_cache = {}

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(self.tr("Objects"))
        title.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(title)

        # Object list
        self.object_list = QListWidget()
        self.object_list.setIconSize(QSize(32, 32))
        self.object_list.itemClicked.connect(self.on_object_clicked)
        layout.addWidget(self.object_list)

        # Clear selection button
        clear_btn = QPushButton(self.tr("Clear Selection"))
        clear_btn.clicked.connect(self.clear_selection)
        layout.addWidget(clear_btn)

    def set_project_info(self, project_path, project_data):
        """Set project information for sprite loading"""
        self.project_path = Path(project_path) if project_path else None
        self.project_data = project_data
        if hasattr(self, 'sprite_cache'):
            self.sprite_cache.clear()
        logger.debug("Updated project info, cleared sprite cache")

    def set_available_objects(self, objects_dict):
        """Set available objects from project data"""
        self.available_objects = objects_dict
        self.refresh_object_list()

    def refresh_object_list(self):
        """Refresh the object list with sprite previews"""
        self.object_list.clear()

        for object_name, object_data in self.available_objects.items():
            item = QListWidgetItem(object_name)
            item.setData(Qt.UserRole, object_name)

            # Try to load sprite preview
            sprite_icon = self.load_object_sprite_icon(object_name, object_data)
            if sprite_icon:
                item.setIcon(sprite_icon)

            self.object_list.addItem(item)

    def load_object_sprite_icon(self, object_name, object_data):
        """Load sprite icon for object list"""
        if not self.project_data or not self.project_path:
            return self.create_default_icon(object_name)

        try:
            sprite_name = object_data.get('sprite', '')

            if not sprite_name:
                return self.create_default_icon(object_name)

            # Find the sprite file
            sprites = self.project_data.get('assets', {}).get('sprites', {})
            if sprite_name not in sprites:
                return self.create_default_icon(object_name)

            sprite_data = sprites[sprite_name]
            sprite_file_path = sprite_data.get('file_path', '')

            if not sprite_file_path:
                return self.create_default_icon(object_name)

            # Try to load the sprite file
            full_sprite_path = self.project_path / sprite_file_path
            if full_sprite_path.exists():
                pixmap = QPixmap(str(full_sprite_path))

                if not pixmap.isNull():
                    # Scale sprite to icon size (32x32)
                    pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    return pixmap

            return self.create_default_icon(object_name)

        except Exception as e:
            logger.error(f"Error loading sprite icon for {object_name}: {e}")
            return self.create_default_icon(object_name)

    def create_default_icon(self, object_name):
        """Create a default 32px icon for objects without sprites.

        Delegates to the shared renderer with the palette's own shorter
        abbreviation rule (>4 chars -> first 2 + "..") so the icons keep
        their previous appearance while sharing the drawing code.
        """
        return create_default_sprite(object_name, abbrev_over=4, abbrev_keep=2)

    def get_object_color(self, object_name):
        """Get color for object (same as canvas; delegates to shared object_render)."""
        return object_color(object_name)

    def on_object_clicked(self, item):
        """Handle object selection"""
        object_name = item.data(Qt.UserRole)
        self.object_selected.emit(object_name)

    def clear_selection(self):
        """Clear object selection"""
        self.object_list.clearSelection()
        self.object_selected.emit("")
