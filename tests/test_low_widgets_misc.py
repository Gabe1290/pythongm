"""Regression tests for L33 (asset tree foreground), L34 (atomic save),
L35 (tutorial openLinks)."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6


# --------------------------------------------------------------------------
# L34 — atomic save_project_data (pure, no Qt)
# --------------------------------------------------------------------------

def test_save_project_data_writes_and_leaves_no_temp(tmp_path):
    from widgets.asset_tree.asset_utils import save_project_data
    target = tmp_path / "project.json"
    assert save_project_data(target, {"name": "T", "x": 1}) is True
    assert json.loads(target.read_text(encoding="utf-8")) == {"name": "T", "x": 1}
    # No .tmp artifacts left behind.
    leftovers = [p for p in tmp_path.iterdir() if ".tmp" in p.name]
    assert leftovers == []


def test_save_project_data_preserves_original_on_failure(tmp_path):
    from widgets.asset_tree import asset_utils
    target = tmp_path / "project.json"
    target.write_text('{"original": true}', encoding="utf-8")

    # Non-serializable payload makes json.dump raise mid-write.
    class _Bad:
        pass

    ok = asset_utils.save_project_data(target, {"bad": _Bad()})
    assert ok is False
    # The original file must be intact (atomic write never touched it).
    assert json.loads(target.read_text(encoding="utf-8")) == {"original": True}
    leftovers = [p for p in tmp_path.iterdir() if ".tmp" in p.name]
    assert leftovers == []


# --------------------------------------------------------------------------
# Qt-dependent tests
# --------------------------------------------------------------------------

pytestmark = []  # module-level tests above are pure


@pytest.fixture(scope="module")
def _qapp():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@skip_without_pyside6
def test_imported_asset_uses_palette_foreground(_qapp):  # L33
    from PySide6.QtCore import Qt
    from widgets.asset_tree.asset_tree_item import AssetTreeItem
    item = AssetTreeItem(asset_type="sounds", asset_name="snd",
                         asset_data={"imported": True})
    # No explicit foreground brush -> default (NoBrush), so the theme palette
    # text color applies (was hardcoded black).
    assert item.foreground(0).style() == Qt.BrushStyle.NoBrush


@skip_without_pyside6
def test_tutorial_open_links_disabled(_qapp):  # L35
    from widgets.tutorial_panel import TutorialPanel
    panel = TutorialPanel()
    assert panel.content_browser.openLinks() is False
    assert panel.content_browser.openExternalLinks() is False
