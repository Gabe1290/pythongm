"""Regression test for test_game editor sync (audit M8).

docs/FULL_AUDIT_2026-06-11.md: before launching the game, test_game synced
every open editor's live data into the project, but it iterated only
self.editor_tabs. Editors floated out of the tab strip (toolbar 'Floating'
mode / per-editor float button) live in self.open_editors /
self.detached_editor_windows and were never synced, so F5 in Floating mode
ran the game with stale data. The sync now uses _iter_open_editors, which
yields both tabbed and detached editors.
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


def test_test_game_syncs_detached_editors(tmp_path):
    """A detached editor (yielded by _iter_open_editors, absent from tabs)
    is synced before launch. The stub project dir has no project.json, so
    test_game bails right after the sync loop."""
    tabbed = _editor("obj_player", {"events": {"step": {}}})
    detached = _editor("obj_enemy", {"events": {"create": {}}})

    synced = []
    stub = SimpleNamespace(
        _game_process=None,
        current_project_path=tmp_path,  # no project.json -> early return after sync
        _iter_open_editors=lambda: iter([tabbed, detached]),
        on_editor_save_requested=lambda name, data: synced.append((name, data)),
        save_project=MagicMock(),
        _show_validation_warnings=MagicMock(),
        update_status=lambda *a: None,
        tr=lambda s: s,
    )

    with patch('core.ide_window.QMessageBox'):
        _ide_cls().test_game(stub)

    synced_names = [n for n, _ in synced]
    assert "obj_player" in synced_names
    assert "obj_enemy" in synced_names  # the detached editor — pre-fix it was skipped
    stub.save_project.assert_called_once()
