#!/usr/bin/env python3
"""
Object Editor Components - Simplified
Only contains placeholder widgets
"""

from typing import Dict, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


class ActionListWidget(QWidget):
    """Widget for displaying available actions - PLACEHOLDER"""
    action_selected = Signal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # ✅ TRANSLATABLE: Placeholder message
        label = QLabel(self.tr("Actions are now managed through the Events panel"))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(label)


class VisualScriptingArea(QWidget):
    """Area for visual script editing - PLACEHOLDER"""
    script_modified = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_event = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # ✅ TRANSLATABLE: Placeholder message
        label = QLabel(self.tr("Visual scripting is now managed through the Events panel"))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(label)
    
    def set_current_event(self, event_name: str):
        self.current_event = event_name
    
    def get_script_data(self) -> Dict[str, List]:
        return {}