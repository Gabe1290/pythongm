"""widgets/asset_tree/asset_dialogs.OrphanedFilesDialog — Tier 3 of
docs/CLEAN_PROJECT_PLAN.md. Real offscreen QApplication + a real
AssetManager against a real temp project directory, matching this repo's
established widget-test convention (see tests/test_trash_dialog.py and
tests/test_unused_assets_dialog.py).
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def asset_manager(_qapp, tmp_path):
    (tmp_path / "sprites").mkdir()
    with patch('pygame.mixer.init'):
        from core.asset_manager import AssetManager
        return AssetManager(project_directory=tmp_path)


def _sync_cache(asset_manager, project_data):
    """OrphanedFilesDialog._refresh_found calls save_assets_to_project_data
    first (the force_project_refresh pattern), which overwrites
    project_data['assets'] from asset_manager.assets_cache — so a
    hand-built project_data dict in a test needs the cache seeded to
    match, or that call silently wipes it back to empty."""
    asset_manager.assets_cache = {
        k: dict(v) for k, v in project_data.get("assets", {}).items()
    }


def _make_dialog(project_data, asset_manager):
    from widgets.asset_tree.asset_dialogs import OrphanedFilesDialog
    _sync_cache(asset_manager, project_data)
    return OrphanedFilesDialog(project_data, asset_manager)


class TestOrphanedFilesDialogListing:
    def test_no_orphans_shows_placeholder(self, _qapp, asset_manager):
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)

        assert dialog.tree_widget.topLevelItemCount() == 1
        assert not dialog.trash_btn.isEnabled()

    def test_orphaned_file_is_listed(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"png")
        project_data = {"assets": {}}

        dialog = _make_dialog(project_data, asset_manager)

        found = set()
        for i in range(dialog.tree_widget.topLevelItemCount()):
            cat_item = dialog.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                found.add(cat_item.child(j).data(0, Qt.UserRole))
        assert "sprites/spr_leftover.png" in found

    def test_referenced_file_is_not_listed(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        project_data = {"assets": {"sprites": {
            "spr_hero": {"file_path": "sprites/spr_hero.png"}}}}

        dialog = _make_dialog(project_data, asset_manager)

        for i in range(dialog.tree_widget.topLevelItemCount()):
            cat_item = dialog.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                assert cat_item.child(j).data(0, Qt.UserRole) != "sprites/spr_hero.png"


class TestOrphanedFilesDialogTrashing:
    def test_trash_selected_moves_file_and_lists_in_trash(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"png")
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._trash_selected()

        assert dialog.trashed_count == 1
        assert not (tmp_path / "sprites" / "spr_leftover.png").exists()
        assert dialog.trash_list.count() == 1
        # Re-scanning after trashing should no longer find it as an
        # orphan on disk (it isn't on disk anymore).
        found = set()
        for i in range(dialog.tree_widget.topLevelItemCount()):
            cat_item = dialog.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                found.add(cat_item.child(j).data(0, Qt.UserRole))
        assert "sprites/spr_leftover.png" not in found

    def test_trash_declined_keeps_file_in_place(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"png")
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.No):
            dialog._trash_selected()

        assert dialog.trashed_count == 0
        assert (tmp_path / "sprites" / "spr_leftover.png").exists()

    def test_no_selection_trash_is_a_safe_noop(self, _qapp, asset_manager):
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)

        dialog._trash_selected()

        assert dialog.trashed_count == 0


class TestOrphanedFilesDialogRestore:
    def test_restore_moves_file_back_and_updates_lists(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"png")
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)
        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._trash_selected()

        dialog.trash_list.setCurrentRow(0)
        dialog._restore_selected()

        assert (tmp_path / "sprites" / "spr_leftover.png").exists()
        assert dialog.trash_list.count() == 0

    def test_restore_collision_shows_warning_and_keeps_entry(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"original")
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)
        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._trash_selected()

        # Something new created at the same path since the trash.
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"new")

        dialog.trash_list.setCurrentRow(0)
        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.warning") as mock_warn:
            dialog._restore_selected()

        assert mock_warn.called
        assert dialog.trash_list.count() == 1
        assert (tmp_path / "sprites" / "spr_leftover.png").read_bytes() == b"new"

    def test_no_selection_restore_is_a_safe_noop(self, _qapp, asset_manager):
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)

        dialog._restore_selected()  # nothing selected


class TestOrphanedFilesDialogPermanentDelete:
    def test_delete_permanently_confirmed_removes_entry(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"png")
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)
        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._trash_selected()

        dialog.trash_list.setCurrentRow(0)
        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._delete_selected_permanently()

        assert dialog.trash_list.count() == 0

    def test_empty_all_confirmed_clears_everything(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_a.png").write_bytes(b"a")
        (tmp_path / "sprites" / "spr_b.png").write_bytes(b"b")
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)
        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._trash_selected()
        assert dialog.trash_list.count() == 2

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._empty_all()

        assert dialog.trash_list.count() == 0


class TestOrphanedTrashIsolatedFromAssetTrash:
    def test_trashed_orphan_does_not_appear_in_asset_manager_trash(
            self, _qapp, asset_manager, tmp_path):
        """Regression for the design decision in utils/project_cleanup.py's
        module docstring: mixing stores risks AssetManager.restore_from_trash
        planting a fake assets_cache entry for a bare file on restore."""
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"png")
        project_data = {"assets": {}}
        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)
        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._trash_selected()

        assert asset_manager.list_trash() == []


class TestShowOrphanedFilesDialogDispatch:
    """core/ide_window.py's PyGameMakerIDE.show_orphaned_files_dialog, via
    the repo's established unbound-call-on-a-stub pattern."""

    def _ide_cls(self):
        from core.ide_window import PyGameMakerIDE
        return PyGameMakerIDE

    def test_no_project_shows_info_message(self, _qapp):
        stub = MagicMock()
        stub.current_project_path = None
        stub.project_manager = MagicMock()
        stub.tr = lambda text: text

        with patch("core.ide._dialogs.QMessageBox") as mock_box:
            self._ide_cls().show_orphaned_files_dialog(stub)

        assert mock_box.information.called

    def test_with_project_opens_dialog(self, _qapp):
        stub = MagicMock()
        stub.current_project_path = "/fake/project"
        stub.project_manager.asset_manager = MagicMock()
        stub.current_project_data = {"assets": {}}
        stub.tr = lambda text: text

        with patch("widgets.asset_tree.asset_dialogs.OrphanedFilesDialog") as mock_dialog_cls:
            mock_dialog_cls.return_value = MagicMock()
            self._ide_cls().show_orphaned_files_dialog(stub)

        assert mock_dialog_cls.return_value.exec.called
