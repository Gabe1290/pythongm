#!/usr/bin/env python3
"""
Sprite Editor — main editor widget.
Inherits BaseEditor and integrates canvas, tools, color palette, and frame timeline.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter, QWidget, QToolBar,
    QLabel, QSpinBox, QSizePolicy, QMessageBox, QToolButton, QMenu, QFrame,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import (
    QImage, QColor, QUndoCommand, QAction, QActionGroup, QIcon,
    QPainter, QPixmap, QPen, QBrush,
)

from editors.base_editor import BaseEditor, EditorUndoCommand
from core.logger import get_logger

from .sprite_canvas import SpriteCanvas
from .sprite_tools import (
    PencilTool, EraserTool, ColorPickerTool, FillTool,
    LineTool, RectTool, EllipseTool, SelectTool,
    mirror_horizontal, mirror_vertical,
)
from .sprite_frames import FrameTimeline
from .color_palette import ColorPaletteWidget

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Undo commands
# ---------------------------------------------------------------------------

class SpriteEditCommand(QUndoCommand):
    """Undo command that stores before/after QImage snapshots."""

    def __init__(self, editor, old_image: QImage, new_image: QImage, description: str):
        super().__init__(description)
        self._editor = editor
        self._old = old_image.copy()
        self._new = new_image.copy()
        self._frame_index = editor.frame_timeline.get_current_index()

    def undo(self):
        self._editor._set_frame_image(self._frame_index, self._old)

    def redo(self):
        self._editor._set_frame_image(self._frame_index, self._new)


class FrameEditCommand(QUndoCommand):
    """Undo command for frame add/remove/duplicate operations."""

    def __init__(self, editor, old_frames: list, new_frames: list,
                 old_index: int, new_index: int, description: str):
        super().__init__(description)
        self._editor = editor
        self._old_frames = [f.copy() for f in old_frames]
        self._new_frames = [f.copy() for f in new_frames]
        self._old_index = old_index
        self._new_index = new_index

    def undo(self):
        self._editor.frame_timeline.set_frames(self._old_frames)
        self._editor.frame_timeline.set_current_index(self._old_index)
        self._editor.canvas.set_image(self._editor.frame_timeline.get_current_frame())

    def redo(self):
        self._editor.frame_timeline.set_frames(self._new_frames)
        self._editor.frame_timeline.set_current_index(self._new_index)
        self._editor.canvas.set_image(self._editor.frame_timeline.get_current_frame())


# ---------------------------------------------------------------------------
# Sprite Editor
# ---------------------------------------------------------------------------

class SpriteEditor(BaseEditor):
    """Rudimentary sprite/pixel-art editor."""

    sprite_editor_activated = Signal(str, dict)

    def __init__(self, project_path: str = None, parent=None):
        # Instance attributes used before super().__init__ calls setup_base_ui
        self._tools = {}
        self._active_tool_name = "pencil"

        super().__init__(project_path, parent)

        # Build sprite-specific UI inside content_widget
        self._setup_sprite_ui()

        # Instantiate tools
        self._init_tools()

        # Set default tool
        self._select_tool("pencil")

        # Connect canvas key signals (avoids QShortcut conflicts with IDE Edit menu)
        self.canvas.copy_requested.connect(self._shortcut_copy)
        self.canvas.cut_requested.connect(self._shortcut_cut)
        self.canvas.paste_requested.connect(self._shortcut_paste)
        self.canvas.delete_requested.connect(self._shortcut_delete)
        self.canvas.key_pressed.connect(self._on_canvas_key)
        self.canvas.context_menu_requested.connect(self._show_canvas_context_menu)

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------

    def _setup_sprite_ui(self):
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Vertical splitter: canvas area on top, frame timeline on bottom
        vsplitter = QSplitter(Qt.Vertical)

        # Top part: left panel (tools + colors) + centered square canvas
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)

        # Left panel — tool box + color palette
        left_panel = QWidget()
        left_panel.setMaximumWidth(120)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        # Tool box frame
        self._tool_frame = QFrame()
        self._tool_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self._tool_grid = QGridLayout(self._tool_frame)
        self._tool_grid.setContentsMargins(2, 2, 2, 2)
        self._tool_grid.setSpacing(2)
        left_layout.addWidget(self._tool_frame)

        # Add tool buttons to grid and remaining actions to toolbar
        self._add_tool_actions()

        # Color palette
        self.color_palette = ColorPaletteWidget()
        self.color_palette.color_selected.connect(self._on_color_selected)
        left_layout.addWidget(self.color_palette)
        left_layout.addStretch()

        top_layout.addWidget(left_panel)

        # Center — square canvas (enforces width=height internally)
        self.canvas = SpriteCanvas()
        self.canvas.canvas_modified.connect(self._on_canvas_modified)
        self.canvas.color_picked.connect(self._on_color_picked)
        self.canvas.zoom_changed.connect(self._on_zoom_changed)
        top_layout.addWidget(self.canvas, 1)

        vsplitter.addWidget(top_widget)

        # Bottom — frame timeline
        self.frame_timeline = FrameTimeline()
        self.frame_timeline.frame_selected.connect(self._on_frame_selected)
        self.frame_timeline.frames_changed.connect(self._on_frames_changed)
        vsplitter.addWidget(self.frame_timeline)

        # Give most space to the canvas area, minimal to the timeline
        vsplitter.setSizes([500, 120])
        vsplitter.setStretchFactor(0, 1)  # canvas area stretches
        vsplitter.setStretchFactor(1, 0)  # timeline stays compact

        layout.addWidget(vsplitter, 1)

    def _add_tool_actions(self):
        """Add sprite-specific tool buttons with icons to the base toolbar."""
        # Tool action group (mutually exclusive)
        self.tool_group = QActionGroup(self)
        self.tool_group.setExclusive(True)

        tool_defs = [
            ("pencil", self.tr("Pencil"), self.tr("Draw pixels (P)")),
            ("eraser", self.tr("Eraser"), self.tr("Erase pixels (E)")),
            ("color_picker", self.tr("Picker"), self.tr("Pick color from canvas (I)")),
            ("fill", self.tr("Fill"), self.tr("Flood fill area (G)")),
            ("line", self.tr("Line"), self.tr("Draw line (L)")),
            ("rectangle", self.tr("Rect"), self.tr("Draw rectangle (R)")),
            ("ellipse", self.tr("Ellipse"), self.tr("Draw ellipse (O)")),
            ("select", self.tr("Select"), self.tr("Rectangle selection (S)")),
        ]

        self._tool_buttons = {}

        for i, (tool_id, label, tooltip) in enumerate(tool_defs):
            icon = self._make_tool_icon(tool_id)
            action = QAction(icon, label, self)
            action.setToolTip(tooltip)
            action.setCheckable(True)
            action.setData(tool_id)
            action.triggered.connect(lambda checked, tid=tool_id: self._select_tool(tid))
            self.tool_group.addAction(action)

            btn = QToolButton()
            btn.setDefaultAction(action)
            btn.setFixedSize(28, 28)
            btn.setIconSize(btn.size() * 0.7)
            row, col = divmod(i, 4)
            self._tool_grid.addWidget(btn, row, col)
            self._tool_buttons[tool_id] = btn

            if tool_id == "pencil":
                action.setChecked(True)

        # Dropdown list alternative
        self._tool_combo = QComboBox()
        self._tool_combo.setToolTip(self.tr("Select tool from list"))
        for tool_id, label, tooltip in tool_defs:
            self._tool_combo.addItem(self._make_tool_icon(tool_id), label, tool_id)
        self._tool_combo.currentIndexChanged.connect(self._on_tool_combo_changed)
        self._tool_grid.addWidget(self._tool_combo, 2, 0, 1, 4)

        # Brush size — below dropdown in tool panel
        size_layout = QHBoxLayout()
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_label = QLabel(self.tr("Size:"))
        size_layout.addWidget(size_label)
        self._size_spin = QSpinBox()
        self._size_spin.setRange(1, 16)
        self._size_spin.setValue(1)
        self._size_spin.setToolTip(self.tr("Brush / line width in pixels"))
        self._size_spin.valueChanged.connect(self._on_brush_size_changed)
        size_layout.addWidget(self._size_spin)
        self._tool_grid.addLayout(size_layout, 3, 0, 1, 4)

        # Filled mode toggle (for rect/ellipse) — icon
        self._filled_action = self.toolbar.addAction(
            self._make_toolbar_icon("filled"), self.tr("Filled"), self._toggle_filled)
        self._filled_action.setCheckable(True)
        self._filled_action.setToolTip(self.tr("Toggle filled shapes"))

        self.toolbar.addSeparator()

        # Mirror / Flip
        self.toolbar.addAction(self.tr("Mirror H"), self._mirror_h)
        self.toolbar.addAction(self.tr("Mirror V"), self._mirror_v)

        self.toolbar.addSeparator()

        # Grid toggle
        self._grid_action = self.toolbar.addAction(self.tr("Grid"), self._toggle_grid)
        self._grid_action.setCheckable(True)
        self._grid_action.setChecked(True)
        self._grid_action.setToolTip(self.tr("Toggle pixel grid"))

        # Zoom controls — magnifying glass icons
        self.toolbar.addSeparator()
        self.toolbar.addAction(
            self._make_toolbar_icon("zoom_out"), self.tr("Zoom Out"), self._zoom_out)
        self._zoom_label = QLabel(" 10x ")
        self.toolbar.addWidget(self._zoom_label)
        self.toolbar.addAction(
            self._make_toolbar_icon("zoom_in"), self.tr("Zoom In"), self._zoom_in)

    def _on_tool_combo_changed(self, index: int):
        """Handle tool selection from the dropdown combo box."""
        tool_id = self._tool_combo.itemData(index)
        if tool_id:
            self._select_tool(tool_id)

    @staticmethod
    def _make_tool_icon(tool_id: str, size: int = 20) -> QIcon:
        """Generate a small pixel-art style icon for a drawing tool."""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing, True)

        fg = QColor(60, 60, 60)
        accent = QColor(80, 140, 220)
        pen = QPen(fg, 1.5)
        p.setPen(pen)

        if tool_id == "pencil":
            # Dot
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(fg))
            p.drawEllipse(6, 6, 8, 8)

        elif tool_id == "eraser":
            # Eraser block
            p.setBrush(QBrush(QColor(240, 180, 180)))
            p.drawRoundedRect(4, 6, 12, 10, 2, 2)
            p.setPen(QPen(fg, 1))
            p.drawLine(9, 6, 9, 16)

        elif tool_id == "color_picker":
            # Eyedropper
            p.setPen(QPen(fg, 2))
            p.drawLine(5, 15, 12, 8)
            p.setBrush(QBrush(fg))
            p.drawEllipse(11, 3, 6, 6)

        elif tool_id == "fill":
            # Paint bucket — tilted bucket shape
            p.setBrush(QBrush(accent))
            p.drawRect(5, 5, 10, 8)
            p.setPen(QPen(fg, 1.5))
            p.drawLine(5, 5, 5, 13)
            p.drawLine(5, 13, 15, 13)
            p.drawLine(15, 5, 15, 13)
            p.drawLine(5, 5, 15, 5)
            # Drop
            p.setBrush(QBrush(accent))
            p.setPen(Qt.NoPen)
            p.drawEllipse(8, 14, 4, 5)

        elif tool_id == "line":
            # Diagonal line
            p.setPen(QPen(fg, 2))
            p.drawLine(4, 16, 16, 4)

        elif tool_id == "rectangle":
            # Rectangle outline
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(fg, 1.5))
            p.drawRect(3, 5, 14, 10)

        elif tool_id == "ellipse":
            # Ellipse outline
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(fg, 1.5))
            p.drawEllipse(2, 4, 16, 12)

        elif tool_id == "select":
            # Dashed selection rectangle
            dash_pen = QPen(fg, 1.2, Qt.DashLine)
            p.setPen(dash_pen)
            p.setBrush(Qt.NoBrush)
            p.drawRect(3, 4, 14, 12)

        p.end()
        return QIcon(pixmap)

    @staticmethod
    def _make_toolbar_icon(icon_id: str, size: int = 18) -> QIcon:
        """Generate icons for toolbar buttons (zoom, filled toggle, etc.)."""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing, True)
        fg = QColor(60, 60, 60)

        if icon_id == "zoom_in":
            # Magnifying glass with +
            p.setPen(QPen(fg, 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(2, 2, 10, 10)
            p.setPen(QPen(fg, 2))
            p.drawLine(10, 10, 16, 16)
            # Plus
            p.setPen(QPen(fg, 1.5))
            p.drawLine(5, 7, 9, 7)
            p.drawLine(7, 5, 7, 9)

        elif icon_id == "zoom_out":
            # Magnifying glass with -
            p.setPen(QPen(fg, 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(2, 2, 10, 10)
            p.setPen(QPen(fg, 2))
            p.drawLine(10, 10, 16, 16)
            # Minus
            p.setPen(QPen(fg, 1.5))
            p.drawLine(5, 7, 9, 7)

        elif icon_id == "filled":
            # Outlined rect on left, filled rect on right
            p.setPen(QPen(fg, 1.2))
            p.setBrush(Qt.NoBrush)
            p.drawRect(1, 4, 7, 10)
            p.setBrush(QBrush(fg))
            p.drawRect(10, 4, 7, 10)

        p.end()
        return QIcon(pixmap)

    # ------------------------------------------------------------------
    # Tool management
    # ------------------------------------------------------------------

    def _init_tools(self):
        self._tools = {
            "pencil": PencilTool(),
            "eraser": EraserTool(),
            "color_picker": ColorPickerTool(),
            "fill": FillTool(),
            "line": LineTool(),
            "rectangle": RectTool(),
            "ellipse": EllipseTool(),
            "select": SelectTool(),
        }

    def _select_tool(self, tool_id: str):
        # Commit any floating selection before switching
        if self._active_tool_name == "select" and tool_id != "select":
            select_tool = self._tools.get("select")
            if select_tool and select_tool.has_floating():
                self.canvas.take_stroke_snapshot()
                select_tool.commit(self.canvas.get_image())
                self._on_canvas_modified()

        self._active_tool_name = tool_id
        tool = self._tools.get(tool_id)
        if tool:
            tool.reset()
            self.canvas.set_tool(tool)
            self.update_status(self.tr("Tool: {0}").format(tool_id.replace("_", " ").title()))

        # Check corresponding action
        for action in self.tool_group.actions():
            if action.data() == tool_id:
                action.setChecked(True)
                break

        # Sync dropdown without re-triggering
        if hasattr(self, '_tool_combo'):
            idx = self._tool_combo.findData(tool_id)
            if idx >= 0 and self._tool_combo.currentIndex() != idx:
                self._tool_combo.blockSignals(True)
                self._tool_combo.setCurrentIndex(idx)
                self._tool_combo.blockSignals(False)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_color_selected(self, color: QColor):
        self.canvas.set_color(color)

    def _on_color_picked(self, color: QColor):
        self.color_palette.set_foreground(color)
        self.canvas.set_color(color)
        # Auto-switch back to pencil after picking
        self._select_tool("pencil")

    def _on_canvas_modified(self):
        """Called when a stroke finishes."""
        snapshot = self.canvas.get_stroke_snapshot()
        if snapshot:
            cmd = SpriteEditCommand(
                self, snapshot, self.canvas.get_image(),
                self.tr("Draw")
            )
            self.undo_stack.push(cmd)
            self.canvas.clear_stroke_snapshot()

        # Sync canvas image back to frame timeline
        self.frame_timeline.update_current_frame(self.canvas.get_image())
        self.data_modified.emit(self.asset_name)

    def _on_frame_selected(self, index: int):
        """Switch canvas to show the selected frame."""
        frame = self.frame_timeline.get_current_frame()
        if frame:
            self.canvas.set_image(frame)

    def _on_frames_changed(self):
        """Frame list was modified (add/delete/duplicate)."""
        self.data_modified.emit(self.asset_name)

    def _toggle_filled(self):
        filled = self._filled_action.isChecked()
        for name in ("rectangle", "ellipse"):
            tool = self._tools.get(name)
            if tool:
                tool.filled = filled

    def _toggle_grid(self):
        self.canvas.set_show_grid(self._grid_action.isChecked())

    def _zoom_in(self):
        self.canvas.set_zoom(self.canvas.get_zoom() + 1)

    def _zoom_out(self):
        self.canvas.set_zoom(self.canvas.get_zoom() - 1)

    def _on_zoom_changed(self, zoom: int):
        self._zoom_label.setText(f" {zoom}x ")

    def _on_brush_size_changed(self, size: int):
        for tool in self._tools.values():
            tool.size = size

    def _mirror_h(self):
        self.canvas.take_stroke_snapshot()
        img = self.canvas.get_image()
        mirrored = mirror_horizontal(img)
        self.canvas.set_image(mirrored)
        self._on_canvas_modified()

    def _mirror_v(self):
        self.canvas.take_stroke_snapshot()
        img = self.canvas.get_image()
        mirrored = mirror_vertical(img)
        self.canvas.set_image(mirrored)
        self._on_canvas_modified()

    # ------------------------------------------------------------------
    # Clipboard / selection shortcuts (via canvas signals)
    # ------------------------------------------------------------------

    def _shortcut_copy(self):
        select_tool = self._tools.get("select")
        if select_tool and select_tool.copy_selection(self.canvas.get_image()):
            self.update_status(self.tr("Copied selection"))

    def _shortcut_cut(self):
        select_tool = self._tools.get("select")
        if select_tool and (select_tool.selection_rect or select_tool.has_floating()):
            self.canvas.take_stroke_snapshot()
            if select_tool.cut_selection(self.canvas.get_image()):
                self._on_canvas_modified()
                self.canvas.viewport().update()
                self.update_status(self.tr("Cut selection"))

    def _shortcut_paste(self):
        select_tool = self._tools.get("select")
        if not select_tool or not select_tool.has_clipboard():
            return
        if self._active_tool_name != "select":
            self._select_tool("select")
        self.canvas.take_stroke_snapshot()
        if select_tool.paste(self.canvas.get_image()):
            self.canvas.viewport().update()
            self.update_status(self.tr("Pasted from clipboard"))

    def _shortcut_delete(self):
        select_tool = self._tools.get("select")
        if select_tool and (select_tool.selection_rect or select_tool.has_floating()):
            self.canvas.take_stroke_snapshot()
            if select_tool.delete_selection(self.canvas.get_image()):
                self._on_canvas_modified()
                self.canvas.viewport().update()

    # ------------------------------------------------------------------
    # Canvas right-click context menu
    # ------------------------------------------------------------------

    def _show_canvas_context_menu(self, global_pos: 'QPoint'):
        select_tool = self._tools.get("select")
        has_sel = select_tool and (select_tool.selection_rect or select_tool.has_floating())
        has_clip = select_tool and select_tool.has_clipboard()

        menu = QMenu(self)

        copy_act = menu.addAction(self.tr("Copy\tCtrl+C"))
        copy_act.setEnabled(bool(has_sel))
        copy_act.triggered.connect(self._shortcut_copy)

        cut_act = menu.addAction(self.tr("Cut\tCtrl+X"))
        cut_act.setEnabled(bool(has_sel))
        cut_act.triggered.connect(self._shortcut_cut)

        paste_act = menu.addAction(self.tr("Paste\tCtrl+V"))
        paste_act.setEnabled(bool(has_clip))
        paste_act.triggered.connect(self._shortcut_paste)

        menu.addSeparator()

        delete_act = menu.addAction(self.tr("Delete\tDel"))
        delete_act.setEnabled(bool(has_sel))
        delete_act.triggered.connect(self._shortcut_delete)

        if has_sel:
            deselect_act = menu.addAction(self.tr("Deselect\tEsc"))
            deselect_act.triggered.connect(
                lambda: self._on_canvas_key(Qt.Key_Escape))

        menu.addSeparator()

        select_all_act = menu.addAction(self.tr("Select All"))
        select_all_act.triggered.connect(self._select_all)

        menu.exec(global_pos)

    def _select_all(self):
        """Select the entire canvas."""
        if self._active_tool_name != "select":
            self._select_tool("select")
        select_tool = self._tools.get("select")
        if select_tool:
            img = self.canvas.get_image()
            select_tool.selection_rect = QRect(0, 0, img.width(), img.height())
            select_tool._start = (0, 0)
            select_tool._end = (img.width() - 1, img.height() - 1)
            self.canvas.viewport().update()

    # ------------------------------------------------------------------
    # Keyboard shortcuts for tools (forwarded from canvas key_pressed signal)
    # ------------------------------------------------------------------

    def _on_canvas_key(self, key: int):
        # Escape for selection
        select_tool = self._tools.get("select")
        if self._active_tool_name == "select" and select_tool and key == Qt.Key_Escape:
            if select_tool.has_floating():
                self.canvas.take_stroke_snapshot()
                select_tool.commit(self.canvas.get_image())
                self._on_canvas_modified()
            else:
                select_tool.selection_rect = None
            self.canvas.viewport().update()
            return

        # Tool shortcuts
        shortcuts = {
            Qt.Key_P: "pencil",
            Qt.Key_E: "eraser",
            Qt.Key_I: "color_picker",
            Qt.Key_G: "fill",
            Qt.Key_L: "line",
            Qt.Key_R: "rectangle",
            Qt.Key_O: "ellipse",
            Qt.Key_S: "select",
        }
        tool_id = shortcuts.get(key)
        if tool_id:
            self._select_tool(tool_id)

    # ------------------------------------------------------------------
    # BaseEditor abstract method implementations
    # ------------------------------------------------------------------

    def load_data(self, data: Dict[str, Any]):
        """Load sprite data: read image file, split into frames."""
        file_path_str = data.get("file_path", "")
        frame_width = data.get("frame_width", 32)
        frame_height = data.get("frame_height", 32)
        num_frames = data.get("frames", 1)
        animation_type = data.get("animation_type", "single")
        speed = data.get("speed", 10.0)

        frames = []

        if file_path_str and self.project_path:
            abs_path = Path(self.project_path) / file_path_str
            if abs_path.exists():
                full_image = QImage(str(abs_path))
                if not full_image.isNull():
                    full_image = full_image.convertToFormat(QImage.Format_ARGB32)

                    if animation_type == "single" or num_frames <= 1:
                        frames.append(full_image)
                    elif animation_type == "strip_h":
                        for i in range(num_frames):
                            x = i * frame_width
                            if x + frame_width <= full_image.width():
                                frames.append(full_image.copy(x, 0, frame_width, frame_height))
                    elif animation_type == "strip_v":
                        for i in range(num_frames):
                            y = i * frame_height
                            if y + frame_height <= full_image.height():
                                frames.append(full_image.copy(0, y, frame_width, frame_height))
                    elif animation_type == "grid":
                        cols = max(1, full_image.width() // frame_width)
                        for i in range(num_frames):
                            col = i % cols
                            row = i // cols
                            x = col * frame_width
                            y = row * frame_height
                            if (x + frame_width <= full_image.width() and
                                    y + frame_height <= full_image.height()):
                                frames.append(full_image.copy(x, y, frame_width, frame_height))

        # Fallback: create a single blank frame
        if not frames:
            w = data.get("width", 32) or 32
            h = data.get("height", 32) or 32
            blank = QImage(w, h, QImage.Format_ARGB32)
            blank.fill(QColor(0, 0, 0, 0))
            frames.append(blank)

        self.frame_timeline.set_fps(speed)
        self.frame_timeline.set_frames(frames)
        self.canvas.set_image(self.frame_timeline.get_current_frame())

    def get_data(self) -> Dict[str, Any]:
        """Return sprite metadata dict (image saving happens in save())."""
        frames = self.frame_timeline.get_frames()
        num_frames = len(frames)
        fw, fh = self.frame_timeline.get_frame_size()

        data = dict(self.asset_data)
        data.update({
            "frame_width": fw,
            "frame_height": fh,
            "width": fw * num_frames if num_frames > 1 else fw,
            "height": fh,
            "frames": num_frames,
            "animation_type": "strip_h" if num_frames > 1 else "single",
            "speed": self.frame_timeline._fps,
            "origin_x": data.get("origin_x", fw // 2),
            "origin_y": data.get("origin_y", fh // 2),
            "asset_type": "sprite",
        })
        return data

    def validate_data(self) -> tuple[bool, str]:
        frames = self.frame_timeline.get_frames()
        if not frames:
            return False, self.tr("No frames in sprite")
        return True, ""

    # ------------------------------------------------------------------
    # Save — writes the PNG to disk before emitting save_requested
    # ------------------------------------------------------------------

    def save(self):
        """Override save to write image file before metadata save."""
        if self.is_read_only:
            return False

        is_valid, msg = self.validate_data()
        if not is_valid:
            QMessageBox.warning(self, self.tr("Validation Error"), msg)
            return False

        try:
            # Composite frames into strip
            strip_image = self.frame_timeline.composite_strip()

            # Determine destination path
            file_ext = ".png"
            relative_path = f"sprites/{self.asset_name}{file_ext}"
            if self.project_path:
                dest = Path(self.project_path) / relative_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                strip_image.save(str(dest), "PNG")
                logger.info(f"Saved sprite image: {dest}")

                # Update file_path in asset data
                self.asset_data["file_path"] = relative_path

                # Regenerate thumbnail
                self._regenerate_thumbnail(dest)

            # Now do the normal metadata save via BaseEditor
            current_data = self.get_data()
            current_data["file_path"] = relative_path

            self.save_requested.emit(self.asset_name, current_data)

            self.asset_data = current_data.copy()
            self.is_modified = False
            self.save_action.setEnabled(False)
            self.update_window_title()
            self.update_status(self.tr("Saved: {0}").format(self.asset_name))

            if hasattr(self, 'status_widget'):
                self.status_widget.set_saved()

            return True

        except Exception as e:
            logger.error(f"Error saving sprite: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Save Error"),
                                 self.tr("Failed to save sprite: {0}").format(e))
            return False

    def _regenerate_thumbnail(self, image_path: Path):
        """Regenerate thumbnail using AssetManager if available."""
        try:
            # Walk up the widget tree to find the IDE and its asset manager
            parent = self.parent()
            while parent:
                if hasattr(parent, 'asset_manager') and parent.asset_manager:
                    sprite_data = self.get_data()
                    thumb = parent.asset_manager.generate_thumbnail(
                        image_path, self.asset_name, sprite_data
                    )
                    if thumb:
                        self.asset_data["thumbnail"] = str(Path("thumbnails") / f"{self.asset_name}_thumb.png")
                    return
                parent = parent.parent()
        except Exception as e:
            logger.debug(f"Could not regenerate thumbnail: {e}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_frame_image(self, frame_index: int, image: QImage):
        """Set a specific frame's image (used by undo/redo)."""
        frames = self.frame_timeline.get_frames()
        if 0 <= frame_index < len(frames):
            frames[frame_index] = image.copy()
            self.frame_timeline.set_frames(frames)
            self.frame_timeline.set_current_index(frame_index)
            self.canvas.set_image(image)
