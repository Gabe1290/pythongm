#!/usr/bin/env python3
"""
Sprite Canvas Widget — the main pixel editing surface.

Inherits QAbstractScrollArea so it owns its own scrollbars.  When the
zoomed image is larger than the viewport, scrollbars appear automatically.
No external QScrollArea wrapper is needed.
"""

from PySide6.QtWidgets import QAbstractScrollArea, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize, QEvent
from PySide6.QtGui import (
    QImage, QPainter, QColor, QPen, QWheelEvent,
    QMouseEvent, QPaintEvent, QKeyEvent
)

from .sprite_tools import BaseTool


# Checkerboard tile size (in screen pixels)
_CHECKER_SIZE = 8
_CHECKER_LIGHT = QColor(255, 255, 255)
_CHECKER_DARK = QColor(235, 235, 235)

# Padding around the image (pixels, in content-space)
_MARGIN = 32


class SpriteCanvas(QAbstractScrollArea):
    """Pixel-art editing canvas with built-in scrollbars, zoom, and
    tool dispatch.

    Scrollbars appear when the zoomed image (+margin) exceeds the
    viewport.  Ctrl+Wheel zooms; plain Wheel scrolls.
    """

    # Emitted after any drawing operation modifies the image
    canvas_modified = Signal()
    # Emitted when the color picker picks a color
    color_picked = Signal(QColor)
    # Emitted when zoom changes (new zoom value)
    zoom_changed = Signal(int)
    # Clipboard / key signals (forwarded to SpriteEditor)
    copy_requested = Signal()
    cut_requested = Signal()
    paste_requested = Signal()
    delete_requested = Signal()
    key_pressed = Signal(int)  # forwards unhandled key for tool shortcuts
    context_menu_requested = Signal(QPoint)  # right-click global pos

    def __init__(self, parent=None):
        super().__init__(parent)

        # Canvas image (current frame being edited)
        self._image = QImage(32, 32, QImage.Format_ARGB32)
        self._image.fill(QColor(0, 0, 0, 0))

        # Snapshot before current stroke for undo
        self._stroke_snapshot = None

        # View state
        self._zoom = 10  # integer multiplier
        self._show_grid = True

        # Interaction state
        self._current_tool = None  # type: BaseTool | None
        self._current_color = QColor(0, 0, 0, 255)
        self._painting = False

        # Hover pixel for brush cursor overlay
        self._hover_pixel = None  # (px, py) or None when mouse outside

        # Viewport setup
        self.viewport().setMouseTracking(True)
        self.viewport().setFocusPolicy(Qt.StrongFocus)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFrameShape(QAbstractScrollArea.NoFrame)

        self._update_scrollbars()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_image(self, image: QImage):
        """Set the canvas image (e.g. when switching frames)."""
        self._image = image.convertToFormat(QImage.Format_ARGB32)
        self._update_scrollbars()
        self.viewport().update()

    def get_image(self) -> QImage:
        """Return the current canvas image."""
        return self._image

    def set_tool(self, tool: BaseTool):
        """Set the active drawing tool."""
        if self._current_tool:
            self._current_tool.reset()
        self._current_tool = tool

    def set_color(self, color: QColor):
        """Set the current drawing color."""
        self._current_color = color

    def set_zoom(self, zoom: int):
        """Set the zoom level (clamped to 1–64)."""
        self._zoom = max(1, min(64, zoom))
        self._update_scrollbars()
        self.zoom_changed.emit(self._zoom)
        self.viewport().update()

    def get_zoom(self) -> int:
        return self._zoom

    def set_show_grid(self, show: bool):
        self._show_grid = show
        self.viewport().update()

    def get_show_grid(self) -> bool:
        return self._show_grid

    def new_blank(self, width: int, height: int):
        """Create a new blank transparent image."""
        self._image = QImage(width, height, QImage.Format_ARGB32)
        self._image.fill(QColor(0, 0, 0, 0))
        self._update_scrollbars()
        self.viewport().update()

    def take_stroke_snapshot(self):
        """Save a snapshot before a stroke begins (for undo)."""
        self._stroke_snapshot = self._image.copy()

    def get_stroke_snapshot(self) -> QImage | None:
        """Return the pre-stroke snapshot."""
        return self._stroke_snapshot

    def clear_stroke_snapshot(self):
        self._stroke_snapshot = None

    # ------------------------------------------------------------------
    # Scrollbar management
    # ------------------------------------------------------------------

    def _content_size(self) -> QSize:
        """Total size of the zoomed image + margins."""
        return QSize(
            self._image.width() * self._zoom + 2 * _MARGIN,
            self._image.height() * self._zoom + 2 * _MARGIN,
        )

    def _update_scrollbars(self):
        """Recalculate scrollbar ranges based on zoom and viewport size."""
        vp = self.viewport().size()
        content = self._content_size()

        hs = self.horizontalScrollBar()
        hs.setRange(0, max(0, content.width() - vp.width()))
        hs.setPageStep(vp.width())

        vs = self.verticalScrollBar()
        vs.setRange(0, max(0, content.height() - vp.height()))
        vs.setPageStep(vp.height())

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _origin(self) -> tuple[int, int]:
        """Top-left corner of the image in viewport coordinates."""
        vp = self.viewport().size()
        content = self._content_size()

        # Centre when content fits; otherwise use scrollbar offset
        if content.width() <= vp.width():
            ox = (vp.width() - content.width()) // 2 + _MARGIN
        else:
            ox = _MARGIN - self.horizontalScrollBar().value()

        if content.height() <= vp.height():
            oy = (vp.height() - content.height()) // 2 + _MARGIN
        else:
            oy = _MARGIN - self.verticalScrollBar().value()

        return ox, oy

    def _screen_to_pixel(self, screen_pos: QPoint) -> tuple[int, int]:
        """Convert viewport coordinates to image pixel coordinates."""
        ox, oy = self._origin()
        x = int((screen_pos.x() - ox) / self._zoom)
        y = int((screen_pos.y() - oy) / self._zoom)
        return x, y

    # ------------------------------------------------------------------
    # Paint (on the viewport)
    # ------------------------------------------------------------------

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Background
        painter.fillRect(self.viewport().rect(), QColor(200, 200, 200))

        img_w = self._image.width()
        img_h = self._image.height()
        zoom = self._zoom
        ox, oy = self._origin()

        # Checkerboard (transparency indicator)
        self._draw_checkerboard(painter, ox, oy, img_w * zoom, img_h * zoom)

        # Draw the sprite image scaled to zoom
        target = QRect(ox, oy, img_w * zoom, img_h * zoom)
        painter.drawImage(target, self._image)

        # Draw tool preview overlay (line, rect, ellipse in-progress)
        if self._current_tool:
            preview = self._current_tool.get_preview()
            if preview:
                painter.drawImage(target, preview)

            # Draw floating selection overlay
            from .sprite_tools import SelectTool
            if isinstance(self._current_tool, SelectTool):
                fp = self._current_tool.get_floating_preview()
                if fp:
                    fimg, frect = fp
                    ftarget = QRect(
                        ox + frect.x() * zoom,
                        oy + frect.y() * zoom,
                        frect.width() * zoom,
                        frect.height() * zoom,
                    )
                    painter.drawImage(ftarget, fimg)

                # Draw selection rectangle
                sel = self._current_tool.selection_rect
                if sel:
                    pen = QPen(QColor(255, 255, 255, 200), 1, Qt.DashLine)
                    painter.setPen(pen)
                    painter.setBrush(Qt.NoBrush)
                    sel_screen = QRect(
                        ox + sel.x() * zoom,
                        oy + sel.y() * zoom,
                        sel.width() * zoom,
                        sel.height() * zoom,
                    )
                    painter.drawRect(sel_screen)

        # Grid overlay
        if self._show_grid and zoom >= 4:
            self._draw_grid(painter, ox, oy, img_w, img_h, zoom)

        # Brush cursor overlay
        if self._hover_pixel and self._current_tool:
            self._draw_brush_cursor(painter, ox, oy, zoom, img_w, img_h)

        painter.end()

    def _draw_checkerboard(self, painter: QPainter, ox, oy, w, h):
        """Draw a checkerboard pattern behind the image area."""
        painter.save()
        painter.setClipRect(QRect(ox, oy, w, h).intersected(self.viewport().rect()))
        cs = _CHECKER_SIZE
        cols = w // cs + 2
        rows = h // cs + 2
        for r in range(rows):
            for c in range(cols):
                color = _CHECKER_LIGHT if (r + c) % 2 == 0 else _CHECKER_DARK
                painter.fillRect(ox + c * cs, oy + r * cs, cs, cs, color)
        painter.restore()

    def _draw_grid(self, painter: QPainter, ox, oy, img_w, img_h, zoom):
        """Draw pixel grid lines."""
        pen = QPen(QColor(255, 255, 255, 40), 1)
        painter.setPen(pen)
        for x in range(img_w + 1):
            sx = ox + x * zoom
            painter.drawLine(sx, oy, sx, oy + img_h * zoom)
        for y in range(img_h + 1):
            sy = oy + y * zoom
            painter.drawLine(ox, sy, ox + img_w * zoom, sy)

    def _draw_brush_cursor(self, painter: QPainter, ox, oy, zoom, img_w, img_h):
        """Draw a cursor overlay showing the brush/eraser footprint."""
        from .sprite_tools import PencilTool, EraserTool
        tool = self._current_tool
        if not isinstance(tool, (PencilTool, EraserTool)):
            return

        px, py = self._hover_pixel
        half = tool.size // 2
        # Top-left pixel of the brush square
        bx = px - half
        by = py - half

        # Convert to screen coordinates
        sx = ox + bx * zoom
        sy = oy + by * zoom
        sw = tool.size * zoom
        sh = tool.size * zoom

        # Clip to image bounds
        img_rect = QRect(ox, oy, img_w * zoom, img_h * zoom)
        cursor_rect = QRect(sx, sy, sw, sh)
        if not img_rect.intersects(cursor_rect):
            return

        if isinstance(tool, EraserTool):
            # Semi-transparent red fill to show what will be erased
            painter.fillRect(cursor_rect, QColor(255, 80, 80, 50))
            pen = QPen(QColor(255, 80, 80, 160), 1)
        else:
            # Outline only for pencil
            pen = QPen(QColor(255, 255, 255, 160), 1)

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(cursor_rect)

    # ------------------------------------------------------------------
    # QAbstractScrollArea overrides
    # ------------------------------------------------------------------

    def sizeHint(self):
        return QSize(512, 512)

    def minimumSizeHint(self):
        return QSize(200, 200)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Enforce square: cap width to height so the canvas stays square
        h = event.size().height()
        if self.maximumWidth() != h:
            self.setMaximumWidth(h)
        self._update_scrollbars()

    def scrollContentsBy(self, dx, dy):
        self.viewport().update()

    # ------------------------------------------------------------------
    # Mouse events (forwarded from viewport by QAbstractScrollArea)
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._current_tool:
            px, py = self._screen_to_pixel(event.pos())
            self.take_stroke_snapshot()
            self._painting = True

            from .sprite_tools import ColorPickerTool
            self._current_tool.on_press(self._image, px, py, self._current_color)

            if isinstance(self._current_tool, ColorPickerTool) and self._current_tool.picked_color:
                self.color_picked.emit(self._current_tool.picked_color)

            self.viewport().update()

    def mouseMoveEvent(self, event: QMouseEvent):
        # Always track hover position for brush cursor overlay
        self._hover_pixel = self._screen_to_pixel(event.pos())
        if self._painting and self._current_tool:
            px, py = self._hover_pixel

            from .sprite_tools import ColorPickerTool
            self._current_tool.on_move(self._image, px, py, self._current_color)

            if isinstance(self._current_tool, ColorPickerTool) and self._current_tool.picked_color:
                self.color_picked.emit(self._current_tool.picked_color)

        self.viewport().update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._painting and self._current_tool:
            px, py = self._screen_to_pixel(event.pos())
            self._current_tool.on_release(self._image, px, py, self._current_color)
            self._painting = False
            self.canvas_modified.emit()
            self.viewport().update()

    def leaveEvent(self, event):
        self._hover_pixel = None
        self.viewport().update()

    def contextMenuEvent(self, event):
        self.context_menu_requested.emit(event.globalPos())
        event.accept()

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.ControlModifier:
            old_zoom = self._zoom
            delta = 1 if event.angleDelta().y() > 0 else -1
            new_zoom = max(1, min(64, old_zoom + delta))

            if new_zoom != old_zoom:
                # Keep the pixel under the cursor fixed
                mouse_pos = event.position().toPoint()
                px, py = self._screen_to_pixel(mouse_pos)

                self._zoom = new_zoom
                self._update_scrollbars()
                self.zoom_changed.emit(new_zoom)

                # Adjust scroll so (px, py) stays under the mouse
                new_ox = int(px * new_zoom + _MARGIN)
                new_oy = int(py * new_zoom + _MARGIN)
                self.horizontalScrollBar().setValue(new_ox - mouse_pos.x())
                self.verticalScrollBar().setValue(new_oy - mouse_pos.y())

                self.viewport().update()
            event.accept()
        else:
            # Default: let QAbstractScrollArea scroll the viewport
            super().wheelEvent(event)

    def event(self, event):
        # Accept ShortcutOverride so Ctrl+C/X/V reach keyPressEvent
        # instead of being consumed by the main window's Edit menu actions.
        if event.type() == QEvent.ShortcutOverride:
            key = event.key()
            mods = event.modifiers()
            if mods & Qt.ControlModifier and key in (Qt.Key_C, Qt.Key_X, Qt.Key_V):
                event.accept()
                return True
            if key == Qt.Key_Delete:
                event.accept()
                return True
        return super().event(event)

    def keyPressEvent(self, event: QKeyEvent):
        mods = event.modifiers()
        key = event.key()
        if mods & Qt.ControlModifier:
            if key == Qt.Key_C:
                self.copy_requested.emit()
                event.accept()
                return
            elif key == Qt.Key_X:
                self.cut_requested.emit()
                event.accept()
                return
            elif key == Qt.Key_V:
                self.paste_requested.emit()
                event.accept()
                return
        if key == Qt.Key_Delete:
            self.delete_requested.emit()
            event.accept()
            return
        # Forward unhandled keys (tool shortcuts, Escape, etc.)
        self.key_pressed.emit(key)
        event.accept()
