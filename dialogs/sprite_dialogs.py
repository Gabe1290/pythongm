#!/usr/bin/env python3
from PySide6.QtWidgets import QDialog

class SpriteImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Sprite")

class SpriteEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sprite Editor")
