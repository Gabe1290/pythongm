"""Asset Manager batch rename — TODO.md's "Asset Manager: batch rename
was deliberately deferred as its own feature, never built."

docs/ASSET_MANAGER_PLAN.md scoped this out of Tier 3 (bulk delete) as "a
different UI shape than delete's uniform 'remove all of these'" --
unlike delete, each renamed asset needs its OWN new name. BatchRenameDialog
(widgets/asset_tree/asset_dialogs.py) shows one editable row per selected
asset, pre-filled with its current name, plus an optional find/replace-
in-names helper that rewrites every row at once -- covers both "type
each new name by hand" and "substitute a common substring across many".
AssetTreeWidget.bulk_rename_selected wires it into the existing
multi-select context menu (same reduced "bulk menu" bulk_delete_selected
already uses) and applies each changed row through the exact same
AssetOperations rename path a single rename uses.

Pure dialog-logic tests use an injected name_exists_fn callable, so they
need no live project. The AssetTreeWidget integration tests use a real
offscreen QApplication + ProjectManager/AssetManager against a real temp
project directory, matching tests/test_asset_tree_bulk_delete.py's
"tree_with_project" fixture exactly.
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

from PySide6.QtWidgets import QWidget, QDialog, QDialogButtonBox


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# ---------------------------------------------------------------------------
# BatchRenameDialog -- pure logic, injected name_exists_fn
# ---------------------------------------------------------------------------

def _never_exists(_name, _asset_type):
    return False


class TestBatchRenameDialogValidation:
    def _ok_enabled(self, dialog):
        return dialog.button_box.button(QDialogButtonBox.Ok).isEnabled()

    def test_no_changes_is_valid_a_noop(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a"), ("sprite", "b")], _never_exists)
        try:
            assert self._ok_enabled(dialog)
            assert dialog._planned_renames() == {}
        finally:
            dialog.deleteLater()

    def test_editing_one_row_plans_only_that_rename(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a"), ("sprite", "b")], _never_exists)
        try:
            dialog._new_name_items[0].setText("a_renamed")
            assert dialog._planned_renames() == {("sprite", "a"): "a_renamed"}
            assert self._ok_enabled(dialog)
        finally:
            dialog.deleteLater()

    def test_invalid_name_disables_ok(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a")], _never_exists)
        try:
            dialog._new_name_items[0].setText("bad/name")
            assert not self._ok_enabled(dialog)
            # The invalid name is still reported as "planned" (surfaced
            # as an error, not silently dropped) -- _validate is what
            # gates the Ok button, not _planned_renames itself.
            assert dialog._planned_renames() == {("sprite", "a"): "bad/name"}
            assert dialog.status_label.text() != ""
        finally:
            dialog.deleteLater()

    def test_two_rows_renamed_to_the_same_new_name_disables_ok(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a"), ("sprite", "b")], _never_exists)
        try:
            dialog._new_name_items[0].setText("same")
            dialog._new_name_items[1].setText("same")
            assert not self._ok_enabled(dialog)
        finally:
            dialog.deleteLater()

    def test_renaming_onto_an_unchanged_batch_rows_name_disables_ok(self, _qapp):
        """Row 0 ("a") renamed to "b", while row 1 ("b") is left
        unchanged -- "b" is still taken within this batch."""
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a"), ("sprite", "b")], _never_exists)
        try:
            dialog._new_name_items[0].setText("b")
            assert not self._ok_enabled(dialog)
        finally:
            dialog.deleteLater()

    def test_collision_with_an_asset_outside_the_batch_disables_ok(self, _qapp):
        def exists(name, asset_type):
            return name == "taken"
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a")], exists)
        try:
            dialog._new_name_items[0].setText("taken")
            assert not self._ok_enabled(dialog)
        finally:
            dialog.deleteLater()

    def test_name_exists_fn_is_scoped_per_asset_type(self, _qapp):
        """A collision check for a "sound" row must be called with
        asset_type="sound", not leak across types in the same batch."""
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        seen_types = []

        def exists(name, asset_type):
            seen_types.append(asset_type)
            return False

        dialog = BatchRenameDialog([("sprite", "a"), ("sound", "x")], exists)
        try:
            dialog._new_name_items[0].setText("a2")
            dialog._new_name_items[1].setText("x2")
            dialog._validate()
            assert "sprite" in seen_types
            assert "sound" in seen_types
        finally:
            dialog.deleteLater()

    def test_accept_only_commits_planned_renames_when_valid(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a"), ("sprite", "b")], _never_exists)
        try:
            dialog._new_name_items[0].setText("a_new")
            dialog._accept_renames()
            assert dialog.renames == {("sprite", "a"): "a_new"}
            assert dialog.result() == QDialog.Accepted
        finally:
            dialog.deleteLater()

    def test_accept_is_refused_while_invalid(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a"), ("sprite", "b")], _never_exists)
        try:
            dialog._new_name_items[0].setText("same")
            dialog._new_name_items[1].setText("same")
            dialog._accept_renames()
            assert dialog.result() != QDialog.Accepted
            assert dialog.renames == {}
        finally:
            dialog.deleteLater()


class TestBatchRenameDialogFindReplace:
    def test_apply_to_all_rewrites_every_row(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog(
            [("sprite", "enemy_1"), ("sprite", "enemy_2")], _never_exists)
        try:
            dialog.find_edit.setText("enemy")
            dialog.replace_edit.setText("monster")
            dialog._apply_find_replace()
            assert dialog._new_name_items[0].text() == "monster_1"
            assert dialog._new_name_items[1].text() == "monster_2"
            assert dialog._planned_renames() == {
                ("sprite", "enemy_1"): "monster_1",
                ("sprite", "enemy_2"): "monster_2",
            }
        finally:
            dialog.deleteLater()

    def test_find_replace_composes_with_a_manual_edit_made_first(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "foo")], _never_exists)
        try:
            dialog._new_name_items[0].setText("foobar")
            dialog.find_edit.setText("bar")
            dialog.replace_edit.setText("baz")
            dialog._apply_find_replace()
            assert dialog._new_name_items[0].text() == "foobaz"
        finally:
            dialog.deleteLater()

    def test_empty_find_text_is_a_noop(self, _qapp):
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a")], _never_exists)
        try:
            dialog.replace_edit.setText("x")
            dialog._apply_find_replace()
            assert dialog._new_name_items[0].text() == "a"
        finally:
            dialog.deleteLater()


class TestBatchRenameDialogChainRenameLimitation:
    """Documented limitation (class docstring): a chain rename (A -> B,
    where B is itself being renamed away in the same batch) is rejected
    as a plain external collision, not silently mis-applied."""

    def test_chain_rename_is_rejected_not_silently_wrong(self, _qapp):
        def exists(name, asset_type):
            # Simulate the live project still having "b" (not yet renamed).
            return name == "b"
        from widgets.asset_tree.asset_dialogs import BatchRenameDialog
        dialog = BatchRenameDialog([("sprite", "a"), ("sprite", "b")], exists)
        try:
            dialog._new_name_items[0].setText("b")  # a -> b
            dialog._new_name_items[1].setText("c")  # b -> c
            assert not self._is_ok_enabled(dialog)
        finally:
            dialog.deleteLater()

    @staticmethod
    def _is_ok_enabled(dialog):
        return dialog.button_box.button(QDialogButtonBox.Ok).isEnabled()


# ---------------------------------------------------------------------------
# AssetTreeWidget.bulk_rename_selected -- real project round-trip
# ---------------------------------------------------------------------------

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
    tree._test_host_ref = host  # keep `host` alive; see bulk_delete test's note

    for name in ("spr_a", "spr_b", "spr_c"):
        pm.asset_manager.assets_cache.setdefault('sprites', {})[name] = _sprite(name)
        tree.add_asset('sprites', name, _sprite(name))
    pm.save_project()  # flush to disk so asset_name_exists' on-disk read sees them

    return tree, pm, project_dir


def _sprite_items(tree):
    for i in range(tree.topLevelItemCount()):
        cat = tree.topLevelItem(i)
        from widgets.asset_tree.asset_tree_item import AssetTreeItem
        if isinstance(cat, AssetTreeItem) and cat.asset_type == 'sprites':
            return [cat.child(j) for j in range(cat.childCount())]
    return []


class TestBulkRenameSelected:
    def test_no_selection_is_a_safe_noop(self, tree_with_project):
        tree, pm, _ = tree_with_project
        tree.bulk_rename_selected()  # must not raise
        assert 'spr_a' in pm.asset_manager.assets_cache['sprites']

    def test_single_selection_uses_the_ordinary_rename_dialog(self, tree_with_project):
        tree, pm, _ = tree_with_project
        items = _sprite_items(tree)
        items[0].setSelected(True)

        with patch.object(tree.operations, 'rename_asset') as mock_single:
            tree.bulk_rename_selected()

        mock_single.assert_called_once_with(items[0])

    def test_multi_selection_opens_batch_dialog_and_applies_renames(self, tree_with_project):
        tree, pm, project_dir = tree_with_project
        items = _sprite_items(tree)
        for it in items:
            it.setSelected(True)

        from widgets.asset_tree.asset_dialogs import BatchRenameDialog

        class _FakeAccepted(BatchRenameDialog):
            def exec(self):
                self._new_name_items[0].setText("spr_a_renamed")
                self.renames = self._planned_renames()
                return QDialog.Accepted

        # bulk_rename_selected imports BatchRenameDialog lazily inside the
        # method (from .asset_dialogs import BatchRenameDialog), so the
        # patch target is the dialog's own defining module -- the lazy
        # import re-resolves the attribute on every call.
        with patch("widgets.asset_tree.asset_dialogs.BatchRenameDialog", _FakeAccepted):
            tree.bulk_rename_selected()

        cache = pm.asset_manager.assets_cache['sprites']
        assert 'spr_a' not in cache
        assert 'spr_a_renamed' in cache
        assert 'spr_b' in cache
        assert 'spr_c' in cache

        item_names = {it.asset_name for it in _sprite_items(tree)}
        assert item_names == {'spr_a_renamed', 'spr_b', 'spr_c'}

    def test_cancelled_dialog_renames_nothing(self, tree_with_project):
        tree, pm, _ = tree_with_project
        items = _sprite_items(tree)
        for it in items:
            it.setSelected(True)

        from widgets.asset_tree.asset_dialogs import BatchRenameDialog

        class _FakeRejected(BatchRenameDialog):
            def exec(self):
                return QDialog.Rejected

        with patch("widgets.asset_tree.asset_dialogs.BatchRenameDialog", _FakeRejected):
            tree.bulk_rename_selected()

        for name in ("spr_a", "spr_b", "spr_c"):
            assert name in pm.asset_manager.assets_cache['sprites']
