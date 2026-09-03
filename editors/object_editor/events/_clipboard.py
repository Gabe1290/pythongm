#!/usr/bin/env python3
"""Action copy / paste for :class:`ObjectEventsPanel`.

Extracted verbatim from ``_panel.py`` (``docs/POST_1_0_REFACTOR.md`` File 1,
cluster 6), except the two direct ``ObjectEventsPanel._action_clipboard``
references in ``_store_clipboard`` / ``_clipboard_actions`` became
``type(self)._action_clipboard`` to avoid a ``_clipboard`` <-> ``_panel``
import cycle. Equivalent for the one concrete class (no subclasses), and
``test_action_copy_paste.py`` still sets/reads it on ``ObjectEventsPanel``.
The ``_action_clipboard = None`` class attribute stays on
``ObjectEventsPanel`` itself.
"""

import copy

from PySide6.QtWidgets import QTreeWidgetItem, QTreeWidgetItemIterator
from PySide6.QtCore import Qt

from core.logger import get_logger

logger = get_logger(__name__)


class ClipboardMixin:

    def copy_selected_action(self):
        """Ctrl+C: copy all currently selected actions (if any are selected)."""
        self._store_clipboard(self._selected_action_items())

    def paste_selected_action(self):
        """Ctrl+V: paste the clipboard action relative to the current selection.

        On an action -> insert after it; on an event / keyboard sub-event node
        -> append to that event. paste_action_append no-ops on nodes that can't
        hold actions (e.g. keyboard/alarm containers), so this is safe to call
        for any selection.
        """
        current_item = self.events_tree.currentItem()
        if not current_item:
            return
        action_data = current_item.data(0, Qt.UserRole)
        if isinstance(action_data, dict) and "action" in action_data:
            self.paste_action_after(current_item)
        else:
            self.paste_action_append(current_item)

    def _paste_menu_label(self):
        """'Paste Action' or 'Paste N Actions' to reflect the clipboard size."""
        clip = self._clipboard_actions()
        count = len(clip) if clip else 0
        if count > 1:
            return self.tr("Paste {0} Actions").format(count)
        return self.tr("Paste Action")

    def _add_action_clipboard_menu(self, menu, action_item):
        """Append Copy/Paste entries to an action item's context menu.
        Copy reflects how many actions are selected; Paste (insert-after) is
        only offered when the clipboard holds at least one action.
        """
        selected = self._selected_action_items()
        copy_count = len(selected) if action_item in selected else 1
        copy_label = (self.tr("Copy {0} Actions").format(copy_count)
                      if copy_count > 1 else self.tr("Copy Action"))
        copy_item = menu.addAction(copy_label)
        copy_item.triggered.connect(lambda: self.copy_action(action_item))

        if self._clipboard_actions() is not None:
            paste_item = menu.addAction(self._paste_menu_label())
            paste_item.triggered.connect(lambda: self.paste_action_after(action_item))

    def _add_event_paste_menu(self, menu, event_item):
        """Append a Paste-Action (append-to-end) entry to an event node's menu
        when the clipboard holds actions and the node accepts actions.
        """
        if self._clipboard_actions() is None:
            return
        if self._event_actions_list(event_item) is None:
            return
        paste_item = menu.addAction(self._paste_menu_label())
        paste_item.triggered.connect(lambda: self.paste_action_append(event_item))

    def _event_actions_list(self, event_item: QTreeWidgetItem):
        """Return the actions list for a leaf event node or keyboard sub-event
        node (so paste-append knows where to drop a copied action), or None
        when the node can't accept actions directly (e.g. keyboard/alarm
        containers).
        """
        parent = event_item.parent()
        if parent is None:
            event_name = event_item.data(0, Qt.UserRole)
            event_data = self.current_events_data.get(event_name)
            if isinstance(event_data, dict) and "actions" in event_data:
                return event_data["actions"]
            return None

        # Keyboard sub-event node: parent is the container event
        if parent.parent() is not None:
            return None
        main_event_name = parent.data(0, Qt.UserRole)
        sub_event_data = event_item.data(0, Qt.UserRole)
        if (isinstance(sub_event_data, str) and isinstance(main_event_name, str)
                and sub_event_data.startswith(main_event_name + "_")):
            sub_event_key = sub_event_data[len(main_event_name) + 1:]
            container = self.current_events_data.get(main_event_name, {})
            if (isinstance(container, dict) and sub_event_key in container
                    and "actions" in container[sub_event_key]):
                return container[sub_event_key]["actions"]
        return None

    def _selected_action_items(self):
        """Return every selected action item in top-to-bottom tree order.

        Qt's selectedItems() order is undefined, so walk the tree to make paste
        order match what the user sees.
        """
        selected = set(self.events_tree.selectedItems())
        if not selected:
            return []
        ordered = []
        iterator = QTreeWidgetItemIterator(self.events_tree)
        while iterator.value():
            item = iterator.value()
            if item in selected:
                data = item.data(0, Qt.UserRole)
                if isinstance(data, dict) and "action" in data:
                    ordered.append(item)
            iterator += 1
        return ordered

    def _store_clipboard(self, action_items):
        """Deep-copy the given action items onto the shared clipboard."""
        actions = []
        for item in action_items:
            data = item.data(0, Qt.UserRole)
            if isinstance(data, dict) and "action" in data:
                actions.append(copy.deepcopy(data))
        if actions:
            type(self)._action_clipboard = actions
            logger.debug(f"Copied {len(actions)} action(s) to clipboard")

    def copy_action(self, action_item: QTreeWidgetItem):
        """Copy actions to the shared clipboard (context-menu entry).

        Copies the whole selection when the right-clicked action is part of it,
        otherwise just the right-clicked action.
        """
        selected = self._selected_action_items()
        items = selected if action_item in selected else [action_item]
        self._store_clipboard(items)

    def _clipboard_actions(self):
        """Return the clipboard's action list, or None when empty."""
        clip = type(self)._action_clipboard
        if isinstance(clip, list) and clip:
            return clip
        return None

    def paste_action_after(self, action_item: QTreeWidgetItem):
        """Paste the clipboard actions immediately after the given action."""
        clip = self._clipboard_actions()
        if clip is None:
            return
        actions, index = self._locate_action_list(action_item)
        if actions is None:
            return
        for offset, action in enumerate(clip, start=1):
            actions.insert(index + offset, copy.deepcopy(action))
        self.refresh_events_display()
        self.events_modified.emit()

    def paste_action_append(self, event_item: QTreeWidgetItem):
        """Paste the clipboard actions at the end of an event's action list."""
        clip = self._clipboard_actions()
        if clip is None:
            return
        actions = self._event_actions_list(event_item)
        if actions is None:
            return
        for action in clip:
            actions.append(copy.deepcopy(action))
        self.refresh_events_display()
        self.events_modified.emit()
