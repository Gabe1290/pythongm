#!/usr/bin/env python3
"""Regression: renaming a sprite must keep its tree thumbnail.

A sprite created/imported this session can carry an empty or stale
``file_path`` in the asset-manager cache while its PNG actually sits at the
conventional ``sprites/<name>.png`` location. Two defects then combined to
blank the tree miniature on rename:

  * ``AssetManager.rename_asset`` only renamed the on-disk file (and updated
    ``file_path``) when ``file_path`` was set *and* the file existed there;
    otherwise the renamed asset kept a stale/empty path and no file moved.
  * ``AssetOperations.refresh_asset_item_after_rename``'s fallback built a
    bogus ``<project>/assets/<folder>/<name>.png`` path (there is no
    ``assets/`` subdirectory in this layout), so it could never recover, and
    the stale-``file_path`` case never even reached it.

Both are now resilient: the file is located by the conventional
``<type>/<old_name>.*`` layout, and the thumbnail refresh always also tries
``<folder>/<new_name>.<ext>`` derived from the new name.
"""

import os
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
from PySide6.QtGui import QImage

import widgets.asset_tree.asset_operations as asset_operations
from core.asset_manager import AssetManager
from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
from widgets.asset_tree.asset_tree_item import AssetTreeItem
from widgets.asset_tree.asset_operations import AssetOperations


def _app():
    return QApplication.instance() or QApplication([])


def _write_png(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    QImage(16, 16, QImage.Format_ARGB32).save(str(path), "PNG")


def test_rename_moves_file_when_cached_filepath_empty():
    """AssetManager.rename_asset renames the on-disk PNG and sets the new
    file_path even when the cached file_path is empty (created-this-session)."""
    _app()
    proj = Path(tempfile.mkdtemp())
    _write_png(proj / "sprites" / "door.png")

    am = AssetManager(proj)
    am.assets_cache = {
        "sprites": {
            "door": {"name": "door", "asset_type": "sprite",
                     "imported": True, "file_path": ""},
        }
    }

    assert am.rename_asset("sprites", "door", "gate") is True

    data = am.get_asset("sprites", "gate")
    assert data["file_path"] == "sprites/gate.png"
    assert (proj / "sprites" / "gate.png").exists()
    assert not (proj / "sprites" / "door.png").exists()


def test_refresh_recovers_thumbnail_with_stale_filepath():
    """The thumbnail refresh resolves the new-name file even when asset_data
    still carries a stale (pre-rename) file_path, and heals file_path."""
    _app()
    proj = Path(tempfile.mkdtemp())
    _write_png(proj / "sprites" / "newname.png")

    tree = AssetTreeWidget()
    tree.project_path = str(proj)
    ops = AssetOperations(tree)

    item = AssetTreeItem(None, "sprites", "newname", {
        "name": "newname", "asset_type": "sprite", "imported": True,
        "file_path": "sprites/oldname.png",  # stale: no such file on disk
    })
    tree.addTopLevelItem(item)

    ops.refresh_asset_item_after_rename(item, "newname")

    assert not item.icon(0).isNull()
    assert item.text(0) == "newname"
    assert item.asset_data["file_path"] == "sprites/newname.png"


def test_refresh_recovers_thumbnail_with_empty_filepath():
    """Same recovery when file_path is empty rather than stale."""
    _app()
    proj = Path(tempfile.mkdtemp())
    _write_png(proj / "sprites" / "newname.png")

    tree = AssetTreeWidget()
    tree.project_path = str(proj)
    ops = AssetOperations(tree)

    item = AssetTreeItem(None, "sprites", "newname", {
        "name": "newname", "asset_type": "sprite", "imported": True,
        "file_path": "",
    })
    tree.addTopLevelItem(item)

    ops.refresh_asset_item_after_rename(item, "newname")

    assert not item.icon(0).isNull()
    assert item.asset_data["file_path"] == "sprites/newname.png"


def test_delete_open_asset_closes_editor_with_composite_key(monkeypatch):
    """Deleting an asset that is open in an editor must close it via the L5
    composite open-editor key. A stale two-arg call
    (close_editor_by_name(name, category)) raised TypeError and aborted the
    delete with a traceback."""
    _app()

    class StubIDE(QWidget):
        def __init__(self):
            super().__init__()
            self.calls = []
            self.open_editors = {"sprites:player": object()}

        def _editor_key(self, category, name):
            return f"{category}:{name}"

        def close_editor_by_name(self, key):  # single positional arg
            self.calls.append(key)

    ide = StubIDE()
    tree = AssetTreeWidget()
    tree.setParent(ide)
    tree.project_path = tempfile.mkdtemp()
    item = AssetTreeItem(None, "sprites", "player",
                         {"name": "player", "asset_type": "sprite", "imported": True})
    tree.addTopLevelItem(item)

    # Cancel the confirmation dialog; the close-editor logic runs before it.
    monkeypatch.setattr(asset_operations.QMessageBox, "question",
                        staticmethod(lambda *a, **k: QMessageBox.No))

    tree.operations.delete_asset(item)

    assert ide.calls == ["sprites:player"]
