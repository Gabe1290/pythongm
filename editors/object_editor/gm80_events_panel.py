#!/usr/bin/env python3
"""
GameMaker 8.0 Events Panel
Displays events organized by GM8.0 categories with drag-and-drop action support
"""

from typing import Dict, List, Any
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
    get_event
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

from core.logger import get_logger
logger = get_logger(__name__)


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
    "event_other": {"categories": ["other"]},  # Other events (no_more_lives, no_more_health, etc.)

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


# ============================================================================
# BLOCKLY TO GM80 ACTION MAPPING
# ============================================================================

# Maps Blockly action block types to GM80 action names
# Key: Blockly block type, Value: list of GM80 action names it enables
BLOCKLY_TO_GM80_ACTION_MAPPING = {
    # Movement actions
    "move_set_hspeed": ["set_hspeed"],
    "move_set_vspeed": ["set_vspeed"],
    "move_stop": ["stop_movement"],
    "move_direction": ["start_moving_direction", "set_direction_speed"],
    "move_towards": ["move_towards_point"],
    "move_snap_to_grid": ["snap_to_grid"],
    "move_jump_to": ["jump_to_position", "jump_to_start", "jump_to_random"],
    "grid_stop_if_no_keys": ["stop_if_no_keys"],
    "grid_check_keys_and_move": ["check_keys_and_move"],
    "grid_if_on_grid": ["if_on_grid"],
    "set_gravity": ["set_gravity"],
    "set_friction": ["set_friction"],
    "reverse_horizontal": ["reverse_horizontal"],
    "reverse_vertical": ["reverse_vertical"],
    "bounce": ["bounce"],
    "wrap_around_room": ["wrap_around_room"],
    "move_to_contact": ["move_to_contact"],

    # Instance actions
    "instance_destroy": ["destroy_instance"],
    "instance_destroy_other": ["destroy_instance"],  # Same action with target="other"
    "instance_create": ["create_instance"],

    # Room actions
    "room_goto_next": ["next_room"],
    "room_goto_previous": ["previous_room"],
    "room_restart": ["restart_room"],
    "room_goto": ["goto_room"],
    "room_if_next_exists": ["if_next_room_exists"],
    "room_if_previous_exists": ["if_previous_room_exists"],

    # Score/Lives/Health actions (use relative=True for add)
    "score_set": ["set_score"],
    "score_add": ["set_score"],  # Same action with relative=True
    "lives_set": ["set_lives"],
    "lives_add": ["set_lives"],  # Same action with relative=True
    "health_set": ["set_health"],
    "health_add": ["set_health"],  # Same action with relative=True
    "draw_score": ["draw_score"],
    "draw_lives": ["draw_lives"],
    "draw_health_bar": ["draw_health_bar"],

    # Drawing actions
    "draw_text": ["draw_text"],
    "draw_rectangle": ["draw_rectangle"],
    "draw_circle": ["draw_circle"],
    "set_sprite": ["set_sprite"],
    "set_alpha": ["set_alpha"],

    # Timing actions
    "set_alarm": ["set_alarm"],

    # Sound actions (from plugins)
    "sound_play": ["play_sound"],
    "music_play": ["play_music"],
    "music_stop": ["stop_music"],

    # Output actions
    "output_message": ["display_message"],

    # Game control actions
    "game_end": ["end_game"],
    "game_restart": ["restart_game"],
    "show_highscore": ["show_highscore"],
    "clear_highscore": ["clear_highscore"],
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
        """Check if an event category is enabled based on Blockly configuration.

        A category is enabled if:
        1. A Blockly block directly enables the entire category, OR
        2. Any individual event in that category is enabled
        """
        # Check if a Blockly block directly enables this category
        for blockly_type, mapping in BLOCKLY_TO_GM80_MAPPING.items():
            if "categories" in mapping and category_id in mapping["categories"]:
                if self.blockly_config.is_block_enabled(blockly_type):
                    return True

        # Also check if any individual events in this category are enabled
        # This handles cases like keyboard where events are mapped individually
        events = get_events_by_category(category_id)
        for event in events:
            if self.is_individual_event_enabled(event.name, category_id):
                return True

        return False

    def is_individual_event_enabled(self, event_name: str, category_id: str) -> bool:
        """Check if a specific individual event is enabled (not category-wide)"""
        for blockly_type, mapping in BLOCKLY_TO_GM80_MAPPING.items():
            if "events" in mapping and event_name in mapping["events"]:
                if self.blockly_config.is_block_enabled(blockly_type):
                    return True
        return False

    def is_event_enabled(self, event_name: str, category_id: str) -> bool:
        """Check if a specific event is enabled based on Blockly configuration"""
        # First check if there's a direct category mapping that enables ALL events in category
        for blockly_type, mapping in BLOCKLY_TO_GM80_MAPPING.items():
            if "categories" in mapping and category_id in mapping["categories"]:
                if self.blockly_config.is_block_enabled(blockly_type):
                    return True

        # Then check if this specific event is individually enabled
        return self.is_individual_event_enabled(event_name, category_id)

    def reload_config(self):
        """Reload the Blockly configuration (call after config changes)"""
        self.blockly_config = load_config()

    def apply_config(self, config):
        """Apply a specific Blockly configuration directly (without loading from file)"""
        self.blockly_config = config
        logger.info(f"Events panel updated with config: {config.preset_name}")
        logger.debug(f"Enabled blocks: {len(config.enabled_blocks)} blocks")

    def is_action_enabled(self, action_name: str) -> bool:
        """Check if a GM80 action is enabled based on Blockly configuration"""
        # Check all Blockly block types to see if any enables this action
        for blockly_type, gm80_actions in BLOCKLY_TO_GM80_ACTION_MAPPING.items():
            if action_name in gm80_actions:
                if self.blockly_config.is_block_enabled(blockly_type):
                    return True
        # Action not in any mapping - not enabled
        return False

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

            # Track if any actions are available
            has_enabled_actions = False
            total_actions = 0
            filtered_actions = 0

            # Create submenus for each action tab (filtered by Blockly config)
            for tab_id, tab_info in get_action_tabs_ordered():
                # Get actions in this tab and filter by config
                actions = get_actions_by_tab(GM80_ALL_ACTIONS, tab_id)
                total_actions += len(actions)
                enabled_actions = [a for a in actions if self.is_action_enabled(a.name)]
                filtered_actions += len(enabled_actions)

                # Skip empty tabs
                if not enabled_actions:
                    continue

                has_enabled_actions = True
                tab_menu = add_action_menu.addMenu(f"{tab_info['icon']} {tab_info['name']}")

                for action in enabled_actions:
                    # Check if action is implemented
                    is_implemented = getattr(action, 'implemented', True)

                    if is_implemented:
                        action_item = tab_menu.addAction(f"{action.icon} {action.display_name}")
                        action_item.triggered.connect(
                            lambda checked, e=event_data, a=action: self.add_action_to_event(e, a.name)
                        )
                    else:
                        # Show unimplemented actions as grayed out with indicator
                        action_item = tab_menu.addAction(f"{action.icon} {action.display_name} (not implemented)")
                        action_item.setEnabled(False)

            logger.debug(f"Action filtering: {filtered_actions}/{total_actions} actions enabled")

            # Show warning if no actions are enabled
            if not has_enabled_actions:
                no_actions = add_action_menu.addAction(self.tr("⚠️ No actions enabled"))
                no_actions.setEnabled(False)

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

            # Handle keyboard events specially - they use nested structure
            # event_name might be "keyboard_UP" but data is stored as keyboard.UP
            # Check for patterns like: keyboard_UP, keyboard_press_LEFT, keyboard_release_SPACE
            for base_event in ["keyboard_release", "keyboard_press", "keyboard"]:
                if event_name.startswith(base_event + "_"):
                    key_name = event_name[len(base_event) + 1:]  # Get the key part
                    if key_name:  # Make sure there's actually a key name
                        # Add to nested structure
                        if base_event not in self.current_events_data:
                            self.current_events_data[base_event] = {}
                        if key_name not in self.current_events_data[base_event]:
                            self.current_events_data[base_event][key_name] = {"actions": []}
                        if "actions" not in self.current_events_data[base_event][key_name]:
                            self.current_events_data[base_event][key_name]["actions"] = []
                        self.current_events_data[base_event][key_name]["actions"].append(action_data)
                        self.refresh_display()
                        self.events_modified.emit()
                        return

            # Regular event handling
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
        """Remove an event or keyboard sub-event"""
        # Check if this is a keyboard sub-event (e.g., keyboard_UP, keyboard_press_LEFT)
        for base_event in ["keyboard_release", "keyboard_press", "keyboard"]:
            if event_name.startswith(base_event + "_"):
                key_name = event_name[len(base_event) + 1:]
                if key_name and base_event in self.current_events_data:
                    keyboard_data = self.current_events_data[base_event]
                    if isinstance(keyboard_data, dict) and key_name in keyboard_data:
                        reply = QMessageBox.question(self, self.tr("Remove Event"),
                            self.tr("Are you sure you want to remove the {0} {1} event?").format(base_event, key_name),
                            QMessageBox.Yes | QMessageBox.No)

                        if reply == QMessageBox.Yes:
                            del keyboard_data[key_name]
                            # If no more keys, remove the parent event too
                            remaining_keys = [k for k in keyboard_data.keys() if k != "actions"]
                            if not remaining_keys:
                                del self.current_events_data[base_event]
                            self.refresh_display()
                            self.events_modified.emit()
                        return

        # Regular event removal
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

                # Debug: log which keys were added
                if keys_added:
                    logger.debug(f"Added {len(keys_added)} keyboard keys to tree: {keys_added}")

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
                        action_name = action_data.get("action", "unknown") if isinstance(action_data, dict) else "unknown"
                        action_def = get_action_def(action_name)
                        if action_def:
                            action_item = QTreeWidgetItem(event_item)
                            action_item.setText(0, f"{action_def.icon} {action_def.display_name}")

                            # Format parameters
                            params = action_data.get("parameters", {})
                            if params:
                                param_str = ", ".join(f"{k}={v}" for k, v in params.items())
                                action_item.setText(1, param_str)

                            action_item.setData(0, Qt.UserRole, action_data)

        # Expand all items by default so actions are visible
        self.events_tree.expandAll()

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
            "Tools → Configure Events & Actions\n\n"
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
