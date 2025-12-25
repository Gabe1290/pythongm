#!/usr/bin/env python3
"""
Enhanced Properties Panel Widget for PyGameMaker IDE
"""
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGroupBox, 
                               QFormLayout, QLineEdit, QTextEdit, QSpinBox,
                               QColorDialog, QPushButton, QCheckBox, QComboBox)

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap
from typing import Dict, Any

class EnhancedPropertiesPanel(QWidget):
    """Enhanced properties widget with grouped sections"""
    
    # Signals for property changes
    property_changed = Signal(str, object)  # property_name, value (bool or str)
    room_property_changed = Signal(str, object)  # property_name, value
    object_property_changed = Signal(str, object)  # property_name, value
    
    def __init__(self):
        super().__init__()
        self.available_sprites = {}
        self.project_base_path = None
        self.setup_ui()
        self.current_asset = None
        self.current_room_editor = None  # Reference to active room editor
        self.current_object_editor = None

    def set_project_base_path(self, base_path: str):
        """Set the project base path for resolving relative paths"""
        self.project_base_path = base_path

    def get_project_base_path(self):
        """Get the project base directory path"""
        if hasattr(self, 'project_base_path') and self.project_base_path:
            return self.project_base_path
        
        # Try to find it through parent chain
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_path') and parent.current_project_path:
                project_file_path = Path(parent.current_project_path)
                if project_file_path.name == 'project.json':
                    return str(project_file_path.parent)
                else:
                    return str(project_file_path)
            parent = parent.parent()
        
        return None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Asset info group
        info_group = QGroupBox(self.tr("Asset Information"))
        info_layout = QFormLayout(info_group)

        self.name_label = QLabel(self.tr("No asset selected"))
        self.type_label = QLabel("-")
        self.status_label = QLabel("-")

        info_layout.addRow(self.tr("Name:"), self.name_label)
        info_layout.addRow(self.tr("Type:"), self.type_label)
        info_layout.addRow(self.tr("Status:"), self.status_label)
        
        layout.addWidget(info_group)
        
        # Properties group
        self.properties_group = QGroupBox(self.tr("Properties"))
        self.properties_layout = QFormLayout(self.properties_group)
        layout.addWidget(self.properties_group)

        # Preview group
        preview_group = QGroupBox(self.tr("Preview"))
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel(self.tr("No preview available"))
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setMaximumHeight(300)
        self.preview_label.setScaledContents(False)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid gray;
                padding: 10px;
            }
        """)

        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)
        
        layout.addStretch()
    
    def set_room_editor_context(self, room_editor, room_name: str, room_properties: Dict[str, Any]):
        """Set context to show room properties from room editor"""
        # CRITICAL: Disconnect from previous room editor BEFORE setting new reference
        # This prevents changes from being sent to the wrong room editor
        if self.room_property_changed.receivers() > 0:
            try:
                self.room_property_changed.disconnect()
            except (RuntimeError, TypeError):
                pass  # No previous connections

        self.current_room_editor = room_editor
        self.current_asset = ('room_editor', room_name, room_properties)

        # Connect to preview update signal
        if hasattr(room_editor, 'room_preview_update_requested'):
            # Simple approach: just try to connect, Qt handles duplicates
            try:
                room_editor.room_preview_update_requested.connect(self.update_room_preview)
            except RuntimeError:
                # Connection already exists, that's fine
                pass

        # Connect to the NEW room editor's update method
        self.room_property_changed.connect(room_editor.update_room_property_from_ide)
        print(f"✅ Connected properties panel to room editor: {room_name}")

        # Update info
        self.name_label.setText(room_name)
        self.type_label.setText(self.tr("Room (Editor)"))
        self.status_label.setText(self.tr("Active"))

        # Block signals during initial setup to prevent spurious property changes
        self._setting_room_properties = True
        self.show_room_properties(room_properties)
        self._setting_room_properties = False
        
        # Generate initial preview
        QTimer.singleShot(100, self.update_room_preview)
    
    def show_room_properties(self, room_data: Dict[str, Any]):
        """Show room properties with live editing"""
        # Clear previous properties
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Room dimensions
        self.width_spin = QSpinBox()
        self.width_spin.setRange(64, 8192)
        self.width_spin.setValue(room_data.get('width', 1024))
        self.width_spin.valueChanged.connect(lambda v: self.on_room_property_changed('width', v))
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(64, 8192)
        self.height_spin.setValue(room_data.get('height', 768))
        self.height_spin.valueChanged.connect(lambda v: self.on_room_property_changed('height', v))
        
        # Background color
        self.bg_color_btn = QPushButton()
        bg_color = room_data.get('background_color', '#87CEEB')
        self.bg_color_btn.setStyleSheet(f"background-color: {bg_color}; border: 1px solid gray; min-height: 25px;")
        self.bg_color_btn.setText(bg_color)
        self.bg_color_btn.clicked.connect(self.choose_background_color)
        
        # Background image selection
        self.bg_image_combo = QComboBox()
        self.bg_image_combo.addItem(self.tr("None"))

        # Get available backgrounds/sprites
        available_backgrounds = self.get_available_backgrounds()
        for bg_name in available_backgrounds.keys():
            self.bg_image_combo.addItem(bg_name)

        current_bg = room_data.get('background_image', '')
        if current_bg:
            index = self.bg_image_combo.findText(current_bg)
            if index >= 0:
                self.bg_image_combo.setCurrentIndex(index)

        self.bg_image_combo.currentTextChanged.connect(
            lambda v: self.on_room_property_changed('background_image', v if v != self.tr("None") else '')
        )

        # Tiling options
        self.tile_h_check = QCheckBox()
        self.tile_h_check.setChecked(room_data.get('tile_horizontal', False))
        self.tile_h_check.toggled.connect(lambda v: self.on_room_property_changed('tile_horizontal', v))

        self.tile_v_check = QCheckBox()
        self.tile_v_check.setChecked(room_data.get('tile_vertical', False))
        self.tile_v_check.toggled.connect(lambda v: self.on_room_property_changed('tile_vertical', v))

        # Views
        self.views_check = QCheckBox()
        self.views_check.setChecked(room_data.get('enable_views', False))
        self.views_check.toggled.connect(lambda v: self.on_room_property_changed('enable_views', v))

        # Add to layout in logical order
        self.properties_layout.addRow(self.tr("Width:"), self.width_spin)
        self.properties_layout.addRow(self.tr("Height:"), self.height_spin)
        self.properties_layout.addRow(self.tr("Background Color:"), self.bg_color_btn)
        self.properties_layout.addRow(self.tr("Background Image:"), self.bg_image_combo)
        self.properties_layout.addRow(self.tr("Tile Horizontal:"), self.tile_h_check)
        self.properties_layout.addRow(self.tr("Tile Vertical:"), self.tile_v_check)
        self.properties_layout.addRow(self.tr("Enable Views:"), self.views_check)

        # Instance count (read-only)
        instance_count = len(room_data.get('instances', []))
        self.properties_layout.addRow(self.tr("Instances:"), QLabel(str(instance_count)))
    
    def choose_background_color(self):
        """Open color dialog for background color"""
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QColorDialog
        
        current_color = self.bg_color_btn.text()
        color = QColorDialog.getColor(QColor(current_color), self, self.tr("Choose Background Color"))
        
        if color.isValid():
            color_hex = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {color_hex}; border: 1px solid gray; min-height: 25px;")
            self.bg_color_btn.setText(color_hex)
            self.on_room_property_changed('background_color', color_hex)
    
    def get_available_backgrounds(self) -> Dict[str, Any]:
        """Get available backgrounds from project"""
        try:
            parent = self.parent()
            while parent:
                # Try current_project_data first
                if hasattr(parent, 'current_project_data') and parent.current_project_data:
                    assets = parent.current_project_data.get('assets', {})
                    backgrounds = assets.get('backgrounds', {})

                    # If no backgrounds found, try getting from project_manager
                    if not backgrounds and hasattr(parent, 'project_manager') and parent.project_manager:
                        pm_data = parent.project_manager.get_current_project_data()
                        if pm_data:
                            pm_assets = pm_data.get('assets', {})
                            backgrounds = pm_assets.get('backgrounds', {})
                            # Also update current_project_data to stay in sync
                            if backgrounds:
                                parent.current_project_data.setdefault('assets', {})['backgrounds'] = backgrounds

                    return backgrounds
                parent = parent.parent()
            return {}
        except Exception as e:
            print(f"❌ Error getting available backgrounds: {e}")
            return {}

    def update_room_preview(self):
        """Update the room preview image"""
        if not self.current_room_editor:
            return
        
        try:
            # Get preview size
            preview_size = self.preview_label.size()
            max_width = max(200, preview_size.width() - 20)
            max_height = max(150, preview_size.height() - 20)
            
            # Generate preview from room editor
            if hasattr(self.current_room_editor, 'generate_room_preview'):
                preview_pixmap = self.current_room_editor.generate_room_preview(max_width, max_height)
                
                if not preview_pixmap.isNull():
                    # Display the preview
                    self.preview_label.setPixmap(preview_pixmap)
                    self.preview_label.setText("")  # Clear any text
                    
                    # Update tooltip
                    room_data = self.current_room_editor.get_data()
                    instance_count = len(room_data.get('instances', []))
                    tooltip = self.tr("Room Preview\n{0}x{1}\n{2} instances").format(room_data.get('width', 0), room_data.get('height', 0), instance_count)
                    self.preview_label.setToolTip(tooltip)
                else:
                    self.preview_label.setText(self.tr("Preview\nGeneration Failed"))
            else:
                self.preview_label.setText(self.tr("Preview\nNot Available"))
        
        except Exception as e:
            print(f"Error updating room preview: {e}")
            self.preview_label.setText(self.tr("Preview\nUpdate Error"))
    
    def on_room_property_changed(self, property_name: str, value):
        """Handle room property changes and notify room editor"""
        # Don't emit during initial property setup (prevents cross-contamination)
        if getattr(self, '_setting_room_properties', False):
            return

        print(f"Properties panel: {property_name} changed to {value}")

        # Emit signal that room editor will catch
        self.room_property_changed.emit(property_name, value)

        # Update preview after a short delay to allow room editor to process change
        QTimer.singleShot(100, self.update_room_preview)
    
    def clear_room_context(self):
        """Clear room editor context"""
        # Just clear references, don't worry about disconnecting
        self.current_room_editor = None
        if hasattr(self, 'current_asset') and self.current_asset and self.current_asset[0] == 'room_editor':
            self.current_asset = None
            self.show_default_state()
    
    def show_default_state(self):
        """Show default state when no asset is selected"""
        self.name_label.setText(self.tr("No asset selected"))
        self.type_label.setText("-")
        self.status_label.setText("-")
        
        # Clear properties
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.preview_label.setText(self.tr("No preview available"))
        self.preview_label.setPixmap(QPixmap())  # Clear any pixmap
    
    def set_asset(self, asset_data):
        """Set asset data for display"""
        if not asset_data:
            return
        
        asset_type = asset_data.get('asset_type', 'unknown')
        asset_name = asset_data.get('name', 'unknown')
        asset_info = asset_data.get('data', {})
        
        # If we're in an EDITOR context (room/object editor open), only block if 
        # the asset being selected is the SAME TYPE as the open editor
        if self.current_room_editor and asset_type == 'rooms':
            return  # Don't override room editor with room asset selection
        if self.current_object_editor and asset_type == 'objects':
            return  # Don't override object editor with object asset selection
        
        # For sprites/backgrounds/other assets, always show preview
        self.show_asset_properties(asset_type, asset_name, asset_info)
    
    def show_asset_properties(self, asset_type: str, asset_name: str, asset_data: Dict[str, Any]):
        """Show properties for an asset with image preview"""
        self.current_asset = (asset_type, asset_name, asset_data)
        
        # Update info
        self.name_label.setText(asset_name)
        self.type_label.setText(asset_type.title())
        self.status_label.setText(self.tr("Loaded"))
        
        # Clear previous properties
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add properties based on asset type
        if asset_type == 'rooms':
            width_edit = QLineEdit(str(asset_data.get('width', 800)))
            height_edit = QLineEdit(str(asset_data.get('height', 600)))
            bg_color_edit = QLineEdit(asset_data.get('background_color', '#87CEEB'))
            
            self.properties_layout.addRow(self.tr("Width:"), width_edit)
            self.properties_layout.addRow(self.tr("Height:"), height_edit)
            self.properties_layout.addRow(self.tr("Background:"), bg_color_edit)

            # Update preview
            self.preview_label.setPixmap(QPixmap())  # Clear pixmap
            self.preview_label.setText(self.tr("Room: {0}\n{1} x {2}").format(asset_name, asset_data.get('width', 800), asset_data.get('height', 600)))
        
        elif asset_type == 'sprites':
            # Sprite properties
            frames = asset_data.get('frames', 1)
            frame_width = asset_data.get('frame_width', asset_data.get('width', 0))
            frame_height = asset_data.get('frame_height', asset_data.get('height', 0))

            # Show frame dimensions for animated sprites
            if frames > 1:
                width_edit = QLineEdit(f"{frame_width} (frame)")
                height_edit = QLineEdit(f"{frame_height} (frame)")
            else:
                width_edit = QLineEdit(str(asset_data.get('width', 0)))
                height_edit = QLineEdit(str(asset_data.get('height', 0)))
            width_edit.setReadOnly(True)
            height_edit.setReadOnly(True)

            frames_edit = QLineEdit(str(frames))
            frames_edit.setReadOnly(True)
            origin_x_edit = QLineEdit(str(asset_data.get('origin_x', 0)))
            origin_x_edit.setReadOnly(True)
            origin_y_edit = QLineEdit(str(asset_data.get('origin_y', 0)))
            origin_y_edit.setReadOnly(True)
            speed_edit = QLineEdit(f"{asset_data.get('speed', 10.0)} FPS")
            speed_edit.setReadOnly(True)

            self.properties_layout.addRow(self.tr("Width:"), width_edit)
            self.properties_layout.addRow(self.tr("Height:"), height_edit)
            self.properties_layout.addRow(self.tr("Frames:"), frames_edit)
            self.properties_layout.addRow(self.tr("Origin X:"), origin_x_edit)
            self.properties_layout.addRow(self.tr("Origin Y:"), origin_y_edit)
            self.properties_layout.addRow(self.tr("Speed:"), speed_edit)

            # Show animation type for animated sprites
            if frames > 1:
                anim_type = asset_data.get('animation_type', 'strip_h')
                anim_type_display = {
                    'strip_h': self.tr('Horizontal Strip'),
                    'strip_v': self.tr('Vertical Strip'),
                    'grid': self.tr('Grid'),
                    'single': self.tr('Single Frame')
                }.get(anim_type, anim_type)
                anim_edit = QLineEdit(anim_type_display)
                anim_edit.setReadOnly(True)
                self.properties_layout.addRow(self.tr("Animation:"), anim_edit)

            # Show file path
            file_path = asset_data.get('file_path', 'N/A')
            file_path_edit = QLineEdit(file_path)
            file_path_edit.setReadOnly(True)
            self.properties_layout.addRow(self.tr("File:"), file_path_edit)

            # Load and display the sprite image (with animation if applicable)
            self.load_sprite_preview(asset_name, asset_data)
        
        elif asset_type == 'backgrounds':
            # Background properties
            width_edit = QLineEdit(str(asset_data.get('width', 0)))
            width_edit.setReadOnly(True)
            height_edit = QLineEdit(str(asset_data.get('height', 0)))
            height_edit.setReadOnly(True)
            
            self.properties_layout.addRow(self.tr("Width:"), width_edit)
            self.properties_layout.addRow(self.tr("Height:"), height_edit)

            # Show file path
            file_path = asset_data.get('file_path', 'N/A')
            file_path_edit = QLineEdit(file_path)
            file_path_edit.setReadOnly(True)
            self.properties_layout.addRow(self.tr("File:"), file_path_edit)
            
            # Try to load and display the actual background image
            self.load_sprite_preview(asset_name, asset_data)

        elif asset_type == 'objects':
            # Object properties - use dedicated method
            self.show_object_properties(asset_data)
        
        else:
            # Generic properties
            for key, value in asset_data.items():
                if key not in ['name', 'type']:
                    prop_edit = QLineEdit(str(value))
                    self.properties_layout.addRow(f"{key.title()}:", prop_edit)
            
            self.preview_label.setPixmap(QPixmap())  # Clear pixmap
            self.preview_label.setText(self.tr("{0}: {1}").format(asset_type.title(), asset_name))

    def load_sprite_preview(self, asset_name: str, asset_data: Dict[str, Any]):
        """Load and display sprite/background image in preview"""
        
        # Try to get the image path - handle both absolute and relative paths
        image_path = None
        
        # First try project_path (handle both absolute and relative)
        if 'project_path' in asset_data and asset_data['project_path']:
            project_path = asset_data['project_path']
            
            if Path(project_path).is_absolute():
                # Absolute path - use directly
                image_path = project_path
            else:
                # Relative path - combine with project base
                project_base = self.get_project_base_path()
                if project_base:
                    image_path = str(Path(project_base) / project_path)
        
        # If no project_path, construct from relative file_path
        elif 'file_path' in asset_data and asset_data['file_path']:
            relative_path = asset_data['file_path']
            project_base = self.get_project_base_path()
            
            if project_base:
                image_path = str(Path(project_base) / relative_path)
            else:
                self.preview_label.setText(f"Cannot determine project path for {asset_name}")
                return
        else:
            print(f"❌ DEBUG: No 'project_path' or 'file_path' in asset_data")
        
        if not image_path:
            self.preview_label.setText(self.tr("No image file path found for {0}").format(asset_name))
            return

        # Check if file exists
        if not Path(image_path).exists():
            self.preview_label.setText(self.tr("Image file not found:\n{0}").format(Path(image_path).name))
            return

        try:
            # Load the image
            pixmap = QPixmap(str(image_path))
            
            if pixmap.isNull():
                self.preview_label.setText(self.tr("Failed to load image:\n{0}").format(asset_name))
                return
            
            # Scale image to fit preview area while maintaining aspect ratio
            preview_size = self.preview_label.size()
            max_width = max(200, preview_size.width() - 20)
            max_height = max(180, preview_size.height() - 20)
            
            scaled_pixmap = pixmap.scaled(
                max_width, max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Display the image
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.setText("")

            # Update tooltip with image info
            info_text = self.tr("{0}\n{1}x{2}").format(asset_name, pixmap.width(), pixmap.height())
            self.preview_label.setToolTip(info_text)

        except Exception as e:
            print(f"❌ DEBUG: Exception loading image: {e}")
            import traceback
            traceback.print_exc()
            self.preview_label.setText(self.tr("Error loading image:\n{0}").format(str(e)))
    
    def set_object_editor_context(self, object_editor, object_name: str, object_properties: Dict[str, Any]):
        """Set context to show object properties from object editor"""

        self.current_object_editor = object_editor
        self.current_asset = ('object_editor', object_name, object_properties)
        
        # Update info
        self.name_label.setText(object_name)
        self.type_label.setText(self.tr("Object (Editor)"))
        self.status_label.setText(self.tr("Active"))
        
        self.show_object_properties(object_properties)

    def show_object_properties(self, object_data: Dict[str, Any]):
        """Show object properties with live editing"""
        
        # Prevent recursion during property setup
        if getattr(self, '_updating_properties', False):
            return
            
        self._updating_properties = True
        
        try:
            # Clear previous properties
            while self.properties_layout.count():
                child = self.properties_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Clear reference to prevent access to deleted widgets
            if hasattr(self, 'sprite_combo'):
                self.sprite_combo = None
            
            # Sprite assignment
            self.sprite_combo = QComboBox()
            self.sprite_combo.addItem(self.tr("None"))
            
            # Get available sprites from project
            available_sprites = self.get_available_sprites()
            for sprite_name in available_sprites.keys():
                self.sprite_combo.addItem(sprite_name)
            
            current_sprite = object_data.get('sprite', '')
            if current_sprite:
                index = self.sprite_combo.findText(current_sprite)
                if index >= 0:
                    self.sprite_combo.setCurrentIndex(index)
            
            # Object flags
            self.visible_check = QCheckBox()
            self.visible_check.setChecked(object_data.get('visible', True))
            self.visible_check.toggled.connect(lambda v: self.on_object_property_changed('visible', v))
            
            self.solid_check = QCheckBox()
            self.solid_check.setChecked(object_data.get('solid', False))
            self.solid_check.toggled.connect(lambda v: self.on_object_property_changed('solid', v))
            
            self.persistent_check = QCheckBox()
            self.persistent_check.setChecked(object_data.get('persistent', False))
            self.persistent_check.toggled.connect(lambda v: self.on_object_property_changed('persistent', v))
            
            # Add to layout
            self.properties_layout.addRow(self.tr("Sprite:"), self.sprite_combo)
            # Show sprite dimensions if a sprite is assigned
            if current_sprite and current_sprite in available_sprites:
                sprite_data = available_sprites[current_sprite]
                sprite_width = sprite_data.get('width', '?')
                sprite_height = sprite_data.get('height', '?')
                size_label = QLabel(self.tr("{0} x {1}").format(sprite_width, sprite_height))
                size_label.setStyleSheet("color: #666;")
                self.properties_layout.addRow(self.tr("Sprite Size:"), size_label)

            self.properties_layout.addRow(self.tr("Visible:"), self.visible_check)
            self.properties_layout.addRow(self.tr("Solid:"), self.solid_check)
            self.properties_layout.addRow(self.tr("Persistent:"), self.persistent_check)

            # Event count (read-only)
            event_count = len(object_data.get('events', {}))
            self.properties_layout.addRow(self.tr("Events:"), QLabel(str(event_count)))
            
            # Update preview with sprite
            self.show_object_preview(object_data)
            
        finally:
            # Clear the flag after a delay to allow UI to settle
            QTimer.singleShot(200, self._finish_property_setup)

    def _on_sprite_changed(self, sprite_name: str):
            """Handle sprite combo changes"""
            if getattr(self, '_updating_properties', False):
                return

            value = sprite_name if sprite_name != self.tr("None") else ''
            self.on_object_property_changed('sprite', value)
    
    def _finish_property_setup(self):
            """Finish property setup by clearing flag and connecting signals"""
            self._updating_properties = False
            
            # Now connect the sprite combo signal after flag is cleared
            if hasattr(self, 'sprite_combo') and self.sprite_combo:
                try:
                    self.sprite_combo.currentTextChanged.connect(self._on_sprite_changed)
                except RuntimeError:
                    # Widget may have been deleted
                    pass

    def get_available_sprites(self) -> Dict[str, Any]:
        """Get available sprites from project data"""
        try:
            # Try to get sprites from parent IDE
            parent = self.parent()
            
            level = 0
            while parent:
                level += 1
                
                if hasattr(parent, 'current_project_data'):
                    if parent.current_project_data:
                        
                        # Sprites are under 'assets' -> 'sprites' in the JSON
                        assets = parent.current_project_data.get('assets', {})
                        
                        sprites = assets.get('sprites', {})
                        return sprites
                
                parent = parent.parent()
                if level > 10:  # Safety limit
                    print("⚠️ DEBUG: Too many parent levels, stopping")
                    break
            
            # Fallback: empty dict
            print("⚠️ DEBUG: No parent with current_project_data found")
            return {}
        except Exception as e:
            print(f"❌ Error getting available sprites: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def refresh_sprite_combo(self):
        """Refresh the sprite combo box after project changes"""
        # Don't refresh if we're currently updating properties
        if getattr(self, '_updating_properties', False):
            return
            
        # Check if sprite_combo exists and hasn't been deleted
        if hasattr(self, 'sprite_combo') and self.sprite_combo:
            try:
                # Block signals during refresh to prevent loops
                self.sprite_combo.blockSignals(True)
                
                current_selection = self.sprite_combo.currentText()
                
                # Clear and repopulate
                self.sprite_combo.clear()
                self.sprite_combo.addItem(self.tr("None"))
                
                available_sprites = self.get_available_sprites()
                for sprite_name in available_sprites.keys():
                    self.sprite_combo.addItem(sprite_name)
                
                # Restore selection
                index = self.sprite_combo.findText(current_selection)
                if index >= 0:
                    self.sprite_combo.setCurrentIndex(index)
                
                # Re-enable signals
                self.sprite_combo.blockSignals(False)
                
            except RuntimeError:
                # Widget has been deleted, skip refresh
                return

    def show_object_preview(self, object_data: Dict[str, Any]):
        """Show object preview (sprite or placeholder)"""
        sprite_name = object_data.get('sprite', '')
        
        if sprite_name:
            # Try to get sprite data from project
            available_sprites = self.get_available_sprites()
            
            if sprite_name in available_sprites:
                sprite_data = available_sprites[sprite_name]
                
                # Get sprite dimensions
                sprite_width = sprite_data.get('width', 'Unknown')
                sprite_height = sprite_data.get('height', 'Unknown')
                object_name = object_data.get('name', 'Unknown')
                event_count = len(object_data.get('events', {}))
                
                # Load the preview image (this sets a basic tooltip)
                self.load_sprite_preview(sprite_name, sprite_data)

                # Override tooltip with more detailed object info
                tooltip_text = self.tr("Object: {0}\nSprite: {1}\nSize: {2}x{3}\nEvents: {4}").format(
                    object_name, sprite_name, sprite_width, sprite_height, event_count
                )
                self.preview_label.setToolTip(tooltip_text)
                return
            else:
                print(f"⚠️ DEBUG: Sprite '{sprite_name}' not found in available sprites")
        
        # Show default object preview (no sprite or sprite not found)
        self.preview_label.setPixmap(QPixmap())  # Clear pixmap
        object_name = object_data.get('name', 'Unknown')
        event_count = len(object_data.get('events', {}))
        visible = object_data.get('visible', True)
        solid = object_data.get('solid', False)

        status_parts = [self.tr("Object: {0}").format(object_name)]
        if sprite_name:
            status_parts.append(self.tr("Sprite: {0}").format(sprite_name))
        else:
            status_parts.append(self.tr("No sprite assigned"))
        status_parts.append(self.tr("Events: {0}").format(event_count))

        flags = []
        if visible:
            flags.append(self.tr("Visible"))
        if solid:
            flags.append(self.tr("Solid"))
        if flags:
            status_parts.append(" ".join(flags))

        status_text = "\n".join(status_parts)
        self.preview_label.setText(status_text)
        self.preview_label.setToolTip(status_text)

    def on_object_property_changed(self, property_name: str, value):
        """Handle object property changes and notify ONLY the current object editor"""
        print(f"Properties panel: object {property_name} changed to {value}")
        
        # Special handling for sprite changes
        if property_name == 'sprite':
            print(f"Sprite change detected: {value}")
            
            # Update the preview immediately
            if hasattr(self, 'current_asset') and self.current_asset:
                object_data = self.current_asset[2].copy()
                object_data[property_name] = value
                self.show_object_preview(object_data)
        
        # Send the property change ONLY to the current object editor
        if hasattr(self, 'current_object_editor') and self.current_object_editor:
            try:
                # Call the method directly instead of using signals
                self.current_object_editor.update_object_property_from_ide(property_name, value)
            except RuntimeError:
                # Object editor has been deleted
                self.current_object_editor = None

    def clear_object_context(self):
        """Clear object editor context"""
        self.current_object_editor = None
        if hasattr(self, 'current_asset') and self.current_asset and self.current_asset[0] == 'object_editor':
            self.current_asset = None
            self.show_default_state()

    def safe_disconnect_signal(self, signal, slot=None):
        """Safely disconnect a signal, avoiding warnings"""
        if not signal:
            return False
        try:
            if slot:
                try:
                    signal.disconnect(slot)
                except (RuntimeError, TypeError):
                    # Try general disconnect as fallback
                    signal.disconnect()
            else:
                signal.disconnect()
            return True
        except (RuntimeError, TypeError, AttributeError):
            # Signal has no connections or other error
            return False
        
    def set_project(self, project_path, project_data):
        """Set project data - compatibility method"""
        pass