#!/usr/bin/env python3
"""
Room Canvas widget for Room Editor
Handles drawing and interaction with room instances
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QFont, QUndoStack

from editors.room_undo_commands import (
    AddInstanceCommand, RemoveInstanceCommand, MoveInstanceCommand,
    BatchAddInstancesCommand, BatchRemoveInstancesCommand,
    AddTileCommand, BatchAddTilesCommand, BatchRemoveTilesCommand
)
from .object_instance import ObjectInstance

from core.logger import get_logger
logger = get_logger(__name__)


class RoomCanvas(QWidget):
    """Canvas widget for displaying and editing the room"""

    instance_selected = Signal(object)
    instance_moved = Signal(object)
    instance_added = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(64, 64)
        self.room_width = 1024
        self.room_height = 768
        self.background_color = QColor("#87CEEB")

        # Legacy single-background fields (kept for compat)
        self.background_image_name = ''
        self.tile_horizontal = False
        self.tile_vertical = False
        self.bg_hspeed = 0.0
        self.bg_vspeed = 0.0

        # Multi-layer backgrounds (list of 8 dicts)
        self.bg_layers = []

        self.instances = []
        # CHANGED: Support multiple selected instances
        self.selected_instances = []  # List of selected instances
        self.dragging = False
        self.drag_offset = QPoint(0, 0)
        self.current_object_type = None
        self.painting_mode = False
        self.last_painted_grid = None
        self.erasing_mode = False

        # Rubber band selection
        self.rubber_band_selecting = False
        self.rubber_band_start = None
        self.rubber_band_rect = None

        # Undo/Redo system
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)
        self.painted_instances = []
        self.erased_instances = []
        self.move_start_positions = {}  # Dict of instance -> (old_x, old_y)

        # Instance preview
        self.preview_position = None
        self.show_preview = False

        # Clipboard for copy/paste
        self.clipboard_instances = []
        self.last_mouse_pos = QPoint(0, 0)

        self.grid_enabled = True
        self.grid_size = 32
        self.snap_to_grid = True

        # Tile layer
        self.tiles = []  # List of tile dicts
        self.tile_painting_mode = False
        self.tile_erasing_mode = False
        self.current_tile_info = None  # Dict with background_name, tile_x, tile_y, width, height
        self.painted_tiles = []
        self.erased_tiles = []
        self.last_painted_tile_grid = None
        self.tile_pixmap_cache = {}  # (bg_name, tx, ty, w, h) -> QPixmap
        self._tile_layer_dirty = True
        self._tile_layer_cache = None  # Pre-composited tile layer QPixmap

        # Sprite cache and project info
        self.sprite_cache = {}
        self.project_path = None
        self.project_data = None

        self.setMouseTracking(True)

    def set_project_info(self, project_path, project_data):
        """Set project information for sprite loading"""
        self.project_path = Path(project_path) if project_path else None
        self.project_data = project_data
        self.sprite_cache.clear()

    def set_room_properties(self, width, height, bg_color, bg_image='', tile_h=False, tile_v=False,
                            bg_hspeed=0.0, bg_vspeed=0.0, bg_stretch=True, bg_layers=None):
        """Set room properties including background"""
        self.room_width = width
        self.room_height = height

        if isinstance(bg_color, str):
            self.background_color = QColor(bg_color)
        else:
            self.background_color = bg_color

        self.background_image_name = bg_image
        self.tile_horizontal = tile_h
        self.tile_vertical = tile_v
        self.bg_hspeed = bg_hspeed
        self.bg_vspeed = bg_vspeed
        self.bg_stretch = bg_stretch
        self.bg_layers = bg_layers or []

        self.setFixedSize(width, height)
        self.update()

    def set_current_object_type(self, object_name):
        """Set the current object type for placement"""
        self.current_object_type = object_name
        # Clear tile mode when selecting an object
        if object_name:
            self.current_tile_info = None

        if object_name:
            self.show_preview = True
        else:
            self.show_preview = False
            self.preview_position = None

        self.update()

    # ================================================================
    # Tile methods
    # ================================================================

    def set_current_tile(self, tile_info):
        """Set the current tile for placement (clears object mode)"""
        self.current_tile_info = tile_info
        self.current_object_type = None
        self.show_preview = bool(tile_info)
        self.update()

    def clear_tile_mode(self):
        """Exit tile placement mode"""
        self.current_tile_info = None
        self.show_preview = False
        self.preview_position = None
        self.update()

    def load_tiles(self, tiles_data):
        """Load tiles from data"""
        self.tiles = [dict(t) for t in tiles_data]
        self._tile_layer_dirty = True
        self.update()

    def get_tiles(self):
        """Get all tiles as list of dicts"""
        return [dict(t) for t in self.tiles]

    def find_tile_at(self, pos):
        """Find a tile at the given position"""
        px, py = pos.x(), pos.y()
        for tile in reversed(self.tiles):
            tx, ty = tile['x'], tile['y']
            tw, th = tile['width'], tile['height']
            if tx <= px < tx + tw and ty <= py < ty + th:
                return tile
        return None

    def get_tile_pixmap(self, tile):
        """Get a cropped QPixmap for a tile from cache"""
        key = (tile['background_name'], tile['tile_x'], tile['tile_y'],
               tile['width'], tile['height'])

        if key in self.tile_pixmap_cache:
            return self.tile_pixmap_cache[key]

        # Load the background image
        bg_pixmap = self.load_background_image(tile['background_name'])
        if not bg_pixmap or bg_pixmap.isNull():
            return None

        # Crop the tile region
        cropped = bg_pixmap.copy(tile['tile_x'], tile['tile_y'],
                                 tile['width'], tile['height'])
        if not cropped.isNull():
            self.tile_pixmap_cache[key] = cropped
            return cropped
        return None

    def draw_tiles(self, painter):
        """Draw all tiles (uses pre-composited cache for performance)"""
        if not self.tiles:
            return

        if self._tile_layer_dirty or self._tile_layer_cache is None:
            self._recomposite_tile_layer()
            self._tile_layer_dirty = False

        if self._tile_layer_cache and not self._tile_layer_cache.isNull():
            painter.drawPixmap(0, 0, self._tile_layer_cache)

    def _recomposite_tile_layer(self):
        """Pre-composite all tiles into a single pixmap"""
        self._tile_layer_cache = QPixmap(self.room_width, self.room_height)
        self._tile_layer_cache.fill(Qt.transparent)

        p = QPainter(self._tile_layer_cache)
        # Sort by depth descending (higher depth = behind)
        sorted_tiles = sorted(self.tiles, key=lambda t: t.get('depth', 1000000), reverse=True)
        for tile in sorted_tiles:
            tile_pix = self.get_tile_pixmap(tile)
            if tile_pix:
                p.drawPixmap(tile['x'], tile['y'], tile_pix)
        p.end()

    def draw_tile_preview(self, painter):
        """Draw a semi-transparent preview of the tile being placed"""
        if not self.preview_position or not self.current_tile_info:
            return

        tile_w = self.current_tile_info['width']
        tile_h = self.current_tile_info['height']

        # Snap to tile grid
        snapped_pos = self._snap_to_tile_grid(self.preview_position)

        tile_pix = self.get_tile_pixmap(self.current_tile_info)
        painter.setOpacity(0.5)
        if tile_pix:
            painter.drawPixmap(snapped_pos.x(), snapped_pos.y(), tile_pix)
        else:
            painter.fillRect(snapped_pos.x(), snapped_pos.y(), tile_w, tile_h,
                           QColor(128, 128, 255, 128))
        painter.setOpacity(1.0)

        # Outline
        painter.setPen(QPen(QColor("#00FF00"), 2, Qt.DashLine))
        painter.drawRect(snapped_pos.x(), snapped_pos.y(), tile_w, tile_h)

    def _snap_to_tile_grid(self, pos):
        """Snap position to tile-sized grid"""
        if not self.current_tile_info:
            return self.snap_to_grid_pos(pos)

        tw = self.current_tile_info['width']
        th = self.current_tile_info['height']
        x = int(pos.x() // tw) * tw
        y = int(pos.y() // th) * th
        return QPoint(x, y)

    def add_instance(self, instance, use_undo=True):
        """Add an object instance to the room"""
        if use_undo:
            command = AddInstanceCommand(self, instance, f"Add {instance.object_name}")
            self.undo_stack.push(command)
        else:
            self.instances.append(instance)
            self.instance_added.emit(instance)
            self.update()

    def remove_instance(self, instance, use_undo=True):
        """Remove an object instance from the room"""
        if instance not in self.instances:
            logger.debug(f"Instance {instance.object_name} not in instances list")
            return

        if use_undo:
            command = RemoveInstanceCommand(self, instance, f"Delete {instance.object_name}")
            self.undo_stack.push(command)
        else:
            if instance in self.instances:
                self.instances.remove(instance)
            # Remove from selection if selected
            if instance in self.selected_instances:
                self.selected_instances.remove(instance)
            self.update()

    def remove_instances(self, instances, use_undo=True):
        """Remove multiple instances at once"""
        logger.debug(f"remove_instances called with {len(instances)} instances, use_undo={use_undo}")

        if not instances:
            logger.debug("No instances to remove")
            return

        # Make a copy of the list to avoid modification during iteration
        instances_to_remove = list(instances)

        # Verify all instances exist before proceeding
        valid_instances = [inst for inst in instances_to_remove if inst in self.instances]

        if not valid_instances:
            logger.debug("No valid instances found to remove")
            return

        if use_undo:
            if len(valid_instances) > 1:
                logger.debug(f"Creating BatchRemoveInstancesCommand for {len(valid_instances)} instances")
                command = BatchRemoveInstancesCommand(self, valid_instances)
                self.undo_stack.push(command)
            else:
                logger.debug("Creating RemoveInstanceCommand for 1 instance")
                command = RemoveInstanceCommand(self, valid_instances[0])
                self.undo_stack.push(command)
        else:
            logger.debug(f"Removing {len(valid_instances)} instances directly (no undo)")
            for instance in valid_instances:
                if instance in self.instances:
                    self.instances.remove(instance)
                if instance in self.selected_instances:
                    self.selected_instances.remove(instance)
            self.update()

    def clear_instances(self):
        """Clear all instances"""
        self.instances.clear()
        self.selected_instances.clear()
        self.update()

    def get_instances(self):
        """Get all instances as dictionaries"""
        return [instance.to_dict() for instance in self.instances]

    def load_instances(self, instances_data):
        """Load instances from data"""
        self.instances.clear()
        for instance_data in instances_data:
            instance = ObjectInstance.from_dict(instance_data)
            self.instances.append(instance)
        self.update()

    def snap_to_grid_pos(self, pos):
        """Snap position to grid - places object in the grid cell where clicked"""
        if self.snap_to_grid and self.grid_enabled:
            grid_x = int(pos.x() // self.grid_size)
            grid_y = int(pos.y() // self.grid_size)
            x = grid_x * self.grid_size
            y = grid_y * self.grid_size
            return QPoint(x, y)
        return pos

    def find_instance_at(self, pos):
        """Find instance at given position"""
        for instance in reversed(self.instances):
            width = getattr(instance, '_sprite_width', 32)
            height = getattr(instance, '_sprite_height', 32)
            instance_rect = QRect(instance.x, instance.y, width, height)
            if instance_rect.contains(pos):
                return instance
        return None

    def find_instances_in_rect(self, rect):
        """Find all instances within a rectangle"""
        found_instances = []
        for instance in self.instances:
            width = getattr(instance, '_sprite_width', 32)
            height = getattr(instance, '_sprite_height', 32)
            instance_rect = QRect(instance.x, instance.y, width, height)

            # Check if rectangles intersect
            if rect.intersects(instance_rect):
                found_instances.append(instance)

        return found_instances

    def select_instance(self, instance, add_to_selection=False):
        """Select an instance (or add to selection with Shift)"""
        if not add_to_selection:
            self.selected_instances.clear()

        if instance and instance not in self.selected_instances:
            self.selected_instances.append(instance)

        # Emit with first selected instance or None
        self.instance_selected.emit(
            self.selected_instances[0] if self.selected_instances else None
        )
        self.update()

    def deselect_all(self):
        """Deselect all instances"""
        self.selected_instances.clear()
        self.instance_selected.emit(None)
        self.update()

    def get_selected_count(self):
        """Get number of selected instances"""
        return len(self.selected_instances)

    def get_primary_selected_instance(self):
        """Get the primary selected instance (first in list)"""
        return self.selected_instances[0] if self.selected_instances else None

    # Copy/Paste/Cut methods
    def copy_selected_instance(self):
        """Copy the selected instance to clipboard"""
        if self.selected_instance:
            self.clipboard_instances = [self.selected_instance.to_dict()]
            logger.debug(f"Copied {self.selected_instance.object_name} to clipboard")
            return True
        return False

    def copy_selected_instances(self):
        """Copy the selected instances to clipboard"""
        if self.selected_instances:
            self.clipboard_instances = [inst.to_dict() for inst in self.selected_instances]
            logger.debug(f"Copied {len(self.selected_instances)} instance(s) to clipboard")
            return True
        return False

    def paste_instances(self):
        """Paste instances from clipboard at mouse position"""
        if not self.clipboard_instances:
            logger.debug("Clipboard is empty")
            return False

        paste_pos = self.snap_to_grid_pos(self.last_mouse_pos)
        first_instance_data = self.clipboard_instances[0]
        offset_x = paste_pos.x() - first_instance_data['x']
        offset_y = paste_pos.y() - first_instance_data['y']

        pasted_instances = []
        for instance_data in self.clipboard_instances:
            new_instance = ObjectInstance(
                instance_data['object_name'],
                instance_data['x'] + offset_x,
                instance_data['y'] + offset_y
            )
            new_instance.rotation = instance_data.get('rotation', 0)
            new_instance.scale_x = instance_data.get('scale_x', 1.0)
            new_instance.scale_y = instance_data.get('scale_y', 1.0)
            new_instance.visible = instance_data.get('visible', True)

            pasted_instances.append(new_instance)
            self.instances.append(new_instance)

        if len(pasted_instances) == 1:
            command = AddInstanceCommand(self, pasted_instances[0], f"Paste {pasted_instances[0].object_name}", already_added=True)
        else:
            command = BatchAddInstancesCommand(self, pasted_instances, "Paste Instances", already_added=True)

        self.undo_stack.push(command)

        if pasted_instances:
            self.selected_instance = pasted_instances[0]
            self.instance_selected.emit(self.selected_instance)

        self.update()
        logger.debug(f"Pasted {len(pasted_instances)} instance(s)")
        return True

    def cut_selected_instance(self):
        """Cut the selected instance (copy + delete)"""
        if not self.selected_instance:
            logger.debug("No instance selected to cut")
            return False

        self.clipboard_instances = [self.selected_instance.to_dict()]
        instance_to_cut = self.selected_instance
        command = RemoveInstanceCommand(self, instance_to_cut, f"Cut {instance_to_cut.object_name}")
        self.undo_stack.push(command)

        logger.debug(f"Cut {instance_to_cut.object_name} to clipboard")
        return True

    def cut_selected_instances(self):
        """Cut the selected instances (copy + delete)"""
        if not self.selected_instances:
            logger.debug("No instances selected to cut")
            return False

        self.clipboard_instances = [inst.to_dict() for inst in self.selected_instances]
        instances_to_cut = self.selected_instances.copy()

        if len(instances_to_cut) > 1:
            command = BatchRemoveInstancesCommand(self, instances_to_cut)
        else:
            command = RemoveInstanceCommand(self, instances_to_cut[0], f"Cut {instances_to_cut[0].object_name}")

        self.undo_stack.push(command)
        logger.debug(f"Cut {len(instances_to_cut)} instance(s) to clipboard")
        return True


    def duplicate_selected_instance(self):
        """Duplicate the selected instance (copy + paste at offset)"""
        if not self.selected_instance:
            logger.debug("No instance selected to duplicate")
            return False

        self.clipboard_instances = [self.selected_instance.to_dict()]
        offset_x = self.grid_size
        offset_y = self.grid_size

        instance_data = self.clipboard_instances[0]
        new_instance = ObjectInstance(
            instance_data['object_name'],
            instance_data['x'] + offset_x,
            instance_data['y'] + offset_y
        )
        new_instance.rotation = instance_data.get('rotation', 0)
        new_instance.scale_x = instance_data.get('scale_x', 1.0)
        new_instance.scale_y = instance_data.get('scale_y', 1.0)
        new_instance.visible = instance_data.get('visible', True)

        self.instances.append(new_instance)
        command = AddInstanceCommand(self, new_instance, f"Duplicate {new_instance.object_name}", already_added=True)
        self.undo_stack.push(command)

        self.selected_instance = new_instance
        self.instance_selected.emit(new_instance)

        self.update()
        logger.debug(f"Duplicated {new_instance.object_name}")
        return True

    def duplicate_selected_instances(self):
        """Duplicate the selected instances (copy + paste at offset)"""
        if not self.selected_instances:
            logger.debug("No instances selected to duplicate")
            return False

        self.clipboard_instances = [inst.to_dict() for inst in self.selected_instances]
        offset_x = self.grid_size
        offset_y = self.grid_size

        duplicated_instances = []
        for instance_data in self.clipboard_instances:
            new_instance = ObjectInstance(
                instance_data['object_name'],
                instance_data['x'] + offset_x,
                instance_data['y'] + offset_y
            )
            new_instance.rotation = instance_data.get('rotation', 0)
            new_instance.scale_x = instance_data.get('scale_x', 1.0)
            new_instance.scale_y = instance_data.get('scale_y', 1.0)
            new_instance.visible = instance_data.get('visible', True)

            duplicated_instances.append(new_instance)
            self.instances.append(new_instance)

        if len(duplicated_instances) > 1:
            command = BatchAddInstancesCommand(self, duplicated_instances, "Duplicate Instances", already_added=True)
        else:
            command = AddInstanceCommand(self, duplicated_instances[0], f"Duplicate {duplicated_instances[0].object_name}", already_added=True)

        self.undo_stack.push(command)

        # Select the duplicated instances
        self.selected_instances = duplicated_instances
        self.instance_selected.emit(self.selected_instances[0] if self.selected_instances else None)

        self.update()
        logger.debug(f"Duplicated {len(duplicated_instances)} instance(s)")
        return True

    # Paint event and drawing methods
    def paintEvent(self, event):
        """Paint the room canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.draw_background(painter)

        # Draw tile layer (behind instances)
        self.draw_tiles(painter)

        if self.grid_enabled:
            self.draw_grid(painter)

        painter.setPen(QPen(QColor("#333333"), 2))
        painter.drawRect(0, 0, self.room_width, self.room_height)

        for instance in self.instances:
            self.draw_instance(painter, instance)

        # Foreground background layers (on top of instances)
        self.draw_foregrounds(painter)

        # Highlight all selected instances
        for instance in self.selected_instances:
            self.draw_selection(painter, instance)

        # Draw rubber band selection rectangle
        if self.rubber_band_selecting and self.rubber_band_rect:
            painter.setPen(QPen(QColor("#0080FF"), 2, Qt.DashLine))
            painter.setBrush(QBrush(QColor(0, 128, 255, 50)))
            painter.drawRect(self.rubber_band_rect)

        if self.show_preview and self.preview_position and self.current_object_type:
            self.draw_instance_preview(painter)

        if self.show_preview and self.preview_position and self.current_tile_info:
            self.draw_tile_preview(painter)

    def draw_background(self, painter):
        """Draw room background (color and/or multi-layer images)"""
        painter.fillRect(0, 0, self.room_width, self.room_height, self.background_color)

        # Use multi-layer backgrounds if available, else fall back to legacy single bg
        if self.bg_layers:
            for layer in self.bg_layers:
                if not layer.get('visible') or layer.get('foreground'):
                    continue
                self._draw_bg_layer(painter, layer)
        elif self.background_image_name:
            # Legacy single-background rendering
            self._draw_bg_layer(painter, {
                'background_image': self.background_image_name,
                'tile_h': self.tile_horizontal,
                'tile_v': self.tile_vertical,
                'hspeed': self.bg_hspeed,
                'vspeed': self.bg_vspeed,
                'stretch': getattr(self, 'bg_stretch', True),
                'x': 0, 'y': 0,
            })

    def draw_foregrounds(self, painter):
        """Draw foreground background layers (on top of instances)"""
        if not self.bg_layers:
            return
        for layer in self.bg_layers:
            if layer.get('visible') and layer.get('foreground'):
                self._draw_bg_layer(painter, layer)

    def _draw_bg_layer(self, painter, layer):
        """Draw a single background layer"""
        img_name = layer.get('background_image', '')
        if not img_name:
            return

        bg_pixmap = self.load_background_image(img_name)
        if not bg_pixmap or bg_pixmap.isNull():
            return

        lx = layer.get('x', 0)
        ly = layer.get('y', 0)
        do_tile_h = layer.get('tile_h', False) or layer.get('hspeed', 0.0) != 0.0
        do_tile_v = layer.get('tile_v', False) or layer.get('vspeed', 0.0) != 0.0

        if do_tile_h or do_tile_v:
            img_width = bg_pixmap.width()
            img_height = bg_pixmap.height()
            x_count = (self.room_width // img_width) + 2 if do_tile_h else 1
            y_count = (self.room_height // img_height) + 2 if do_tile_v else 1

            for xt in range(x_count):
                for yt in range(y_count):
                    x_pos = lx + (xt * img_width if do_tile_h else 0)
                    y_pos = ly + (yt * img_height if do_tile_v else 0)
                    if x_pos < self.room_width and y_pos < self.room_height:
                        painter.drawPixmap(x_pos, y_pos, bg_pixmap)
        else:
            if layer.get('stretch', False):
                painter.drawPixmap(lx, ly, self.room_width, self.room_height, bg_pixmap)
            else:
                painter.drawPixmap(lx, ly, bg_pixmap)

    def load_background_image(self, image_name):
        """Load background image from project"""
        if not self.project_data or not self.project_path:
            return None

        if image_name in self.sprite_cache:
            return self.sprite_cache[image_name]

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
                                self.sprite_cache[image_name] = pixmap
                                return pixmap
            return None
        except Exception as e:
            logger.error(f"Error loading background image {image_name}: {e}")
            return None

    def draw_grid(self, painter):
        """Draw the grid"""
        painter.setPen(QPen(QColor("#CCCCCC"), 1))

        for x in range(0, self.room_width + 1, self.grid_size):
            painter.drawLine(x, 0, x, self.room_height)

        for y in range(0, self.room_height + 1, self.grid_size):
            painter.drawLine(0, y, self.room_width, y)

    def draw_instance(self, painter, instance):
        """Draw an object instance using its sprite with rotation and scale"""
        sprite = self.load_object_sprite(instance.object_name)

        # Get dimensions
        if sprite and not sprite.isNull():
            width = sprite.width()
            height = sprite.height()
        else:
            width = 32
            height = 32

        # Store dimensions for selection
        instance._sprite_width = width
        instance._sprite_height = height

        # Apply transformations
        painter.save()  # Save current state

        # Get transformation properties (with defaults)
        rotation = getattr(instance, 'rotation', 0)
        scale_x = getattr(instance, 'scale_x', 1.0)
        scale_y = getattr(instance, 'scale_y', 1.0)

        # Only apply transformations if needed (optimization)
        if rotation != 0 or scale_x != 1.0 or scale_y != 1.0:
            # Move origin to instance center
            center_x = instance.x + (width * scale_x) / 2
            center_y = instance.y + (height * scale_y) / 2
            painter.translate(center_x, center_y)

            # Apply rotation
            if rotation != 0:
                painter.rotate(rotation)

            # Apply scale
            if scale_x != 1.0 or scale_y != 1.0:
                painter.scale(scale_x, scale_y)

            # Draw at offset position (centered)
            if sprite and not sprite.isNull():
                painter.drawPixmap(-width / 2, -height / 2, sprite)
            else:
                # Draw placeholder rectangle
                color = self.get_object_color(instance.object_name)
                painter.fillRect(-width / 2, -height / 2, width, height, color)
                painter.setPen(QPen(QColor("#000000"), 1))
                painter.drawRect(-width / 2, -height / 2, width, height)

                painter.setPen(QPen(QColor("#FFFFFF"), 1))
                font = QFont()
                font.setPointSize(8)
                painter.setFont(font)

                name = instance.object_name
                if len(name) > 6:
                    name = name[:4] + ".."

                painter.drawText(-width / 2 + 2, -height / 2 + 12, name)
        else:
            # No transformation needed - draw normally
            if sprite and not sprite.isNull():
                sprite_rect = QRect(instance.x, instance.y, width, height)
                painter.drawPixmap(sprite_rect, sprite)
            else:
                color = self.get_object_color(instance.object_name)
                painter.fillRect(instance.x, instance.y, width, height, color)
                painter.setPen(QPen(QColor("#000000"), 1))
                painter.drawRect(instance.x, instance.y, width, height)

                painter.setPen(QPen(QColor("#FFFFFF"), 1))
                font = QFont()
                font.setPointSize(8)
                painter.setFont(font)

                name = instance.object_name
                if len(name) > 6:
                    name = name[:4] + ".."

                painter.drawText(instance.x + 2, instance.y + 12, name)

        painter.restore()  # Restore previous state

    def draw_selection(self, painter, instance):
        """Draw selection highlight around instance"""
        width = getattr(instance, '_sprite_width', 32)
        height = getattr(instance, '_sprite_height', 32)

        painter.setPen(QPen(QColor("#FF0000"), 2))
        painter.drawRect(instance.x - 2, instance.y - 2, width + 4, height + 4)

        handle_size = 6
        painter.fillRect(instance.x - 3, instance.y - 3, handle_size, handle_size, QColor("#FF0000"))
        painter.fillRect(instance.x + width - 3, instance.y - 3, handle_size, handle_size, QColor("#FF0000"))
        painter.fillRect(instance.x - 3, instance.y + height - 3, handle_size, handle_size, QColor("#FF0000"))
        painter.fillRect(instance.x + width - 3, instance.y + height - 3, handle_size, handle_size, QColor("#FF0000"))

    def draw_instance_preview(self, painter):
        """Draw a semi-transparent preview of the object being placed"""
        if not self.preview_position or not self.current_object_type:
            return

        snapped_pos = self.snap_to_grid_pos(self.preview_position)
        sprite = self.load_object_sprite(self.current_object_type)

        painter.setOpacity(0.5)

        if sprite and not sprite.isNull():
            sprite_rect = QRect(snapped_pos.x(), snapped_pos.y(), sprite.width(), sprite.height())
            painter.drawPixmap(sprite_rect, sprite)
        else:
            color = self.get_object_color(self.current_object_type)
            painter.fillRect(snapped_pos.x(), snapped_pos.y(), 32, 32, color)
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.drawRect(snapped_pos.x(), snapped_pos.y(), 32, 32)

            painter.setPen(QPen(QColor("#FFFFFF"), 1))
            font = QFont()
            font.setPointSize(8)
            painter.setFont(font)

            name = self.current_object_type
            if len(name) > 6:
                name = name[:4] + ".."

            painter.drawText(snapped_pos.x() + 2, snapped_pos.y() + 12, name)

        painter.setOpacity(1.0)
        painter.setPen(QPen(QColor("#00FF00"), 2, Qt.DashLine))
        painter.drawRect(snapped_pos.x(), snapped_pos.y(), self.grid_size, self.grid_size)
        painter.setOpacity(1.0)

    def load_object_sprite(self, object_name):
        """Load sprite for an object from the project (first frame for animated sprites)"""
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
                pixmap = self.create_default_sprite(object_name)
                self.sprite_cache[object_name] = pixmap
                return pixmap

            sprites = self.project_data.get('assets', {}).get('sprites', {})
            if sprite_name not in sprites:
                pixmap = self.create_default_sprite(object_name)
                self.sprite_cache[object_name] = pixmap
                return pixmap

            sprite_data = sprites[sprite_name]
            sprite_file_path = sprite_data.get('file_path', '')

            if not sprite_file_path:
                pixmap = self.create_default_sprite(object_name)
                self.sprite_cache[object_name] = pixmap
                return pixmap

            full_sprite_path = self.project_path / sprite_file_path
            if full_sprite_path.exists():
                pixmap = QPixmap(str(full_sprite_path))

                if not pixmap.isNull():
                    # Check if this is an animated sprite - extract first frame
                    animation_type = sprite_data.get('animation_type', 'single')
                    frames = sprite_data.get('frames', 1)

                    if frames > 1 and animation_type != 'single':
                        # Extract first frame from sprite sheet
                        frame_width = sprite_data.get('frame_width', pixmap.width())
                        frame_height = sprite_data.get('frame_height', pixmap.height())

                        # Ensure frame dimensions are valid
                        frame_width = min(frame_width, pixmap.width())
                        frame_height = min(frame_height, pixmap.height())

                        # Extract first frame (top-left corner)
                        pixmap = pixmap.copy(0, 0, frame_width, frame_height)

                    # Scale if too large for room editor display
                    if pixmap.width() > 64 or pixmap.height() > 64:
                        pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                    self.sprite_cache[object_name] = pixmap
                    return pixmap

            pixmap = self.create_default_sprite(object_name)
            self.sprite_cache[object_name] = pixmap
            return pixmap

        except Exception as e:
            logger.error(f"Error loading sprite for {object_name}: {e}")
            pixmap = self.create_default_sprite(object_name)
            self.sprite_cache[object_name] = pixmap
            return pixmap

    def clear_sprite_cache(self, object_name=None):
        """Clear sprite cache for specific object or all objects"""
        if object_name:
            if object_name in self.sprite_cache:
                del self.sprite_cache[object_name]
                logger.debug(f"Cleared sprite cache for {object_name}")
        else:
            self.sprite_cache.clear()
            logger.debug("Cleared all sprite cache")

    def create_default_sprite(self, object_name):
        """Create a default sprite for objects without sprites"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        color = self.get_object_color(object_name)
        painter.fillRect(0, 0, 32, 32, color)
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawRect(0, 0, 31, 31)

        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)

        name = object_name
        if len(name) > 6:
            name = name[:4] + ".."

        text_rect = painter.fontMetrics().boundingRect(name)
        x = (32 - text_rect.width()) // 2
        y = (32 + text_rect.height()) // 2 - 2
        painter.drawText(x, y, name)

        painter.end()
        return pixmap

    def get_object_color(self, object_name):
        """Get a color for an object type"""
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

    # Mouse event handlers
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.RightButton:
            pos = event.position().toPoint()

            # Tile erasing mode
            if self.current_tile_info:
                self.erased_tiles = []
                tile = self.find_tile_at(pos)
                if tile:
                    self.erased_tiles.append(tile)
                    self.tiles.remove(tile)
                    self._tile_layer_dirty = True
                    self.update()
                self.tile_erasing_mode = True
                return

            clicked_instance = self.find_instance_at(pos)

            self.erased_instances = []

            if clicked_instance:
                self.erased_instances.append(clicked_instance)
                self.instances.remove(clicked_instance)
                if clicked_instance in self.selected_instances:
                    self.selected_instances.remove(clicked_instance)
                self.instance_selected.emit(
                    self.selected_instances[0] if self.selected_instances else None
                )
                self.update()

            self.erasing_mode = True
            return

        elif event.button() == Qt.LeftButton:
            pos = event.position().toPoint()

            # Tile painting mode
            if self.current_tile_info:
                snapped_pos = self._snap_to_tile_grid(pos)
                self.show_preview = False

                tw = self.current_tile_info['width']
                th = self.current_tile_info['height']
                grid_key = (snapped_pos.x() // tw, snapped_pos.y() // th)
                self.last_painted_tile_grid = grid_key

                new_tile = {
                    'background_name': self.current_tile_info['background_name'],
                    'x': snapped_pos.x(),
                    'y': snapped_pos.y(),
                    'tile_x': self.current_tile_info['tile_x'],
                    'tile_y': self.current_tile_info['tile_y'],
                    'width': tw,
                    'height': th,
                    'depth': self.current_tile_info.get('depth', 1000000),
                    'layer': self.current_tile_info.get('layer', 0),
                }
                self.painted_tiles = [new_tile]
                self.tiles.append(new_tile)
                self._tile_layer_dirty = True
                self.tile_painting_mode = True
                self.update()
                return

            clicked_instance = self.find_instance_at(pos)

            # Check for Shift key modifier
            shift_pressed = event.modifiers() & Qt.ShiftModifier

            if clicked_instance:
                # Clicking on an existing instance
                if shift_pressed:
                    # Shift+click: toggle selection
                    if clicked_instance in self.selected_instances:
                        self.selected_instances.remove(clicked_instance)
                    else:
                        self.selected_instances.append(clicked_instance)

                    self.instance_selected.emit(
                        self.selected_instances[0] if self.selected_instances else None
                    )

                    # Don't start dragging on Shift+click - only toggle selection
                    # This prevents the jump behavior
                    self.update()
                    return
                else:
                    # Regular click: select only this instance (or keep multi-selection if already selected)
                    if clicked_instance not in self.selected_instances:
                        self.selected_instances.clear()
                        self.selected_instances.append(clicked_instance)
                        self.instance_selected.emit(clicked_instance)

                # Start dragging all selected instances
                self.dragging = True
                self.drag_offset = pos - QPoint(clicked_instance.x, clicked_instance.y)

                # Store starting positions for all selected instances
                self.move_start_positions = {
                    inst: (inst.x, inst.y) for inst in self.selected_instances
                }

            elif self.current_object_type:
                # Place new instance and enter painting mode
                snapped_pos = self.snap_to_grid_pos(pos)
                self.show_preview = False

                grid_x = snapped_pos.x() // self.grid_size
                grid_y = snapped_pos.y() // self.grid_size
                self.last_painted_grid = (grid_x, grid_y)

                new_instance = ObjectInstance(self.current_object_type, snapped_pos.x(), snapped_pos.y())
                self.painted_instances = [new_instance]
                self.instances.append(new_instance)

                self.selected_instances = [new_instance]
                self.instance_selected.emit(new_instance)
                self.instance_added.emit(new_instance)
                self.painting_mode = True
                self.update()

            else:
                # Clicking on empty space: start rubber band selection
                if not shift_pressed:
                    self.selected_instances.clear()
                    self.instance_selected.emit(None)

                self.rubber_band_selecting = True
                self.rubber_band_start = pos
                self.rubber_band_rect = QRect(pos, pos)

            self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        pos = event.position().toPoint()
        self.last_mouse_pos = pos

        # Tile preview
        if self.current_tile_info and not self.tile_painting_mode and not self.tile_erasing_mode:
            self.preview_position = pos
            self.show_preview = True
            self.update()

        if self.current_object_type and not self.dragging and not self.painting_mode and not self.erasing_mode and not self.rubber_band_selecting:
            self.preview_position = pos
            self.show_preview = True
            self.update()

        if self.dragging and self.selected_instances:
            # Move all selected instances together
            primary_instance = self.selected_instances[0]
            new_pos = self.snap_to_grid_pos(pos - self.drag_offset)

            # Calculate delta from primary instance's original position
            old_primary_pos = self.move_start_positions[primary_instance]
            delta_x = new_pos.x() - old_primary_pos[0]
            delta_y = new_pos.y() - old_primary_pos[1]

            # Move all selected instances by the same delta
            for instance in self.selected_instances:
                old_x, old_y = self.move_start_positions[instance]
                instance.x = max(0, min(old_x + delta_x, self.room_width - 32))
                instance.y = max(0, min(old_y + delta_y, self.room_height - 32))

            if self.selected_instances:
                self.instance_moved.emit(self.selected_instances[0])
            self.update()

        elif self.rubber_band_selecting and self.rubber_band_start:
            # Update rubber band rectangle
            self.rubber_band_rect = QRect(self.rubber_band_start, pos).normalized()
            self.update()

        elif self.painting_mode and self.current_object_type:
            snapped_pos = self.snap_to_grid_pos(pos)
            grid_x = snapped_pos.x() // self.grid_size
            grid_y = snapped_pos.y() // self.grid_size
            current_grid = (grid_x, grid_y)

            if current_grid != self.last_painted_grid:
                self.last_painted_grid = current_grid
                existing_instance = self.find_instance_at(snapped_pos)
                if not existing_instance:
                    new_instance = ObjectInstance(self.current_object_type, snapped_pos.x(), snapped_pos.y())
                    self.painted_instances.append(new_instance)
                    self.instances.append(new_instance)
                    self.instance_added.emit(new_instance)
                    self.update()

        elif self.tile_painting_mode and self.current_tile_info:
            snapped_pos = self._snap_to_tile_grid(pos)
            tw = self.current_tile_info['width']
            th = self.current_tile_info['height']
            grid_key = (snapped_pos.x() // tw, snapped_pos.y() // th)

            if grid_key != self.last_painted_tile_grid:
                self.last_painted_tile_grid = grid_key
                new_tile = {
                    'background_name': self.current_tile_info['background_name'],
                    'x': snapped_pos.x(),
                    'y': snapped_pos.y(),
                    'tile_x': self.current_tile_info['tile_x'],
                    'tile_y': self.current_tile_info['tile_y'],
                    'width': tw,
                    'height': th,
                    'depth': self.current_tile_info.get('depth', 1000000),
                    'layer': self.current_tile_info.get('layer', 0),
                }
                self.painted_tiles.append(new_tile)
                self.tiles.append(new_tile)
                self._tile_layer_dirty = True
                self.update()

        elif self.tile_erasing_mode:
            tile = self.find_tile_at(pos)
            if tile and tile not in self.erased_tiles:
                self.erased_tiles.append(tile)
                self.tiles.remove(tile)
                self._tile_layer_dirty = True
                self.update()

        elif self.erasing_mode:
            instance_to_delete = self.find_instance_at(pos)
            if instance_to_delete and instance_to_delete not in self.erased_instances:
                self.erased_instances.append(instance_to_delete)
                self.instances.remove(instance_to_delete)
                if instance_to_delete in self.selected_instances:
                    self.selected_instances.remove(instance_to_delete)
                self.instance_selected.emit(
                    self.selected_instances[0] if self.selected_instances else None
                )
                self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            # Handle tile paint batch undo
            if self.tile_painting_mode and self.painted_tiles:
                if len(self.painted_tiles) > 1:
                    command = BatchAddTilesCommand(self, self.painted_tiles, "Paint Tiles", already_added=True)
                    self.undo_stack.push(command)
                elif len(self.painted_tiles) == 1:
                    command = AddTileCommand(self, self.painted_tiles[0], "Add Tile", already_added=True)
                    self.undo_stack.push(command)
                self.painted_tiles = []
                self.tile_painting_mode = False
                self.last_painted_tile_grid = None
                if self.current_tile_info:
                    self.show_preview = True
                self.update()
                return

            # Handle multi-instance move undo
            if self.dragging and self.selected_instances and self.move_start_positions:
                moved_instances = []
                for instance in self.selected_instances:
                    if instance in self.move_start_positions:
                        old_x, old_y = self.move_start_positions[instance]
                        new_x, new_y = instance.x, instance.y

                        if old_x != new_x or old_y != new_y:
                            moved_instances.append((instance, old_x, old_y, new_x, new_y))

                if moved_instances:
                    if len(moved_instances) > 1:
                        # Create batch move command
                        from editors.room_undo_commands import BatchMoveInstancesCommand
                        command = BatchMoveInstancesCommand(self, moved_instances)
                        self.undo_stack.push(command)
                    else:
                        instance, old_x, old_y, new_x, new_y = moved_instances[0]
                        command = MoveInstanceCommand(
                            self, instance, old_x, old_y, new_x, new_y,
                            f"Move {instance.object_name}"
                        )
                        self.undo_stack.push(command)

                self.move_start_positions = {}

            # Handle rubber band selection
            if self.rubber_band_selecting and self.rubber_band_rect:
                selected = self.find_instances_in_rect(self.rubber_band_rect)

                # Add to selection (Shift was held during drag)
                shift_pressed = event.modifiers() & Qt.ShiftModifier
                if not shift_pressed:
                    self.selected_instances = selected
                else:
                    for inst in selected:
                        if inst not in self.selected_instances:
                            self.selected_instances.append(inst)

                self.instance_selected.emit(
                    self.selected_instances[0] if self.selected_instances else None
                )

                self.rubber_band_selecting = False
                self.rubber_band_start = None
                self.rubber_band_rect = None

            # Handle paint batch undo
            if self.painting_mode and self.painted_instances:
                if len(self.painted_instances) > 1:
                    command = BatchAddInstancesCommand(self, self.painted_instances, "Paint Instances", already_added=True)
                    self.undo_stack.push(command)
                elif len(self.painted_instances) == 1:
                    command = AddInstanceCommand(self, self.painted_instances[0], f"Add {self.painted_instances[0].object_name}", already_added=True)
                    self.undo_stack.push(command)

                self.painted_instances = []

            self.dragging = False
            self.painting_mode = False
            self.last_painted_grid = None

            if self.current_object_type:
                self.show_preview = True

        elif event.button() == Qt.RightButton:
            # Handle tile erase batch undo
            if self.tile_erasing_mode and self.erased_tiles:
                command = BatchRemoveTilesCommand(self, self.erased_tiles, "Erase Tiles")
                self.undo_stack.push(command)
                self.erased_tiles = []
                self.tile_erasing_mode = False
                if self.current_tile_info:
                    self.show_preview = True
                self.update()
                return

            # CRITICAL FIX: Only create undo command if instances were actually erased
            if self.erasing_mode and self.erased_instances:
                # Verify instances still exist in the instances list
                valid_erased = [inst for inst in self.erased_instances if inst not in self.instances]

                if valid_erased:
                    if len(valid_erased) > 1:
                        command = BatchRemoveInstancesCommand(self, valid_erased)
                        self.undo_stack.push(command)
                    elif len(valid_erased) == 1:
                        command = RemoveInstanceCommand(self, valid_erased[0])
                        self.undo_stack.push(command)

                self.erased_instances = []

            self.erasing_mode = False

        self.update()

    def leaveEvent(self, event):
        """Handle mouse leaving the canvas"""
        self.show_preview = False
        self.update()

    def enterEvent(self, event):
        """Handle mouse entering the canvas"""
        if self.current_object_type or self.current_tile_info:
            self.show_preview = True

