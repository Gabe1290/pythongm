#!/usr/bin/env python3
"""
Find in Project — TODO.md's "project-wide search (asset names,
identifiers)" item, logged separately when Find/Replace (a single text
editor's own search) shipped 2026-10-18.

Non-modal, rebound each time it's shown (core/ide/_edit_actions.py's
find_in_project, mirroring FindReplaceDialog's own set_target/show
pattern), so switching projects and reopening always searches the
currently loaded one. The actual search is utils/project_search.
search_project -- this dialog is purely the UI: a search field, a
debounced live results list, and double-click-to-open.
"""
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QCheckBox, QDialog, QHBoxLayout, QLabel,
                                QLineEdit, QTreeWidget, QTreeWidgetItem,
                                QVBoxLayout)

from utils.project_search import search_project

# Debounce: a full project re-walk on every keystroke is wasteful for a
# larger project. 250ms is short enough to still feel live.
_SEARCH_DEBOUNCE_MS = 250

_KIND_LABELS = {
    "asset_name": "Asset",
    "object_field": "Object field",
    "action_name": "Action",
    "action_param": "Parameter",
    "room_field": "Room field",
    "script_code": "Script",
}


class ProjectSearchDialog(QDialog):
    """Search every asset name, object field, action parameter, room
    field, and script body in the current project for a substring match.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Find in Project"))
        self.setModal(False)
        self.resize(640, 420)
        self._project_data = None
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._run_search)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel(self.tr("Find:")))
        self.search_field = QLineEdit()
        self.search_field.textChanged.connect(self._on_text_changed)
        self.search_field.returnPressed.connect(self._run_search)
        search_row.addWidget(self.search_field)
        self.case_checkbox = QCheckBox(self.tr("Case sensitive"))
        self.case_checkbox.toggled.connect(self._on_text_changed)
        search_row.addWidget(self.case_checkbox)
        layout.addLayout(search_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)

        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(
            [self.tr("Type"), self.tr("Location"), self.tr("Match")])
        self.results_tree.setRootIsDecorated(False)
        self.results_tree.setUniformRowHeights(True)
        self.results_tree.itemDoubleClicked.connect(self._on_result_double_clicked)
        layout.addWidget(self.results_tree)

        hint_label = QLabel(self.tr(
            "Double-click a result to open it. A reference built up at "
            "runtime (string concatenation, a variable) inside "
            "execute_code/execute_script can't be found this way — only "
            "literal text."))
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: #888;")
        layout.addWidget(hint_label)

    # ------------------------------------------------------------------
    # Binding
    # ------------------------------------------------------------------

    def set_project_data(self, project_data: dict):
        """Bind the project this dialog searches. Safe to call repeatedly
        (e.g. re-showing the dialog after the user switched/reloaded the
        project) — re-runs the current search against the new data
        immediately so a stale result list is never shown next to the
        wrong project."""
        self._project_data = project_data
        if self.search_field.text().strip():
            self._run_search()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _on_text_changed(self, *_args):
        self._debounce_timer.start(_SEARCH_DEBOUNCE_MS)

    def _run_search(self):
        self._debounce_timer.stop()
        self.results_tree.clear()
        query = self.search_field.text().strip()
        if not query:
            self.status_label.setText("")
            return
        if self._project_data is None:
            self.status_label.setText(self.tr("No project open"))
            return

        results = search_project(
            self._project_data, query, case_sensitive=self.case_checkbox.isChecked())

        for result in results:
            item = QTreeWidgetItem([
                self.tr(_KIND_LABELS.get(result.kind, result.kind)),
                result.location,
                result.matched_text,
            ])
            item.setData(0, Qt.UserRole, (result.category, result.name))
            self.results_tree.addTopLevelItem(item)

        if results:
            # %d, not Qt's %n plural form -- this app's established
            # convention (see FindReplaceDialog's own "%d replacement(s)
            # made"), not Qt's plural-aware tr(), which nothing else here
            # uses either.
            self.status_label.setText(self.tr("%d result(s)") % len(results))
        else:
            self.status_label.setText(self.tr("No results"))

    # ------------------------------------------------------------------
    # Opening a result
    # ------------------------------------------------------------------

    def _on_result_double_clicked(self, item: QTreeWidgetItem, _column: int):
        category, name = item.data(0, Qt.UserRole)
        ide = self.parent()
        if ide is None or self._project_data is None:
            return
        assets = self._project_data.get("assets") or {}
        asset_data = (assets.get(category) or {}).get(name)
        if asset_data is None:
            self.status_label.setText(
                self.tr("'{0}' no longer exists — try searching again").format(name))
            return
        if hasattr(ide, "on_asset_double_clicked"):
            ide.on_asset_double_clicked({
                "asset_type": category,
                "name": name,
                "data": asset_data,
            })
