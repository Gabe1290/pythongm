#!/usr/bin/env python3
"""
Action editor dialogs for configuring action parameters
"""

from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidgetItem, QTreeWidget, QMenu,
    QLabel, QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QDialogButtonBox, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .action_types import ActionType, ActionParameter

class ActionConfigDialog(QDialog):
    """Dialog for configuring action parameters"""
    
    def __init__(self, action_type: ActionType, initial_params: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.action_type = action_type
        self.current_params = initial_params or {}
        
        # Check if this is a conditional action
        self.is_conditional = action_type.name == "if_condition"
        self.param_widgets = {}
        
        # Store nested action parameters
        self.nested_action_params = {
            'then_action_params': self.current_params.get('then_action_params', {}),
            'else_action_params': self.current_params.get('else_action_params', {})
        }
        
        self.setWindowTitle(f"Configure {action_type.display_name}")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Special handling for conditional actions
        if self.is_conditional:
            layout = QVBoxLayout(self)
            label = QLabel("This action requires special configuration.")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(self.accept)
            layout.addWidget(button_box)
            return
        
        # Regular action configuration
        layout = QVBoxLayout(self)
        
        # Action info
        title_label = QLabel(f"{self.action_type.icon} {self.action_type.display_name}")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        if self.action_type.description:
            desc_label = QLabel(self.action_type.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Parameters
        self.param_widgets = {}
        
        for param in self.action_type.parameters:
            param_layout = QHBoxLayout()
            
            label = QLabel(f"{param.display_name}:")
            label.setMinimumWidth(120)
            param_layout.addWidget(label)
            
            # Special handling for object_type (includes "any" option)
            if param.name == "object_type":
                widget = QComboBox()
                widget.setEditable(True)
                
                # Add "any" first
                widget.addItem("any")
                widget.addItem("solid")
                
                # Then add available objects
                available_objects = self.get_available_objects()
                if available_objects:
                    widget.addItems(available_objects)
                else:
                    widget.addItems(["obj_box", "obj_wall", "obj_player", "obj_enemy"])
                
                if param.name in self.current_params:
                    widget.setCurrentText(str(self.current_params[param.name]))
                else:
                    widget.setCurrentText(str(param.default_value))
            
            # Special handling for object selection parameters (object_name)
            elif param.name == "object_name" or "object" in param.name.lower():
                widget = QComboBox()
                widget.setEditable(True)
                
                available_objects = self.get_available_objects()
                if available_objects:
                    widget.addItems(available_objects)
                else:
                    widget.addItems(["obj_box", "obj_wall", "obj_player", "obj_enemy"])
                
                if param.name in self.current_params:
                    widget.setCurrentText(str(self.current_params[param.name]))
                else:
                    widget.setCurrentText(str(param.default_value))
            
            # Special handling for room selection parameters
            elif param.name == "room_name" or "room" in param.name.lower():
                widget = QComboBox()
                widget.setEditable(True)
                
                available_rooms = self.get_available_rooms()
                
                for room in available_rooms:
                    if room == "---":
                        widget.insertSeparator(widget.count())
                    else:
                        widget.addItem(room)
                
                if param.name in self.current_params:
                    current_value = str(self.current_params[param.name])
                    if current_value == "__next__":
                        widget.setCurrentText("→ Next Room")
                    elif current_value == "__prev__":
                        widget.setCurrentText("← Previous Room")
                    elif current_value == "__current__":
                        widget.setCurrentText("↺ Restart Current Room")
                    else:
                        widget.setCurrentText(current_value)
                else:
                    widget.setCurrentText(str(param.default_value))
            
            # Special handling for then_action and else_action - add configure button
            elif param.name in ["then_action", "else_action"]:
                widget = QComboBox()
                if param.choices:
                    widget.addItems(param.choices)
                if param.name in self.current_params:
                    widget.setCurrentText(str(self.current_params[param.name]))
                else:
                    widget.setCurrentText(str(param.default_value))
                
                param_layout.addWidget(widget)
                
                # Add "Configure..." button
                config_btn = QPushButton("⚙️ Configure...")
                config_btn.setMaximumWidth(120)
                config_btn.clicked.connect(
                    lambda checked, p=param.name, w=widget: self.configure_nested_action(p, w.currentText())
                )
                param_layout.addWidget(config_btn)
                
                self.param_widgets[param.name] = widget
                layout.addLayout(param_layout)
                continue

            # Create appropriate widget based on parameter type
            elif param.param_type == "string":
                widget = QLineEdit()
                widget.setPlaceholderText(str(param.default_value))
                if param.name in self.current_params:
                    widget.setText(str(self.current_params[param.name]))
                else:
                    widget.setText(str(param.default_value))
            
            elif param.param_type == "number":
                widget = QSpinBox()
                widget.setMinimum(-9999)
                widget.setMaximum(9999)
                if param.name in self.current_params:
                    widget.setValue(int(self.current_params[param.name]))
                else:
                    widget.setValue(int(param.default_value))
            
            elif param.param_type == "choice":
                widget = QComboBox()
                if param.choices:
                    widget.addItems(param.choices)
                if param.name in self.current_params:
                    widget.setCurrentText(str(self.current_params[param.name]))
                else:
                    widget.setCurrentText(str(param.default_value))
            
            elif param.param_type == "boolean":
                widget = QCheckBox()
                if param.name in self.current_params:
                    widget.setChecked(bool(self.current_params[param.name]))
                else:
                    widget.setChecked(bool(param.default_value))
            
            # Special handling for action_list parameters (then_actions, else_actions)
            elif param.param_type == "action_list":
                widget = QPushButton("📋 Configure Actions...")
                widget.clicked.connect(
                    lambda checked, p=param.name: self.configure_action_list(p)
                )
                
                param_layout.addWidget(widget)
                
                # Store the action list data
                if param.name not in self.nested_action_params:
                    self.nested_action_params[param.name] = self.current_params.get(param.name, [])
                
                layout.addLayout(param_layout)
                continue

            else:
                widget = QLineEdit()
                widget.setPlaceholderText(str(param.default_value))
                if param.name in self.current_params:
                    widget.setText(str(self.current_params[param.name]))
            
            param_layout.addWidget(widget)
            self.param_widgets[param.name] = widget
            
            layout.addLayout(param_layout)
        
        layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def configure_nested_action(self, param_name: str, action_name: str):
        """Open configuration dialog for nested action"""
        from events.action_types import get_action_type
        
        if not action_name or action_name == "":
            return
        
        # Get the action type
        action_type = get_action_type(action_name)
        if not action_type:
            return
        
        # Get existing parameters if any
        param_key = f"{param_name}_params"
        existing_params = self.nested_action_params.get(param_key, {})
        
        # Open the action's configuration dialog
        dialog = ActionConfigDialog(action_type, existing_params, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            # Store the configured parameters
            self.nested_action_params[param_key] = dialog.get_parameter_values()
            print(f"✅ Configured {action_name}: {self.nested_action_params[param_key]}")

    def get_available_objects(self):
        """Get list of available objects from the project"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_data'):
                project_data = parent.current_project_data
                if project_data and 'assets' in project_data:
                    objects = project_data['assets'].get('objects', {})
                    return list(objects.keys())
                break
            parent = parent.parent()
        
        return []

    def get_available_rooms(self):
        """Get list of available rooms from the project, including navigation options"""
        room_list = []
        
        # Add special navigation options first
        room_list.extend([
            "→ Next Room",
            "← Previous Room", 
            "↺ Restart Current Room",
            "---"
        ])
        
        # Walk up parent hierarchy to find project data
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_data'):
                project_data = parent.current_project_data
                if project_data and 'assets' in project_data:
                    rooms = project_data['assets'].get('rooms', {})
                    room_list.extend(list(rooms.keys()))
                    break
            parent = parent.parent()
        
        # If no rooms found, add some defaults
        if len(room_list) == 4:
            room_list.extend(["Room01", "Room02", "Room03"])
        
        return room_list
    
    def get_parameter_values(self) -> Dict[str, Any]:
        """Get configured parameter values including nested action parameters"""
        if self.is_conditional:
            return getattr(self, 'conditional_params', {})
        
        # Get current parameter values from widgets
        values = {}
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QLineEdit):
                values[param_name] = widget.text()
            elif isinstance(widget, QSpinBox):
                values[param_name] = widget.value()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
                
                # Map navigation options
                if param_name == "room_name" or "room" in param_name.lower():
                    if value == "→ Next Room":
                        value = "__next__"
                    elif value == "← Previous Room":
                        value = "__prev__"
                    elif value == "↺ Restart Current Room":
                        value = "__current__"
                
                values[param_name] = value
            elif isinstance(widget, QCheckBox):
                values[param_name] = widget.isChecked()
        
        # ADD NESTED ACTION PARAMETERS
        for key, params in self.nested_action_params.items():
            if params:  # Only add if there are parameters
                values[key] = params
                print(f"   Adding nested param: {key} = {params}")  # ← ADD DEBUG
        
        print(f"DEBUG: Final values being returned: {values}")  # ← ADD DEBUG
        return values
    
    def configure_action_list(self, param_name: str):
        """Open multi-action editor for action lists"""
        # Get existing action list
        action_list = self.nested_action_params.get(param_name, [])
        
        # Make a copy to avoid direct mutation
        action_list_copy = action_list.copy() if action_list else []
        
        # Open multi-action editor
        dialog = MultiActionEditor(action_list_copy, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            # Store the configured action list
            self.nested_action_params[param_name] = dialog.get_action_list()
            print(f"✅ Configured {len(self.nested_action_params[param_name])} actions for {param_name}")
            print(f"   Actions: {self.nested_action_params[param_name]}")  # ← ADD DEBUG
    
class MultiActionEditor(QDialog):
    """Dialog for editing a list of actions (for Then/Else branches)"""
    
    def __init__(self, action_list: List[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.action_list = action_list or []
        
        self.setWindowTitle("Configure Actions")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Action Sequence")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Action list
        self.action_tree = QTreeWidget()
        self.action_tree.setHeaderLabels(["Action", "Parameters"])
        self.action_tree.itemDoubleClicked.connect(self.edit_action)
        layout.addWidget(self.action_tree)
        
        # Buttons for managing actions
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Action")
        add_btn.clicked.connect(self.add_action)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edit Action")
        edit_btn.clicked.connect(lambda: self.edit_action(self.action_tree.currentItem(), 0))
        button_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("➖ Remove Action")
        remove_btn.clicked.connect(self.remove_action)
        button_layout.addWidget(remove_btn)
        
        move_up_btn = QPushButton("⬆️ Move Up")
        move_up_btn.clicked.connect(self.move_up)
        button_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("⬇️ Move Down")
        move_down_btn.clicked.connect(self.move_down)
        button_layout.addWidget(move_down_btn)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Load existing actions
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the action list display"""
        from events.action_types import get_action_type
        
        self.action_tree.clear()
        
        for action_data in self.action_list:
            action_name = action_data.get("action", "")
            action_type = get_action_type(action_name)
            
            if action_type:
                item = QTreeWidgetItem()
                item.setText(0, f"{action_type.icon} {action_type.display_name}")
                
                # Show parameter summary
                params = action_data.get("parameters", {})
                if params:
                    param_summary = ", ".join([f"{k}={v}" for k, v in params.items()])
                    item.setText(1, param_summary[:50] + ("..." if len(param_summary) > 50 else ""))
                
                item.setData(0, Qt.ItemDataRole.UserRole, action_data)
                self.action_tree.addTopLevelItem(item)
    
    def add_action(self):
        """Show menu to add a new action"""
        from events.action_types import get_actions_by_category
        
        menu = QMenu(self)
        
        actions_by_category = get_actions_by_category()
        for category, actions in actions_by_category.items():
            category_menu = menu.addMenu(category)
            
            for action_type in actions:
                action_item = category_menu.addAction(f"{action_type.icon} {action_type.display_name}")
                action_item.triggered.connect(
                    lambda checked, at=action_type: self.configure_and_add_action(at)
                )
        
        menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
    
    def configure_and_add_action(self, action_type):
        """Configure and add a new action"""
        dialog = ActionConfigDialog(action_type, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            action_data = {
                "action": action_type.name,
                "parameters": dialog.get_parameter_values()
            }
            self.action_list.append(action_data)
            self.refresh_display()
    
    def edit_action(self, item, column):
        """Edit an existing action"""
        if not item:
            return
        
        from events.action_types import get_action_type
        
        action_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not action_data:
            return
        
        action_type = get_action_type(action_data["action"])
        if not action_type:
            return
        
        dialog = ActionConfigDialog(action_type, action_data.get("parameters", {}), parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            action_data["parameters"] = dialog.get_parameter_values()
            self.refresh_display()
    
    def remove_action(self):
        """Remove the selected action"""
        current_item = self.action_tree.currentItem()
        if not current_item:
            return
        
        index = self.action_tree.indexOfTopLevelItem(current_item)
        if 0 <= index < len(self.action_list):
            self.action_list.pop(index)
            self.refresh_display()
    
    def move_up(self):
        """Move selected action up"""
        current_item = self.action_tree.currentItem()
        if not current_item:
            return
        
        index = self.action_tree.indexOfTopLevelItem(current_item)
        if index > 0:
            self.action_list[index], self.action_list[index - 1] = self.action_list[index - 1], self.action_list[index]
            self.refresh_display()
            self.action_tree.setCurrentItem(self.action_tree.topLevelItem(index - 1))
    
    def move_down(self):
        """Move selected action down"""
        current_item = self.action_tree.currentItem()
        if not current_item:
            return
        
        index = self.action_tree.indexOfTopLevelItem(current_item)
        if index < len(self.action_list) - 1:
            self.action_list[index], self.action_list[index + 1] = self.action_list[index + 1], self.action_list[index]
            self.refresh_display()
            self.action_tree.setCurrentItem(self.action_tree.topLevelItem(index + 1))
    
    def get_action_list(self) -> List[Dict[str, Any]]:
        """Get the configured action list"""
        return self.action_list