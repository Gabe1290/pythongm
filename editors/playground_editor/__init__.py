#!/usr/bin/env python3
"""
Playground Editor - Main class
Visual editor for creating Aseba .playground files.
"""

import json
import math
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QScrollArea,
    QToolBar, QMessageBox, QLabel, QDialog, QFormLayout,
    QSpinBox, QDoubleSpinBox, QComboBox, QDialogButtonBox, QFileDialog,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap

from core.logger import get_logger
logger = get_logger(__name__)

from .playground_canvas import PlaygroundCanvas, PlaygroundEditMode, DEFAULT_COLORS
from .playground_properties import PlaygroundElementProperties
from .playground_tool_palette import PlaygroundToolPalette
from .color_manager import PlaygroundColorManager
from .playground_elements import PlaygroundWall, PlaygroundRobot
from .playground_undo_commands import ModifyElementCommand


class PlaygroundEditor(QWidget):
    """Visual editor for Aseba playground files"""

    save_requested = Signal(str, dict)
    close_requested = Signal(str)
    data_modified = Signal(str)
    playground_editor_activated = Signal(str, dict)

    def __init__(self, project_path, parent=None):
        super().__init__(parent)
        self.project_path = Path(project_path)
        self.asset_name = ""
        self.is_modified = False
        self.ground_texture_filename = ""  # filename relative to playgrounds/

        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.auto_save)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(4)

        # Tool palette
        self.tool_palette = PlaygroundToolPalette()
        left_layout.addWidget(self.tool_palette)

        # Color manager
        self.color_manager = PlaygroundColorManager()
        left_layout.addWidget(self.color_manager)

        # Element properties
        self.element_properties = PlaygroundElementProperties()
        left_layout.addWidget(self.element_properties)

        left_panel.setMaximumWidth(280)
        splitter.addWidget(left_panel)

        # Center - Canvas in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        self.canvas = PlaygroundCanvas()
        scroll_area.setWidget(self.canvas)
        splitter.addWidget(scroll_area)

        splitter.setSizes([280, 600])

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(splitter)
        main_layout.addWidget(content)

    def create_toolbar(self):
        """Create the playground editor toolbar"""
        self.toolbar = QToolBar(self.tr("Playground Editor"))
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)

        # Save
        save_action = self.toolbar.addAction(self.tr("Save"))
        save_action.setToolTip(self.tr("Save playground (Ctrl+S)"))
        save_action.triggered.connect(self.save)

        self.toolbar.addSeparator()

        # Undo/Redo
        self.undo_action = self.toolbar.addAction(self.tr("Undo"))
        self.undo_action.setToolTip(self.tr("Undo (Ctrl+Z)"))
        self.undo_action.setEnabled(False)

        self.redo_action = self.toolbar.addAction(self.tr("Redo"))
        self.redo_action.setToolTip(self.tr("Redo (Ctrl+Y)"))
        self.redo_action.setEnabled(False)

        self.toolbar.addSeparator()

        # Grid toggle
        self.grid_action = self.toolbar.addAction(self.tr("Grid"))
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.setToolTip(self.tr("Toggle grid display"))

        # Snap toggle
        self.snap_action = self.toolbar.addAction(self.tr("Snap"))
        self.snap_action.setCheckable(True)
        self.snap_action.setChecked(True)
        self.snap_action.setToolTip(self.tr("Snap to grid"))

        self.toolbar.addSeparator()

        # Wall thickness control
        self.toolbar.addWidget(QLabel(self.tr(" Thickness: ")))
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(1.0, 50.0)
        self.thickness_spin.setDecimals(1)
        self.thickness_spin.setSingleStep(0.5)
        self.thickness_spin.setValue(5.0)
        self.thickness_spin.setFixedWidth(70)
        self.thickness_spin.setToolTip(self.tr("Default wall thickness for drag-to-draw"))
        self.thickness_spin.valueChanged.connect(self._on_thickness_changed)
        self.toolbar.addWidget(self.thickness_spin)

        # Block size control
        self.toolbar.addWidget(QLabel(self.tr(" Block: ")))
        self.block_size_spin = QDoubleSpinBox()
        self.block_size_spin.setRange(4.0, 200.0)
        self.block_size_spin.setDecimals(0)
        self.block_size_spin.setSingleStep(1.0)
        self.block_size_spin.setValue(20.0)
        self.block_size_spin.setFixedWidth(60)
        self.block_size_spin.setToolTip(self.tr("Block size for block-paint mode"))
        self.block_size_spin.valueChanged.connect(self._on_block_size_changed)
        self.toolbar.addWidget(self.block_size_spin)

        # Block paint color picker
        self.block_color_combo = QComboBox()
        self.block_color_combo.setFixedWidth(100)
        self.block_color_combo.setToolTip(self.tr("Color for painted blocks"))
        self.block_color_combo.currentTextChanged.connect(self._on_block_color_changed)
        self.toolbar.addWidget(self.block_color_combo)

        self.toolbar.addSeparator()

        # Arena settings
        arena_action = self.toolbar.addAction(self.tr("Arena Settings"))
        arena_action.setToolTip(self.tr("Configure arena dimensions and background"))
        arena_action.triggered.connect(self.show_arena_settings)

        self.toolbar.addSeparator()

        # Run
        run_action = self.toolbar.addAction(self.tr("▶ Run"))
        run_action.setToolTip(self.tr("Simulate the playground with linked robot code"))
        run_action.triggered.connect(self.run_playground)

        # Export
        export_action = self.toolbar.addAction(self.tr("Export .playground"))
        export_action.setToolTip(self.tr("Export as Aseba .playground file"))
        export_action.triggered.connect(self.export_playground)

    def setup_connections(self):
        """Connect signals between components"""
        # Tool palette -> canvas edit mode
        self.tool_palette.mode_changed.connect(self._on_mode_changed)

        # Canvas -> properties
        self.canvas.element_selected.connect(self._on_element_selected)
        self.canvas.element_moved.connect(self._on_element_moved)
        self.canvas.element_added.connect(lambda _: self.mark_modified())

        # Properties -> canvas
        self.element_properties.property_changed.connect(
            self._on_property_changed)

        # Color manager -> canvas + properties
        self.color_manager.colors_changed.connect(self._on_colors_changed)

        # Undo/Redo
        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)
        self.canvas.undo_stack.canUndoChanged.connect(
            self.undo_action.setEnabled)
        self.canvas.undo_stack.canRedoChanged.connect(
            self.redo_action.setEnabled)

        # Grid/Snap
        self.grid_action.toggled.connect(self._on_grid_toggled)
        self.snap_action.toggled.connect(self._on_snap_toggled)

    # ─── Loading and saving ─────────────────────────────────────

    def load_asset(self, asset_name, asset_data):
        """Load a playground asset"""
        self.asset_name = asset_name
        data = asset_data or {}

        # Arena
        arena = data.get('arena', {})
        self.canvas.set_arena_properties(
            arena.get('width', 400),
            arena.get('height', 400),
            arena.get('color', 'white'),
        )

        # Ground texture
        self.ground_texture_filename = arena.get('ground_texture', '') or ''
        self._load_ground_texture()

        # Colors
        colors = data.get('colors', list(DEFAULT_COLORS))
        self.canvas.set_colors(colors)
        self.color_manager.set_colors(colors)
        names = self.color_manager.get_color_names()
        self.element_properties.set_color_names(names)
        self._refresh_block_color_combo(names)

        # Elements
        self.canvas.load_data(
            data.get('walls', []),
            data.get('robots', []),
        )

        # Available Thymio objects for linking
        self._refresh_linkable_objects()

        self.is_modified = False
        self.playground_editor_activated.emit(asset_name, data)
        logger.info(f"Loaded playground: {asset_name}")

    def _refresh_linkable_objects(self):
        """Load available Thymio objects from project and pass to properties panel"""
        names = []
        try:
            project_file = self.project_path / "project.json"
            if project_file.exists():
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                objects = project_data.get('assets', {}).get('objects', {})
                for name, obj_data in objects.items():
                    # Only show objects that look like Thymio objects
                    if (name.lower().startswith('thymio')
                            or obj_data.get('is_thymio')
                            or self._object_uses_thymio_events(obj_data)):
                        names.append(name)
        except Exception as e:
            logger.warning(f"Could not load objects for linking: {e}")
        self.element_properties.set_linkable_objects(names)

    @staticmethod
    def _object_uses_thymio_events(obj_data):
        """Heuristic: object uses Thymio events if any event name starts with 'thymio_'"""
        events = obj_data.get('events', {}) or {}
        for ev_name in events:
            if ev_name.startswith('thymio_'):
                return True
        return False

    def get_data(self):
        """Get current playground data as dict"""
        return {
            'name': self.asset_name,
            'asset_type': 'playground',
            'arena': {
                'width': self.canvas.arena_width,
                'height': self.canvas.arena_height,
                'color': self.canvas.arena_color_name,
                'ground_texture': self.ground_texture_filename,
            },
            'colors': self.color_manager.get_colors(),
            'walls': self.canvas.get_walls_data(),
            'robots': self.canvas.get_robots_data(),
        }

    # ─── Ground texture management ──────────────────────────────

    def _texture_dir(self):
        """Directory where texture files are stored"""
        return self.project_path / "playgrounds"

    def _texture_path(self):
        """Full path to the current texture file, or None"""
        if not self.ground_texture_filename:
            return None
        return self._texture_dir() / self.ground_texture_filename

    def _load_ground_texture(self):
        """Load ground texture from disk into the canvas"""
        path = self._texture_path()
        if path and path.exists():
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                self.canvas.ground_texture = pixmap
                self.canvas.update()
                return
        self.canvas.ground_texture = None
        self.canvas.update()

    def pick_ground_texture(self):
        """Open file dialog to pick a ground texture PNG"""
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Select Ground Texture"),
            str(self.project_path),
            self.tr("Images (*.png *.jpg *.jpeg *.bmp)"),
        )
        if not path:
            return False

        src = Path(path)
        tex_dir = self._texture_dir()
        tex_dir.mkdir(parents=True, exist_ok=True)

        # Copy into project with a name derived from the playground
        safe_name = self.asset_name or "playground"
        dest_name = f"{safe_name}_texture{src.suffix.lower()}"
        dest = tex_dir / dest_name

        try:
            shutil.copy2(src, dest)
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("Texture Error"),
                self.tr("Could not copy texture:\n{}").format(e))
            return False

        self.ground_texture_filename = dest_name
        self._load_ground_texture()
        self.mark_modified()
        return True

    def clear_ground_texture(self):
        """Remove the ground texture"""
        self.ground_texture_filename = ""
        self.canvas.ground_texture = None
        self.canvas.update()
        self.mark_modified()

    def save(self):
        """Save the playground"""
        data = self.get_data()
        self.save_requested.emit(self.asset_name, data)
        self.is_modified = False
        logger.info(f"Saved playground: {self.asset_name}")
        return True

    def auto_save(self):
        """Auto-save if modified"""
        if self.is_modified:
            self.save()

    def mark_modified(self):
        """Mark playground as modified"""
        self.is_modified = True
        self.data_modified.emit(self.asset_name)
        # Start auto-save timer
        self.auto_save_timer.start(3000)

    # ─── Event handlers ─────────────────────────────────────────

    def _on_mode_changed(self, mode):
        mode_map = {
            "select": PlaygroundEditMode.SELECT,
            "wall": PlaygroundEditMode.WALL,
            "robot": PlaygroundEditMode.ROBOT,
            "block": PlaygroundEditMode.BLOCK,
        }
        self.canvas.edit_mode = mode_map.get(mode, PlaygroundEditMode.SELECT)

    def _on_element_selected(self, element):
        self.element_properties.set_element(element)

    def _on_element_moved(self, element):
        self.element_properties.set_element(element)
        self.mark_modified()

    def _on_property_changed(self, element, prop_name, value):
        if prop_name == 'delete':
            self.canvas.remove_element(element)
            self.element_properties.set_element(None)
            self.mark_modified()
            return

        old_value = getattr(element, prop_name, None)
        if old_value == value:
            return
        cmd = ModifyElementCommand(
            self.canvas, element, prop_name, old_value, value,
            f"Change {prop_name}")
        self.canvas.undo_stack.push(cmd)
        # Refresh properties to show current values
        self.element_properties.set_element(element)
        self.mark_modified()

    def _on_colors_changed(self, colors):
        self.canvas.set_colors(colors)
        names = self.color_manager.get_color_names()
        self.element_properties.set_color_names(names)
        self._refresh_block_color_combo(names)
        self.mark_modified()

    def _refresh_block_color_combo(self, names):
        """Refresh the block paint color combo with current color names"""
        current = self.block_color_combo.currentText()
        self.block_color_combo.blockSignals(True)
        self.block_color_combo.clear()
        self.block_color_combo.addItems(names)
        idx = self.block_color_combo.findText(current)
        if idx >= 0:
            self.block_color_combo.setCurrentIndex(idx)
        elif names:
            # Default to "wall" if present, else first
            idx = self.block_color_combo.findText("wall")
            self.block_color_combo.setCurrentIndex(idx if idx >= 0 else 0)
            self.canvas.block_paint_color = self.block_color_combo.currentText()
        self.block_color_combo.blockSignals(False)

    def _on_grid_toggled(self, checked):
        self.canvas.grid_enabled = checked
        self.canvas.update()

    def _on_snap_toggled(self, checked):
        self.canvas.snap_to_grid = checked

    def _on_thickness_changed(self, value):
        self.canvas.default_wall_thickness = value

    def _on_block_size_changed(self, value):
        self.canvas.block_size = float(value)
        self.canvas.update()

    def _on_block_color_changed(self, name):
        if name:
            self.canvas.block_paint_color = name

    # ─── Undo/Redo ──────────────────────────────────────────────

    def undo(self):
        if self.canvas.undo_stack.canUndo():
            self.canvas.undo_stack.undo()
            self.mark_modified()

    def redo(self):
        if self.canvas.undo_stack.canRedo():
            self.canvas.undo_stack.redo()
            self.mark_modified()

    # ─── Arena settings dialog ──────────────────────────────────

    def show_arena_settings(self):
        """Show dialog to configure arena dimensions, color, and ground texture"""
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Arena Settings"))
        layout = QFormLayout(dialog)

        width_spin = QSpinBox()
        width_spin.setRange(100, 5000)
        width_spin.setValue(self.canvas.arena_width)
        layout.addRow(self.tr("Width:"), width_spin)

        height_spin = QSpinBox()
        height_spin.setRange(100, 5000)
        height_spin.setValue(self.canvas.arena_height)
        layout.addRow(self.tr("Height:"), height_spin)

        color_combo = QComboBox()
        color_combo.addItems(self.color_manager.get_color_names())
        idx = color_combo.findText(self.canvas.arena_color_name)
        if idx >= 0:
            color_combo.setCurrentIndex(idx)
        layout.addRow(self.tr("Background:"), color_combo)

        grid_spin = QSpinBox()
        grid_spin.setRange(5, 100)
        grid_spin.setValue(self.canvas.grid_size)
        layout.addRow(self.tr("Grid size:"), grid_spin)

        # Ground texture row
        tex_row = QWidget()
        tex_layout = QHBoxLayout(tex_row)
        tex_layout.setContentsMargins(0, 0, 0, 0)
        tex_label = QLabel(self.ground_texture_filename or self.tr("(none)"))
        tex_label.setStyleSheet("color: #555;")
        browse_btn = QPushButton(self.tr("Browse..."))
        clear_btn = QPushButton(self.tr("Clear"))
        clear_btn.setEnabled(bool(self.ground_texture_filename))

        def _browse():
            if self.pick_ground_texture():
                tex_label.setText(self.ground_texture_filename or self.tr("(none)"))
                clear_btn.setEnabled(bool(self.ground_texture_filename))

        def _clear():
            self.clear_ground_texture()
            tex_label.setText(self.tr("(none)"))
            clear_btn.setEnabled(False)

        browse_btn.clicked.connect(_browse)
        clear_btn.clicked.connect(_clear)
        tex_layout.addWidget(tex_label, 1)
        tex_layout.addWidget(browse_btn)
        tex_layout.addWidget(clear_btn)
        layout.addRow(self.tr("Ground texture:"), tex_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() == QDialog.Accepted:
            self.canvas.grid_size = grid_spin.value()
            self.canvas.set_arena_properties(
                width_spin.value(),
                height_spin.value(),
                color_combo.currentText(),
            )
            self.mark_modified()

    # ─── Run (in-IDE simulation) ─────────────────────────────────

    def run_playground(self):
        """Launch the playground in a simulation window"""
        # Save before running so get_data() reflects current state
        data = self.get_data()

        # Load full project data (for linked objects' events)
        project_data = {}
        try:
            project_file = self.project_path / "project.json"
            if project_file.exists():
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                # Also load external object files (events are stored there)
                self._load_external_objects(project_data)
        except Exception as e:
            logger.warning(f"Could not load project data: {e}")

        try:
            from runtime.playground_runner import PlaygroundRunnerWindow
            self._runner_window = PlaygroundRunnerWindow(data, project_data, self)
            self._runner_window.show()
        except Exception as e:
            logger.error(f"Failed to launch playground runner: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, self.tr("Run Failed"),
                self.tr("Error launching simulator:\n{}").format(str(e)))

    def _load_external_objects(self, project_data):
        """Merge object data from objects/ directory files into project_data"""
        objects_dir = self.project_path / "objects"
        if not objects_dir.exists():
            return
        assets = project_data.setdefault('assets', {})
        objects = assets.setdefault('objects', {})
        for obj_name in list(objects.keys()):
            obj_file = objects_dir / f"{obj_name}.json"
            if obj_file.exists():
                try:
                    with open(obj_file, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                    # Merge file events into the object data
                    if 'events' in file_data:
                        objects[obj_name]['events'] = file_data['events']
                except Exception as e:
                    logger.debug(f"Could not load object file {obj_file}: {e}")

    # ─── Export ──────────────────────────────────────────────────

    def export_playground(self):
        """Export current playground as .playground file"""
        from export.Aseba.playground_exporter import PlaygroundExporter

        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("Export Playground"),
            str(self.project_path / f"{self.asset_name}.playground"),
            self.tr("Aseba Playground (*.playground)"),
        )
        if not path:
            return

        try:
            exporter = PlaygroundExporter()
            texture_path = self._texture_path()
            texture_arg = str(texture_path) if texture_path and texture_path.exists() else None
            exporter.export(self.get_data(), path, ground_texture_path=texture_arg)
            QMessageBox.information(
                self, self.tr("Export Successful"),
                self.tr("Playground exported to:\n{}").format(path))
        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(
                self, self.tr("Export Failed"),
                self.tr("Error exporting playground:\n{}").format(str(e)))
