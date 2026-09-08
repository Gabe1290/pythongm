"""L8, docs/FULL_AUDIT_2026-09-07.md: on_editor_data_modified identified
the tab by bare title.

data_modified only carries the asset's bare name (Signal(str)), and
on_editor_data_modified matched a tab by `tabText(i) == asset_name` --
so a sprite and an object sharing a name ("player" is common) have two
tabs both titled "player", and editing EITHER one always marked
whichever tab came first in the QTabWidget, not the one that actually
changed.

Fix: match by widget identity via self.sender() -- the standard Qt way
to recover which connected object emitted the signal currently being
handled -- the same idiom close_editor_by_name (same file) already uses.

Uses a real QTabWidget + two real BaseEditor-derived widgets, connected
via a genuine Qt signal/slot connection (not a lambda wrapper, so
sender() tracking is exactly what production code gets) to a minimal
QObject host carrying just EditorLifecycleMixin -- avoids constructing
the full PyGameMakerIDE window (see
tests/test_create_asset_name_validation.py's docstring for why that's
worth avoiding here).
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


class _TestEditor:
    """Minimal BaseEditor subclass -- just enough to instantiate (the
    three abstractmethods) and carry the real data_modified signal."""

    def load_data(self, data):
        self.asset_data = data

    def get_data(self):
        return self.asset_data

    def validate_data(self):
        return True, ""


def _make_editor(_qapp):
    from editors.base_editor import BaseEditor

    class Editor(_TestEditor, BaseEditor):
        pass

    return Editor()


def _make_host(editor_tabs):
    from PySide6.QtCore import QObject
    from core.ide._editor_lifecycle import EditorLifecycleMixin

    class Host(EditorLifecycleMixin, QObject):
        def __init__(self):
            super().__init__()
            self.editor_tabs = editor_tabs
            self.project_manager = MagicMock()

    return Host()


def test_editing_the_second_of_two_same_named_tabs_marks_the_second(_qapp):
    from PySide6.QtWidgets import QTabWidget

    tabs = QTabWidget()
    sprite_editor = _make_editor(_qapp)
    object_editor = _make_editor(_qapp)
    tabs.addTab(sprite_editor, "player")   # index 0
    tabs.addTab(object_editor, "player")   # index 1

    host = _make_host(tabs)
    sprite_editor.data_modified.connect(host.on_editor_data_modified)
    object_editor.data_modified.connect(host.on_editor_data_modified)

    # The OBJECT editor (index 1) changed -- only its tab should get the
    # dirty marker, even though both tabs share the exact same title.
    object_editor.data_modified.emit("player")

    assert tabs.tabText(0) == "player"
    assert tabs.tabText(1) == "player*"


def test_editing_the_first_of_two_same_named_tabs_marks_the_first(_qapp):
    from PySide6.QtWidgets import QTabWidget

    tabs = QTabWidget()
    sprite_editor = _make_editor(_qapp)
    object_editor = _make_editor(_qapp)
    tabs.addTab(sprite_editor, "player")   # index 0
    tabs.addTab(object_editor, "player")   # index 1

    host = _make_host(tabs)
    sprite_editor.data_modified.connect(host.on_editor_data_modified)
    object_editor.data_modified.connect(host.on_editor_data_modified)

    sprite_editor.data_modified.emit("player")

    assert tabs.tabText(0) == "player*"
    assert tabs.tabText(1) == "player"


def test_already_dirty_tab_is_not_double_marked(_qapp):
    from PySide6.QtWidgets import QTabWidget

    tabs = QTabWidget()
    editor = _make_editor(_qapp)
    tabs.addTab(editor, "player*")

    host = _make_host(tabs)
    editor.data_modified.connect(host.on_editor_data_modified)

    editor.data_modified.emit("player")

    assert tabs.tabText(0) == "player*"
