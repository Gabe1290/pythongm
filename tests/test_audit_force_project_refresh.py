"""
Regression test for audit finding M60.

M60 claimed force_project_refresh() reloaded the project from disk with no
dirty check, silently discarding unsaved in-memory changes (the classic case:
a drag-reorder of rooms that only marks the project dirty). The fix (audit
H13/H14) replaced the disk reload with an in-memory refresh: the tree is
redrawn from the live ProjectManager.current_project_data, NEVER from
load_project(). This test locks that in by giving the fake project_manager a
load_project() that would clobber the in-memory order if it were ever called,
plus an in-memory room order that differs from "disk", and asserting:

  * force_project_refresh() does NOT call load_project (no disk reload), and
  * the tree reflects the unsaved in-memory room order afterwards.

Constructs a real offscreen QApplication (no pytest-qt) so it runs on 3.11.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

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


class _FakeAssetManager:
    def save_assets_to_project_data(self, data):
        # No-op: the live cache is already reflected in current_project_data
        # for the purposes of this test.
        pass


class _FakeProjectManager:
    """Stands in for core.ProjectManager.

    Holds an in-memory project model (current_project_data) whose room order
    has been changed but NOT saved. load_project() represents the stale disk
    state; if force_project_refresh ever calls it, the order reverts -- which
    is exactly the M60 regression we guard against.
    """

    def __init__(self):
        # Unsaved in-memory order: room3 dragged to the front.
        self.current_project_data = {
            "assets": {
                "rooms": {
                    "room3": {"name": "room3"},
                    "room1": {"name": "room1"},
                    "room2": {"name": "room2"},
                }
            }
        }
        self.asset_manager = _FakeAssetManager()
        self.load_project_calls = 0

    def load_project(self, *args, **kwargs):
        # Stale disk order (room3 still last). Calling this would discard the
        # unsaved reorder -- the M60 bug. Record the call and apply the
        # clobber so the test can detect it either way.
        self.load_project_calls += 1
        self.current_project_data = {
            "assets": {
                "rooms": {
                    "room1": {"name": "room1"},
                    "room2": {"name": "room2"},
                    "room3": {"name": "room3"},
                }
            }
        }
        return True


def _ordered_room_names(tree):
    from widgets.asset_tree.asset_tree_widget import AssetTreeItem
    names = []
    for i in range(tree.topLevelItemCount()):
        cat = tree.topLevelItem(i)
        if isinstance(cat, AssetTreeItem) and cat.asset_type == "rooms":
            for j in range(cat.childCount()):
                child = cat.child(j)
                if isinstance(child, AssetTreeItem):
                    names.append(child.asset_name)
    return names


def test_force_project_refresh_uses_in_memory_not_disk(_qapp):
    from PySide6.QtWidgets import QWidget
    from widgets.asset_tree.asset_tree_widget import AssetTreeWidget

    # A parent that exposes project_manager, as force_project_refresh walks
    # up the parent chain looking for it.
    host = QWidget()
    pm = _FakeProjectManager()
    host.project_manager = pm

    tree = AssetTreeWidget(parent=host)

    tree.force_project_refresh()

    # The disk reload path must never be taken.
    assert pm.load_project_calls == 0, (
        "force_project_refresh reloaded from disk (load_project called) -- "
        "this is the M60 regression that discards unsaved in-memory changes"
    )

    # The tree must reflect the unsaved in-memory reorder (room3 first).
    assert _ordered_room_names(tree) == ["room3", "room1", "room2"]
