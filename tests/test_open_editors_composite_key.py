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
