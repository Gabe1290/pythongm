"""Regression tests for closing the Welcome tab in a translated UI.

Audit H1 (docs/FULL_AUDIT_2026-06-11.md): close_editor_tab guarded the
Welcome tab by comparing the tab text against the English literal
"Welcome", but the tab is titled self.tr("Welcome") — in a French UI
("Bienvenue") the guard failed, the welcome tab was deleteLater()'d, and
every later addTab(self.welcome_tab) (project load, last-tab close,
float) raised RuntimeError on the dead C++ wrapper.

The guard is now by widget identity, and _add_welcome_tab suppresses the
tab's close button. These tests run the real unbound IDE methods on a
lightweight stub whose tr() simulates the French translation, following
the test_game_subprocess_supervision.py pattern (standing up the full IDE
window is heavy).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _make_stub(qapp):
    from PySide6.QtWidgets import QTabWidget, QWidget

    class _IDEStub:
        def __init__(self):
            self.editor_tabs = QTabWidget()
            self.editor_tabs.setTabsClosable(True)
            self.welcome_tab = QWidget()
            self.open_editors = {}

        def tr(self, text):
            return {"Welcome": "Bienvenue"}.get(text, text)

        def safe_disconnect_signal(self, *args):
            pass

        def _forget_open_editor(self, editor):
            for k, v in list(self.open_editors.items()):
                if v is editor:
                    del self.open_editors[k]

    return _IDEStub()


def _flush_deferred_deletes():
    from PySide6.QtCore import QCoreApplication, QEvent
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def _is_alive(widget):
    import shiboken6
    return shiboken6.isValid(widget)


class TestWelcomeTabClose:

    def test_closing_translated_welcome_tab_is_a_noop(self, qapp):
        ide_cls = _ide_cls()
        stub = _make_stub(qapp)
        ide_cls._add_welcome_tab(stub)
        assert stub.editor_tabs.tabText(0) == "Bienvenue"

        ide_cls.close_editor_tab(stub, 0)
        _flush_deferred_deletes()

        assert stub.editor_tabs.count() == 1
        assert stub.editor_tabs.widget(0) is stub.welcome_tab
        assert _is_alive(stub.welcome_tab)

    def test_welcome_tab_survives_for_later_readds(self, qapp):
        """The H1 chain: close, then re-add as on_project_loaded does."""
        ide_cls = _ide_cls()
        stub = _make_stub(qapp)
        ide_cls._add_welcome_tab(stub)

        ide_cls.close_editor_tab(stub, 0)
        _flush_deferred_deletes()

        # Pre-fix this raised RuntimeError('Internal C++ object already
        # deleted') once the deferred delete had run.
        stub.editor_tabs.removeTab(0)
        ide_cls._add_welcome_tab(stub)
        assert stub.editor_tabs.count() == 1
        assert _is_alive(stub.welcome_tab)

    def test_welcome_tab_has_no_close_button(self, qapp):
        from PySide6.QtWidgets import QTabBar
        ide_cls = _ide_cls()
        stub = _make_stub(qapp)
        ide_cls._add_welcome_tab(stub)

        bar = stub.editor_tabs.tabBar()
        assert bar.tabButton(0, QTabBar.RightSide) is None
        assert bar.tabButton(0, QTabBar.LeftSide) is None

    def test_regular_editor_tab_still_closes(self, qapp):
        from PySide6.QtWidgets import QWidget
        ide_cls = _ide_cls()
        stub = _make_stub(qapp)
        ide_cls._add_welcome_tab(stub)

        editor = QWidget()
        stub.editor_tabs.addTab(editor, "obj_player")
        stub.open_editors["obj_player"] = editor

        ide_cls.close_editor_tab(stub, 1)
        _flush_deferred_deletes()

        assert stub.editor_tabs.count() == 1
        assert stub.editor_tabs.widget(0) is stub.welcome_tab
        assert "obj_player" not in stub.open_editors
        assert not _is_alive(editor)
