#!/usr/bin/env python3
"""
Floating window host for editors. Lets the IDE pop a BaseEditor (Object,
Sprite, etc.) out of the tab strip into its own movable window so users can
view two assets side-by-side. Closing the window re-attaches the editor.
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget


class DetachedEditorWindow(QMainWindow):
    """QMainWindow that hosts a single editor widget.

    The IDE creates one of these when the user clicks Float on an editor's
    toolbar. Closing the window emits ``reattach_requested`` so the IDE can
    move the editor back into a tab. For hard-close paths (the editor itself
    asks to close after a save prompt), the IDE sets ``reattach_on_close``
    to False before closing the window.
    """

    reattach_requested = Signal(object)  # emits the inner editor widget

    def __init__(self, editor: QWidget, parent=None):
        super().__init__(parent)

        self._editor = editor
        self.reattach_on_close = True

        # Title tracks the editor; BaseEditor.update_window_title sets it
        # to "asset_name [● *]" with modification markers, which is exactly
        # what we want to show in the window's title bar.
        title = editor.windowTitle() or getattr(editor, "asset_name", None) or "Editor"
        self.setWindowTitle(title)
        try:
            editor.windowTitleChanged.connect(self.setWindowTitle)
        except (AttributeError, RuntimeError):
            # AttributeError: editor isn't a proper QWidget subclass and
            # has no windowTitleChanged signal. RuntimeError: the editor
            # has already been deleted by Qt before we get here.
            pass

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # QTabWidget.removeTab hides the page widget without reparenting it,
        # so the editor arrives here parented to the old tab widget and with
        # visibility=False. Reparent explicitly and force-show before adding,
        # otherwise the floating window comes up blank.
        editor.setParent(None)
        editor.show()
        layout.addWidget(editor)
        self.setCentralWidget(container)

        self.resize(950, 720)

    def take_editor(self) -> Optional[QWidget]:
        """Detach the inner editor so the IDE can re-parent it back to a tab."""
        editor = self._editor
        if editor is None:
            return None
        try:
            editor.windowTitleChanged.disconnect(self.setWindowTitle)
        except (TypeError, RuntimeError, AttributeError):
            # TypeError: signal was never connected. RuntimeError: the
            # underlying Qt object has already been deleted. AttributeError:
            # editor doesn't have the signal (non-QWidget host).
            pass
        # Remove the editor from this window's central layout. setParent(None)
        # is the cleanest reparent step before the IDE adds it to a QTabWidget.
        editor.setParent(None)
        self._editor = None
        return editor

    def closeEvent(self, event: QCloseEvent):
        """User clicked X (or window was closed). Re-attach by default."""
        if self.reattach_on_close and self._editor is not None:
            self.reattach_requested.emit(self._editor)
        event.accept()
