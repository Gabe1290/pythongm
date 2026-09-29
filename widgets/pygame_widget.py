#!/usr/bin/env python3
"""A Qt widget that displays a pygame surface (docs/THYMIO_EXTENSION_PLAN.md,
Stage C3). Extracted out of ``widgets/thymio_playground.py`` before that file
moved into ``extensions/thymio/`` — this class has zero Thymio-specific code
(it's pygame-surface-to-QPixmap plumbing plus Qt input forwarding) and
``editors/block_world_editor/window.py`` reuses it verbatim for its own
build-mode camera. Two independent extensions must not depend on each
other, so this stays in core, shared by both.
"""
import pygame

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap, QKeyEvent, QMouseEvent


class PygameWidget(QLabel):
    """
    Qt widget that displays a pygame surface.
    Handles keyboard and mouse input and passes it to the playground.
    """

    key_pressed = Signal(int)
    key_released = Signal(int)
    mouse_pressed = Signal(int, int, int)   # x, y, button
    mouse_released = Signal(int, int, int)  # x, y, button
    mouse_moved = Signal(int, int)          # x, y
    mouse_wheel = Signal(int, int, int)     # x, y, delta (positive=up/zoom in)

    def __init__(self, width: int, height: int, parent=None):
        super().__init__(parent)
        self.surface_width = width
        self.surface_height = height

        # Create pygame surface (off-screen rendering)
        pygame.init()
        self.surface = pygame.Surface((width, height))

        # Set fixed size
        self.setFixedSize(width, height)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        # Style
        self.setStyleSheet("border: 2px solid #888;")

    def get_surface(self) -> pygame.Surface:
        """Get the pygame surface for drawing"""
        return self.surface

    def resize_surface(self, width: int, height: int):
        """Resize the pygame surface and widget"""
        self.surface_width = width
        self.surface_height = height
        self.surface = pygame.Surface((width, height))
        self.setFixedSize(width, height)

    def update_display(self):
        """Convert pygame surface to Qt pixmap and display"""
        # Get raw pixel data from pygame surface
        data = pygame.image.tostring(self.surface, 'RGB')

        # Create QImage from raw data
        image = QImage(data, self.surface_width, self.surface_height,
                       self.surface_width * 3, QImage.Format_RGB888)

        # Convert to pixmap and display
        pixmap = QPixmap.fromImage(image)
        self.setPixmap(pixmap)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        self.key_pressed.emit(event.key())
        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release events"""
        self.key_released.emit(event.key())
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        pos = event.position().toPoint()
        self.mouse_pressed.emit(pos.x(), pos.y(), event.button())
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events"""
        pos = event.position().toPoint()
        self.mouse_released.emit(pos.x(), pos.y(), event.button())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events"""
        pos = event.position().toPoint()
        self.mouse_moved.emit(pos.x(), pos.y())
        event.accept()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        pos = event.position().toPoint()
        # angleDelta().y() is positive for scrolling up, negative for down
        delta = event.angleDelta().y()
        self.mouse_wheel.emit(pos.x(), pos.y(), delta)
        event.accept()
