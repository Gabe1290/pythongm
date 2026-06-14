"""Regression test for orphaned external asset files on delete/rename (M59).

Rooms/objects/playgrounds store their payload in <type>/<name>.json side files
that file_path doesn't reference. Deleting/renaming the asset must remove/move
that side file, else the orphan resurrects the dead asset's data into a future
asset reusing the name. H3 covered rooms/objects; M59 adds playgrounds.
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


def _manager(tmp_path):
    from core.asset_manager import AssetManager
    am = AssetManager(project_directory=tmp_path)
    return am


def _side_file(tmp_path, asset_type, name, content="{}"):
    d = tmp_path / asset_type
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{name}.json"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.mark.parametrize("asset_type", ["rooms", "objects", "playgrounds"])
def test_delete_removes_side_file(_qapp, tmp_path, asset_type):
    am = _manager(tmp_path)
    am.assets_cache = {asset_type: {"a1": {"name": "a1"}}}
    side = _side_file(tmp_path, asset_type, "a1")
    assert side.exists()

    assert am.delete_asset(asset_type, "a1") is True
    assert not side.exists(), f"{asset_type} side file must be deleted"


@pytest.mark.parametrize("asset_type", ["rooms", "objects", "playgrounds"])
def test_rename_moves_side_file(_qapp, tmp_path, asset_type):
    am = _manager(tmp_path)
    am.assets_cache = {asset_type: {"old": {"name": "old"}}}
    old_side = _side_file(tmp_path, asset_type, "old", '{"k": 1}')

    assert am.rename_asset(asset_type, "old", "new") is True
    assert not old_side.exists()
    new_side = tmp_path / asset_type / "new.json"
    assert new_side.exists()
    assert new_side.read_text(encoding="utf-8") == '{"k": 1}'
