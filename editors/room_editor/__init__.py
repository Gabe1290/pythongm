#!/usr/bin/env python3
"""
Room Editor - Main class
Enhanced room editor that allows placing objects in rooms
"""

import json
import copy
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                               QScrollArea, QToolBar, QMessageBox, QLabel)
from PySide6.QtCore import Qt, Signal, QTimer

from .room_canvas import RoomCanvas
from .object_palette import ObjectPalette
from .instance_properties import InstanceProperties


class RoomEditor(QWidget):
    """Complete room editor with object placement"""
    
    save_requested = Signal(str, dict)
    close_requested = Signal(str)
    data_modified = Signal(str)
    room_editor_activated = Signal(str, dict)
    
    def __init__(self, project_path, parent=None):
        super().__init__(parent)
        self.project_path = Path(project_path)
        self.asset_name = ""
        self.current_room_properties = {
            'width': 1024,
            'height': 768,
            'background_color': '#87CEEB',
            'background_image': '',
            'tile_horizontal': False,
            'tile_vertical': False,
            'instances': []
        }
        self.is_modified = False
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # Main content layout
        content_layout = QHBoxLayout()
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Object palette and properties
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Object palette
        self.object_palette = ObjectPalette()
        left_layout.addWidget(self.object_palette)
        
        # Instance properties
        self.instance_properties = InstanceProperties()
        left_layout.addWidget(self.instance_properties)
        
        left_panel.setMaximumWidth(250)
        splitter.addWidget(left_panel)
        
        # Center - Room canvas in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.room_canvas = RoomCanvas()
        scroll_area.setWidget(self.room_canvas)
        
        splitter.addWidget(scroll_area)
        
        # Set splitter proportions
        splitter.setSizes([250, 600])
        
        content_layout.addWidget(splitter)
        main_layout.addWidget(content_widget)
    
    def create_toolbar(self):
        """Create the room editor toolbar"""
        self.toolbar = QToolBar(self.tr("Room Editor"))
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)

        # Save button (shortcut handled by main window menu)
        save_action = self.toolbar.addAction(self.tr("💾 Save"))
        save_action.setToolTip(self.tr("Save room (Ctrl+S)"))
        save_action.triggered.connect(self.save)
        
        self.toolbar.addSeparator()
        
        # Undo/Redo buttons (shortcuts handled by main window menu)
        self.undo_action = self.toolbar.addAction(self.tr("↶ Undo"))
        self.undo_action.setToolTip(self.tr("Undo (Ctrl+Z)"))
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self.undo)

        self.redo_action = self.toolbar.addAction(self.tr("↷ Redo"))
        self.redo_action.setToolTip(self.tr("Redo (Ctrl+Y)"))
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self.redo)

        self.toolbar.addSeparator()

        # Edit actions (shortcuts handled by main window menu)
        self.cut_action = self.toolbar.addAction(self.tr("✂️ Cut"))
        self.cut_action.setToolTip(self.tr("Cut selected instance (Ctrl+X)"))
        self.cut_action.setEnabled(False)
        self.cut_action.triggered.connect(self.cut_instance)

        self.copy_action = self.toolbar.addAction(self.tr("📋 Copy"))
        self.copy_action.setToolTip(self.tr("Copy selected instance (Ctrl+C)"))
        self.copy_action.setEnabled(False)
        self.copy_action.triggered.connect(self.copy_instance)

        self.paste_action = self.toolbar.addAction(self.tr("📄 Paste"))
        self.paste_action.setToolTip(self.tr("Paste instance (Ctrl+V)"))
        self.paste_action.setEnabled(False)
        self.paste_action.triggered.connect(self.paste_instance)

        self.duplicate_action = self.toolbar.addAction(self.tr("⎘ Duplicate"))
        self.duplicate_action.setToolTip(self.tr("Duplicate selected instance (Ctrl+D)"))
        self.duplicate_action.setEnabled(False)
        self.duplicate_action.triggered.connect(self.duplicate_instance)

        self.toolbar.addSeparator()

        # Grid toggle
        self.grid_action = self.toolbar.addAction(self.tr("🔲 Grid"))
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.setToolTip(self.tr("Toggle grid visibility"))
        self.grid_action.triggered.connect(self.toggle_grid)

        # Snap to grid toggle
        self.snap_action = self.toolbar.addAction(self.tr("🧲 Snap"))
        self.snap_action.setCheckable(True)
        self.snap_action.setChecked(True)
        self.snap_action.setToolTip(self.tr("Toggle snap to grid"))
        self.snap_action.triggered.connect(self.toggle_snap)
        
        self.toolbar.addSeparator()
        
        # Clear all instances
        clear_action = self.toolbar.addAction(self.tr("🗑️ Clear All"))
        clear_action.setToolTip(self.tr("Remove all object instances"))
        clear_action.triggered.connect(self.clear_all_instances)

        self.toolbar.addSeparator()

        # Status label
        self.status_label = QLabel(self.tr("Ready"))
        self.toolbar.addWidget(self.status_label)
    
    def toggle_grid(self, checked):
        """Toggle grid visibility"""
        if hasattr(self, 'room_canvas'):
            self.room_canvas.grid_enabled = checked
            self.room_canvas.update()
    
    def toggle_snap(self, checked):
        """Toggle snap to grid"""
        if hasattr(self, 'room_canvas'):
            self.room_canvas.snap_to_grid = checked
    
    def clear_all_instances(self):
        """Clear all object instances with confirmation"""
        if hasattr(self, 'room_canvas') and self.room_canvas.instances:
            reply = QMessageBox.question(
                self,
                self.tr("Clear All Instances"),
                self.tr("Are you sure you want to remove all {0} object instances?").format(len(self.room_canvas.instances)),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.room_canvas.clear_instances()
                self.instance_properties.set_instance(None)
                self.mark_modified()
                self.update_status(self.tr("All instances cleared"))
    
    def update_status(self, message, timeout=3000):
        """Update status message"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
            if timeout > 0:
                QTimer.singleShot(timeout, lambda: self.status_label.setText(self.tr("Ready")) if hasattr(self, 'status_label') else None)
    
    def setup_connections(self):
        """Set up signal connections"""
        self.object_palette.object_selected.connect(self.on_object_selected)
        self.room_canvas.instance_selected.connect(self.on_instance_selected)
        self.room_canvas.instance_moved.connect(self.on_instance_moved)
        self.room_canvas.instance_added.connect(self.on_instance_added)
        self.instance_properties.property_changed.connect(self.on_instance_property_changed)
        
        # Room canvas
        self.room_canvas.instance_selected.connect(self.on_instance_selected)
        self.room_canvas.instance_added.connect(self.mark_modified)
        self.room_canvas.instance_moved.connect(self.mark_modified)
        
        # Instance properties
        self.instance_properties.property_changed.connect(self.on_instance_property_changed)

        # Connect undo stack signals
        if hasattr(self.room_canvas, 'undo_stack'):
            self.room_canvas.undo_stack.canUndoChanged.connect(self.update_undo_actions)
            self.room_canvas.undo_stack.canRedoChanged.connect(self.update_undo_actions)
        
        # Setup keyboard shortcuts that work regardless of focus
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for the room editor"""
        from PySide6.QtGui import QShortcut, QKeySequence
        
        # Delete shortcut - works even if canvas doesn't have focus
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.delete_shortcut.activated.connect(self.delete_selected_instances)
        
        print("✓ Room editor keyboard shortcuts registered (Delete key)")

    def delete_selected_instances(self):
        """Delete currently selected instances"""
        if self.room_canvas.selected_instances:
            instances_to_delete = self.room_canvas.selected_instances.copy()
            print(f"DELETE: Removing {len(instances_to_delete)} instance(s)")
            self.room_canvas.remove_instances(instances_to_delete, use_undo=True)
            self.mark_modified()
            count = len(instances_to_delete)
            if count == 1:
                self.update_status(self.tr("Deleted {0}").format(instances_to_delete[0].object_name))
            else:
                self.update_status(self.tr("Deleted {0} instances").format(count))

    def refresh_object_sprites(self, object_name: str):
        """Refresh sprites for a specific object"""
        if object_name in self.room_canvas.sprite_cache:
            del self.room_canvas.sprite_cache[object_name]
        
        self.object_palette.refresh_object_list()
        self.room_canvas.update()
        
        print(f"Refreshed sprites for object: {object_name}")

    def load_asset(self, asset_name, asset_data):
        """Load room asset data"""
        self.asset_name = asset_name
        # Use deep copy to prevent cross-contamination between multiple open room editors
        self.current_room_properties = copy.deepcopy(asset_data)
        
        # Set room properties including background settings
        self.room_canvas.set_room_properties(
            asset_data.get('width', 1024),
            asset_data.get('height', 768),
            asset_data.get('background_color', '#87CEEB'),
            asset_data.get('background_image', ''),
            asset_data.get('tile_horizontal', False),
            asset_data.get('tile_vertical', False)
        )
        
        # Pass project information to canvas for sprite loading
        self.pass_project_info_to_canvas()
        
        # Load instances
        instances_data = asset_data.get('instances', [])
        self.room_canvas.load_instances(instances_data)
        
        # Load available objects from project
        self.load_available_objects()

        # Emit activation signal
        self.room_editor_activated.emit(asset_name, self.current_room_properties)

        self.is_modified = False
        self.update_status(self.tr("Loaded room '{0}' with {1} instances").format(asset_name, len(instances_data)))
    
    def pass_project_info_to_canvas(self):
        """Pass project information to canvas and palette"""
        if hasattr(self, 'room_canvas') and self.parent():
            ide_window = self.parent()
            while ide_window and not hasattr(ide_window, 'current_project_data'):
                ide_window = ide_window.parent()
            
            if ide_window and hasattr(ide_window, 'current_project_data'):
                project_path = getattr(ide_window, 'current_project_path', None)
                project_data = ide_window.current_project_data
                
                self.room_canvas.sprite_cache.clear()
                self.room_canvas.set_project_info(project_path, project_data)
                self.object_palette.set_project_info(project_path, project_data)

    def load_available_objects(self):
        """Load available objects from the project"""
        try:
            project_file = self.project_path / "project.json"
            if project_file.exists():
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
                
                objects = project_data.get('assets', {}).get('objects', {})
                
                self.object_palette.set_project_info(self.project_path, project_data)
                self.object_palette.set_available_objects(objects)

                self.update_status(self.tr("Loaded {0} objects").format(len(objects)))

        except Exception as e:
            print(f"Error loading objects: {e}")
            self.update_status(self.tr("Error loading objects: {0}").format(e), 5000)
    
    def on_object_selected(self, object_name):
        """Handle object selection from palette"""
        self.room_canvas.set_current_object_type(object_name)
        if object_name:
            self.update_status(self.tr("Selected '{0}' - Click in room to place").format(object_name))
        else:
            self.update_status(self.tr("No object selected"))
    
    def on_instance_selected(self, instance):
        """Handle instance selection in canvas"""
        self.instance_properties.set_instance(instance)
        
        # Get selection count
        selection_count = self.room_canvas.get_selected_count()
        
        # Enable/disable edit buttons based on selection
        has_selection = selection_count > 0
        self.cut_action.setEnabled(has_selection)
        self.copy_action.setEnabled(has_selection)
        self.duplicate_action.setEnabled(has_selection)
        
        if selection_count > 0:
            if selection_count == 1:
                self.update_status(self.tr("Selected {0} at ({1}, {2})").format(instance.object_name, instance.x, instance.y))
            else:
                self.update_status(self.tr("Selected {0} instances").format(selection_count))
        else:
            self.update_status(self.tr("No instance selected"))
    
    def on_instance_moved(self, instance):
        """Handle instance movement"""
        self.mark_modified()
        self.instance_properties.set_instance(instance)
        self.update_status(self.tr("Moved {0} to ({1}, {2})").format(instance.object_name, instance.x, instance.y))

    def on_instance_added(self, instance):
        """Handle instance addition"""
        self.mark_modified()
        self.update_status(self.tr("Added {0} at ({1}, {2})").format(instance.object_name, instance.x, instance.y))
    
    def on_instance_property_changed(self, instance, property_name, value):
        """Handle instance property change"""
        if property_name == "delete":
            self.room_canvas.remove_instance(instance)
            self.instance_properties.set_instance(None)
            self.update_status(self.tr("Deleted {0} instance").format(instance.object_name))
        else:
            self.update_status(self.tr("Updated {0} {1}: {2}").format(instance.object_name, property_name, value))

        self.mark_modified()
        self.room_canvas.update()
    
    def mark_modified(self):
        """Mark the room as modified"""
        if not self.is_modified:
            self.is_modified = True
            self.data_modified.emit(self.asset_name)
    
    def get_data(self):
        """Get current room data with all required fields"""
        # Use deep copy to ensure returned data is independent
        data = copy.deepcopy(self.current_room_properties)
        data['instances'] = self.room_canvas.get_instances()
        
        if 'name' not in data:
            data['name'] = self.asset_name
        
        if 'asset_type' not in data:
            data['asset_type'] = 'room'
        
        if 'imported' not in data:
            data['imported'] = True
        
        from datetime import datetime
        data['modified'] = datetime.now().isoformat()
        
        return data
    
    def save(self):
        """Save the room"""
        try:
            self.update_status(self.tr("Saving room..."))
            data = self.get_data()
            self.save_requested.emit(self.asset_name, data)
            self.is_modified = False
            self.update_status(self.tr("Room '{0}' saved successfully").format(self.asset_name))
            return True
        except Exception as e:
            print(f"Error saving room: {e}")
            self.update_status(self.tr("Error saving room: {0}").format(e), 5000)
            QMessageBox.critical(self, self.tr("Save Error"), self.tr("Failed to save room:\n{0}").format(e))
            return False
    
    def update_room_property_from_ide(self, property_name, value):
        """Update room property from IDE properties panel"""
        print(f"Room editor updating property: {property_name} = {value}")
        
        self.current_room_properties[property_name] = value
        
        if property_name in ['width', 'height', 'background_color', 'background_image', 'tile_horizontal', 'tile_vertical']:
            self.room_canvas.set_room_properties(
                self.current_room_properties.get('width', 1024),
                self.current_room_properties.get('height', 768),
                self.current_room_properties.get('background_color', '#87CEEB'),
                self.current_room_properties.get('background_image', ''),
                self.current_room_properties.get('tile_horizontal', False),
                self.current_room_properties.get('tile_vertical', False)
            )
            print(f"Canvas updated with new {property_name}: {value}")
        
        self.mark_modified()
    
    def undo(self):
        """Undo last action"""
        if hasattr(self.room_canvas, 'undo_stack'):
            self.room_canvas.undo_stack.undo()
            self.mark_modified()
            self.update_status(self.tr("Undo"))

    def redo(self):
        """Redo last undone action"""
        if hasattr(self.room_canvas, 'undo_stack'):
            self.room_canvas.undo_stack.redo()
            self.mark_modified()
            self.update_status(self.tr("Redo"))

    def update_undo_actions(self):
        """Update undo/redo button states"""
        if hasattr(self.room_canvas, 'undo_stack'):
            can_undo = self.room_canvas.undo_stack.canUndo()
            can_redo = self.room_canvas.undo_stack.canRedo()
            
            self.undo_action.setEnabled(can_undo)
            self.redo_action.setEnabled(can_redo)
            
            if can_undo:
                undo_text = self.room_canvas.undo_stack.undoText()
                self.undo_action.setText(self.tr("↶ Undo: {0}").format(undo_text))
            else:
                self.undo_action.setText(self.tr("↶ Undo"))

            if can_redo:
                redo_text = self.room_canvas.undo_stack.redoText()
                self.redo_action.setText(self.tr("↷ Redo: {0}").format(redo_text))
            else:
                self.redo_action.setText(self.tr("↷ Redo"))

    def cut_instance(self):
        """Cut selected instance(s)"""
        if hasattr(self.room_canvas, 'cut_selected_instances'):
            if self.room_canvas.cut_selected_instances():
                self.paste_action.setEnabled(True)
                self.mark_modified()
                count = self.room_canvas.get_selected_count()
                self.update_status(self.tr("Cut {0} instance(s) to clipboard").format(count))

    def copy_instance(self):
        """Copy selected instance(s)"""
        if hasattr(self.room_canvas, 'copy_selected_instances'):
            if self.room_canvas.copy_selected_instances():
                self.paste_action.setEnabled(True)
                count = self.room_canvas.get_selected_count()
                self.update_status(self.tr("Copied {0} instance(s) to clipboard").format(count))
                
    def paste_instance(self):
        """Paste instance(s) from clipboard"""
        if hasattr(self.room_canvas, 'paste_instances'):
            # Get count before pasting
            clipboard_count = len(self.room_canvas.clipboard_instances)

            if self.room_canvas.paste_instances():
                self.mark_modified()
                if clipboard_count == 1:
                    self.update_status(self.tr("Instance pasted"))
                else:
                    self.update_status(self.tr("Pasted {0} instances").format(clipboard_count))

    def duplicate_instance(self):
        """Duplicate selected instance(s)"""
        if hasattr(self.room_canvas, 'duplicate_selected_instances'):
            if self.room_canvas.duplicate_selected_instances():
                self.mark_modified()
                count = self.room_canvas.get_selected_count()
                self.update_status(self.tr("Duplicated {0} instance(s)").format(count))