"""widgets/asset_tree/asset_dialogs.TrashDialog — the UI half of the
soft-delete design decision (utils/asset_trash.py's module docstring,
docs/ASSET_MANAGER_PLAN.md "bulk-delete-undo" question). Real offscreen
QApplication + a real AssetManager against a real temp project directory,
matching this repo's established widget-test convention.
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


def _make_dialog(_qapp, asset_manager):
    from widgets.asset_tree.asset_dialogs import TrashDialog
    return TrashDialog(asset_manager)


class TestTrashDialogListing:
    def test_empty_trash_shows_nothing_and_disables_buttons(self, _qapp, asset_manager):
        dialog = _make_dialog(_qapp, asset_manager)
        assert dialog.list_widget.count() == 0
        assert not dialog.restore_btn.isEnabled()
        assert not dialog.delete_btn.isEnabled()
        assert not dialog.empty_btn.isEnabled()

    def test_trashed_asset_appears_in_the_list(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        asset_manager.assets_cache["sprites"] = {
            "spr_hero": {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}}
        asset_manager.delete_asset("sprites", "spr_hero")

        dialog = _make_dialog(_qapp, asset_manager)

        assert dialog.list_widget.count() == 1
        assert "spr_hero" in dialog.list_widget.item(0).text()
        assert dialog.empty_btn.isEnabled()


class TestTrashDialogRestore:
    def test_restore_calls_on_restored_callback_and_refreshes(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        asset_manager.assets_cache["sprites"] = {
            "spr_hero": {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}}
        asset_manager.delete_asset("sprites", "spr_hero")

        dialog = _make_dialog(_qapp, asset_manager)
        dialog.list_widget.setCurrentRow(0)
        callback = MagicMock()
        dialog.on_restored = callback

        dialog._restore_selected()

        callback.assert_called_once()
        args = callback.call_args[0]
        assert args[0] == "sprites"
        assert args[1] == "spr_hero"
        assert dialog.list_widget.count() == 0  # refreshed, now empty

    def test_restore_collision_shows_warning_and_keeps_entry(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"original")
        asset_manager.assets_cache["sprites"] = {
            "spr_hero": {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}}
        asset_manager.delete_asset("sprites", "spr_hero")
        # A new file now sits where the restored one would go.
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"a newer sprite")

        dialog = _make_dialog(_qapp, asset_manager)
        dialog.list_widget.setCurrentRow(0)

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox") as mock_box:
            dialog._restore_selected()

        assert mock_box.warning.called
        assert dialog.list_widget.count() == 1  # entry survives for a retry

    def test_no_selection_restore_is_a_safe_noop(self, _qapp, asset_manager):
        dialog = _make_dialog(_qapp, asset_manager)
        dialog._restore_selected()  # must not raise


class TestTrashDialogPermanentDelete:
    def test_delete_selected_confirms_then_removes(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        asset_manager.assets_cache["sprites"] = {
            "spr_hero": {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}}
        asset_manager.delete_asset("sprites", "spr_hero")

        dialog = _make_dialog(_qapp, asset_manager)
        dialog.list_widget.setCurrentRow(0)

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox") as mock_box:
            mock_box.question.return_value = mock_box.Yes
            dialog._delete_selected()

        assert dialog.list_widget.count() == 0
        assert asset_manager.list_trash() == []

    def test_delete_selected_declined_keeps_entry(self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        asset_manager.assets_cache["sprites"] = {
            "spr_hero": {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}}
        asset_manager.delete_asset("sprites", "spr_hero")

        dialog = _make_dialog(_qapp, asset_manager)
        dialog.list_widget.setCurrentRow(0)

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox") as mock_box:
            mock_box.question.return_value = mock_box.No
            dialog._delete_selected()

        assert dialog.list_widget.count() == 1
        assert len(asset_manager.list_trash()) == 1

    def test_empty_all_confirms_then_clears_everything(self, _qapp, asset_manager, tmp_path):
        for name in ("spr_a", "spr_b"):
            (tmp_path / "sprites" / f"{name}.png").write_bytes(b"png")
        asset_manager.assets_cache["sprites"] = {
            "spr_a": {"name": "spr_a", "file_path": "sprites/spr_a.png"},
            "spr_b": {"name": "spr_b", "file_path": "sprites/spr_b.png"},
        }
        asset_manager.delete_asset("sprites", "spr_a")
        asset_manager.delete_asset("sprites", "spr_b")

        dialog = _make_dialog(_qapp, asset_manager)
        assert dialog.list_widget.count() == 2

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox") as mock_box:
            mock_box.question.return_value = mock_box.Yes
            dialog._empty_all()

        assert dialog.list_widget.count() == 0
        assert asset_manager.list_trash() == []


class TestTrashDialogClearedReferencesDetail:
    def test_selecting_entry_with_cleared_references_shows_detail(
            self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        asset_manager.assets_cache["sprites"] = {
            "spr_hero": {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}}
        asset_manager.assets_cache["objects"] = {
            "obj_player": {"name": "obj_player", "sprite": "spr_hero"}}
        asset_manager.delete_asset("sprites", "spr_hero")

        dialog = _make_dialog(_qapp, asset_manager)
        dialog.list_widget.setCurrentRow(0)

        assert "obj_player" in dialog.detail_label.text()

    def test_selecting_entry_without_cleared_references_shows_nothing(
            self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        asset_manager.assets_cache["sprites"] = {
            "spr_hero": {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}}
        asset_manager.delete_asset("sprites", "spr_hero")

        dialog = _make_dialog(_qapp, asset_manager)
        dialog.list_widget.setCurrentRow(0)

        assert dialog.detail_label.text() == ""


class TestShowTrashDialogDispatch:
    """core/ide_window.py's PyGameMakerIDE.show_trash_dialog, via the
    repo's established unbound-call-on-a-stub pattern."""

    def _ide_cls(self):
        from core.ide_window import PyGameMakerIDE
        return PyGameMakerIDE

    def test_no_project_shows_info_message(self, _qapp):
        stub = MagicMock()
        stub.current_project_path = None
        stub.project_manager = MagicMock()
        stub.tr = lambda text: text

        with patch("core.ide._dialogs.QMessageBox") as mock_box:
            self._ide_cls().show_trash_dialog(stub)

        assert mock_box.information.called

    def test_with_project_opens_dialog(self, _qapp):
        stub = MagicMock()
        stub.current_project_path = "/fake/project"
        stub.project_manager.asset_manager = MagicMock()
        stub.tr = lambda text: text

        # show_trash_dialog imports TrashDialog locally from its real
        # module, so that's the path to patch (not core.ide_window).
        with patch("widgets.asset_tree.asset_dialogs.TrashDialog") as mock_dialog_cls:
            mock_dialog_cls.return_value = MagicMock()
            self._ide_cls().show_trash_dialog(stub)

        assert mock_dialog_cls.return_value.exec.called
