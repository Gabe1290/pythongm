#!/usr/bin/env python3
"""
Thymio Event Selector Dialog
Visual dialog for selecting Thymio robot events with interactive robot diagram.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QDialogButtonBox, QWidget, QLineEdit,
    QPushButton, QFrame, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from widgets.thymio_diagram_widget import (
    ThymioDiagramWidget, get_events_for_region
)
from events.thymio_events import THYMIO_EVENT_TYPES, THYMIO_EVENT_CATEGORIES


class ThymioEventSelector(QDialog):
    """
    Dialog for selecting Thymio events with visual robot diagram.

    Features:
    - Interactive Thymio robot diagram with clickable regions
    - Category filter buttons
    - Search filtering
    - Event list with icons and descriptions
    """

    event_selected = Signal(str)  # Emits event name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_event = None
        self.current_category = None  # None means show all
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(self.tr("Select Thymio Event"))
        self.setMinimumSize(450, 650)
        self.resize(450, 700)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        title = QLabel(self.tr("Select a Thymio event to respond to:"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        # Thymio diagram widget
        diagram_container = QFrame()
        diagram_container.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        diagram_layout = QHBoxLayout(diagram_container)
        diagram_layout.setContentsMargins(5, 5, 5, 5)

        self.diagram = ThymioDiagramWidget()
        self.diagram.region_clicked.connect(self.on_diagram_clicked)
        self.diagram.region_hovered.connect(self.on_diagram_hovered)
        diagram_layout.addStretch()
        diagram_layout.addWidget(self.diagram)
        diagram_layout.addStretch()

        layout.addWidget(diagram_container)

        # Hint label
        hint_label = QLabel(self.tr("Click on the robot to filter events, or select from the list below."))
        hint_label.setStyleSheet("color: #666; font-style: italic;")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        # Category buttons
        category_frame = QFrame()
        category_layout = QHBoxLayout(category_frame)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(5)

        # "All" button
        self.all_button = QPushButton(self.tr("All"))
        self.all_button.setCheckable(True)
        self.all_button.setChecked(True)
        self.all_button.clicked.connect(lambda: self.filter_by_category(None))
        category_layout.addWidget(self.all_button)

        self.category_buttons = {'all': self.all_button}

        # Category buttons from THYMIO_EVENT_CATEGORIES
        for cat_key, cat_info in sorted(THYMIO_EVENT_CATEGORIES.items(),
                                         key=lambda x: x[1].get('order', 0)):
            # Shorten the display name (remove "Thymio " prefix)
            short_name = cat_info['name'].replace("Thymio ", "")
            btn = QPushButton(f"{cat_info['icon']} {short_name}")
            btn.setCheckable(True)
            btn.setToolTip(cat_info.get('description', ''))
            btn.clicked.connect(lambda checked, c=cat_key: self.filter_by_category(c))
            category_layout.addWidget(btn)
            self.category_buttons[cat_key] = btn

        layout.addWidget(category_frame)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel(self.tr("Search:"))
        search_layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("Type to filter events..."))
        self.search_box.textChanged.connect(self.filter_events)
        self.search_box.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_box)

        layout.addLayout(search_layout)

        # Event list
        self.event_list = QListWidget()
        self.event_list.itemClicked.connect(self.on_event_clicked)
        self.event_list.itemDoubleClicked.connect(self.on_event_double_clicked)
        self.event_list.setMinimumHeight(200)
        layout.addWidget(self.event_list)

        # Description label
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(
            "background-color: #f5f5f5; padding: 8px; border-radius: 4px;"
        )
        self.description_label.setMinimumHeight(50)
        layout.addWidget(self.description_label)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)
        self.ok_button = buttons.button(QDialogButtonBox.Ok)
        self.ok_button.setText(self.tr("Select Event"))
        self.ok_button.setEnabled(False)
        layout.addWidget(buttons)

        # Populate the event list
        self.populate_events()

    def populate_events(self):
        """Populate the event list with all Thymio events"""
        self.event_list.clear()

        for event_name, event_type in THYMIO_EVENT_TYPES.items():
            # Apply category filter
            if self.current_category and event_type.category != self.current_category:
                continue

            # Create list item
            icon = event_type.icon or ""
            display_text = f"{icon} {event_type.display_name}"
            description = event_type.description or ""

            item = QListWidgetItem(f"{display_text}\n   {description}")
            item.setData(Qt.UserRole, {
                'name': event_name,
                'display_name': event_type.display_name,
                'description': description,
                'category': event_type.category,
                'icon': icon
            })
            item.setToolTip(f"{event_type.display_name}\n{description}")

            self.event_list.addItem(item)

        # Apply search filter if there's text
        if self.search_box.text():
            self.filter_events(self.search_box.text())

        # Select first item if available
        if self.event_list.count() > 0:
            self.event_list.setCurrentRow(0)
            self.on_event_clicked(self.event_list.item(0))

    def filter_by_category(self, category):
        """Filter events by category"""
        self.current_category = category

        # Update button states
        for cat_key, btn in self.category_buttons.items():
            if cat_key == 'all':
                btn.setChecked(category is None)
            else:
                btn.setChecked(cat_key == category)

        # Clear diagram highlights
        self.diagram.clear_highlights()

        # Repopulate list
        self.populate_events()

    def filter_events(self, text):
        """Filter events based on search text"""
        text = text.lower()

        for i in range(self.event_list.count()):
            item = self.event_list.item(i)
            event_data = item.data(Qt.UserRole)

            # Check if search text matches event name, display name, or description
            name = event_data.get('name', '').lower()
            display_name = event_data.get('display_name', '').lower()
            description = event_data.get('description', '').lower()

            matches = (text in name or
                      text in display_name or
                      text in description)

            item.setHidden(not matches)

    def on_diagram_clicked(self, region_id):
        """Handle click on diagram region"""
        # Get events related to this region
        related_events = get_events_for_region(region_id)

        if related_events:
            # Clear category filter to show all
            self.filter_by_category(None)

            # Find and select the first matching event
            for i in range(self.event_list.count()):
                item = self.event_list.item(i)
                event_data = item.data(Qt.UserRole)
                if event_data['name'] in related_events:
                    self.event_list.setCurrentItem(item)
                    self.event_list.scrollToItem(item)
                    self.on_event_clicked(item)

                    # Highlight the related events
                    self._highlight_related_events(related_events)
                    break

            # Also highlight the clicked region
            self.diagram.clear_highlights()
            self.diagram.highlight_region(region_id)

    def on_diagram_hovered(self, region_id):
        """Handle hover over diagram region"""
        # Could show preview of related events
        pass

    def _highlight_related_events(self, event_names):
        """Visually highlight events in the list that match the given names"""
        for i in range(self.event_list.count()):
            item = self.event_list.item(i)
            event_data = item.data(Qt.UserRole)

            if event_data['name'] in event_names:
                # Show the item (in case it was filtered)
                item.setHidden(False)

    def on_event_clicked(self, item):
        """Handle single click on event"""
        if item:
            event_data = item.data(Qt.UserRole)
            self.selected_event = event_data['name']

            # Update description
            icon = event_data.get('icon', '')
            name = event_data.get('display_name', '')
            desc = event_data.get('description', '')
            category = event_data.get('category', '')

            self.description_label.setText(
                f"<b>{icon} {name}</b><br>"
                f"<small>Category: {category}</small><br><br>"
                f"{desc}"
            )

            self.ok_button.setEnabled(True)

            # Highlight related regions on diagram
            self._highlight_diagram_for_event(event_data['name'])

    def on_event_double_clicked(self, item):
        """Handle double-click on event"""
        self.accept_selection()

    def _highlight_diagram_for_event(self, event_name):
        """Highlight diagram regions related to the selected event"""
        self.diagram.clear_highlights()

        # Map events to diagram regions
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
            'thymio_timer_0': [],
            'thymio_timer_1': [],
            'thymio_sound_detected': [],
            'thymio_sound_finished': [],
            'thymio_message_received': [],
        }

        regions = event_to_regions.get(event_name, [])
        if regions:
            self.diagram.highlight_regions(regions)

    def accept_selection(self):
        """Accept the current selection"""
        current_item = self.event_list.currentItem()
        if current_item:
            event_data = current_item.data(Qt.UserRole)
            self.selected_event = event_data['name']
            self.event_selected.emit(self.selected_event)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                self.tr("No Selection"),
                self.tr("Please select a Thymio event first.")
            )

    def get_selected_event(self):
        """Get the selected event name"""
        return self.selected_event
