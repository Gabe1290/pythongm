"""utils/asset_trash.py — the soft-delete mechanism settled on for the
shared "bulk-delete-undo" design question (docs/ASSET_MANAGER_PLAN.md /
docs/CLEAN_PROJECT_PLAN.md Tier 3). Pure file/manifest logic, no Qt.
"""
import json
from pathlib import Path

import pytest

from utils.asset_trash import trash_asset, list_trash, restore_asset, empty_trash


@pytest.fixture
def project_dir(tmp_path):
    (tmp_path / "sprites").mkdir()
    (tmp_path / "thumbnails").mkdir()
    (tmp_path / "objects").mkdir()
    return tmp_path


def test_trash_moves_main_file_and_records_manifest(project_dir):
    sprite_file = project_dir / "sprites" / "spr_hero.png"
    sprite_file.write_bytes(b"fake png data")
    asset_data = {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}

    entry_id = trash_asset(project_dir, "sprites", "spr_hero", asset_data)

    assert not sprite_file.exists()
    entries = list_trash(project_dir)
    assert len(entries) == 1
    assert entries[0]["id"] == entry_id
    assert entries[0]["asset_type"] == "sprites"
    assert entries[0]["asset_name"] == "spr_hero"
    assert entries[0]["asset_data"] == asset_data
    assert entries[0]["files"]["main"] == "sprites/spr_hero.png"


def test_trash_moves_thumbnail_and_side_file_too(project_dir):
    (project_dir / "sprites" / "spr_hero.png").write_bytes(b"png")
    (project_dir / "thumbnails" / "spr_hero_thumb.png").write_bytes(b"thumb")
    (project_dir / "objects" / "obj_a.json").write_text('{"events": {}}')
    asset_data = {"name": "obj_a", "sprite": "spr_hero"}

    entry_id = trash_asset(project_dir, "objects", "obj_a", asset_data,
                            side_file_rel="objects/obj_a.json")

    assert not (project_dir / "objects" / "obj_a.json").exists()
    entries = list_trash(project_dir)
    assert entries[0]["files"]["side_file"] == "objects/obj_a.json"


def test_trash_missing_file_does_not_crash(project_dir):
    # Some assets (a room referenced only through project.json + side
    # file) have no "main" physical file at all.
    asset_data = {"name": "obj_no_file"}
    entry_id = trash_asset(project_dir, "objects", "obj_no_file", asset_data)
    entries = list_trash(project_dir)
    assert entries[0]["files"] == {}
    assert entry_id


def test_list_trash_newest_first(project_dir):
    trash_asset(project_dir, "sprites", "spr_1", {"name": "spr_1"})
    trash_asset(project_dir, "sprites", "spr_2", {"name": "spr_2"})
    entries = list_trash(project_dir)
    assert [e["asset_name"] for e in entries] == ["spr_2", "spr_1"]


def test_restore_moves_files_back_and_returns_asset_data(project_dir):
    sprite_file = project_dir / "sprites" / "spr_hero.png"
    sprite_file.write_bytes(b"original bytes")
    asset_data = {"name": "spr_hero", "file_path": "sprites/spr_hero.png", "width": 32}

    entry_id = trash_asset(project_dir, "sprites", "spr_hero", asset_data)
    assert not sprite_file.exists()

    restored = restore_asset(project_dir, entry_id)

    assert restored == asset_data
    assert sprite_file.exists()
    assert sprite_file.read_bytes() == b"original bytes"
    # Restoring removes the trash entry.
    assert list_trash(project_dir) == []


def test_restore_refuses_on_name_collision(project_dir):
    sprite_file = project_dir / "sprites" / "spr_hero.png"
    sprite_file.write_bytes(b"original")
    asset_data = {"name": "spr_hero", "file_path": "sprites/spr_hero.png"}
    entry_id = trash_asset(project_dir, "sprites", "spr_hero", asset_data)

    # A new asset was created at the same path after the delete.
    sprite_file.write_bytes(b"a different, newer sprite")

    restored = restore_asset(project_dir, entry_id)

    assert restored is None
    # Nothing was overwritten, and the trash entry survives for a later retry.
    assert sprite_file.read_bytes() == b"a different, newer sprite"
    assert len(list_trash(project_dir)) == 1


def test_restore_unknown_id_returns_none(project_dir):
    assert restore_asset(project_dir, "does-not-exist") is None


def test_empty_trash_one_entry(project_dir):
    (project_dir / "sprites" / "spr_1.png").write_bytes(b"a")
    (project_dir / "sprites" / "spr_2.png").write_bytes(b"b")
    id1 = trash_asset(project_dir, "sprites", "spr_1", {"name": "spr_1", "file_path": "sprites/spr_1.png"})
    id2 = trash_asset(project_dir, "sprites", "spr_2", {"name": "spr_2", "file_path": "sprites/spr_2.png"})

    removed = empty_trash(project_dir, id1)

    assert removed == 1
    remaining = list_trash(project_dir)
    assert len(remaining) == 1
    assert remaining[0]["id"] == id2
    # The physical trash files for id1 are gone permanently.
    assert not (project_dir / ".trash" / "sprites" / id1).exists()


def test_empty_trash_all_entries(project_dir):
    trash_asset(project_dir, "sprites", "spr_1", {"name": "spr_1"})
    trash_asset(project_dir, "sprites", "spr_2", {"name": "spr_2"})

    removed = empty_trash(project_dir)

    assert removed == 2
    assert list_trash(project_dir) == []


def test_empty_trash_on_empty_trash_is_a_noop(project_dir):
    assert empty_trash(project_dir) == 0


def test_manifest_survives_a_reload(project_dir):
    entry_id = trash_asset(project_dir, "sprites", "spr_hero", {"name": "spr_hero"})
    # Simulate a fresh process reading the manifest back from disk.
    manifest_path = project_dir / ".trash" / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["id"] == entry_id


def test_cleared_references_recorded_but_not_acted_on(project_dir):
    entry_id = trash_asset(
        project_dir, "sprites", "spr_hero", {"name": "spr_hero"},
        cleared_references=[{"object": "obj_player", "field": "sprite"}])
    entries = list_trash(project_dir)
    assert entries[0]["cleared_references"] == [{"object": "obj_player", "field": "sprite"}]
