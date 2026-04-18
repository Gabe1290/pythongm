#!/usr/bin/env python3
"""
Tool palette for the Playground Editor.
Provides Select, Wall, and Robot mode buttons.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup,
)
from PySide6.QtCore import Signal, Qt


class PlaygroundToolPalette(QWidget):
    """Tool selection palette for playground editing modes"""

    mode_changed = Signal(str)  # "select", "wall", "robot"

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        title = QLabel(self.tr("Tools"))
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.select_btn = QPushButton(self.tr("Select"))
        self.select_btn.setCheckable(True)
        self.select_btn.setChecked(True)
        self.select_btn.setToolTip(self.tr("Select and move elements"))
        self.button_group.addButton(self.select_btn, 0)
        layout.addWidget(self.select_btn)

        self.wall_btn = QPushButton(self.tr("Wall"))
        self.wall_btn.setCheckable(True)
        self.wall_btn.setToolTip(self.tr("Click to place walls"))
        self.button_group.addButton(self.wall_btn, 1)
        layout.addWidget(self.wall_btn)

        self.robot_btn = QPushButton(self.tr("Robot"))
        self.robot_btn.setCheckable(True)
        self.robot_btn.setToolTip(self.tr("Click to place robots"))
        self.button_group.addButton(self.robot_btn, 2)
        layout.addWidget(self.robot_btn)

        self.block_btn = QPushButton(self.tr("Block"))
        self.block_btn.setCheckable(True)
        self.block_btn.setToolTip(self.tr("Paint cube blocks on a grid (Minecraft-style)"))
        self.button_group.addButton(self.block_btn, 3)
        layout.addWidget(self.block_btn)

        layout.addStretch()

        self.button_group.idClicked.connect(self._on_button_clicked)

    def _on_button_clicked(self, button_id):
        modes = {0: "select", 1: "wall", 2: "robot", 3: "block"}
        self.mode_changed.emit(modes.get(button_id, "select"))

    def set_mode(self, mode):
        """Programmatically set the active mode"""
        mode_map = {"select": 0, "wall": 1, "robot": 2, "block": 3}
        btn_id = mode_map.get(mode, 0)
        btn = self.button_group.button(btn_id)
        if btn:
            btn.setChecked(True)
