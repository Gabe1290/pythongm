"""widgets/asset_tree/asset_dialogs.UnusedAssetsDialog — Tier 4 of
docs/ASSET_MANAGER_PLAN.md. Real offscreen QApplication + a real
AssetManager against a real temp project directory, matching this repo's
established widget-test convention (see tests/test_trash_dialog.py).
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


def _project_data():
    return {
        "assets": {
            "sprites": {
                "spr_used": {"name": "spr_used", "file_path": ""},
                "spr_unused": {"name": "spr_unused", "file_path": ""},
            },
            "objects": {
                "obj_hero": {"name": "obj_hero", "sprite": "spr_used", "events": {}},
            },
            "rooms": {
                "room_1": {"name": "room_1", "instances": [
                    {"object_name": "obj_hero", "x": 0, "y": 0}]},
            },
        }
    }


def _sync_cache(asset_manager, project_data):
    """AssetManager normally loads its cache from disk; for a hand-built
    project_data dict in a test, seed the cache the same shape
    save_assets_to_project_data expects to read back out of."""
    asset_manager.assets_cache = {
        k: dict(v) for k, v in project_data["assets"].items()
    }


def _make_dialog(project_data, asset_manager):
    from widgets.asset_tree.asset_dialogs import UnusedAssetsDialog
    return UnusedAssetsDialog(project_data, asset_manager)


class TestUnusedAssetsDialogListing:
    def test_no_unused_assets_shows_placeholder_and_disables_delete(self, _qapp, asset_manager):
        # An empty project has nothing to flag. (A populated project always
        # has at least one "unused" room in this detector — rooms have no
        # usage-tracking path at all, a documented limitation, not tested
        # here — so this is the simplest genuinely-zero-unused fixture.)
        project_data = {"assets": {}}
        _sync_cache(asset_manager, project_data)

        dialog = _make_dialog(project_data, asset_manager)

        assert dialog.tree_widget.topLevelItemCount() == 1
        assert dialog.tree_widget.topLevelItem(0).childCount() == 0
        assert not dialog.delete_btn.isEnabled()

    def test_unused_asset_appears_under_its_category(self, _qapp, asset_manager):
        project_data = _project_data()
        _sync_cache(asset_manager, project_data)

        dialog = _make_dialog(project_data, asset_manager)

        found = False
        for i in range(dialog.tree_widget.topLevelItemCount()):
            cat_item = dialog.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                if dialog.item_key(child) == ("sprites", "spr_unused"):
                    found = True
        assert found

    def test_used_asset_is_not_listed(self, _qapp, asset_manager):
        project_data = _project_data()
        _sync_cache(asset_manager, project_data)

        dialog = _make_dialog(project_data, asset_manager)

        for i in range(dialog.tree_widget.topLevelItemCount()):
            cat_item = dialog.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                assert dialog.item_key(cat_item.child(j)) != ("sprites", "spr_used")


def _check_category(dialog, category_prefix):
    """Check every leaf under the first top-level category whose label
    starts with the given prefix (categories are labelled "Sprites (N)"
    etc., so this matches on the title-cased type name)."""
    for i in range(dialog.tree_widget.topLevelItemCount()):
        cat_item = dialog.tree_widget.topLevelItem(i)
        if cat_item.text(0).lower().startswith(category_prefix.lower()):
            for j in range(cat_item.childCount()):
                cat_item.child(j).setCheckState(0, Qt.Checked)


class TestUnusedAssetsDialogSelection:
    def test_select_all_enables_delete(self, _qapp, asset_manager):
        # _project_data()'s unused set is {sprites: [spr_unused], rooms:
        # [room_1]}. Select All deliberately excludes rooms (a room with
        # zero AssetUsage records may just be a starting room never
        # explicitly navigated to by name — not the same claim as
        # "unused"), so only spr_unused gets swept in here.
        project_data = _project_data()
        _sync_cache(asset_manager, project_data)
        dialog = _make_dialog(project_data, asset_manager)

        dialog._set_all_checked(True)

        assert dialog.delete_btn.isEnabled()
        assert dialog._checked_items() == [("sprites", "spr_unused")]

    def test_select_all_excludes_rooms_but_manual_room_check_still_works(
            self, _qapp, asset_manager):
        project_data = _project_data()
        _sync_cache(asset_manager, project_data)
        dialog = _make_dialog(project_data, asset_manager)

        dialog._set_all_checked(True)
        _check_category(dialog, "rooms")

        assert ("rooms", "room_1") in dialog._checked_items()

    def test_select_none_disables_delete(self, _qapp, asset_manager):
        project_data = _project_data()
        _sync_cache(asset_manager, project_data)
        dialog = _make_dialog(project_data, asset_manager)

        dialog._set_all_checked(True)
        dialog._set_all_checked(False)

        assert not dialog.delete_btn.isEnabled()
        assert dialog._checked_items() == []


class TestUnusedAssetsDialogDelete:
    def test_delete_selected_confirmed_moves_to_trash_and_calls_callback(
            self, _qapp, asset_manager, tmp_path):
        (tmp_path / "sprites" / "spr_unused.png").write_bytes(b"png")
        project_data = _project_data()
        project_data["assets"]["sprites"]["spr_unused"]["file_path"] = "sprites/spr_unused.png"
        _sync_cache(asset_manager, project_data)

        dialog = _make_dialog(project_data, asset_manager)
        seen = []
        dialog.on_deleted = lambda t, n: seen.append((t, n))
        _check_category(dialog, "sprites")

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=__import__("PySide6.QtWidgets", fromlist=["QMessageBox"]).QMessageBox.Yes):
            dialog._delete_selected()

        assert seen == [("sprites", "spr_unused")]
        assert dialog.deleted_count == 1
        assert len(asset_manager.list_trash()) == 1
        assert "spr_unused" not in asset_manager.assets_cache.get("sprites", {})

    def test_delete_selected_declined_keeps_asset(self, _qapp, asset_manager):
        project_data = _project_data()
        _sync_cache(asset_manager, project_data)

        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)

        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=__import__("PySide6.QtWidgets", fromlist=["QMessageBox"]).QMessageBox.No):
            dialog._delete_selected()

        assert dialog.deleted_count == 0
        assert asset_manager.list_trash() == []

    def test_no_selection_delete_is_a_safe_noop(self, _qapp, asset_manager):
        project_data = _project_data()
        _sync_cache(asset_manager, project_data)
        dialog = _make_dialog(project_data, asset_manager)

        dialog._delete_selected()  # nothing checked

        assert dialog.deleted_count == 0

    def test_delete_refreshes_and_can_reveal_newly_unused_asset(
            self, _qapp, asset_manager, tmp_path):
        """Deleting an unused object removes its sprite reference, which
        should then surface that sprite as newly unused on the very next
        listing (refresh_list re-scans project_data after every delete)."""
        (tmp_path / "sprites" / "spr_used.png").write_bytes(b"png")
        # No room this time — obj_hero itself is unused, so it appears in
        # the dialog's own list of things it's willing to delete.
        project_data = {"assets": {
            "sprites": {"spr_used": {"name": "spr_used", "file_path": "sprites/spr_used.png"}},
            "objects": {"obj_hero": {"name": "obj_hero", "sprite": "spr_used", "events": {}}},
        }}
        _sync_cache(asset_manager, project_data)

        dialog = _make_dialog(project_data, asset_manager)
        _check_category(dialog, "objects")

        from PySide6.QtWidgets import QMessageBox
        with patch("widgets.asset_tree.asset_dialogs.QMessageBox.question",
                   return_value=QMessageBox.Yes):
            dialog._delete_selected()

        sprite_names = set()
        for i in range(dialog.tree_widget.topLevelItemCount()):
            cat_item = dialog.tree_widget.topLevelItem(i)
            if cat_item.text(0).lower().startswith("sprites"):
                for j in range(cat_item.childCount()):
                    sprite_names.add(dialog.item_key(cat_item.child(j)))
        assert ("sprites", "spr_used") in sprite_names


class TestItemKeyIsVersionIndependent:
    """UnusedAssetsDialog.item_key must hand back a hashable (type, name)
    tuple whatever Qt's QVariant round-trip did to the stored value.

    setData stores a tuple; PySide6 6.10 returns a LIST where 6.9 returned
    the tuple it was given, so a caller that hashed the pair (set, dict key)
    raised TypeError on one version and passed on the other. Both shapes are
    pinned explicitly below rather than only round-tripping through setData,
    because a round-trip test alone only ever exercises whichever conversion
    the installed PySide6 happens to do."""

    def _item(self, stored):
        from PySide6.QtWidgets import QTreeWidgetItem
        item = QTreeWidgetItem(["leaf"])
        item.setData(0, Qt.UserRole, stored)
        return item

    def test_normalizes_a_list_to_a_tuple(self, _qapp):
        from widgets.asset_tree.asset_dialogs import UnusedAssetsDialog
        item = self._item(["sprites", "spr_unused"])
        assert UnusedAssetsDialog.item_key(item) == ("sprites", "spr_unused")
        hash(UnusedAssetsDialog.item_key(item))  # must not raise

    def test_leaves_a_tuple_alone(self, _qapp):
        from widgets.asset_tree.asset_dialogs import UnusedAssetsDialog
        item = self._item(("sprites", "spr_unused"))
        assert UnusedAssetsDialog.item_key(item) == ("sprites", "spr_unused")

    def test_category_and_placeholder_rows_have_no_key(self, _qapp):
        from widgets.asset_tree.asset_dialogs import UnusedAssetsDialog
        assert UnusedAssetsDialog.item_key(self._item("sprites")) is None
        assert UnusedAssetsDialog.item_key(self._item(None)) is None

    def test_checked_items_are_hashable(self, _qapp, asset_manager):
        project_data = _project_data()
        _sync_cache(asset_manager, project_data)
        dialog = _make_dialog(project_data, asset_manager)
        dialog._set_all_checked(True)
        assert set(dialog._checked_items())  # TypeError here on a regression


class TestShowUnusedAssetsDialogDispatch:
    """core/ide_window.py's PyGameMakerIDE.show_unused_assets_dialog, via
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
            self._ide_cls().show_unused_assets_dialog(stub)

        assert mock_box.information.called

    def test_with_project_opens_dialog_and_saves_on_delete(self, _qapp):
        stub = MagicMock()
        stub.current_project_path = "/fake/project"
        stub.project_manager.asset_manager = MagicMock()
        stub.current_project_data = {"assets": {}}
        stub.tr = lambda text: text

        mock_dialog = MagicMock()
        mock_dialog.deleted_count = 2
        with patch("widgets.asset_tree.asset_dialogs.UnusedAssetsDialog") as mock_dialog_cls:
            mock_dialog_cls.return_value = mock_dialog
            self._ide_cls().show_unused_assets_dialog(stub)

        assert mock_dialog.exec.called
        assert stub.project_manager.save_project.called

    def test_with_project_no_deletions_skips_save(self, _qapp):
        stub = MagicMock()
        stub.current_project_path = "/fake/project"
        stub.project_manager.asset_manager = MagicMock()
        stub.current_project_data = {"assets": {}}
        stub.tr = lambda text: text

        mock_dialog = MagicMock()
        mock_dialog.deleted_count = 0
        with patch("widgets.asset_tree.asset_dialogs.UnusedAssetsDialog") as mock_dialog_cls:
            mock_dialog_cls.return_value = mock_dialog
            self._ide_cls().show_unused_assets_dialog(stub)

        assert not stub.project_manager.save_project.called
