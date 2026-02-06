#!/usr/bin/env python3
"""
Action editor dialogs for configuring action parameters
"""

from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidgetItem, QTreeWidget, QMenu,
    QLabel, QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QDialogButtonBox, QTextEdit, QColorDialog,
    QWidget, QScrollArea, QFormLayout
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
        self.current_params = initial_params or {}

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

        self.setWindowTitle(self.tr("Configure {0}").format(action_type.display_name))
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

            elif param.param_type == "number":
                widget = QSpinBox()
                widget.setMinimum(param.min_value if param.min_value is not None else -9999)
                widget.setMaximum(param.max_value if param.max_value is not None else 9999)
                if param.name in self.current_params:
                    widget.setValue(int(self.current_params[param.name]))
                else:
                    widget.setValue(int(param.default_value))

            elif param.param_type == "float":
                widget = QDoubleSpinBox()
                widget.setMinimum(param.min_value if param.min_value is not None else -9999.0)
                widget.setMaximum(param.max_value if param.max_value is not None else 9999.0)
                widget.setDecimals(2)
                if param.name in self.current_params:
                    widget.setValue(float(self.current_params[param.name]))
                else:
                    widget.setValue(float(param.default_value))

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
                except Exception:
                    pass

                widget.clicked.connect(
                    lambda checked, w=widget: self.choose_color(w)
                )

            # Sprite selector
            elif param.param_type == "sprite":
                widget = QComboBox()
                widget.setEditable(False)

                # Get available sprites from project
                available_sprites = self.get_available_sprites()
                if available_sprites:
                    widget.addItems(available_sprites)
                else:
                    widget.addItems([self.tr("(No sprites available)")])

                if param.name in self.current_params:
                    widget.setCurrentText(str(self.current_params[param.name]))
                else:
                    widget.setCurrentText(str(param.default_value))

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
        dialog = ActionConfigDialog(action_type, existing_params, parent=self)

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
