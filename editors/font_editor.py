#!/usr/bin/env python3
"""
Font Editor — minimal editable editor for the ``fonts`` asset type.

Unlike sounds/backgrounds, a font asset here is a *system font
reference* (family name + size + style), not an imported file — see
``core/asset_manager.py`` ``create_asset`` for the default template. So
this editor has no file path, no preview image, no re-import action:
just the four fields that make up the reference, plus a live sample
label so "does this look right" has an answer without leaving the tab.

Closes the TODO.md "Generic asset-type editor fallback" item for the
``fonts`` asset type. Note: as of this writing, the runtime's
``set_draw_font`` action stores the chosen font *asset name* on the
instance but nothing in ``runtime/game_runner.py`` reads it back to
actually change how ``draw_text`` renders — the font asset's fields
(``font_name``/``size``/``bold``/``italic``) aren't consumed by
rendering yet. This editor still exists to close the "no editor at all,
warns and does nothing" gap TODO.md asks for; wiring the fields into
draw_text rendering is a separate, larger runtime task (see the
corresponding new TODO.md entry).
"""

from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout,
)

from editors.base_editor import BaseEditor
from core.logger import get_logger

logger = get_logger(__name__)


class FontEditor(BaseEditor):
    """Form editor for font assets.

    Persisted shape on disk (see ``core/asset_manager.py``
    ``create_asset``)::

        {
          "name": "<asset_name>",
          "asset_type": "font",
          "font_name": "Arial",
          "size": 12,
          "bold": False,
          "italic": False,
          "charset": "ascii"        # preserved verbatim, not exposed here
        }
    """

    def __init__(self, project_path: str = None, parent=None):
        super().__init__(project_path, parent)
        self._extra_fields: Dict[str, Any] = {}
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

        self.family_edit = QLineEdit()
        self.family_edit.textChanged.connect(self._on_field_changed)
        form.addRow(self.tr("Font family:"), self.family_edit)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(4, 200)
        self.size_spin.valueChanged.connect(self._on_field_changed)
        form.addRow(self.tr("Size:"), self.size_spin)

        self.bold_check = QCheckBox(self.tr("Bold"))
        self.bold_check.toggled.connect(self._on_field_changed)
        form.addRow('', self.bold_check)

        self.italic_check = QCheckBox(self.tr("Italic"))
        self.italic_check.toggled.connect(self._on_field_changed)
        form.addRow('', self.italic_check)

        layout.addLayout(form)

        self.sample_label = QLabel(self.tr("The quick brown fox"))
        self.sample_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sample_label.setMinimumHeight(64)
        self.sample_label.setStyleSheet(
            "QLabel { border: 1px solid palette(mid); background: palette(base); }")
        layout.addWidget(self.sample_label)

        self.family_edit.textChanged.connect(self._update_sample)
        self.size_spin.valueChanged.connect(self._update_sample)
        self.bold_check.toggled.connect(self._update_sample)
        self.italic_check.toggled.connect(self._update_sample)

        layout.addStretch()

    def _update_sample(self, *_args):
        from PySide6.QtGui import QFont
        family = self.family_edit.text().strip() or "Arial"
        font = QFont(family, self.size_spin.value())
        font.setBold(self.bold_check.isChecked())
        font.setItalic(self.italic_check.isChecked())
        self.sample_label.setFont(font)

    # ------------------------------------------------------------------
    # BaseEditor contract
    # ------------------------------------------------------------------

    def load_data(self, data: Dict[str, Any]):
        data = data if isinstance(data, dict) else {}

        self.family_edit.blockSignals(True)
        self.family_edit.setText(data.get('font_name', 'Arial') or 'Arial')
        self.family_edit.blockSignals(False)

        self.size_spin.blockSignals(True)
        self.size_spin.setValue(int(data.get('size', 12) or 12))
        self.size_spin.blockSignals(False)

        self.bold_check.blockSignals(True)
        self.bold_check.setChecked(bool(data.get('bold', False)))
        self.bold_check.blockSignals(False)

        self.italic_check.blockSignals(True)
        self.italic_check.setChecked(bool(data.get('italic', False)))
        self.italic_check.blockSignals(False)

        self._extra_fields = {
            k: v for k, v in data.items()
            if k not in ('font_name', 'size', 'bold', 'italic', 'name', 'asset_type')
        }

        self._update_sample()

    def get_data(self) -> Dict[str, Any]:
        out: Dict[str, Any] = dict(self._extra_fields)
        out['font_name'] = self.family_edit.text().strip() or 'Arial'
        out['size'] = self.size_spin.value()
        out['bold'] = self.bold_check.isChecked()
        out['italic'] = self.italic_check.isChecked()
        out.setdefault('charset', 'ascii')
        out['name'] = self.asset_name
        out['asset_type'] = 'font'
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
