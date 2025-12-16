#!/usr/bin/env python3
"""
Tutorial Selection Dialog for PyGameMaker IDE
Displays a list of available tutorials - selection opens in preview panel
"""
import json
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QListWidgetItem,
                               QTextBrowser)
from PySide6.QtCore import Qt


class TutorialDialog(QDialog):
    """Dialog for selecting tutorials - displays in preview panel when selected"""

    def __init__(self, parent=None, tutorials_path=None):
        super().__init__(parent)
        self.tutorials_path = Path(tutorials_path) if tutorials_path else None
        self.selected_tutorial = None

        self.setWindowTitle(self.tr("Tutorials"))
        self.setMinimumSize(500, 400)
        self.resize(550, 450)

        self.setup_ui()
        self.load_tutorial_list()

    def get_selected_tutorial(self):
        """Return the selected tutorial data"""
        return self.selected_tutorial

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(self.tr("<h2>PyGameMaker Tutorials</h2>"))
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(self.tr("Double-click a tutorial to start:"))
        layout.addWidget(instructions)

        # Tutorial list
        self.tutorial_list = QListWidget()
        self.tutorial_list.itemClicked.connect(self.on_tutorial_clicked)
        self.tutorial_list.itemDoubleClicked.connect(self.on_tutorial_double_clicked)
        layout.addWidget(self.tutorial_list)

        # Description area
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(
            "QLabel { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }"
        )
        self.description_label.setMinimumHeight(60)
        layout.addWidget(self.description_label)

        # Tip
        tip_label = QLabel(self.tr("Tip: Check the documentation (F1) for quick help!"))
        tip_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(tip_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

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

                for tutorial in index_data.get('tutorials', []):
                    title = tutorial.get('title', 'Untitled')
                    item = QListWidgetItem(title)
                    item.setData(Qt.UserRole, tutorial)
                    self.tutorial_list.addItem(item)
                return
            except Exception as e:
                print(f"Error loading tutorials index: {e}")

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
        """Show description when tutorial is clicked"""
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

    def on_tutorial_double_clicked(self, item):
        """Open tutorial when double-clicked"""
        tutorial_data = item.data(Qt.UserRole)
        if tutorial_data and isinstance(tutorial_data, dict):
            self.selected_tutorial = tutorial_data
            self.accept()  # Close dialog and return Accepted
