"""M13, docs/FULL_AUDIT_2026-09-07.md: core/ide/_assets.py's import_gmk_file
picks a non-clashing sibling output folder for the imported project via
`while candidate.exists() and any(candidate.iterdir()):`. If the candidate
name is occupied by a FILE (or, on a network mount, a broken junction --
the school box's Documents folder is a Kerberos CIFS mount per CLAUDE.md's
2026-09-04 session note) rather than a directory, `iterdir()` raises
NotADirectoryError -- caught only by whatever broad except sits above this
in the call chain, surfacing as a generic "import failed" with no useful
detail, instead of just treating the name as occupied and trying the next
suffix the way it already does for a non-empty directory.

Drives the real IDE method (matching tests/test_create_asset_name_validation.py's
established lightweight-double pattern for this same mixin), monkeypatching
QFileDialog.getOpenFileName and import_gmk_detailed so no real file dialog
or GMK parsing happens -- only the destination-picking loop is under test.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


class _FakeIDE:
    """The minimal surface core.ide._assets.AssetsMixin.import_gmk_file
    reads/calls on its host, besides Qt dialogs (which are monkeypatched)."""

    def tr(self, text):
        return text

    def update_status(self, *a, **k):
        pass

    def load_project(self, *a, **k):
        pass


def _host():
    from core.ide._assets import AssetsMixin

    class Host(AssetsMixin, _FakeIDE):
        pass

    return Host()


def _patch_dialogs(monkeypatch, gmk_path):
    import core.ide._assets as assets_mod
    monkeypatch.setattr(
        assets_mod.QFileDialog, "getOpenFileName",
        staticmethod(lambda *a, **k: (str(gmk_path), "")))
    warnings = []
    monkeypatch.setattr(
        assets_mod.QMessageBox, "warning",
        staticmethod(lambda *a, **k: warnings.append(a[1] if len(a) > 1 else None)))
    monkeypatch.setattr(
        assets_mod.QMessageBox, "information",
        staticmethod(lambda *a, **k: None))
    return warnings


def _patch_importer(monkeypatch, captured_output_dirs):
    """Stub import_gmk_detailed to record the output_dir it was called
    with and fail immediately -- no real GMK parsing needed for this test."""
    import importers.gmk_importer as gmk_mod

    def fake_import(gmk_path, output_dir):
        captured_output_dirs.append(Path(output_dir))
        from importers.gmk_importer import GmkImportResult
        result = GmkImportResult()
        result.success = False
        result.warnings = ["stub failure -- not a real import"]
        return result

    monkeypatch.setattr(gmk_mod, "import_gmk_detailed", fake_import)
    # import_gmk_file does `from importers.gmk_importer import
    # import_gmk_detailed` INSIDE the method, so patching the module
    # attribute above is what actually takes effect at call time.


def test_destination_occupied_by_a_file_does_not_raise(tmp_path, monkeypatch):
    gmk_file = tmp_path / "mygame.gmk"
    gmk_file.write_bytes(b"stub")

    # The natural destination name is occupied by a FILE, not a directory --
    # this is exactly what used to crash iterdir().
    (tmp_path / "mygame").write_text("not a directory", encoding="utf-8")

    warnings = _patch_dialogs(monkeypatch, gmk_file)
    captured = []
    _patch_importer(monkeypatch, captured)

    host = _host()
    host.import_gmk_file()  # must not raise NotADirectoryError

    assert captured, "the (stubbed) importer must have been reached"
    assert captured[0] == tmp_path / "mygame_2", (
        "the file-occupied name must be skipped in favour of the next suffix")
    # The stub always fails, so the user should see the "Import Failed"
    # dialog with the stub's warning text -- not a crash.
    assert warnings


def test_destination_occupied_by_a_nonempty_directory_still_skips_it(tmp_path, monkeypatch):
    """Behaviour-preservation baseline: the pre-existing non-empty-directory
    case must still work exactly as before."""
    gmk_file = tmp_path / "mygame.gmk"
    gmk_file.write_bytes(b"stub")

    occupied = tmp_path / "mygame"
    occupied.mkdir()
    (occupied / "existing.txt").write_text("x", encoding="utf-8")

    _patch_dialogs(monkeypatch, gmk_file)
    captured = []
    _patch_importer(monkeypatch, captured)

    host = _host()
    host.import_gmk_file()

    assert captured[0] == tmp_path / "mygame_2"


def test_destination_free_uses_the_natural_name(tmp_path, monkeypatch):
    gmk_file = tmp_path / "mygame.gmk"
    gmk_file.write_bytes(b"stub")

    _patch_dialogs(monkeypatch, gmk_file)
    captured = []
    _patch_importer(monkeypatch, captured)

    host = _host()
    host.import_gmk_file()

    assert captured[0] == tmp_path / "mygame"
