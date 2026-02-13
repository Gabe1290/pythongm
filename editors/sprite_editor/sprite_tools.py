#!/usr/bin/env python3
"""
Sprite Drawing Tools for the Sprite Editor
Each tool handles mouse press/move/release on a QImage canvas.
"""

from collections import deque
from PySide6.QtGui import QImage, QColor
from PySide6.QtCore import QPoint, QRect


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def bresenham_line(x0, y0, x1, y1):
    """Yield (x, y) pixel coordinates along a line using Bresenham's algorithm."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        yield (x0, y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def mirror_horizontal(image: QImage) -> QImage:
    """Return a horizontally mirrored copy of the image."""
    return image.mirrored(True, False)


def mirror_vertical(image: QImage) -> QImage:
    """Return a vertically mirrored copy of the image."""
    return image.mirrored(False, True)


def _in_bounds(image: QImage, x: int, y: int) -> bool:
    return 0 <= x < image.width() and 0 <= y < image.height()


def _set_pixel(image: QImage, x: int, y: int, color: QColor):
    if _in_bounds(image, x, y):
        image.setPixelColor(x, y, color)


# ---------------------------------------------------------------------------
# Base Tool
# ---------------------------------------------------------------------------

class BaseTool:
    """Base class for all sprite editing tools."""

    name = "base"

    def __init__(self):
        self.color = QColor(0, 0, 0, 255)
        self.size = 1  # brush size in pixels

    def on_press(self, image: QImage, x: int, y: int, color: QColor):
        """Called when the mouse button is pressed."""

    def on_move(self, image: QImage, x: int, y: int, color: QColor):
        """Called while the mouse is being dragged."""

    def on_release(self, image: QImage, x: int, y: int, color: QColor):
        """Called when the mouse button is released."""

    def get_preview(self) -> QImage | None:
        """Return an overlay image for tool preview (e.g. shape being drawn)."""
        return None

    def reset(self):
        """Reset tool state between strokes."""


# ---------------------------------------------------------------------------
# Pencil Tool
# ---------------------------------------------------------------------------

class PencilTool(BaseTool):
    name = "pencil"

    def __init__(self):
        super().__init__()
        self._last_x = -1
        self._last_y = -1

    def on_press(self, image, x, y, color):
        self._last_x = x
        self._last_y = y
        self._draw_brush(image, x, y, color)

    def on_move(self, image, x, y, color):
        if self._last_x >= 0:
            for px, py in bresenham_line(self._last_x, self._last_y, x, y):
                self._draw_brush(image, px, py, color)
        self._last_x = x
        self._last_y = y

    def on_release(self, image, x, y, color):
        self._last_x = -1
        self._last_y = -1

    def reset(self):
        self._last_x = -1
        self._last_y = -1

    def _draw_brush(self, image, cx, cy, color):
        half = self.size // 2
        for dy in range(self.size):
            for dx in range(self.size):
                _set_pixel(image, cx - half + dx, cy - half + dy, color)


# ---------------------------------------------------------------------------
# Eraser Tool
# ---------------------------------------------------------------------------

class EraserTool(BaseTool):
    name = "eraser"

    def __init__(self):
        super().__init__()
        self._last_x = -1
        self._last_y = -1
        self._transparent = QColor(0, 0, 0, 0)

    def on_press(self, image, x, y, color):
        self._last_x = x
        self._last_y = y
        self._erase(image, x, y)

    def on_move(self, image, x, y, color):
        if self._last_x >= 0:
            for px, py in bresenham_line(self._last_x, self._last_y, x, y):
                self._erase(image, px, py)
        self._last_x = x
        self._last_y = y

    def on_release(self, image, x, y, color):
        self._last_x = -1
        self._last_y = -1

    def reset(self):
        self._last_x = -1
        self._last_y = -1

    def _erase(self, image, cx, cy):
        half = self.size // 2
        for dy in range(self.size):
            for dx in range(self.size):
                _set_pixel(image, cx - half + dx, cy - half + dy, self._transparent)


# ---------------------------------------------------------------------------
# Color Picker (Eyedropper) Tool
# ---------------------------------------------------------------------------

class ColorPickerTool(BaseTool):
    name = "color_picker"

    def __init__(self):
        super().__init__()
        self.picked_color = None

    def on_press(self, image, x, y, color):
        if _in_bounds(image, x, y):
            self.picked_color = image.pixelColor(x, y)

    def on_move(self, image, x, y, color):
        if _in_bounds(image, x, y):
            self.picked_color = image.pixelColor(x, y)

    def reset(self):
        self.picked_color = None


# ---------------------------------------------------------------------------
# Flood Fill Tool
# ---------------------------------------------------------------------------

class FillTool(BaseTool):
    name = "fill"

    def on_press(self, image, x, y, color):
        if not _in_bounds(image, x, y):
            return

        target_color = image.pixelColor(x, y)
        if target_color == color:
            return  # nothing to fill

        w, h = image.width(), image.height()
        queue = deque([(x, y)])
        visited = set()
        visited.add((x, y))

        while queue:
            cx, cy = queue.popleft()
            if image.pixelColor(cx, cy) != target_color:
                continue
            image.setPixelColor(cx, cy, color)

            for nx, ny in [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]:
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))


# ---------------------------------------------------------------------------
# Line Tool
# ---------------------------------------------------------------------------

class LineTool(BaseTool):
    name = "line"

    def __init__(self):
        super().__init__()
        self._start = None
        self._end = None
        self._preview = None
        self._image_size = None

    def on_press(self, image, x, y, color):
        self._start = (x, y)
        self._end = (x, y)
        self._image_size = (image.width(), image.height())
        self._update_preview(color)

    def on_move(self, image, x, y, color):
        if self._start:
            self._end = (x, y)
            self._update_preview(color)

    def on_release(self, image, x, y, color):
        if self._start:
            self._end = (x, y)
            for px, py in bresenham_line(*self._start, *self._end):
                _set_pixel(image, px, py, color)
        self._start = None
        self._end = None
        self._preview = None

    def get_preview(self):
        return self._preview

    def reset(self):
        self._start = None
        self._end = None
        self._preview = None

    def _update_preview(self, color):
        if not self._start or not self._image_size:
            return
        w, h = self._image_size
        self._preview = QImage(w, h, QImage.Format_ARGB32)
        self._preview.fill(QColor(0, 0, 0, 0))
        for px, py in bresenham_line(*self._start, *self._end):
            _set_pixel(self._preview, px, py, color)


# ---------------------------------------------------------------------------
# Rectangle Tool
# ---------------------------------------------------------------------------

class RectTool(BaseTool):
    name = "rectangle"

    def __init__(self):
        super().__init__()
        self._start = None
        self._end = None
        self._preview = None
        self._image_size = None
        self.filled = False

    def on_press(self, image, x, y, color):
        self._start = (x, y)
        self._end = (x, y)
        self._image_size = (image.width(), image.height())
        self._update_preview(color)

    def on_move(self, image, x, y, color):
        if self._start:
            self._end = (x, y)
            self._update_preview(color)

    def on_release(self, image, x, y, color):
        if self._start:
            self._end = (x, y)
            self._draw_rect(image, color)
        self._start = None
        self._end = None
        self._preview = None

    def get_preview(self):
        return self._preview

    def reset(self):
        self._start = None
        self._end = None
        self._preview = None

    def _draw_rect(self, image, color):
        x0 = min(self._start[0], self._end[0])
        y0 = min(self._start[1], self._end[1])
        x1 = max(self._start[0], self._end[0])
        y1 = max(self._start[1], self._end[1])

        if self.filled:
            for py in range(y0, y1 + 1):
                for px in range(x0, x1 + 1):
                    _set_pixel(image, px, py, color)
        else:
            for px in range(x0, x1 + 1):
                _set_pixel(image, px, y0, color)
                _set_pixel(image, px, y1, color)
            for py in range(y0, y1 + 1):
                _set_pixel(image, x0, py, color)
                _set_pixel(image, x1, py, color)

    def _update_preview(self, color):
        if not self._start or not self._image_size:
            return
        w, h = self._image_size
        self._preview = QImage(w, h, QImage.Format_ARGB32)
        self._preview.fill(QColor(0, 0, 0, 0))
        self._draw_rect_on(self._preview, color)

    def _draw_rect_on(self, image, color):
        x0 = min(self._start[0], self._end[0])
        y0 = min(self._start[1], self._end[1])
        x1 = max(self._start[0], self._end[0])
        y1 = max(self._start[1], self._end[1])

        if self.filled:
            for py in range(y0, y1 + 1):
                for px in range(x0, x1 + 1):
                    _set_pixel(image, px, py, color)
        else:
            for px in range(x0, x1 + 1):
                _set_pixel(image, px, y0, color)
                _set_pixel(image, px, y1, color)
            for py in range(y0, y1 + 1):
                _set_pixel(image, x0, py, color)
                _set_pixel(image, x1, py, color)


# ---------------------------------------------------------------------------
# Ellipse Tool
# ---------------------------------------------------------------------------

class EllipseTool(BaseTool):
    name = "ellipse"

    def __init__(self):
        super().__init__()
        self._start = None
        self._end = None
        self._preview = None
        self._image_size = None
        self.filled = False

    def on_press(self, image, x, y, color):
        self._start = (x, y)
        self._end = (x, y)
        self._image_size = (image.width(), image.height())
        self._update_preview(color)

    def on_move(self, image, x, y, color):
        if self._start:
            self._end = (x, y)
            self._update_preview(color)

    def on_release(self, image, x, y, color):
        if self._start:
            self._end = (x, y)
            self._draw_ellipse(image, color)
        self._start = None
        self._end = None
        self._preview = None

    def get_preview(self):
        return self._preview

    def reset(self):
        self._start = None
        self._end = None
        self._preview = None

    def _draw_ellipse(self, image, color):
        x0 = min(self._start[0], self._end[0])
        y0 = min(self._start[1], self._end[1])
        x1 = max(self._start[0], self._end[0])
        y1 = max(self._start[1], self._end[1])

        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        rx = (x1 - x0) / 2.0
        ry = (y1 - y0) / 2.0

        if rx < 0.5 or ry < 0.5:
            _set_pixel(image, int(cx), int(cy), color)
            return

        self._midpoint_ellipse(image, cx, cy, rx, ry, color)

    def _midpoint_ellipse(self, image, cx, cy, rx, ry, color):
        """Draw ellipse using midpoint algorithm."""
        if rx < 0.5 and ry < 0.5:
            _set_pixel(image, int(cx), int(cy), color)
            return

        # Collect outline points for potential filling
        scanlines = {}

        def plot_points(px, py):
            points = [
                (int(cx + px), int(cy + py)),
                (int(cx - px), int(cy + py)),
                (int(cx + px), int(cy - py)),
                (int(cx - px), int(cy - py)),
            ]
            for x, y in points:
                _set_pixel(image, x, y, color)
                if self.filled:
                    if y not in scanlines:
                        scanlines[y] = [x, x]
                    else:
                        scanlines[y][0] = min(scanlines[y][0], x)
                        scanlines[y][1] = max(scanlines[y][1], x)

        x = 0
        y = ry

        # Region 1
        d1 = ry * ry - rx * rx * ry + 0.25 * rx * rx
        dx = 2 * ry * ry * x
        dy = 2 * rx * rx * y

        while dx < dy:
            plot_points(x, y)
            if d1 < 0:
                x += 1
                dx += 2 * ry * ry
                d1 += dx + ry * ry
            else:
                x += 1
                y -= 1
                dx += 2 * ry * ry
                dy -= 2 * rx * rx
                d1 += dx - dy + ry * ry

        # Region 2
        d2 = (ry * ry * (x + 0.5) ** 2 + rx * rx * (y - 1) ** 2 - rx * rx * ry * ry)

        while y >= 0:
            plot_points(x, y)
            if d2 > 0:
                y -= 1
                dy -= 2 * rx * rx
                d2 += rx * rx - dy
            else:
                y -= 1
                x += 1
                dx += 2 * ry * ry
                dy -= 2 * rx * rx
                d2 += dx - dy + rx * rx

        # Fill scanlines if filled mode
        if self.filled:
            for sy, (sx_min, sx_max) in scanlines.items():
                for sx in range(sx_min, sx_max + 1):
                    _set_pixel(image, sx, sy, color)

    def _update_preview(self, color):
        if not self._start or not self._image_size:
            return
        w, h = self._image_size
        self._preview = QImage(w, h, QImage.Format_ARGB32)
        self._preview.fill(QColor(0, 0, 0, 0))
        self._draw_ellipse_on_preview(color)

    def _draw_ellipse_on_preview(self, color):
        x0 = min(self._start[0], self._end[0])
        y0 = min(self._start[1], self._end[1])
        x1 = max(self._start[0], self._end[0])
        y1 = max(self._start[1], self._end[1])

        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        rx = (x1 - x0) / 2.0
        ry = (y1 - y0) / 2.0

        if rx < 0.5 or ry < 0.5:
            _set_pixel(self._preview, int(cx), int(cy), color)
            return

        self._midpoint_ellipse(self._preview, cx, cy, rx, ry, color)


# ---------------------------------------------------------------------------
# Selection Tool
# ---------------------------------------------------------------------------

class SelectTool(BaseTool):
    name = "select"

    def __init__(self):
        super().__init__()
        self._start = None
        self._end = None
        self.selection_rect = None  # QRect
        self._floating = None  # QImage of the selected/cut region
        self._float_origin = None  # QPoint where the floating selection sits
        self._drag_offset = None  # offset from click to float_origin
        self._dragging = False

    def on_press(self, image, x, y, color):
        # If clicking inside an existing floating selection, start dragging it
        if self._floating and self.selection_rect and self.selection_rect.contains(x, y):
            self._dragging = True
            self._drag_offset = QPoint(x - self.selection_rect.x(), y - self.selection_rect.y())
            return

        # Commit any existing floating selection
        if self._floating:
            self.commit(image)

        # Start new selection
        self._start = (x, y)
        self._end = (x, y)
        self.selection_rect = None

    def on_move(self, image, x, y, color):
        if self._dragging and self._floating:
            self.selection_rect.moveTo(x - self._drag_offset.x(), y - self._drag_offset.y())
            return

        if self._start and not self._dragging:
            self._end = (x, y)
            x0 = min(self._start[0], self._end[0])
            y0 = min(self._start[1], self._end[1])
            x1 = max(self._start[0], self._end[0])
            y1 = max(self._start[1], self._end[1])
            self.selection_rect = QRect(x0, y0, x1 - x0 + 1, y1 - y0 + 1)

    def on_release(self, image, x, y, color):
        if self._dragging:
            self._dragging = False
            return

        if self._start:
            self._end = (x, y)
            x0 = min(self._start[0], self._end[0])
            y0 = min(self._start[1], self._end[1])
            x1 = max(self._start[0], self._end[0])
            y1 = max(self._start[1], self._end[1])
            w = x1 - x0 + 1
            h = y1 - y0 + 1
            if w > 1 or h > 1:
                self.selection_rect = QRect(x0, y0, w, h)
            else:
                self.selection_rect = None
            self._start = None

    def lift_selection(self, image: QImage):
        """Cut the selected area from the image into a floating layer."""
        if not self.selection_rect:
            return
        r = self.selection_rect
        self._floating = image.copy(r.x(), r.y(), r.width(), r.height())
        self._float_origin = QPoint(r.x(), r.y())

        # Clear the area on the source image
        transparent = QColor(0, 0, 0, 0)
        for py in range(r.y(), r.y() + r.height()):
            for px in range(r.x(), r.x() + r.width()):
                _set_pixel(image, px, py, transparent)

    def commit(self, image: QImage):
        """Stamp the floating selection back onto the image."""
        if self._floating and self.selection_rect:
            from PySide6.QtGui import QPainter
            painter = QPainter(image)
            painter.drawImage(self.selection_rect.topLeft(), self._floating)
            painter.end()
        self._floating = None
        self._float_origin = None
        self.selection_rect = None
        self._dragging = False

    def has_floating(self):
        return self._floating is not None

    def get_floating_preview(self):
        """Return (QImage, QRect) for the floating selection, or None."""
        if self._floating and self.selection_rect:
            return self._floating, self.selection_rect
        return None

    def reset(self):
        self._start = None
        self._end = None
        self.selection_rect = None
        self._floating = None
        self._float_origin = None
        self._drag_offset = None
        self._dragging = False
