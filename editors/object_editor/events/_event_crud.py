#!/usr/bin/env python3
"""Event add/remove operations for :class:`ObjectEventsPanel`.

Extracted verbatim from ``_panel.py`` (``docs/POST_1_0_REFACTOR.md`` File 1,
cluster 3). Methods are unchanged -- this is a mixin, not free functions, so
``self`` and ``self.tr()`` (translation context "ObjectEventsPanel") keep
working exactly as before; sibling methods/attributes
(``refresh_events_display``, ``current_events_data``, ``events_modified`` …)
resolve on the concrete panel at runtime.
"""

from PySide6.QtWidgets import QMessageBox, QMenu, QDialog, QTreeWidgetItem
from PySide6.QtCore import Qt

from events.event_types import get_available_events
from events.thymio_events import THYMIO_EVENT_CATEGORIES, is_thymio_event


class EventCrudMixin:

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
        """Show menu to add new events, filtered by blockly_config"""
        menu = QMenu(self)

        available_events = get_available_events(self.blockly_config)

        # Hide Thymio events unless the project has at least one playground
        show_thymio = self.project_has_playgrounds()

        # Separate standard events from Thymio events
        standard_events = []
        thymio_events = []
        for event_type in available_events:
            if is_thymio_event(event_type.name):
                if show_thymio:
                    thymio_events.append(event_type)
            else:
                standard_events.append(event_type)

        # --- Standard events ---
        for event_type in standard_events:
            if event_type.name == "collision":
                # Special handling for collision events - create submenu
                collision_menu = menu.addMenu(self.tr("{0} Collision With...").format(event_type.icon))

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

            elif event_type.name == "keyboard_no_key":
                # No Key event - no key selector needed, stored under keyboard > nokey
                action = menu.addAction(f"{event_type.icon} {self.tr(event_type.display_name)}")
                action.triggered.connect(lambda checked: self.add_keyboard_no_key_event())

            elif event_type.name in ["keyboard", "keyboard_press", "keyboard_release"]:
                # New keyboard events with key selector
                action = menu.addAction(f"{event_type.icon} {self.tr(event_type.display_name)}...")
                action.triggered.connect(lambda checked, name=event_type.name: self.add_keyboard_event_with_selector(name))

            elif event_type.name == "mouse":
                # Mouse event with event selector
                action = menu.addAction(f"{event_type.icon} {self.tr(event_type.display_name)}...")
                action.triggered.connect(lambda checked: self.add_mouse_event_with_selector())

            elif event_type.name == "alarm":
                # Alarm event with alarm number selector (0-11)
                alarm_menu = menu.addMenu(f"{event_type.icon} {self.tr(event_type.display_name)}")
                for alarm_num in range(12):
                    alarm_action = alarm_menu.addAction(f"⏰ {self.tr('Alarm')} {alarm_num}")
                    alarm_action.triggered.connect(
                        lambda checked, n=alarm_num: self.add_alarm_event(n)
                    )

            elif event_type.parameters and isinstance(event_type.parameters, list):
                # Handle old-style keyboard events with sub_events
                has_sub_events = any(
                    isinstance(p, dict) and p.get("type") == "sub_events"
                    for p in event_type.parameters
                )

                if has_sub_events:
                    sub_menu = menu.addMenu(f"{event_type.icon} {self.tr(event_type.display_name)}")
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
                    action = menu.addAction(f"{event_type.icon} {self.tr(event_type.display_name)}")
                    action.triggered.connect(lambda checked, name=event_type.name: self.add_event(name))
            else:
                # Regular events
                action = menu.addAction(f"{event_type.icon} {self.tr(event_type.display_name)}")
                action.triggered.connect(lambda checked, name=event_type.name: self.add_event(name))

        # --- Thymio events submenu (only if any Thymio events are enabled) ---
        if thymio_events:
            menu.addSeparator()
            thymio_menu = menu.addMenu(self.tr("🤖 Thymio Events"))

            # Group enabled Thymio events by category
            thymio_by_category = {}
            for event_type in thymio_events:
                cat = event_type.category
                if cat not in thymio_by_category:
                    thymio_by_category[cat] = []
                thymio_by_category[cat].append(event_type)

            # Add category submenus in order
            sorted_categories = sorted(
                thymio_by_category.keys(),
                key=lambda c: THYMIO_EVENT_CATEGORIES.get(c, {}).get("order", 999)
            )
            for category in sorted_categories:
                cat_info = THYMIO_EVENT_CATEGORIES.get(category, {})
                cat_icon = cat_info.get("icon", "🤖")
                # Strip "Thymio " prefix for cleaner submenu names
                cat_label = category.replace("Thymio ", "")
                cat_submenu = thymio_menu.addMenu(f"{cat_icon} {self.tr(cat_label)}")

                for event_type in thymio_by_category[category]:
                    action = cat_submenu.addAction(
                        f"{event_type.icon} {self.tr(event_type.display_name)}"
                    )
                    action.triggered.connect(
                        lambda checked, name=event_type.name: self.add_event(name)
                    )

            # Visual selector at the bottom
            thymio_menu.addSeparator()
            visual_action = thymio_menu.addAction(self.tr("🤖 Visual Selector..."))
            visual_action.triggered.connect(self.add_thymio_event_with_selector)

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

    def add_keyboard_no_key_event(self):
        """Add the 'No Key' keyboard event (fires when no key is pressed)"""
        # Stored under keyboard > nokey for runtime compatibility
        if "keyboard" not in self.current_events_data:
            self.current_events_data["keyboard"] = {}

        if "nokey" in self.current_events_data["keyboard"]:
            QMessageBox.information(
                self,
                self.tr("Event Exists"),
                self.tr("The Keyboard <No Key> event already exists.")
            )
            return

        self.current_events_data["keyboard"]["nokey"] = {
            "actions": []
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

    def add_alarm_event(self, alarm_num: int):
        """Add an alarm event for a specific alarm number (0-11)"""
        alarm_key = f"alarm_{alarm_num}"

        # Initialize alarm event structure if it doesn't exist
        if "alarm" not in self.current_events_data:
            self.current_events_data["alarm"] = {}

        # Check if this specific alarm already exists
        if alarm_key in self.current_events_data["alarm"]:
            QMessageBox.information(
                self,
                self.tr("Alarm Event Exists"),
                self.tr("Alarm {0} event already exists.").format(alarm_num)
            )
            return

        # Create new alarm sub-event with empty actions list
        self.current_events_data["alarm"][alarm_key] = {
            "actions": []
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

    def remove_selected_event(self):
        """Remove the currently selected event"""
        current_item = self.events_tree.currentItem()
        if not current_item or current_item.parent() is not None:
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
