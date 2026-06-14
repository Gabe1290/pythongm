"""Regression test for force_project_refresh discarding unsaved work (M60).

force_project_refresh used to call project_manager.load_project() unconditionally,
re-reading project.json from disk and clearing is_dirty — silently reverting
unsaved in-memory changes (e.g. drag-reorder of rooms) and defeating the
close-with-unsaved-changes prompt. H13/H14 changed it to refresh from the live
in-memory model. This locks in that it never reloads from disk.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_force_refresh_does_not_reload_from_disk(_qapp):
    from PySide6.QtWidgets import QWidget
    from widgets.asset_tree.asset_tree_widget import AssetTreeWidget

    class _AssetManager:
        def __init__(self):
            self.folded = False

        def save_assets_to_project_data(self, data):
            self.folded = True

    class _ProjectManager:
        def __init__(self):
            self.current_project_data = {"assets": {"rooms": {}}}
            self.asset_manager = _AssetManager()
            self.load_called = False
            self.is_dirty_flag = True

        def load_project(self, *a, **k):  # must NOT be called
            self.load_called = True
            raise AssertionError("force_project_refresh reloaded from disk")

    parent = QWidget()
    pm = _ProjectManager()
    parent.project_manager = pm

    tree = AssetTreeWidget(parent)
    # Avoid heavy redraw work; we only care that no disk reload happens.
    tree.refresh_from_project = lambda data: None

    tree.force_project_refresh()

    assert pm.load_called is False
    assert pm.asset_manager.folded is True  # refreshed from the live model
    assert pm.is_dirty_flag is True  # dirty flag preserved
