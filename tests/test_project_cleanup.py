"""utils/project_cleanup.py — Clean Project Tier 1 (docs/CLEAN_PROJECT_PLAN.md
/ DEFERRED_ITEMS_PLAN.md item 11): sweeping orphaned *.tmp atomic-write
siblings. Pure filesystem logic, no Qt dependency.
"""
import os
import time
from pathlib import Path

from utils.project_cleanup import (
    find_orphan_tmp_files, sweep_orphan_tmp_files, find_orphaned_physical_files)


def _age_file(path: Path, seconds_old: int):
    old_time = time.time() - seconds_old
    os.utime(path, (old_time, old_time))


class TestFindOrphanTmpFiles:
    def test_finds_old_tmp_file(self, tmp_path):
        tmp_file = tmp_path / "project.json.tmp"
        tmp_file.write_text("{}")
        _age_file(tmp_file, 120)

        found = find_orphan_tmp_files(tmp_path, min_age_seconds=60)

        assert found == [tmp_file]

    def test_ignores_recent_tmp_file(self, tmp_path):
        """A .tmp file younger than the age floor might be an in-flight
        save — don't touch it."""
        tmp_file = tmp_path / "project.json.tmp"
        tmp_file.write_text("{}")
        # No _age_file call: mtime is "now".

        found = find_orphan_tmp_files(tmp_path, min_age_seconds=60)

        assert found == []

    def test_finds_tmp_files_in_subdirectories(self, tmp_path):
        (tmp_path / "rooms").mkdir()
        tmp_file = tmp_path / "rooms" / "room_1.json.tmp"
        tmp_file.write_text("{}")
        _age_file(tmp_file, 120)

        found = find_orphan_tmp_files(tmp_path, min_age_seconds=60)

        assert found == [tmp_file]

    def test_ignores_non_tmp_files(self, tmp_path):
        real_file = tmp_path / "project.json"
        real_file.write_text("{}")
        _age_file(real_file, 120)

        found = find_orphan_tmp_files(tmp_path, min_age_seconds=60)

        assert found == []

    def test_empty_project_dir_returns_empty_list(self, tmp_path):
        assert find_orphan_tmp_files(tmp_path) == []

    def test_missing_project_dir_is_a_safe_noop(self, tmp_path):
        missing = tmp_path / "does_not_exist"
        assert find_orphan_tmp_files(missing) == []


class TestSweepOrphanTmpFiles:
    def test_removes_old_tmp_files_and_returns_removed_paths(self, tmp_path):
        tmp_file = tmp_path / "project.json.tmp"
        tmp_file.write_text("{}")
        _age_file(tmp_file, 120)

        removed = sweep_orphan_tmp_files(tmp_path, min_age_seconds=60)

        assert removed == [tmp_file]
        assert not tmp_file.exists()

    def test_leaves_recent_tmp_file_in_place(self, tmp_path):
        tmp_file = tmp_path / "project.json.tmp"
        tmp_file.write_text("{}")

        removed = sweep_orphan_tmp_files(tmp_path, min_age_seconds=60)

        assert removed == []
        assert tmp_file.exists()

    def test_leaves_real_files_untouched(self, tmp_path):
        real_file = tmp_path / "project.json"
        real_file.write_text('{"real": true}')
        _age_file(real_file, 120)

        sweep_orphan_tmp_files(tmp_path, min_age_seconds=60)

        assert real_file.exists()
        assert real_file.read_text() == '{"real": true}'

    def test_multiple_orphans_all_removed(self, tmp_path):
        (tmp_path / "objects").mkdir()
        f1 = tmp_path / "project.json.tmp"
        f2 = tmp_path / "objects" / "obj_hero.json.tmp"
        f1.write_text("{}")
        f2.write_text("{}")
        _age_file(f1, 120)
        _age_file(f2, 120)

        removed = sweep_orphan_tmp_files(tmp_path, min_age_seconds=60)

        assert set(removed) == {f1, f2}
        assert not f1.exists()
        assert not f2.exists()


class TestFindOrphanedPhysicalFiles:
    def test_referenced_file_is_not_orphaned(self, tmp_path):
        (tmp_path / "sprites").mkdir()
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        project_data = {"assets": {"sprites": {
            "spr_hero": {"file_path": "sprites/spr_hero.png"}}}}

        orphaned = find_orphaned_physical_files(tmp_path, project_data)

        assert orphaned == {}

    def test_unreferenced_file_is_orphaned(self, tmp_path):
        (tmp_path / "sprites").mkdir()
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        (tmp_path / "sprites" / "spr_leftover.png").write_bytes(b"png")
        project_data = {"assets": {"sprites": {
            "spr_hero": {"file_path": "sprites/spr_hero.png"}}}}

        orphaned = find_orphaned_physical_files(tmp_path, project_data)

        assert orphaned == {"sprites": [tmp_path / "sprites" / "spr_leftover.png"]}

    def test_thumbnail_reference_protects_thumbnail_file(self, tmp_path):
        (tmp_path / "sprites").mkdir()
        (tmp_path / "thumbnails").mkdir()
        (tmp_path / "sprites" / "spr_hero.png").write_bytes(b"png")
        (tmp_path / "thumbnails" / "spr_hero_thumb.png").write_bytes(b"png")
        project_data = {"assets": {"sprites": {
            "spr_hero": {"file_path": "sprites/spr_hero.png",
                         "thumbnail": "thumbnails/spr_hero_thumb.png"}}}}

        orphaned = find_orphaned_physical_files(tmp_path, project_data)

        assert orphaned == {}

    def test_orphaned_thumbnail_with_no_owning_entry(self, tmp_path):
        (tmp_path / "thumbnails").mkdir()
        (tmp_path / "thumbnails" / "spr_deleted_thumb.png").write_bytes(b"png")
        project_data = {"assets": {}}

        orphaned = find_orphaned_physical_files(tmp_path, project_data)

        assert orphaned == {"thumbnails": [tmp_path / "thumbnails" / "spr_deleted_thumb.png"]}

    def test_non_asset_extension_is_ignored(self, tmp_path):
        (tmp_path / "sprites").mkdir()
        (tmp_path / "sprites" / "README.txt").write_text("notes")
        project_data = {"assets": {}}

        orphaned = find_orphaned_physical_files(tmp_path, project_data)

        assert orphaned == {}

    def test_multiple_categories_reported_independently(self, tmp_path):
        (tmp_path / "sprites").mkdir()
        (tmp_path / "sounds").mkdir()
        (tmp_path / "sprites" / "spr_orphan.png").write_bytes(b"png")
        (tmp_path / "sounds" / "snd_orphan.wav").write_bytes(b"wav")
        project_data = {"assets": {}}

        orphaned = find_orphaned_physical_files(tmp_path, project_data)

        assert orphaned == {
            "sprites": [tmp_path / "sprites" / "spr_orphan.png"],
            "sounds": [tmp_path / "sounds" / "snd_orphan.wav"],
        }

    def test_missing_category_directory_is_a_safe_noop(self, tmp_path):
        project_data = {"assets": {}}

        orphaned = find_orphaned_physical_files(tmp_path, project_data)

        assert orphaned == {}

    def test_empty_project_data_is_a_safe_noop(self, tmp_path):
        (tmp_path / "sprites").mkdir()
        (tmp_path / "sprites" / "spr_orphan.png").write_bytes(b"png")

        orphaned = find_orphaned_physical_files(tmp_path, {})

        assert orphaned == {"sprites": [tmp_path / "sprites" / "spr_orphan.png"]}
