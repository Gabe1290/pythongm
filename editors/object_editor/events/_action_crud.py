#!/usr/bin/env python3
"""Action add/edit/remove operations for :class:`ObjectEventsPanel`.

Extracted verbatim from ``_panel.py`` (``docs/POST_1_0_REFACTOR.md`` File 1,
cluster 4). A mixin, so ``self`` / ``self.tr()`` / sibling members
(``refresh_events_display``, ``current_events_data``, ``_CONTAINER_EVENT_HINTS`` …)
resolve on the concrete panel unchanged.

``get_action_type`` here is the alias-aware wrapper from ``_action_lookup``;
tests stubbing action resolution for ``edit_action`` should patch
``editors.object_editor.events._action_crud.get_action_type`` (and, for the
render path, ``..._action_lookup.get_action_type``).
"""

from PySide6.QtWidgets import QMessageBox, QDialog, QTreeWidgetItem
from PySide6.QtCore import Qt

from events.event_types import get_event_type
from events.conditional_editor import create_action_dialog
from core.logger import get_logger

from ._action_lookup import get_action_type

logger = get_logger(__name__)


class ActionCrudMixin:

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

    def add_action_to_event(self, event_name: str, action_name: str):
        """Add an action to an event"""
        action_type = get_action_type(action_name)
        if not action_type:
            return

        # Reject container events early (alarm, keyboard, keyboard_press,
        # keyboard_release). Without this, the action lands at
        # current_events_data[event_name]["actions"] as a sibling of the
        # sub-keys — see _CONTAINER_EVENT_HINTS docstring for why.
        if event_name in self._CONTAINER_EVENT_HINTS:
            QMessageBox.information(
                self,
                self.tr("Cannot Add Action"),
                self.tr("Cannot add actions directly to '{0}'.\n\n"
                        "Right-click on {1} and add the action there instead.").format(
                    event_name, self.tr(self._CONTAINER_EVENT_HINTS[event_name])
                )
            )
            return

        # Forward-compat: some event types may declare sub_events via a
        # type-parameter rather than by literal name. Kept after the
        # explicit name check above so the targeted error message wins
        # when both would fire.
        event_type = get_event_type(event_name)
        if event_type and event_type.parameters:
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

        dialog = create_action_dialog(action_type, parent=self)

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

        dialog = create_action_dialog(action_type, parent=self)

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

    def edit_action(self, action_item: QTreeWidgetItem):
        """Edit an existing action"""
        action_data = action_item.data(0, Qt.UserRole)
        if not action_data:
            return

        if not isinstance(action_data, dict) or "action" not in action_data:
            return

        action_type = get_action_type(action_data["action"])
        if not action_type:
            logger.warning(f"Unknown action type: {action_data['action']}")
            from events.plugin_loader import extension_for_action
            owner = extension_for_action(action_data["action"])
            if owner:
                message = self.tr(
                    "This action needs the '{0}' extension, which is "
                    "currently disabled, so it can't be edited here.\n\n"
                    "The action itself is unaffected and will be kept "
                    "exactly as-is when you save."
                ).format(owner["name"])
            else:
                message = self.tr(
                    "This action ('{0}') needs an extension that isn't "
                    "installed in this copy of PyGameMaker, so it can't be "
                    "edited here.\n\n"
                    "The action itself is unaffected and will be kept "
                    "exactly as-is when you save."
                ).format(action_data["action"])
            QMessageBox.information(self, self.tr("Extension Action"), message)
            return

        try:
            dialog = create_action_dialog(action_type, action_data.get("parameters", {}), parent=self)
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, self.tr("Error"), self.tr("Could not open action editor: {0}").format(str(e)))
            return

        if dialog.exec() == QDialog.Accepted:
            new_params = dialog.get_parameter_values()

            # Locate the action in self.current_events_data (not the tree copy)
            parent_item = action_item.parent()
            if not parent_item:
                return

            grandparent_item = parent_item.parent()
            action_index = parent_item.indexOfChild(action_item)

            if grandparent_item is not None:
                # Nested structure (keyboard sub-event): Grandparent → Parent → Action
                main_event_name = grandparent_item.data(0, Qt.UserRole)
                sub_event_data = parent_item.data(0, Qt.UserRole)

                if isinstance(sub_event_data, str) and sub_event_data.startswith(main_event_name + "_"):
                    sub_event_key = sub_event_data[len(main_event_name) + 1:]
                else:
                    sub_event_key = None

                if (sub_event_key and
                    main_event_name in self.current_events_data and
                    sub_event_key in self.current_events_data[main_event_name] and
                    0 <= action_index < len(self.current_events_data[main_event_name][sub_event_key]["actions"])):
                    self.current_events_data[main_event_name][sub_event_key]["actions"][action_index]["parameters"] = new_params
                else:
                    return
            else:
                # Direct event action: Parent → Action
                event_name = parent_item.data(0, Qt.UserRole)

                if (event_name in self.current_events_data and
                    "actions" in self.current_events_data[event_name] and
                    0 <= action_index < len(self.current_events_data[event_name]["actions"])):
                    self.current_events_data[event_name]["actions"][action_index]["parameters"] = new_params
                else:
                    return

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

    def _locate_action_list(self, action_item: QTreeWidgetItem):
        """Resolve an action tree item to its backing (list, index) in
        self.current_events_data, or (None, None) if it can't be located.

        Mirrors remove_action's navigation so copy/paste land on exactly the
        list the rest of the panel mutates (regular/collision/mouse events and
        keyboard sub-events alike).
        """
        parent_item = action_item.parent()
        if not parent_item:
            return None, None

        grandparent_item = parent_item.parent()
        action_index = parent_item.indexOfChild(action_item)

        if grandparent_item is not None:
            # Keyboard sub-event action: Container -> Sub-key -> Action
            main_event_name = grandparent_item.data(0, Qt.UserRole)
            sub_event_data = parent_item.data(0, Qt.UserRole)
            if (isinstance(sub_event_data, str) and isinstance(main_event_name, str)
                    and sub_event_data.startswith(main_event_name + "_")):
                sub_event_key = sub_event_data[len(main_event_name) + 1:]
                container = self.current_events_data.get(main_event_name, {})
                if (isinstance(container, dict) and sub_event_key in container
                        and "actions" in container[sub_event_key]):
                    actions = container[sub_event_key]["actions"]
                    if 0 <= action_index < len(actions):
                        return actions, action_index
            return None, None

        # Direct event action: Event -> Action
        event_name = parent_item.data(0, Qt.UserRole)
        event_data = self.current_events_data.get(event_name)
        if (isinstance(event_data, dict) and "actions" in event_data
                and 0 <= action_index < len(event_data["actions"])):
            return event_data["actions"], action_index
        return None, None

    def add_action_to_collision_event(self, collision_event: str, action_name: str):
        """Add an action to a collision event"""
        action_type = get_action_type(action_name)

        if not action_type:
            return

        dialog = create_action_dialog(action_type, parent=self)

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

    def add_action_to_mouse_event(self, mouse_event: str, action_name: str):
        """Add an action to a mouse event"""
        action_type = get_action_type(action_name)

        if not action_type:
            return

        dialog = create_action_dialog(action_type, parent=self)

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
