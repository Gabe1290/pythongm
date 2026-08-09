"""AssetTreeWidget bulk multi-select delete — Tier 3 of
docs/ASSET_MANAGER_PLAN.md. Real offscreen QApplication + a real
ProjectManager/AssetManager against a real temp project directory
(matching tests/test_asset_tree_state_sync.py's "project" fixture), so
the deletion actually round-trips through the live model and lands in
the trash, not a mocked stand-in.
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

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _make_pm():
    with patch('pygame.mixer.init'):
        from core.asset_manager import AssetManager
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=AssetManager())
        pm.auto_save_timer = MagicMock()
        return pm


def _sprite(name):
    return {'name': name, 'asset_type': 'sprite', 'file_path': '',
            'width': 32, 'height': 32}


@pytest.fixture
def tree_with_project(_qapp, tmp_path):
    from widgets.asset_tree.asset_tree_widget import AssetTreeWidget

    pm = _make_pm()
    assert pm.create_new_project("proj", tmp_path) is True
    project_dir = tmp_path / "proj"

    host = QWidget()
    host.project_manager = pm

    tree = AssetTreeWidget(host)
    tree.project_manager = pm
    tree.project_path = str(project_dir)
    # Qt parent/child ownership is C++-side; without a live Python
    # reference to `host` it gets garbage-collected at the end of this
    # function, which destroys `tree` (its child) right along with it —
    # "Internal C++ object already deleted" on first use. Pin it here.
    tree._test_host_ref = host

    for name in ("spr_a", "spr_b", "spr_c"):
        pm.asset_manager.assets_cache.setdefault('sprites', {})[name] = _sprite(name)
        tree.add_asset('sprites', name, _sprite(name))

    return tree, pm, project_dir


def _sprite_items(tree):
    for i in range(tree.topLevelItemCount()):
        cat = tree.topLevelItem(i)
        from widgets.asset_tree.asset_tree_item import AssetTreeItem
        if isinstance(cat, AssetTreeItem) and cat.asset_type == 'sprites':
            return [cat.child(j) for j in range(cat.childCount())]
    return []


class TestSelectionMode:
    def test_extended_selection_enabled(self, tree_with_project):
        from PySide6.QtWidgets import QTreeWidget
        tree, _, _ = tree_with_project
        assert tree.selectionMode() == QTreeWidget.SelectionMode.ExtendedSelection


class TestBulkDeleteSelected:
    def test_no_selection_is_a_safe_noop(self, tree_with_project):
        tree, pm, _ = tree_with_project
        tree.bulk_delete_selected()
        assert 'spr_a' in pm.asset_manager.assets_cache['sprites']

    def test_single_selection_uses_ordinary_delete_path(self, tree_with_project):
        """A single selected item should NOT go through the bulk
        combined-confirmation path — it keeps the richer per-asset
        usage-detail confirmation from AssetOperations.delete_asset."""
        tree, pm, _ = tree_with_project
        items = _sprite_items(tree)
        items[0].setSelected(True)

        with patch.object(tree.operations, 'delete_asset') as mock_single, \
             patch.object(tree.operations, 'delete_asset_confirmed') as mock_confirmed:
            tree.bulk_delete_selected()

        mock_single.assert_called_once_with(items[0])
        mock_confirmed.assert_not_called()

    def test_multi_selection_confirmed_deletes_all_with_one_dialog(self, tree_with_project):
        tree, pm, project_dir = tree_with_project
        items = _sprite_items(tree)
        for it in items:
            it.setSelected(True)

        with patch("widgets.asset_tree.asset_tree_widget.QMessageBox.question",
                   return_value=QMessageBox.Yes) as mock_question:
            tree.bulk_delete_selected()

        assert mock_question.call_count == 1  # ONE combined confirmation, not N
        for name in ("spr_a", "spr_b", "spr_c"):
            assert name not in pm.asset_manager.assets_cache.get('sprites', {})

        # Trash-backed, same as a single delete.
        assert len(pm.asset_manager.list_trash()) == 3

    def test_multi_selection_declined_deletes_nothing(self, tree_with_project):
        tree, pm, _ = tree_with_project
        items = _sprite_items(tree)
        for it in items:
            it.setSelected(True)

        with patch("widgets.asset_tree.asset_tree_widget.QMessageBox.question",
                   return_value=QMessageBox.No):
            tree.bulk_delete_selected()

        for name in ("spr_a", "spr_b", "spr_c"):
            assert name in pm.asset_manager.assets_cache['sprites']

    def test_category_items_are_never_included_in_selection(self, tree_with_project):
        """A category item lacks ItemIsSelectable (asset_tree_item.py) —
        that only blocks interactive/click selection though; the
        programmatic setSelected(True) API selects it anyway (asserted
        below), so bulk_delete_selected's own is_category filter is the
        real, necessary safety net keeping a category out of a batch
        delete, not a belt-and-braces no-op."""
        from widgets.asset_tree.asset_tree_item import AssetTreeItem
        tree, pm, _ = tree_with_project
        items = _sprite_items(tree)
        for it in items[:2]:
            it.setSelected(True)
        # Also select the category header itself.
        for i in range(tree.topLevelItemCount()):
            cat = tree.topLevelItem(i)
            if isinstance(cat, AssetTreeItem) and cat.asset_type == 'sprites':
                cat.setSelected(True)
                assert cat.isSelected() is True

        with patch("widgets.asset_tree.asset_tree_widget.QMessageBox.question",
                   return_value=QMessageBox.Yes) as mock_question:
            tree.bulk_delete_selected()

        # Confirmation dialog reports exactly 2 assets, not a 3rd
        # "category" entry sneaking in.
        assert mock_question.call_args[0][1] == "Delete 2 Assets"
        assert 'spr_a' not in pm.asset_manager.assets_cache.get('sprites', {})
        assert 'spr_b' not in pm.asset_manager.assets_cache.get('sprites', {})
        assert 'spr_c' in pm.asset_manager.assets_cache['sprites']


class TestDeleteAssetConfirmed:
    """AssetOperations.delete_asset_confirmed — the shared step split out
    of delete_asset so bulk delete can skip the per-item dialog."""

    def test_does_not_show_a_confirmation_dialog(self, tree_with_project):
        tree, pm, _ = tree_with_project
        items = _sprite_items(tree)

        with patch("widgets.asset_tree.asset_operations.QMessageBox") as mock_box:
            result = tree.operations.delete_asset_confirmed(items[0])

        assert result is True
        mock_box.question.assert_not_called()
        assert 'spr_a' not in pm.asset_manager.assets_cache['sprites']

    def test_closes_open_editor_when_called_directly(self, tree_with_project):
        """delete_asset_confirmed is the only editor-closing step for a
        caller (bulk delete) that skips delete_asset's dialog entirely —
        _close_open_editor_if_any must still fire from this path, not
        only from delete_asset's pre-confirmation call."""
        tree, pm, _ = tree_with_project
        items = _sprite_items(tree)
        tree._test_host_ref.open_editors = {"sprites:spr_a": object()}
        tree._test_host_ref._editor_key = lambda category, name: f"{category}:{name}"
        closed = []
        tree._test_host_ref.close_editor_by_name = lambda key: closed.append(key)

        tree.operations.delete_asset_confirmed(items[0])

        assert closed == ["sprites:spr_a"]

    def test_category_item_returns_false(self, tree_with_project):
        from widgets.asset_tree.asset_tree_item import AssetTreeItem
        tree, _, _ = tree_with_project
        for i in range(tree.topLevelItemCount()):
            cat = tree.topLevelItem(i)
            if isinstance(cat, AssetTreeItem) and cat.asset_type == 'sprites':
                assert tree.operations.delete_asset_confirmed(cat) is False
                return
        pytest.fail("sprites category not found")
