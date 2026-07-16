"""Regression test locking in the current state of GMK import for
treasure/maze_4 (docs/GMK_IMPORTER_HARDENING_PLAN.md, Tier 3 item 8).

Both samples were dropped from the bundled set in rc.12 after user
testing surfaced action-parameter/mapping bugs; their .gmk sources were
recovered from git history 2026-07-16 (samples/treasure.gmk,
samples/maze_4.gmk -- see that commit) specifically to re-run the
importer against them. A fresh import of both now produces zero
"Unmapped GM action" placeholder comments and the expected asset counts
-- this test pins that state so a future importer regression (e.g. a
GM_ACTION_MAP entry accidentally removed) surfaces here instead of
silently reintroducing the exact class of bug that got these samples
dropped in the first place.

This is NOT a claim that either sample is fully correct or ready to
reintroduce -- only that the importer no longer falls through to unmapped
stubs, and every object.sprite / room-instance.object / background_image
reference actually resolves to a real asset, for anything either
project's data touches. Full re-validation (visual playtest, a real
test-game run) is still open, per the plan doc.
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

from importers.gmk_importer import import_gmk_detailed  # noqa: E402


def _all_action_dicts(events: dict):
    """Yield every action dict nested anywhere under an object's `events`
    (then/else branches, repeat/block bodies, sub_actions, ...)."""
    def walk(node):
        if isinstance(node, dict):
            if "action" in node:
                yield node
            for value in node.values():
                yield from walk(value)
        elif isinstance(node, list):
            for item in node:
                yield from walk(item)
    yield from walk(events)


def _import(gmk_name, tmp_path):
    gmk_path = REPO_ROOT / "samples" / gmk_name
    assert gmk_path.exists(), f"{gmk_path} missing (recovered from git history in c6682d9)"
    out_dir = tmp_path / "reimport"
    import_gmk_detailed(str(gmk_path), str(out_dir))
    return out_dir


def _no_unmapped_actions(out_dir):
    unmapped = []
    for obj_file in sorted((out_dir / "objects").glob("*.json")):
        data = json.loads(obj_file.read_text(encoding="utf-8"))
        for action in _all_action_dicts(data.get("events", {})):
            if action.get("action") == "comment" and "Unmapped GM action" in str(
                    action.get("parameters", {}).get("text", "")):
                unmapped.append((obj_file.name, action))
    return unmapped


def _dangling_asset_references(out_dir):
    """Every object.sprite / room-instance.object_name / room
    background_image reference must resolve to a real asset name --
    catches the "silently-renamed sprite/object references on case or
    whitespace conflicts" category TODO.md's GMK hardening notes flag as
    a plausible importer failure mode, distinct from the unmapped-action
    check above (a reference can be present and well-formed but still
    point at nothing)."""
    project = json.loads((out_dir / "project.json").read_text(encoding="utf-8"))
    assets = project["assets"]
    object_names = set(assets.get("objects", {}).keys())
    sprite_names = set(assets.get("sprites", {}).keys())
    background_names = set(assets.get("backgrounds", {}).keys())

    dangling = []
    for obj_name, obj_data in assets.get("objects", {}).items():
        sprite = obj_data.get("sprite")
        if sprite and sprite != "<self>" and sprite not in sprite_names:
            dangling.append(("object.sprite", obj_name, sprite))

    for room_name, room_data in assets.get("rooms", {}).items():
        external = room_data.get("_external_file")
        full_room = json.loads((out_dir / external).read_text(encoding="utf-8")) \
            if external else room_data
        for inst in full_room.get("instances", []):
            obj_ref = inst.get("object_name") or inst.get("object")
            if obj_ref and obj_ref not in object_names:
                dangling.append(("room.instance.object", room_name, obj_ref))
        bg = full_room.get("background_image")
        if bg and bg not in background_names:
            dangling.append(("room.background_image", room_name, bg))
        for layer in full_room.get("backgrounds", []):
            layer_bg = layer.get("background_image")
            if layer_bg and layer_bg not in background_names:
                dangling.append(("room.backgrounds[].background_image", room_name, layer_bg))
    return dangling


class TestTreasureImport:
    def test_imports_without_raising(self, tmp_path):
        _import("treasure.gmk", tmp_path)

    def test_no_unmapped_action_stubs(self, tmp_path):
        out_dir = _import("treasure.gmk", tmp_path)
        assert _no_unmapped_actions(out_dir) == []

    def test_expected_asset_counts(self, tmp_path):
        out_dir = _import("treasure.gmk", tmp_path)
        project = json.loads((out_dir / "project.json").read_text(encoding="utf-8"))
        assets = project["assets"]
        assert len(assets["objects"]) == 7
        assert len(assets["rooms"]) == 4
        assert len(assets["sprites"]) == 10
        assert len(assets["sounds"]) == 6
        assert len(assets["scripts"]) == 1

    def test_monster_script_calls_survive_as_execute_script(self, tmp_path):
        """treasure is the one sample using project-level scripts
        (adapt_direction) -- confirm the importer still emits
        execute_script rather than inlining or dropping the call."""
        out_dir = _import("treasure.gmk", tmp_path)
        data = json.loads((out_dir / "objects" / "monster.json").read_text(encoding="utf-8"))
        script_calls = [a for a in _all_action_dicts(data.get("events", {}))
                         if a.get("action") == "execute_script"]
        assert script_calls
        assert all(a["parameters"].get("script") == "adapt_direction" for a in script_calls)

    def test_no_dangling_asset_references(self, tmp_path):
        out_dir = _import("treasure.gmk", tmp_path)
        assert _dangling_asset_references(out_dir) == []


class TestMaze4Import:
    def test_imports_without_raising(self, tmp_path):
        _import("maze_4.gmk", tmp_path)

    def test_no_unmapped_action_stubs(self, tmp_path):
        out_dir = _import("maze_4.gmk", tmp_path)
        assert _no_unmapped_actions(out_dir) == []

    def test_expected_asset_counts(self, tmp_path):
        out_dir = _import("maze_4.gmk", tmp_path)
        project = json.loads((out_dir / "project.json").read_text(encoding="utf-8"))
        assets = project["assets"]
        assert len(assets["objects"]) == 24
        assert len(assets["rooms"]) == 21
        assert len(assets["sprites"]) == 24
        assert len(assets["sounds"]) == 10

    def test_no_dangling_asset_references(self, tmp_path):
        out_dir = _import("maze_4.gmk", tmp_path)
        assert _dangling_asset_references(out_dir) == []
