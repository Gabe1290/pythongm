#!/usr/bin/env python3
"""
Sprite Editor — main editor widget.
Inherits BaseEditor and integrates canvas, tools, color palette, and frame timeline.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QToolBar,
    QLabel, QSpinBox, QSizePolicy, QMessageBox, QToolButton, QMenu,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QImage, QColor, QUndoCommand, QAction, QActionGroup, QIcon
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

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------

    def _setup_sprite_ui(self):
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add sprite-specific toolbar actions
        self._add_tool_actions()

        # Vertical splitter: canvas area on top, frame timeline on bottom
        vsplitter = QSplitter(Qt.Vertical)

        # Top part: color palette + centered square canvas
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)

        # Left panel — color palette
        self.color_palette = ColorPaletteWidget()
        self.color_palette.setMaximumWidth(120)
        self.color_palette.color_selected.connect(self._on_color_selected)
        top_layout.addWidget(self.color_palette)

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
        """Add sprite-specific tool buttons to the base toolbar."""
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

        for tool_id, label, tooltip in tool_defs:
            action = QAction(label, self)
            action.setToolTip(tooltip)
            action.setCheckable(True)
            action.setData(tool_id)
            action.triggered.connect(lambda checked, tid=tool_id: self._select_tool(tid))
            self.tool_group.addAction(action)
            self.toolbar.addAction(action)
            if tool_id == "pencil":
                action.setChecked(True)

        self.toolbar.addSeparator()

        # Filled mode toggle (for rect/ellipse)
        self._filled_action = self.toolbar.addAction(self.tr("Filled"), self._toggle_filled)
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

        # Zoom controls
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.tr("Zoom -"), self._zoom_out)
        self._zoom_label = QLabel(" 10x ")
        self.toolbar.addWidget(self._zoom_label)
        self.toolbar.addAction(self.tr("Zoom +"), self._zoom_in)

        # Brush size
        self.toolbar.addSeparator()
        size_label = QLabel(self.tr(" Size: "))
        self.toolbar.addWidget(size_label)
        self._size_spin = QSpinBox()
        self._size_spin.setRange(1, 16)
        self._size_spin.setValue(1)
        self._size_spin.setFixedWidth(50)
        self._size_spin.valueChanged.connect(self._on_brush_size_changed)
        self.toolbar.addWidget(self._size_spin)

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
    # Keyboard shortcuts for tools
    # ------------------------------------------------------------------

    def keyPressEvent(self, event):
        key = event.key()
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
        if tool_id and not event.modifiers():
            self._select_tool(tool_id)
            return
        super().keyPressEvent(event)

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
