#!/usr/bin/env python3
"""
Preferences Dialog for PyGameMaker IDE
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QFormLayout, QSpinBox, QCheckBox,
    QPushButton, QLabel, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt, Signal

class PreferencesDialog(QDialog):
    """Dialog for IDE preferences"""
    
    preferencesChanged = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the preferences UI"""
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Window settings
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout(window_group)
        
        self.window_width = QSpinBox()
        self.window_width.setRange(800, 3000)
        self.window_width.setValue(1200)
        window_layout.addRow("Default Width:", self.window_width)
        
        self.window_height = QSpinBox()
        self.window_height.setRange(600, 2000)
        self.window_height.setValue(800)
        window_layout.addRow("Default Height:", self.window_height)
        
        self.maximize_on_start = QCheckBox("Maximize on startup")
        window_layout.addRow("", self.maximize_on_start)
        
        general_layout.addWidget(window_group)
        
        # Editor settings
        editor_group = QGroupBox("Editor Settings")
        editor_layout = QFormLayout(editor_group)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        editor_layout.addRow("Font Size:", self.font_size)
        
        self.auto_save = QCheckBox("Auto-save projects")
        self.auto_save.setChecked(True)
        editor_layout.addRow("", self.auto_save)
        
        general_layout.addWidget(editor_group)
        general_layout.addStretch()
        
        tabs.addTab(general_tab, "General")
        
        # Projects tab
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)
        
        projects_group = QGroupBox("Project Settings")
        projects_form = QFormLayout(projects_group)
        
        self.recent_projects = QSpinBox()
        self.recent_projects.setRange(5, 20)
        self.recent_projects.setValue(10)
        projects_form.addRow("Max Recent Projects:", self.recent_projects)
        
        projects_layout.addWidget(projects_group)
        projects_layout.addStretch()
        
        tabs.addTab(projects_tab, "Projects")
        
        layout.addWidget(tabs)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_preferences)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_preferences)
        self.ok_button.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
    def apply_preferences(self):
        """Apply preferences"""
        prefs = {
            'window_width': self.window_width.value(),
            'window_height': self.window_height.value(),
            'maximize_on_start': self.maximize_on_start.isChecked(),
            'font_size': self.font_size.value(),
            'auto_save': self.auto_save.isChecked(),
            'recent_projects': self.recent_projects.value()
        }
        self.preferencesChanged.emit(prefs)
        
    def accept_preferences(self):
        """Accept and apply preferences"""
        self.apply_preferences()
        self.accept()
