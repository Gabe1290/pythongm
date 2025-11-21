#!/usr/bin/env python3
"""
GameMaker 8.0 Action Configuration Dialog
Provides parameter input for GM8.0 actions
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QComboBox, QTextEdit, QPushButton, QLabel,
    QDialogButtonBox, QGroupBox, QColorDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from actions.gm80_actions import ActionDefinition, ActionParameter


class GM80ActionDialog(QDialog):
    """Dialog for configuring GM8.0 action parameters"""

    def __init__(self, action_def: ActionDefinition,
                 current_params: Optional[Dict[str, Any]] = None,
                 parent=None):
        super().__init__(parent)
        self.action_def = action_def
        self.current_params = current_params or {}
        self.param_widgets = {}

        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(f"Configure: {self.action_def.display_name}")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        # Action title and description
        title_label = QLabel(f"{self.action_def.icon} {self.action_def.display_name}")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)

        if self.action_def.description:
            desc_label = QLabel(self.action_def.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: gray; padding: 5px;")
            layout.addWidget(desc_label)

        # Parameters
        if self.action_def.parameters:
            params_group = QGroupBox("Parameters")
            params_layout = QFormLayout()

            for param in self.action_def.parameters:
                widget = self.create_parameter_widget(param)
                if widget:
                    self.param_widgets[param.name] = widget
                    label = QLabel(param.display_name + ":")
                    if param.description:
                        label.setToolTip(param.description)
                    params_layout.addRow(label, widget)

            params_group.setLayout(params_layout)
            layout.addWidget(params_group)
        else:
            no_params_label = QLabel("This action has no parameters.")
            no_params_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_params_label)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def create_parameter_widget(self, param: ActionParameter):
        """Create appropriate widget for parameter type"""
        param_type = param.type
        default_value = self.current_params.get(param.name, param.default)

        if param_type == "boolean":
            widget = QCheckBox()
            widget.setChecked(bool(default_value if default_value is not None else False))
            return widget

        elif param_type == "int":
            widget = QSpinBox()
            widget.setRange(-99999, 99999)
            widget.setValue(int(default_value if default_value is not None else 0))
            return widget

        elif param_type == "float":
            widget = QDoubleSpinBox()
            widget.setRange(-99999.0, 99999.0)
            widget.setDecimals(2)
            widget.setValue(float(default_value if default_value is not None else 0.0))
            return widget

        elif param_type == "string":
            widget = QLineEdit()
            widget.setText(str(default_value if default_value is not None else ""))
            return widget

        elif param_type == "code":
            widget = QTextEdit()
            widget.setPlainText(str(default_value if default_value is not None else ""))
            widget.setMinimumHeight(100)
            widget.setFont(QFont("Courier New", 10))
            return widget

        elif param_type == "choice":
            widget = QComboBox()
            if param.options:
                widget.addItems([str(opt) for opt in param.options])
                if default_value is not None and default_value in param.options:
                    widget.setCurrentText(str(default_value))
            return widget

        elif param_type == "color":
            # Color picker button
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            color_edit = QLineEdit()
            color_edit.setText(str(default_value if default_value is not None else "#FFFFFF"))
            color_edit.setPlaceholderText("#RRGGBB")
            layout.addWidget(color_edit)

            pick_btn = QPushButton("Pick Color...")
            pick_btn.clicked.connect(lambda: self.pick_color(color_edit))
            layout.addWidget(pick_btn)

            container._color_edit = color_edit  # Store reference
            return container

        elif param_type in ["object", "sprite", "sound", "room", "background",
                           "font", "script", "timeline"]:
            # Resource selector dropdown
            widget = QComboBox()
            widget.setEditable(True)

            # Get available resources from project
            resources = self.get_available_resources(param_type)
            if resources:
                widget.addItems(resources)
                if default_value and default_value in resources:
                    widget.setCurrentText(str(default_value))

            if default_value:
                widget.setCurrentText(str(default_value))

            return widget

        elif param_type == "direction_buttons":
            # 8-way direction selector (simplified for now)
            widget = QLineEdit()
            widget.setText(str(default_value if default_value is not None else "[]"))
            widget.setPlaceholderText("Directions (e.g., [0, 90, 180, 270])")
            return widget

        else:
            # Fallback to string input
            widget = QLineEdit()
            widget.setText(str(default_value if default_value is not None else ""))
            return widget

    def pick_color(self, color_edit: QLineEdit):
        """Show color picker dialog"""
        current_color = QColor(color_edit.text())
        color = QColorDialog.getColor(current_color, self, "Pick Color")
        if color.isValid():
            color_edit.setText(color.name())

    def get_parameter_values(self) -> Dict[str, Any]:
        """Get all parameter values from widgets"""
        values = {}

        for param_name, widget in self.param_widgets.items():
            param = next((p for p in self.action_def.parameters if p.name == param_name), None)
            if not param:
                continue

            param_type = param.type

            if param_type == "boolean":
                values[param_name] = widget.isChecked()

            elif param_type == "int":
                values[param_name] = widget.value()

            elif param_type == "float":
                values[param_name] = widget.value()

            elif param_type == "string":
                values[param_name] = widget.text()

            elif param_type == "code":
                values[param_name] = widget.toPlainText()

            elif param_type == "choice":
                values[param_name] = widget.currentText()

            elif param_type == "color":
                # Extract color from the container widget
                color_edit = widget._color_edit
                values[param_name] = color_edit.text()

            elif param_type in ["object", "sprite", "sound", "room", "background",
                               "font", "script", "timeline"]:
                values[param_name] = widget.currentText()

            elif param_type == "direction_buttons":
                # Parse direction list
                try:
                    import json
                    values[param_name] = json.loads(widget.text())
                except:
                    values[param_name] = []

            else:
                values[param_name] = widget.text()

        return values

    def get_available_resources(self, resource_type: str) -> list:
        """Get list of available resources from project"""
        # Walk up to find IDE window
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_data'):
                project_data = parent.current_project_data
                if project_data and 'assets' in project_data:
                    # Map parameter type to asset type
                    asset_type_map = {
                        "object": "objects",
                        "sprite": "sprites",
                        "sound": "sounds",
                        "room": "rooms",
                        "background": "backgrounds",
                        "font": "fonts",
                        "script": "scripts",
                        "timeline": "timelines"
                    }

                    asset_type = asset_type_map.get(resource_type, resource_type + "s")
                    assets = project_data['assets'].get(asset_type, {})
                    return list(assets.keys())
                break
            parent = parent.parent()

        return []
