#!/usr/bin/env python3
"""
Color Palette Widget for the Sprite Editor.
Foreground/background swatches, quick-access color grid, QColorDialog integration.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QColorDialog, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QColor, QPainter, QPen, QMouseEvent


# Default 16-color palette (classic pixel-art palette)
DEFAULT_COLORS = [
    "#000000", "#FFFFFF", "#FF0000", "#00FF00",
    "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
    "#808080", "#C0C0C0", "#800000", "#008000",
    "#000080", "#808000", "#800080", "#008080",
]


class ColorSwatch(QWidget):
    """A small clickable color square."""

    clicked = Signal(QColor)

    def __init__(self, color: QColor, size: int = 20, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)

    def set_color(self, color: QColor):
        self._color = color
        self.update()

    def get_color(self) -> QColor:
        return self._color

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._color)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        # Double-click opens color dialog to change this swatch
        if event.button() == Qt.LeftButton:
            color = QColorDialog.getColor(self._color, self, self.tr("Choose Color"),
                                          QColorDialog.ShowAlphaChannel)
            if color.isValid():
                self._color = color
                self.update()
                self.clicked.emit(color)

    def paintEvent(self, event):
        painter = QPainter(self)
        # Checkerboard behind (for alpha)
        cs = 5
        for r in range(self.height() // cs + 1):
            for c in range(self.width() // cs + 1):
                col = QColor(204, 204, 204) if (r + c) % 2 == 0 else QColor(170, 170, 170)
                painter.fillRect(c * cs, r * cs, cs, cs, col)
        # Color fill
        painter.fillRect(self.rect(), self._color)
        # Border
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        painter.end()


class ForegroundBackgroundSwatch(QWidget):
    """Overlapping foreground/background color display (like Photoshop)."""

    color_changed = Signal(QColor)  # emits the new foreground color

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fg = QColor(0, 0, 0, 255)
        self._bg = QColor(255, 255, 255, 255)
        self.setFixedSize(48, 48)
        self.setCursor(Qt.PointingHandCursor)

    def get_foreground(self) -> QColor:
        return self._fg

    def set_foreground(self, color: QColor):
        self._fg = color
        self.update()

    def get_background(self) -> QColor:
        return self._bg

    def set_background(self, color: QColor):
        self._bg = color
        self.update()

    def swap_colors(self):
        self._fg, self._bg = self._bg, self._fg
        self.update()
        self.color_changed.emit(self._fg)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Click on the foreground area (top-left bigger square)
            color = QColorDialog.getColor(self._fg, self, self.tr("Foreground Color"),
                                          QColorDialog.ShowAlphaChannel)
            if color.isValid():
                self._fg = color
                self.update()
                self.color_changed.emit(self._fg)
        elif event.button() == Qt.RightButton:
            color = QColorDialog.getColor(self._bg, self, self.tr("Background Color"),
                                          QColorDialog.ShowAlphaChannel)
            if color.isValid():
                self._bg = color
                self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Background swatch (bottom-right, smaller)
        bg_rect = QRect(16, 16, 28, 28)
        painter.fillRect(bg_rect, self._bg)
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawRect(bg_rect)

        # Foreground swatch (top-left, larger, on top)
        fg_rect = QRect(0, 0, 30, 30)
        painter.fillRect(fg_rect, self._fg)
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(fg_rect)
        painter.end()


class ColorPaletteWidget(QWidget):
    """Complete color palette: foreground/background + color grid."""

    color_selected = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Top row: FG/BG swatch + swap button
        top_row = QHBoxLayout()
        self._fb_swatch = ForegroundBackgroundSwatch()
        self._fb_swatch.color_changed.connect(self.color_selected.emit)
        top_row.addWidget(self._fb_swatch)

        swap_btn_widget = QLabel("X")
        swap_btn_widget.setToolTip(self.tr("Swap foreground/background"))
        swap_btn_widget.setAlignment(Qt.AlignCenter)
        swap_btn_widget.setFixedSize(16, 16)
        swap_btn_widget.setCursor(Qt.PointingHandCursor)
        swap_btn_widget.mousePressEvent = lambda e: self._fb_swatch.swap_colors()
        top_row.addWidget(swap_btn_widget)
        top_row.addStretch()

        layout.addLayout(top_row)

        # Color grid
        grid = QGridLayout()
        grid.setSpacing(2)
        self._swatches = []

        for i, hex_color in enumerate(DEFAULT_COLORS):
            swatch = ColorSwatch(QColor(hex_color), size=18)
            swatch.clicked.connect(self._on_swatch_clicked)
            row, col = divmod(i, 4)
            grid.addWidget(swatch, row, col)
            self._swatches.append(swatch)

        layout.addLayout(grid)

    def _on_swatch_clicked(self, color: QColor):
        self._fb_swatch.set_foreground(color)
        self.color_selected.emit(color)

    def get_foreground(self) -> QColor:
        return self._fb_swatch.get_foreground()

    def set_foreground(self, color: QColor):
        self._fb_swatch.set_foreground(color)

    def get_background(self) -> QColor:
        return self._fb_swatch.get_background()
