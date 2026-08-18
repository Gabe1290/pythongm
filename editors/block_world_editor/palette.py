#!/usr/bin/env python3
"""BlockPalette -- a scrollable grid of clickable block-type swatches,
mirroring editors/room_editor/tile_palette.py's interaction shape (click
a swatch, it becomes the current placement choice) for "which block type"
instead of "which tile."
"""
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QGridLayout, QPushButton, QScrollArea, QWidget

from extensions.block_world.state import BLOCK_TYPES, block_face_textures

SWATCH_SIZE = 48
ICON_SIZE = 40
COLUMNS = 4


class BlockPalette(QScrollArea):
    """Emits block_selected(block_type) whenever the current swatch
    changes -- by click, or programmatically via select()."""

    block_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self._buttons = {}
        self._current = None
        self._build_ui()

    def _build_ui(self):
        content = QWidget()
        layout = QGridLayout(content)
        layout.setSpacing(4)

        for i, block_type in enumerate(sorted(BLOCK_TYPES)):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setFixedSize(SWATCH_SIZE, SWATCH_SIZE)
            btn.setToolTip(block_type)

            pix = QPixmap(block_face_textures(block_type)["top"])
            if not pix.isNull():
                btn.setIcon(QIcon(pix.scaled(
                    ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))

            btn.clicked.connect(lambda checked, bt=block_type: self.select(bt))
            layout.addWidget(btn, i // COLUMNS, i % COLUMNS)
            self._buttons[block_type] = btn

        content.setLayout(layout)
        self.setWidget(content)

    def select(self, block_type: str) -> None:
        """Make block_type the current selection. A no-op for an unknown
        type (defensive -- callers should validate against BLOCK_TYPES,
        but a bad restore-from-save value must not crash the editor)."""
        if block_type not in self._buttons:
            return
        if self._current is not None and self._current in self._buttons:
            self._buttons[self._current].setChecked(False)
        self._current = block_type
        self._buttons[block_type].setChecked(True)
        self.block_selected.emit(block_type)

    def current_block(self):
        return self._current
