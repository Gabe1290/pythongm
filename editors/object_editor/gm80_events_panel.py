#!/usr/bin/env python3
"""
GameMaker 8.0 Events Panel
Displays events organized by GM8.0 categories with drag-and-drop action support
"""

from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QMenu, QMessageBox, QDialog, QLabel
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

# Import GM8.0 event and action systems
from events.gm80_events import (
    get_event_categories_ordered,
    get_events_by_category,
    get_event,
    GM80_EVENT_CATEGORIES
)
from actions import (
    get_action_tabs_ordered,
    get_actions_by_tab,
    get_action,
    GM80_ALL_ACTIONS
)

# Create convenience wrapper for get_action with GM80_ALL_ACTIONS pre-bound
def get_action_def(action_name: str):
    """Get action definition by name from GM80_ALL_ACTIONS"""
    return get_action(GM80_ALL_ACTIONS, action_name)

# Import Blockly configuration for filtering
from config.blockly_config import load_config


# ============================================================================
# BLOCKLY TO GM80 EVENT MAPPING
# ============================================================================

# Maps Blockly event block types to GM80 event categories/names
BLOCKLY_TO_GM80_MAPPING = {
    # Direct category mappings
    "event_create": {"categories": ["create"]},
    "event_destroy": {"categories": ["destroy"]},
    "event_draw": {"categories": ["draw"]},
    "event_collision": {"categories": ["collision"]},
    "event_alarm": {"categories": ["alarm"]},
    
    # Step events - includes begin_step, step, end_step
    "event_step": {"categories": ["step"]},
    
    # Keyboard events
    "event_keyboard_nokey": {"events": ["keyboard_no_key"]},
    "event_keyboard_anykey": {"events": ["keyboard_any_key"]},
    "event_keyboard_held": {"events": ["keyboard"]},
    "event_keyboard_press": {"events": ["keyboard_press"]},
    "event_keyboard_release": {"events": ["keyboard_release"]},
    
    # Mouse events - entire category
    "event_mouse": {"categories": ["mouse"]},
}


class GM80EventsPanel(QWidget):
    """GameMaker 8.0 style events panel with organized categories"""

    events_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_events_data = {}
        
        # Load Blockly configuration for event filtering
        self.blockly_config = load_config()
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the GM8.0 events UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel(self.tr("Object Events"))
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Events tree
        self.events_tree = QTreeWidget()
        self.events_tree.setHeaderLabels([self.tr("Event"), self.tr("Actions")])
        self.events_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.events_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.events_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.events_tree.itemClicked.connect(self.on_item_clicked)  # Handle single-click
        self.events_tree.itemSelectionChanged.connect(self.on_selection_changed)  # Handle selection changes

        # IMPORTANT: Set tree to expand items by default
        self.events_tree.setItemsExpandable(True)
        self.events_tree.setExpandsOnDoubleClick(True)

        # Disable auto-collapse behavior
        self.events_tree.setAnimated(False)  # Disable animations that might collapse items

        # Configure header for 55-45 split (Event column slightly wider)
        header = self.events_tree.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, header.ResizeMode.Interactive)  # Event column resizable

        # Set initial column width after widget is shown
        def set_initial_widths():
            total_width = self.events_tree.viewport().width()
            self.events_tree.setColumnWidth(0, int(total_width * 0.55))

        QTimer.singleShot(100, set_initial_widths)

        # Maintain proportions on resize
        def on_resize(event):
            QTreeWidget.resizeEvent(self.events_tree, event)
            viewport_width = self.events_tree.viewport().width()
            self.events_tree.setColumnWidth(0, int(viewport_width * 0.55))

        self.events_tree.resizeEvent = on_resize

        layout.addWidget(self.events_tree)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_event_btn = QPushButton(self.tr("+ Add Event"))
        self.add_event_btn.clicked.connect(self.show_add_event_menu)
        button_layout.addWidget(self.add_event_btn)

        self.remove_event_btn = QPushButton(self.tr("- Remove Event"))
        self.remove_event_btn.clicked.connect(self.remove_selected_event)
        self.remove_event_btn.setEnabled(False)
        button_layout.addWidget(self.remove_event_btn)

        layout.addLayout(button_layout)

    def is_event_category_enabled(self, category_id: str) -> bool:
        """Check if an event category is enabled based on Blockly configuration"""
        # Find which Blockly blocks enable this category
        for blockly_type, mapping in BLOCKLY_TO_GM80_MAPPING.items():
            if "categories" in mapping and category_id in mapping["categories"]:
                if self.blockly_config.is_block_enabled(blockly_type):
                    return True
        return False
    
    def is_event_enabled(self, event_name: str, category_id: str) -> bool:
        """Check if a specific event is enabled based on Blockly configuration"""
        # Check if entire category is enabled
        if self.is_event_category_enabled(category_id):
            return True
        
        # Check specific event mappings
        for blockly_type, mapping in BLOCKLY_TO_GM80_MAPPING.items():
            if "events" in mapping and event_name in mapping["events"]:
                if self.blockly_config.is_block_enabled(blockly_type):
                    return True
        
        return False
    
    def reload_config(self):
        """Reload the Blockly configuration (call after config changes)"""
        self.blockly_config = load_config()

    def show_add_event_menu(self):
        """Show organized event menu by GM8.0 categories (filtered by Blockly config)"""
        menu = QMenu(self)
        
        # Track if any events are available
        has_enabled_events = False

        # Get event categories in order
        for category_id, category_info in get_event_categories_ordered():
            # Skip category if not enabled
            if not self.is_event_category_enabled(category_id):
                continue
            
            has_enabled_events = True
            category_menu = menu.addMenu(f"{category_info['icon']} {category_info['name']}")

            # Get events in this category
            events = get_events_by_category(category_id)

            for event in events:
                # Check if this specific event is enabled
                if not self.is_event_enabled(event.name, category_id):
                    continue
                
                # Special handling for dynamic events
                if category_id == "collision":
                    self.add_collision_submenu(category_menu)
                    break
                elif category_id == "keyboard":
                    self.add_keyboard_submenu(category_menu, event)
                    break
                else:
                    # Regular event
                    action = category_menu.addAction(f"{event.icon} {event.display_name}")
                    action.triggered.connect(
                        lambda checked, e=event: self.add_event(e.name)
                    )
        
        # Show warning if no events are enabled
        if not has_enabled_events:
            no_events = menu.addAction(self.tr("⚠️ No events enabled"))
            no_events.setEnabled(False)
            menu.addSeparator()
            help_action = menu.addAction(self.tr("Configure enabled events..."))
            help_action.triggered.connect(self.show_config_help)

        menu.exec(self.add_event_btn.mapToGlobal(self.add_event_btn.rect().bottomLeft()))

    def add_collision_submenu(self, parent_menu):
        """Add collision events submenu"""
        # Get available objects from project
        objects = self.get_available_objects()

        if objects:
            for obj_name in objects:
                action = parent_menu.addAction(f"📦 {obj_name}")
                action.triggered.connect(
                    lambda checked, obj=obj_name: self.add_collision_event(obj)
                )
        else:
            no_obj = parent_menu.addAction(self.tr("No objects available"))
            no_obj.setEnabled(False)

    def add_keyboard_submenu(self, parent_menu, event):
        """Add keyboard event with key selector (filtered by Blockly config)"""
        for event_def in get_events_by_category("keyboard"):
            # Check if this specific keyboard event is enabled
            if not self.is_event_enabled(event_def.name, "keyboard"):
                continue
            
            # Check if this event requires a key selector (has parameters)
            needs_key_selector = event_def.parameters and any(
                p.get("type") == "key_selector" for p in event_def.parameters
            )

            if needs_key_selector:
                # Events that need key selection: add "..." and open dialog
                action = parent_menu.addAction(f"{event_def.icon} {event_def.display_name}...")
                action.triggered.connect(
                    lambda checked, e=event_def: self.add_keyboard_event_with_dialog(e.name)
                )
            else:
                # Direct events (No Key, Any Key): no "..." and add directly
                action = parent_menu.addAction(f"{event_def.icon} {event_def.display_name}")
                action.triggered.connect(
                    lambda checked, e=event_def: self.add_direct_keyboard_event(e.name)
                )

    def add_event(self, event_name: str):
        """Add a simple event"""
        if event_name in self.current_events_data:
            QMessageBox.information(self, self.tr("Event Exists"),
                self.tr("The {0} event already exists.").format(event_name))
            return

        self.current_events_data[event_name] = {"actions": []}
        self.refresh_display()
        self.events_modified.emit()

    def add_direct_keyboard_event(self, event_name: str):
        """Add a direct keyboard event (No Key, Any Key) without key selector"""
        # These events use the "keyboard" parent with a special subtype
        # e.g., keyboard_no_key -> keyboard.nokey, keyboard_any_key -> keyboard.anykey
        if event_name == "keyboard_no_key":
            parent_event = "keyboard"
            subtype = "nokey"
        elif event_name == "keyboard_any_key":
            parent_event = "keyboard"
            subtype = "anykey"
        else:
            # Fallback - just add as a simple event
            self.add_event(event_name)
            return

        # Create nested structure like other keyboard events
        if parent_event not in self.current_events_data:
            self.current_events_data[parent_event] = {}

        if subtype in self.current_events_data[parent_event]:
            QMessageBox.information(self, self.tr("Event Exists"),
                self.tr("The {0} event already exists.").format(event_name))
            return

        self.current_events_data[parent_event][subtype] = {"actions": []}
        self.refresh_display()
        self.events_modified.emit()

    def add_collision_event(self, target_object: str):
        """Add collision event for specific object"""
        event_key = f"collision_with_{target_object}"

        if event_key in self.current_events_data:
            QMessageBox.information(self, self.tr("Event Exists"),
                self.tr("This collision event already exists."))
            return

        self.current_events_data[event_key] = {
            "actions": [],
            "target_object": target_object
        }
        self.refresh_display()
        self.events_modified.emit()

    def add_keyboard_event_with_dialog(self, event_name: str):
        """Add keyboard event using key selector dialog"""
        from dialogs.key_selector_dialog import KeySelectorDialog

        dialog = KeySelectorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            selected_key = dialog.get_selected_key()

            if selected_key:
                event_key = f"{event_name}_{selected_key}"

                if event_name not in self.current_events_data:
                    self.current_events_data[event_name] = {}

                if selected_key in self.current_events_data[event_name]:
                    QMessageBox.information(self, self.tr("Event Exists"),
                        self.tr("The {0} key event already exists.").format(selected_key))
                    return

                self.current_events_data[event_name][selected_key] = {"actions": []}
                self.refresh_display()
                self.events_modified.emit()

    def show_context_menu(self, position):
        """Show context menu for adding actions"""
        item = self.events_tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        # Determine item type
        event_data = item.data(0, Qt.UserRole)

        if isinstance(event_data, str):
            # This is an event item
            add_action_menu = menu.addMenu(self.tr("Add Action"))

            # Create submenus for each action tab
            for tab_id, tab_info in get_action_tabs_ordered():
                tab_menu = add_action_menu.addMenu(f"{tab_info['icon']} {tab_info['name']}")

                # Get actions in this tab
                actions = get_actions_by_tab(GM80_ALL_ACTIONS, tab_id)

                for action in actions:
                    action_item = tab_menu.addAction(f"{action.icon} {action.display_name}")
                    action_item.triggered.connect(
                        lambda checked, e=event_data, a=action: self.add_action_to_event(e, a.name)
                    )

            menu.addSeparator()
            remove_action = menu.addAction(self.tr("Remove Event"))
            remove_action.triggered.connect(lambda: self.remove_event(event_data))

        elif isinstance(event_data, dict) and "action" in event_data:
            # This is an action item
            edit_action = menu.addAction(self.tr("Edit Action"))
            edit_action.triggered.connect(lambda: self.edit_action(item))

            menu.addSeparator()

            # Move up/down options
            move_up_action = menu.addAction(self.tr("Move Up"))
            move_up_action.triggered.connect(lambda: self.move_action(item, -1))

            move_down_action = menu.addAction(self.tr("Move Down"))
            move_down_action.triggered.connect(lambda: self.move_action(item, 1))

            # Enable/disable based on position
            parent_item = item.parent()
            if parent_item:
                action_index = parent_item.indexOfChild(item)
                move_up_action.setEnabled(action_index > 0)
                move_down_action.setEnabled(action_index < parent_item.childCount() - 1)

            menu.addSeparator()

            remove_action = menu.addAction(self.tr("Remove Action"))
            remove_action.triggered.connect(lambda: self.remove_action(item))

        menu.exec(self.events_tree.mapToGlobal(position))

    def add_action_to_event(self, event_name: str, action_name: str):
        """Add action to an event"""
        from editors.object_editor.gm80_action_dialog import GM80ActionDialog

        action_def = get_action_def(action_name)
        if not action_def:
            return

        dialog = GM80ActionDialog(action_def, parent=self)
        if dialog.exec() == QDialog.Accepted:
            parameters = dialog.get_parameter_values()

            action_data = {
                "action": action_name,
                "parameters": parameters
            }

            # Add to event
            if event_name not in self.current_events_data:
                self.current_events_data[event_name] = {"actions": []}

            if "actions" not in self.current_events_data[event_name]:
                self.current_events_data[event_name]["actions"] = []

            self.current_events_data[event_name]["actions"].append(action_data)
            self.refresh_display()
            self.events_modified.emit()

    def edit_action(self, action_item: QTreeWidgetItem):
        """Edit an existing action"""
        from editors.object_editor.gm80_action_dialog import GM80ActionDialog

        action_data = action_item.data(0, Qt.UserRole)
        if not action_data:
            return

        action_def = get_action_def(action_data["action"])
        if not action_def:
            return

        # Get the parent event to find the actual action in current_events_data
        parent_item = action_item.parent()
        if not parent_item:
            return

        event_name = parent_item.data(0, Qt.UserRole)
        action_index = parent_item.indexOfChild(action_item)

        # Get the actual actions list from current_events_data
        actions_list = self._get_actions_list_for_event(event_name)
        if actions_list is None or action_index < 0 or action_index >= len(actions_list):
            return

        # Get the actual action data from the list (not the copy from tree widget)
        actual_action_data = actions_list[action_index]

        dialog = GM80ActionDialog(action_def, actual_action_data.get("parameters", {}), parent=self)
        if dialog.exec() == QDialog.Accepted:
            # Update the actual action data in current_events_data
            actual_action_data["parameters"] = dialog.get_parameter_values()
            self.refresh_display()
            self.events_modified.emit()

    def remove_action(self, action_item: QTreeWidgetItem):
        """Remove an action"""
        parent_item = action_item.parent()
        if not parent_item:
            return

        event_name = parent_item.data(0, Qt.UserRole)
        action_index = parent_item.indexOfChild(action_item)

        # Get the actions list for this event (handles nested keyboard events)
        actions = self._get_actions_list_for_event(event_name)
        if actions is not None and 0 <= action_index < len(actions):
            reply = QMessageBox.question(self, self.tr("Remove Action"),
                self.tr("Are you sure you want to remove this action?"),
                QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                actions.pop(action_index)
                self.refresh_display()
                self.events_modified.emit()

    def move_action(self, action_item: QTreeWidgetItem, direction: int):
        """Move an action up (-1) or down (+1) in the list"""
        parent_item = action_item.parent()
        if not parent_item:
            return

        event_name = parent_item.data(0, Qt.UserRole)
        action_index = parent_item.indexOfChild(action_item)

        # Get the actions list for this event
        actions = self._get_actions_list_for_event(event_name)
        if actions is None:
            return

        new_index = action_index + direction

        # Check bounds
        if new_index < 0 or new_index >= len(actions):
            return

        # Swap the actions
        actions[action_index], actions[new_index] = actions[new_index], actions[action_index]

        # Refresh display and emit signal
        self.refresh_display()
        self.events_modified.emit()

    def _get_actions_list_for_event(self, event_name: str):
        """Get the actions list for an event, handling nested keyboard events"""
        # Check if it's a nested keyboard event (e.g., "keyboard_right", "keyboard_press_up")
        if "_" in event_name:
            parts = event_name.rsplit("_", 1)
            if len(parts) == 2:
                parent_event, key_name = parts
                # Check for keyboard events with nested structure
                if parent_event in ["keyboard", "keyboard_press", "keyboard_release"]:
                    if parent_event in self.current_events_data:
                        key_data = self.current_events_data[parent_event].get(key_name, {})
                        if isinstance(key_data, dict) and "actions" in key_data:
                            return key_data["actions"]

        # Regular event
        if event_name in self.current_events_data:
            return self.current_events_data[event_name].get("actions", [])

        return None

    def remove_event(self, event_name: str):
        """Remove an event"""
        if event_name in self.current_events_data:
            reply = QMessageBox.question(self, self.tr("Remove Event"),
                self.tr("Are you sure you want to remove the {0} event?").format(event_name),
                QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                del self.current_events_data[event_name]
                self.refresh_display()
                self.events_modified.emit()

    def remove_selected_event(self):
        """Remove currently selected event"""
        current_item = self.events_tree.currentItem()
        if not current_item or current_item.parent() is not None:
            return

        event_name = current_item.data(0, Qt.UserRole)
        if event_name:
            self.remove_event(event_name)

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle single-click - toggle expand/collapse for events and enable/disable remove button"""
        if not item:
            self.remove_event_btn.setEnabled(False)
            return

        # Check if this is an event item (has event_name in data)
        item_data = item.data(0, Qt.UserRole)
        is_event_item = isinstance(item_data, str) and not item_data.startswith("action:")

        # Also check parent - if clicking on an action, the parent is the event
        if not is_event_item and item.parent():
            parent_data = item.parent().data(0, Qt.UserRole)
            is_event_item = isinstance(parent_data, str) and not parent_data.startswith("action:")

        # Enable remove button if an event (or action within event) is selected
        self.remove_event_btn.setEnabled(is_event_item or (item.parent() is not None))

        # Only toggle expand/collapse if this is an event item (has children)
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())

    def on_selection_changed(self):
        """Handle selection changes - enable/disable remove button"""
        selected_items = self.events_tree.selectedItems()
        if not selected_items:
            self.remove_event_btn.setEnabled(False)
            return

        item = selected_items[0]
        item_data = item.data(0, Qt.UserRole)

        # Check if this is an event item (string data that's not an action)
        is_event_item = isinstance(item_data, str) and not item_data.startswith("action:")

        # Also enable if an action is selected (can remove parent event)
        has_parent_event = item.parent() is not None

        self.remove_event_btn.setEnabled(is_event_item or has_parent_event)

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click - edit actions"""
        if not item:
            return

        item_data = item.data(0, Qt.UserRole)

        if isinstance(item_data, dict) and "action" in item_data:
            # Edit action
            self.edit_action(item)

    def refresh_display(self):
        """Refresh the events tree display"""
        self.events_tree.clear()

        for event_name, event_data in self.current_events_data.items():
            # IMPORTANT: Check keyboard events FIRST before regular events
            # because keyboard events have nested structure but also have event definitions
            if event_name in ["keyboard", "keyboard_press", "keyboard_release"]:
                # Keyboard event with nested key data
                # Format: {"keyboard": {"right": {"actions": [...]}, "left": {"actions": [...]}}}

                # Create parent keyboard event
                icon = "⌨️"
                event_type_name = event_name.replace("_", " ").title()
                parent_event = QTreeWidgetItem(self.events_tree)
                parent_event.setText(0, f"{icon} {event_type_name}")

                # Count total keys
                key_count = sum(1 for k, v in event_data.items()
                               if isinstance(v, dict) and 'actions' in v)
                parent_event.setText(1, self.tr("{0} keys").format(key_count))
                parent_event.setData(0, Qt.UserRole, event_name)
                parent_event.setExpanded(True)  # Expand parent by default

                # Add child items for each key
                keys_added = []  # Track which keys we add for debugging
                for key_name, key_data in event_data.items():
                    if key_name == "actions":
                        # Old format - direct actions under event
                        continue

                    if isinstance(key_data, dict) and 'actions' in key_data:
                        # Create child item for this specific key
                        key_item = QTreeWidgetItem(parent_event)
                        key_item.setText(0, f"  {key_name}")
                        key_item.setText(1, self.tr("{0} actions").format(len(key_data.get('actions', []))))
                        key_item.setData(0, Qt.UserRole, f"{event_name}_{key_name}")
                        key_item.setExpanded(True)  # Expand key by default
                        keys_added.append(key_name)

                        # Add actions under the key
                        for action_data in key_data.get("actions", []):
                            action_def = get_action_def(action_data["action"])
                            if action_def:
                                action_item = QTreeWidgetItem(key_item)
                                action_item.setText(0, f"{action_def.icon} {action_def.display_name}")

                                # Format parameters
                                params = action_data.get("parameters", {})
                                if params:
                                    param_str = ", ".join(f"{k}={v}" for k, v in params.items())
                                    action_item.setText(1, param_str)

                                action_item.setData(0, Qt.UserRole, action_data)

                # Debug: print which keys were added
                if keys_added:
                    print(f"DEBUG: Added {len(keys_added)} keyboard keys to tree: {keys_added}")

            elif event_name.startswith("collision_with_"):
                # Collision event
                target = event_name.replace("collision_with_", "")
                event_item = QTreeWidgetItem(self.events_tree)
                event_item.setText(0, self.tr("💥 Collision with {0}").format(target))
                event_item.setText(1, self.tr("{0} actions").format(len(event_data.get('actions', []))))
                event_item.setData(0, Qt.UserRole, event_name)
                event_item.setExpanded(True)  # Expand immediately

                # Add actions
                for action_data in event_data.get("actions", []):
                    action_def = get_action_def(action_data["action"])
                    if action_def:
                        action_item = QTreeWidgetItem(event_item)
                        action_item.setText(0, f"{action_def.icon} {action_def.display_name}")

                        # Format parameters
                        params = action_data.get("parameters", {})
                        if params:
                            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
                            action_item.setText(1, param_str)

                        action_item.setData(0, Qt.UserRole, action_data)

            else:
                # Regular event (fallback)
                event_def = get_event(event_name)
                if event_def:
                    event_item = QTreeWidgetItem(self.events_tree)
                    event_item.setText(0, f"{event_def.icon} {event_def.display_name}")
                    event_item.setText(1, self.tr("{0} actions").format(len(event_data.get('actions', []))))
                    event_item.setData(0, Qt.UserRole, event_name)
                    event_item.setExpanded(True)  # Expand immediately

                    # Add actions
                    for action_data in event_data.get("actions", []):
                        action_def = get_action_def(action_data["action"])
                        if action_def:
                            action_item = QTreeWidgetItem(event_item)
                            action_item.setText(0, f"{action_def.icon} {action_def.display_name}")

                            # Format parameters
                            params = action_data.get("parameters", {})
                            if params:
                                param_str = ", ".join(f"{k}={v}" for k, v in params.items())
                                action_item.setText(1, param_str)

                            action_item.setData(0, Qt.UserRole, action_data)

        # Collapse all items by default
        self.events_tree.collapseAll()

    def load_events_data(self, events_data: Dict[str, Any]):
        """Load events data"""
        import copy
        self.current_events_data = copy.deepcopy(events_data)
        self.refresh_display()

    def get_events_data(self) -> Dict[str, Any]:
        """Get current events data"""
        return self.current_events_data.copy()
    
    def show_config_help(self):
        """Show help dialog about configuring enabled events"""
        QMessageBox.information(
            self,
            self.tr("Configure Events"),
            self.tr("To enable/disable events, go to:\n\n"
            "Tools → Configure Blockly Blocks\n\n"
            "Select which events you want available in both the\n"
            "visual programming editor and this traditional event editor.\n\n"
            "Changes will take effect immediately.")
        )

    def get_available_objects(self) -> List[str]:
        """Get list of available objects from project"""
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
