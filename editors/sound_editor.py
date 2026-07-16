#!/usr/bin/env python3
"""
Sound Editor — minimal editable editor for the ``sounds`` asset type.

Same design philosophy as ``editors/script_editor.py``: a thin form over
the asset's editable fields (``volume``, ``loop``), not a waveform editor
or a re-import surface (that's the toolbar's "Import Sound" action). Adds
one thing scripts don't need — a Play/Stop preview button, since "does
this sound clip right" is the one thing a form field can't answer.

Closes the TODO.md "Generic asset-type editor fallback" item for the
``sounds`` asset type.
"""

from pathlib import Path
from typing import Any, Dict

from PySide6.QtWidgets import (
    QCheckBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout, QWidget,
)

from editors.base_editor import BaseEditor
from core.logger import get_logger

logger = get_logger(__name__)


class SoundEditor(BaseEditor):
    """Form editor for sound assets.

    Persisted shape on disk (see ``core/asset_manager.py``
    ``_create_asset_data``)::

        {
          "name": "<asset_name>",
          "asset_type": "sound",
          "file_path": "sounds/<file>",   # not editable here
          "volume": 1.0,
          "loop": False,
          "length": 1.23,                 # informational, preserved verbatim
          "imported": True, "created": "...", "modified": "..."
        }

    Only ``volume``/``loop`` are editable; everything else round-trips
    untouched. Re-importing the backing audio file is a separate toolbar
    action, not this editor's job.
    """

    def __init__(self, project_path: str = None, parent=None):
        super().__init__(project_path, parent)
        self._extra_fields: Dict[str, Any] = {}
        self._file_path = ''
        self._sound = None  # lazily-loaded pygame.mixer.Sound for preview
        self._setup_content()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_content(self):
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self.file_label = QLabel('')
        self.file_label.setWordWrap(True)
        form.addRow(self.tr("File:"), self.file_label)

        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0.0, 1.0)
        self.volume_spin.setSingleStep(0.05)
        self.volume_spin.setDecimals(2)
        self.volume_spin.valueChanged.connect(self._on_field_changed)
        form.addRow(self.tr("Volume:"), self.volume_spin)

        self.loop_check = QCheckBox(self.tr("Loop"))
        self.loop_check.toggled.connect(self._on_field_changed)
        form.addRow('', self.loop_check)

        layout.addLayout(form)

        preview_row = QHBoxLayout()
        self.play_button = QPushButton(self.tr("▶ Play"))
        self.play_button.clicked.connect(self._toggle_preview)
        preview_row.addWidget(self.play_button)
        preview_row.addStretch()
        layout.addLayout(preview_row)

        layout.addStretch()

    # ------------------------------------------------------------------
    # Preview playback
    # ------------------------------------------------------------------

    def _resolve_absolute_path(self) -> Path:
        if not self._file_path:
            return None
        if self.project_path:
            return Path(self.project_path) / self._file_path
        return Path(self._file_path)

    def _toggle_preview(self):
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            logger.debug(f"Audio preview unavailable: {e}")
            return

        import pygame

        if pygame.mixer.get_busy():
            pygame.mixer.stop()
            self.play_button.setText(self.tr("▶ Play"))
            return

        abs_path = self._resolve_absolute_path()
        if not abs_path or not abs_path.exists():
            logger.warning(f"Sound file not found for preview: {abs_path}")
            return

        try:
            self._sound = pygame.mixer.Sound(str(abs_path))
            self._sound.set_volume(self.volume_spin.value())
            self._sound.play()
            self.play_button.setText(self.tr("■ Stop"))
        except Exception as e:
            logger.warning(f"Could not play sound preview {abs_path}: {e}")

    # ------------------------------------------------------------------
    # BaseEditor contract
    # ------------------------------------------------------------------

    def load_data(self, data: Dict[str, Any]):
        data = data if isinstance(data, dict) else {}
        self._file_path = data.get('file_path', '')
        self.file_label.setText(self._file_path or self.tr("(no file)"))

        self.volume_spin.blockSignals(True)
        self.volume_spin.setValue(float(data.get('volume', 1.0) or 1.0))
        self.volume_spin.blockSignals(False)

        self.loop_check.blockSignals(True)
        self.loop_check.setChecked(bool(data.get('loop', False)))
        self.loop_check.blockSignals(False)

        self._extra_fields = {
            k: v for k, v in data.items()
            if k not in ('volume', 'loop', 'name', 'asset_type')
        }

    def get_data(self) -> Dict[str, Any]:
        out: Dict[str, Any] = dict(self._extra_fields)
        out['volume'] = self.volume_spin.value()
        out['loop'] = self.loop_check.isChecked()
        out['name'] = self.asset_name
        out['asset_type'] = 'sound'
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

    def closeEvent(self, event):
        try:
            import pygame
            if pygame.mixer.get_init() and pygame.mixer.get_busy():
                pygame.mixer.stop()
        except Exception:
            pass
        super().closeEvent(event)
