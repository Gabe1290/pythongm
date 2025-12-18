#!/usr/bin/env python3
"""
Tutorial Panel Widget for PyGameMaker IDE
Displays HTML tutorials in the right panel, similar to GameMaker 8
"""
import json
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QListWidgetItem,
                               QStackedWidget, QTextBrowser, QSplitter,
                               QGroupBox, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QFont, QDesktopServices


class TutorialPanel(QWidget):
    """Panel for displaying HTML tutorials like GameMaker 8"""

    # Signal emitted when user wants to close tutorials
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tutorials_path = None
        self.current_tutorial = None
        self.current_page_index = 0
        self.tutorial_pages = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header with title and close button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(self.tr("<b>Tutorials</b>"))
        title_label.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.close_btn = QPushButton(self.tr("Close"))
        self.close_btn.setMaximumWidth(60)
        self.close_btn.clicked.connect(self.close_requested.emit)
        header_layout.addWidget(self.close_btn)

        layout.addWidget(header)

        # Stacked widget to switch between tutorial list and tutorial content
        self.stack = QStackedWidget()

        # Page 0: Tutorial list
        self.list_page = QWidget()
        list_layout = QVBoxLayout(self.list_page)
        list_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel(self.tr("Select a tutorial:"))
        list_layout.addWidget(list_label)

        self.tutorial_list = QListWidget()
        self.tutorial_list.itemDoubleClicked.connect(self.on_tutorial_selected)
        list_layout.addWidget(self.tutorial_list)

        open_btn = QPushButton(self.tr("Open Tutorial"))
        open_btn.clicked.connect(self.open_selected_tutorial)
        list_layout.addWidget(open_btn)

        self.stack.addWidget(self.list_page)

        # Page 1: Tutorial content viewer
        self.content_page = QWidget()
        content_layout = QVBoxLayout(self.content_page)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Tutorial title
        self.tutorial_title = QLabel()
        self.tutorial_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.tutorial_title.setWordWrap(True)
        content_layout.addWidget(self.tutorial_title)

        # Page indicator
        self.page_indicator = QLabel()
        self.page_indicator.setStyleSheet("color: gray; font-size: 10px;")
        content_layout.addWidget(self.page_indicator)

        # HTML content browser
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(False)
        self.content_browser.anchorClicked.connect(self.on_link_clicked)
        content_layout.addWidget(self.content_browser)

        # Navigation buttons
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 5, 0, 0)

        self.back_to_list_btn = QPushButton(self.tr("Back to List"))
        self.back_to_list_btn.clicked.connect(self.show_tutorial_list)
        nav_layout.addWidget(self.back_to_list_btn)

        nav_layout.addStretch()

        self.prev_btn = QPushButton(self.tr("< Previous"))
        self.prev_btn.clicked.connect(self.previous_page)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton(self.tr("Next >"))
        self.next_btn.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_btn)

        content_layout.addWidget(nav_widget)

        self.stack.addWidget(self.content_page)

        layout.addWidget(self.stack)

        # Start with tutorial list
        self.stack.setCurrentIndex(0)

    def set_tutorials_path(self, path):
        """Set the path to the Tutorials folder and load available tutorials"""
        self.base_tutorials_path = Path(path)
        self.tutorials_path = self._get_localized_tutorials_path()
        self.load_tutorial_list()

    def _get_localized_tutorials_path(self):
        """Get the tutorials path for the current language, falling back to English"""
        if not self.base_tutorials_path:
            return None

        # Get current language
        try:
            from core.language_manager import get_language_manager
            language_manager = get_language_manager()
            current_lang = language_manager.get_current_language()
        except Exception:
            current_lang = 'en'

        # Check for language-specific folder
        if current_lang and current_lang != 'en':
            localized_path = self.base_tutorials_path / current_lang
            if localized_path.exists() and (localized_path / "index.json").exists():
                return localized_path

        # Fall back to base path (English)
        return self.base_tutorials_path

    def load_tutorial_list(self):
        """Load the list of available tutorials from the Tutorials folder"""
        self.tutorial_list.clear()

        if not self.tutorials_path or not self.tutorials_path.exists():
            self.tutorial_list.addItem(self.tr("No tutorials folder found"))
            return

        # Check for index.json
        index_file = self.tutorials_path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)

                for tutorial in index_data.get('tutorials', []):
                    item = QListWidgetItem(tutorial.get('title', 'Untitled'))
                    item.setData(Qt.UserRole, tutorial)
                    self.tutorial_list.addItem(item)
                return
            except Exception as e:
                print(f"Error loading tutorials index: {e}")

        # Fallback: scan for tutorial folders
        for folder in sorted(self.tutorials_path.iterdir()):
            if folder.is_dir() and not folder.name.startswith('.'):
                # Look for tutorial.json or HTML files in the folder
                tutorial_json = folder / "tutorial.json"
                if tutorial_json.exists():
                    try:
                        with open(tutorial_json, 'r', encoding='utf-8') as f:
                            tutorial_data = json.load(f)
                            tutorial_data['folder'] = str(folder)
                            item = QListWidgetItem(tutorial_data.get('title', folder.name))
                            item.setData(Qt.UserRole, tutorial_data)
                            self.tutorial_list.addItem(item)
                    except Exception as e:
                        print(f"Error loading tutorial {folder}: {e}")
                else:
                    # Check if folder contains HTML files
                    html_files = list(folder.glob("*.html"))
                    if html_files:
                        item = QListWidgetItem(folder.name.replace('_', ' ').title())
                        item.setData(Qt.UserRole, {'folder': str(folder), 'title': folder.name})
                        self.tutorial_list.addItem(item)

        if self.tutorial_list.count() == 0:
            self.tutorial_list.addItem(self.tr("No tutorials available"))

    def on_tutorial_selected(self, item):
        """Handle double-click on a tutorial item"""
        self.open_tutorial(item)

    def open_selected_tutorial(self):
        """Open the currently selected tutorial"""
        item = self.tutorial_list.currentItem()
        if item:
            self.open_tutorial(item)

    def open_tutorial(self, item):
        """Open a tutorial from a list item and display its first page"""
        tutorial_data = item.data(Qt.UserRole)
        if not tutorial_data or not isinstance(tutorial_data, dict):
            return
        self.open_tutorial_by_data(tutorial_data)

    def open_tutorial_by_data(self, tutorial_data):
        """Open a tutorial by its data dictionary and display its first page"""
        if not tutorial_data or not isinstance(tutorial_data, dict):
            return

        folder_name = tutorial_data.get('folder')
        if not folder_name:
            # Try to construct path from title
            title = tutorial_data.get('title', '')
            folder_name = title.lower().replace(' ', '_')

        # Join with tutorials_path to get the full path
        folder = self.tutorials_path / folder_name
        if not folder.exists():
            self.content_browser.setHtml(
                f"<h3>{self.tr('Tutorial not found')}</h3>"
                f"<p>{self.tr('The tutorial folder does not exist:')}<br>{folder}</p>"
            )
            self.stack.setCurrentIndex(1)
            return

        self.current_tutorial = tutorial_data
        self.tutorial_title.setText(tutorial_data.get('title', folder.name))

        # Load pages from folder
        self.tutorial_pages = []

        # Check for pages list in tutorial.json
        pages = tutorial_data.get('pages', [])
        if pages:
            for page in pages:
                page_file = folder / page
                if page_file.exists():
                    self.tutorial_pages.append(page_file)
        else:
            # Scan for HTML files and sort them
            html_files = sorted(folder.glob("*.html"))
            self.tutorial_pages = list(html_files)

        if not self.tutorial_pages:
            self.content_browser.setHtml(
                f"<h3>{self.tr('No content')}</h3>"
                f"<p>{self.tr('This tutorial has no HTML pages.')}</p>"
            )
        else:
            self.current_page_index = 0
            self.load_current_page()

        self.stack.setCurrentIndex(1)
        self.update_navigation_buttons()

    def load_current_page(self):
        """Load and display the current tutorial page"""
        if not self.tutorial_pages or self.current_page_index >= len(self.tutorial_pages):
            return

        page_file = self.tutorial_pages[self.current_page_index]

        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Set search paths for relative image paths
            self.content_browser.setSearchPaths([str(page_file.parent)])
            self.content_browser.setHtml(html_content)

        except Exception as e:
            self.content_browser.setHtml(
                f"<h3>{self.tr('Error loading page')}</h3>"
                f"<p>{str(e)}</p>"
            )

        self.update_page_indicator()

    def update_page_indicator(self):
        """Update the page number indicator"""
        total = len(self.tutorial_pages)
        current = self.current_page_index + 1
        self.page_indicator.setText(self.tr("Page {0} of {1}").format(current, total))

    def update_navigation_buttons(self):
        """Enable/disable navigation buttons based on current page"""
        self.prev_btn.setEnabled(self.current_page_index > 0)
        self.next_btn.setEnabled(self.current_page_index < len(self.tutorial_pages) - 1)

    def previous_page(self):
        """Go to the previous tutorial page"""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.load_current_page()
            self.update_navigation_buttons()

    def next_page(self):
        """Go to the next tutorial page"""
        if self.current_page_index < len(self.tutorial_pages) - 1:
            self.current_page_index += 1
            self.load_current_page()
            self.update_navigation_buttons()

    def show_tutorial_list(self):
        """Return to the tutorial list view"""
        self.stack.setCurrentIndex(0)
        self.current_tutorial = None
        self.tutorial_pages = []
        self.current_page_index = 0

    def on_link_clicked(self, url):
        """Handle clicks on links in the tutorial content"""
        url_string = url.toString()

        # Check if it's an external link
        if url_string.startswith('http://') or url_string.startswith('https://'):
            QDesktopServices.openUrl(url)
        elif url_string.endswith('.html'):
            # Internal link to another page
            # Try to find and navigate to that page
            for i, page in enumerate(self.tutorial_pages):
                if page.name == url.fileName():
                    self.current_page_index = i
                    self.load_current_page()
                    self.update_navigation_buttons()
                    break
