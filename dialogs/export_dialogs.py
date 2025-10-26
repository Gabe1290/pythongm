#!/usr/bin/env python3
from PySide6.QtWidgets import QDialog

class GameExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Game")

class BuildSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Build Settings")
