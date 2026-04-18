#!/usr/bin/env python3
"""
Playground Canvas for the Playground Editor.
QPainter-based canvas for placing walls and robots in an Aseba playground.
"""

import math
from enum import Enum, auto

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPolygonF,
    QUndoStack, QTransform,
)

from editors.playground_editor.playground_elements import PlaygroundWall, PlaygroundRobot
from editors.playground_editor.playground_undo_commands import (
    AddElementCommand, RemoveElementCommand, MoveElementCommand,
)

from core.logger import get_logger
logger = get_logger(__name__)


class PlaygroundEditMode(Enum):
    SELECT = auto()
    WALL = auto()
    ROBOT = auto()
    BLOCK = auto()


# Default colors for new playgrounds
DEFAULT_COLORS = [
    {"name": "white", "r": 1.0, "g": 1.0, "b": 1.0},
    {"name": "wall", "r": 0.45, "g": 0.45, "b": 0.50},
    {"name": "red", "r": 0.77, "g": 0.2, "b": 0.15},
    {"name": "green", "r": 0.0, "g": 0.5, "b": 0.17},
    {"name": "blue", "r": 0.0, "g": 0.38, "b": 0.61},
]

# Hit-test margin in pixels
HIT_MARGIN = 6
# Robot icon radius
ROBOT_RADIUS = 8
THYMIO_SIZE = 12


class PlaygroundCanvas(QWidget):
    """Canvas for visually editing an Aseba playground"""

    element_selected = Signal(object)   # PlaygroundWall, PlaygroundRobot, or None
    element_moved = Signal(object)
    element_added = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # Arena properties
        self.arena_width = 400
        self.arena_height = 400
        self.arena_color_name = "white"
        self.ground_texture = None  # QPixmap or None

        # Named colors
        self.colors = list(DEFAULT_COLORS)

        # Elements
        self.walls = []
        self.robots = []

        # Selection and interaction
        self.selected_elements = []
        self.edit_mode = PlaygroundEditMode.SELECT

        # Grid
        self.grid_enabled = True
        self.snap_to_grid = True
        self.grid_size = 10

        # Drag state
        self._dragging = False
        self._drag_start = None
        self._drag_element = None
        self._drag_offset_x = 0
        self._drag_offset_y = 0

        # Wall drawing state (drag-to-draw)
        self._drawing_wall = False
        self._wall_draw_start = None   # (x, y) in arena coords
        self._wall_draw_end = None     # (x, y) in arena coords
        self.default_wall_thickness = 5.0
        self.default_wall_height = 10.0

        # Block painting state
        self.block_paint_color = "wall"
        self.block_size = 20.0  # cube size (l1=l2=h=block_size)
        self._painting_blocks = False
        self._erasing_blocks = False
        self._painted_cells = set()  # grid cells painted in current stroke
        self._batch_paint_walls = []  # walls added in current stroke

        # Preview
        self._preview_pos = None

        # Undo
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)

        # Next robot port (auto-increment)
        self._next_port = 33333

        self._update_size()

    def _update_size(self):
        """Update widget size to match arena"""
        margin = 20
        self.setMinimumSize(self.arena_width + margin * 2,
                            self.arena_height + margin * 2)
        self.setFixedSize(self.arena_width + margin * 2,
                          self.arena_height + margin * 2)
        self._margin = margin

    # ─── Arena properties ───────────────────────────────────────

    def set_arena_properties(self, width, height, color_name):
        """Set arena dimensions and background color"""
        self.arena_width = width
        self.arena_height = height
        self.arena_color_name = color_name
        self._update_size()
        self.update()

    def set_colors(self, colors):
        """Set the named color palette"""
        self.colors = list(colors) if colors else list(DEFAULT_COLORS)
        self.update()

    def resolve_color(self, name):
        """Resolve a named color to a QColor"""
        for c in self.colors:
            if c['name'] == name:
                return QColor(int(c['r'] * 255), int(c['g'] * 255), int(c['b'] * 255))
        return QColor(180, 180, 180)  # fallback gray

    # ─── Element management ─────────────────────────────────────

    def add_wall(self, wall_data=None, use_undo=True):
        """Add a wall element"""
        if wall_data:
            wall = PlaygroundWall.from_dict(wall_data)
        else:
            wall = PlaygroundWall()
        if use_undo:
            cmd = AddElementCommand(self, wall, "Add Wall")
            self.walls.append(wall)
            cmd.already_added = True
            self.undo_stack.push(cmd)
        else:
            self.walls.append(wall)
        self.element_added.emit(wall)
        self.update()
        return wall

    def add_robot(self, robot_data=None, use_undo=True):
        """Add a robot element"""
        if robot_data:
            robot = PlaygroundRobot.from_dict(robot_data)
        else:
            robot = PlaygroundRobot(port=self._next_port)
            self._next_port += 1
        if use_undo:
            cmd = AddElementCommand(self, robot, "Add Robot")
            self.robots.append(robot)
            cmd.already_added = True
            self.undo_stack.push(cmd)
        else:
            self.robots.append(robot)
        self.element_added.emit(robot)
        self.update()
        return robot

    def remove_element(self, element):
        """Remove a wall or robot with undo support"""
        cmd = RemoveElementCommand(self, element, "Delete Element")
        self.undo_stack.push(cmd)
        self.update()

    def load_data(self, walls_data, robots_data):
        """Load walls and robots from data (no undo)"""
        self.walls.clear()
        self.robots.clear()
        self.selected_elements.clear()
        for wd in (walls_data or []):
            self.walls.append(PlaygroundWall.from_dict(wd))
        for rd in (robots_data or []):
            robot = PlaygroundRobot.from_dict(rd)
            self.robots.append(robot)
        # Track next port
        if self.robots:
            self._next_port = max(r.port for r in self.robots) + 1
        self.undo_stack.clear()
        self.update()

    def get_walls_data(self):
        return [w.to_dict() for w in self.walls]

    def get_robots_data(self):
        return [r.to_dict() for r in self.robots]

    # ─── Snapping ───────────────────────────────────────────────

    def snap(self, x, y):
        """Snap position to grid if enabled"""
        if self.snap_to_grid and self.grid_size > 0:
            x = round(x / self.grid_size) * self.grid_size
            y = round(y / self.grid_size) * self.grid_size
        return x, y

    # ─── Hit testing ────────────────────────────────────────────

    def _canvas_to_arena(self, pos):
        """Convert canvas widget coords to arena coords"""
        return pos.x() - self._margin, pos.y() - self._margin

    def find_element_at(self, ax, ay):
        """Find element at arena coords (robots checked first, then walls)"""
        # Check robots first (smaller targets, on top)
        for robot in reversed(self.robots):
            dx = ax - robot.x
            dy = ay - robot.y
            if dx * dx + dy * dy <= (THYMIO_SIZE + HIT_MARGIN) ** 2:
                return robot
        # Check walls
        for wall in reversed(self.walls):
            if self._point_in_wall(ax, ay, wall):
                return wall
        return None

    def _point_in_wall(self, px, py, wall):
        """Check if point (px, py) is inside a rotated wall rectangle"""
        # Transform point into wall-local coordinates
        dx = px - wall.x
        dy = py - wall.y
        cos_a = math.cos(-wall.angle)
        sin_a = math.sin(-wall.angle)
        lx = dx * cos_a - dy * sin_a
        ly = dx * sin_a + dy * cos_a
        half_l1 = wall.l1 / 2 + HIT_MARGIN
        half_l2 = wall.l2 / 2 + HIT_MARGIN
        return abs(lx) <= half_l1 and abs(ly) <= half_l2

    # ─── Drawing ────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background (outside arena)
        painter.fillRect(self.rect(), QColor(60, 60, 60))

        # Translate to arena origin
        painter.translate(self._margin, self._margin)

        # Arena background
        arena_color = self.resolve_color(self.arena_color_name)
        painter.fillRect(0, 0, self.arena_width, self.arena_height, arena_color)

        # Ground texture
        if self.ground_texture:
            painter.drawPixmap(0, 0, self.arena_width, self.arena_height,
                               self.ground_texture)

        # Grid
        if self.grid_enabled:
            self._draw_grid(painter)

        # Walls
        for wall in self.walls:
            self._draw_wall(painter, wall, wall in self.selected_elements)

        # Robots
        for robot in self.robots:
            self._draw_robot(painter, robot, robot in self.selected_elements)

        # Placement preview (cursor hint)
        if self._preview_pos and self.edit_mode != PlaygroundEditMode.SELECT and not self._drawing_wall:
            self._draw_preview(painter)

        # Wall drag-draw preview
        if self._drawing_wall:
            self._draw_wall_draft(painter)

        # Arena border
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, self.arena_width, self.arena_height)

        painter.end()

    def _draw_grid(self, painter):
        """Draw the grid overlay"""
        pen = QPen(QColor(200, 200, 200, 80), 1)
        painter.setPen(pen)
        gs = self.grid_size
        for x in range(0, self.arena_width + 1, gs):
            painter.drawLine(x, 0, x, self.arena_height)
        for y in range(0, self.arena_height + 1, gs):
            painter.drawLine(0, y, self.arena_width, y)

    def _draw_wall(self, painter, wall, selected=False):
        """Draw a wall as a rotated filled rectangle"""
        painter.save()
        painter.translate(wall.x, wall.y)
        painter.rotate(math.degrees(wall.angle))

        color = self.resolve_color(wall.color)
        if wall.mass is not None:
            # Movable walls get a slightly different shade
            color = color.lighter(120)

        painter.setBrush(QBrush(color))
        outline = QColor(0, 0, 0) if not selected else QColor(255, 80, 80)
        painter.setPen(QPen(outline, 2 if selected else 1))
        painter.drawRect(QRectF(-wall.l1 / 2, -wall.l2 / 2, wall.l1, wall.l2))

        # Mass indicator
        if wall.mass is not None:
            painter.setPen(QPen(QColor(0, 0, 200), 1))
            font = QFont()
            font.setPixelSize(max(8, int(min(wall.l1, wall.l2) * 0.6)))
            painter.setFont(font)
            painter.drawText(QRectF(-wall.l1 / 2, -wall.l2 / 2, wall.l1, wall.l2),
                             Qt.AlignCenter, "M")

        painter.restore()

    def _draw_robot(self, painter, robot, selected=False):
        """Draw a robot icon at its position"""
        painter.save()
        painter.translate(robot.x, robot.y)
        painter.rotate(math.degrees(robot.angle))

        outline = QColor(255, 80, 80) if selected else QColor(40, 40, 40)
        painter.setPen(QPen(outline, 2 if selected else 1))

        if robot.robot_type == 'thymio2':
            # Simplified top-down Thymio shape (rounded trapezoid)
            s = THYMIO_SIZE
            body = QPolygonF([
                QPointF(-s, -s * 0.8),
                QPointF(s, -s * 0.8),
                QPointF(s * 0.7, s),
                QPointF(-s * 0.7, s),
            ])
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawPolygon(body)
            # Direction indicator
            painter.setBrush(QBrush(QColor(0, 200, 0)))
            painter.drawEllipse(QPointF(0, -s * 0.5), 3, 3)
        else:
            # E-puck: simple circle
            painter.setBrush(QBrush(QColor(200, 220, 255)))
            painter.drawEllipse(QPointF(0, 0), ROBOT_RADIUS, ROBOT_RADIUS)
            # Direction line
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawLine(QPointF(0, 0), QPointF(0, -ROBOT_RADIUS))

        painter.restore()

        # Draw name label
        painter.setPen(QPen(QColor(0, 0, 0)))
        font = QFont()
        font.setPixelSize(9)
        painter.setFont(font)
        painter.drawText(int(robot.x - 30), int(robot.y + THYMIO_SIZE + 12),
                         60, 14, Qt.AlignCenter, robot.name)

    def _draw_preview(self, painter):
        """Draw a semi-transparent preview of what will be placed"""
        ax, ay = self._preview_pos
        painter.setOpacity(0.4)
        if self.edit_mode == PlaygroundEditMode.WALL:
            # Cursor hint: small crosshair + thickness indicator
            pen = QPen(QColor(0, 200, 0), 1, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawLine(int(ax) - 8, int(ay), int(ax) + 8, int(ay))
            painter.drawLine(int(ax), int(ay) - 8, int(ax), int(ay) + 8)
        elif self.edit_mode == PlaygroundEditMode.ROBOT:
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(0, 200, 0), 1, Qt.DashLine))
            painter.drawEllipse(QPointF(ax, ay), THYMIO_SIZE, THYMIO_SIZE)
        elif self.edit_mode == PlaygroundEditMode.BLOCK:
            # Highlight the grid cell under the cursor
            col, row = self._block_cell(ax, ay)
            cx, cy = self._cell_center(col, row)
            size = self.block_size
            painter.setBrush(QBrush(self.resolve_color(self.block_paint_color)))
            painter.setPen(QPen(QColor(0, 200, 0), 1, Qt.DashLine))
            painter.drawRect(QRectF(cx - size / 2, cy - size / 2, size, size))
        painter.setOpacity(1.0)

    def _draw_wall_draft(self, painter):
        """Draw a preview of the wall being drag-drawn"""
        if not (self._wall_draw_start and self._wall_draw_end):
            return
        sx, sy = self._wall_draw_start
        ex, ey = self._wall_draw_end
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy)
        if length < 1:
            return
        angle = math.atan2(dy, dx)
        cx, cy = (sx + ex) / 2, (sy + ey) / 2

        painter.save()
        painter.setOpacity(0.5)
        painter.translate(cx, cy)
        painter.rotate(math.degrees(angle))
        painter.setBrush(QBrush(self.resolve_color("wall")))
        painter.setPen(QPen(QColor(0, 200, 0), 1, Qt.DashLine))
        painter.drawRect(QRectF(-length / 2, -self.default_wall_thickness / 2,
                                length, self.default_wall_thickness))
        painter.restore()
        painter.setOpacity(1.0)

        # Length label
        painter.setPen(QPen(QColor(0, 100, 0)))
        font = QFont()
        font.setPixelSize(10)
        painter.setFont(font)
        painter.drawText(int(cx) + 10, int(cy) - 10, f"{length:.0f}")

    # ─── Mouse events ───────────────────────────────────────────

    def mousePressEvent(self, event):
        ax, ay = self._canvas_to_arena(event.position())

        if event.button() == Qt.LeftButton:
            if self.edit_mode == PlaygroundEditMode.SELECT:
                element = self.find_element_at(ax, ay)
                if element:
                    if event.modifiers() & Qt.ShiftModifier:
                        if element in self.selected_elements:
                            self.selected_elements.remove(element)
                        else:
                            self.selected_elements.append(element)
                    else:
                        if element not in self.selected_elements:
                            self.selected_elements = [element]
                    self._dragging = True
                    self._drag_element = element
                    self._drag_start = (ax, ay)
                    self._drag_offset_x = ax - element.x
                    self._drag_offset_y = ay - element.y
                    self.element_selected.emit(element)
                else:
                    self.selected_elements.clear()
                    self.element_selected.emit(None)

            elif self.edit_mode == PlaygroundEditMode.WALL:
                # Start drag-to-draw
                sx, sy = self.snap(ax, ay)
                self._drawing_wall = True
                self._wall_draw_start = (sx, sy)
                self._wall_draw_end = (sx, sy)

            elif self.edit_mode == PlaygroundEditMode.ROBOT:
                sx, sy = self.snap(ax, ay)
                robot = PlaygroundRobot(x=sx, y=sy, port=self._next_port,
                                        name=f"Thymio{len(self.robots)}")
                self.add_robot(robot.to_dict())
                self.selected_elements = [self.robots[-1]]
                self.element_selected.emit(self.robots[-1])

            elif self.edit_mode == PlaygroundEditMode.BLOCK:
                self._painting_blocks = True
                self._painted_cells = set()
                self._batch_paint_walls = []
                self._paint_block_at(ax, ay)

        elif event.button() == Qt.RightButton:
            if self.edit_mode == PlaygroundEditMode.BLOCK:
                # Erase blocks on right-click-drag
                self._erasing_blocks = True
                self._painted_cells = set()
                self._erase_block_at(ax, ay)
            else:
                # Right-click: delete element at position
                element = self.find_element_at(ax, ay)
                if element:
                    self.remove_element(element)

        self.update()

    def mouseMoveEvent(self, event):
        ax, ay = self._canvas_to_arena(event.position())

        if self._dragging and self._drag_element:
            sx, sy = self.snap(ax - self._drag_offset_x, ay - self._drag_offset_y)
            self._drag_element.x = sx
            self._drag_element.y = sy
            self.update()
        elif self._drawing_wall:
            sx, sy = self.snap(ax, ay)
            # Constrain to horizontal/vertical when Shift is held
            if event.modifiers() & Qt.ShiftModifier and self._wall_draw_start:
                start_x, start_y = self._wall_draw_start
                if abs(sx - start_x) > abs(sy - start_y):
                    sy = start_y
                else:
                    sx = start_x
            self._wall_draw_end = (sx, sy)
            self.update()
        elif self._painting_blocks:
            self._paint_block_at(ax, ay)
            self.update()
        elif self._erasing_blocks:
            self._erase_block_at(ax, ay)
            self.update()
        elif self.edit_mode != PlaygroundEditMode.SELECT:
            sx, sy = self.snap(ax, ay)
            self._preview_pos = (sx, sy)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._dragging:
            if self._drag_element and self._drag_start:
                old_x, old_y = self._drag_start
                old_x -= self._drag_offset_x
                old_y -= self._drag_offset_y
                old_x, old_y = self.snap(old_x, old_y)
                new_x = self._drag_element.x
                new_y = self._drag_element.y
                if old_x != new_x or old_y != new_y:
                    # Push move command (element already moved, so set back then push)
                    self._drag_element.x = old_x
                    self._drag_element.y = old_y
                    cmd = MoveElementCommand(
                        self, self._drag_element,
                        old_x, old_y, new_x, new_y, "Move Element")
                    self.undo_stack.push(cmd)
                    self.element_moved.emit(self._drag_element)
            self._dragging = False
            self._drag_element = None
            self._drag_start = None
            self.update()
        elif event.button() == Qt.LeftButton and self._drawing_wall:
            self._finalize_wall_draft()
            self.update()
        elif event.button() == Qt.LeftButton and self._painting_blocks:
            self._painting_blocks = False
            self._finalize_block_paint()
            self.update()
        elif event.button() == Qt.RightButton and self._erasing_blocks:
            self._erasing_blocks = False
            self._painted_cells = set()
            self.update()

    def _finalize_wall_draft(self):
        """Create a wall from the drag-draw start/end points"""
        MIN_WALL_LENGTH = 4.0  # minimum length to create a wall
        start = self._wall_draw_start
        end = self._wall_draw_end
        self._drawing_wall = False
        self._wall_draw_start = None
        self._wall_draw_end = None

        if not (start and end):
            return
        sx, sy = start
        ex, ey = end
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy)

        if length < MIN_WALL_LENGTH:
            # Too small - treat as click: place default wall at cursor
            wall = PlaygroundWall(x=sx, y=sy, l1=50,
                                  l2=self.default_wall_thickness,
                                  h=self.default_wall_height)
        else:
            cx, cy = (sx + ex) / 2, (sy + ey) / 2
            angle = math.atan2(dy, dx)
            wall = PlaygroundWall(x=cx, y=cy, l1=length,
                                  l2=self.default_wall_thickness,
                                  h=self.default_wall_height,
                                  angle=angle)

        self.add_wall(wall.to_dict())
        self.selected_elements = [self.walls[-1]]
        self.element_selected.emit(self.walls[-1])

    # ─── Block painting ─────────────────────────────────────────

    def _block_cell(self, ax, ay):
        """Convert arena coords to block grid cell (col, row)"""
        size = self.block_size
        return (int(ax // size), int(ay // size))

    def _cell_center(self, col, row):
        """Arena coords at the center of a block cell"""
        size = self.block_size
        return (col * size + size / 2, row * size + size / 2)

    def _find_block_at_cell(self, col, row):
        """Find a block-shaped wall whose center matches this cell"""
        cx, cy = self._cell_center(col, row)
        for w in self.walls:
            if (abs(w.x - cx) < 0.5 and abs(w.y - cy) < 0.5
                    and abs(w.l1 - self.block_size) < 0.5
                    and abs(w.l2 - self.block_size) < 0.5):
                return w
        return None

    def _paint_block_at(self, ax, ay):
        """Place a block at the grid cell containing (ax, ay), if not already there"""
        cell = self._block_cell(ax, ay)
        if cell in self._painted_cells:
            return
        self._painted_cells.add(cell)
        if self._find_block_at_cell(*cell) is not None:
            return  # already a block here
        cx, cy = self._cell_center(*cell)
        block = PlaygroundWall(
            x=cx, y=cy,
            l1=self.block_size, l2=self.block_size,
            h=self.block_size,
            color=self.block_paint_color,
            angle=0.0,
        )
        self.walls.append(block)
        self._batch_paint_walls.append(block)
        self.element_added.emit(block)

    def _erase_block_at(self, ax, ay):
        """Remove the block at the grid cell containing (ax, ay)"""
        cell = self._block_cell(ax, ay)
        if cell in self._painted_cells:
            return
        self._painted_cells.add(cell)
        block = self._find_block_at_cell(*cell)
        if block is not None:
            # Use remove command for undo support
            self.remove_element(block)

    def _finalize_block_paint(self):
        """Push a single undo command for the whole paint stroke"""
        if self._batch_paint_walls:
            # Build a batch add command
            from editors.playground_editor.playground_undo_commands import AddElementCommand
            from PySide6.QtGui import QUndoCommand

            walls = list(self._batch_paint_walls)
            canvas = self

            class BatchPaintBlocksCommand(QUndoCommand):
                def __init__(self):
                    super().__init__(f"Paint {len(walls)} Blocks")

                def undo(self):
                    for w in walls:
                        if w in canvas.walls:
                            canvas.walls.remove(w)
                    canvas.update()

                def redo(self):
                    for w in walls:
                        if w not in canvas.walls:
                            canvas.walls.append(w)
                    canvas.update()

            # The walls are already added - push a command that can undo/redo them
            cmd = BatchPaintBlocksCommand()
            self.undo_stack.push(cmd)
            # redo() runs on push which would re-add walls that are already there - OK
        self._batch_paint_walls = []
        self._painted_cells = set()

    def leaveEvent(self, event):
        self._preview_pos = None
        self.update()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            for elem in list(self.selected_elements):
                self.remove_element(elem)
            self.selected_elements.clear()
            self.element_selected.emit(None)
            self.update()
        else:
            super().keyPressEvent(event)
