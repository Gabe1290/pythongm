"""Several LanguageChange events in a row leave exactly one main toolbar, with live actions.

Reported 2026-11-22 (French IDE, raycast_5 open): a greyed Test Game / Debug / Export group sat next
to the working one. At startup main.py sends LanguageChange to every widget, and each one rebuilds
the menus (new QActions) and the toolbar. The old toolbar was only deleteLater()'d, so the next
rebuild's findChild found the already-removed one, left the live toolbar in place, and added a
second -- whose actions were the previous menus', disabled before any project opened and never
updated again. Real offscreen QApplication, no pytest-qt.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6


def test_repeated_language_changes_leave_one_live_toolbar():
    from PySide6.QtCore import QEvent
    from PySide6.QtWidgets import QApplication, QToolBar
    app = QApplication.instance() or QApplication([])
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    try:
        ide.show()
        app.processEvents()
        for _ in range(3):                       # no event loop in between, as at startup
            app.sendEvent(ide, QEvent(QEvent.Type.LanguageChange))
        app.processEvents()
        ide.load_project(str(ROOT / "samples" / "maze_1"))
        app.processEvents()

        toolbars = [t for t in ide.findChildren(QToolBar)
                    if t.objectName() == "MainToolbar" and t.isVisible()]
        assert len(toolbars) == 1
        test_buttons = [a for a in toolbars[0].actions() if a is ide.test_game_action]
        assert len(test_buttons) == 1 and test_buttons[0].isEnabled()
        stale = [a for a in toolbars[0].actions() if not a.isSeparator() and "Test" in a.text()
                 and a is not ide.test_game_action]
        assert not stale
    finally:
        ide.close()
        ide.deleteLater()
        app.processEvents()
