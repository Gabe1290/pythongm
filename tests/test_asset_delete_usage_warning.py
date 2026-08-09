"""AssetOperations.delete_asset's confirmation dialog now warns about
existing usages — DEFERRED_ITEMS_PLAN.md item 10 (Asset Manager) Tier 1.
See docs/ASSET_MANAGER_PLAN.md.

Before this, deleting a still-referenced sprite/sound/object/background
gave a generic "this will permanently remove it" confirmation with no
hint of what would break — the only reference-clearing that ever existed
was sprite->object, and even that gave no warning up front. Now the
dialog text includes a usage summary (built from utils.asset_usage) when
the asset is still referenced, and stays exactly as before when it's
genuinely unused.
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


def _make_item(_qapp, asset_type, asset_name, asset_data=None):
    from widgets.asset_tree.asset_tree_item import AssetTreeItem
    return AssetTreeItem(parent=None, asset_type=asset_type, asset_name=asset_name,
                          asset_data=asset_data or {"name": asset_name})


class _FakeTree:
    def __init__(self, project_data):
        self.project_path = "/tmp/fake_project"
        self.project_manager = MagicMock()
        self.project_manager.current_project_data = project_data

    def parent(self):
        return None


def _project_with_used_sprite():
    return {"assets": {
        "sprites": {"spr_hero": {"name": "spr_hero"}},
        "objects": {"obj_player": {"sprite": "spr_hero", "events": {}}},
        "rooms": {},
    }}


def _project_with_unused_sprite():
    return {"assets": {
        "sprites": {"spr_orphan": {"name": "spr_orphan"}},
        "objects": {},
        "rooms": {},
    }}


def test_delete_warns_about_existing_usages(_qapp):
    from widgets.asset_tree.asset_operations import AssetOperations

    item = _make_item(_qapp, "sprites", "spr_hero")
    ops = AssetOperations(_FakeTree(_project_with_used_sprite()))

    with patch("widgets.asset_tree.asset_operations.QMessageBox") as mock_box:
        mock_box.question.return_value = mock_box.No
        ops.delete_asset(item)

    assert mock_box.question.called
    message = mock_box.question.call_args[0][2]
    assert "still referenced in 1 place" in message
    assert "obj_player" in message


def test_delete_of_unused_asset_has_no_usage_note(_qapp):
    from widgets.asset_tree.asset_operations import AssetOperations

    item = _make_item(_qapp, "sprites", "spr_orphan")
    ops = AssetOperations(_FakeTree(_project_with_unused_sprite()))

    with patch("widgets.asset_tree.asset_operations.QMessageBox") as mock_box:
        mock_box.question.return_value = mock_box.No
        ops.delete_asset(item)

    assert mock_box.question.called
    message = mock_box.question.call_args[0][2]
    assert "still referenced" not in message
    assert "permanently remove the asset" in message


def test_delete_with_no_project_manager_does_not_crash(_qapp):
    # AssetOperations is also used via a "legacy fallback" path with no
    # project_manager attached (see test_audit_asset_operations_sidefiles.py) —
    # the usage lookup must degrade gracefully, not throw, when there's no
    # current_project_data to check against.
    from widgets.asset_tree.asset_operations import AssetOperations

    class _NoProjectManagerTree:
        project_path = "/tmp/fake_project"
        project_manager = None

        def parent(self):
            return None

    item = _make_item(_qapp, "sprites", "spr_anything")
    ops = AssetOperations(_NoProjectManagerTree())

    with patch("widgets.asset_tree.asset_operations.QMessageBox") as mock_box:
        mock_box.question.return_value = mock_box.No
        ops.delete_asset(item)  # must not raise

    assert mock_box.question.called
