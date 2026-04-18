#!/usr/bin/env python3
"""
Named color manager for the Playground Editor.
Manages the palette of named colors used in Aseba playground files.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QColorDialog, QInputDialog,
    QMessageBox,
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QColor, QPixmap, QIcon


class PlaygroundColorManager(QWidget):
    """Widget for managing named colors in a playground"""

    colors_changed = Signal(list)  # list of {"name", "r", "g", "b"} dicts

    def __init__(self, parent=None):
        super().__init__(parent)
        self._colors = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        title = QLabel(self.tr("Colors"))
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.color_list = QListWidget()
        self.color_list.setMaximumHeight(120)
        self.color_list.itemDoubleClicked.connect(self._on_edit_color)
        layout.addWidget(self.color_list)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(2)

        add_btn = QPushButton("+")
        add_btn.setFixedWidth(30)
        add_btn.setToolTip(self.tr("Add color"))
        add_btn.clicked.connect(self._on_add_color)
        btn_row.addWidget(add_btn)

        remove_btn = QPushButton("-")
        remove_btn.setFixedWidth(30)
        remove_btn.setToolTip(self.tr("Remove color"))
        remove_btn.clicked.connect(self._on_remove_color)
        btn_row.addWidget(remove_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def set_colors(self, colors):
        """Load colors into the list"""
        self._colors = list(colors) if colors else []
        self._refresh_list()

    def get_colors(self):
        """Get current color list"""
        return list(self._colors)

    def get_color_names(self):
        """Get list of color names"""
        return [c['name'] for c in self._colors]

    def _refresh_list(self):
        """Rebuild the list widget"""
        self.color_list.clear()
        for c in self._colors:
            qc = QColor(int(c['r'] * 255), int(c['g'] * 255), int(c['b'] * 255))
            pixmap = QPixmap(16, 16)
            pixmap.fill(qc)
            item = QListWidgetItem(QIcon(pixmap), c['name'])
            self.color_list.addItem(item)

    def _on_add_color(self):
        name, ok = QInputDialog.getText(
            self, self.tr("Add Color"), self.tr("Color name:"))
        if not ok or not name.strip():
            return
        name = name.strip()
        # Check for duplicate
        if any(c['name'] == name for c in self._colors):
            QMessageBox.warning(self, self.tr("Duplicate"),
                                self.tr("A color named '{}' already exists.").format(name))
            return
        color = QColorDialog.getColor(QColor(180, 180, 180), self,
                                       self.tr("Choose Color"))
        if not color.isValid():
            return
        self._colors.append({
            'name': name,
            'r': round(color.redF(), 3),
            'g': round(color.greenF(), 3),
            'b': round(color.blueF(), 3),
        })
        self._refresh_list()
        self.colors_changed.emit(self._colors)

    def _on_remove_color(self):
        item = self.color_list.currentItem()
        if not item:
            return
        name = item.text()
        self._colors = [c for c in self._colors if c['name'] != name]
        self._refresh_list()
        self.colors_changed.emit(self._colors)

    def _on_edit_color(self, item):
        """Double-click to change a color's RGB value"""
        name = item.text()
        existing = next((c for c in self._colors if c['name'] == name), None)
        if not existing:
            return
        current = QColor(int(existing['r'] * 255),
                          int(existing['g'] * 255),
                          int(existing['b'] * 255))
        color = QColorDialog.getColor(current, self, self.tr("Edit Color"))
        if not color.isValid():
            return
        existing['r'] = round(color.redF(), 3)
        existing['g'] = round(color.greenF(), 3)
        existing['b'] = round(color.blueF(), 3)
        self._refresh_list()
        self.colors_changed.emit(self._colors)
