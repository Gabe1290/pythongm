"""Regression test for orphaned external asset files on delete/rename (M59,
M2 docs/FULL_AUDIT_2026-09-07.md).

Rooms/objects/playgrounds/sprites store their payload in <type>/<name>.json
side files that file_path doesn't reference. Deleting/renaming the asset must
remove/move that side file, else the orphan resurrects the dead asset's data
into a future asset reusing the name. H3 covered rooms/objects; M59 added
playgrounds; M2 adds sprites (rename_asset's side-file-carry tuple had
"rooms"/"objects"/"playgrounds" but not "sprites", even though delete_asset
already handled all four -- a renamed sprite left sprites/<old>.json behind,
and a future sprite reusing that name would silently inherit its stale
frame_width/precise/speed).
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


@pytest.mark.parametrize("asset_type", ["rooms", "objects", "playgrounds", "sprites"])
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


def test_sprite_rename_moves_json_side_file_alongside_png(_qapp, tmp_path):
    """Sprites are the one asset_type here with a REAL main file (the PNG)
    distinct from the JSON side file, so this needs its own setup rather
    than the shared parametrize above: rename_asset's "find the main file
    by conventional <type>/<old_name>.* layout" fallback (used when no
    file_path is recorded) matches ANY file whose stem is old_name --
    with only a lone old.json present (as the shared parametrize's generic
    fixture would give it), that fallback renames the .json itself via a
    completely different code path, and the test would pass even without
    the side-file-carry fix this covers. Giving the sprite a real,
    recorded file_path for its .png removes that ambiguity: the fallback
    is never consulted, so old.json can only move via the dedicated
    side-file-carry block (M2, docs/FULL_AUDIT_2026-09-07.md).
    """
    am = _manager(tmp_path)
    sprites_dir = tmp_path / "sprites"
    sprites_dir.mkdir(exist_ok=True)  # AssetManager.__init__ already made it
    (sprites_dir / "old.png").write_bytes(b"\x89PNG\r\n")
    am.assets_cache = {"sprites": {
        "old": {"name": "old", "file_path": "sprites/old.png"},
    }}
    old_side = _side_file(tmp_path, "sprites", "old", '{"frame_width": 32}')

    assert am.rename_asset("sprites", "old", "new") is True

    # The main file moved via the ordinary file_path-based path.
    assert not (sprites_dir / "old.png").exists()
    assert (sprites_dir / "new.png").exists()

    # The JSON side file must have moved too -- this is the M2 fix.
    assert not old_side.exists(), (
        "sprites/old.json orphan left behind: a future sprite named "
        "'new' would silently inherit its stale metadata")
    new_side = sprites_dir / "new.json"
    assert new_side.exists()
    assert new_side.read_text(encoding="utf-8") == '{"frame_width": 32}'
