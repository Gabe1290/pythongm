"""Regression test: ObjectEventsPanel's Copy/Paste QShortcuts (Ctrl+C/Ctrl+V)
used the QShortcut default context (WindowShortcut), which is window-wide --
identical in scope to core/ide/_menu_builder.py's own Edit menu Copy ("Ctrl+C")
and Paste ("Ctrl+V") actions. With both active in the same top-level window
(true the instant an object editor is open), Qt can't resolve which handler a
keypress should go to.

Real classroom report, 2026-10-11: "Qt Warning: QAction::event: Ambiguous
shortcut overload: Ctrl+C" printed to the terminal of a compiled build.
Fixed by scoping both QShortcuts to WidgetWithChildrenShortcut, so they only
fire while this panel (or a descendant) has focus, instead of competing with
the menu's window-wide bindings.
"""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def panel(_qapp):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from editors.object_editor.events._panel import ObjectEventsPanel
    p = ObjectEventsPanel()
    p.setup_shortcuts()  # normally deferred via QTimer.singleShot(0, ...)
    return p


def test_copy_shortcut_is_scoped_to_the_widget(panel):
    from PySide6.QtCore import Qt
    assert panel.copy_action_shortcut.context() == Qt.ShortcutContext.WidgetWithChildrenShortcut


def test_paste_shortcut_is_scoped_to_the_widget(panel):
    from PySide6.QtCore import Qt
    assert panel.paste_action_shortcut.context() == Qt.ShortcutContext.WidgetWithChildrenShortcut


def test_copy_and_paste_shortcuts_are_still_ctrl_c_and_ctrl_v(panel):
    """The fix only narrows WHERE these fire, not WHAT key combo triggers
    them -- confirms the scoping change didn't silently change the shortcut
    itself."""
    from PySide6.QtGui import QKeySequence
    assert panel.copy_action_shortcut.key() == QKeySequence(QKeySequence.StandardKey.Copy)
    assert panel.paste_action_shortcut.key() == QKeySequence(QKeySequence.StandardKey.Paste)


def test_move_up_down_shortcuts_unaffected(panel):
    """Ctrl+Up/Ctrl+Down have no window-wide equivalent anywhere else in the
    app, so this fix deliberately left them at the QShortcut default --
    pins that they still work at all after editing this method."""
    from PySide6.QtCore import Qt
    assert panel.move_up_shortcut.context() == Qt.ShortcutContext.WindowShortcut
    assert panel.move_down_shortcut.context() == Qt.ShortcutContext.WindowShortcut


def test_main_menu_still_binds_window_wide_copy_and_paste():
    """Confirms the OTHER half of the collision this fix resolves still
    exists as window-wide (so the scoping fix is actually doing something,
    not just narrowing a shortcut that had nothing to collide with)."""
    source = (Path(__file__).resolve().parent.parent / "core" / "ide" / "_menu_builder.py").read_text(encoding="utf-8")
    assert 'self.create_action(self.tr("&Copy"), "Ctrl+C", self.copy)' in source
    assert 'self.create_action(self.tr("&Paste"), "Ctrl+V", self.paste)' in source
