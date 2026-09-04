#!/usr/bin/env python3
"""Edit-menu actions for :class:`PyGameMakerIDE`.

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2). A mixin -- ``self`` / ``self.tr()`` / siblings (``open_editors``,
``editor_tabs``, ``welcome_tab``, ``status_bar``, ``focusWidget`` …) resolve
on the concrete window. No ``mock.patch("core.ide_window.<NAME>")`` site
exercises any of these (``test_find_replace.py`` calls them unbound on the
class with a stub ``self``), so no patch target moved.
"""

from core.logger import get_logger

logger = get_logger(__name__)


class EditActionsMixin:

    def _active_editor(self):
        """Return the editor the user is interacting with right now.

        Prefers the currently focused widget's owning editor (which works
        for detached editor windows), falling back to the active tab's
        widget. Returns None if no editor is in focus or the active tab
        is the welcome tab.
        """
        from PySide6.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused is not None:
            open_set = set(self.open_editors.values())
            walk = focused
            while walk is not None:
                if walk in open_set:
                    return walk
                walk = walk.parent()
        current = self.editor_tabs.currentWidget()
        if current is None or current is self.welcome_tab:
            return None
        return current

    def undo(self):
        """Handle undo - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is None:
            logger.debug("Undo (no editor-specific undo available)")
            return
        if hasattr(editor, 'undo'):
            try:
                editor.undo()
            except Exception:
                logger.debug("Undo: editor.undo() raised", exc_info=True)

    def redo(self):
        """Handle redo - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is None:
            logger.debug("Redo (no editor-specific redo available)")
            return
        if hasattr(editor, 'redo'):
            try:
                editor.redo()
            except Exception:
                logger.debug("Redo: editor.redo() raised", exc_info=True)

    def cut(self):
        """Handle cut - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is not None:
            if editor.__class__.__name__ == 'RoomEditor' and hasattr(editor, 'cut_instance'):
                editor.cut_instance()
                return
            if hasattr(editor, 'cut'):
                try:
                    editor.cut()
                    return
                except Exception:
                    logger.debug("Cut: editor.cut() raised", exc_info=True)
        # Fall back to the focused widget for plain text-edit cut
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'cut'):
            try:
                focused_widget.cut()
            except Exception:
                logger.debug("Cut: focusWidget().cut() raised", exc_info=True)

    def copy(self):
        """Handle copy - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is not None:
            if editor.__class__.__name__ == 'RoomEditor' and hasattr(editor, 'copy_instance'):
                editor.copy_instance()
                return
            if hasattr(editor, 'copy'):
                try:
                    editor.copy()
                    return
                except Exception:
                    logger.debug("Copy: editor.copy() raised", exc_info=True)
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'copy'):
            try:
                focused_widget.copy()
            except Exception:
                logger.debug("Copy: focusWidget().copy() raised", exc_info=True)

    def paste(self):
        """Handle paste - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is not None:
            if editor.__class__.__name__ == 'RoomEditor' and hasattr(editor, 'paste_instance'):
                editor.paste_instance()
                return
            if hasattr(editor, 'paste'):
                try:
                    editor.paste()
                    return
                except Exception:
                    logger.debug("Paste: editor.paste() raised", exc_info=True)
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'paste'):
            try:
                focused_widget.paste()
            except Exception:
                logger.debug("Paste: focusWidget().paste() raised", exc_info=True)

    def duplicate(self):
        """Handle duplicate - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is not None and editor.__class__.__name__ == 'RoomEditor':
            if hasattr(editor, 'duplicate_instance'):
                editor.duplicate_instance()
                return
        logger.debug("Duplicate action (no room editor active)")

    def _find_target_text_edit(self):
        """The text-edit widget Find/Replace searches — currently the
        Script Editor's code_edit (a QPlainTextEdit) only. Room editor
        scripts / event scripts (execute_code action dialogs, a separate
        QTextEdit inside gm80_action_dialog.py) aren't wired in yet; see
        TODO.md's Find/Replace entry."""
        editor = self._active_editor()
        if editor is not None and hasattr(editor, 'code_edit'):
            return editor.code_edit
        return None

    def _show_find_dialog(self, show_replace: bool):
        target = self._find_target_text_edit()
        if target is None:
            self.status_bar.showMessage(
                self.tr("Find is only available in the code editor"), 3000)
            return
        if getattr(self, '_find_dialog', None) is None:
            from dialogs.find_replace_dialog import FindReplaceDialog
            self._find_dialog = FindReplaceDialog(self)
        self._find_dialog.set_target(target)
        self._find_dialog.set_replace_visible(show_replace)
        self._find_dialog.show()
        self._find_dialog.raise_()
        self._find_dialog.activateWindow()
        self._find_dialog.find_field.setFocus()
        self._find_dialog.find_field.selectAll()

    def find(self):
        """Edit → Find... (Ctrl+F)."""
        self._show_find_dialog(show_replace=False)

    def find_replace(self):
        """Edit → Find and Replace... (Ctrl+H)."""
        self._show_find_dialog(show_replace=True)
