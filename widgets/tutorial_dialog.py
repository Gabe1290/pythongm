#!/usr/bin/env python3
"""
Tutorial Selection Dialog for PyGameMaker IDE
Displays a list of available tutorials - selection opens in preview panel
"""
import json
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from core.logger import get_logger
from widgets._tutorial_paths import localized_tutorials_path
logger = get_logger(__name__)


class TutorialDialog(QDialog):
    """Dialog for selecting tutorials - displays in preview panel when selected"""

    def __init__(self, parent=None, tutorials_path=None):
        super().__init__(parent)
        self.base_tutorials_path = Path(tutorials_path) if tutorials_path else None
        self.tutorials_path = self._get_localized_tutorials_path()
        self.selected_tutorial = None

        self.setWindowTitle(self.tr("Tutorials"))
        self.setMinimumSize(500, 400)
        self.resize(550, 450)

        self.setup_ui()
        self.load_tutorial_list()

    def _get_localized_tutorials_path(self):
        """Get the tutorials path for the current language, falling back to English"""
        return localized_tutorials_path(self.base_tutorials_path)

    def get_selected_tutorial(self):
        """Return the selected tutorial data"""
        return self.selected_tutorial

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(self.tr("<h2>PyGameMaker Tutorials</h2>"))
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(self.tr("Select a tutorial and click Open (or double-click):"))
        layout.addWidget(instructions)

        # Tutorial list
        self.tutorial_list = QListWidget()
        self.tutorial_list.itemClicked.connect(self.on_tutorial_clicked)
        self.tutorial_list.itemDoubleClicked.connect(self.on_tutorial_double_clicked)
        self.tutorial_list.itemSelectionChanged.connect(self._update_open_button)
        layout.addWidget(self.tutorial_list)

        # Description area with thumbnail
        desc_widget = QHBoxLayout()

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(160, 120)
        self.thumbnail_label.setStyleSheet(
            "QLabel { background-color: #2c3e50; border-radius: 5px; }"
        )
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        desc_widget.addWidget(self.thumbnail_label)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(
            "QLabel { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }"
        )
        self.description_label.setMinimumHeight(120)
        self.description_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        desc_widget.addWidget(self.description_label, 1)

        layout.addLayout(desc_widget)

        # Tip
        tip_label = QLabel(self.tr("Tip: Check the documentation (F1) for quick help!"))
        tip_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(tip_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.open_btn = QPushButton(self.tr("Open"))
        self.open_btn.setDefault(True)
        self.open_btn.setEnabled(False)  # Enabled when a tutorial is selected.
        self.open_btn.clicked.connect(self._open_selected_tutorial)
        button_layout.addWidget(self.open_btn)

        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _update_open_button(self):
        """Enable Open only when a real (selectable) tutorial item is highlighted."""
        item = self.tutorial_list.currentItem()
        enabled = bool(item and (item.flags() & Qt.ItemIsEnabled) and isinstance(item.data(Qt.UserRole), dict))
        self.open_btn.setEnabled(enabled)

    def _open_selected_tutorial(self):
        """Shared open-action used by the Open button and Enter key."""
        item = self.tutorial_list.currentItem()
        if item is not None:
            self.on_tutorial_double_clicked(item)

    def load_tutorial_list(self):
        """Load the list of available tutorials"""
        self.tutorial_list.clear()
        self.description_label.setText(self.tr("Select a tutorial to see its description."))

        if not self.tutorials_path or not self.tutorials_path.exists():
            item = QListWidgetItem(self.tr("No tutorials folder found"))
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.tutorial_list.addItem(item)
            return

        # Check for index.json
        index_file = self.tutorials_path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)

                from config.editions import filter_tutorials_for_edition
                tutorials = filter_tutorials_for_edition(index_data.get('tutorials', []))
                for tutorial in tutorials:
                    title = tutorial.get('title', 'Untitled')
                    item = QListWidgetItem(title)
                    item.setData(Qt.UserRole, tutorial)
                    self.tutorial_list.addItem(item)
                # Placeholder when the edition-filtered index is empty (L1).
                if self.tutorial_list.count() == 0:
                    self.tutorial_list.addItem(self.tr("No tutorials available"))
                return
            except Exception as e:
                logger.error(f"Error loading tutorials index: {e}")

        # Fallback: scan for tutorial folders
        for folder in sorted(self.tutorials_path.iterdir()):
            if folder.is_dir() and not folder.name.startswith('.'):
                html_files = list(folder.glob("*.html"))
                if html_files:
                    title = folder.name.replace('_', ' ').title()
                    # Remove leading numbers like "01 " or "02 "
                    if len(title) > 3 and title[0:2].isdigit() and title[2] == ' ':
                        title = title[3:]
                    item = QListWidgetItem(title)
                    item.setData(Qt.UserRole, {
                        'folder': folder.name,
                        'title': title,
                        'description': f'Tutorial in {folder.name}'
                    })
                    self.tutorial_list.addItem(item)

        if self.tutorial_list.count() == 0:
            item = QListWidgetItem(self.tr("No tutorials available"))
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.tutorial_list.addItem(item)

    def on_tutorial_clicked(self, item):
        """Show description and thumbnail when tutorial is clicked"""
        tutorial_data = item.data(Qt.UserRole)
        if tutorial_data and isinstance(tutorial_data, dict):
            description = tutorial_data.get('description', '')
            pages = tutorial_data.get('pages', [])
            page_count = len(pages) if pages else '?'

            text = f"<b>{tutorial_data.get('title', '')}</b><br>"
            if description:
                text += f"{description}<br>"
            text += f"<i>{self.tr('Pages:')} {page_count}</i>"

            self.description_label.setText(text)

            # Load thumbnail
            thumbnail = tutorial_data.get('thumbnail', '')
            if thumbnail and self.base_tutorials_path:
                thumb_path = self.base_tutorials_path / thumbnail
                if thumb_path.exists():
                    pixmap = QPixmap(str(thumb_path))
                    self.thumbnail_label.setPixmap(
                        pixmap.scaled(160, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    )
                else:
                    self.thumbnail_label.clear()
            else:
                self.thumbnail_label.clear()

    def on_tutorial_double_clicked(self, item):
        """Open tutorial when double-clicked"""
        tutorial_data = item.data(Qt.UserRole)
        if tutorial_data and isinstance(tutorial_data, dict):
            self.selected_tutorial = tutorial_data
            self.accept()  # Close dialog and return Accepted
