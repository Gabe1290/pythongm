#!/usr/bin/env python3
"""
Object Editor for GameMaker IDE
Main object editor class for editing game objects
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QToolBar,
    QLabel, QPushButton, QSpinBox, QComboBox, QCheckBox,
    QMessageBox, QGroupBox, QSizePolicy, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap

from ..base_editor import BaseEditor, EditorUndoCommand
from .object_properties_panel import ObjectPropertiesPanel
from .object_events_panel import ObjectEventsPanel
from ..object_editor_components import ActionListWidget, VisualScriptingArea
from visual_programming import (
    VisualCanvas, NodePalette, NodePropertiesPanel, 
    create_node_from_type, VisualCodeGenerator
)

class ObjectChangeCommand(EditorUndoCommand):
    """Undo command for object changes"""
    
    def __init__(self, object_editor, description: str, old_data: Dict[str, Any]):
        super().__init__(object_editor, description)
        self.old_data = old_data.copy()


class ObjectEditor(BaseEditor):
    """Main object editor widget"""
    
    # Additional signals specific to object editor
    object_property_changed = Signal(str, object)  # property_name, value
    object_editor_activated = Signal(str, dict)    # object_name, properties
    
    def __init__(self, project_path: str = None, parent=None):
        # Initialize data before calling super().__init__()
        self.available_sprites = {}
        self.current_object_properties = {}
        self._pending_events_data = None
        
        # Call parent constructor (this sets up base UI including toolbar)
        super().__init__(project_path, parent)
        
        # Object-specific setup AFTER base setup
        self.setup_object_ui()
        self.setup_object_connections()
        
        # Apply any pending data that was loaded before UI was ready
        if hasattr(self, 'apply_pending_data'):
            self.apply_pending_data()
        
        self.load_project_assets_if_available()
        
        # Final check that save functionality is working
        print("ObjectEditor initialization complete")
        if hasattr(self, 'save_action'):
            print(f"Save action available: {self.save_action.text()}")
        else:
            print("WARNING: No save action found after initialization!")
        
        # Verify events panel exists
        if hasattr(self, 'events_panel'):
            print("Events panel initialized successfully")
        else:
            print("WARNING: Events panel not initialized!")
    
    def setup_object_ui(self):
        """Setup object editor specific UI"""
        # Clear the base content widget and rebuild
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # IMPORTANT: Ensure base toolbar actions exist first
        if not hasattr(self, 'save_action') or not self.save_action:
            print("Warning: Save action not found in base toolbar")
            self.ensure_save_button_visible()
        
        # Add object-specific toolbar actions AFTER ensuring save exists
        self.add_object_toolbar_actions()
        
        # Force toolbar to be visible
        self.toolbar.setVisible(True)
        self.toolbar.show()

        # Ensure save button is properly configured and visible
        self.ensure_save_button_visible()
        
        # Create main splitter (2-panel layout)
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Create left panel
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Create center panel
        center_panel = self.create_center_panel()
        main_splitter.addWidget(center_panel)
        
        # Set splitter sizes - left panel MUCH wider by default
        main_splitter.setSizes([500, 600])
        
        # Make BOTH panels resizable and stretchable
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)

        # Make splitter handle more visible and adjustable
        main_splitter.setHandleWidth(4)
        main_splitter.setChildrenCollapsible(False)

        # Add splitter to content layout
        content_layout.addWidget(main_splitter)
        
        print("Object UI setup complete")
        
        # CRITICAL FIX: Force toolbar visible at the END of setup
        if hasattr(self, 'toolbar'):
            self.toolbar.setVisible(True)
            self.toolbar.show()
            self.toolbar.update()

    def ensure_save_button_visible(self):
        """Ensure the save button is visible and functional"""
        # Check if toolbar exists
        if not hasattr(self, 'toolbar') or not self.toolbar:
            print("ERROR: No toolbar found, cannot add save button")
            return
        
        # Check if save_action exists from BaseEditor
        if hasattr(self, 'save_action') and self.save_action:
            print(f"Save action exists: {self.save_action.text()}")
            
            # Ensure it's in the toolbar
            toolbar_actions = self.toolbar.actions()
            if self.save_action not in toolbar_actions:
                print("Save action exists but not in toolbar, adding it")
                
                # Insert at the beginning of toolbar
                if toolbar_actions:
                    self.toolbar.insertAction(toolbar_actions[0], self.save_action)
                    save_index = self.toolbar.actions().index(self.save_action)
                    if save_index < len(self.toolbar.actions()) - 1:
                        self.toolbar.insertSeparator(self.toolbar.actions()[save_index + 1])
                else:
                    self.toolbar.addAction(self.save_action)
                    self.toolbar.addSeparator()
        else:
            print("Creating new save action")
            
            from PySide6.QtGui import QAction, QKeySequence
            
            # ✅ TRANSLATABLE: Save button text
            self.save_action = QAction(self.tr("💾 Save"), self)
            self.save_action.setShortcut(QKeySequence.Save)
            self.save_action.setToolTip(self.tr("Save object (Ctrl+S)"))
            
            existing_actions = self.toolbar.actions()
            
            if existing_actions:
                self.toolbar.insertAction(existing_actions[0], self.save_action)
                self.toolbar.insertSeparator(existing_actions[0])
            else:
                self.toolbar.addAction(self.save_action)
                self.toolbar.addSeparator()
            
            self.save_action.triggered.connect(self.save)
            print("Created and connected save action")
        
        # Ensure action is properly connected
        try:
            self.save_action.triggered.disconnect()
        except (RuntimeError, TypeError):
            pass
        
        self.save_action.triggered.connect(self.save)
        
        # Enable/disable based on asset state
        if self.asset_name:
            self.save_action.setEnabled(True)
            print(f"Save action enabled for asset: {self.asset_name}")
        else:
            self.save_action.setEnabled(False)
            print("Save action disabled - no asset loaded")
        
        self.toolbar.setVisible(True)
        self.toolbar.show()
        
        # Create keyboard shortcut as additional backup
        if not hasattr(self, '_save_shortcut'):
            from PySide6.QtGui import QShortcut, QKeySequence
            self._save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
            self._save_shortcut.activated.connect(self.save)
            print("Added keyboard shortcut backup for save")
    
    def add_object_toolbar_actions(self):
        """Add object-specific actions to toolbar"""
        self.toolbar.addSeparator()
        
        # ✅ TRANSLATABLE: Toolbar actions
        self.toolbar.addAction(self.tr("🎮 Test Object"), self.test_object)
        self.toolbar.addAction(self.tr("📋 View Code"), self.view_generated_code)
    
    def create_left_panel(self) -> QWidget:
        """Create left panel with events"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        
        # ✅ TRANSLATABLE: Group box title
        events_group = QGroupBox(self.tr("Object Events"))
        events_layout = QVBoxLayout(events_group)
        events_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create the events panel
        self.events_panel = ObjectEventsPanel()
        self.events_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        events_layout.addWidget(self.events_panel)
        
        layout.addWidget(events_group, 1)
        
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(10000)
        panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        print("Left panel created with events_panel")
        
        return panel
    
    def create_center_panel(self) -> QWidget:
        """Create center panel with properties and tabs"""
        print("DEBUG: Creating center panel...")
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Use the new ObjectPropertiesPanel
        self.properties_panel = ObjectPropertiesPanel()
        self.properties_panel.property_changed.connect(self.on_property_changed)
        layout.addWidget(self.properties_panel)
        
        # Keep references for compatibility
        self.visible_checkbox = self.properties_panel.visible_checkbox
        self.persistent_checkbox = self.properties_panel.persistent_checkbox
        self.solid_checkbox = self.properties_panel.solid_checkbox
        
        print("DEBUG: Creating info bar...")
        # Info bar - extremely compact
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(3, 1, 3, 1)
        info_layout.setSpacing(10)
        
        # ✅ TRANSLATABLE: Info labels
        self.object_info_label = QLabel(self.tr("Object: Not loaded"))
        self.object_info_label.setFixedHeight(18)
        self.object_info_label.setStyleSheet("font-size: 9px; padding: 0px;")
        
        self.event_info_label = QLabel(self.tr("No event selected"))
        self.event_info_label.setFixedHeight(18)
        self.event_info_label.setStyleSheet("font-size: 9px; padding: 0px;")
        
        info_layout.addWidget(self.object_info_label)
        info_layout.addStretch()
        info_layout.addWidget(self.event_info_label)
        
        layout.addLayout(info_layout, 0)
        
        print("DEBUG: Creating tab widget...")
        # Create tab widget for different views
        self.center_tabs = QTabWidget()
        
        print("DEBUG: Creating traditional tab...")
        # Tab 1: Traditional Event List
        traditional_tab = QWidget()
        traditional_layout = QVBoxLayout(traditional_tab)
        traditional_layout.setContentsMargins(10, 10, 10, 10)
        
        # ✅ TRANSLATABLE: Placeholder text
        placeholder_label = QLabel(
            self.tr("Actions are managed through the Object Events panel on the left.\n\n"
                   "Select an event and right-click to add actions.")
        )
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("color: #666; font-size: 12px;")
        traditional_layout.addWidget(placeholder_label)
        
        # Keep references for compatibility but hide them
        self.actions_widget = ActionListWidget()
        self.actions_widget.hide()
        self.scripting_area = VisualScriptingArea()
        self.scripting_area.hide()
        
        print("DEBUG: Adding traditional tab to center_tabs...")
        # ✅ TRANSLATABLE: Tab titles
        self.center_tabs.addTab(traditional_tab, self.tr("📋 Event List"))
        
        print("DEBUG: Creating visual programming tab...")
        # Tab 2: Visual Programming (DISABLED)
        try:
            visual_tab = self.create_visual_programming_tab()
            visual_tab_index = self.center_tabs.addTab(visual_tab, self.tr("🎨 Visual Programming"))
            self.center_tabs.setTabEnabled(visual_tab_index, False)
            self.center_tabs.setTabToolTip(visual_tab_index, self.tr("Visual Programming - Coming Soon"))
            print("DEBUG: Visual programming tab created successfully")
        except Exception as e:
            print(f"ERROR creating visual programming tab: {e}")
            import traceback
            traceback.print_exc()

        print("DEBUG: Creating code editor tab...")
        # Tab 3: Code tab (DISABLED)
        try:
            from PySide6.QtWidgets import QTextEdit
            self.code_editor = QTextEdit()
            # ✅ TRANSLATABLE: Placeholder text
            self.code_editor.setPlaceholderText(
                self.tr("// Custom GML code will go here\n// This feature will be added later")
            )
            self.code_editor.setReadOnly(True)
            code_tab_index = self.center_tabs.addTab(self.code_editor, self.tr("💻 Code Editor"))
            self.center_tabs.setTabEnabled(code_tab_index, False)
            self.center_tabs.setTabToolTip(code_tab_index, self.tr("Code Editor - Coming Soon"))
            print("DEBUG: Code editor tab created successfully")
        except Exception as e:
            print(f"ERROR creating code editor tab: {e}")
            import traceback
            traceback.print_exc()

        print("DEBUG: Adding tabs to layout...")
        layout.addWidget(self.center_tabs, 100)
        
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        panel.setMinimumWidth(200)
        
        self.center_tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.center_tabs.setMinimumWidth(200)
        self.center_tabs.setMinimumHeight(400)
        
        print("DEBUG: Center panel created with all UI elements")

        return panel

    def create_visual_programming_tab(self) -> QWidget:
        """Create the visual programming tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Left: Node palette
        self.node_palette = NodePalette()
        self.node_palette.setMaximumWidth(250)
        self.node_palette.node_requested.connect(self.add_node_to_canvas)
        layout.addWidget(self.node_palette)
        
        # Center: Visual canvas
        self.visual_canvas = VisualCanvas()
        self.visual_canvas.node_selected.connect(self.on_visual_node_selected)
        self.visual_canvas.node_deselected.connect(self.on_visual_node_deselected)
        self.visual_canvas.nodes_modified.connect(self.on_visual_nodes_modified)
        layout.addWidget(self.visual_canvas)
        
        # Right: Node properties
        self.node_properties = NodePropertiesPanel()
        self.node_properties.setMaximumWidth(250)
        self.node_properties.property_changed.connect(self.on_node_property_changed)
        layout.addWidget(self.node_properties)
        
        return tab

    def add_node_to_canvas(self, type_id: str):
        """Add a node to the visual canvas"""
        node = create_node_from_type(type_id)
        if node:
            view_center = self.visual_canvas.mapToScene(
                self.visual_canvas.viewport().rect().center()
            )
            self.visual_canvas.add_node(node, view_center)
            print(f"Added node: {node.title}")

    def on_visual_node_selected(self, node):
        """Handle visual node selection"""
        self.node_properties.set_node(node)
        print(f"Selected node: {node.title}")

    def on_visual_node_deselected(self):
        """Handle visual node deselection"""
        self.node_properties.set_node(None)

    def on_visual_nodes_modified(self):
        """Handle visual nodes modification"""
        self.mark_modified()
        print("Visual nodes modified")

    def on_node_property_changed(self, node, property_name, value):
        """Handle node property change"""
        print(f"Node property changed: {property_name} = {value}")
        self.mark_modified()
        self.visual_canvas.update()
    
    def setup_object_connections(self):
        """Setup object editor specific connections"""
        # Connect events panel
        if hasattr(self, 'events_panel') and self.events_panel:
            try:
                if hasattr(self.events_panel, 'events_modified'):
                    self.events_panel.events_modified.connect(self.on_events_modified)
                if hasattr(self.events_panel, 'event_selected'):
                    self.events_panel.event_selected.connect(self.on_event_selected)
            except AttributeError as e:
                print(f"Note: Events panel signal not available: {e}")
        
        # Connect scripting area
        if hasattr(self, 'scripting_area') and self.scripting_area:
            try:
                if hasattr(self.scripting_area, 'script_modified'):
                    self.scripting_area.script_modified.connect(self.on_script_modified)
            except AttributeError as e:
                print(f"Note: Scripting area signal not available: {e}")

        # Ensure save functionality
        self.ensure_save_functionality()

    def ensure_save_functionality(self):
        """Ensure save button and functionality are available"""
        if hasattr(self, 'save_action'):
            if self.asset_name:
                self.save_action.setEnabled(True)
            
            actions = [action.text() for action in self.toolbar.actions()]
            if not any('Save' in action for action in actions):
                # ✅ TRANSLATABLE: Save action
                save_action = self.toolbar.insertAction(
                    self.toolbar.actions()[0] if self.toolbar.actions() else None,
                    self.tr("💾 Save")
                )
                save_action.triggered.connect(self.save)
                save_action.setShortcut("Ctrl+S")
                self.save_action = save_action
                
                self.toolbar.insertSeparator(self.toolbar.actions()[1] if len(self.toolbar.actions()) > 1 else None)
        else:
            # ✅ TRANSLATABLE: Save action
            self.save_action = self.toolbar.addAction(self.tr("💾 Save"), self.save)
            self.save_action.setShortcut("Ctrl+S")
            self.save_action.setEnabled(True)
            
            self.toolbar.removeAction(self.save_action)
            if self.toolbar.actions():
                self.toolbar.insertAction(self.toolbar.actions()[0], self.save_action)
            else:
                self.toolbar.addAction(self.save_action)
        
        if not hasattr(self, '_save_shortcut'):
            from PySide6.QtGui import QShortcut, QKeySequence
            self._save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
            self._save_shortcut.activated.connect(self.save)
    
    def save(self):
        """Manual save method for the object editor"""
        if not self.asset_name:
            print("Cannot save: No asset loaded")
            return False
        
        print(f"Manual save triggered for: {self.asset_name}")
        
        try:
            # Validate data first
            is_valid, error_msg = self.validate_data()
            if not is_valid:
                # ✅ TRANSLATABLE: Error dialog
                QMessageBox.warning(
                    self, 
                    self.tr("Validation Error"), 
                    self.tr("Cannot save: {0}").format(error_msg)
                )
                return False
            
            # Get current data (including events)
            data = self.get_data()
            
            # Debug output for events
            events_count = len(data.get('events', {}))
            print(f"Saving object with {events_count} events")
            if events_count > 0:
                for event_name in data['events'].keys():
                    print(f"  - Saving event: {event_name}")
            
            # Emit save request signal
            self.save_requested.emit(self.asset_name, data)
            
            # Update state
            self.is_modified = False
            self.save_action.setEnabled(False)
            
            # Stop auto-save timer
            if hasattr(self, '_save_timer'):
                self._save_timer.stop()
            
            # Update UI to show saved state
            # ✅ TRANSLATABLE: Status message
            self.update_status(self.tr("Saved: {0}").format(self.asset_name))
            self.update_window_title()
            
            print(f"Successfully saved object: {self.asset_name}")
            return True
            
        except Exception as e:
            error_msg = f"Error saving object: {e}"
            print(error_msg)
            # ✅ TRANSLATABLE: Error dialog
            QMessageBox.critical(
                self, 
                self.tr("Save Error"), 
                self.tr("Error saving object: {0}").format(e)
            )
            return False

    def load_asset(self, asset_name: str, asset_data: Dict[str, Any]):
        """Load object asset data"""
        print(f"Loading object asset: {asset_name}")
        
        # Call parent method
        super().load_asset(asset_name, asset_data)
        
        # Ensure save button is available and enabled after loading
        self.ensure_save_button_visible()
        
        # Enable save action since we now have an asset
        if hasattr(self, 'save_action') and self.save_action:
            self.save_action.setEnabled(True)
            print(f"Enabled save action for {asset_name}")
        
        print(f"Object asset loaded: {asset_name}")

    def load_project_assets_if_available(self):
        """Load project assets if project path is available"""
        if self.project_path:
            self.load_project_assets()
    
    def load_project_assets(self):
        """Load available sprites from project"""
        try:
            project_data = self.load_project_data()
            
            if project_data:
                assets = project_data.get('assets', {})
                
                # Load sprites for sprite assignment
                self.available_sprites = assets.get('sprites', {})
                
                # Update status
                sprite_count = len(self.available_sprites)
                # ✅ TRANSLATABLE: Status message
                self.update_status(self.tr("Loaded {0} sprites").format(sprite_count))
                            
        except Exception as e:
            print(f"Error loading project assets: {e}")
            # ✅ TRANSLATABLE: Error message
            self.update_status(self.tr("Error loading assets: {0}").format(e))
    
    def load_data(self, data: Dict[str, Any]):
        """Load object data into the editor"""
        try:
            # Store object properties
            self.current_object_properties = data.copy()
            
            # Store events data for later if UI not ready
            self._pending_events_data = data.get('events', {})
            
            # Load events data only if events_panel exists
            if hasattr(self, 'events_panel') and self.events_panel:
                events_data = data.get('events', {})
                
                if events_data:
                    print(f"Loading {len(events_data)} events for {self.asset_name}:")
                    for event_name, event_info in events_data.items():
                        if isinstance(event_info, dict):
                            actions_count = len(event_info.get('actions', []))
                            print(f"  - Event: {event_name} ({actions_count} actions)")
                
                self.events_panel.load_events_data(events_data)
            else:
                print("Note: Events panel not initialized yet, storing for later")
            
            # Load properties into properties panel
            if hasattr(self, 'properties_panel'):
                self.properties_panel.load_properties(data)
            
            # Load visual programming data
            visual_data = data.get('visual_programming', {})
            if visual_data and hasattr(self, 'visual_canvas'):
                self.load_visual_programming_data(visual_data)
            
            # Update display only if UI elements exist
            if hasattr(self, 'object_info_label'):
                self.update_object_info()
            
            # Emit signal for IDE properties panel
            if hasattr(self, 'object_editor_activated'):
                self.object_editor_activated.emit(self.asset_name, self.current_object_properties)
            
        except Exception as e:
            print(f"Warning during object data loading: {e}")
            self.current_object_properties = data.copy()
    
    def apply_pending_data(self):
        """Apply any pending data after UI is fully initialized"""
        if hasattr(self, '_pending_events_data') and self._pending_events_data:
            if hasattr(self, 'events_panel') and self.events_panel:
                print(f"Applying pending events data: {len(self._pending_events_data)} events")
                self.events_panel.load_events_data(self._pending_events_data)
                self._pending_events_data = None
        
        # Update object info if needed
        if hasattr(self, 'object_info_label') and self.asset_name:
            self.update_object_info()

    def get_data(self) -> Dict[str, Any]:
        """Get current object data"""
        # Collect events and scripts safely
        events_data = {}
        script_data = {}
        
        try:
            if hasattr(self, 'events_panel') and self.events_panel and hasattr(self.events_panel, 'get_events_data'):
                events_data = self.events_panel.get_events_data()
                print(f"✓ Got {len(events_data)} events from events panel")
        except Exception as e:
            print(f"Note: Could not get events data: {e}")
        
        try:
            if hasattr(self, 'scripting_area') and self.scripting_area and hasattr(self.scripting_area, 'get_script_data'):
                script_data = self.scripting_area.get_script_data()
        except Exception as e:
            print(f"Note: Could not get script data: {e}")
        
        # Merge script data into events data
        for event_name, actions in script_data.items():
            if event_name in events_data:
                events_data[event_name]['actions'] = actions
        
        # Get properties from properties panel
        properties = {}
        if hasattr(self, 'properties_panel'):
            properties = self.properties_panel.get_properties()
        
        # Get object properties from current stored properties
        object_data = {
            'name': self.asset_name or 'obj_object1',
            'sprite': self.current_object_properties.get('sprite', ''),
            'visible': properties.get('visible', self.current_object_properties.get('visible', True)),
            'solid': properties.get('solid', self.current_object_properties.get('solid', False)),
            'persistent': properties.get('persistent', self.current_object_properties.get('persistent', False)),
            'events': events_data,
            'asset_type': 'object',
            'imported': True
        }
        
        # Add visual programming data
        visual_data = self.get_visual_programming_data()
        if visual_data and visual_data.get('nodes'):
            object_data['visual_programming'] = visual_data
        
        return object_data
    
    def validate_data(self) -> tuple[bool, str]:
        """Validate current object data"""
        try:
            data = self.get_data()
            
            # Check required fields
            if not data.get('name'):
                # ✅ TRANSLATABLE: Validation error
                return False, self.tr("Object name is required")
            
            # Validate sprite reference if assigned
            sprite_name = data.get('sprite', '')
            if sprite_name and sprite_name not in self.available_sprites:
                # ✅ TRANSLATABLE: Validation error
                return False, self.tr("Referenced sprite '{0}' does not exist").format(sprite_name)
            
            # Validate events
            events = data.get('events', {})
            for event_name, event_data in events.items():
                if not isinstance(event_data, dict):
                    # ✅ TRANSLATABLE: Validation error
                    return False, self.tr("Event '{0}' has invalid data structure").format(event_name)
                
                actions = event_data.get('actions', [])
                if not isinstance(actions, list):
                    # ✅ TRANSLATABLE: Validation error
                    return False, self.tr("Event '{0}' has invalid actions data").format(event_name)
            
            return True, ""
            
        except Exception as e:
            # ✅ TRANSLATABLE: Validation error
            return False, self.tr("Validation error: {0}").format(e)
    
    def on_property_changed(self, property_name: str, value: bool):
        """Handle property checkbox changes"""
        print(f"Property changed: {property_name} = {value}")
        
        # Update current properties
        if not hasattr(self, 'current_object_properties'):
            self.current_object_properties = {}
        
        old_sprite = None
        if property_name == 'sprite':
            old_sprite = self.current_object_properties.get('sprite', '')
        
        self.current_object_properties[property_name] = value
        
        # Update display
        if hasattr(self, 'update_object_info'):
            self.update_object_info()
        
        # Notify sprite changes
        if property_name == 'sprite' and self.asset_name:
            self.notify_sprite_change(self.asset_name, old_sprite or '', value or '')
        
        # Mark as modified
        self.mark_modified()
    
    def update_object_property_from_ide(self, property_name: str, value):
        """Update object property from IDE properties panel"""
        # Check if value actually changed
        if hasattr(self, 'current_object_properties'):
            current_value = self.current_object_properties.get(property_name)
            if current_value == value:
                return
        
        # Add recursion prevention
        if hasattr(self, '_processing_update') and self._processing_update:
            return
        
        self._processing_update = True
        try:
            print(f"Object editor: {property_name} = {value}")
            
            old_sprite = None
            if property_name == 'sprite' and hasattr(self, 'current_object_properties'):
                old_sprite = self.current_object_properties.get('sprite', '')
            
            if not hasattr(self, 'current_object_properties'):
                self.current_object_properties = {}
            
            self.current_object_properties[property_name] = value
            
            if hasattr(self, 'update_object_info'):
                self.update_object_info()
            
            if property_name == 'sprite' and self.asset_name:
                self.notify_sprite_change(self.asset_name, old_sprite or '', value or '')
            
            self.is_modified = True
            if hasattr(self, 'save_action'):
                self.save_action.setEnabled(True)
            
            if hasattr(self, 'data_modified'):
                self.data_modified.emit(self.asset_name)
            
            if hasattr(self, 'update_window_title'):
                self.update_window_title()
            
            if self.auto_save_enabled:
                self.start_auto_save_timer()
                
        finally:
            self._processing_update = False

    def mark_modified(self):
        """Mark the object as modified and enable save button"""
        if hasattr(self, 'is_modified'):
            self.is_modified = True
        if hasattr(self, 'save_action'):
            self.save_action.setEnabled(True)
        if hasattr(self, 'data_modified'):
            self.data_modified.emit(self.asset_name)
        if hasattr(self, 'update_window_title'):
            self.update_window_title()

    def notify_sprite_change(self, object_name: str, old_sprite: str, new_sprite: str):
        """Notify IDE of sprite changes so room editors can update"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'refresh_object_sprites'):
                parent.refresh_object_sprites(object_name, old_sprite, new_sprite)
                break
            parent = parent.parent()

    def update_object_info(self):
        """Update object information display"""
        if self.asset_name:
            sprite_name = self.current_object_properties.get('sprite', 'None')
            visible = self.current_object_properties.get('visible', True)
            solid = self.current_object_properties.get('solid', False)
            persistent = self.current_object_properties.get('persistent', False)
            
            # ✅ TRANSLATABLE: Info text
            info_text = self.tr("Object: {0} | Sprite: {1}").format(self.asset_name, sprite_name)
            if visible:
                info_text += " | " + self.tr("Visible")
            if solid:
                info_text += " | " + self.tr("Solid")
            if persistent:
                info_text += " | " + self.tr("Persistent")
                
            self.object_info_label.setText(info_text)
    
    # Event handlers
    def on_event_selected(self, event_name: str):
        """Handle event selection"""
        self.scripting_area.set_current_event(event_name)
        # ✅ TRANSLATABLE: Event info
        self.event_info_label.setText(self.tr("Event: {0}").format(event_name))
        self.update_status(self.tr("Editing event: {0}").format(event_name))
    
    def on_events_modified(self):
        """Handle events modification"""
        self.data_modified.emit(self.asset_name)
    
    def on_script_modified(self):
        """Handle script modification"""
        self.data_modified.emit(self.asset_name)
    
    def on_action_selected(self, action_name: str, action_data: Dict):
        """Handle action selection"""
        category = action_data.get('category', 'Unknown')
        # ✅ TRANSLATABLE: Status message
        self.update_status(self.tr("Selected action: {0} ({1})").format(action_name, category))
    
    # Toolbar actions
    def test_object(self):
        """Test the object (placeholder)"""
        # ✅ TRANSLATABLE: Status message
        self.update_status(self.tr("Object testing not implemented yet"))
    
    def view_generated_code(self):
        """View generated GML code"""
        script_data = self.scripting_area.get_script_data()
        
        if not script_data:
            # ✅ TRANSLATABLE: Info dialog
            QMessageBox.information(
                self, 
                self.tr("No Code"), 
                self.tr("No events or actions have been added yet.")
            )
            return
        
        # Generate basic code representation
        code_text = f"// Generated code for {self.asset_name}\n\n"
        
        for event_name, actions in script_data.items():
            code_text += f"// Event: {event_name}\n"
            if actions:
                for action in actions:
                    code_text += f"    {action}();\n"
            else:
                code_text += "    // No actions\n"
            code_text += "\n"
        
        # Show in code editor tab
        self.code_editor.setText(code_text)
        self.center_tabs.setCurrentIndex(1)
        
        # ✅ TRANSLATABLE: Status message
        self.update_status(self.tr("Generated code view updated"))
    
    # Override base methods
    def on_project_assets_loaded(self, assets: Dict[str, Any]):
        """Called when project assets are loaded"""
        self.available_sprites = assets.get('sprites', {})
        sprite_count = len(self.available_sprites)
        # ✅ TRANSLATABLE: Status message
        self.update_status(self.tr("Assets loaded: {0} sprites").format(sprite_count))
    
    def debug_events_state(self):
        """Debug method to check events state"""
        print("\n=== EVENTS DEBUG INFO ===")
        print(f"Asset name: {self.asset_name}")
        print(f"Has events_panel: {hasattr(self, 'events_panel')}")
        
        if hasattr(self, 'events_panel') and self.events_panel:
            events_data = self.events_panel.get_events_data()
            print(f"Number of events: {len(events_data)}")
            for event_name, event_info in events_data.items():
                if isinstance(event_info, dict):
                    print(f"  - {event_name}: {len(event_info.get('actions', []))} actions")
        
        if hasattr(self, 'current_object_properties'):
            stored_events = self.current_object_properties.get('events', {})
            print(f"Stored events in properties: {len(stored_events)}")
        
        print("======================\n")

    def sync_visual_to_events(self):
        """Convert visual programming nodes to event/action data"""
        if not hasattr(self, 'visual_canvas'):
            return
        
        if not self.visual_canvas.nodes:
            print("No visual nodes to sync")
            return
        
        # Generate code from visual nodes
        generator = VisualCodeGenerator()
        generator.set_graph(self.visual_canvas.nodes, self.visual_canvas.connections)
        
        events_data = generator.generate()
        
        if events_data:
            if hasattr(self, 'events_panel') and self.events_panel:
                self.events_panel.load_events_data(events_data)
                print(f"Synced visual programming to events: {len(events_data)} events")
        else:
            print("No events generated from visual programming")

    def sync_events_to_visual(self):
        """Convert event/action data to visual programming nodes (future feature)"""
        print("Sync events to visual: Not implemented yet")

    def get_visual_programming_data(self) -> dict:
        """Get visual programming data for saving"""
        if hasattr(self, 'visual_canvas'):
            return self.visual_canvas.to_dict()
        return {}

    def load_visual_programming_data(self, data: dict):
        """Load visual programming data"""
        if hasattr(self, 'visual_canvas') and data:
            def node_factory(node_data):
                return create_node_from_type(node_data['node_id'])
            
            self.visual_canvas.from_dict(data, node_factory)
            print(f"Loaded visual programming: {len(data.get('nodes', []))} nodes")