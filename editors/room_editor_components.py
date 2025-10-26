#!/usr/bin/env python3
"""
Room Editor Components for GameMaker IDE
Contains specialized widgets and classes for room editing
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, 
    QGraphicsItem, QGraphicsPixmapItem, QTreeWidget, QTreeWidgetItem,
    QGroupBox, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, 
    QPushButton, QLabel, QColorDialog, QListWidget, QListWidgetItem, QCheckBox,
    QTextEdit, QSlider, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QRectF, QPointF, QSizeF, Signal, QMimeData, QSize
from PySide6.QtGui import (
    QPixmap, QPainter, QPen, QBrush, QColor, QFont,
    QDragEnterEvent, QDropEvent, QMouseEvent, QWheelEvent, QIcon
)


class RoomObject(QGraphicsPixmapItem):
    """Represents an object instance in the room"""
    
    def __init__(self, object_name: str, sprite_pixmap: QPixmap, x: float, y: float, object_id: int = None):
        super().__init__(sprite_pixmap)
        
        # Object properties
        self.object_name = object_name
        self.object_id = object_id or id(self)  # Unique identifier
        
        # Set position
        self.setPos(x, y)
        
        # Make it interactive
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Store original position for undo functionality
        self.original_pos = QPointF(x, y)
        
        # Object instance properties
        self.properties = {
            'object_name': object_name,
            'id': self.object_id,
            'x': x,
            'y': y,
            'creation_code': '',
            'scale_x': 1.0,
            'scale_y': 1.0,
            'rotation': 0.0,
            'color': '#FFFFFF',
            'alpha': 1.0
        }
        
        # Visual feedback
        self.selection_outline = None
        self.grid_snap = True
        self.grid_size = 16
    
    def itemChange(self, change, value):
        """Handle item changes for snapping to grid and boundary checking"""
        if change == QGraphicsItem.ItemPositionChange and self.grid_snap:
            # Snap to grid
            new_pos = value
            snap_x = round(new_pos.x() / self.grid_size) * self.grid_size
            snap_y = round(new_pos.y() / self.grid_size) * self.grid_size
            
            # Check room boundaries if available
            if self.scene():
                room_view = None
                for view in self.scene().views():
                    if hasattr(view, 'room_boundary') and view.room_boundary:
                        room_view = view
                        break
                
                if room_view and room_view.room_boundary:
                    room_rect = room_view.room_boundary.rect()
                    
                    # Get object bounds
                    obj_rect = self.boundingRect()
                    
                    # Clamp position to keep object within room boundaries
                    snap_x = max(0, min(snap_x, room_rect.width() - obj_rect.width()))
                    snap_y = max(0, min(snap_y, room_rect.height() - obj_rect.height()))
            
            snapped_pos = QPointF(snap_x, snap_y)
            
            # Update properties
            self.properties['x'] = snap_x
            self.properties['y'] = snap_y
            
            return snapped_pos
            
        elif change == QGraphicsItem.ItemSelectedChange:
            # Handle selection change
            if value:  # Selected
                self.show_selection_outline()
            else:  # Deselected
                self.hide_selection_outline()
        
        return super().itemChange(change, value)
    
    def show_selection_outline(self):
        """Show selection outline around object"""
        if not self.selection_outline:
            rect = self.boundingRect()
            pen = QPen(QColor(255, 255, 0), 2, Qt.DashLine)  # Yellow dashed outline
            self.selection_outline = self.scene().addRect(rect, pen)
            self.selection_outline.setPos(self.pos())
            self.selection_outline.setZValue(self.zValue() + 0.1)
    
    def hide_selection_outline(self):
        """Hide selection outline"""
        if self.selection_outline:
            self.scene().removeItem(self.selection_outline)
            self.selection_outline = None
    
    def update_position_from_properties(self):
        """Update visual position from properties data"""
        new_x = self.properties.get('x', 0)
        new_y = self.properties.get('y', 0)
        self.setPos(new_x, new_y)
    
    def get_instance_data(self) -> Dict[str, Any]:
        """Get instance data for saving"""
        return {
            'object_name': self.object_name,
            'id': self.object_id,
            'x': self.properties['x'],
            'y': self.properties['y'],
            'creation_code': self.properties.get('creation_code', ''),
            'scale_x': self.properties.get('scale_x', 1.0),
            'scale_y': self.properties.get('scale_y', 1.0),
            'rotation': self.properties.get('rotation', 0.0),
            'color': self.properties.get('color', '#FFFFFF'),
            'alpha': self.properties.get('alpha', 1.0)
        }
    
    def set_grid_snap(self, enabled: bool, grid_size: int = 16):
        """Enable/disable grid snapping"""
        self.grid_snap = enabled
        self.grid_size = grid_size


class RoomGraphicsView(QGraphicsView):
    """Custom graphics view for room editing with zoom, pan, and drag-drop"""
    
    # Signals
    object_selected = Signal(object)  # RoomObject selected
    object_deselected = Signal()     # No object selected
    object_dropped = Signal(str, float, float)  # object_name, x, y
    view_transformed = Signal()      # View zoom/pan changed
    
    def __init__(self, scene):
        super().__init__(scene)
        
        # View settings
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Set view background to dark gray to contrast with room
        self.setBackgroundBrush(QBrush(QColor(64, 64, 64)))
        
        # Zoom settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.05
        self.max_zoom = 8.0
        
        # Grid settings
        self.show_grid = True
        self.grid_size = 16
        self.grid_color = QColor(200, 200, 200)
        
        # Track mouse position
        self.mouse_scene_pos = QPointF(0, 0)
        
        # Room boundary visualization
        self.room_boundary = None
        self.room_outer_border = None
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle zoom with mouse wheel"""
        # Calculate zoom factor
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # Save the scene pos
        old_pos = self.mapToScene(event.position().toPoint())
        
        # Determine zoom direction
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        # Calculate new zoom level
        new_zoom = self.zoom_factor * zoom_factor
        
        # Clamp zoom level
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        
        # Apply zoom
        self.scale(zoom_factor, zoom_factor)
        self.zoom_factor = new_zoom
        
        # Get the new position
        new_pos = self.mapToScene(event.position().toPoint())
        
        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        
        # Emit signal
        self.view_transformed.emit()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Track mouse position"""
        self.mouse_scene_pos = self.mapToScene(event.pos())
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        super().mousePressEvent(event)
        
        # Check if an object was clicked
        item = self.itemAt(event.pos())
        if isinstance(item, RoomObject):
            self.object_selected.emit(item)
        else:
            self.object_deselected.emit()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events from object palette"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Handle drag move events"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle dropping objects into the room"""
        if event.mimeData().hasText():
            object_name = event.mimeData().text()
            drop_pos = self.mapToScene(event.position().toPoint())
            
            # Check if drop position is within room boundaries
            if self.room_boundary:
                room_rect = self.room_boundary.rect()
                if not room_rect.contains(drop_pos):
                    # Clamp position to room boundaries
                    drop_pos.setX(max(0, min(drop_pos.x(), room_rect.width())))
                    drop_pos.setY(max(0, min(drop_pos.y(), room_rect.height())))
            
            # Snap to grid
            snap_x = round(drop_pos.x() / self.grid_size) * self.grid_size
            snap_y = round(drop_pos.y() / self.grid_size) * self.grid_size
            
            # Emit signal to create object
            self.object_dropped.emit(object_name, snap_x, snap_y)
            event.acceptProposedAction()
    
    def set_zoom(self, zoom_level: float):
        """Set specific zoom level"""
        if self.min_zoom <= zoom_level <= self.max_zoom:
            factor = zoom_level / self.zoom_factor
            self.scale(factor, factor)
            self.zoom_factor = zoom_level
            self.view_transformed.emit()
    
    def zoom_to_fit(self):
        """Zoom to fit all content"""
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self.zoom_factor = self.transform().m11()  # Get current zoom from transform
        self.view_transformed.emit()
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.resetTransform()
        self.zoom_factor = 1.0
        self.view_transformed.emit()
    
    def get_mouse_scene_position(self) -> QPointF:
        """Get current mouse position in scene coordinates"""
        return self.mouse_scene_pos
    
    def update_room_boundary(self, room_rect: QRectF, background_color: str = '#87CEEB'):
        """Update the visual room boundary"""
        # Remove existing boundary elements
        if self.room_boundary:
            self.scene().removeItem(self.room_boundary)
            self.room_boundary = None
        
        if self.room_outer_border:
            self.scene().removeItem(self.room_outer_border)
            self.room_outer_border = None
        
        if room_rect.isValid():
            # Create room background rectangle with thick border
            room_bg = self.scene().addRect(
                room_rect,
                QPen(QColor(0, 0, 0), 4, Qt.SolidLine),  # Black border, 4px thick
                QBrush(QColor(background_color))  # Room background color
            )
            room_bg.setZValue(-999)  # Behind everything except grid
            self.room_boundary = room_bg
            
            # Add a subtle outer border for better visibility
            outer_border = self.scene().addRect(
                room_rect.adjusted(-2, -2, 2, 2),  # Slightly larger
                QPen(QColor(128, 128, 128), 2, Qt.SolidLine),  # Gray outer border
                QBrush(Qt.NoBrush)  # No fill
            )
            outer_border.setZValue(-1000)  # Behind room boundary
            self.room_outer_border = outer_border
            
            # Extend scene rect to show area around the room
            extended_rect = QRectF(
                room_rect.x() - 300, room_rect.y() - 300,
                room_rect.width() + 600, room_rect.height() + 600
            )
            self.scene().setSceneRect(extended_rect)
    
    def set_room_background_color(self, color: str):
        """Update room background color"""
        if self.room_boundary:
            self.room_boundary.setBrush(QBrush(QColor(color)))


class ObjectPalette(QListWidget):
    """Widget displaying available objects that can be placed in room"""
    
    # Signals
    object_selected = Signal(str, dict)  # object_name, object_data
    
    def __init__(self):
        super().__init__()
        
        # Setup drag and drop
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)
        
        # Visual settings
        self.setMaximumWidth(250)
        self.setMinimumWidth(150)
        self.setIconSize(QSize(32, 32))
        
        # Setup view mode
        self.setViewMode(QListWidget.ListMode)
        self.setResizeMode(QListWidget.Adjust)
        
        # Set size policy to expand vertically
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Store object data
        self.object_data = {}
    
    def populate_objects(self, objects: Dict[str, Any], sprites: Dict[str, Any] = None):
        """Populate the palette with available objects"""
        self.clear()
        self.object_data = {}
        
        if not objects:
            # Add placeholder item
            item = QListWidgetItem("No objects available")
            item.setFlags(Qt.NoItemFlags)  # Not selectable
            self.addItem(item)
            return
        
        for obj_name, obj_data in objects.items():
            item = QListWidgetItem(obj_name)
            
            # Create icon from sprite or default
            icon_pixmap = self.create_object_icon(obj_data, sprites)
            if not icon_pixmap.isNull():
                item.setIcon(QIcon(icon_pixmap))
            
            # Store object data
            item.setData(Qt.UserRole, obj_data)
            self.object_data[obj_name] = obj_data
            
            # Add tooltip with object info
            tooltip = f"Object: {obj_name}"
            if 'sprite' in obj_data:
                tooltip += f"\nSprite: {obj_data['sprite']}"
            if 'description' in obj_data:
                tooltip += f"\n{obj_data['description']}"
            item.setToolTip(tooltip)
            
            self.addItem(item)
        
        # Connect selection
        self.itemClicked.connect(self.on_item_clicked)
    
    def create_object_icon(self, obj_data: Dict[str, Any], sprites: Dict[str, Any] = None) -> QPixmap:
        """Create icon for object"""
        sprite_name = obj_data.get('sprite', '')
        
        # Try to load sprite
        if sprite_name and sprites and sprite_name in sprites:
            sprite_data = sprites[sprite_name]
            sprite_path = sprite_data.get('project_path', '')
            
            if sprite_path and Path(sprite_path).exists():
                pixmap = QPixmap(sprite_path)
                if not pixmap.isNull():
                    return pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Create default icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(100, 150, 200))
        
        # Draw object name abbreviation
        painter = QPainter(pixmap)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        
        # Get first 3 characters or abbreviation
        obj_name = obj_data.get('name', 'obj')
        abbrev = obj_name[:3].upper()
        painter.drawText(pixmap.rect(), Qt.AlignCenter, abbrev)
        painter.end()
        
        return pixmap
    
    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click"""
        obj_data = item.data(Qt.UserRole)
        if obj_data:
            self.object_selected.emit(item.text(), obj_data)
    
    def startDrag(self, supportedActions):
        """Start drag operation with object name"""
        item = self.currentItem()
        if item and item.flags() & Qt.ItemIsSelectable:
            # Create drag
            drag = self.startDrag(supportedActions)
            mime_data = QMimeData()
            mime_data.setText(item.text())
            
            # Set drag pixmap
            icon = item.icon()
            if not icon.isNull():
                drag.setPixmap(icon.pixmap(32, 32))
            
            drag.setMimeData(mime_data)


class RoomPropertiesPanel(QWidget):
    """Panel for editing room and instance properties"""
    
    # Signals
    room_property_changed = Signal(str, object)  # property_name, new_value
    instance_property_changed = Signal(int, str, object)  # instance_id, property_name, new_value
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Current data
        self.current_room_data = {}
        self.current_instance = None
        
        # Block signals during updates
        self.updating = False
    
    def setup_ui(self):
        """Setup the properties panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Room properties section
        self.setup_room_properties(layout)
        
        # Instance properties section  
        self.setup_instance_properties(layout)
        
        # Add stretch to push everything to top but allow expansion
        layout.addStretch(1)

        # Set size policy to expand vertically
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
    
    def setup_room_properties(self, parent_layout):
        """Setup room properties section"""
        room_group = QGroupBox("Room Properties")
        room_layout = QFormLayout(room_group)
        
        # Basic room properties
        self.room_name_edit = QLineEdit()
        self.room_width_spin = QSpinBox()
        self.room_height_spin = QSpinBox()
        
        # Set ranges
        self.room_width_spin.setRange(64, 8192)
        self.room_height_spin.setRange(64, 8192)
        self.room_width_spin.setValue(1024)
        self.room_height_spin.setValue(768)
        
        room_layout.addRow("Name:", self.room_name_edit)
        room_layout.addRow("Width:", self.room_width_spin)
        room_layout.addRow("Height:", self.room_height_spin)
        
        # Background settings
        self.bg_color_btn = QPushButton("Background Color")
        self.bg_color_btn.clicked.connect(self.choose_background_color)
        
        self.bg_image_combo = QComboBox()
        self.bg_image_combo.addItem("None")
        
        room_layout.addRow("Background:", self.bg_color_btn)
        room_layout.addRow("Background Image:", self.bg_image_combo)
        
        # Views/Camera settings
        self.enable_views_check = QCheckBox("Enable Views")
        room_layout.addRow(self.enable_views_check)
        
        parent_layout.addWidget(room_group)
        
        # Connect room property signals
        self.room_name_edit.textChanged.connect(lambda v: self.emit_room_property('name', v))
        self.room_width_spin.valueChanged.connect(lambda v: self.emit_room_property('width', v))
        self.room_height_spin.valueChanged.connect(lambda v: self.emit_room_property('height', v))
        self.enable_views_check.toggled.connect(lambda v: self.emit_room_property('enable_views', v))
    
    def setup_instance_properties(self, parent_layout):
        """Setup instance properties section"""
        self.instance_group = QGroupBox("Instance Properties")
        instance_layout = QFormLayout(self.instance_group)
        
        # Instance identification
        self.instance_id_label = QLabel("None")
        self.instance_object_label = QLabel("None")
        
        instance_layout.addRow("Instance ID:", self.instance_id_label)
        instance_layout.addRow("Object:", self.instance_object_label)
        
        # Position properties
        self.instance_x_spin = QSpinBox()
        self.instance_y_spin = QSpinBox()
        self.instance_x_spin.setRange(-9999, 9999)
        self.instance_y_spin.setRange(-9999, 9999)
        
        instance_layout.addRow("X Position:", self.instance_x_spin)
        instance_layout.addRow("Y Position:", self.instance_y_spin)
        
        # Transform properties
        self.instance_scale_x_spin = QDoubleSpinBox()
        self.instance_scale_y_spin = QDoubleSpinBox()
        self.instance_rotation_spin = QSpinBox()
        
        self.instance_scale_x_spin.setRange(0.1, 10.0)
        self.instance_scale_y_spin.setRange(0.1, 10.0)
        self.instance_scale_x_spin.setSingleStep(0.1)
        self.instance_scale_y_spin.setSingleStep(0.1)
        self.instance_scale_x_spin.setValue(1.0)
        self.instance_scale_y_spin.setValue(1.0)
        
        self.instance_rotation_spin.setRange(0, 359)
        self.instance_rotation_spin.setSuffix("°")
        
        instance_layout.addRow("Scale X:", self.instance_scale_x_spin)
        instance_layout.addRow("Scale Y:", self.instance_scale_y_spin)
        instance_layout.addRow("Rotation:", self.instance_rotation_spin)
        
        # Creation code
        self.creation_code_edit = QTextEdit()
        self.creation_code_edit.setMaximumHeight(100)
        self.creation_code_edit.setPlaceholderText("// Creation code for this instance")
        
        instance_layout.addRow("Creation Code:", self.creation_code_edit)
        
        # Hidden by default
        self.instance_group.setVisible(False)
        parent_layout.addWidget(self.instance_group)
        
        # Connect instance property signals
        self.instance_x_spin.valueChanged.connect(lambda v: self.emit_instance_property('x', v))
        self.instance_y_spin.valueChanged.connect(lambda v: self.emit_instance_property('y', v))
        self.instance_scale_x_spin.valueChanged.connect(lambda v: self.emit_instance_property('scale_x', v))
        self.instance_scale_y_spin.valueChanged.connect(lambda v: self.emit_instance_property('scale_y', v))
        self.instance_rotation_spin.valueChanged.connect(lambda v: self.emit_instance_property('rotation', v))
        self.creation_code_edit.textChanged.connect(lambda: self.emit_instance_property('creation_code', self.creation_code_edit.toPlainText()))
    
    def emit_room_property(self, prop_name: str, value):
        """Emit room property change signal"""
        if not self.updating:
            self.room_property_changed.emit(prop_name, value)
    
    def emit_instance_property(self, prop_name: str, value):
        """Emit instance property change signal"""
        if not self.updating and self.current_instance:
            instance_id = self.current_instance.object_id
            self.instance_property_changed.emit(instance_id, prop_name, value)
    
    def load_room_properties(self, room_data: Dict[str, Any]):
        """Load room properties into the panel"""
        self.updating = True
        self.current_room_data = room_data
        
        # Load basic properties
        self.room_name_edit.setText(room_data.get('name', 'room1'))
        self.room_width_spin.setValue(room_data.get('width', 1024))
        self.room_height_spin.setValue(room_data.get('height', 768))
        self.enable_views_check.setChecked(room_data.get('enable_views', False))
        
        # Update background color button
        bg_color = room_data.get('background_color', '#87CEEB')
        self.bg_color_btn.setStyleSheet(f"background-color: {bg_color}; color: white;")
        
        # Store the color in current_room_data
        self.current_room_data['background_color'] = bg_color

        self.updating = False
    
    def show_instance_properties(self, room_object: RoomObject):
        """Show properties for selected object instance"""
        self.updating = True
        self.current_instance = room_object
        self.instance_group.setVisible(True)
        
        # Load instance data
        props = room_object.properties
        
        self.instance_id_label.setText(str(props.get('id', 'Unknown')))
        self.instance_object_label.setText(props.get('object_name', 'Unknown'))
        
        self.instance_x_spin.setValue(int(props.get('x', 0)))
        self.instance_y_spin.setValue(int(props.get('y', 0)))
        self.instance_scale_x_spin.setValue(props.get('scale_x', 1.0))
        self.instance_scale_y_spin.setValue(props.get('scale_y', 1.0))
        self.instance_rotation_spin.setValue(int(props.get('rotation', 0)))
        
        self.creation_code_edit.setPlainText(props.get('creation_code', ''))
        
        self.updating = False
    
    def hide_instance_properties(self):
        """Hide instance properties panel"""
        self.current_instance = None
        self.instance_group.setVisible(False)
    
    def choose_background_color(self):
        """Open color dialog for background color"""
        current_color = self.current_room_data.get('background_color', '#87CEEB')
        color = QColorDialog.getColor(QColor(current_color), self)
        
        if color.isValid():
            color_hex = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {color_hex}; color: white;")
            
            # Update the room data immediately
            self.current_room_data['background_color'] = color_hex
            
            # Emit the signal
            self.emit_room_property('background_color', color_hex)
            
            print(f"Background color changed to: {color_hex}")  # Debug output
    
    def update_instance_properties(self, room_object: RoomObject):
        """Update displayed properties when instance changes externally"""
        if self.current_instance == room_object:
            self.show_instance_properties(room_object)


class RoomLayerWidget(QWidget):
    """Widget for managing room layers (future feature)"""
    
    layer_visibility_changed = Signal(str, bool)  # layer_name, visible
    layer_selected = Signal(str)  # layer_name
    
    def __init__(self):
        super().__init__()
        self.layers = {}  # Initialize layers dict first
        self.setup_ui()
    
    def setup_ui(self):
        """Setup layer management UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Layers")
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Layer list
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabel("Layer")
        self.layer_tree.setMaximumHeight(150)
        self.layer_tree.setMinimumHeight(100)
        
        # Add default layers
        self.add_default_layers()
        
        # Add stretch to allow expansion
        layout.addStretch()

        # Set size policy
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        layout.addWidget(self.layer_tree)
    
    def add_default_layers(self):
        """Add default room layers"""
        layers = [
            ("Background", True),
            ("Instances", True), 
            ("Foreground", True)
        ]
        
        for layer_name, visible in layers:
            item = QTreeWidgetItem([layer_name])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Checked if visible else Qt.Unchecked)
            self.layer_tree.addTopLevelItem(item)
            self.layers[layer_name] = visible