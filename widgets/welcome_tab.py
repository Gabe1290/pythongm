#!/usr/bin/env python3
"""
Welcome Tab Widget for PyGameMaker IDE
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt


class WelcomeTab(QWidget):
    """Welcome tab shown when no editors are open"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Welcome message
        title = QLabel(self.tr("Welcome to PyGameMaker IDE"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        
        subtitle = QLabel(self.tr("Create amazing 2D games with visual scripting"))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #666; margin: 10px;")
        
        # Quick actions
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.Box)
        actions_frame.setMaximumWidth(400)
        actions_layout = QVBoxLayout(actions_frame)
        
        actions_title = QLabel(self.tr("Quick Actions"))
        actions_title.setAlignment(Qt.AlignCenter)
        actions_title.setStyleSheet("font-weight: bold; margin: 10px;")
        
        new_project_btn = QPushButton(self.tr("🆕 New Project (Ctrl+N)"))
        open_project_btn = QPushButton(self.tr("📂 Open Project (Ctrl+O)"))
        new_room_btn = QPushButton(self.tr("🏠 Create Room (Ctrl+R)"))
        
        for btn in [new_project_btn, open_project_btn, new_room_btn]:
            btn.setStyleSheet("QPushButton { padding: 8px; margin: 2px; text-align: left; }")
        
        # Connect buttons to main window actions
        if self.main_window:
            new_project_btn.clicked.connect(self.main_window.new_project)
            open_project_btn.clicked.connect(self.main_window.open_project)
            new_room_btn.clicked.connect(self.main_window.create_room)
        
        actions_layout.addWidget(actions_title)
        actions_layout.addWidget(new_project_btn)
        actions_layout.addWidget(open_project_btn)
        actions_layout.addWidget(new_room_btn)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(actions_frame)