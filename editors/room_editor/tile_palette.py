#!/usr/bin/env python3
"""
Tile Palette dialog for Room Editor
Floating window that displays available tilesets and allows selecting individual tiles for placement
"""

from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                                QPushButton, QScrollArea, QSpinBox, QDialog,
                                QFormLayout, QCheckBox, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen

from core.logger import get_logger
logger = get_logger(__name__)


class TileGridWidget(QWidget):
    """Widget that displays a tileset image with a selectable grid overlay"""

    tile_selected = Signal(int, int)  # tile_x, tile_y in pixels

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.tile_width = 16
        self.tile_height = 16
        self.h_offset = 0
        self.v_offset = 0
        self.h_sep = 0
        self.v_sep = 0
        self.selected_tile_x = -1
        self.selected_tile_y = -1
        self.setMinimumSize(64, 64)

    def set_tileset(self, pixmap, tile_width, tile_height,
                    h_offset=0, v_offset=0, h_sep=0, v_sep=0):
        """Set the tileset image and grid parameters"""
        self.pixmap = pixmap
        self.tile_width = max(1, tile_width)
        self.tile_height = max(1, tile_height)
        self.h_offset = h_offset
        self.v_offset = v_offset
        self.h_sep = h_sep
        self.v_sep = v_sep
        self.selected_tile_x = -1
        self.selected_tile_y = -1

        if pixmap and not pixmap.isNull():
            self.setFixedSize(pixmap.width(), pixmap.height())
        else:
            self.setFixedSize(64, 64)
        self.update()

    def clear(self):
        """Clear the tileset display"""
        self.pixmap = None
        self.selected_tile_x = -1
        self.selected_tile_y = -1
        self.setFixedSize(64, 64)
        self.update()

    def paintEvent(self, event):
        """Draw the tileset with grid overlay"""
        painter = QPainter(self)

        if not self.pixmap or self.pixmap.isNull():
            painter.fillRect(self.rect(), QColor("#404040"))
            painter.setPen(QColor("#888888"))
            painter.drawText(self.rect(), Qt.AlignCenter, self.tr("No tileset"))
            return

        # Draw the tileset image
        painter.drawPixmap(0, 0, self.pixmap)

        # Draw grid overlay
        painter.setPen(QPen(QColor(0, 0, 0, 80), 1))
        img_w = self.pixmap.width()
        img_h = self.pixmap.height()

        x = self.h_offset
        while x < img_w:
            y = self.v_offset
            while y < img_h:
                painter.drawRect(x, y, self.tile_width, self.tile_height)
                y += self.tile_height + self.v_sep
            x += self.tile_width + self.h_sep

        # Highlight selected tile
        if self.selected_tile_x >= 0 and self.selected_tile_y >= 0:
            painter.setPen(QPen(QColor("#FF0000"), 2))
            painter.setBrush(QColor(255, 0, 0, 50))
            painter.drawRect(self.selected_tile_x, self.selected_tile_y,
                           self.tile_width, self.tile_height)

    def mousePressEvent(self, event):
        """Handle tile selection on click"""
        if event.button() != Qt.LeftButton or not self.pixmap:
            return

        pos = event.position().toPoint()
        # Find which tile cell was clicked
        tile_x, tile_y = self._pos_to_tile(pos)
        if tile_x >= 0 and tile_y >= 0:
            self.selected_tile_x = tile_x
            self.selected_tile_y = tile_y
            self.tile_selected.emit(tile_x, tile_y)
            self.update()

    def _pos_to_tile(self, pos):
        """Convert pixel position to tile origin (in pixels), or (-1,-1) if outside grid"""
        px, py = pos.x(), pos.y()

        # Check if inside the tileset area
        if not self.pixmap or px < self.h_offset or py < self.v_offset:
            return -1, -1

        # Calculate tile column/row
        cell_w = self.tile_width + self.h_sep
        cell_h = self.tile_height + self.v_sep
        if cell_w <= 0 or cell_h <= 0:
            return -1, -1

        col = (px - self.h_offset) // cell_w
        row = (py - self.v_offset) // cell_h

        tile_x = self.h_offset + col * cell_w
        tile_y = self.v_offset + row * cell_h

        # Verify click is within the tile area (not in separator)
        local_x = px - tile_x
        local_y = py - tile_y
        if local_x > self.tile_width or local_y > self.tile_height:
            return -1, -1

        # Verify within image bounds
        if tile_x + self.tile_width > self.pixmap.width():
            return -1, -1
        if tile_y + self.tile_height > self.pixmap.height():
            return -1, -1

        return tile_x, tile_y


class TilePaletteDialog(QDialog):
    """Floating dialog for selecting tiles from tilesets to place in rooms"""

    tile_selected = Signal(dict)  # Emits tile info dict
    selection_cleared = Signal()
    # Emitted when the user edits tilesheet metadata (size, sep, offset,
    # use_as_tileset) for the current background. Carries the background name
    # and a snapshot dict of the new metadata so the room editor can persist
    # it via project_manager.update_asset.
    background_metadata_changed = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Tile Palette"))
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)
        self.project_path = None
        self.project_data = None
        self.tileset_backgrounds = {}  # name -> asset data
        self.current_bg_name = ""
        self._loading_metadata = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Tileset selector
        selector_layout = QFormLayout()
        self.tileset_combo = QComboBox()
        self.tileset_combo.currentTextChanged.connect(self.on_tileset_changed)
        selector_layout.addRow(self.tr("Tileset:"), self.tileset_combo)
        layout.addLayout(selector_layout)

        # Tilesheet grid controls — size, separation (grid-line thickness),
        # and outer offset. Editing any of these updates the live grid
        # overlay AND persists back to the background asset, so e.g. a
        # 32x32 sheet with 1-pixel separator lines can be configured here
        # instead of hand-editing project.json.
        grid_group = QGroupBox(self.tr("Tilesheet grid"))
        grid_form = QGridLayout(grid_group)

        self.use_as_tileset_check = QCheckBox(self.tr("Use as tileset"))
        self.use_as_tileset_check.toggled.connect(self.on_metadata_changed)
        grid_form.addWidget(self.use_as_tileset_check, 0, 0, 1, 4)

        grid_form.addWidget(QLabel(self.tr("Tile W:")), 1, 0)
        self.tile_w_spin = QSpinBox()
        self.tile_w_spin.setRange(1, 512)
        self.tile_w_spin.setValue(16)
        self.tile_w_spin.valueChanged.connect(self.on_metadata_changed)
        grid_form.addWidget(self.tile_w_spin, 1, 1)

        grid_form.addWidget(QLabel(self.tr("Tile H:")), 1, 2)
        self.tile_h_spin = QSpinBox()
        self.tile_h_spin.setRange(1, 512)
        self.tile_h_spin.setValue(16)
        self.tile_h_spin.valueChanged.connect(self.on_metadata_changed)
        grid_form.addWidget(self.tile_h_spin, 1, 3)

        grid_form.addWidget(QLabel(self.tr("H sep:")), 2, 0)
        self.h_sep_spin = QSpinBox()
        self.h_sep_spin.setRange(0, 64)
        self.h_sep_spin.setToolTip(self.tr("Horizontal gap between tiles, in pixels (set to 1 for sheets with 1-px grid lines)"))
        self.h_sep_spin.valueChanged.connect(self.on_metadata_changed)
        grid_form.addWidget(self.h_sep_spin, 2, 1)

        grid_form.addWidget(QLabel(self.tr("V sep:")), 2, 2)
        self.v_sep_spin = QSpinBox()
        self.v_sep_spin.setRange(0, 64)
        self.v_sep_spin.setToolTip(self.tr("Vertical gap between tiles, in pixels"))
        self.v_sep_spin.valueChanged.connect(self.on_metadata_changed)
        grid_form.addWidget(self.v_sep_spin, 2, 3)

        grid_form.addWidget(QLabel(self.tr("H offset:")), 3, 0)
        self.h_offset_spin = QSpinBox()
        self.h_offset_spin.setRange(0, 512)
        self.h_offset_spin.setToolTip(self.tr("Left-edge offset before the first tile column, in pixels"))
        self.h_offset_spin.valueChanged.connect(self.on_metadata_changed)
        grid_form.addWidget(self.h_offset_spin, 3, 1)

        grid_form.addWidget(QLabel(self.tr("V offset:")), 3, 2)
        self.v_offset_spin = QSpinBox()
        self.v_offset_spin.setRange(0, 512)
        self.v_offset_spin.setToolTip(self.tr("Top-edge offset before the first tile row, in pixels"))
        self.v_offset_spin.valueChanged.connect(self.on_metadata_changed)
        grid_form.addWidget(self.v_offset_spin, 3, 3)

        layout.addWidget(grid_group)

        # Layer selector
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel(self.tr("Layer:")))
        self.layer_spin = QSpinBox()
        self.layer_spin.setRange(0, 7)
        self.layer_spin.setValue(0)
        layer_layout.addWidget(self.layer_spin)
        layout.addLayout(layer_layout)

        # Tile grid in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        self.tile_grid = TileGridWidget()
        self.tile_grid.tile_selected.connect(self.on_grid_tile_selected)
        scroll_area.setWidget(self.tile_grid)
        layout.addWidget(scroll_area, 1)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton(self.tr("Clear Tile"))
        clear_btn.clicked.connect(self.clear_selection)
        btn_layout.addWidget(clear_btn)

        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.hide)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def set_project_info(self, project_path, project_data):
        """Set project information and populate tileset list"""
        self.project_path = Path(project_path) if project_path else None
        self.project_data = project_data
        self.refresh_tileset_list()

    def refresh_tileset_list(self):
        """Refresh list of available tilesets from backgrounds"""
        self.tileset_combo.blockSignals(True)
        self.tileset_combo.clear()
        self.tileset_backgrounds.clear()

        if not self.project_data:
            self.tileset_combo.blockSignals(False)
            return

        backgrounds = self.project_data.get('assets', {}).get('backgrounds', {})
        for bg_name, bg_data in backgrounds.items():
            # Include all backgrounds - those marked as tilesets first
            self.tileset_backgrounds[bg_name] = bg_data

        # Sort: tilesets first, then regular backgrounds
        sorted_names = sorted(
            self.tileset_backgrounds.keys(),
            key=lambda n: (0 if self.tileset_backgrounds[n].get('use_as_tileset') else 1, n)
        )

        self.tileset_combo.addItem(self.tr("(none)"), "")
        for name in sorted_names:
            bg = self.tileset_backgrounds[name]
            prefix = "[T] " if bg.get('use_as_tileset') else ""
            self.tileset_combo.addItem(f"{prefix}{name}", name)

        self.tileset_combo.blockSignals(False)

    def on_tileset_changed(self, text):
        """Handle tileset selection change"""
        bg_name = self.tileset_combo.currentData()
        if not bg_name:
            self.tile_grid.clear()
            self.current_bg_name = ""
            self.selection_cleared.emit()
            return

        self.current_bg_name = bg_name
        bg_data = self.tileset_backgrounds.get(bg_name, {})

        # Load the background image
        pixmap = self._load_background_pixmap(bg_name)
        if not pixmap:
            self.tile_grid.clear()
            return

        # Get tile dimensions from background metadata. tile_width/height
        # may legitimately be 0 in older project files (non-tileset bgs);
        # clamp to 1 so the spinbox doesn't reject the value, then preserve
        # the original 0 in bg_data until the user actually edits.
        tw = max(1, int(bg_data.get('tile_width') or 16))
        th = max(1, int(bg_data.get('tile_height') or 16))
        ho = int(bg_data.get('h_offset', 0) or 0)
        vo = int(bg_data.get('v_offset', 0) or 0)
        hs = int(bg_data.get('h_sep', 0) or 0)
        vs = int(bg_data.get('v_sep', 0) or 0)
        use_as_tileset = bool(bg_data.get('use_as_tileset', False))

        # Mirror values to the UI without firing on_metadata_changed.
        self._loading_metadata = True
        try:
            self.tile_w_spin.setValue(tw)
            self.tile_h_spin.setValue(th)
            self.h_sep_spin.setValue(hs)
            self.v_sep_spin.setValue(vs)
            self.h_offset_spin.setValue(ho)
            self.v_offset_spin.setValue(vo)
            self.use_as_tileset_check.setChecked(use_as_tileset)
        finally:
            self._loading_metadata = False

        self.tile_grid.set_tileset(pixmap, tw, th, ho, vo, hs, vs)

    def on_metadata_changed(self, *_args):
        """Persist tilesheet metadata edits to bg_data and refresh the grid.

        Triggered by any of the six spinboxes or the use_as_tileset checkbox.
        Mutates bg_data in place (which is shared by reference with
        asset_manager.assets_cache) and emits background_metadata_changed so
        the room editor can route the change through project_manager."""
        if self._loading_metadata or not self.current_bg_name:
            return

        bg_data = self.tileset_backgrounds.get(self.current_bg_name)
        if bg_data is None:
            return

        tw = self.tile_w_spin.value()
        th = self.tile_h_spin.value()
        hs = self.h_sep_spin.value()
        vs = self.v_sep_spin.value()
        ho = self.h_offset_spin.value()
        vo = self.v_offset_spin.value()

        bg_data['tile_width'] = tw
        bg_data['tile_height'] = th
        bg_data['h_sep'] = hs
        bg_data['v_sep'] = vs
        bg_data['h_offset'] = ho
        bg_data['v_offset'] = vo
        bg_data['use_as_tileset'] = self.use_as_tileset_check.isChecked()

        pixmap = self._load_background_pixmap(self.current_bg_name)
        if pixmap:
            self.tile_grid.set_tileset(pixmap, tw, th, ho, vo, hs, vs)

        self.background_metadata_changed.emit(self.current_bg_name, dict(bg_data))

    def on_grid_tile_selected(self, tile_x, tile_y):
        """Handle tile selection from grid"""
        if not self.current_bg_name:
            return

        tile_info = {
            'background_name': self.current_bg_name,
            'tile_x': tile_x,
            'tile_y': tile_y,
            'width': self.tile_w_spin.value(),
            'height': self.tile_h_spin.value(),
            'depth': 1000000,
            'layer': self.layer_spin.value(),
        }
        self.tile_selected.emit(tile_info)

    def clear_selection(self):
        """Clear tile selection"""
        self.tile_grid.selected_tile_x = -1
        self.tile_grid.selected_tile_y = -1
        self.tile_grid.update()
        self.selection_cleared.emit()

    def _load_background_pixmap(self, bg_name):
        """Load a background image as QPixmap"""
        if not self.project_path or not self.project_data:
            return None

        bg_data = self.tileset_backgrounds.get(bg_name, {})
        file_path = bg_data.get('file_path', '')
        if not file_path:
            return None

        full_path = self.project_path / file_path
        if not full_path.exists():
            return None

        pixmap = QPixmap(str(full_path))
        return pixmap if not pixmap.isNull() else None

    def closeEvent(self, event):
        """Hide instead of closing so we can reopen"""
        self.hide()
        event.ignore()
