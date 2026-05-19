#!/usr/bin/env python3
"""
Shared Float/Attach toolbar behaviour for detachable editors.

`BaseEditor`, `RoomEditor` and `PlaygroundEditor` each carried a byte-identical
copy of the `float_requested`/`reattach_requested` signals plus
`_on_float_clicked`/`set_floating_state` (a recent feature flagged as
drift-prone in the code audit). They are independent `QWidget` subclasses, so
this is provided as a mixin rather than a common base.

Concrete classes must be QWidget/QObject subclasses that create a
`self.float_action` toolbar action wired to `self._on_float_clicked` and a
`self._is_floating` flag (see the editors' `setup_ui`).

Translation note: PySide6 `QObject.tr()` resolves its context from the
*concrete* runtime class even for `tr()` calls inherited from a mixin
(empirically verified), so the existing per-editor .qm contexts keep working
unchanged.
"""

from PySide6.QtCore import Signal


class FloatableEditorMixin:
    """Mixin: Float/Attach toolbar button + IDE detach/reattach signals."""

    float_requested = Signal(object)     # the editor itself — IDE handles detach
    reattach_requested = Signal(object)  # editor asks IDE to put it back in a tab

    def _on_float_clicked(self):
        """Toolbar Float/Attach button — IDE handles the actual reparent."""
        if self._is_floating:
            self.reattach_requested.emit(self)
        else:
            self.float_requested.emit(self)

    def set_floating_state(self, is_floating: bool):
        """Called by the IDE after a successful float/attach so the toolbar
        button reflects the current state."""
        self._is_floating = bool(is_floating)
        if not hasattr(self, 'float_action'):
            return
        if self._is_floating:
            self.float_action.setText(self.tr("📥 Attach"))
            self.float_action.setToolTip(self.tr("Return this editor to the IDE's tab strip"))
        else:
            self.float_action.setText(self.tr("🪟 Float"))
            self.float_action.setToolTip(self.tr("Open this editor in its own window"))
