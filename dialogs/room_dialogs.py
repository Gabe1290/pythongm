#!/usr/bin/env python3
from PySide6.QtWidgets import QDialog

class RoomEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Room Editor")

class RoomSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Room Settings")
