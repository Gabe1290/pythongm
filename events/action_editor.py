#!/usr/bin/env python3
"""
Action editor dialogs for configuring action parameters
"""

from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidgetItem, QTreeWidget, QMenu,
    QLabel, QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QDialogButtonBox, QTextEdit, QColorDialog,
    QWidget, QScrollArea, QFormLayout, QMessageBox,
    QGroupBox, QRadioButton, QButtonGroup,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from core.logger import get_logger
logger = get_logger(__name__)

from .action_types import ActionType

class ActionConfigDialog(QDialog):
    """Dialog for configuring action parameters"""

    def __init__(self, action_type: ActionType, initial_params: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.action_type = action_type
        self.current_params = dict(initial_params) if initial_params else {}
        # Apply parameter aliases so older saved JSON (which may use a legacy key like
        # "variable_name" for what's now "variable") populates the dialog correctly.
        # On save the canonical key is written, so resaving migrates the action.
        for param in self.action_type.parameters:
            if param.name not in self.current_params:
                for alias in param.aliases:
                    if alias in self.current_params:
                        self.current_params[param.name] = self.current_params.pop(alias)
                        break

        # Check if this is a conditional action
        self.is_conditional = action_type.name == "if_condition"
        self.param_widgets = {}

        # Store nested action parameters
        self.nested_action_params = {
            'then_action_params': self.current_params.get('then_action_params', {}),
            'else_action_params': self.current_params.get('else_action_params', {})
        }

        # Store message translations (param_name -> {lang_code: translated_text})
        self.message_translations = {}
        if initial_params:
            for key, val in initial_params.items():
                if key.endswith("_translations") and isinstance(val, dict):
                    base_param = key[:-len("_translations")]
                    self.message_translations[base_param] = dict(val)

        self.setWindowTitle(self.tr("Configure {0}").format(self.tr(action_type.display_name)))
        self.setModal(True)
        self.resize(500, 400)

        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        # Special handling for conditional actions
        if self.is_conditional:
            layout = QVBoxLayout(self)
            label = QLabel(self.tr("This action requires special configuration."))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(self.accept)
            layout.addWidget(button_box)
            return

        # Regular action configuration
        layout = QVBoxLayout(self)

        # Action info
        title_label = QLabel(f"{self.action_type.icon} {self.tr(self.action_type.display_name)}")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)

        if self.action_type.description:
            desc_label = QLabel(self.action_type.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(desc_label)

        layout.addSpacing(10)

        # "Applies to" group (GM-style Self / Other / Object selector)
        self._object_radio = None
        self._other_radio = None
        self._self_radio = None
        self._applies_to_object_combo = None
        if getattr(self.action_type, 'supports_applies_to', False):
            layout.addWidget(self._build_applies_to_group())
            layout.addSpacing(10)

        # Parameters
        self.param_widgets = {}

        for param in self.action_type.parameters:
            param_layout = QHBoxLayout()

            label = QLabel(f"{self.tr(param.display_name)}:")
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

            # Special handling for object selection parameters (object_name).
            # Exclude pure choice params: check_empty's param is named 'objects'
            # but is a choice of ['solid','all'] the runtime collapses anything
            # else to 'all' — appending every project object name there offered
            # selections that silently behaved as 'all' (L18). Those fall
            # through to the choice branch below.
            elif (param.param_type != "choice"
                  and (param.name == "object_name" or "object" in param.name.lower())):
                widget = QComboBox()
                widget.setEditable(True)

                # Prepend choice-based selectors (e.g. ["any", "solid"] for
                # if_collision's "Against" field) ahead of the per-project
                # object list, so built-in selectors are as discoverable as
                # specific objects. Without this, if_collision's dropdown
                # showed "any" as the default-typed text but the value was
                # not in the list — confusing because the user couldn't
                # re-select it from the dropdown after editing.
                if param.choices:
                    widget.addItems(param.choices)

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
                        widget.setCurrentText(self.tr("→ Next Room"))
                    elif current_value == "__prev__":
                        widget.setCurrentText(self.tr("← Previous Room"))
                    elif current_value == "__current__":
                        widget.setCurrentText(self.tr("↺ Restart Current Room"))
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

                # Only add "Configure..." button if choices are actual registered action types
                from events.action_types import get_action_type
                has_configurable = any(get_action_type(c) for c in (param.choices or []) if c and c != "none")
                if has_configurable:
                    config_btn = QPushButton(self.tr("⚙️ Configure..."))
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
                widget.setPlaceholderText(str(param.default_value) if param.default_value else "")
                if param.name in self.current_params:
                    widget.setText(str(self.current_params[param.name]))
                else:
                    widget.setText(str(param.default_value) if param.default_value else "")

            # Multi-line freeform text (e.g. comments / notes)
            elif param.param_type == "text":
                widget = QTextEdit()
                widget.setAcceptRichText(False)
                widget.setMinimumHeight(80)
                widget.setPlaceholderText(str(param.default_value) if param.default_value else "")
                if param.name in self.current_params:
                    widget.setPlainText(str(self.current_params[param.name]))
                elif param.default_value:
                    widget.setPlainText(str(param.default_value))

            elif param.param_type in ("number", "float"):
                # Use QLineEdit to support both numeric values and expressions
                # (e.g. "32", "other.x + 16", "self.hspeed * 8")
                value = self.current_params.get(param.name, param.default_value)
                widget = QLineEdit()
                widget.setText(str(value) if value is not None else "0")
                widget.setPlaceholderText(self.tr("Number or expression"))

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
                widget = QPushButton(self.tr("📋 Configure Actions..."))
                widget.clicked.connect(
                    lambda checked, p=param.name: self.configure_action_list(p)
                )

                param_layout.addWidget(widget)

                # Store the action list data
                if param.name not in self.nested_action_params:
                    self.nested_action_params[param.name] = self.current_params.get(param.name, [])

                layout.addLayout(param_layout)
                continue

            # Color picker
            elif param.param_type == "color":
                current_color = self.current_params.get(param.name, param.default_value)
                widget = QPushButton()
                widget.setText(self.tr("🎨 Choose Color..."))
                widget.setProperty("color_value", current_color)

                # Set button background to current color
                try:
                    if isinstance(current_color, str) and current_color.startswith('#'):
                        widget.setStyleSheet(f"background-color: {current_color}; color: white;")
                except RuntimeError:
                    # Underlying Qt widget was deleted between creation and
                    # styling — happens during rapid editor switches.
                    pass

                widget.clicked.connect(
                    lambda checked, w=widget: self.choose_color(w)
                )

            # Sprite selector
            elif param.param_type == "sprite":
                widget = QComboBox()
                widget.setEditable(False)

                available_sprites = list(self.get_available_sprites() or [])

                # The value to display (saved value, else the default).
                if param.name in self.current_params:
                    current = str(self.current_params[param.name])
                else:
                    current = "" if param.default_value is None else str(param.default_value)

                # Prepend sentinel/empty entries that are not real project
                # sprites so they stay selectable and round-trip through
                # currentText. A non-editable combo silently ignores
                # setCurrentText for a value it has no item for, which
                # previously re-pointed every edited set_sprite action (default
                # "<self>") to the project's first sprite, and made draw_lives'
                # empty "no icon" value unreachable.
                sentinels = []
                if not param.required:
                    sentinels.append("")  # explicit "(no sprite)" option
                if isinstance(param.default_value, str) and param.default_value.startswith("<"):
                    if param.default_value not in sentinels:
                        sentinels.append(param.default_value)
                if current and current not in available_sprites and current not in sentinels:
                    sentinels.append(current)

                for s in sentinels:
                    widget.addItem(s)
                if available_sprites:
                    widget.addItems(available_sprites)
                elif not sentinels:
                    widget.addItems([self.tr("(No sprites available)")])

                widget.setCurrentText(current)

            # Sound selector
            elif param.param_type == "sound":
                widget = QComboBox()
                widget.setEditable(False)

                # Get available sounds from project
                available_sounds = self.get_available_sounds()
                if available_sounds:
                    widget.addItems(available_sounds)
                else:
                    widget.addItems([self.tr("(No sounds available)")])

                if param.name in self.current_params:
                    widget.setCurrentText(str(self.current_params[param.name]))
                else:
                    widget.setCurrentText(str(param.default_value))

            # Multi-line code editor
            elif param.param_type == "code":
                widget = QTextEdit()
                widget.setMaximumHeight(150)
                widget.setPlaceholderText(self.tr("Enter code here..."))
                if param.name in self.current_params:
                    widget.setPlainText(str(self.current_params[param.name]))
                else:
                    widget.setPlainText(str(param.default_value))

            # Position (X,Y pair)
            elif param.param_type == "position":
                # Create a horizontal layout for X and Y inputs
                pos_widget = QWidget()
                pos_layout = QHBoxLayout(pos_widget)
                pos_layout.setContentsMargins(0, 0, 0, 0)

                x_spin = QSpinBox()
                x_spin.setPrefix(self.tr("X: "))
                x_spin.setMinimum(-9999)
                x_spin.setMaximum(9999)

                y_spin = QSpinBox()
                y_spin.setPrefix(self.tr("Y: "))
                y_spin.setMinimum(-9999)
                y_spin.setMaximum(9999)

                # Set values
                if param.name in self.current_params:
                    pos_value = self.current_params[param.name]
                    if isinstance(pos_value, (list, tuple)) and len(pos_value) >= 2:
                        x_spin.setValue(int(pos_value[0]))
                        y_spin.setValue(int(pos_value[1]))
                else:
                    if isinstance(param.default_value, (list, tuple)) and len(param.default_value) >= 2:
                        x_spin.setValue(int(param.default_value[0]))
                        y_spin.setValue(int(param.default_value[1]))

                pos_layout.addWidget(x_spin)
                pos_layout.addWidget(y_spin)

                # Store both spinboxes for later retrieval
                pos_widget.setProperty("x_spin", x_spin)
                pos_widget.setProperty("y_spin", y_spin)

                widget = pos_widget

            else:
                widget = QLineEdit()
                widget.setPlaceholderText(str(param.default_value))
                if param.name in self.current_params:
                    widget.setText(str(self.current_params[param.name]))

            param_layout.addWidget(widget)
            self.param_widgets[param.name] = widget

            # Add "Translations..." button for message string parameters
            if param.param_type == "string" and param.name == "message":
                trans_btn = QPushButton(self.tr("Translations..."))
                trans_btn.setMaximumWidth(120)
                trans_btn.setToolTip(self.tr("Add translations for different languages"))
                trans_btn.clicked.connect(
                    lambda checked, p=param.name: self.edit_translations(p)
                )
                param_layout.addWidget(trans_btn)

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
        from events.conditional_editor import create_action_dialog
        dialog = create_action_dialog(action_type, existing_params, parent=self)

        if dialog.exec() == QDialog.Accepted:
            # Store the configured parameters
            self.nested_action_params[param_key] = dialog.get_parameter_values()
            logger.debug(f"Configured {action_name}: {self.nested_action_params[param_key]}")

    def choose_color(self, button_widget):
        """Open color picker dialog"""
        current_color = button_widget.property("color_value")

        # Parse current color
        if isinstance(current_color, str) and current_color.startswith('#'):
            initial_color = QColor(current_color)
        else:
            initial_color = QColor(255, 255, 255)

        # Show color picker
        color = QColorDialog.getColor(initial_color, self, self.tr("Choose Color"))

        if color.isValid():
            color_hex = color.name()  # Returns "#RRGGBB"
            button_widget.setProperty("color_value", color_hex)
            button_widget.setStyleSheet(f"background-color: {color_hex}; color: white;")
            button_widget.setText(self.tr("🎨 {0}").format(color_hex))

    def edit_translations(self, param_name: str):
        """Open the translations dialog for a message parameter"""
        current_translations = self.message_translations.get(param_name, {})
        default_text = ""
        widget = self.param_widgets.get(param_name)
        if isinstance(widget, QLineEdit):
            default_text = widget.text()

        dialog = MessageTranslationsDialog(
            default_text=default_text,
            translations=current_translations,
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.message_translations[param_name] = dialog.get_translations()

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

    def get_available_sprites(self):
        """Get list of available sprites from the project"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_data'):
                project_data = parent.current_project_data
                if project_data and 'assets' in project_data:
                    sprites = project_data['assets'].get('sprites', {})
                    return list(sprites.keys())
                break
            parent = parent.parent()

        return []

    def get_available_sounds(self):
        """Get list of available sounds from the project"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_data'):
                project_data = parent.current_project_data
                if project_data and 'assets' in project_data:
                    sounds = project_data['assets'].get('sounds', {})
                    return list(sounds.keys())
                break
            parent = parent.parent()

        return []

    def get_available_rooms(self):
        """Get list of available rooms from the project, including navigation options"""
        room_list = []

        # Add special navigation options first
        room_list.extend([
            self.tr("→ Next Room"),
            self.tr("← Previous Room"),
            self.tr("↺ Restart Current Room"),
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

    def _build_applies_to_group(self) -> QGroupBox:
        """Build the GM-style "Applies to" Self/Other/Object selector.

        Persists in action params as `target` ('self'|'other'|'object') and
        `target_object` (object name when target=='object').
        """
        group = QGroupBox(self.tr("Applies to"))
        glayout = QVBoxLayout(group)

        current_target = self.current_params.get('target', 'self')
        if current_target not in ('self', 'other', 'object'):
            # Tolerate legacy 'sel' alias from older runtime calls.
            current_target = 'self' if current_target == 'sel' else 'self'

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
        objects = self.get_available_objects() or []
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
        }[current_target].setChecked(True)

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
        if not getattr(self.action_type, 'supports_applies_to', False):
            return {}
        if self._object_radio is None:
            return {}
        if self._object_radio.isChecked():
            return {
                'target': 'object',
                'target_object': self._applies_to_object_combo.currentText(),
            }
        if self._other_radio.isChecked():
            return {'target': 'other', 'target_object': ''}
        return {'target': 'self', 'target_object': ''}

    def get_parameter_values(self) -> Dict[str, Any]:
        """Get configured parameter values including nested action parameters"""
        if self.is_conditional:
            return getattr(self, 'conditional_params', {})

        # Get current parameter values from widgets
        values = self._get_applies_to_values()
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QLineEdit):
                values[param_name] = widget.text()
            elif isinstance(widget, QSpinBox):
                values[param_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                values[param_name] = widget.value()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()

                # Map navigation options
                if param_name == "room_name" or "room" in param_name.lower():
                    if value == self.tr("→ Next Room"):
                        value = "__next__"
                    elif value == self.tr("← Previous Room"):
                        value = "__prev__"
                    elif value == self.tr("↺ Restart Current Room"):
                        value = "__current__"

                values[param_name] = value
            elif isinstance(widget, QCheckBox):
                values[param_name] = widget.isChecked()
            elif isinstance(widget, QTextEdit):
                # Code editor
                values[param_name] = widget.toPlainText()
            elif isinstance(widget, QPushButton):
                # Color picker button
                color_value = widget.property("color_value")
                values[param_name] = color_value if color_value else "#FFFFFF"
            elif hasattr(widget, 'property') and widget.property("x_spin") is not None:
                # Position widget (X,Y pair)
                x_spin = widget.property("x_spin")
                y_spin = widget.property("y_spin")
                values[param_name] = [x_spin.value(), y_spin.value()]

        # Add message translations if any exist
        for param_name, translations in self.message_translations.items():
            if translations:  # Only add non-empty translation dicts
                values[f"{param_name}_translations"] = translations

        # ADD NESTED ACTION PARAMETERS
        for key, params in self.nested_action_params.items():
            if params:  # Only add if there are parameters
                values[key] = params
                logger.debug(f"Adding nested param: {key} = {params}")

        logger.debug(f"Final values being returned: {values}")
        return values

    def accept(self):
        """Validate expression fields before closing.

        This project teaches Python, so a condition like
        ``vspeed > 0 && y < other.y`` is invalid — the student must use
        ``and`` / ``or`` / ``not``. Catch the common C/GML operators here and
        keep the dialog open so the mistake is fixed before it silently fails
        at runtime. Only the ``expression`` field is checked (other fields may
        legitimately contain ``!`` or ``|``).
        """
        from runtime.action_executor import detect_c_style_operators

        widget = self.param_widgets.get("expression") if hasattr(self, "param_widgets") else None
        if widget is not None:
            if isinstance(widget, QTextEdit):
                text = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                text = widget.text()
            else:
                text = ""
            offenders = detect_c_style_operators(text)
            if offenders:
                fixes = ", ".join(f"'{found}' → '{py}'" for found, py in offenders)
                QMessageBox.warning(
                    self,
                    self.tr("Use Python operators"),
                    self.tr(
                        "This expression uses C-style operators that Python "
                        "does not understand:\n\n    {fixes}\n\n"
                        "Please use the Python operators instead "
                        "(and / or / not), e.g. \"vspeed > 0 and y < other.y\"."
                    ).format(fixes=fixes),
                )
                return  # keep the dialog open so the student can fix it
        super().accept()

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
            logger.debug(f"Configured {len(self.nested_action_params[param_name])} actions for {param_name}")
            logger.debug(f"Actions: {self.nested_action_params[param_name]}")

class MultiActionEditor(QDialog):
    """Dialog for editing a list of actions (for Then/Else branches)"""

    def __init__(self, action_list: List[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.action_list = action_list or []

        self.setWindowTitle(self.tr("Configure Actions"))
        self.setModal(True)
        self.resize(600, 500)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(self.tr("Action Sequence"))
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # Action list
        self.action_tree = QTreeWidget()
        self.action_tree.setHeaderLabels([self.tr("Action"), self.tr("Parameters")])
        self.action_tree.itemDoubleClicked.connect(self.edit_action)
        layout.addWidget(self.action_tree)

        # Buttons for managing actions
        button_layout = QHBoxLayout()

        add_btn = QPushButton(self.tr("➕ Add Action"))
        add_btn.clicked.connect(self.add_action)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton(self.tr("✏️ Edit Action"))
        edit_btn.clicked.connect(lambda: self.edit_action(self.action_tree.currentItem(), 0))
        button_layout.addWidget(edit_btn)

        remove_btn = QPushButton(self.tr("➖ Remove Action"))
        remove_btn.clicked.connect(self.remove_action)
        button_layout.addWidget(remove_btn)

        move_up_btn = QPushButton(self.tr("⬆️ Move Up"))
        move_up_btn.clicked.connect(self.move_up)
        button_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton(self.tr("⬇️ Move Down"))
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

            # Render EVERY action, including unknown types, so the visible row
            # index always equals the data index. Skipping unknowns (e.g.
            # Blockly-only 'check_keys_and_move' or a plugin action) shifted the
            # rows, so Remove/Move operated on the wrong action (L19).
            item = QTreeWidgetItem()
            if action_type:
                item.setText(0, f"{action_type.icon} {self.tr(action_type.display_name)}")
            else:
                item.setText(0, f"❓ {self.tr('unknown')}: {action_name}")

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
            category_menu = menu.addMenu(self.tr(category))

            for action_type in actions:
                action_item = category_menu.addAction(f"{action_type.icon} {self.tr(action_type.display_name)}")
                action_item.triggered.connect(
                    lambda checked, at=action_type: self.configure_and_add_action(at)
                )

        menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))

    def configure_and_add_action(self, action_type):
        """Configure and add a new action"""
        from events.conditional_editor import create_action_dialog
        dialog = create_action_dialog(action_type, parent=self)

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

        from events.conditional_editor import create_action_dialog
        dialog = create_action_dialog(action_type, action_data.get("parameters", {}), parent=self)

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


class MessageTranslationsDialog(QDialog):
    """Dialog for editing translations of a message string"""

    def __init__(self, default_text: str = "", translations: dict = None, parent=None):
        super().__init__(parent)
        self.default_text = default_text
        self.translations = dict(translations) if translations else {}
        self.lang_edits = {}  # {lang_code: QLineEdit}

        self.setWindowTitle(self.tr("Message Translations"))
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()

    def _get_language_list(self):
        """Get available languages from LanguageManager, excluding English"""
        try:
            from core.language_manager import LanguageManager
            lang_info = LanguageManager.LANGUAGE_INFO
            # Return all languages except English, sorted by display name
            return sorted(
                [(code, name) for code, (name, _flag) in lang_info.items() if code != 'en'],
                key=lambda x: x[1]
            )
        except ImportError:
            # Fallback if LanguageManager is not available
            return [
                ('fr', 'Francais'), ('de', 'Deutsch'), ('es', 'Espanol'),
                ('it', 'Italiano'), ('pt', 'Portugues'), ('ru', 'Russian'),
                ('uk', 'Ukrainian'), ('sl', 'Slovenscina'),
            ]

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Show the default (English) message as read-only reference
        ref_label = QLabel(self.tr("Default message (English):"))
        layout.addWidget(ref_label)
        ref_text = QLineEdit(self.default_text)
        ref_text.setReadOnly(True)
        ref_text.setStyleSheet("background-color: #f0f0f0;")
        layout.addWidget(ref_text)

        layout.addSpacing(10)

        # Scrollable area for language fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)

        for lang_code, lang_name in self._get_language_list():
            edit = QLineEdit()
            edit.setPlaceholderText(self.tr("Translation for {0}").format(lang_name))
            if lang_code in self.translations:
                edit.setText(self.translations[lang_code])
            self.lang_edits[lang_code] = edit
            form_layout.addRow(f"{lang_name} ({lang_code}):", edit)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_translations(self) -> dict:
        """Return only non-empty translations"""
        result = {}
        for lang_code, edit in self.lang_edits.items():
            text = edit.text().strip()
            if text:
                result[lang_code] = text
        return result
