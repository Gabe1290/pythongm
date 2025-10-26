#!/usr/bin/env python3
from pathlib import Path
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Signal

class EventActionWidget(QWidget):
    actionSelected = Signal(str)
    eventSelected = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Events & Actions"))

    def set_project(self, project_path: str, project_data: dict):
        """Set project for event actions panel - ADDED to fix AttributeError"""
        try:
            self.current_project_path = project_path
            self.current_project_data = project_data
            print(f"✅ Event actions panel set to project: {Path(project_path).name}")
        except Exception as e:
            print(f"❌ Error setting project in event actions panel: {e}")

# All possible aliases
EventActionsPanel = EventActionWidget
EventActionPanel = EventActionWidget
ActionsWidget = EventActionWidget
EventsWidget = EventActionWidget
