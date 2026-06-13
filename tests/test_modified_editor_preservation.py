"""Regression tests for preserving modified editors (audit M12).

docs/FULL_AUDIT_2026-06-11.md: on_project_loaded tore down every editor
(deleteLater) with no is_modified check, and closeEvent checked only
project_manager.is_dirty() — which editor-local edits never set
(on_editor_data_modified only renamed the tab). So switching projects or
closing the IDE silently discarded unsaved in-editor work, while closing a
single tab prompted to save.

Now editor edits mark the project dirty (so the close prompt fires), and a
_flush_open_editors helper pushes editor data into the project before the
close-Save and before a project switch.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _editor(name, data):
    return SimpleNamespace(get_data=lambda: data, asset_name=name)


class TestEditorEditMarksProjectDirty:
    def test_on_editor_data_modified_marks_dirty(self, qapp):
        from PySide6.QtWidgets import QTabWidget
        pm = MagicMock()
        stub = SimpleNamespace(editor_tabs=QTabWidget(), project_manager=pm)
        _ide_cls().on_editor_data_modified(stub, "obj_hero")
        pm.mark_dirty.assert_called_once()


class TestFlushOpenEditors:
    def test_flush_pushes_tabbed_and_detached(self, qapp):
        tabbed = _editor("obj_a", {"events": {"step": {}}})
        detached = _editor("obj_b", {"events": {"create": {}}})
        saved = []
        stub = SimpleNamespace(
            _iter_open_editors=lambda: iter([tabbed, detached]),
            on_editor_save_requested=lambda n, d: saved.append((n, d)),
        )
        _ide_cls()._flush_open_editors(stub)
        names = [n for n, _ in saved]
        assert names == ["obj_a", "obj_b"]


class TestCloseEventSavesEditorWork:
    def _close_stub(self, dirty, flushed, saved_ok=True):
        return SimpleNamespace(
            saveGeometry=lambda: b"",
            saveState=lambda: b"",
            project_manager=SimpleNamespace(is_dirty=lambda: dirty),
            _flush_open_editors=lambda: flushed.append(True),
            save_project=lambda: saved_ok,
            detached_editor_windows={},
            _tutorial_detached_window=None,
            stop_game=lambda: None,
            tr=lambda s: s,
        )

    def test_save_flushes_editors_before_saving(self, qapp):
        flushed = []
        stub = self._close_stub(dirty=True, flushed=flushed)
        event = MagicMock()
        with patch('core.ide_window.Config'), \
             patch('core.ide_window.QMessageBox') as MB:
            MB.Save = 1
            MB.Discard = 2
            MB.Cancel = 4
            MB.question.return_value = MB.Save
            _ide_cls().closeEvent(stub, event)
        assert flushed == [True]      # editors flushed before save
        event.accept.assert_called_once()

    def test_cancel_does_not_flush_or_close(self, qapp):
        flushed = []
        stub = self._close_stub(dirty=True, flushed=flushed)
        event = MagicMock()
        with patch('core.ide_window.Config'), \
             patch('core.ide_window.QMessageBox') as MB:
            MB.Save = 1
            MB.Discard = 2
            MB.Cancel = 4
            MB.question.return_value = MB.Cancel
            _ide_cls().closeEvent(stub, event)
        assert flushed == []
        event.ignore.assert_called_once()
        event.accept.assert_not_called()
