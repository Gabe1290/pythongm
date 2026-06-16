"""Regression test for open_editors composite keying (audit L5).

open_editors was keyed by bare asset name, so a room and an object that legally
share a name collided: opening the second focused the first (couldn't open),
and deleting one closed the other. Keys are now "<category>:<name>".
"""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def test_editor_key_is_composite():
    ide = _ide_cls()
    # Same bare name, different categories -> distinct keys.
    assert ide._editor_key(ide, "rooms", "niveau1") != ide._editor_key(ide, "objects", "niveau1")


def test_canonical_category_unifies_singular_plural():
    ide = _ide_cls()
    assert ide._canonical_category("object") == "objects"
    assert ide._canonical_category("objects") == "objects"
    assert ide._canonical_category("room") == "rooms"


class _FakeTabs:
    """Minimal stand-in for QTabWidget that accepts mock editors as widgets."""
    def __init__(self):
        self.widgets = []
    def count(self):
        return len(self.widgets)
    def widget(self, i):
        return self.widgets[i]
    def addTab(self, w, label):
        self.widgets.append(w)
        return len(self.widgets) - 1
    def setCurrentIndex(self, i):
        pass


def test_same_named_room_and_object_both_open(qapp):
    room_editor = object()
    tabs = _FakeTabs()
    tabs.widgets.append(room_editor)

    stub = SimpleNamespace(
        open_editors={"rooms:niveau1": room_editor},
        editor_tabs=tabs,
        _focus_detached_editor=lambda key: False,
        _editor_key=lambda cat, name: f"{cat}:{name}",
        current_project_path="/tmp/x",
        window_mode="tabbed",
        tr=lambda s: s,
        update_status=lambda *a, **k: None,
        _collapse_right_panel=lambda: None,
        on_editor_save_requested=None,
        on_editor_close_requested=None,
        on_editor_data_modified=None,
        float_editor=None,
        reattach_editor=None,
        on_object_editor_activated=None,
    )

    # Opening an OBJECT named 'niveau1' must NOT focus the room (different
    # composite key); it builds a new object editor.
    with patch('core.ide_window.ObjectEditor') as OE:
        _ide_cls().open_object_editor(stub, "niveau1", {})
        OE.assert_called_once()  # a new object editor was constructed

    assert "rooms:niveau1" in stub.open_editors
    assert "objects:niveau1" in stub.open_editors
    assert stub.open_editors["rooms:niveau1"] is room_editor


def test_close_request_resolves_composite_key():
    """An editor's close_requested carries the bare asset_name, but
    open_editors is composite-keyed. on_editor_close_requested must resolve the
    emitting editor's real "<category>:<name>" key (via sender()/_open_key) and
    must disambiguate two same-named editors of different categories. Passing
    the bare name (the old behaviour) silently missed the registry and left the
    editor open.
    """
    from PySide6.QtWidgets import QApplication, QWidget
    from PySide6.QtCore import QObject, Signal

    QApplication.instance() or QApplication([])
    ide_cls = _ide_cls()

    class _Editor(QObject):
        close_requested = Signal(str)

        def __init__(self, name, key):
            super().__init__()
            self.asset_name = name
            self._open_editor_key = key

    class _StubIDE(QWidget):
        _editor_key = ide_cls._editor_key
        _canonical_category = ide_cls._canonical_category
        _open_key = ide_cls._open_key
        on_editor_close_requested = ide_cls.on_editor_close_requested

        def __init__(self):
            super().__init__()
            self.open_editors = {}
            self.detached_editor_windows = {}
            self.closed = []

        def close_editor_by_name(self, key):
            self.closed.append(key)

    ide = _StubIDE()
    sprite_ed = _Editor("player", "sprites:player")
    object_ed = _Editor("player", "objects:player")
    ide.open_editors = {"sprites:player": sprite_ed, "objects:player": object_ed}
    sprite_ed.close_requested.connect(ide.on_editor_close_requested)
    object_ed.close_requested.connect(ide.on_editor_close_requested)

    sprite_ed.close_requested.emit(sprite_ed.asset_name)
    object_ed.close_requested.emit(object_ed.asset_name)

    assert ide.closed == ["sprites:player", "objects:player"]
