#!/usr/bin/env python3
"""
Room Preview Generator Utility
Generates preview images for rooms without requiring a full room editor
"""

from pathlib import Path
from typing import Dict, Any, Optional
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QFont
from PySide6.QtCore import Qt, QRect


class RoomPreviewGenerator:
    """Generates room preview images from room data"""

    def __init__(self, project_path: str, project_data: Dict[str, Any]):
        """
        Initialize the preview generator.

        Args:
            project_path: Path to the project directory
            project_data: Full project data dictionary
        """
        self.project_path = Path(project_path) if project_path else None
        self.project_data = project_data or {}
        self.sprite_cache = {}

    def generate_preview(self, room_data: Dict[str, Any],
                         max_width: int = 200, max_height: int = 150) -> QPixmap:
        """
        Generate a preview image for a room.

        Args:
            room_data: Room data dictionary containing width, height, instances, etc.
            max_width: Maximum width of the preview
            max_height: Maximum height of the preview

        Returns:
            QPixmap containing the room preview
        """
        room_width = room_data.get('width', 800)
        room_height = room_data.get('height', 600)

        # Calculate scale to fit within max dimensions while maintaining aspect ratio
        scale_x = max_width / room_width
        scale_y = max_height / room_height
        scale = min(scale_x, scale_y)

        # Calculate preview dimensions
        preview_width = int(room_width * scale)
        preview_height = int(room_height * scale)

        # Create pixmap
        pixmap = QPixmap(preview_width, preview_height)
        pixmap.fill(Qt.transparent)

        # Create painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Apply scale transformation
        painter.scale(scale, scale)

        # Draw background
        self._draw_background(painter, room_data, room_width, room_height)

        # Draw instances
        instances = room_data.get('instances', [])
        for instance_data in instances:
            self._draw_instance(painter, instance_data)

        # Draw room border
        painter.setPen(QPen(QColor("#333333"), 2 / scale))
        painter.drawRect(0, 0, room_width, room_height)

        painter.end()

        return pixmap

    def _draw_background(self, painter: QPainter, room_data: Dict[str, Any],
                         room_width: int, room_height: int):
        """Draw the room background color and image"""
        # Fill with background color
        bg_color_str = room_data.get('background_color', '#87CEEB')
        bg_color = QColor(bg_color_str)
        painter.fillRect(0, 0, room_width, room_height, bg_color)

        # Draw background image if present
        bg_image_name = room_data.get('background_image', '')
        if not bg_image_name:
            return

        bg_pixmap = self._load_background_image(bg_image_name)
        if not bg_pixmap or bg_pixmap.isNull():
            return

        tile_h = room_data.get('tile_horizontal', False)
        tile_v = room_data.get('tile_vertical', False)

        if tile_h or tile_v:
            img_width = bg_pixmap.width()
            img_height = bg_pixmap.height()

            x_count = (room_width // img_width) + 2 if tile_h else 1
            y_count = (room_height // img_height) + 2 if tile_v else 1

            for x_tile in range(x_count):
                for y_tile in range(y_count):
                    x_pos = x_tile * img_width if tile_h else 0
                    y_pos = y_tile * img_height if tile_v else 0

                    if x_pos < room_width and y_pos < room_height:
                        painter.drawPixmap(x_pos, y_pos, bg_pixmap)
        else:
            painter.drawPixmap(0, 0, room_width, room_height, bg_pixmap)

    def _draw_instance(self, painter: QPainter, instance_data: Dict[str, Any]):
        """Draw an object instance"""
        object_name = instance_data.get('object_name', '')
        x = instance_data.get('x', 0)
        y = instance_data.get('y', 0)
        rotation = instance_data.get('rotation', 0)
        scale_x = instance_data.get('scale_x', 1.0)
        scale_y = instance_data.get('scale_y', 1.0)
        visible = instance_data.get('visible', True)

        if not visible:
            return

        # Load sprite
        sprite = self._load_object_sprite(object_name)

        if sprite and not sprite.isNull():
            width = sprite.width()
            height = sprite.height()
        else:
            width = 32
            height = 32

        # Apply transformations
        painter.save()

        if rotation != 0 or scale_x != 1.0 or scale_y != 1.0:
            # Move origin to instance center
            center_x = x + (width * scale_x) / 2
            center_y = y + (height * scale_y) / 2
            painter.translate(center_x, center_y)

            if rotation != 0:
                painter.rotate(rotation)

            if scale_x != 1.0 or scale_y != 1.0:
                painter.scale(scale_x, scale_y)

            # Draw at offset position (centered)
            if sprite and not sprite.isNull():
                painter.drawPixmap(int(-width / 2), int(-height / 2), sprite)
            else:
                self._draw_placeholder(painter, object_name,
                                       int(-width / 2), int(-height / 2), width, height)
        else:
            # No transformation needed - draw normally
            if sprite and not sprite.isNull():
                painter.drawPixmap(x, y, sprite)
            else:
                self._draw_placeholder(painter, object_name, x, y, width, height)

        painter.restore()

    def _draw_placeholder(self, painter: QPainter, object_name: str,
                          x: int, y: int, width: int, height: int):
        """Draw a placeholder rectangle for objects without sprites"""
        color = self._get_object_color(object_name)
        painter.fillRect(x, y, width, height, color)
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawRect(x, y, width, height)

        # Draw object name
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)

        name = object_name
        if len(name) > 6:
            name = name[:4] + ".."
        painter.drawText(x + 2, y + 12, name)

    def _get_object_color(self, object_name: str) -> QColor:
        """Get a consistent color for an object based on its name"""
        hash_val = hash(object_name)
        r = (hash_val & 0xFF0000) >> 16
        g = (hash_val & 0x00FF00) >> 8
        b = hash_val & 0x0000FF
        return QColor(r, g, b, 180)

    def _load_background_image(self, image_name: str) -> Optional[QPixmap]:
        """Load a background image from the project"""
        if not self.project_data or not self.project_path:
            return None

        cache_key = f"bg_{image_name}"
        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]

        try:
            for asset_type in ['backgrounds', 'sprites']:
                assets = self.project_data.get('assets', {}).get(asset_type, {})
                if image_name in assets:
                    asset_data = assets[image_name]
                    file_path = asset_data.get('file_path', '')

                    if file_path:
                        full_path = self.project_path / file_path
                        if full_path.exists():
                            pixmap = QPixmap(str(full_path))
                            if not pixmap.isNull():
                                self.sprite_cache[cache_key] = pixmap
                                return pixmap
            return None
        except Exception as e:
            print(f"Error loading background image {image_name}: {e}")
            return None

    def _load_object_sprite(self, object_name: str) -> Optional[QPixmap]:
        """Load sprite for an object from the project"""
        if not self.project_data or not self.project_path:
            return None

        if object_name in self.sprite_cache:
            return self.sprite_cache[object_name]

        try:
            objects = self.project_data.get('assets', {}).get('objects', {})
            if object_name not in objects:
                return None

            object_data = objects[object_name]
            sprite_name = object_data.get('sprite', '')

            if not sprite_name:
                return None

            sprites = self.project_data.get('assets', {}).get('sprites', {})
            if sprite_name not in sprites:
                return None

            sprite_data = sprites[sprite_name]
            sprite_file_path = sprite_data.get('file_path', '')

            if not sprite_file_path:
                return None

            full_sprite_path = self.project_path / sprite_file_path
            if not full_sprite_path.exists():
                return None

            pixmap = QPixmap(str(full_sprite_path))

            if pixmap.isNull():
                return None

            # Extract first frame if animated
            animation_type = sprite_data.get('animation_type', 'single')
            frames = sprite_data.get('frames', 1)

            if frames > 1 and animation_type != 'single':
                frame_width = sprite_data.get('frame_width', pixmap.width())
                frame_height = sprite_data.get('frame_height', pixmap.height())

                frame_width = min(frame_width, pixmap.width())
                frame_height = min(frame_height, pixmap.height())

                pixmap = pixmap.copy(0, 0, frame_width, frame_height)

            self.sprite_cache[object_name] = pixmap
            return pixmap

        except Exception as e:
            print(f"Error loading object sprite {object_name}: {e}")
            return None

    def clear_cache(self):
        """Clear the sprite cache"""
        self.sprite_cache.clear()
