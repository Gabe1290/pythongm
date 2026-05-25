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
    QDialogButtonBox, QGroupBox, QColorDialog, QWidget,
    QRadioButton, QButtonGroup,
)
from PySide6.QtGui import QFont, QColor

from actions import ActionDefinition, ActionParameter

from core.logger import get_logger
logger = get_logger(__name__)


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
        self.setWindowTitle(self.tr("Configure: {0}").format(self.action_def.display_name))
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        # Action title and description
        title_label = QLabel(f"{self.action_def.icon} {self.tr(self.action_def.display_name)}")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)

        if self.action_def.description:
            desc_label = QLabel(self.tr(self.action_def.description))
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: gray; padding: 5px;")
            layout.addWidget(desc_label)

        # "Applies to" group (GM-style Self / Other / Object selector)
        self._applies_to_target = None
        self._applies_to_object_combo = None
        if getattr(self.action_def, 'supports_applies_to', False):
            layout.addWidget(self._build_applies_to_group())

        # Parameters
        if self.action_def.parameters:
            params_group = QGroupBox(self.tr("Parameters"))
            params_layout = QFormLayout()

            for param in self.action_def.parameters:
                widget = self.create_parameter_widget(param)
                if widget:
                    self.param_widgets[param.name] = widget
                    label = QLabel(self.tr(param.display_name) + ":")
                    if param.description:
                        label.setToolTip(param.description)
                    params_layout.addRow(label, widget)

            params_group.setLayout(params_layout)
            layout.addWidget(params_group)
        else:
            no_params_label = QLabel(self.tr("This action has no parameters."))
            no_params_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_params_label)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _build_applies_to_group(self) -> QGroupBox:
        """Build the GM-style "Applies to" Self/Other/Object selector.

        Stores choice in self._applies_to_target ('self'|'other'|'object'),
        with the object name available via self._applies_to_object_combo.
        Persists in action params as 'target' and 'target_object'.
        """
        group = QGroupBox(self.tr("Applies to"))
        glayout = QVBoxLayout(group)

        self._applies_to_target = self.current_params.get('target', 'self')
        if self._applies_to_target not in ('self', 'other', 'object'):
            # Tolerate legacy 'sel' alias from older runtime calls.
            self._applies_to_target = 'self' if self._applies_to_target == 'sel' else 'self'

        self._applies_to_buttons = QButtonGroup(group)
        self._self_radio = QRadioButton(self.tr("Self"))
        self._other_radio = QRadioButton(self.tr("Other"))
        self._object_radio = QRadioButton(self.tr("Object:"))
        self._applies_to_buttons.addButton(self._self_radio)
        self._applies_to_buttons.addButton(self._other_radio)
        self._applies_to_buttons.addButton(self._object_radio)

        glayout.addWidget(self._self_radio)
        glayout.addWidget(self._other_radio)

        # Object row: radio + dropdown of project objects
        object_row = QHBoxLayout()
        object_row.addWidget(self._object_radio)
        self._applies_to_object_combo = QComboBox()
        self._applies_to_object_combo.setEditable(False)
        self._applies_to_object_combo.setMinimumWidth(180)
        objects = self.get_available_resources("object")
        if objects:
            self._applies_to_object_combo.addItems(objects)
        saved_obj = self.current_params.get('target_object', '')
        if saved_obj and saved_obj in objects:
            self._applies_to_object_combo.setCurrentText(saved_obj)
        object_row.addWidget(self._applies_to_object_combo, stretch=1)
        glayout.addLayout(object_row)

        # Restore selection
        {
            'self': self._self_radio,
            'other': self._other_radio,
            'object': self._object_radio,
        }[self._applies_to_target].setChecked(True)

        # Object combo only enabled when "Object" radio is selected
        def _sync_object_combo():
            self._applies_to_object_combo.setEnabled(self._object_radio.isChecked())
        _sync_object_combo()
        self._self_radio.toggled.connect(_sync_object_combo)
        self._other_radio.toggled.connect(_sync_object_combo)
        self._object_radio.toggled.connect(_sync_object_combo)

        return group

    def _get_applies_to_values(self) -> Dict[str, Any]:
        """Read current Applies-to selection. Returns {} if selector wasn't shown."""
        if not getattr(self.action_def, 'supports_applies_to', False):
            return {}
        if self._object_radio.isChecked():
            return {
                'target': 'object',
                'target_object': self._applies_to_object_combo.currentText(),
            }
        if self._other_radio.isChecked():
            return {'target': 'other', 'target_object': ''}
        return {'target': 'self', 'target_object': ''}

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

            pick_btn = QPushButton(self.tr("Pick Color..."))
            pick_btn.clicked.connect(lambda: self.pick_color(color_edit))
            layout.addWidget(pick_btn)

            container._color_edit = color_edit  # Store reference
            return container

        elif param_type in ["object", "sprite", "sound", "room", "background",
                           "font", "script", "timeline"]:
            # Resource selector dropdown
            logger.debug(f"Creating QComboBox for param_type='{param_type}'")
            widget = QComboBox()
            # NOT editable - this ensures the dropdown arrow is always visible
            widget.setEditable(False)
            widget.setMinimumWidth(200)

            # For object type, add special options first
            if param_type == "object":
                widget.addItem("any")
                widget.addItem("solid")
                widget.addItem("all")
                widget.insertSeparator(3)

            # For sprite type in set_sprite action, add "<self>" option first
            # This allows modifying animation properties of the current sprite
            if param_type == "sprite" and self.action_def.name == "set_sprite":
                widget.addItem("<self>")
                widget.insertSeparator(1)

            # Get available resources from project
            resources = self.get_available_resources(param_type)
            logger.debug(f"Found {len(resources)} resources: {resources}")
            if resources:
                widget.addItems(resources)

            # Set current value
            if default_value:
                widget.setCurrentText(str(default_value))

            logger.debug(f"QComboBox created with {widget.count()} items, isEditable={widget.isEditable()}")

            return widget

        elif param_type == "direction_buttons":
            # 8-way direction selector (simplified for now)
            widget = QLineEdit()
            widget.setText(str(default_value if default_value is not None else "[]"))
            widget.setPlaceholderText("Directions (e.g., [0, 90, 180, 270])")
            return widget

        elif param_type == "action_list":
            # Action list (then_actions, else_actions) - use a button to configure
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            # Store the action list data
            action_list = default_value if isinstance(default_value, list) else []
            container._action_list = action_list

            # Show count label
            count_label = QLabel(self.tr("{0} actions").format(len(action_list)))
            layout.addWidget(count_label)
            container._count_label = count_label

            # Configure button
            config_btn = QPushButton(self.tr("📋 Configure..."))
            config_btn.clicked.connect(lambda: self.configure_action_list(container, param.name))
            layout.addWidget(config_btn)

            return container

        else:
            # Fallback to string input
            widget = QLineEdit()
            widget.setText(str(default_value if default_value is not None else ""))
            return widget

    def pick_color(self, color_edit: QLineEdit):
        """Show color picker dialog"""
        current_color = QColor(color_edit.text())
        color = QColorDialog.getColor(current_color, self, self.tr("Pick Color"))
        if color.isValid():
            color_edit.setText(color.name())

    def configure_action_list(self, container, param_name: str):
        """Open dialog to configure action list"""
        from events.action_editor import MultiActionEditor

        action_list = container._action_list.copy() if container._action_list else []

        dialog = MultiActionEditor(action_list, parent=self)
        if dialog.exec() == QDialog.Accepted:
            container._action_list = dialog.get_action_list()
            container._count_label.setText(self.tr("{0} actions").format(len(container._action_list)))

    def get_parameter_values(self) -> Dict[str, Any]:
        """Get all parameter values from widgets"""
        values = self._get_applies_to_values()

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
                except Exception:
                    values[param_name] = []

            elif param_type == "action_list":
                # Extract action list from container widget
                values[param_name] = widget._action_list if hasattr(widget, '_action_list') else []

            else:
                values[param_name] = widget.text()

        return values

    def get_available_resources(self, resource_type: str) -> list:
        """Get list of available resources from project"""
        from PySide6.QtWidgets import QApplication

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

        # Try to find project data from multiple sources:
        # 1. Walk up parent chain
        # 2. Check active window (main IDE)
        # 3. Check all top-level windows

        sources_to_check = []

        # Add parent chain
        parent = self.parent()
        while parent:
            sources_to_check.append(parent)
            parent = parent.parent()

        # Add active window
        active_window = QApplication.activeWindow()
        if active_window and active_window not in sources_to_check:
            sources_to_check.append(active_window)

        # Add all top-level widgets
        for widget in QApplication.topLevelWidgets():
            if widget not in sources_to_check:
                sources_to_check.append(widget)

        # Check all sources for project data
        for source in sources_to_check:
            # Try current_project_data first
            if hasattr(source, 'current_project_data'):
                project_data = source.current_project_data
                if project_data and 'assets' in project_data:
                    assets = project_data['assets'].get(asset_type, {})
                    if assets:
                        return sorted(assets.keys())

            # Also try project_manager as fallback
            if hasattr(source, 'project_manager') and source.project_manager:
                project_data = source.project_manager.get_current_project_data()
                if project_data and 'assets' in project_data:
                    assets = project_data['assets'].get(asset_type, {})
                    if assets:
                        return sorted(assets.keys())

        return []
