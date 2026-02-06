#!/usr/bin/env python3
"""
Object Events Panel
Manages object events and their actions
"""

from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QDialog, QDialogButtonBox,
    QCheckBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

# Import our new event/action system
from events.event_types import get_available_events, get_event_type
from events.action_types import get_action_type as _get_action_type, get_actions_by_category
from events.action_editor import ActionConfigDialog

# Action name aliases (alternative names -> canonical names)
ACTION_ALIASES = {
    'add_score': 'set_score',
    'add_lives': 'set_lives',
    'add_health': 'set_health',
    'room_restart': 'restart_room',
    'room_goto_next': 'next_room',
    'room_goto_previous': 'previous_room',
    'room_goto': 'goto_room',
}

def get_action_type(action_name: str):
    """Get action type with alias support"""
    # Try the original name first
    result = _get_action_type(action_name)
    if result:
        return result

    # Try the alias if available
    if action_name in ACTION_ALIASES:
        return _get_action_type(ACTION_ALIASES[action_name])

    return None

# Import formatter
from .object_actions_formatter import ActionParametersFormatter

# Import Python code parser for execute_code action parsing
from .python_code_parser import PythonToActionsParser

from core.logger import get_logger
logger = get_logger(__name__)


class ObjectEventsPanel(QWidget):
    """Panel for managing object events and their actions"""

    events_modified = Signal()
    event_selected = Signal(str)  # event_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_events_data = {}
        self.dragging_action = None  # Track action being dragged
        self.drag_source_parent = None  # Track where drag started
        self.blockly_config = None  # Blockly configuration for filtering actions
        self.setup_ui()

        # Setup shortcuts after UI is complete
        QTimer.singleShot(0, self.setup_shortcuts)

    def setup_ui(self):
        """Setup the events panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Events list
        events_label = QLabel(self.tr("Object Events"))
        events_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(events_label)

        # Events tree widget
        self.events_tree = QTreeWidget()
        self.events_tree.setHeaderLabels([self.tr("Event"), self.tr("Actions")])
        self.events_tree.setExpandsOnDoubleClick(False)

        # Make columns use full width for text
        self.events_tree.setWordWrap(False)  # Don't wrap text
        self.events_tree.setTextElideMode(Qt.ElideRight)  # Show ... at end if too long

        # Configure header for 55-45 split with dynamic resizing
        header = self.events_tree.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, header.ResizeMode.Interactive)  # Event column resizable
        # Column 1 (Actions) will stretch automatically

        # Set initial 55-45 split after widget is shown (Event column slightly wider)
        def set_initial_widths():
            total_width = self.events_tree.viewport().width()
            self.events_tree.setColumnWidth(0, int(total_width * 0.55))

        # Delay setting widths until widget is visible
        QTimer.singleShot(100, set_initial_widths)

        # Add resize event handler to maintain proportions
        def on_resize(event):
            """Keep columns proportional when resizing"""
            # Let the default handler run first
            QTreeWidget.resizeEvent(self.events_tree, event)
            # Then adjust column 0 to be 55% of visible width
            viewport_width = self.events_tree.viewport().width()
            self.events_tree.setColumnWidth(0, int(viewport_width * 0.55))

        # Override resize event
        self.events_tree.resizeEvent = on_resize

        self.events_tree.itemClicked.connect(self.on_event_selected)
        self.events_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.events_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.events_tree.customContextMenuRequested.connect(self.show_context_menu)

        # Enable drag and drop for reordering
        self.events_tree.setDragEnabled(True)
        self.events_tree.setAcceptDrops(True)
        self.events_tree.setDropIndicatorShown(True)
        self.events_tree.setDragDropMode(QTreeWidget.InternalMove)
        self.events_tree.setSelectionMode(QTreeWidget.SingleSelection)

        # Override drag/drop events
        self.events_tree.dragEnterEvent = self.tree_drag_enter_event
        self.events_tree.dragMoveEvent = self.tree_drag_move_event
        self.events_tree.dropEvent = self.tree_drop_event

        layout.addWidget(self.events_tree)

        # Add event button
        button_layout = QHBoxLayout()
        self.add_event_btn = QPushButton(self.tr("+ Add Event"))
        self.add_event_btn.clicked.connect(self.show_add_event_menu)
        button_layout.addWidget(self.add_event_btn)

        self.remove_event_btn = QPushButton(self.tr("- Remove Event"))
        self.remove_event_btn.clicked.connect(self.remove_selected_event)
        self.remove_event_btn.setEnabled(False)
        button_layout.addWidget(self.remove_event_btn)

        layout.addLayout(button_layout)

        # Action reordering buttons
        reorder_layout = QHBoxLayout()
        self.move_up_btn = QPushButton(self.tr("↑ Move Up"))
        self.move_up_btn.clicked.connect(self.move_action_up)
        self.move_up_btn.setEnabled(False)
        self.move_up_btn.setToolTip(self.tr("Move selected action up (Ctrl+Up)"))
        reorder_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton(self.tr("↓ Move Down"))
        self.move_down_btn.clicked.connect(self.move_action_down)
        self.move_down_btn.setEnabled(False)
        self.move_down_btn.setToolTip(self.tr("Move selected action down (Ctrl+Down)"))
        reorder_layout.addWidget(self.move_down_btn)

        layout.addLayout(reorder_layout)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts after widget is fully initialized"""
        try:
            from PySide6.QtGui import QShortcut, QKeySequence
            self.move_up_shortcut = QShortcut(QKeySequence(self.tr("Ctrl+Up")), self)
            self.move_up_shortcut.activated.connect(self.move_action_up)

            self.move_down_shortcut = QShortcut(QKeySequence(self.tr("Ctrl+Down")), self)
            self.move_down_shortcut.activated.connect(self.move_action_down)
        except Exception as e:
            logger.warning(f"Could not setup shortcuts: {e}")

    def add_event(self, event_name: str):
        """Add a regular event (not a sub-event)"""
        # Check if event already exists
        if event_name in self.current_events_data:
            QMessageBox.information(
                self,
                self.tr("Event Exists"),
                self.tr("The {0} event already exists.").format(event_name)
            )
            return

        # Create new event with empty actions list
        self.current_events_data[event_name] = {
            "actions": []
        }

        self.refresh_events_display()
        self.events_modified.emit()

    def show_add_event_menu(self):
        """Show menu to add new events"""
        menu = QMenu(self)

        available_events = get_available_events()
        for event_type in available_events:
            if event_type.name == "collision":
                # Special handling for collision events - create submenu
                collision_menu = menu.addMenu(self.tr(f"{event_type.icon} Collision With..."))

                # Get available objects from project
                available_objects = self.get_available_objects()

                if available_objects:
                    for obj_name in available_objects:
                        obj_action = collision_menu.addAction(f"📦 {obj_name}")
                        obj_action.triggered.connect(
                            lambda checked, obj=obj_name: self.add_collision_event(obj)
                        )
                else:
                    no_objects_action = collision_menu.addAction(self.tr("No objects available"))
                    no_objects_action.setEnabled(False)

            elif event_type.name in ["keyboard", "keyboard_press", "keyboard_release"]:
                # New keyboard events with key selector
                action = menu.addAction(f"{event_type.icon} {event_type.display_name}...")
                action.triggered.connect(lambda checked, name=event_type.name: self.add_keyboard_event_with_selector(name))

            elif event_type.name == "mouse":
                # Mouse event with event selector
                action = menu.addAction(f"{event_type.icon} {event_type.display_name}...")
                action.triggered.connect(lambda checked: self.add_mouse_event_with_selector())

            elif event_type.parameters and isinstance(event_type.parameters, list):
                # Handle old-style keyboard events with sub_events
                has_sub_events = any(
                    isinstance(p, dict) and p.get("type") == "sub_events"
                    for p in event_type.parameters
                )

                if has_sub_events:
                    sub_menu = menu.addMenu(f"{event_type.icon} {event_type.display_name}")
                    sub_event_param = next(
                        (p for p in event_type.parameters
                        if isinstance(p, dict) and p.get("type") == "sub_events"),
                        None
                    )

                    if sub_event_param:
                        keys = sub_event_param.get("keys", [])
                        for key in keys:
                            key_icons = {
                                "left": "⬅️",
                                "right": "➡️",
                                "up": "⬆️",
                                "down": "⬇️"
                            }
                            icon = key_icons.get(key, "▪️")
                            action = sub_menu.addAction(f"{icon} {key.title()} {self.tr('Arrow')}")
                            action.triggered.connect(
                                lambda checked, name=event_type.name, k=key: self.add_sub_event(name, k)
                            )
                else:
                    action = menu.addAction(f"{event_type.icon} {event_type.display_name}")
                    action.triggered.connect(lambda checked, name=event_type.name: self.add_event(name))
            else:
                # Regular events
                action = menu.addAction(f"{event_type.icon} {event_type.display_name}")
                action.triggered.connect(lambda checked, name=event_type.name: self.add_event(name))

        # Add Thymio Events option
        menu.addSeparator()
        thymio_action = menu.addAction(self.tr("🤖 Thymio Event..."))
        thymio_action.triggered.connect(self.add_thymio_event_with_selector)

        menu.exec(self.add_event_btn.mapToGlobal(self.add_event_btn.rect().bottomLeft()))

    def add_sub_event(self, event_name: str, key: str):
        """Add a keyboard sub-event for a specific key"""
        # Initialize keyboard event structure if it doesn't exist
        if event_name not in self.current_events_data:
            self.current_events_data[event_name] = {}

        # Check if this specific key already exists
        if key in self.current_events_data[event_name]:
            QMessageBox.information(
                self,
                self.tr("Key Event Exists"),
                self.tr("The {0} arrow key event already exists.").format(key)
            )
            return

        # Create new sub-event with empty actions list
        self.current_events_data[event_name][key] = {
            "actions": []
        }

        self.refresh_events_display()
        self.events_modified.emit()

    def add_keyboard_event_with_selector(self, event_name: str):
        """Add a keyboard event using the key selector dialog"""
        from dialogs.key_selector_dialog import KeySelectorDialog

        dialog = KeySelectorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            selected_key = dialog.get_selected_key()
            selected_key_code = dialog.get_selected_key_code()

            if selected_key and selected_key_code:
                # Check if event already exists
                if event_name in self.current_events_data and selected_key in self.current_events_data[event_name]:
                    QMessageBox.information(
                        self,
                        self.tr("Key Event Exists"),
                        self.tr("The {0} key event already exists for {1}.").format(selected_key, event_name)
                    )
                    return

                # Initialize event structure if needed
                if event_name not in self.current_events_data:
                    self.current_events_data[event_name] = {}

                # Add the key event with metadata
                self.current_events_data[event_name][selected_key] = {
                    "actions": [],
                    "key_code": selected_key_code
                }

                self.refresh_events_display()
                self.events_modified.emit()

    def add_mouse_event_with_selector(self):
        """Add a mouse event using the mouse event selector dialog"""
        from dialogs.mouse_event_selector_dialog import MouseEventSelectorDialog

        dialog = MouseEventSelectorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            selected_event = dialog.get_selected_event()

            if selected_event:
                # Create event key from the mouse event data
                # Format: "mouse_{event_type}" e.g., "mouse_left_button", "mouse_wheel_up"
                event_type = selected_event.get('event_type', '')
                button = selected_event.get('button', '')

                # Build the unique event key
                if button:
                    event_key = f"mouse_{button.lower()}_{event_type}"
                else:
                    event_key = f"mouse_{event_type}"

                # Check if event already exists
                if event_key in self.current_events_data:
                    QMessageBox.information(
                        self,
                        self.tr("Mouse Event Exists"),
                        self.tr("This mouse event already exists.")
                    )
                    return

                # Add the mouse event
                self.current_events_data[event_key] = {
                    "actions": [],
                    "mouse_event": selected_event
                }

                self.refresh_events_display()
                self.events_modified.emit()

    def add_thymio_event_with_selector(self):
        """Add a Thymio event using the visual Thymio event selector dialog"""
        from dialogs.thymio_event_selector import ThymioEventSelector

        dialog = ThymioEventSelector(self)
        if dialog.exec() == QDialog.Accepted:
            selected_event = dialog.get_selected_event()

            if selected_event:
                # Check if event already exists
                if selected_event in self.current_events_data:
                    QMessageBox.information(
                        self,
                        self.tr("Thymio Event Exists"),
                        self.tr("This Thymio event already exists.")
                    )
                    return

                # Add the Thymio event
                self.current_events_data[selected_event] = {
                    "actions": []
                }

                self.refresh_events_display()
                self.events_modified.emit()

    def add_thymio_action_with_selector(self, event_name: str):
        """Add a Thymio action using the visual Thymio action selector dialog"""
        from dialogs.thymio_action_selector import ThymioActionSelector

        dialog = ThymioActionSelector(self)
        if dialog.exec() == QDialog.Accepted:
            action_name, parameters = dialog.get_result()

            if action_name:
                # Create action data structure
                action_data = {
                    "action": action_name,
                    "parameters": parameters
                }

                # Add to event
                if event_name not in self.current_events_data:
                    self.current_events_data[event_name] = {"actions": []}

                self.current_events_data[event_name]["actions"].append(action_data)
                self.refresh_events_display()
                self.events_modified.emit()

    def add_thymio_action_to_sub_event(self, event_name: str, sub_event_key: str):
        """Add a Thymio action to a keyboard sub-event using the visual selector dialog"""
        from dialogs.thymio_action_selector import ThymioActionSelector

        dialog = ThymioActionSelector(self)
        if dialog.exec() == QDialog.Accepted:
            action_name, parameters = dialog.get_result()

            if action_name:
                # Create action data structure
                action_data = {
                    "action": action_name,
                    "parameters": parameters
                }

                # Add to sub-event
                if event_name in self.current_events_data:
                    if sub_event_key in self.current_events_data[event_name]:
                        if "actions" not in self.current_events_data[event_name][sub_event_key]:
                            self.current_events_data[event_name][sub_event_key]["actions"] = []
                        self.current_events_data[event_name][sub_event_key]["actions"].append(action_data)
                        self.refresh_events_display()
                        self.events_modified.emit()

    def remove_selected_event(self):
        """Remove the currently selected event"""
        current_item = self.events_tree.currentItem()
        if not current_item or not current_item.parent() is None:
            return  # Must be a top-level event item

        event_name = current_item.data(0, Qt.UserRole)
        if event_name and event_name in self.current_events_data:
            reply = QMessageBox.question(
                self,
                self.tr("Remove Event"),
                self.tr("Are you sure you want to remove the {0} event and all its actions?").format(event_name),
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                del self.current_events_data[event_name]
                self.refresh_events_display()
                self.events_modified.emit()

    def show_context_menu(self, position):
        """Show context menu for events tree"""
        item = self.events_tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        # Determine the item level and type
        parent = item.parent()
        grandparent = parent.parent() if parent else None

        # Level 1: Top-level event (create, step, collision, keyboard parent, etc.)
        if parent is None:
            event_name = item.data(0, Qt.UserRole)

            # Handle collision events specially
            if isinstance(event_name, str) and (event_name.startswith("collision_with_") or event_name.startswith("not_collision_with_")):
                add_action_menu = menu.addMenu(self.tr("Add Action"))

                actions_by_category = get_actions_by_category(self.blockly_config)
                for category, actions in actions_by_category.items():
                    category_menu = add_action_menu.addMenu(category)

                    for action_type in actions:
                        action_item = category_menu.addAction(f"{action_type.icon} {action_type.display_name}")
                        action_item.triggered.connect(
                            lambda checked, e=event_name, a=action_type.name: self.add_action_to_collision_event(e, a)
                        )

                # Add Thymio action option
                add_action_menu.addSeparator()
                thymio_action = add_action_menu.addAction(self.tr("🤖 Thymio Action..."))
                thymio_action.triggered.connect(lambda checked, e=event_name: self.add_thymio_action_with_selector(e))

                menu.addSeparator()
                remove_action = menu.addAction(self.tr("Remove Collision Event"))
                remove_action.triggered.connect(lambda: self.remove_collision_event(event_name))

            # Handle mouse events specially
            elif isinstance(event_name, str) and event_name.startswith("mouse_"):
                add_action_menu = menu.addMenu(self.tr("Add Action"))

                actions_by_category = get_actions_by_category(self.blockly_config)
                for category, actions in actions_by_category.items():
                    category_menu = add_action_menu.addMenu(category)

                    for action_type in actions:
                        action_item = category_menu.addAction(f"{action_type.icon} {action_type.display_name}")
                        action_item.triggered.connect(
                            lambda checked, e=event_name, a=action_type.name: self.add_action_to_mouse_event(e, a)
                        )

                # Add Thymio action option
                add_action_menu.addSeparator()
                thymio_action = add_action_menu.addAction(self.tr("🤖 Thymio Action..."))
                thymio_action.triggered.connect(lambda checked, e=event_name: self.add_thymio_action_with_selector(e))

                menu.addSeparator()
                remove_action = menu.addAction(self.tr("Remove Mouse Event"))
                remove_action.triggered.connect(lambda: self.remove_mouse_event(event_name))

            else:
                # Regular events (create, step, etc.) or keyboard parent events
                add_action_menu = menu.addMenu(self.tr("Add Action"))

                actions_by_category = get_actions_by_category(self.blockly_config)
                for category, actions in actions_by_category.items():
                    category_menu = add_action_menu.addMenu(category)

                    for action_type in actions:
                        action_item = category_menu.addAction(f"{action_type.icon} {action_type.display_name}")
                        action_item.triggered.connect(
                            lambda checked, e=event_name, a=action_type.name: self.add_action_to_event(e, a)
                        )

                # Add Thymio action option
                add_action_menu.addSeparator()
                thymio_action = add_action_menu.addAction(self.tr("🤖 Thymio Action..."))
                thymio_action.triggered.connect(lambda checked, e=event_name: self.add_thymio_action_with_selector(e))

                menu.addSeparator()
                remove_action = menu.addAction(self.tr("Remove Event"))
                remove_action.triggered.connect(self.remove_selected_event)

        # Level 2: Could be keyboard sub-event OR action under regular event
        elif parent and grandparent is None:
            item_data = item.data(0, Qt.UserRole)

            # Check if this is a keyboard sub-event (string data) or action (dict data)
            if isinstance(item_data, str) and "_" in item_data:
                # This is a keyboard sub-event (Left Arrow, Right Arrow, etc.)
                parent_item = parent
                event_name = parent_item.data(0, Qt.UserRole)

                # Extract the key from the stored data (format: "keyboard_left" or "keyboard_press_left")
                if item_data.startswith(event_name + "_"):
                    sub_event_key = item_data[len(event_name) + 1:]  # Extract the key after "event_name_"

                    # Add action submenu for this specific key
                    add_action_menu = menu.addMenu(self.tr("Add Action"))

                    actions_by_category = get_actions_by_category(self.blockly_config)
                    for category, actions in actions_by_category.items():
                        category_menu = add_action_menu.addMenu(category)

                        for action_type in actions:
                            action_item = category_menu.addAction(f"{action_type.icon} {action_type.display_name}")
                            action_item.triggered.connect(
                                lambda checked, e=event_name, k=sub_event_key, a=action_type.name:
                                self.add_action_to_sub_event(e, k, a)
                            )

                    # Add Thymio action option
                    add_action_menu.addSeparator()
                    thymio_action = add_action_menu.addAction(self.tr("🤖 Thymio Action..."))
                    thymio_action.triggered.connect(
                        lambda checked, e=event_name, k=sub_event_key: self.add_thymio_action_to_sub_event(e, k)
                    )

                    menu.addSeparator()
                    remove_action = menu.addAction(self.tr(f"Remove {sub_event_key.title()} Arrow Event"))
                    remove_action.triggered.connect(lambda: self.remove_sub_event(parent_item, item))

            elif isinstance(item_data, dict):
                # This is an action under a regular event (Create, Step, Collision, etc.)
                edit_action = menu.addAction(self.tr("Edit Action"))
                edit_action.triggered.connect(lambda: self.edit_action(item))

                remove_action = menu.addAction(self.tr("Remove Action"))
                remove_action.triggered.connect(lambda: self.remove_action(item))

        # Level 3: Action item (child of either regular event or keyboard sub-event)
        else:
            action_data = item.data(0, Qt.UserRole)
            if action_data and isinstance(action_data, dict):
                edit_action = menu.addAction(self.tr("Edit Action"))
                edit_action.triggered.connect(lambda: self.edit_action(item))

                remove_action = menu.addAction(self.tr("Remove Action"))
                remove_action.triggered.connect(lambda: self.remove_action(item))

        menu.exec(self.events_tree.mapToGlobal(position))

    def add_action_to_event(self, event_name: str, action_name: str):
        """Add an action to an event"""
        action_type = get_action_type(action_name)
        if not action_type:
            return

        # Check if this event has sub-events (keyboard, keyboard_press)
        event_type = get_event_type(event_name)
        if event_type and event_type.parameters:
            # Check if it has sub_events parameter
            has_sub_events = any(
                isinstance(p, dict) and p.get("type") == "sub_events"
                for p in event_type.parameters
            )

            if has_sub_events:
                QMessageBox.information(
                    self,
                    self.tr("Cannot Add Action"),
                    self.tr("Cannot add actions directly to %1.\n\n"
                            "Please add actions to specific arrow keys instead:\n"
                            "Right-click on Left Arrow, Right Arrow, Up Arrow, or Down Arrow.")
                    )
                return

        # Special handling for if_condition action
        if action_name == "if_condition":
            from events.conditional_editor import ConditionalActionEditor
            dialog = ConditionalActionEditor(parent=self)
        else:
            # Show regular configuration dialog
            dialog = ActionConfigDialog(action_type, parent=self)

        if dialog.exec() == QDialog.Accepted:
            # Get configured parameters
            parameters = dialog.get_parameter_values()

            # Create action data
            action_data = {
                "action": action_name,
                "parameters": parameters
            }

            # Add to event
            if event_name not in self.current_events_data:
                self.current_events_data[event_name] = {"actions": []}

            # Ensure actions list exists
            if "actions" not in self.current_events_data[event_name]:
                self.current_events_data[event_name]["actions"] = []

            self.current_events_data[event_name]["actions"].append(action_data)

            self.refresh_events_display()
            self.events_modified.emit()

    def add_action_to_sub_event(self, event_name: str, key: str, action_name: str):
        """Add an action to a keyboard sub-event"""
        action_type = get_action_type(action_name)
        if not action_type:
            return

        # Special handling for if_condition action
        if action_name == "if_condition":
            from events.conditional_editor import ConditionalActionEditor
            dialog = ConditionalActionEditor(parent=self)
        else:
            # Show regular configuration dialog
            dialog = ActionConfigDialog(action_type, parent=self)

        if dialog.exec() == QDialog.Accepted:
            # Get configured parameters
            parameters = dialog.get_parameter_values()

            # Create action data
            action_data = {
                "action": action_name,
                "parameters": parameters
            }

            # Add to sub-event
            if event_name not in self.current_events_data:
                self.current_events_data[event_name] = {}
            if key not in self.current_events_data[event_name]:
                self.current_events_data[event_name][key] = {"actions": []}

            self.current_events_data[event_name][key]["actions"].append(action_data)

            self.refresh_events_display()
            self.events_modified.emit()

    def remove_sub_event(self, parent_item: QTreeWidgetItem, sub_item: QTreeWidgetItem):
        """Remove a keyboard sub-event"""
        event_name = parent_item.data(0, Qt.UserRole)
        sub_event_data = sub_item.data(0, Qt.UserRole)

        # The format is "{event_name}_{key}", so remove the event_name prefix
        if isinstance(sub_event_data, str) and sub_event_data.startswith(event_name + "_"):
            sub_event_key = sub_event_data[len(event_name) + 1:]  # Extract the key after "event_name_"
        else:
            sub_event_key = None

        if event_name and sub_event_key and event_name in self.current_events_data:
            if sub_event_key in self.current_events_data[event_name]:
                reply = QMessageBox.question(
                    self,
                    self.tr("Remove Key Event"),
                    self.tr("Are you sure you want to remove the {0} arrow key event and all its actions?").format(sub_event_key),
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    del self.current_events_data[event_name][sub_event_key]

                    # If no more sub-events, remove the parent event
                    if not self.current_events_data[event_name]:
                        del self.current_events_data[event_name]

                    self.refresh_events_display()
                    self.events_modified.emit()

    def edit_action(self, action_item: QTreeWidgetItem):
        """Edit an existing action"""
        action_data = action_item.data(0, Qt.UserRole)
        if not action_data:
            return

        action_type = get_action_type(action_data["action"])
        if not action_type:
            return

        # Special handling for if_condition action
        if action_data["action"] == "if_condition":
            from events.conditional_editor import ConditionalActionEditor
            dialog = ConditionalActionEditor(action_data.get("parameters", {}), parent=self)
        else:
            # Show regular configuration dialog with current parameters
            dialog = ActionConfigDialog(action_type, action_data.get("parameters", {}), parent=self)

        if dialog.exec() == QDialog.Accepted:
            # Update parameters
            action_data["parameters"] = dialog.get_parameter_values()

            self.refresh_events_display()
            self.events_modified.emit()

    def remove_action(self, action_item: QTreeWidgetItem):
        """Remove an action from an event"""
        parent_item = action_item.parent()
        if not parent_item:
            return

        # Check if this is a nested structure (keyboard sub-event)
        grandparent_item = parent_item.parent()

        if grandparent_item is not None:
            # This is a keyboard sub-event action: Keyboard → Left Arrow → Action
            main_event_name = grandparent_item.data(0, Qt.UserRole)  # "keyboard" or "keyboard_press"
            sub_event_data = parent_item.data(0, Qt.UserRole)        # "keyboard_left" or "keyboard_press_left"

            # Extract key by removing the event name prefix
            if isinstance(sub_event_data, str) and sub_event_data.startswith(main_event_name + "_"):
                sub_event_key = sub_event_data[len(main_event_name) + 1:]
            else:
                sub_event_key = None

            if sub_event_key:
                action_index = parent_item.indexOfChild(action_item)

                # Navigate to the correct data structure
                if (main_event_name in self.current_events_data and
                    sub_event_key in self.current_events_data[main_event_name] and
                    0 <= action_index < len(self.current_events_data[main_event_name][sub_event_key]["actions"])):

                    reply = QMessageBox.question(
                        self,
                        self.tr("Remove Action"),
                        self.tr("Are you sure you want to remove this action?"),
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        self.current_events_data[main_event_name][sub_event_key]["actions"].pop(action_index)
                        self.refresh_events_display()
                        self.events_modified.emit()
        else:
            # This is a direct event action: Create → Action
            event_name = parent_item.data(0, Qt.UserRole)
            action_index = parent_item.indexOfChild(action_item)

            if (event_name in self.current_events_data and
                "actions" in self.current_events_data[event_name] and
                0 <= action_index < len(self.current_events_data[event_name]["actions"])):

                reply = QMessageBox.question(
                    self,
                    self.tr("Remove Action"),
                    self.tr("Are you sure you want to remove this action?"),
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    self.current_events_data[event_name]["actions"].pop(action_index)
                    self.refresh_events_display()
                    self.events_modified.emit()

    def refresh_events_display(self):
        """Refresh the events tree display"""
        self.events_tree.clear()

        for event_name, event_data in self.current_events_data.items():

            # Handle collision events specially (both normal and NOT colliding)
            if event_name.startswith("collision_with_") or event_name.startswith("not_collision_with_"):
                is_negated = event_name.startswith("not_collision_with_")

                if is_negated:
                    target_object = event_name.replace("not_collision_with_", "")
                    event_item = QTreeWidgetItem(self.events_tree)
                    event_item.setText(0, self.tr(f"❌ NOT Colliding with {target_object}"))
                else:
                    target_object = event_name.replace("collision_with_", "")
                    event_item = QTreeWidgetItem(self.events_tree)
                    event_item.setText(0, self.tr(f"💥 Collision with {target_object}"))

                actions = event_data.get("actions", [])
                event_item.setText(1, self.tr("{0} actions").format(len(actions)))
                event_item.setData(0, Qt.UserRole, event_name)

                # Add action items
                for action_data in actions:
                    action_name = action_data.get("action", "unknown")
                    action_type = get_action_type(action_name)

                    action_item = QTreeWidgetItem(event_item)
                    if action_type:
                        action_item.setText(0, f"{action_type.icon} {action_type.display_name}")
                    else:
                        # Fallback display for unknown action types
                        action_item.setText(0, f"❓ {action_name}")

                    # Use smart parameter formatting
                    params = action_data.get("parameters", {})
                    if params:
                        param_summary = ActionParametersFormatter.format_action_parameters(
                            action_name, params
                        )
                        action_item.setText(1, param_summary)

                    action_item.setData(0, Qt.UserRole, action_data)

            # Handle keyboard events (keyboard, keyboard_press, keyboard_release)
            elif event_name in ["keyboard", "keyboard_press", "keyboard_release"] and isinstance(event_data, dict) and not event_data.get("actions"):
                event_type = get_event_type(event_name)
                if not event_type:
                    continue

                event_item = QTreeWidgetItem(self.events_tree)
                event_item.setText(0, f"{event_type.icon} {event_type.display_name}")
                event_item.setData(0, Qt.UserRole, event_name)

                total_actions = sum(len(sub_data.get("actions", [])) for key, sub_data in event_data.items() if key != "actions" and isinstance(sub_data, dict))
                event_item.setText(1, self.tr("{0} total actions").format(total_actions))

                # Icons for common keys
                key_icons = {
                    "left": "⬅️", "right": "➡️", "up": "⬆️", "down": "⬇️",
                    "LEFT": "⬅️", "RIGHT": "➡️", "UP": "⬆️", "DOWN": "⬇️",
                    "SPACE": "⎵", "ENTER": "↵", "ESCAPE": "⎋",
                    "W": "🅦", "A": "🅐", "S": "🅢", "D": "🅓"
                }

                for key, sub_data in event_data.items():
                    if key == "actions" or not isinstance(sub_data, dict):
                        continue

                    # Normalize key name: strip redundant prefix (press_down -> down)
                    display_key = key
                    if event_name == "keyboard_press" and key.startswith("press_"):
                        display_key = key[6:]  # Remove "press_"
                    elif event_name == "keyboard_release" and key.startswith("release_"):
                        display_key = key[8:]  # Remove "release_"

                    sub_item = QTreeWidgetItem(event_item)
                    icon = key_icons.get(display_key, "⌨️")

                    # Format key display name
                    if display_key in ["left", "right", "up", "down"]:
                        display_name = f"{display_key.title()} Arrow"
                    else:
                        display_name = f"Key {display_key}"

                    sub_item.setText(0, f"{icon} {display_name}")
                    sub_item.setText(1, self.tr("{0} actions").format(len(sub_data.get('actions', []))))
                    sub_item.setData(0, Qt.UserRole, f"{event_name}_{key}")

                    for action_data in sub_data.get("actions", []):
                        action_name = action_data.get("action", "unknown")
                        action_type = get_action_type(action_name)

                        action_item = QTreeWidgetItem(sub_item)
                        if action_type:
                            action_item.setText(0, f"  {action_type.icon} {action_type.display_name}")
                        else:
                            action_item.setText(0, f"  ❓ {action_name}")

                        # Use smart parameter formatting
                        params = action_data.get("parameters", {})
                        if params:
                            param_summary = ActionParametersFormatter.format_action_parameters(
                                action_name, params
                            )
                            action_item.setText(1, param_summary)

                        action_item.setData(0, Qt.UserRole, action_data)

            # Handle mouse events
            elif event_name.startswith("mouse_") and isinstance(event_data, dict):
                mouse_event_data = event_data.get("mouse_event", {})
                display_name = mouse_event_data.get("display_name", event_name)
                icon = mouse_event_data.get("icon", "🖱️")

                event_item = QTreeWidgetItem(self.events_tree)
                event_item.setText(0, f"{icon} {display_name}")
                event_item.setText(1, self.tr("{0} actions").format(len(event_data.get('actions', []))))
                event_item.setData(0, Qt.UserRole, event_name)

                # Add action items
                actions = event_data.get("actions", [])
                for action_data in actions:
                    action_name = action_data.get("action", "unknown")
                    action_type = get_action_type(action_name)

                    action_item = QTreeWidgetItem(event_item)
                    if action_type:
                        action_item.setText(0, f"{action_type.icon} {action_type.display_name}")
                    else:
                        action_item.setText(0, f"❓ {action_name}")

                    # Use smart parameter formatting
                    params = action_data.get("parameters", {})
                    if params:
                        param_summary = ActionParametersFormatter.format_action_parameters(
                            action_name, params
                        )
                        action_item.setText(1, param_summary)

                    action_item.setData(0, Qt.UserRole, action_data)

            else:
                # Regular events
                event_type = get_event_type(event_name)
                if not event_type:
                    continue

                event_item = QTreeWidgetItem(self.events_tree)
                event_item.setText(0, f"{event_type.icon} {event_type.display_name}")
                event_item.setText(1, f"{len(event_data.get('actions', []))} actions")
                event_item.setData(0, Qt.UserRole, event_name)

                actions = event_data.get("actions", [])
                for action_data in actions:
                    action_name = action_data.get("action", "unknown")
                    action_type = get_action_type(action_name)

                    action_item = QTreeWidgetItem(event_item)
                    if action_type:
                        action_item.setText(0, f"{action_type.icon} {action_type.display_name}")
                    else:
                        action_item.setText(0, f"❓ {action_name}")

                    # Use smart parameter formatting
                    params = action_data.get("parameters", {})
                    if params:
                        param_summary = ActionParametersFormatter.format_action_parameters(
                            action_name, params
                        )
                        action_item.setText(1, param_summary)

                    action_item.setData(0, Qt.UserRole, action_data)

        self.events_tree.collapseAll()

    def on_event_selected(self, item: QTreeWidgetItem):
        """Handle event selection"""
        # Enable/disable buttons based on selection
        if item and item.parent() is None:  # Event item
            self.remove_event_btn.setEnabled(True)
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            event_name = item.data(0, Qt.UserRole)
            if event_name:
                self.event_selected.emit(event_name)
        else:
            self.remove_event_btn.setEnabled(False)

            # Check if it's an action - enable move buttons
            if item:
                item_data = item.data(0, Qt.UserRole)
                is_action = isinstance(item_data, dict) and "action" in item_data

                if is_action and item.parent():
                    parent = item.parent()
                    index = parent.indexOfChild(item)
                    total = parent.childCount()

                    # Enable up if not at top
                    self.move_up_btn.setEnabled(index > 0)

                    # Enable down if not at bottom
                    self.move_down_btn.setEnabled(index < total - 1)
                else:
                    self.move_up_btn.setEnabled(False)
                    self.move_down_btn.setEnabled(False)
            else:
                self.move_up_btn.setEnabled(False)
                self.move_down_btn.setEnabled(False)

    def tree_drag_enter_event(self, event):
        """Handle drag enter event"""
        event.accept()

    def tree_drag_move_event(self, event):
        """Handle drag move event"""
        # Only allow dropping on action items or between actions
        target_item = self.events_tree.itemAt(event.position().toPoint())

        if target_item:
            # Get source item
            source_item = self.events_tree.currentItem()
            if not source_item:
                event.ignore()
                return

            # Check if source is an action
            source_data = source_item.data(0, Qt.UserRole)
            is_source_action = isinstance(source_data, dict) and "action" in source_data

            if not is_source_action:
                event.ignore()
                return

            # Check if source and target are in the same event/sub-event
            source_parent = source_item.parent()
            target_parent = target_item.parent()

            # Allow dropping on another action in the same parent
            target_data = target_item.data(0, Qt.UserRole)
            is_target_action = isinstance(target_data, dict) and "action" in target_data

            if is_target_action and source_parent == target_parent:
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def tree_drop_event(self, event):
        """Handle drop event - reorder actions"""
        source_item = self.events_tree.currentItem()
        target_item = self.events_tree.itemAt(event.position().toPoint())

        if not source_item or not target_item:
            event.ignore()
            return

        # Verify both are actions in the same parent
        source_data = source_item.data(0, Qt.UserRole)
        target_data = target_item.data(0, Qt.UserRole)

        is_source_action = isinstance(source_data, dict) and "action" in source_data
        is_target_action = isinstance(target_data, dict) and "action" in target_data

        if not (is_source_action and is_target_action):
            event.ignore()
            return

        source_parent = source_item.parent()
        target_parent = target_item.parent()

        if source_parent != target_parent:
            event.ignore()
            return

        # Get the event/sub-event path
        event_path = self.get_event_path(source_parent)
        if not event_path:
            event.ignore()
            return

        # Get action indices
        source_index = source_parent.indexOfChild(source_item)
        target_index = source_parent.indexOfChild(target_item)

        if source_index == target_index:
            event.ignore()
            return

        # Reorder in data structure
        self.reorder_action(event_path, source_index, target_index)

        event.accept()

    def get_event_path(self, item):
        """Get the path to an event or sub-event (e.g., ['create'] or ['keyboard', 'left'])"""
        if not item:
            return None

        path = []
        current = item

        while current:
            item_data = current.data(0, Qt.UserRole)

            if isinstance(item_data, str):
                # Check if this is a sub-event (format: "keyboard_left")
                if "_" in item_data and current.parent():
                    # Extract just the sub-event key
                    parent_data = current.parent().data(0, Qt.UserRole)
                    if isinstance(parent_data, str) and item_data.startswith(parent_data + "_"):
                        sub_key = item_data[len(parent_data) + 1:]
                        path.insert(0, sub_key)
                else:
                    # Regular event
                    path.insert(0, item_data)

            current = current.parent()

        return path if path else None

    def reorder_action(self, event_path, source_index, target_index):
        """Reorder action in the data structure"""
        if len(event_path) == 1:
            # Regular event (e.g., ['create'])
            event_name = event_path[0]

            if event_name in self.current_events_data:
                actions = self.current_events_data[event_name].get("actions", [])

                if 0 <= source_index < len(actions) and 0 <= target_index < len(actions):
                    # Remove from source
                    action = actions.pop(source_index)

                    # Insert at target (adjust index if moving down)
                    if source_index < target_index:
                        target_index -= 1

                    actions.insert(target_index, action)

                    logger.debug(f"Reordered action in {event_name}: {source_index} -> {target_index}")
                    self.refresh_events_display()
                    self.events_modified.emit()

        elif len(event_path) == 2:
            # Sub-event (e.g., ['keyboard', 'left'])
            event_name = event_path[0]
            sub_key = event_path[1]

            if (event_name in self.current_events_data and
                sub_key in self.current_events_data[event_name]):

                actions = self.current_events_data[event_name][sub_key].get("actions", [])

                if 0 <= source_index < len(actions) and 0 <= target_index < len(actions):
                    # Remove from source
                    action = actions.pop(source_index)

                    # Insert at target (adjust index if moving down)
                    if source_index < target_index:
                        target_index -= 1

                    actions.insert(target_index, action)

                    logger.debug(f"Reordered action in {event_name}/{sub_key}: {source_index} -> {target_index}")
                    self.refresh_events_display()
                    self.events_modified.emit()

    def move_action_up(self):
        """Move selected action up in the list"""
        current_item = self.events_tree.currentItem()
        if not current_item:
            return

        # Check if it's an action
        action_data = current_item.data(0, Qt.UserRole)
        if not isinstance(action_data, dict) or "action" not in action_data:
            return

        parent_item = current_item.parent()
        if not parent_item:
            return

        current_index = parent_item.indexOfChild(current_item)
        if current_index <= 0:
            return  # Already at top

        # Get event path BEFORE any modifications
        event_path = self.get_event_path(parent_item)
        if not event_path:
            return

        # Simple swap with item above
        target_index = current_index - 1
        self.swap_actions(event_path, current_index, target_index)

        # Re-select the moved item by finding the parent again after refresh
        self.reselect_action_after_move(event_path, target_index)

    def move_action_down(self):
        """Move selected action down in the list"""
        current_item = self.events_tree.currentItem()
        if not current_item:
            return

        # Check if it's an action
        action_data = current_item.data(0, Qt.UserRole)
        if not isinstance(action_data, dict) or "action" not in action_data:
            return

        parent_item = current_item.parent()
        if not parent_item:
            return

        current_index = parent_item.indexOfChild(current_item)
        if current_index >= parent_item.childCount() - 1:
            return  # Already at bottom

        # Get event path BEFORE any modifications
        event_path = self.get_event_path(parent_item)
        if not event_path:
            return

        # Simple swap with item below
        target_index = current_index + 1
        self.swap_actions(event_path, current_index, target_index)

        # Re-select the moved item by finding the parent again after refresh
        self.reselect_action_after_move(event_path, target_index)

    def swap_actions(self, event_path, index1, index2):
        """Swap two actions in the list - simpler than reorder"""
        if len(event_path) == 1:
            # Regular event (e.g., ['create'])
            event_name = event_path[0]

            if event_name in self.current_events_data:
                actions = self.current_events_data[event_name].get("actions", [])

                if 0 <= index1 < len(actions) and 0 <= index2 < len(actions):
                    # Simple swap
                    actions[index1], actions[index2] = actions[index2], actions[index1]

                    logger.debug(f"Swapped actions in {event_name}: {index1} <-> {index2}")
                    self.refresh_events_display()
                    self.events_modified.emit()

        elif len(event_path) == 2:
            # Sub-event (e.g., ['keyboard', 'left'])
            event_name = event_path[0]
            sub_key = event_path[1]

            if (event_name in self.current_events_data and
                sub_key in self.current_events_data[event_name]):

                actions = self.current_events_data[event_name][sub_key].get("actions", [])

                if 0 <= index1 < len(actions) and 0 <= index2 < len(actions):
                    # Simple swap
                    actions[index1], actions[index2] = actions[index2], actions[index1]

                    logger.debug(f"Swapped actions in {event_name}/{sub_key}: {index1} <-> {index2}")
                    self.refresh_events_display()
                    self.events_modified.emit()

    def reselect_action_after_move(self, event_path, action_index):
        """Re-select an action item after the tree has been refreshed"""
        if not event_path:
            return

        # Find the parent item based on the event path
        parent_item = None

        if len(event_path) == 1:
            # Regular event - find at top level
            event_name = event_path[0]
            for i in range(self.events_tree.topLevelItemCount()):
                item = self.events_tree.topLevelItem(i)
                if item.data(0, Qt.UserRole) == event_name:
                    parent_item = item
                    break

        elif len(event_path) == 2:
            # Sub-event - find the parent event, then the sub-event
            event_name = event_path[0]
            sub_key = event_path[1]

            # Find parent event
            for i in range(self.events_tree.topLevelItemCount()):
                item = self.events_tree.topLevelItem(i)
                if item.data(0, Qt.UserRole) == event_name:
                    # Found parent event, now find sub-event
                    for j in range(item.childCount()):
                        sub_item = item.child(j)
                        sub_data = sub_item.data(0, Qt.UserRole)
                        if isinstance(sub_data, str) and sub_data == f"{event_name}_{sub_key}":
                            parent_item = sub_item
                            break
                    break

        # Select the action at the specified index
        if parent_item and action_index < parent_item.childCount():
            action_item = parent_item.child(action_index)
            if action_item:
                self.events_tree.setCurrentItem(action_item)
                self.events_tree.scrollToItem(action_item)

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on tree items - expand/collapse or edit"""
        if not item:
            return

        # Get the item data
        item_data = item.data(0, Qt.UserRole)

        # Check if this is an action item (has dict data with "action" key)
        if isinstance(item_data, dict) and "action" in item_data:
            # This is an action - open the edit dialog
            self.edit_action(item)
            return

        # For events and sub-events (anything with children), toggle expand/collapse
        if item.childCount() > 0:
            is_expanded = item.isExpanded()
            item.setExpanded(not is_expanded)

            # Force a refresh to ensure the state sticks
            self.events_tree.viewport().update()

    def select_event(self, event_name: str):
        """Programmatically select an event"""
        for i in range(self.events_tree.topLevelItemCount()):
            item = self.events_tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == event_name:
                self.events_tree.setCurrentItem(item)
                self.on_event_selected(item)
                break

    def load_events_data(self, events_data: Dict[str, Any]):
        """Load events data into the panel"""
        logger.debug(f"ObjectEventsPanel: Loading events data with {len(events_data)} events")

        # Deep copy to avoid reference issues
        import copy
        self.current_events_data = copy.deepcopy(events_data)

        # Parse execute_code actions to extract proper Thymio actions
        self._parse_execute_code_actions()

        # Debug output
        for event_name, event_info in self.current_events_data.items():
            if isinstance(event_info, dict):
                action_count = len(event_info.get('actions', []))
                logger.debug(f"  - {event_name}: {action_count} actions")

        # Force refresh the display
        self.refresh_events_display()

        # Collapse all by default - only show event names, not actions
        self.events_tree.collapseAll()

        logger.debug(f"Events display refreshed, tree should now show {len(events_data)} events")

    def _parse_execute_code_actions(self):
        """Parse execute_code actions to extract proper action types (especially Thymio)"""
        parser = PythonToActionsParser()

        for event_name, event_info in self.current_events_data.items():
            if not isinstance(event_info, dict):
                continue

            actions = event_info.get('actions', [])
            if not actions:
                continue

            # Build new actions list, parsing execute_code actions
            new_actions = []
            for action in actions:
                action_name = action.get('action') or action.get('type', '')
                if action_name == 'execute_code':
                    code = action.get('parameters', {}).get('code', '')
                    if code and 'thymio.' in code:
                        # This execute_code contains Thymio code - parse it
                        try:
                            result = parser.parse_event_code(code, event_name)
                            parsed_actions = result.get('actions', [])
                            if parsed_actions:
                                # Check if we got meaningful actions (not just execute_code)
                                has_thymio_actions = any(
                                    (a.get('action', '') or a.get('type', '')).startswith('thymio_')
                                    for a in parsed_actions
                                )
                                if has_thymio_actions:
                                    logger.debug(f"Parsed execute_code in {event_name}: {len(parsed_actions)} actions")
                                    new_actions.extend(parsed_actions)
                                    continue
                        except Exception as e:
                            logger.warning(f"Failed to parse execute_code in {event_name}: {e}")
                    # Keep original execute_code if not Thymio code or parsing failed
                    new_actions.append(action)
                else:
                    # Keep non-execute_code actions as-is
                    new_actions.append(action)

            # Update the event's actions
            event_info['actions'] = new_actions

    def get_events_data(self) -> Dict[str, Any]:
        """Get current events data"""
        return self.current_events_data.copy()

    def apply_config(self, config):
        """Apply a Blockly configuration (for compatibility with object editor)"""
        # Store config for potential future use
        self.blockly_config = config
        logger.debug(f"ObjectEventsPanel: Applied config: {config.preset_name if hasattr(config, 'preset_name') else 'unknown'}")

    def get_available_objects(self):
        """Get list of available objects from the project"""
        # Walk up to find the main IDE window and get project data
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_data'):
                project_data = parent.current_project_data
                if project_data and 'assets' in project_data:
                    objects = project_data['assets'].get('objects', {})
                    return list(objects.keys())
                break
            parent = parent.parent()

        # Fallback: return some common object types
        return ["obj_wall", "obj_box", "obj_goal", "obj_player"]

    def add_collision_event(self, target_object: str):
        """Add a collision event for a specific object type with optional negation"""

        # Show dialog to ask if this is a "NOT colliding" check
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Collision Event Options"))
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(self.tr("<b>Collision with: {0}</b>").format(target_object)))
        layout.addSpacing(10)

        negate_checkbox = QCheckBox(self.tr("❌ NOT colliding (trigger when NOT touching)"))
        negate_checkbox.setToolTip(self.tr("Check this to trigger actions when the object is NOT colliding with the target"))
        layout.addWidget(negate_checkbox)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        negate = negate_checkbox.isChecked()

        # Create collision key based on negation
        if negate:
            collision_key = f"not_collision_with_{target_object}"
        else:
            collision_key = f"collision_with_{target_object}"

        # Check if this collision event already exists
        if collision_key in self.current_events_data:
            QMessageBox.information(
                self,
                self.tr("Collision Event Exists"),
                self.tr("This collision event already exists.")
            )
            return

        # Create new collision event
        self.current_events_data[collision_key] = {
            "actions": [],
            "target_object": target_object,
            "negate": negate
        }

        self.refresh_events_display()
        self.events_modified.emit()

    def add_action_to_collision_event(self, collision_event: str, action_name: str):
        """Add an action to a collision event"""
        action_type = get_action_type(action_name)

        if not action_type:
            return

        dialog = ActionConfigDialog(action_type, parent=self)

        if dialog.exec() == QDialog.Accepted:
            parameters = dialog.get_parameter_values()

            action_data = {
                "action": action_name,
                "parameters": parameters
            }

            # ADD THE ACTION TO THE EVENT
            if collision_event not in self.current_events_data:
                self.current_events_data[collision_event] = {"actions": []}

            self.current_events_data[collision_event]["actions"].append(action_data)

            # REFRESH THE DISPLAY
            self.refresh_events_display()
            self.events_modified.emit()

    def remove_collision_event(self, collision_event: str):
        """Remove a collision event"""
        if collision_event in self.current_events_data:
            target_object = collision_event.replace("collision_with_", "").replace("not_collision_with_", "")
            reply = QMessageBox.question(
                self,  # Parent widget - THIS IS THE FIX
                self.tr("Remove Collision Event"),
                self.tr("Are you sure you want to remove the collision event with {0}?").format(target_object),
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                del self.current_events_data[collision_event]
                self.refresh_events_display()
                self.events_modified.emit()

    def add_action_to_mouse_event(self, mouse_event: str, action_name: str):
        """Add an action to a mouse event"""
        action_type = get_action_type(action_name)

        if not action_type:
            return

        # Special handling for if_condition action
        if action_name == "if_condition":
            from events.conditional_editor import ConditionalActionEditor
            dialog = ConditionalActionEditor(parent=self)
        else:
            dialog = ActionConfigDialog(action_type, parent=self)

        if dialog.exec() == QDialog.Accepted:
            parameters = dialog.get_parameter_values()

            action_data = {
                "action": action_name,
                "parameters": parameters
            }

            # Add the action to the mouse event
            if mouse_event not in self.current_events_data:
                self.current_events_data[mouse_event] = {"actions": []}

            if "actions" not in self.current_events_data[mouse_event]:
                self.current_events_data[mouse_event]["actions"] = []

            self.current_events_data[mouse_event]["actions"].append(action_data)

            # Refresh display
            self.refresh_events_display()
            self.events_modified.emit()

    def remove_mouse_event(self, mouse_event: str):
        """Remove a mouse event"""
        if mouse_event in self.current_events_data:
            mouse_event_data = self.current_events_data[mouse_event].get("mouse_event", {})
            display_name = mouse_event_data.get("display_name", mouse_event)

            reply = QMessageBox.question(
                self,
                self.tr("Remove Mouse Event"),
                self.tr("Are you sure you want to remove the {0} event?").format(display_name),
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                del self.current_events_data[mouse_event]
                self.refresh_events_display()
                self.events_modified.emit()
