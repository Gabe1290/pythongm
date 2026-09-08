"""L16, docs/FULL_AUDIT_2026-09-07.md: duplicate-asset path doesn't copy
room/object/sprite side files.

AssetOperations.duplicate_asset (widgets/asset_tree/asset_operations.py,
the only reachable implementation -- the "Duplicate" context-menu action
wires to this one, not core/asset_manager.py's separate same-named
method, which no UI path calls at all) copied `file_path` and
`thumbnail` only. Rooms/objects/playgrounds/sprites keep their real
payload in a <type>/<name>.json side file, not embedded in project.json's
own entry (see tests/test_asset_side_file_cleanup.py's delete/rename
coverage of the same convention) -- so duplicating one of these left the
new copy with only the in-memory tree-item snapshot, no real side file
at all.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _tree_stub(project_path):
    calls = {"add_asset": [], "emitted": []}
    tree = SimpleNamespace(
        project_path=str(project_path),
        parent=lambda: None,
        add_asset=lambda *a: calls["add_asset"].append(a),
        asset_imported=SimpleNamespace(emit=lambda *a: calls["emitted"].append(a)),
    )
    return tree, calls


def _seed_project(tmp_path, asset_category, asset_name, side_file_content):
    type_dir = tmp_path / asset_category
    type_dir.mkdir(parents=True, exist_ok=True)
    (type_dir / f"{asset_name}.json").write_text(
        json.dumps(side_file_content), encoding="utf-8")
    project_data = {
        "assets": {asset_category: {asset_name: {"name": asset_name}}}
    }
    (tmp_path / "project.json").write_text(json.dumps(project_data), encoding="utf-8")


@pytest.mark.parametrize("asset_category", ["rooms", "objects", "playgrounds"])
def test_duplicate_copies_the_side_file(_qapp, tmp_path, asset_category):
    from widgets.asset_tree.asset_operations import AssetOperations
    from widgets.asset_tree.asset_tree_item import AssetTreeItem

    side_content = {"real_payload": "only lives in the side file", "n": 42}
    _seed_project(tmp_path, asset_category, "thing_original", side_content)

    tree, _calls = _tree_stub(tmp_path)
    ops = AssetOperations(tree)
    item = AssetTreeItem(None, asset_type=asset_category, asset_name="thing_original",
                          asset_data={"name": "thing_original"})

    assert ops.duplicate_asset(item) is True

    new_side = tmp_path / asset_category / "thing_original_copy.json"
    assert new_side.exists(), (
        f"{asset_category} duplicate must copy the <type>/<name>.json side file")
    assert json.loads(new_side.read_text(encoding="utf-8")) == side_content

    # The old side file must survive untouched (a copy, not a move).
    old_side = tmp_path / asset_category / "thing_original.json"
    assert old_side.exists()
    assert json.loads(old_side.read_text(encoding="utf-8")) == side_content


def test_duplicate_sprite_copies_the_json_side_file_alongside_the_png(_qapp, tmp_path):
    from widgets.asset_tree.asset_operations import AssetOperations
    from widgets.asset_tree.asset_tree_item import AssetTreeItem

    sprites_dir = tmp_path / "sprites"
    sprites_dir.mkdir()
    (sprites_dir / "spr_original.png").write_bytes(b"\x89PNG\r\n")
    side_content = {"frame_width": 32, "precise": True}
    (sprites_dir / "spr_original.json").write_text(json.dumps(side_content), encoding="utf-8")
    project_data = {
        "assets": {"sprites": {"spr_original": {
            "name": "spr_original", "file_path": "sprites/spr_original.png",
        }}}
    }
    (tmp_path / "project.json").write_text(json.dumps(project_data), encoding="utf-8")

    tree, _calls = _tree_stub(tmp_path)
    ops = AssetOperations(tree)
    item = AssetTreeItem(None, asset_type="sprites", asset_name="spr_original",
                          asset_data={"name": "spr_original", "file_path": "sprites/spr_original.png"})

    assert ops.duplicate_asset(item) is True

    assert (sprites_dir / "spr_original_copy.png").exists()
    new_side = sprites_dir / "spr_original_copy.json"
    assert new_side.exists()
    assert json.loads(new_side.read_text(encoding="utf-8")) == side_content


def test_duplicate_asset_with_no_side_file_still_works(_qapp, tmp_path):
    """A plain sound (never has a side file) must not break."""
    from widgets.asset_tree.asset_operations import AssetOperations
    from widgets.asset_tree.asset_tree_item import AssetTreeItem

    project_data = {"assets": {"sounds": {"snd_beep": {"name": "snd_beep"}}}}
    (tmp_path / "project.json").write_text(json.dumps(project_data), encoding="utf-8")

    tree, _calls = _tree_stub(tmp_path)
    ops = AssetOperations(tree)
    item = AssetTreeItem(None, asset_type="sounds", asset_name="snd_beep",
                          asset_data={"name": "snd_beep"})

    assert ops.duplicate_asset(item) is True
