"""Regression tests for the asset_operations.py legacy-fallback delete path.

Covers:
  M59 — deleting a room/object must also remove its <type>/<name>.json side
        file, or the orphan resurrects the dead asset's instances when the
        name is reused.
  L32 — deleting a sprite must clear the reference inside objects/<obj>.json,
        not just in project.json/cache, or the forced reload's file-precedence
        merge restores the stale (now-deleted) sprite name.

These exercise AssetOperations.remove_asset_from_project's *legacy fallback*
(no project_manager attached), which is pure file I/O and needs no Qt widgets.
"""
import json
from pathlib import Path

from widgets.asset_tree.asset_operations import AssetOperations


class _FakeTree:
    """Minimal stand-in for the asset tree the legacy fallback reads."""
    def __init__(self, project_path):
        self.project_path = str(project_path)
        # No project_manager -> remove_asset_from_project takes the legacy
        # disk-roundtrip fallback (the path the findings target).
        self.project_manager = None

    def parent(self):
        # Walked to find an asset_manager; None short-circuits that traversal.
        return None


def _write_project(tmp_path, assets):
    project_file = tmp_path / "project.json"
    project_file.write_text(json.dumps({"assets": assets}), encoding="utf-8")
    return project_file


def test_delete_room_removes_side_file(tmp_path):
    """M59: rooms/<name>.json is unlinked when the room is deleted."""
    _write_project(tmp_path, {"rooms": {"level2": {"name": "level2"}}})
    rooms_dir = tmp_path / "rooms"
    rooms_dir.mkdir()
    side_file = rooms_dir / "level2.json"
    side_file.write_text(json.dumps({
        "name": "level2",
        "instances": [{"object_name": "obj_wall", "x": 32, "y": 64}],
    }), encoding="utf-8")

    ops = AssetOperations(_FakeTree(tmp_path))
    assert ops.remove_asset_from_project("rooms", "level2") is True

    assert not side_file.exists(), "orphan rooms/level2.json must be deleted"
    data = json.loads((tmp_path / "project.json").read_text(encoding="utf-8"))
    assert "level2" not in data["assets"]["rooms"]


def test_delete_object_removes_side_file(tmp_path):
    """M59 (object variant): objects/<name>.json is unlinked on delete."""
    _write_project(tmp_path, {"objects": {"obj_old": {"name": "obj_old"}}})
    objects_dir = tmp_path / "objects"
    objects_dir.mkdir()
    side_file = objects_dir / "obj_old.json"
    side_file.write_text(json.dumps({"name": "obj_old", "events": {}}),
                         encoding="utf-8")

    ops = AssetOperations(_FakeTree(tmp_path))
    assert ops.remove_asset_from_project("objects", "obj_old") is True

    assert not side_file.exists()


def test_delete_sprite_clears_reference_in_object_side_file(tmp_path):
    """L32: objects/<obj>.json sprite reference is cleared, not just project.json."""
    _write_project(tmp_path, {
        "sprites": {"spr_old": {"name": "spr_old", "file_path": "sprites/spr_old.png"}},
        "objects": {"obj_player": {"name": "obj_player", "sprite": "spr_old"}},
    })
    # The sprite's image (so the unlink branch runs, like a real project).
    sprites_dir = tmp_path / "sprites"
    sprites_dir.mkdir()
    (sprites_dir / "spr_old.png").write_bytes(b"\x89PNG\r\n")

    objects_dir = tmp_path / "objects"
    objects_dir.mkdir()
    obj_side = objects_dir / "obj_player.json"
    obj_side.write_text(json.dumps({"name": "obj_player", "sprite": "spr_old"}),
                        encoding="utf-8")

    ops = AssetOperations(_FakeTree(tmp_path))
    assert ops.remove_asset_from_project("sprites", "spr_old") is True

    # project.json reference cleared (pre-existing behaviour)
    data = json.loads((tmp_path / "project.json").read_text(encoding="utf-8"))
    assert data["assets"]["objects"]["obj_player"]["sprite"] == ""
    # NEW: the side file's stale reference is cleared too, so the forced
    # reload's file-precedence merge can't restore "spr_old".
    side = json.loads(obj_side.read_text(encoding="utf-8"))
    assert side["sprite"] == "", "objects/obj_player.json must drop the deleted sprite"


def test_delete_sprite_leaves_unrelated_object_side_file_untouched(tmp_path):
    """L32: only objects that actually referenced the sprite get rewritten."""
    _write_project(tmp_path, {
        "sprites": {"spr_old": {"name": "spr_old"}},
        "objects": {
            "obj_player": {"name": "obj_player", "sprite": "spr_old"},
            "obj_coin": {"name": "obj_coin", "sprite": "spr_coin"},
        },
    })
    objects_dir = tmp_path / "objects"
    objects_dir.mkdir()
    (objects_dir / "obj_player.json").write_text(
        json.dumps({"name": "obj_player", "sprite": "spr_old"}), encoding="utf-8")
    coin_side = objects_dir / "obj_coin.json"
    coin_side.write_text(
        json.dumps({"name": "obj_coin", "sprite": "spr_coin"}), encoding="utf-8")

    ops = AssetOperations(_FakeTree(tmp_path))
    assert ops.remove_asset_from_project("sprites", "spr_old") is True

    coin = json.loads(coin_side.read_text(encoding="utf-8"))
    assert coin["sprite"] == "spr_coin", "unrelated object must keep its sprite"


def test_delete_room_without_side_file_still_succeeds(tmp_path):
    """M59: absent side file is a no-op, not an error."""
    _write_project(tmp_path, {"rooms": {"level1": {"name": "level1"}}})
    # No rooms/ dir at all.
    ops = AssetOperations(_FakeTree(tmp_path))
    assert ops.remove_asset_from_project("rooms", "level1") is True
    data = json.loads((tmp_path / "project.json").read_text(encoding="utf-8"))
    assert "level1" not in data["assets"]["rooms"]
