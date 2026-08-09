"""ProjectCompressor.compress_project excludes .trash/ — a soft-deleted
asset (utils/asset_trash.py, the "bulk-delete-undo" design decision, see
docs/ASSET_MANAGER_PLAN.md) must not resurface in every zip export/backup.
Before this fix, compress_project's project_path.rglob('*') walk had no
exclusions at all, so trash contents would have been bundled in.
"""
import zipfile
from pathlib import Path

from utils.project_compression import ProjectCompressor


def test_trash_contents_excluded_from_zip(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "project.json").write_text('{"name": "p"}', encoding="utf-8")
    trash_dir = proj / ".trash" / "sprites" / "spr_old__abc123"
    trash_dir.mkdir(parents=True)
    (trash_dir / "spr_old.png").write_bytes(b"deleted sprite bytes")
    (proj / ".trash" / "manifest.json").write_text("[]", encoding="utf-8")

    zip_path = tmp_path / "out.zip"
    assert ProjectCompressor.compress_project(proj, zip_path) is True

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()

    assert "project.json" in names
    assert not any(n.startswith(".trash") for n in names), (
        f".trash contents leaked into export: {names}")


def test_orphaned_file_trash_contents_excluded_from_zip(tmp_path):
    """.trash_orphaned_files/ (utils/project_cleanup.py, Clean Project
    Tier 3) is a second, deliberately separate trash store from .trash/ —
    see project_cleanup.py's module docstring for why — so it needs its
    own exclusion, not just a coincidental match on the ".trash" name
    prefix the sibling test above happens to also catch it under."""
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "project.json").write_text('{"name": "p"}', encoding="utf-8")
    orphan_trash_dir = proj / ".trash_orphaned_files" / "spr_old__abc123"
    orphan_trash_dir.mkdir(parents=True)
    (orphan_trash_dir / "spr_old.png").write_bytes(b"orphaned sprite bytes")
    (proj / ".trash_orphaned_files" / "manifest.json").write_text("[]", encoding="utf-8")

    zip_path = tmp_path / "out.zip"
    assert ProjectCompressor.compress_project(proj, zip_path) is True

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()

    assert "project.json" in names
    assert not any(n.startswith(".trash_orphaned_files") for n in names), (
        f".trash_orphaned_files contents leaked into export: {names}")


def test_ordinary_files_still_included(tmp_path):
    proj = tmp_path / "proj"
    (proj / "sprites").mkdir(parents=True)
    (proj / "project.json").write_text('{"name": "p"}', encoding="utf-8")
    (proj / "sprites" / "spr_live.png").write_bytes(b"a live sprite")

    zip_path = tmp_path / "out.zip"
    assert ProjectCompressor.compress_project(proj, zip_path) is True

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()

    assert "project.json" in names
    assert any("spr_live.png" in n for n in names)
