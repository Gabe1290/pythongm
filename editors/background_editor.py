#!/usr/bin/env python3
"""
Background Editor — minimal editable editor for the ``backgrounds`` asset
type.

Same design philosophy as ``editors/script_editor.py``: a thin form over
the asset's editable fields (``tile_horizontal``, ``tile_vertical``), plus
a read-only image preview since "what does this background look like" is
the one thing the form fields can't answer. Re-importing the backing
image file is a separate toolbar action, not this editor's job.

Closes the TODO.md "Generic asset-type editor fallback" item for the
``backgrounds`` asset type.
"""

from pathlib import Path
from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QFormLayout, QLabel, QVBoxLayout,
)

from editors.base_editor import BaseEditor
from core.logger import get_logger

logger = get_logger(__name__)

_PREVIEW_MAX = 256


class BackgroundEditor(BaseEditor):
    """Form editor for background assets.

    Persisted shape on disk (see ``core/asset_manager.py``
    ``_create_asset_data``)::

        {
          "name": "<asset_name>",
          "asset_type": "background",
          "file_path": "backgrounds/<file>",   # not editable here
          "width": 1024, "height": 768,        # informational, read-only
          "tile_horizontal": False,
          "tile_vertical": False,
          "imported": True, "created": "...", "modified": "..."
        }

    Only ``tile_horizontal``/``tile_vertical`` are editable; everything
    else round-trips untouched.
    """

    def __init__(self, project_path: str = None, parent=None):
        super().__init__(project_path, parent)
        self._extra_fields: Dict[str, Any] = {}
        self._file_path = ''
        self._setup_content()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_content(self):
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(_PREVIEW_MAX)
        self.preview_label.setStyleSheet(
            "QLabel { border: 1px solid palette(mid); background: palette(base); }")
        layout.addWidget(self.preview_label)

        form = QFormLayout()
        form.setSpacing(8)

        self.file_label = QLabel('')
        self.file_label.setWordWrap(True)
        form.addRow(self.tr("File:"), self.file_label)

        self.size_label = QLabel('')
        form.addRow(self.tr("Size:"), self.size_label)

        self.tile_h_check = QCheckBox(self.tr("Tile horizontally"))
        self.tile_h_check.toggled.connect(self._on_field_changed)
        form.addRow('', self.tile_h_check)

        self.tile_v_check = QCheckBox(self.tr("Tile vertically"))
        self.tile_v_check.toggled.connect(self._on_field_changed)
        form.addRow('', self.tile_v_check)

        layout.addLayout(form)
        layout.addStretch()

    def _resolve_absolute_path(self) -> Path:
        if not self._file_path:
            return None
        if self.project_path:
            return Path(self.project_path) / self._file_path
        return Path(self._file_path)

    def _load_preview(self):
        abs_path = self._resolve_absolute_path()
        if not abs_path or not abs_path.exists():
            self.preview_label.setText(self.tr("(image not found)"))
            return
        pixmap = QPixmap(str(abs_path))
        if pixmap.isNull():
            self.preview_label.setText(self.tr("(could not load image)"))
            return
        scaled = pixmap.scaled(
            _PREVIEW_MAX * 2, _PREVIEW_MAX,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled)

    # ------------------------------------------------------------------
    # BaseEditor contract
    # ------------------------------------------------------------------

    def load_data(self, data: Dict[str, Any]):
        data = data if isinstance(data, dict) else {}
        self._file_path = data.get('file_path', '')
        self.file_label.setText(self._file_path or self.tr("(no file)"))

        width = data.get('width', 0)
        height = data.get('height', 0)
        self.size_label.setText(f"{width} × {height}" if width and height else self.tr("(unknown)"))

        self.tile_h_check.blockSignals(True)
        self.tile_h_check.setChecked(bool(data.get('tile_horizontal', False)))
        self.tile_h_check.blockSignals(False)

        self.tile_v_check.blockSignals(True)
        self.tile_v_check.setChecked(bool(data.get('tile_vertical', False)))
        self.tile_v_check.blockSignals(False)

        self._extra_fields = {
            k: v for k, v in data.items()
            if k not in ('tile_horizontal', 'tile_vertical', 'name', 'asset_type')
        }

        self._load_preview()

    def get_data(self) -> Dict[str, Any]:
        out: Dict[str, Any] = dict(self._extra_fields)
        out['tile_horizontal'] = self.tile_h_check.isChecked()
        out['tile_vertical'] = self.tile_v_check.isChecked()
        out['name'] = self.asset_name
        out['asset_type'] = 'background'
        return out

    def validate_data(self) -> tuple[bool, str]:
        return True, ""

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_field_changed(self, *_args):
        if self._saving:
            return
        if not self.is_modified:
            self.is_modified = True
            self.save_action.setEnabled(True)
            self.update_window_title()
            if hasattr(self, 'status_widget'):
                self.status_widget.set_modified(True, self.auto_save_enabled)
        self.data_modified.emit(self.asset_name or '')
