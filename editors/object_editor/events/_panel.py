#!/usr/bin/env python3
"""
Object Events Panel
Manages object events and their actions
"""

import copy
from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QMenu, QMessageBox,
    QDialog, QDialogButtonBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QBrush

# Import our new event/action system
from events.event_types import get_available_events, get_event_type
from events.thymio_events import THYMIO_EVENT_CATEGORIES, is_thymio_event
from events.action_types import get_actions_by_category
from events.conditional_editor import create_action_dialog

from ._action_lookup import ACTION_ALIASES, get_action_type  # noqa: F401  (re-exported)

# Import formatter
from ..object_actions_formatter import ActionParametersFormatter

# Import Python code parser for execute_code action parsing
from ..python_code_parser import PythonToActionsParser

from core.logger import get_logger
logger = get_logger(__name__)

from ._event_crud import EventCrudMixin
from ._action_crud import ActionCrudMixin
from ._render import RenderMixin


class ObjectEventsPanel(EventCrudMixin, ActionCrudMixin, RenderMixin, QWidget):
    """Panel for managing object events and their actions"""

    events_modified = Signal()
    event_selected = Signal(str)  # event_name

    # Shared across all object-editor event panels so actions copied in one
    # object's editor can be pasted into another. Holds a list of deep-copied
    # action dicts ([{"action": ..., "parameters": {...}}, ...]) in paste order,
    # or None when empty.
    _action_clipboard = None

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
            # Guard: the panel may be destroyed before the 100ms timer fires
            # (common in fast test teardown), leaving events_tree as a wrapper
            # around a freed C++ object. Calling .viewport() on it raises.
            try:
                total_width = self.events_tree.viewport().width()
                self.events_tree.setColumnWidth(0, int(total_width * 0.55))
            except RuntimeError:
                pass

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
        # Extended selection so several actions can be copied at once
        # (Ctrl/Shift-click). Single-item operations still use currentItem(),
        # and the overridden dropEvent rebuilds from the data model, so this
        # can't corrupt reordering.
        self.events_tree.setSelectionMode(QTreeWidget.ExtendedSelection)

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

            self.copy_action_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
            self.copy_action_shortcut.activated.connect(self.copy_selected_action)

            self.paste_action_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
            self.paste_action_shortcut.activated.connect(self.paste_selected_action)
        except Exception as e:
            logger.warning(f"Could not setup shortcuts: {e}")

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

    def show_context_menu(self, position):
        """Show context menu for events tree (see events/_context_menu.py)."""
        from ._context_menu import build_context_menu
        return build_context_menu(self, position)

    # Events whose JSON shape is a container dict keyed by sub-event name
    # (alarm number, keyboard sub-key) rather than the leaf shape
    # {"actions": [...]}. Adding an action to the container would land it
    # as a sibling of the sub-keys (e.g. keyboard_press becomes
    # {"SPACE": ..., "actions": [...]}); the runtime only reads
    # keyboard_press[<key>]["actions"], so the action would never fire and
    # the JSON would round-trip through the file in a malformed shape.
    # Each value is the hint text shown to the user pointing them at the
    # right sub-event to right-click on instead.
    _CONTAINER_EVENT_HINTS = {
        "alarm": "Alarm 0, Alarm 1, etc.",
        "keyboard": "a specific key (Left Arrow, Right Arrow, etc.)",
        "keyboard_press": "a specific key (SPACE, ENTER, etc.)",
        "keyboard_release": "a specific key (SPACE, ENTER, etc.)",
    }







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
            ObjectEventsPanel._action_clipboard = actions
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
        clip = ObjectEventsPanel._action_clipboard
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
        from PySide6.QtWidgets import QApplication
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_data'):
                project_data = parent.current_project_data
                if project_data and 'assets' in project_data:
                    objects = project_data['assets'].get('objects', {})
                    return list(objects.keys())
                break
            parent = parent.parent()

        # Try top-level windows as fallback
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'current_project_data') and widget.current_project_data:
                objects = widget.current_project_data.get('assets', {}).get('objects', {})
                return list(objects.keys())

        return []

    def project_has_playgrounds(self) -> bool:
        """Check if the current project contains any playground assets"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_project_data'):
                project_data = parent.current_project_data
                if project_data and 'assets' in project_data:
                    playgrounds = project_data['assets'].get('playgrounds', {})
                    return bool(playgrounds)
                break
            parent = parent.parent()
        return False

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
