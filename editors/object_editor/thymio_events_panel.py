#!/usr/bin/env python3
"""
Thymio Events Panel
Dedicated panel for Thymio robot programming with embedded visual diagram.
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QDialog,
    QFrame, QSplitter, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from widgets.thymio_diagram_widget import (
    ThymioDiagramWidget, get_events_for_region, get_actions_for_region
)
from events.thymio_events import THYMIO_EVENT_TYPES, THYMIO_EVENT_CATEGORIES
from actions.thymio_actions import THYMIO_ACTIONS
from editors.object_editor.gm80_action_dialog import GM80ActionDialog

from core.logger import get_logger
logger = get_logger(__name__)


class ThymioEventsPanel(QWidget):
    """
    Dedicated panel for Thymio programming with visual robot diagram.

    Features:
    - Embedded interactive Thymio diagram
    - Thymio-only event categories
    - Thymio-only actions
    - Visual feedback when clicking diagram regions
    """

    events_modified = Signal()
    event_selected = Signal(str)  # event_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_events_data = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the Thymio events panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel(self.tr("Thymio Programming"))
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Create splitter for diagram and events
        splitter = QSplitter(Qt.Vertical)

        # Top: Thymio diagram
        diagram_frame = QFrame()
        diagram_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        diagram_layout = QVBoxLayout(diagram_frame)
        diagram_layout.setContentsMargins(5, 5, 5, 5)

        # Hint label
        hint_label = QLabel(self.tr("Click on the robot to add events"))
        hint_label.setStyleSheet("color: #666; font-size: 9px;")
        hint_label.setAlignment(Qt.AlignCenter)
        diagram_layout.addWidget(hint_label)

        # Diagram widget centered
        diagram_container = QHBoxLayout()
        diagram_container.addStretch()
        self.diagram = ThymioDiagramWidget()
        self.diagram.region_clicked.connect(self.on_diagram_clicked)
        self.diagram.region_hovered.connect(self.on_diagram_hovered)
        diagram_container.addWidget(self.diagram)
        diagram_container.addStretch()
        diagram_layout.addLayout(diagram_container)

        splitter.addWidget(diagram_frame)

        # Bottom: Events tree
        events_widget = QWidget()
        events_layout = QVBoxLayout(events_widget)
        events_layout.setContentsMargins(0, 5, 0, 0)
        events_layout.setSpacing(3)

        # Category buttons for quick filtering/adding
        category_layout = QHBoxLayout()
        category_layout.setSpacing(2)

        self.category_buttons = {}
        for cat_key, cat_info in sorted(THYMIO_EVENT_CATEGORIES.items(),
                                         key=lambda x: x[1].get('order', 0)):
            short_name = cat_info['name'].replace("Thymio ", "")
            btn = QPushButton(f"{cat_info['icon']}")
            btn.setToolTip(f"{short_name}: {cat_info.get('description', '')}")
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("QPushButton { font-size: 14px; }")
            btn.clicked.connect(lambda checked, c=cat_key: self.show_category_events_menu(c))
            category_layout.addWidget(btn)
            self.category_buttons[cat_key] = btn

        category_layout.addStretch()

        # Add event button
        self.add_event_btn = QPushButton(self.tr("+ Event"))
        self.add_event_btn.setToolTip(self.tr("Add Thymio event"))
        self.add_event_btn.clicked.connect(self.show_add_event_menu)
        category_layout.addWidget(self.add_event_btn)

        events_layout.addLayout(category_layout)

        # Events tree
        self.events_tree = QTreeWidget()
        self.events_tree.setHeaderLabels([self.tr("Event"), self.tr("Actions")])
        self.events_tree.setExpandsOnDoubleClick(False)
        self.events_tree.setRootIsDecorated(True)

        # Configure header
        header = self.events_tree.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, header.ResizeMode.Interactive)

        self.events_tree.itemClicked.connect(self.on_event_selected)
        self.events_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.events_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.events_tree.customContextMenuRequested.connect(self.show_context_menu)

        events_layout.addWidget(self.events_tree)

        splitter.addWidget(events_widget)

        # Set initial splitter sizes (diagram smaller, events larger)
        splitter.setSizes([200, 300])

        layout.addWidget(splitter)

    def on_diagram_clicked(self, region_id):
        """Handle click on diagram region - show menu to add related event"""
        related_events = get_events_for_region(region_id)

        if related_events:
            # Show menu with related events
            menu = QMenu(self)
            menu.setTitle(self.tr("Add Event"))

            for event_name in related_events:
                event_type = THYMIO_EVENT_TYPES.get(event_name)
                if event_type:
                    action = menu.addAction(f"{event_type.icon} {event_type.display_name}")
                    action.triggered.connect(
                        lambda checked, e=event_name: self.add_event(e)
                    )

            # Show menu at cursor position
            menu.exec(self.diagram.mapToGlobal(self.diagram.rect().center()))

            # Highlight the clicked region
            self.diagram.clear_highlights()
            self.diagram.highlight_region(region_id)

    def on_diagram_hovered(self, region_id):
        """Handle hover over diagram region"""
        pass

    def show_category_events_menu(self, category):
        """Show menu with events from a specific category"""
        menu = QMenu(self)

        for event_name, event_type in THYMIO_EVENT_TYPES.items():
            if event_type.category == category:
                action = menu.addAction(f"{event_type.icon} {event_type.display_name}")
                action.triggered.connect(
                    lambda checked, e=event_name: self.add_event(e)
                )

        btn = self.category_buttons.get(category)
        if btn:
            menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def show_add_event_menu(self):
        """Show menu to add Thymio events"""
        menu = QMenu(self)

        # Group by category
        for cat_key, cat_info in sorted(THYMIO_EVENT_CATEGORIES.items(),
                                         key=lambda x: x[1].get('order', 0)):
            short_name = cat_info['name'].replace("Thymio ", "")
            submenu = menu.addMenu(f"{cat_info['icon']} {short_name}")

            for event_name, event_type in THYMIO_EVENT_TYPES.items():
                if event_type.category == cat_key:
                    action = submenu.addAction(f"{event_type.icon} {event_type.display_name}")
                    action.triggered.connect(
                        lambda checked, e=event_name: self.add_event(e)
                    )

        menu.exec(self.add_event_btn.mapToGlobal(self.add_event_btn.rect().bottomLeft()))

    def add_event(self, event_name: str):
        """Add a Thymio event"""
        if event_name in self.current_events_data:
            QMessageBox.information(
                self,
                self.tr("Event Exists"),
                self.tr("This event already exists.")
            )
            return

        self.current_events_data[event_name] = {"actions": []}
        self.refresh_events_display()
        self.events_modified.emit()

        # Highlight related diagram regions
        self._highlight_diagram_for_event(event_name)

    def show_context_menu(self, position):
        """Show context menu for events tree"""
        item = self.events_tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        parent = item.parent()

        if parent is None:
            # Top-level event
            event_name = item.data(0, Qt.UserRole)

            # Add action submenu
            add_action_menu = menu.addMenu(self.tr("Add Action"))

            # Group actions by category
            actions_by_category = {}
            for action_name, action_def in THYMIO_ACTIONS.items():
                cat = action_def.category
                if cat not in actions_by_category:
                    actions_by_category[cat] = []
                actions_by_category[cat].append((action_name, action_def))

            for category in sorted(actions_by_category.keys()):
                # Get category display name
                cat_display = category.replace("thymio_", "").title()
                category_menu = add_action_menu.addMenu(cat_display)

                for action_name, action_def in actions_by_category[category]:
                    action_item = category_menu.addAction(f"{action_def.icon} {action_def.display_name}")
                    action_item.triggered.connect(
                        lambda checked, e=event_name, a=action_name: self.add_action_to_event(e, a)
                    )

            menu.addSeparator()
            remove_action = menu.addAction(self.tr("Remove Event"))
            remove_action.triggered.connect(lambda: self.remove_event(event_name))

        else:
            # Action item
            action_data = item.data(0, Qt.UserRole)
            if action_data and isinstance(action_data, dict):
                edit_action = menu.addAction(self.tr("Edit Action"))
                edit_action.triggered.connect(lambda: self.edit_action(item))

                remove_action = menu.addAction(self.tr("Remove Action"))
                remove_action.triggered.connect(lambda: self.remove_action(item))

        menu.exec(self.events_tree.mapToGlobal(position))

    def add_action_to_event(self, event_name: str, action_name: str):
        """Add a Thymio action to an event"""
        action_def = THYMIO_ACTIONS.get(action_name)
        if not action_def:
            return

        # If action has parameters, show configuration dialog
        if action_def.parameters:
            dialog = GM80ActionDialog(action_def, parent=self)
            if dialog.exec() == QDialog.Accepted:
                params = dialog.get_parameter_values()
            else:
                return
        else:
            params = {}

        action_data = {
            "action": action_name,
            "parameters": params
        }

        if event_name not in self.current_events_data:
            self.current_events_data[event_name] = {"actions": []}

        self.current_events_data[event_name]["actions"].append(action_data)
        self.refresh_events_display()
        self.events_modified.emit()

    def edit_action(self, item: QTreeWidgetItem):
        """Edit an action's parameters"""
        action_data = item.data(0, Qt.UserRole)
        if not action_data or not isinstance(action_data, dict):
            return

        action_name = action_data.get("action")
        action_def = THYMIO_ACTIONS.get(action_name)
        if not action_def:
            return

        current_params = action_data.get("parameters", {})
        dialog = GM80ActionDialog(action_def, current_params, parent=self)

        if dialog.exec() == QDialog.Accepted:
            new_params = dialog.get_parameter_values()
            action_data["parameters"] = new_params

            # Update tree display
            self.refresh_events_display()
            self.events_modified.emit()

    def remove_action(self, item: QTreeWidgetItem):
        """Remove an action from its event"""
        parent = item.parent()
        if not parent:
            return

        event_name = parent.data(0, Qt.UserRole)
        action_index = parent.indexOfChild(item)

        if event_name in self.current_events_data:
            actions = self.current_events_data[event_name].get("actions", [])
            if 0 <= action_index < len(actions):
                del actions[action_index]
                self.refresh_events_display()
                self.events_modified.emit()

    def remove_event(self, event_name: str):
        """Remove an event"""
        reply = QMessageBox.question(
            self,
            self.tr("Remove Event"),
            self.tr("Remove this event and all its actions?"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if event_name in self.current_events_data:
                del self.current_events_data[event_name]
                self.refresh_events_display()
                self.events_modified.emit()

    def on_event_selected(self, item: QTreeWidgetItem, column: int):
        """Handle event selection"""
        # Get top-level event name
        if item.parent():
            event_item = item.parent()
        else:
            event_item = item

        event_name = event_item.data(0, Qt.UserRole)
        if event_name:
            self.event_selected.emit(event_name)
            self._highlight_diagram_for_event(event_name)

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on item"""
        if item.parent():
            # It's an action - edit it
            self.edit_action(item)

    def _highlight_diagram_for_event(self, event_name: str):
        """Highlight diagram regions related to an event"""
        self.diagram.clear_highlights()

        event_to_regions = {
            'thymio_button_forward': ['button_forward'],
            'thymio_button_backward': ['button_backward'],
            'thymio_button_left': ['button_left'],
            'thymio_button_right': ['button_right'],
            'thymio_button_center': ['button_center'],
            'thymio_any_button': ['button_forward', 'button_backward', 'button_left',
                                  'button_right', 'button_center'],
            'thymio_proximity_update': ['prox_0', 'prox_1', 'prox_2', 'prox_3',
                                        'prox_4', 'prox_5', 'prox_6'],
            'thymio_ground_update': ['ground_left', 'ground_right'],
            'thymio_tap': ['robot_body'],
        }

        regions = event_to_regions.get(event_name, [])
        if regions:
            self.diagram.highlight_regions(regions)

    def refresh_events_display(self):
        """Refresh the events tree display"""
        self.events_tree.clear()

        for event_name, event_data in self.current_events_data.items():
            # Only show Thymio events
            event_type = THYMIO_EVENT_TYPES.get(event_name)
            if not event_type:
                continue

            # Create event item
            event_item = QTreeWidgetItem()
            event_item.setText(0, f"{event_type.icon} {event_type.display_name}")
            event_item.setData(0, Qt.UserRole, event_name)
            event_item.setToolTip(0, event_type.description)

            # Add actions
            actions = event_data.get("actions", [])
            for action_data in actions:
                if isinstance(action_data, dict):
                    action_name = action_data.get("action", "")
                    action_def = THYMIO_ACTIONS.get(action_name)

                    if action_def:
                        action_item = QTreeWidgetItem()
                        action_item.setText(0, f"  {action_def.icon} {action_def.display_name}")
                        action_item.setData(0, Qt.UserRole, action_data)

                        # Format parameters for display
                        params = action_data.get("parameters", {})
                        if params:
                            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
                            action_item.setText(1, param_str)

                        event_item.addChild(action_item)

            # Show action count
            event_item.setText(1, f"{len(actions)} action{'s' if len(actions) != 1 else ''}")

            self.events_tree.addTopLevelItem(event_item)
            event_item.setExpanded(True)

    def load_events_data(self, events_data: Dict[str, Any]):
        """Load events data into the panel"""
        # Filter to only Thymio events
        self.current_events_data = {}
        for event_name, event_data in events_data.items():
            if event_name in THYMIO_EVENT_TYPES:
                self.current_events_data[event_name] = event_data.copy() if isinstance(event_data, dict) else {"actions": []}

        self.refresh_events_display()

    def get_events_data(self) -> Dict[str, Any]:
        """Get the current events data"""
        return self.current_events_data.copy()

    def apply_config(self, config):
        """Apply configuration (for compatibility with ObjectEventsPanel)"""
        pass  # Thymio panel always shows Thymio events
