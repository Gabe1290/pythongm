#!/usr/bin/env python3
"""
Thymio Action Selector Dialog
Visual dialog for selecting Thymio robot actions with interactive robot diagram.
"""

from typing import Dict, Any, Optional, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QDialogButtonBox, QWidget, QLineEdit,
    QPushButton, QFrame, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from widgets.thymio_diagram_widget import (
    ThymioDiagramWidget, get_actions_for_region
)
from actions.thymio_actions import THYMIO_ACTIONS


# Action categories with display info
THYMIO_ACTION_CATEGORIES = {
    "thymio_motors": {
        "name": "Motors",
        "icon": "🔧",
        "order": 0,
        "description": "Motor control actions"
    },
    "thymio_leds": {
        "name": "LEDs",
        "icon": "💡",
        "order": 1,
        "description": "LED control actions"
    },
    "thymio_sound": {
        "name": "Sound",
        "icon": "🔊",
        "order": 2,
        "description": "Sound and tone actions"
    },
    "thymio_sensors": {
        "name": "Sensors",
        "icon": "📡",
        "order": 3,
        "description": "Sensor reading actions"
    },
    "thymio_conditions": {
        "name": "Conditions",
        "icon": "❓",
        "order": 4,
        "description": "Conditional check actions"
    },
    "thymio_timing": {
        "name": "Timing",
        "icon": "⏱️",
        "order": 5,
        "description": "Timer configuration"
    },
    "thymio_variables": {
        "name": "Variables",
        "icon": "📝",
        "order": 6,
        "description": "Variable manipulation"
    },
}


class ThymioActionSelector(QDialog):
    """
    Dialog for selecting Thymio actions with visual robot diagram.

    Features:
    - Interactive Thymio robot diagram with clickable regions
    - Category filter buttons
    - Search filtering
    - Action list with icons and descriptions
    - Automatic parameter configuration dialog
    """

    action_selected = Signal(str, dict)  # Emits action name and parameters

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_action = None
        self.configured_parameters = {}
        self.current_category = None  # None means show all
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(self.tr("Select Thymio Action"))
        self.setMinimumSize(450, 700)
        self.resize(450, 750)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        title = QLabel(self.tr("Select a Thymio action to add:"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        # Thymio diagram widget
        diagram_container = QFrame()
        diagram_container.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        diagram_layout = QHBoxLayout(diagram_container)
        diagram_layout.setContentsMargins(5, 5, 5, 5)

        self.diagram = ThymioDiagramWidget()
        self.diagram.region_clicked.connect(self.on_diagram_clicked)
        self.diagram.region_hovered.connect(self.on_diagram_hovered)
        diagram_layout.addStretch()
        diagram_layout.addWidget(self.diagram)
        diagram_layout.addStretch()

        layout.addWidget(diagram_container)

        # Hint label
        hint_label = QLabel(self.tr("Click on the robot to filter actions, or select from the list below."))
        hint_label.setStyleSheet("color: #666; font-style: italic;")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        # Category buttons
        category_frame = QFrame()
        category_layout = QHBoxLayout(category_frame)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(5)

        # "All" button
        self.all_button = QPushButton(self.tr("All"))
        self.all_button.setCheckable(True)
        self.all_button.setChecked(True)
        self.all_button.clicked.connect(lambda: self.filter_by_category(None))
        category_layout.addWidget(self.all_button)

        self.category_buttons = {'all': self.all_button}

        # Category buttons
        for cat_key, cat_info in sorted(THYMIO_ACTION_CATEGORIES.items(),
                                         key=lambda x: x[1].get('order', 0)):
            btn = QPushButton(f"{cat_info['icon']} {cat_info['name']}")
            btn.setCheckable(True)
            btn.setToolTip(cat_info.get('description', ''))
            btn.clicked.connect(lambda checked, c=cat_key: self.filter_by_category(c))
            category_layout.addWidget(btn)
            self.category_buttons[cat_key] = btn

        layout.addWidget(category_frame)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel(self.tr("Search:"))
        search_layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("Type to filter actions..."))
        self.search_box.textChanged.connect(self.filter_actions)
        self.search_box.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_box)

        layout.addLayout(search_layout)

        # Action list
        self.action_list = QListWidget()
        self.action_list.itemClicked.connect(self.on_action_clicked)
        self.action_list.itemDoubleClicked.connect(self.on_action_double_clicked)
        self.action_list.setMinimumHeight(200)
        layout.addWidget(self.action_list)

        # Description label
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(
            "background-color: #f5f5f5; padding: 8px; border-radius: 4px;"
        )
        self.description_label.setMinimumHeight(60)
        layout.addWidget(self.description_label)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)
        self.ok_button = buttons.button(QDialogButtonBox.Ok)
        self.ok_button.setText(self.tr("Configure && Add"))
        self.ok_button.setEnabled(False)
        layout.addWidget(buttons)

        # Populate the action list
        self.populate_actions()

    def populate_actions(self):
        """Populate the action list with all Thymio actions"""
        self.action_list.clear()

        for action_name, action_def in THYMIO_ACTIONS.items():
            # Apply category filter
            if self.current_category and action_def.category != self.current_category:
                continue

            # Create list item
            icon = action_def.icon or ""
            display_text = f"{icon} {action_def.display_name}"
            description = action_def.description or ""

            # Add parameter hint
            param_count = len(action_def.parameters) if action_def.parameters else 0
            if param_count > 0:
                param_hint = f" [{param_count} param{'s' if param_count > 1 else ''}]"
            else:
                param_hint = ""

            item = QListWidgetItem(f"{display_text}{param_hint}\n   {description}")
            item.setData(Qt.UserRole, {
                'name': action_name,
                'display_name': action_def.display_name,
                'description': description,
                'category': action_def.category,
                'icon': icon,
                'param_count': param_count
            })
            item.setToolTip(f"{action_def.display_name}\n{description}")

            self.action_list.addItem(item)

        # Apply search filter if there's text
        if self.search_box.text():
            self.filter_actions(self.search_box.text())

        # Select first item if available
        if self.action_list.count() > 0:
            self.action_list.setCurrentRow(0)
            self.on_action_clicked(self.action_list.item(0))

    def filter_by_category(self, category):
        """Filter actions by category"""
        self.current_category = category

        # Update button states
        for cat_key, btn in self.category_buttons.items():
            if cat_key == 'all':
                btn.setChecked(category is None)
            else:
                btn.setChecked(cat_key == category)

        # Clear diagram highlights
        self.diagram.clear_highlights()

        # Repopulate list
        self.populate_actions()

    def filter_actions(self, text):
        """Filter actions based on search text"""
        text = text.lower()

        for i in range(self.action_list.count()):
            item = self.action_list.item(i)
            action_data = item.data(Qt.UserRole)

            # Check if search text matches action name, display name, or description
            name = action_data.get('name', '').lower()
            display_name = action_data.get('display_name', '').lower()
            description = action_data.get('description', '').lower()

            matches = (text in name or
                      text in display_name or
                      text in description)

            item.setHidden(not matches)

    def on_diagram_clicked(self, region_id):
        """Handle click on diagram region"""
        # Get actions related to this region
        related_actions = get_actions_for_region(region_id)

        if related_actions:
            # Clear category filter to show all
            self.filter_by_category(None)

            # Find and select the first matching action
            for i in range(self.action_list.count()):
                item = self.action_list.item(i)
                action_data = item.data(Qt.UserRole)
                if action_data['name'] in related_actions:
                    self.action_list.setCurrentItem(item)
                    self.action_list.scrollToItem(item)
                    self.on_action_clicked(item)

                    # Highlight related actions in list
                    self._highlight_related_actions(related_actions)
                    break

            # Also highlight the clicked region
            self.diagram.clear_highlights()
            self.diagram.highlight_region(region_id)

    def on_diagram_hovered(self, region_id):
        """Handle hover over diagram region"""
        pass

    def _highlight_related_actions(self, action_names):
        """Visually highlight actions in the list that match the given names"""
        for i in range(self.action_list.count()):
            item = self.action_list.item(i)
            action_data = item.data(Qt.UserRole)

            if action_data['name'] in action_names:
                item.setHidden(False)

    def on_action_clicked(self, item):
        """Handle single click on action"""
        if item:
            action_data = item.data(Qt.UserRole)
            self.selected_action = action_data['name']

            # Update description
            icon = action_data.get('icon', '')
            name = action_data.get('display_name', '')
            desc = action_data.get('description', '')
            category = action_data.get('category', '')
            param_count = action_data.get('param_count', 0)

            # Get category display name
            cat_display = THYMIO_ACTION_CATEGORIES.get(category, {}).get('name', category)

            param_info = ""
            if param_count > 0:
                action_def = THYMIO_ACTIONS.get(self.selected_action)
                if action_def and action_def.parameters:
                    param_names = [p.display_name for p in action_def.parameters]
                    param_info = f"<br><small>Parameters: {', '.join(param_names)}</small>"

            self.description_label.setText(
                f"<b>{icon} {name}</b><br>"
                f"<small>Category: {cat_display}</small>"
                f"{param_info}<br><br>"
                f"{desc}"
            )

            # Update button text based on whether action has parameters
            if param_count > 0:
                self.ok_button.setText(self.tr("Configure && Add"))
            else:
                self.ok_button.setText(self.tr("Add Action"))

            self.ok_button.setEnabled(True)

            # Highlight related regions on diagram
            self._highlight_diagram_for_action(action_data['name'])

    def on_action_double_clicked(self, item):
        """Handle double-click on action"""
        self.accept_selection()

    def _highlight_diagram_for_action(self, action_name):
        """Highlight diagram regions related to the selected action"""
        self.diagram.clear_highlights()

        # Map actions to diagram regions
        action_to_regions = {
            # Motor actions
            'thymio_set_motor_speed': ['motor_left', 'motor_right'],
            'thymio_move_forward': ['motor_left', 'motor_right'],
            'thymio_move_backward': ['motor_left', 'motor_right'],
            'thymio_turn_left': ['motor_left', 'motor_right'],
            'thymio_turn_right': ['motor_left', 'motor_right'],
            'thymio_stop_motors': ['motor_left', 'motor_right'],
            # LED actions
            'thymio_set_led_top': ['led_top'],
            'thymio_set_led_bottom_left': ['led_bottom_left'],
            'thymio_set_led_bottom_right': ['led_bottom_right'],
            'thymio_set_led_circle': ['led_circle_0', 'led_circle_1', 'led_circle_2', 'led_circle_3',
                                      'led_circle_4', 'led_circle_5', 'led_circle_6', 'led_circle_7'],
            'thymio_set_led_circle_all': ['led_circle_0', 'led_circle_1', 'led_circle_2', 'led_circle_3',
                                          'led_circle_4', 'led_circle_5', 'led_circle_6', 'led_circle_7'],
            'thymio_leds_off': ['led_top', 'led_bottom_left', 'led_bottom_right',
                               'led_circle_0', 'led_circle_1', 'led_circle_2', 'led_circle_3',
                               'led_circle_4', 'led_circle_5', 'led_circle_6', 'led_circle_7'],
            # Sensor reading actions
            'thymio_read_proximity': ['prox_0', 'prox_1', 'prox_2', 'prox_3', 'prox_4', 'prox_5', 'prox_6'],
            'thymio_read_ground': ['ground_left', 'ground_right'],
            'thymio_read_button': ['button_forward', 'button_backward', 'button_left',
                                   'button_right', 'button_center'],
            # Conditional actions
            'thymio_if_proximity': ['prox_0', 'prox_1', 'prox_2', 'prox_3', 'prox_4', 'prox_5', 'prox_6'],
            'thymio_if_ground_dark': ['ground_left', 'ground_right'],
            'thymio_if_ground_light': ['ground_left', 'ground_right'],
            'thymio_if_button_pressed': ['button_forward', 'button_backward', 'button_left',
                                         'button_right', 'button_center'],
            'thymio_if_button_released': ['button_forward', 'button_backward', 'button_left',
                                          'button_right', 'button_center'],
        }

        regions = action_to_regions.get(action_name, [])
        if regions:
            self.diagram.highlight_regions(regions)

    def accept_selection(self):
        """Accept the current selection and configure parameters if needed"""
        current_item = self.action_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                self.tr("No Selection"),
                self.tr("Please select a Thymio action first.")
            )
            return

        action_data = current_item.data(Qt.UserRole)
        self.selected_action = action_data['name']

        # Get action definition
        action_def = THYMIO_ACTIONS.get(self.selected_action)

        if action_def and action_def.parameters:
            # Open parameter configuration dialog
            from editors.object_editor.gm80_action_dialog import GM80ActionDialog

            param_dialog = GM80ActionDialog(action_def, parent=self)
            if param_dialog.exec() == QDialog.Accepted:
                self.configured_parameters = param_dialog.get_parameter_values()
                self.action_selected.emit(self.selected_action, self.configured_parameters)
                self.accept()
            # If dialog rejected, don't close this dialog - user can select another action
        else:
            # No parameters, just accept
            self.configured_parameters = {}
            self.action_selected.emit(self.selected_action, self.configured_parameters)
            self.accept()

    def get_selected_action(self) -> Optional[str]:
        """Get the selected action name"""
        return self.selected_action

    def get_configured_parameters(self) -> Dict[str, Any]:
        """Get the configured parameters"""
        return self.configured_parameters

    def get_result(self) -> Tuple[Optional[str], Dict[str, Any]]:
        """Get the complete result (action name and parameters)"""
        return self.selected_action, self.configured_parameters
