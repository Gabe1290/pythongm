#!/usr/bin/env python3
"""
Mouse Event Selector Dialog
Allows users to select mouse events when adding mouse events to objects
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QDialogButtonBox, QTabWidget, QWidget,
    QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from events.event_types import get_mouse_events_for_selector


class MouseEventSelectorDialog(QDialog):
    """Dialog for selecting a mouse event"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_event = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(self.tr("Select Mouse Event"))
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel(self.tr("Select which mouse event to respond to:"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel(self.tr("Search:"))
        search_layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("Type to filter events..."))
        self.search_box.textChanged.connect(self.filter_events)
        search_layout.addWidget(self.search_box)

        layout.addLayout(search_layout)

        # Tabs for different mouse event categories
        self.tab_widget = QTabWidget()

        # Get organized mouse events
        mouse_events = get_mouse_events_for_selector()

        # Create a tab for each category
        self.list_widgets = {}
        for category, events in mouse_events.items():
            if events:  # Only add tab if there are events
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)

                list_widget = QListWidget()
                list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

                # Add events to list
                for event in events:
                    icon = event.get('icon', '🖱️')
                    name = event.get('display_name', event.get('name', 'Unknown'))
                    desc = event.get('description', '')

                    item_text = f"{icon} {name}"
                    if desc:
                        item_text += f"\n   {desc}"

                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, event)
                    list_widget.addItem(item)

                tab_layout.addWidget(list_widget)

                self.tab_widget.addTab(tab, f"{category} ({len(events)})")
                self.list_widgets[category] = list_widget

        layout.addWidget(self.tab_widget)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Select first tab and first item
        if self.list_widgets:
            first_list = list(self.list_widgets.values())[0]
            if first_list.count() > 0:
                first_list.setCurrentRow(0)

    def filter_events(self, text):
        """Filter events based on search text"""
        text = text.lower()

        for list_widget in self.list_widgets.values():
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                event_data = item.data(Qt.UserRole)

                # Check if search text matches event name or description
                name = event_data.get('name', '').lower()
                display_name = event_data.get('display_name', '').lower()
                description = event_data.get('description', '').lower()

                matches = (text in name or
                          text in display_name or
                          text in description)

                item.setHidden(not matches)

    def on_item_double_clicked(self, item):
        """Handle double-click on an item"""
        self.accept_selection()

    def accept_selection(self):
        """Accept the current selection"""
        # Find the currently selected item across all tabs
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index >= 0:
            category = list(self.list_widgets.keys())[current_tab_index]
            list_widget = self.list_widgets[category]

            current_item = list_widget.currentItem()
            if current_item:
                event_data = current_item.data(Qt.UserRole)
                self.selected_event = event_data
                self.accept()
            else:
                # No selection
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    self.tr("No Selection"),
                    self.tr("Please select a mouse event first.")
                )

    def get_selected_event(self):
        """Get the selected mouse event data"""
        return self.selected_event
