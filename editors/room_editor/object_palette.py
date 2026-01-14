#!/usr/bin/env python3
"""
Object Palette widget for Room Editor
Displays available objects for placement in the room
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPen

from core.logger import get_logger
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
        """Create a default icon for objects without sprites"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw colored rectangle
        color = self.get_object_color(object_name)
        painter.fillRect(0, 0, 32, 32, color)

        # Draw border
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawRect(0, 0, 31, 31)

        # Draw abbreviated name
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)

        # Abbreviate object name
        name = object_name
        if len(name) > 4:
            name = name[:2] + ".."

        # Center text
        text_rect = painter.fontMetrics().boundingRect(name)
        x = (32 - text_rect.width()) // 2
        y = (32 + text_rect.height()) // 2 - 2
        painter.drawText(x, y, name)

        painter.end()
        return pixmap

    def get_object_color(self, object_name):
        """Get color for object (same as canvas)"""
        colors = {
            'player': QColor("#00FF00"),
            'enemy': QColor("#FF0000"),
            'wall': QColor("#808080"),
            'coin': QColor("#FFFF00"),
            'door': QColor("#8B4513"),
            'key': QColor("#FFD700"),
        }

        if object_name not in colors:
            hash_val = hash(object_name) % 6
            default_colors = [
                QColor("#FF6B6B"), QColor("#4ECDC4"), QColor("#45B7D1"),
                QColor("#96CEB4"), QColor("#FECA57"), QColor("#FF9FF3")
            ]
            return default_colors[hash_val]

        return colors[object_name]

    def on_object_clicked(self, item):
        """Handle object selection"""
        object_name = item.data(Qt.UserRole)
        self.object_selected.emit(object_name)

    def clear_selection(self):
        """Clear object selection"""
        self.object_list.clearSelection()
        self.object_selected.emit("")
