"""Regression test for re-opening a modified asset (audit M11).

docs/FULL_AUDIT_2026-06-11.md: the open_*_editor focus-existing checks
compared self.editor_tabs.tabText(i) == name, but on_editor_data_modified
renames a dirty editor's tab to name+'*'. So re-opening an asset whose
editor had unsaved changes failed the text match, fell through, and built
a SECOND editor for the same asset (overwriting open_editors[name]),
stranding the original tab's unsaved changes. The focus checks now compare
by widget identity, which is immune to the '*' marker.
"""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _stub_with_open_editor(qapp, asset_name, dirty=True):
    from PySide6.QtWidgets import QTabWidget, QWidget
    tabs = QTabWidget()
    existing = QWidget()
    tabs.addTab(QWidget(), "other")           # index 0
    tabs.addTab(existing, asset_name + ("*" if dirty else ""))  # index 1
    stub = SimpleNamespace(
        open_editors={asset_name: existing},
        editor_tabs=tabs,
        _focus_detached_editor=lambda name: False,
        current_project_path="/tmp/x",
    )
    return stub, tabs, existing


class TestFocusInsteadOfDuplicate:
    def test_room_editor_focuses_dirty_existing(self, qapp):
        stub, tabs, existing = _stub_with_open_editor(qapp, "level1", dirty=True)
        with patch('core.ide_window.RoomEditor') as RE:
            _ide_cls().open_room_editor(stub, "level1", {})
        RE.assert_not_called()                 # no duplicate constructed
        assert tabs.currentWidget() is existing  # focused the existing one

    def test_object_editor_focuses_dirty_existing(self, qapp):
        stub, tabs, existing = _stub_with_open_editor(qapp, "obj_hero", dirty=True)
        with patch('core.ide_window.ObjectEditor') as OE:
            _ide_cls().open_object_editor(stub, "obj_hero", {})
        OE.assert_not_called()
        assert tabs.currentWidget() is existing

    def test_sprite_editor_focuses_dirty_existing(self, qapp):
        stub, tabs, existing = _stub_with_open_editor(qapp, "spr_ball", dirty=True)
        with patch('core.ide_window.SpriteEditor') as SE:
            _ide_cls().open_sprite_editor(stub, "spr_ball", {})
        SE.assert_not_called()
        assert tabs.currentWidget() is existing

    def test_clean_editor_still_focuses(self, qapp):
        # The non-dirty case worked before too; make sure it still does.
        stub, tabs, existing = _stub_with_open_editor(qapp, "level2", dirty=False)
        with patch('core.ide_window.RoomEditor') as RE:
            _ide_cls().open_room_editor(stub, "level2", {})
        RE.assert_not_called()
        assert tabs.currentWidget() is existing
