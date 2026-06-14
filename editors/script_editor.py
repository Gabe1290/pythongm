#!/usr/bin/env python3
"""
Script Editor — minimal editable editor for ``scripts`` asset type.

Hosts a single QPlainTextEdit (monospace font, basic tab-stop tuning)
backed by the same BaseEditor save/dirty/undo plumbing as the other
editors. Round-trips the script's ``code`` field through the project's
scripts dict; preserves ``language`` and any other unknown keys so a
future syntax-highlighting layer or alternate language backend can be
added without losing data already on disk.

Closes the TODO.md "Generic asset-type editor fallback" item for the
``scripts`` asset type. See ``editors/object_editor`` for the existing
in-object Python code path — this editor is separate because GameMaker
scripts are project-level callables shared across multiple objects,
not the inline behaviour code attached to a single object's events.
"""

from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout

from editors.base_editor import BaseEditor
from core.logger import get_logger

logger = get_logger(__name__)


class ScriptEditor(BaseEditor):
    """Plain-text editor for project-level scripts (e.g. ``adapt_direction``).

    The script's persisted shape on disk is::

        {
          "name": "<asset_name>",
          "asset_type": "script",
          "code": "<source string>",
          "language": "python",       # informational; preserved verbatim
          "imported": True,
          "created": "...",
          "modified": "..."
        }

    Only ``code`` is editable through this surface; the rest round-trips
    untouched. Validation is intentionally permissive — incomplete or
    syntactically-broken Python is still saved (the runtime is where
    syntax errors get reported, not the editor), so the user doesn't
    lose work mid-edit.
    """

    def __init__(self, project_path: str = None, parent=None):
        super().__init__(project_path, parent)

        # Holds keys other than `code` from load_data so they're preserved
        # on save (`language`, `imported`, `created`, `modified`, etc.).
        self._extra_fields: Dict[str, Any] = {}

        self._setup_content()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_content(self):
        """Populate self.content_widget (provided by BaseEditor) with the
        QPlainTextEdit. Monospace font + 4-space tab stops keep the
        editor readable for the kind of short scripts the IDE actually
        ships with (cf. treasure/adapt_direction.py).
        """
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        self.code_edit = QPlainTextEdit()

        # Monospace font for code, falling back gracefully if the
        # platform doesn't have Consolas / Menlo / DejaVu Sans Mono.
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(max(font.pointSize(), 10))
        self.code_edit.setFont(font)

        # Tab inserts spaces (Python convention). Tab width = 4 chars
        # measured in the current font's space width.
        metrics = QFontMetrics(font)
        self.code_edit.setTabStopDistance(4 * metrics.horizontalAdvance(' '))

        # Plain-text editor (no rich-text drag/drop, no auto-replace);
        # scripts are source code, not formatted text.
        self.code_edit.setLineWrapMode(QPlainTextEdit.NoWrap)

        # textChanged fires on any edit; route through the standard
        # BaseEditor data_modified signal so dirty-state, auto-save,
        # and undo all work for free.
        self.code_edit.textChanged.connect(self._on_text_changed)

        layout.addWidget(self.code_edit)

        self._wire_document_undo()

    def undo(self):
        """Undo via the QPlainTextEdit document (the IDE Edit > Undo delegates
        here; BaseEditor.undo would no-op on the empty undo_stack) (L14)."""
        self.code_edit.undo()

    def redo(self):
        """Redo via the QPlainTextEdit document (L14)."""
        self.code_edit.redo()

    def _wire_document_undo(self):
        # Editing happens in the QPlainTextEdit's own QTextDocument, not the
        # BaseEditor undo_stack (which stays empty here), so the toolbar
        # Undo/Redo buttons and the IDE Edit menu were permanently dead even
        # though typing was undoable via Ctrl+Z. Wire both to the document's
        # undo history and reflect its availability (L14).
        if getattr(self, 'undo_action', None) is not None:
            try:
                self.undo_action.triggered.disconnect()
                self.redo_action.triggered.disconnect()
            except (RuntimeError, TypeError):
                pass
            self.undo_action.triggered.connect(self.code_edit.undo)
            self.redo_action.triggered.connect(self.code_edit.redo)
            doc = self.code_edit.document()
            doc.undoAvailable.connect(self.undo_action.setEnabled)
            doc.redoAvailable.connect(self.redo_action.setEnabled)

    # ------------------------------------------------------------------
    # BaseEditor contract
    # ------------------------------------------------------------------

    def load_data(self, data: Dict[str, Any]):
        """Populate the editor from an asset-data dict."""
        code = data.get('code', '') if isinstance(data, dict) else ''
        # blockSignals so the programmatic setPlainText doesn't fire
        # textChanged → data_modified, which would mark the editor dirty
        # immediately after loading a clean asset.
        self.code_edit.blockSignals(True)
        try:
            self.code_edit.setPlainText(code)
        finally:
            self.code_edit.blockSignals(False)

        # Preserve everything else on the asset so save() round-trips.
        self._extra_fields = {
            k: v for k, v in (data or {}).items()
            if k not in ('code', 'name', 'asset_type')
        }

    def get_data(self) -> Dict[str, Any]:
        """Build the asset-data dict to persist."""
        out: Dict[str, Any] = dict(self._extra_fields)
        out['code'] = self.code_edit.toPlainText()
        # 'language' defaults to python if the loaded asset didn't carry one.
        out.setdefault('language', 'python')
        out['name'] = self.asset_name
        out['asset_type'] = 'script'
        return out

    def validate_data(self) -> tuple[bool, str]:
        """Always permissive: half-typed Python is still saveable. The
        runtime surfaces actual syntax errors when the script executes.
        """
        return True, ""

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_text_changed(self):
        if self._saving:
            return  # ignore textChanged emitted during save round-trip
        if not self.is_modified:
            self.is_modified = True
            self.save_action.setEnabled(True)
            self.update_window_title()
            if hasattr(self, 'status_widget'):
                self.status_widget.set_modified(True, self.auto_save_enabled)
        self.data_modified.emit(self.asset_name or '')
