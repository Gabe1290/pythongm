"""The Preferences dialog must never be taller than 75% of the IDE window;
long tabs scroll instead."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    yield QApplication.instance() or QApplication([])


@pytest.mark.parametrize("window_height", [600, 800, 1000])
def test_dialog_height_capped_at_75_percent_of_window(_qapp, window_height):
    from PySide6.QtWidgets import QWidget
    from dialogs.preferences_dialog import PreferencesDialog
    window = QWidget()
    window.resize(1200, window_height)
    dialog = PreferencesDialog(window)
    try:
        cap = int(window_height * 0.75)
        assert dialog.maximumHeight() == cap
        assert dialog.height() <= cap
        dialog.show()
        assert dialog.height() <= cap
    finally:
        dialog.close()
        window.deleteLater()


def test_every_tab_page_is_scrollable(_qapp):
    from PySide6.QtWidgets import QScrollArea
    from dialogs.preferences_dialog import PreferencesDialog
    dialog = PreferencesDialog()
    try:
        assert dialog.tabs.count() >= 5
        for i in range(dialog.tabs.count()):
            assert isinstance(dialog.tabs.widget(i), QScrollArea)
    finally:
        dialog.close()
