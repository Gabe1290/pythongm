#!/usr/bin/env python3
"""
About Dialog for PyGameMaker IDE
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class AboutDialog(QDialog):
    """About dialog for the IDE"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("About PyGameMaker IDE"))
        self.setModal(True)
        self.resize(450, 350)
        self.setup_ui()

    def setup_ui(self):
        """Setup the about dialog UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(self.tr("PyGameMaker IDE"))
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Version
        version = QLabel(self.tr("Version 0.10.0-alpha"))
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # GitHub link
        github_label = QLabel('<a href="https://github.com/Gabe1290/pythongm">https://github.com/Gabe1290/pythongm</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(github_label)

        # Tabs
        tabs = QTabWidget()

        # About tab
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)

        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml(self.tr("<h3>PyGameMaker IDE</h3><p>A GameMaker-inspired IDE for creating 2D games with Python.</p><h4>Features:</h4><ul><li>Visual scripting with events and actions</li><li>Asset management for sprites, sounds, and objects</li><li>Room-based game development</li><li>Export to standalone Python games</li></ul><h4>Built with:</h4><ul><li>PySide6 for the user interface</li><li>Pygame for game runtime</li><li>Python 3.11+</li></ul>"))

        about_layout.addWidget(about_text)
        tabs.addTab(about_tab, self.tr("About"))

        # Credits tab
        credits_tab = QWidget()
        credits_layout = QVBoxLayout(credits_tab)

        credits_text = QTextEdit()
        credits_text.setReadOnly(True)
        credits_text.setPlainText(self.tr("Credits:\n\nDevelopment:\n- Gabriel Thullen\n\nSpecial Thanks:\n- The GameMaker Studio community for inspiration\n- The Python and Pygame communities\n- All contributors and testers\n\nThird-Party Libraries:\n- PySide6 (Qt for Python) - LGPLv3\n- Pygame (game development library) - LGPLv2.1\n- Pillow (image processing) - HPND\n- Blockly (visual programming) - Apache 2.0\n\nLicense:\nThis software is released under the GNU General Public License v3 (GPLv3).\nCopyright (C) 2024-2025 Gabriel Thullen"))

        credits_layout.addWidget(credits_text)
        tabs.addTab(credits_tab, self.tr("Credits"))

        layout.addWidget(tabs)

        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton(self.tr("Close"))
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)

        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
