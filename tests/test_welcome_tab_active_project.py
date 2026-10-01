"""Welcome tab — the active project stays visible and closeable.

Two user-reported gaps:
1. "Clear recent projects" wiped Config's recent_projects list entirely, so
   if a project was actually open at the time, the Welcome tab's inline
   list fell back to "(No recent projects yet.)" even though a project was
   sitting open right behind the Welcome tab in the editor-tab strip. The
   currently-open project must always appear in the list, clear or no
   clear.
2. The Welcome tab had no way to close the open project and return the IDE
   to its empty state -- only File -> Close Project did (added 2026-06-26,
   see test_ide_polish_fixes.py's item 2). A "Close current project" button
   now lives in the Welcome tab's right column, visible only while a
   project is actually open.

Constructs a real offscreen QApplication (not pytest-qt), matching
tests/test_sample_docs_dialog.py's pattern so this runs anywhere PySide6 is
installed.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

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
def _clean_recent_config():
    """Isolate Config's recent_projects across tests (it's a class-level
    singleton dict, not per-instance state)."""
    from utils.config import Config
    before = dict(Config._config_data)
    yield
    Config._config_data = before


class _Stub:
    """Minimal main_window stand-in: just the attributes/methods the
    Welcome tab actually reads or calls, not a real IDE window."""

    def __init__(self, current_project_path=None):
        self.current_project_path = current_project_path
        self.close_project_calls = 0

    def tr(self, s):
        return s

    def close_project(self):
        self.close_project_calls += 1
        self.current_project_path = None


def _welcome_tab(_qapp, stub):
    from widgets.welcome_tab import WelcomeTab
    # WelcomeTab(parent) passes parent straight to QWidget.__init__, which
    # requires a real QWidget/None -- _Stub isn't one, so construct
    # parentless and attach the stub as main_window afterward, same shape
    # every other slot in this file already uses (main_window is read via
    # getattr/hasattr, never assumed to be an actual Qt parent).
    tab = WelcomeTab(None)
    tab.main_window = stub
    tab.refresh_recent_projects()
    return tab


def _row_label_texts(tab, row_index):
    from PySide6.QtWidgets import QLabel
    item = tab._recent_list.item(row_index)
    widget = tab._recent_list.itemWidget(item)
    return [child.text() for child in widget.findChildren(QLabel)]


class TestActiveProjectAlwaysListed:

    def test_active_project_shown_after_clearing_recent_list(self, _qapp, _clean_recent_config):
        from utils.config import Config

        Config.set("recent_projects", [])  # the "Clear recent projects" end-state
        stub = _Stub(current_project_path="/projects/my_game")
        tab = _welcome_tab(_qapp, stub)

        assert tab._recent_list.count() == 1
        from PySide6.QtCore import Qt
        item = tab._recent_list.item(0)
        assert item.data(Qt.UserRole) == "/projects/my_game"
        labels = _row_label_texts(tab, 0)
        assert "my_game" in labels
        assert "(current)" in labels

    def test_no_project_and_no_history_shows_placeholder(self, _qapp, _clean_recent_config):
        from utils.config import Config

        Config.set("recent_projects", [])
        stub = _Stub(current_project_path=None)
        tab = _welcome_tab(_qapp, stub)

        assert tab._recent_list.count() == 1
        assert tab._recent_list.item(0).text() == "(No recent projects yet.)"

    def test_active_project_not_duplicated_when_already_in_history(self, _qapp, _clean_recent_config):
        from utils.config import Config

        Config.set("recent_projects", ["/projects/my_game", "/projects/old_one"])
        stub = _Stub(current_project_path="/projects/my_game")
        tab = _welcome_tab(_qapp, stub)

        assert tab._recent_list.count() == 2
        from PySide6.QtCore import Qt
        paths = [tab._recent_list.item(i).data(Qt.UserRole) for i in range(2)]
        assert paths == ["/projects/my_game", "/projects/old_one"]
        assert "(current)" in _row_label_texts(tab, 0)
        assert "(current)" not in _row_label_texts(tab, 1)

    def test_active_project_prepended_when_not_in_history(self, _qapp, _clean_recent_config):
        from utils.config import Config

        Config.set("recent_projects", ["/projects/old_one"])
        stub = _Stub(current_project_path="/projects/my_game")
        tab = _welcome_tab(_qapp, stub)

        assert tab._recent_list.count() == 2
        from PySide6.QtCore import Qt
        paths = [tab._recent_list.item(i).data(Qt.UserRole) for i in range(2)]
        assert paths == ["/projects/my_game", "/projects/old_one"]

    def test_history_entry_not_tagged_current_when_no_project_open(self, _qapp, _clean_recent_config):
        from utils.config import Config

        Config.set("recent_projects", ["/projects/old_one"])
        stub = _Stub(current_project_path=None)
        tab = _welcome_tab(_qapp, stub)

        assert "(current)" not in _row_label_texts(tab, 0)


class TestCloseProjectButton:

    # QWidget.isVisible() reflects the whole ancestor chain, and this tab is
    # never actually shown on screen in these tests (no .show() call) -- it
    # would read False regardless of setVisible() here. isHidden() reflects
    # the widget's own explicit hidden flag independent of whether its
    # window is on screen, which is what these tests actually want to pin.

    def test_hidden_with_no_project_open(self, _qapp, _clean_recent_config):
        from utils.config import Config

        Config.set("recent_projects", [])
        stub = _Stub(current_project_path=None)
        tab = _welcome_tab(_qapp, stub)

        assert tab._close_project_btn.isHidden() is True

    def test_visible_with_a_project_open(self, _qapp, _clean_recent_config):
        from utils.config import Config

        Config.set("recent_projects", [])
        stub = _Stub(current_project_path="/projects/my_game")
        tab = _welcome_tab(_qapp, stub)

        assert tab._close_project_btn.isHidden() is False

    def test_clicking_closes_the_project_and_hides_the_button(self, _qapp, _clean_recent_config):
        from utils.config import Config

        Config.set("recent_projects", [])
        stub = _Stub(current_project_path="/projects/my_game")
        tab = _welcome_tab(_qapp, stub)
        assert tab._close_project_btn.isHidden() is False

        tab._close_project_btn.click()

        assert stub.close_project_calls == 1
        assert tab._close_project_btn.isHidden() is True
        # The list falls back to the empty-history placeholder once the
        # project is gone and there's no other history.
        assert tab._recent_list.item(0).text() == "(No recent projects yet.)"

    def test_main_window_without_close_project_is_a_noop(self, _qapp, _clean_recent_config):
        """A main_window that doesn't implement close_project (shouldn't
        happen in the real IDE, but the slot's hasattr guard must not
        raise) leaves the button click harmless."""
        from utils.config import Config

        class _NoCloseStub:
            def __init__(self):
                self.current_project_path = "/projects/my_game"

            def tr(self, s):
                return s

        Config.set("recent_projects", [])
        tab = _welcome_tab(_qapp, _NoCloseStub())
        tab._close_project_btn.click()  # must not raise
