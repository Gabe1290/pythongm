#!/usr/bin/env python3
"""
Conditional Action Editor - For if/else logic with nested actions
"""

from typing import Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QSpinBox, QGroupBox, QListWidget, QPushButton,
    QDialogButtonBox
)
from PySide6.QtCore import Qt

from events.action_types import get_action_type, get_actions_by_category
from events.action_editor import ActionConfigDialog


class ConditionalActionEditor(QDialog):
    """Editor for if/else conditional actions with nested action lists"""
    
    def __init__(self, current_params: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.current_params = current_params or {}
        self.then_actions = self.current_params.get("then_actions", []).copy()
        self.else_actions = self.current_params.get("else_actions", []).copy()
        
        self.setWindowTitle(self.tr("Configure If Condition"))
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.setup_ui()
        self.load_current_values()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Condition section
        condition_group = QGroupBox(self.tr("Condition"))
        condition_layout = QVBoxLayout()

        # Condition type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel(self.tr("Condition Type:")))
        self.condition_type = QComboBox()
        self.condition_type.addItems([
            self.tr("instance_count"),
            self.tr("variable_compare"),
            self.tr("position_check"),
            self.tr("collision_check"),
            self.tr("key_pressed"),
            self.tr("mouse_check"),
            self.tr("random_chance"),
            self.tr("expression")
        ])
        self.condition_type.currentTextChanged.connect(self.on_condition_type_changed)
        type_layout.addWidget(self.condition_type)
        type_layout.addStretch()
        condition_layout.addLayout(type_layout)
        
        # Stacked widget for different condition configurations
        from PySide6.QtWidgets import QStackedWidget
        self.condition_stack = QStackedWidget()
        
        # Instance count configuration
        instance_widget = self.create_instance_count_widget()
        self.condition_stack.addWidget(instance_widget)
        
        # Variable compare configuration
        variable_widget = self.create_variable_compare_widget()
        self.condition_stack.addWidget(variable_widget)
        
        # Position check configuration
        position_widget = self.create_position_check_widget()
        self.condition_stack.addWidget(position_widget)
        
        # Collision check configuration
        collision_widget = self.create_collision_check_widget()
        self.condition_stack.addWidget(collision_widget)
        
        # Key pressed configuration
        key_widget = self.create_key_pressed_widget()
        self.condition_stack.addWidget(key_widget)
        
        # Mouse check configuration
        mouse_widget = self.create_mouse_check_widget()
        self.condition_stack.addWidget(mouse_widget)
        
        # Random chance configuration
        random_widget = self.create_random_chance_widget()
        self.condition_stack.addWidget(random_widget)
        
        # Expression configuration
        expression_widget = self.create_expression_widget()
        self.condition_stack.addWidget(expression_widget)
        
        condition_layout.addWidget(self.condition_stack)
        condition_group.setLayout(condition_layout)
        layout.addWidget(condition_group)
        
        then_group = QGroupBox(self.tr("Then Do (if condition is TRUE)"))
        then_layout = QVBoxLayout()

        self.then_list = QListWidget()
        self.then_list.setMaximumHeight(150)
        self.then_list.itemDoubleClicked.connect(lambda: self.edit_action_in_list("then"))
        then_layout.addWidget(self.then_list)

        then_buttons = QHBoxLayout()
        self.add_then_btn = QPushButton(self.tr("+ Add Action"))
        self.add_then_btn.clicked.connect(lambda: self.add_action_to_list("then"))
        then_buttons.addWidget(self.add_then_btn)

        self.edit_then_btn = QPushButton(self.tr("Edit Action"))
        self.edit_then_btn.clicked.connect(lambda: self.edit_action_in_list("then"))
        then_buttons.addWidget(self.edit_then_btn)

        self.remove_then_btn = QPushButton(self.tr("- Remove"))
        self.remove_then_btn.clicked.connect(lambda: self.remove_action_from_list("then"))
        then_buttons.addWidget(self.remove_then_btn)
        then_buttons.addStretch()
        then_layout.addLayout(then_buttons)
        
        then_group.setLayout(then_layout)
        layout.addWidget(then_group)
        
        # Else Actions section
        else_group = QGroupBox(self.tr("Else Do (if condition is FALSE)"))
        else_layout = QVBoxLayout()

        self.else_list = QListWidget()
        self.else_list.setMaximumHeight(150)
        self.else_list.itemDoubleClicked.connect(lambda: self.edit_action_in_list("else"))
        else_layout.addWidget(self.else_list)

        else_buttons = QHBoxLayout()
        self.add_else_btn = QPushButton(self.tr("+ Add Action"))
        self.add_else_btn.clicked.connect(lambda: self.add_action_to_list("else"))
        else_buttons.addWidget(self.add_else_btn)

        self.edit_else_btn = QPushButton(self.tr("Edit Action"))
        self.edit_else_btn.clicked.connect(lambda: self.edit_action_in_list("else"))
        else_buttons.addWidget(self.edit_else_btn)

        self.remove_else_btn = QPushButton(self.tr("- Remove"))
        self.remove_else_btn.clicked.connect(lambda: self.remove_action_from_list("else"))
        else_buttons.addWidget(self.remove_else_btn)
        else_buttons.addStretch()
        else_layout.addLayout(else_buttons)
        
        else_group.setLayout(else_layout)
        layout.addWidget(else_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_instance_count_widget(self):
        """Create widget for instance count conditions"""
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Object name - now using a dropdown
        object_layout = QHBoxLayout()
        object_layout.addWidget(QLabel(self.tr("Object:")))
        self.object_name = QComboBox()  # Changed from QLineEdit to QComboBox
        self.object_name.setEditable(True)  # Allow typing custom names

        # Populate with available objects
        available_objects = self.get_available_objects_for_dropdown()
        if available_objects:
            self.object_name.addItems(available_objects)
        else:
            # Add defaults if no project data
            self.object_name.addItems(["obj_box", "obj_wall", "obj_player", "obj_enemy"])

        object_layout.addWidget(self.object_name)
        layout.addLayout(object_layout)

        # Operator and value
        compare_layout = QHBoxLayout()
        compare_layout.addWidget(QLabel(self.tr("Count is:")))
        self.operator = QComboBox()
        self.operator.addItems(["==", "!=", "<", ">", "<=", ">="])
        compare_layout.addWidget(self.operator)
        
        self.value = QSpinBox()
        self.value.setMinimum(0)
        self.value.setMaximum(999)
        compare_layout.addWidget(self.value)
        compare_layout.addStretch()
        layout.addLayout(compare_layout)
        
        return widget
 
    def create_variable_compare_widget(self):
        """Create widget for variable comparison"""
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Variable name
        var_layout = QHBoxLayout()
        var_layout.addWidget(QLabel(self.tr("Variable:")))
        self.var_name = QLineEdit()
        self.var_name.setPlaceholderText(self.tr("health, score, x, y, etc."))
        var_layout.addWidget(self.var_name)
        layout.addLayout(var_layout)

        # Comparison
        compare_layout = QHBoxLayout()
        compare_layout.addWidget(QLabel(self.tr("Is:")))
        self.var_operator = QComboBox()
        self.var_operator.addItems(["==", "!=", "<", ">", "<=", ">="])
        compare_layout.addWidget(self.var_operator)

        compare_layout.addWidget(QLabel(self.tr("Value:")))
        self.var_value = QLineEdit()
        self.var_value.setPlaceholderText("0")
        compare_layout.addWidget(self.var_value)
        compare_layout.addStretch()
        layout.addLayout(compare_layout)
        
        return widget

    def create_position_check_widget(self):
        """Create widget for position checking"""
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Position type
        pos_type_layout = QHBoxLayout()
        pos_type_layout.addWidget(QLabel(self.tr("Check if:")))
        self.pos_check_type = QComboBox()
        self.pos_check_type.addItems([
            self.tr("x position"),
            self.tr("y position"),
            self.tr("in region"),
            self.tr("distance to object")
        ])
        pos_type_layout.addWidget(self.pos_check_type)
        pos_type_layout.addStretch()
        layout.addLayout(pos_type_layout)

        # Position values
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel(self.tr("Is:")))
        self.pos_operator = QComboBox()
        self.pos_operator.addItems(["==", "!=", "<", ">", "<=", ">="])
        pos_layout.addWidget(self.pos_operator)
        
        self.pos_value = QSpinBox()
        self.pos_value.setMinimum(-9999)
        self.pos_value.setMaximum(9999)
        pos_layout.addWidget(self.pos_value)
        pos_layout.addStretch()
        layout.addLayout(pos_layout)
        
        return widget

    def create_collision_check_widget(self):
        """Create widget for collision checking"""
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Collision target
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel(self.tr("Colliding with:")))
        self.collision_object = QComboBox()
        self.collision_object.setEditable(True)
        self.collision_object.addItems(["obj_wall", "obj_enemy", "obj_goal"])
        col_layout.addWidget(self.collision_object)
        layout.addLayout(col_layout)

        # Collision position
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(QLabel(self.tr("At offset X:")))
        self.collision_x = QSpinBox()
        self.collision_x.setMinimum(-100)
        self.collision_x.setMaximum(100)
        self.collision_x.setValue(0)
        offset_layout.addWidget(self.collision_x)

        offset_layout.addWidget(QLabel(self.tr("Y:")))
        self.collision_y = QSpinBox()
        self.collision_y.setMinimum(-100)
        self.collision_y.setMaximum(100)
        self.collision_y.setValue(0)
        offset_layout.addWidget(self.collision_y)
        offset_layout.addStretch()
        layout.addLayout(offset_layout)
        
        return widget

    def create_key_pressed_widget(self):
        """Create widget for key press checking"""
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel(self.tr("Key:")))
        self.key_check = QComboBox()
        self.key_check.addItems([
            self.tr("Space"), self.tr("Enter"), self.tr("Escape"),
            self.tr("Left Arrow"), self.tr("Right Arrow"), self.tr("Up Arrow"), self.tr("Down Arrow"),
            "A", "W", "S", "D",
            self.tr("Shift"), self.tr("Control"), self.tr("Alt")
        ])
        key_layout.addWidget(self.key_check)

        key_layout.addWidget(QLabel(self.tr("Is:")))
        self.key_state = QComboBox()
        self.key_state.addItems([self.tr("Pressed"), self.tr("Held"), self.tr("Released")])
        key_layout.addWidget(self.key_state)
        key_layout.addStretch()
        layout.addLayout(key_layout)
        
        return widget

    def create_mouse_check_widget(self):
        """Create widget for mouse checking"""
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        mouse_layout = QHBoxLayout()
        mouse_layout.addWidget(QLabel(self.tr("Mouse:")))
        self.mouse_check = QComboBox()
        self.mouse_check.addItems([
            self.tr("Left button pressed"),
            self.tr("Right button pressed"),
            self.tr("Middle button pressed"),
            self.tr("Over object"),
            self.tr("In region")
        ])
        mouse_layout.addWidget(self.mouse_check)
        mouse_layout.addStretch()
        layout.addLayout(mouse_layout)
        
        return widget

    def create_random_chance_widget(self):
        """Create widget for random chance"""
        from PySide6.QtWidgets import QWidget, QSlider
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        chance_layout = QHBoxLayout()
        chance_layout.addWidget(QLabel(self.tr("Chance:")))

        self.chance_slider = QSlider(Qt.Horizontal)
        self.chance_slider.setMinimum(0)
        self.chance_slider.setMaximum(100)
        self.chance_slider.setValue(50)
        self.chance_slider.setTickPosition(QSlider.TicksBelow)
        self.chance_slider.setTickInterval(10)
        chance_layout.addWidget(self.chance_slider)

        self.chance_label = QLabel("50%")
        self.chance_slider.valueChanged.connect(
            lambda v: self.chance_label.setText(f"{v}%")
        )
        chance_layout.addWidget(self.chance_label)
        chance_layout.addStretch()
        layout.addLayout(chance_layout)
        
        return widget

    def create_expression_widget(self):
        """Create widget for custom expressions"""
        from PySide6.QtWidgets import QWidget, QTextEdit
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel(self.tr("Custom GML Expression:")))
        self.expression_edit = QTextEdit()
        self.expression_edit.setMaximumHeight(100)
        self.expression_edit.setPlaceholderText(
            self.tr("Enter any GML expression that evaluates to true/false\nExample: x > 100 && y < 200")
        )
        layout.addWidget(self.expression_edit)
        
        return widget

    def on_condition_type_changed(self, condition_type: str):
        """Handle condition type changes"""
        index_map = {
            "instance_count": 0,
            "variable_compare": 1,
            "position_check": 2,
            "collision_check": 3,
            "key_pressed": 4,
            "mouse_check": 5,
            "random_chance": 6,
            "expression": 7
        }
        
        index = index_map.get(condition_type, 0)
        self.condition_stack.setCurrentIndex(index)
    
    def get_available_objects_for_dropdown(self):
        """Get list of available objects from the project"""
        # Walk up parent hierarchy to find project data
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

    def load_current_values(self):
        """Load current parameter values into the UI"""
        self.condition_type.setCurrentText(
            self.current_params.get("condition_type", "instance_count")
        )
        
        # Handle object_name - now it's a QComboBox
        object_name = self.current_params.get("object_name", "obj_box")
        if hasattr(self, 'object_name'):
            if isinstance(self.object_name, QComboBox):
                self.object_name.setCurrentText(object_name)
            else:
                self.object_name.setText(object_name)
        
        self.operator.setCurrentText(
            self.current_params.get("operator", "==")
        )
        self.value.setValue(
            self.current_params.get("value", 0)
        )
        
        self.refresh_action_lists()
    
    def refresh_action_lists(self):
        """Refresh both action list displays"""
        # Then actions
        self.then_list.clear()
        for action_data in self.then_actions:
            action_type = get_action_type(action_data["action"])
            if action_type:
                display_text = f"{action_type.icon} {action_type.display_name}"
                params = action_data.get("parameters", {})
                if params:
                    param_summary = ", ".join([f"{k}={v}" for k, v in params.items() if k not in ["then_actions", "else_actions"]])
                    if param_summary:
                        display_text += f" ({param_summary[:40]}...)" if len(param_summary) > 40 else f" ({param_summary})"
                self.then_list.addItem(display_text)
        
        # Else actions
        self.else_list.clear()
        for action_data in self.else_actions:
            action_type = get_action_type(action_data["action"])
            if action_type:
                display_text = f"{action_type.icon} {action_type.display_name}"
                params = action_data.get("parameters", {})
                if params:
                    param_summary = ", ".join([f"{k}={v}" for k, v in params.items() if k not in ["then_actions", "else_actions"]])
                    if param_summary:
                        display_text += f" ({param_summary[:40]}...)" if len(param_summary) > 40 else f" ({param_summary})"
                self.else_list.addItem(display_text)
    
    def add_action_to_list(self, list_type: str):
        """Show menu to add an action to then or else list"""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        actions_by_category = get_actions_by_category()
        
        for category, actions in actions_by_category.items():
            category_menu = menu.addMenu(category)
            
            for action_type in actions:
                action_item = category_menu.addAction(f"{action_type.icon} {action_type.display_name}")
                action_item.triggered.connect(
                    lambda checked, at=action_type, lt=list_type: self.configure_and_add_action(at, lt)
                )
        
        if list_type == "then":
            menu.exec(self.add_then_btn.mapToGlobal(self.add_then_btn.rect().bottomLeft()))
        else:
            menu.exec(self.add_else_btn.mapToGlobal(self.add_else_btn.rect().bottomLeft()))
    
    def configure_and_add_action(self, action_type, list_type: str):
        """Configure and add an action to the specified list"""
        # Special handling for nested conditionals
        if action_type.name == "if_condition":
            dialog = ConditionalActionEditor(parent=self)
        else:
            dialog = ActionConfigDialog(action_type, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            action_data = {
                "action": action_type.name,
                "parameters": dialog.get_parameter_values()
            }
            
            if list_type == "then":
                self.then_actions.append(action_data)
            else:
                self.else_actions.append(action_data)
            
            self.refresh_action_lists()
    
    def edit_action_in_list(self, list_type: str):
        """Edit the selected action in the specified list"""
        if list_type == "then":
            current_row = self.then_list.currentRow()
            if current_row < 0 or current_row >= len(self.then_actions):
                return
            action_data = self.then_actions[current_row]
        else:
            current_row = self.else_list.currentRow()
            if current_row < 0 or current_row >= len(self.else_actions):
                return
            action_data = self.else_actions[current_row]
        
        action_type = get_action_type(action_data["action"])
        if not action_type:
            return
        
        # Special handling for nested conditionals
        if action_type.name == "if_condition":
            dialog = ConditionalActionEditor(action_data.get("parameters", {}), parent=self)
        else:
            dialog = ActionConfigDialog(action_type, action_data.get("parameters", {}), parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            action_data["parameters"] = dialog.get_parameter_values()
            self.refresh_action_lists()
    
    def remove_action_from_list(self, list_type: str):
        """Remove the selected action from the specified list"""
        if list_type == "then":
            current_row = self.then_list.currentRow()
            if current_row >= 0 and current_row < len(self.then_actions):
                self.then_actions.pop(current_row)
        else:
            current_row = self.else_list.currentRow()
            if current_row >= 0 and current_row < len(self.else_actions):
                self.else_actions.pop(current_row)
        
        self.refresh_action_lists()
    
    def get_parameter_values(self) -> Dict[str, Any]:
        """Get all configured parameter values"""
        condition_type = self.condition_type.currentText()
        
        params = {
            "condition_type": condition_type,
            "then_actions": self.then_actions.copy(),
            "else_actions": self.else_actions.copy()
        }
        
        # Add parameters based on condition type
        if condition_type == "instance_count":
            params.update({
                "object_name": self.object_name.currentText() if isinstance(self.object_name, QComboBox) else self.object_name.text(),
                "operator": self.operator.currentText(),
                "value": self.value.value()
            })
        elif condition_type == "variable_compare":
            params.update({
                "variable": self.var_name.text(),
                "operator": self.var_operator.currentText(),
                "value": self.var_value.text()
            })
        elif condition_type == "position_check":
            params.update({
                "check_type": self.pos_check_type.currentText(),
                "operator": self.pos_operator.currentText(),
                "value": self.pos_value.value()
            })
        elif condition_type == "collision_check":
            params.update({
                "object": self.collision_object.currentText(),
                "offset_x": self.collision_x.value(),
                "offset_y": self.collision_y.value()
            })
        elif condition_type == "key_pressed":
            params.update({
                "key": self.key_check.currentText(),
                "state": self.key_state.currentText()
            })
        elif condition_type == "mouse_check":
            params.update({
                "check": self.mouse_check.currentText()
            })
        elif condition_type == "random_chance":
            params.update({
                "chance": self.chance_slider.value()
            })
        elif condition_type == "expression":
            params.update({
                "expression": self.expression_edit.toPlainText()
            })
        
        return params