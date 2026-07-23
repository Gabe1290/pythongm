"""Warn when a project needs a DISABLED extension (parts a + b).

Now that the 2.5D raycast feature is an extension that can be turned off, a
project using `enable_raycast_view` (etc.) with the extension disabled would
otherwise silently render top-down with only a console log. This adds:

  (a) a `provides_actions` list in each extension's manifest — readable WITHOUT
      loading the extension, so a disabled extension's actions are still known;
  (b) a load-time scan (`missing_extensions_for_project`) the IDE surfaces as a
      warning naming the exact disabled extension.

A project.json that uses no such action — or never mentions an extension — is
fine: the scan returns [].
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from events import plugin_loader as pl  # noqa: E402


# --- (a) manifest declares the actions it owns -------------------------------

def test_raycast_manifest_declares_its_actions():
    manifest = json.loads(
        (REPO_ROOT / "extensions" / "raycast_2_5d" / "extension.json").read_text(encoding="utf-8"))
    assert set(manifest.get("provides_actions", [])) == {
        "enable_raycast_view", "set_facing_angle", "draw_minimap", "draw_doom_hud"}


def test_list_available_extensions_exposes_provides_actions():
    exts = {e["folder"]: e for e in pl.list_available_extensions()}
    assert "enable_raycast_view" in exts["raycast_2_5d"]["provides_actions"]


# --- collect_project_action_names --------------------------------------------

def test_collects_action_names_including_nested():
    project = {"assets": {"objects": {
        "obj_a": {"events": {
            "create": {"actions": [
                {"action": "enable_raycast_view", "parameters": {}},
                {"action": "if_condition", "parameters": {
                    "then_actions": [{"action": "draw_minimap"}],
                    "else_actions": [{"action": "set_facing_angle"}]}},
            ]},
        }},
        "obj_b": {"events": {"draw": {"actions": [{"action": "draw_doom_hud"}]}}},
    }}}
    names = pl.collect_project_action_names(project)
    assert names == {"enable_raycast_view", "if_condition", "draw_minimap",
                     "set_facing_angle", "draw_doom_hud"}


def test_collect_is_tolerant_of_empty_or_odd_data():
    assert pl.collect_project_action_names({}) == set()
    assert pl.collect_project_action_names(None) == set()
    assert pl.collect_project_action_names({"assets": {"objects": None}}) == set()


# --- (b) missing_extensions_for_project --------------------------------------

_PROJECT = {"assets": {"objects": {
    "obj_p": {"events": {"create": {"actions": [{"action": "enable_raycast_view"}]}}}}}}


def _fake_exts(enabled):
    return [{"folder": "raycast_2_5d", "name": "2.5D Raycast View",
             "enabled": enabled,
             "provides_actions": ["enable_raycast_view", "set_facing_angle",
                                  "draw_minimap", "draw_doom_hud"]}]


def test_flags_disabled_extension_a_project_uses(monkeypatch):
    monkeypatch.setattr(pl, "list_available_extensions", lambda: _fake_exts(False))
    missing = pl.missing_extensions_for_project(_PROJECT)
    assert missing == [{"folder": "raycast_2_5d", "name": "2.5D Raycast View",
                        "actions": ["enable_raycast_view"]}]


def test_enabled_extension_is_not_flagged(monkeypatch):
    monkeypatch.setattr(pl, "list_available_extensions", lambda: _fake_exts(True))
    assert pl.missing_extensions_for_project(_PROJECT) == []


def test_project_not_using_the_action_is_not_flagged(monkeypatch):
    monkeypatch.setattr(pl, "list_available_extensions", lambda: _fake_exts(False))
    other = {"assets": {"objects": {
        "o": {"events": {"create": {"actions": [{"action": "set_hspeed"}]}}}}}}
    assert pl.missing_extensions_for_project(other) == []


def test_empty_project_and_missing_field_are_fine(monkeypatch):
    monkeypatch.setattr(pl, "list_available_extensions", lambda: _fake_exts(False))
    assert pl.missing_extensions_for_project({}) == []
    assert pl.missing_extensions_for_project({"assets": {"objects": {}}}) == []


# --- (c) requires_extensions persisted on save -------------------------------

def test_required_extensions_derives_the_dependency():
    proj = {"assets": {"objects": {
        "obj_p": {"events": {"create": {"actions": [{"action": "enable_raycast_view"}]}}}}}}
    assert pl.required_extensions_for_project(proj) == ["raycast_2_5d"]
    # includes an ENABLED extension too — it's a dependency record, not a warning
    plain = {"assets": {"objects": {
        "o": {"events": {"create": {"actions": [{"action": "set_hspeed"}]}}}}}}
    assert pl.required_extensions_for_project(plain) == []
    assert pl.required_extensions_for_project({}) == []


def test_save_writes_requires_extensions_and_drops_it_when_stale():
    from core.project_manager import ProjectManager
    pm = ProjectManager.__new__(ProjectManager)   # bypass __init__/Qt

    # A project that uses a raycast action gets the field.
    pm.current_project_data = {"name": "p", "assets": {"objects": {
        "obj_p": {"events": {"create": {"actions": [{"action": "draw_minimap"}]}}}}, "rooms": {}}}
    assert pm._prepare_project_data_for_save().get("requires_extensions") == ["raycast_2_5d"]

    # A plain project omits it entirely (no littering).
    pm.current_project_data = {"name": "p", "assets": {"objects": {
        "o": {"events": {"create": {"actions": [{"action": "set_hspeed"}]}}}}, "rooms": {}}}
    assert "requires_extensions" not in pm._prepare_project_data_for_save()

    # A stale record (feature removed) is dropped on the next save.
    pm.current_project_data = {"name": "p", "requires_extensions": ["raycast_2_5d"],
                               "assets": {"objects": {
        "o": {"events": {"create": {"actions": [{"action": "set_hspeed"}]}}}}, "rooms": {}}}
    assert "requires_extensions" not in pm._prepare_project_data_for_save()


def test_real_raycast_sample_needs_the_extension_when_disabled(monkeypatch):
    """End-to-end against a real sample: raycast_1 uses enable_raycast_view, so
    it flags the raycast extension when that extension is turned off."""
    from utils.project_file_merge import merge_object_file
    sample = REPO_ROOT / "samples" / "raycast_1"
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    for name, obj in data.get("assets", {}).get("objects", {}).items():
        side = sample / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    monkeypatch.setattr(pl, "list_available_extensions", lambda: _fake_exts(False))
    missing = pl.missing_extensions_for_project(data)
    assert len(missing) == 1 and missing[0]["folder"] == "raycast_2_5d"
    assert "enable_raycast_view" in missing[0]["actions"]
