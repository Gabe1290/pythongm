#!/usr/bin/env python3
"""Events-tree rendering for :class:`ObjectEventsPanel`.

Extracted verbatim from ``_panel.py`` (``docs/POST_1_0_REFACTOR.md`` File 1,
cluster 5). A mixin -- ``self`` / ``self.tr()`` / siblings
(``events_tree``, ``current_events_data`` …) resolve on the concrete panel.

``get_action_type`` is the alias-aware wrapper from ``_action_lookup``;
render-path tests stub ``editors.object_editor.events._action_lookup.get_action_type``.
"""

from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt

from events.event_types import get_event_type

from ._action_lookup import get_action_type
from ..object_actions_formatter import ActionParametersFormatter


class RenderMixin:

    def _set_action_item_text(self, action_item, action_data, indent=""):
        """Populate a QTreeWidgetItem from an action dict.

        Comments render inline as `💬 <their text>` in italic gray so they
        visually stand apart from real actions; regular actions render as
        `<icon> <display_name>` with the smart parameter summary in col 1.
        """
        action_name = action_data.get("action", "unknown")
        params = action_data.get("parameters", {}) or {}

        if action_name == "comment":
            text = str(params.get("text", "")).strip()
            # Collapse to one line for the tree, capped so it doesn't
            # blow out the column on huge multi-line notes.
            one_line = " ".join(text.split())
            if len(one_line) > 80:
                one_line = one_line[:77] + "…"
            label = one_line or self.tr("(empty comment)")
            comment_type = get_action_type("comment")
            icon = comment_type.icon if comment_type else "⚠️"
            action_item.setText(0, f"{indent}{icon} {label}")
            action_item.setText(1, "")
            # Italic gray styling so comments don't read like live actions
            font = action_item.font(0)
            font.setItalic(True)
            action_item.setFont(0, font)
            comment_brush = QBrush(QColor(120, 120, 120))
            action_item.setForeground(0, comment_brush)
        else:
            action_type = get_action_type(action_name)
            if action_type:
                action_item.setText(0, f"{indent}{action_type.icon} {self.tr(action_type.display_name)}")
            else:
                # Unrecognized action — either a disabled/not-installed
                # extension's action, or a genuine typo/stale name. Never
                # crashes and always round-trips verbatim on save; render it
                # visibly inert (gray, like a comment) rather than looking
                # like a normal, editable action, and name the extension it
                # needs when that's knowable.
                from events.plugin_loader import extension_for_action
                owner = extension_for_action(action_name)
                if owner:
                    label = self.tr("{0} (needs {1})").format(action_name, owner["name"])
                else:
                    label = action_name
                action_item.setText(0, f"{indent}❓ {label}")
                # Amber, not the comment's neutral gray — this reads as
                # "needs attention" rather than "intentionally inert".
                amber_brush = QBrush(QColor(180, 120, 20))
                action_item.setForeground(0, amber_brush)
            if params:
                action_item.setText(1, ActionParametersFormatter.format_action_parameters(action_name, params))

        action_item.setData(0, Qt.UserRole, action_data)

    def _collect_expanded_keys(self):
        """Return the set of Qt.UserRole keys for currently-expanded tree items.

        Used to preserve which event / sub-event nodes are open across a
        rebuild, so adding or editing an action doesn't collapse the list the
        user is working in.
        """
        expanded = set()

        def walk(item):
            if item.isExpanded():
                key = item.data(0, Qt.UserRole)
                # Only event / sub-event nodes carry string keys; action leaves
                # store an (unhashable) action dict, which we skip.
                if isinstance(key, str):
                    expanded.add(key)
            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self.events_tree.topLevelItemCount()):
            walk(self.events_tree.topLevelItem(i))
        return expanded

    def _restore_expanded_keys(self, expanded_keys):
        """Re-expand tree items whose Qt.UserRole key was previously expanded."""
        if not expanded_keys:
            return

        def walk(item):
            key = item.data(0, Qt.UserRole)
            if isinstance(key, str) and key in expanded_keys:
                item.setExpanded(True)
            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self.events_tree.topLevelItemCount()):
            walk(self.events_tree.topLevelItem(i))

    def refresh_events_display(self):
        """Refresh the events tree display"""
        expanded_keys = self._collect_expanded_keys()
        self.events_tree.clear()

        for event_name, event_data in self.current_events_data.items():

            # Handle collision events specially (both normal and NOT colliding)
            if event_name.startswith("collision_with_") or event_name.startswith("not_collision_with_"):
                is_negated = event_name.startswith("not_collision_with_")

                if is_negated:
                    target_object = event_name.replace("not_collision_with_", "")
                    event_item = QTreeWidgetItem(self.events_tree)
                    event_item.setText(0, self.tr("❌ NOT Colliding with {0}").format(target_object))
                else:
                    target_object = event_name.replace("collision_with_", "")
                    event_item = QTreeWidgetItem(self.events_tree)
                    event_item.setText(0, self.tr("💥 Collision with {0}").format(target_object))

                actions = event_data.get("actions", [])
                event_item.setText(1, self.tr("{0} actions").format(len(actions)))
                event_item.setData(0, Qt.UserRole, event_name)

                # Add action items
                for action_data in actions:
                    action_item = QTreeWidgetItem(event_item)
                    self._set_action_item_text(action_item, action_data)

            # Handle keyboard events (keyboard, keyboard_press, keyboard_release)
            elif event_name in ["keyboard", "keyboard_press", "keyboard_release"] and isinstance(event_data, dict) and not event_data.get("actions"):
                event_type = get_event_type(event_name)
                if not event_type:
                    continue

                event_item = QTreeWidgetItem(self.events_tree)
                event_item.setText(0, f"{event_type.icon} {self.tr(event_type.display_name)}")
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
                    if display_key == "nokey":
                        display_name = "<No Key>"
                    elif display_key in ["left", "right", "up", "down"]:
                        display_name = f"{display_key.title()} Arrow"
                    else:
                        display_name = f"Key {display_key}"

                    sub_item.setText(0, f"{icon} {display_name}")
                    sub_item.setText(1, self.tr("{0} actions").format(len(sub_data.get('actions', []))))
                    sub_item.setData(0, Qt.UserRole, f"{event_name}_{key}")

                    for action_data in sub_data.get("actions", []):
                        action_item = QTreeWidgetItem(sub_item)
                        self._set_action_item_text(action_item, action_data, indent="  ")

            # Handle alarm events (nested structure: {"alarm": {"alarm_0": {...}, "alarm_1": {...}}})
            elif event_name == "alarm" and isinstance(event_data, dict) and not event_data.get("actions"):
                event_type = get_event_type(event_name)
                if not event_type:
                    continue

                event_item = QTreeWidgetItem(self.events_tree)
                event_item.setText(0, f"{event_type.icon} {self.tr(event_type.display_name)}")
                event_item.setData(0, Qt.UserRole, event_name)

                total_actions = sum(len(sub_data.get("actions", [])) for key, sub_data in event_data.items() if key != "actions" and isinstance(sub_data, dict))
                event_item.setText(1, self.tr("{0} total actions").format(total_actions))

                # Sort alarm sub-events numerically
                alarm_keys = sorted(
                    [k for k in event_data.keys() if k.startswith("alarm_") and isinstance(event_data[k], dict)],
                    key=lambda k: int(k.split("_")[1]) if k.split("_")[1].isdigit() else 0
                )

                for alarm_key in alarm_keys:
                    sub_data = event_data[alarm_key]
                    alarm_num = alarm_key.split("_")[1]

                    sub_item = QTreeWidgetItem(event_item)
                    sub_item.setText(0, f"⏰ {self.tr('Alarm')} {alarm_num}")
                    sub_item.setText(1, self.tr("{0} actions").format(len(sub_data.get('actions', []))))
                    sub_item.setData(0, Qt.UserRole, f"alarm_{alarm_key}")

                    for action_data in sub_data.get("actions", []):
                        action_item = QTreeWidgetItem(sub_item)
                        self._set_action_item_text(action_item, action_data, indent="  ")

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
                    action_item = QTreeWidgetItem(event_item)
                    self._set_action_item_text(action_item, action_data)

            else:
                # Regular events
                event_type = get_event_type(event_name)
                if not event_type:
                    continue

                event_item = QTreeWidgetItem(self.events_tree)
                event_item.setText(0, f"{event_type.icon} {self.tr(event_type.display_name)}")
                event_item.setText(1, f"{len(event_data.get('actions', []))} actions")
                event_item.setData(0, Qt.UserRole, event_name)

                actions = event_data.get("actions", [])
                for action_data in actions:
                    action_item = QTreeWidgetItem(event_item)
                    self._set_action_item_text(action_item, action_data)

        self.events_tree.collapseAll()
        self._restore_expanded_keys(expanded_keys)
