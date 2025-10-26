#!/usr/bin/env python3
from PySide6.QtWidgets import QDialog

class ObjectEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Object Editor")

class EventEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Event Editor")
