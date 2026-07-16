#!/usr/bin/env python3
"""
Find / Find and Replace dialog — restores the Edit → Find... (Ctrl+F) and
Edit → Find and Replace... (Ctrl+H) menu entries removed in rc.11's
"stop lying to users" cleanup (commit 77e9dbf), which deleted the
"Not Implemented" placeholder stubs and tracked the real feature in
TODO.md instead.

Scope (deferred-items plan, Tier 2 item 5): the code editor
(``editors/script_editor.py``'s ``QPlainTextEdit``) only, for this first
pass. Room editor scripts / event scripts (execute_code action dialogs)
are a separate widget (``QTextEdit`` inside
``editors/object_editor/gm80_action_dialog.py``) not wired to this dialog
yet — tracked as a follow-up in TODO.md rather than silently expanded
into scope this pass didn't budget for.
"""

from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import (QCheckBox, QDialog, QFormLayout, QHBoxLayout,
                                QLabel, QLineEdit, QPushButton, QVBoxLayout)


class FindReplaceDialog(QDialog):
    """Non-modal find/replace bar for a single QPlainTextEdit/QTextEdit
    target, rebound each time it's shown (see ide_window.py's
    ``_show_find_dialog``) so switching editor tabs and reopening always
    searches the currently active one."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Find"))
        self.setModal(False)
        self._target = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.find_field = QLineEdit()
        self.find_field.returnPressed.connect(self.find_next)
        form.addRow(self.tr("Find:"), self.find_field)

        self.replace_label = QLabel(self.tr("Replace:"))
        self.replace_field = QLineEdit()
        form.addRow(self.replace_label, self.replace_field)
        layout.addLayout(form)

        options_row = QHBoxLayout()
        self.case_checkbox = QCheckBox(self.tr("Case sensitive"))
        self.whole_word_checkbox = QCheckBox(self.tr("Whole words"))
        options_row.addWidget(self.case_checkbox)
        options_row.addWidget(self.whole_word_checkbox)
        options_row.addStretch(1)
        layout.addLayout(options_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)

        button_row = QHBoxLayout()
        self.find_next_button = QPushButton(self.tr("Find Next"))
        self.find_next_button.clicked.connect(self.find_next)
        self.find_prev_button = QPushButton(self.tr("Find Previous"))
        self.find_prev_button.clicked.connect(self.find_previous)
        self.replace_button = QPushButton(self.tr("Replace"))
        self.replace_button.clicked.connect(self.replace_current)
        self.replace_all_button = QPushButton(self.tr("Replace All"))
        self.replace_all_button.clicked.connect(self.replace_all)
        close_button = QPushButton(self.tr("Close"))
        close_button.clicked.connect(self.close)

        for button in (self.find_next_button, self.find_prev_button,
                       self.replace_button, self.replace_all_button, close_button):
            button_row.addWidget(button)
        layout.addLayout(button_row)

    # ------------------------------------------------------------------
    # Binding
    # ------------------------------------------------------------------

    def set_target(self, text_edit):
        """Bind the QPlainTextEdit/QTextEdit this dialog searches/replaces
        in. Safe to call repeatedly (e.g. re-showing the dialog after the
        user switched editor tabs)."""
        self._target = text_edit
        self.status_label.setText("")

    def set_replace_visible(self, visible: bool):
        self.replace_label.setVisible(visible)
        self.replace_field.setVisible(visible)
        self.replace_button.setVisible(visible)
        self.replace_all_button.setVisible(visible)
        self.setWindowTitle(self.tr("Find and Replace") if visible else self.tr("Find"))

    # ------------------------------------------------------------------
    # Search / replace
    # ------------------------------------------------------------------

    def _find_flags(self, backward=False):
        flags = QTextDocument.FindFlags()
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self.whole_word_checkbox.isChecked():
            flags |= QTextDocument.FindWholeWords
        if backward:
            flags |= QTextDocument.FindBackward
        return flags

    def _search(self, backward=False):
        if self._target is None:
            return False
        text = self.find_field.text()
        if not text:
            return False
        found = self._target.find(text, self._find_flags(backward))
        if not found:
            # Wrap around: jump to the start (or end, searching backward)
            # and retry once before reporting "not found".
            cursor = self._target.textCursor()
            cursor.movePosition(QTextCursor.End if backward else QTextCursor.Start)
            self._target.setTextCursor(cursor)
            found = self._target.find(text, self._find_flags(backward))
        self.status_label.setText("" if found else self.tr("Phrase not found"))
        return found

    def find_next(self):
        return self._search(backward=False)

    def find_previous(self):
        return self._search(backward=True)

    def _selection_matches_search(self):
        cursor = self._target.textCursor()
        selected = cursor.selectedText()
        if not selected:
            return False
        needle = self.find_field.text()
        if self.case_checkbox.isChecked():
            return selected == needle
        return selected.lower() == needle.lower()

    def replace_current(self):
        """Replace the current selection if it's a live search match, then
        advance to the next one — matching the conventional find/replace
        flow of Find (or Find Next) selecting a match before Replace acts
        on it."""
        if self._target is None:
            return
        if self._selection_matches_search():
            cursor = self._target.textCursor()
            cursor.insertText(self.replace_field.text())
        self.find_next()

    def replace_all(self):
        if self._target is None:
            return
        text = self.find_field.text()
        if not text:
            return
        replacement = self.replace_field.text()

        cursor = self._target.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self._target.setTextCursor(cursor)

        group_cursor = self._target.textCursor()
        group_cursor.beginEditBlock()
        count = 0
        try:
            # The standard Qt idiom: find() moves/selects on the widget's
            # live cursor, and inserting through a fresh copy of it
            # advances past the replacement text before the next find() —
            # so a replacement that itself contains the search text (e.g.
            # "cat" -> "cats cat") can't loop forever re-matching what it
            # just inserted.
            while self._target.find(text, self._find_flags(backward=False)):
                found_cursor = self._target.textCursor()
                found_cursor.insertText(replacement)
                count += 1
        finally:
            group_cursor.endEditBlock()
        self.status_label.setText(self.tr("%d replacement(s) made") % count)
