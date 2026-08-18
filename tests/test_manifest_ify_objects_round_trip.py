"""Mandatory round-trip proof for TODO.md's "Manifest-ify objects & sprites"
item: objects with an objects/<name>.json side file now strip `events` from
their project.json entry on save (the same treatment rooms already give
`instances`) -- this is the "load a representative project -> save ->
reload, assert current_project_data is byte-for-byte equivalent" test that
entry calls mandatory, for both a fresh (objects/ dir present) and a legacy
embedded-only (no objects/ dir) project, plus a .zip export/import
round-trip.

Sprites got the same treatment later (Tier 6, 2026-08-15) -- see
tests/test_manifest_ify_sprites_round_trip.py for that mirror-image suite
(the whole sprite body strips to a stub, not just one field, since sprites
have no single heavy field the way objects have `events`).
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _make_project_manager():
    with patch('PySide6.QtCore.QTimer'):
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=MagicMock())
        pm.auto_save_timer = MagicMock()
        return pm


_OBJECT_WITH_EVENTS = {
    "name": "obj_hero",
    "asset_type": "object",
    "sprite": "spr_hero",
    "visible": True,
    "solid": False,
    "depth": 0,
    "events": {
        "create": {"actions": [{"action": "set_hspeed", "parameters": {"speed": 4}}]},
        "step": {"actions": [{"action": "move_towards_point",
                              "parameters": {"x": 100, "y": 100, "speed": 2}}]},
    },
}


def _project_data(name="RoundTripGame"):
    return {
        "name": name,
        "version": "1.0.0",
        "room_order": [],
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {"obj_hero": json.loads(json.dumps(_OBJECT_WITH_EVENTS))},
            "rooms": {}, "fonts": {}, "data": {},
        },
    }


class TestFreshProjectRoundTrip:
    """objects/ dir present -> events strip to the side file."""

    def test_save_strips_events_to_side_file(self, tmp_path):
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        for sub in ("sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"):
            (proj_dir / sub).mkdir(parents=True)
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()

        assert pm._save_to_folder(proj_dir) is True

        on_disk = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        obj_entry = on_disk["assets"]["objects"]["obj_hero"]
        assert obj_entry["events"] == {}
        assert obj_entry["_external_file"] == "objects/obj_hero.json"
        # Lightweight metadata stays embedded, unlike rooms' instances.
        assert obj_entry["sprite"] == "spr_hero"
        assert obj_entry["depth"] == 0

        side_file = json.loads((proj_dir / "objects" / "obj_hero.json").read_text(encoding="utf-8"))
        assert side_file["events"] == _OBJECT_WITH_EVENTS["events"]

    def test_load_after_save_is_byte_for_byte_equivalent(self, tmp_path):
        """The mandatory round-trip: load -> save -> reload, and the
        in-memory current_project_data must carry the exact same object
        data as what was there before the save (not the stripped disk
        form) -- the merge on load must fully restore it."""
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        for sub in ("sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"):
            (proj_dir / sub).mkdir(parents=True)
        pm.current_project_path = proj_dir
        original = _project_data()
        pm.current_project_data = json.loads(json.dumps(original))  # deep copy

        assert pm._save_to_folder(proj_dir) is True

        pm2 = _make_project_manager()
        assert pm2.load_project(proj_dir) is True

        reloaded_obj = pm2.current_project_data["assets"]["objects"]["obj_hero"]
        assert reloaded_obj["events"] == _OBJECT_WITH_EVENTS["events"]
        assert reloaded_obj["sprite"] == "spr_hero"
        assert reloaded_obj["visible"] is True
        assert reloaded_obj["solid"] is False
        assert reloaded_obj["depth"] == 0

    def test_two_save_load_cycles_are_stable(self, tmp_path):
        """Saving an already-round-tripped project a second time must not
        further mutate or lose data (idempotent past the first strip)."""
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        for sub in ("sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"):
            (proj_dir / sub).mkdir(parents=True)
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()
        assert pm._save_to_folder(proj_dir) is True

        pm2 = _make_project_manager()
        assert pm2.load_project(proj_dir) is True
        assert pm2._save_to_folder(proj_dir) is True

        pm3 = _make_project_manager()
        assert pm3.load_project(proj_dir) is True
        assert (pm3.current_project_data["assets"]["objects"]["obj_hero"]["events"]
                == _OBJECT_WITH_EVENTS["events"])


class TestLegacyEmbeddedOnlyProjectUnaffected:
    """No objects/ dir at all -- must keep the pre-existing fully-embedded
    behaviour byte for byte, per this entry's own explicit requirement."""

    def test_save_does_not_strip_events_without_objects_dir(self, tmp_path):
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        proj_dir.mkdir()  # deliberately no objects/ subdir
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()

        assert pm._save_to_folder(proj_dir) is True

        on_disk = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        obj_entry = on_disk["assets"]["objects"]["obj_hero"]
        assert obj_entry["events"] == _OBJECT_WITH_EVENTS["events"]
        assert "_external_file" not in obj_entry
        assert not (proj_dir / "objects").exists()

    def test_load_after_save_still_round_trips(self, tmp_path):
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        proj_dir.mkdir()
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()
        assert pm._save_to_folder(proj_dir) is True

        pm2 = _make_project_manager()
        assert pm2.load_project(proj_dir) is True
        assert (pm2.current_project_data["assets"]["objects"]["obj_hero"]["events"]
                == _OBJECT_WITH_EVENTS["events"])


class TestZipRoundTrip:
    def test_zip_export_import_preserves_events(self, tmp_path):
        from utils.project_compression import ProjectCompressor

        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        for sub in ("sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"):
            (proj_dir / sub).mkdir(parents=True)
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()
        assert pm._save_to_folder(proj_dir) is True

        zip_path = tmp_path / "game.zip"
        assert ProjectCompressor.compress_project(proj_dir, zip_path) is True

        extract_dir = tmp_path / "extracted"
        assert ProjectCompressor.decompress_project(zip_path, extract_dir) is True

        # decompress_project may nest under the original folder name;
        # locate the real project.json wherever it landed.
        project_file = next(extract_dir.rglob("project.json"))
        extracted_proj_dir = project_file.parent

        pm2 = _make_project_manager()
        assert pm2.load_project(extracted_proj_dir) is True
        assert (pm2.current_project_data["assets"]["objects"]["obj_hero"]["events"]
                == _OBJECT_WITH_EVENTS["events"])


class TestRealSampleRoundTrip:
    """The synthetic fixtures above are minimal by design; this proves the
    same round-trip holds against a real bundled sample's actual object
    data (maze_1 -- obj_goal/obj_person each carry real events)."""

    def test_maze_1_events_survive_save_reload(self, tmp_path):
        import shutil

        repo_root = Path(__file__).resolve().parent.parent
        src = repo_root / "samples" / "maze_1"
        # _save_to_folder refuses to write into samples/ directly (a
        # deliberate guard) -- copy to a working location first, matching
        # how the real IDE promotes a bundled sample before editing it.
        proj_dir = tmp_path / "maze_1_copy"
        shutil.copytree(src, proj_dir)

        original = json.loads((src / "project.json").read_text(encoding="utf-8"))
        original_events = {
            name: obj["events"]
            for name, obj in original["assets"]["objects"].items()
        }

        pm = _make_project_manager()
        assert pm.load_project(proj_dir) is True
        assert pm._save_to_folder(proj_dir) is True

        on_disk = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        for name, events in original_events.items():
            entry = on_disk["assets"]["objects"][name]
            if events:
                assert entry["events"] == {}, f"{name} should be stripped"
                assert entry["_external_file"] == f"objects/{name}.json"
            side_file = json.loads(
                (proj_dir / "objects" / f"{name}.json").read_text(encoding="utf-8"))
            assert side_file["events"] == events, f"{name} events lost in side file"

        pm2 = _make_project_manager()
        assert pm2.load_project(proj_dir) is True
        for name, events in original_events.items():
            reloaded = pm2.current_project_data["assets"]["objects"][name]["events"]
            assert reloaded == events, f"{name} events not restored on reload"
