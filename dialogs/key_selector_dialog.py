#!/usr/bin/env python3
"""
Key Selector Dialog
Allows users to select keyboard keys when adding keyboard events
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialogButtonBox, QTabWidget,
    QWidget, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from events.event_types import get_keyboard_events_for_selector


class KeySelectorDialog(QDialog):
    """Dialog for selecting a keyboard key"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_key = None
        self.selected_key_code = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(self.tr("Select Key"))
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel(self.tr("Select which key to respond to:"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel(self.tr("Search:"))
        search_layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("Type to filter keys..."))
        self.search_box.textChanged.connect(self.filter_keys)
        search_layout.addWidget(self.search_box)

        layout.addLayout(search_layout)

        # Tabs for different key categories
        self.tab_widget = QTabWidget()

        # Get organized keyboard events
        keyboard_events = get_keyboard_events_for_selector()

        # Create a tab for each category
        self.list_widgets = {}
        for category, events in keyboard_events.items():
            if events:  # Only add tab if there are events
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)

                list_widget = QListWidget()
                list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

                # Add events to list
                for event in events:
                    item = QListWidgetItem(f"{event['display_name']} (code: {event['key_code']})")
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

    def filter_keys(self, text):
        """Filter keys based on search text"""
        text = text.lower()

        for list_widget in self.list_widgets.values():
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                event_data = item.data(Qt.UserRole)

                # Check if search text matches key name
                key_name = event_data['key'].lower()
                display_name = event_data['display_name'].lower()

                matches = (text in key_name or
                          text in display_name or
                          text in str(event_data['key_code']))

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
                self.selected_key = event_data['key']
                self.selected_key_code = event_data['key_code']
                self.accept()
            else:
                # No selection
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    self.tr("No Selection"),
                    self.tr("Please select a key first.")
                )

    def get_selected_key(self):
        """Get the selected key name"""
        return self.selected_key

    def get_selected_key_code(self):
        """Get the selected key code"""
        return self.selected_key_code
