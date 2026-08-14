"""Two independent readers that load project.json straight off disk and
never merged objects/<name>.json, found while investigating TODO.md's
"Manifest-ify objects & sprites" item: with project.json's embedded object
body always full today (dual storage), this was invisible; it becomes a
real, silent data-loss bug the moment an object's on-disk objects/<name>.json
diverges from project.json's embedded copy (e.g. edited since the last full
project save — the exact drift this repo's dual-storage setup already
documents as a hazard).

- export/Aseba/aseba_exporter.py: AsebaExporter.export() is handed a raw
  project.json PATH by core/ide_window.py's export_aseba_code (not the live
  merged current_project_data) and read events straight from it with no
  merge step -- exporting a Thymio object whose events only live in its
  objects/<name>.json produced an EMPTY .aesl (no onevent blocks at all).
- utils/resource_packager.py's ResourcePackager.export_object (Tools ->
  Export Object / single-asset sharing, .gmobj packages) had the same gap.
  export_room right next to it already merges rooms/<name>.json -- proof
  this exact class of bug is real and had to be fixed once already, for
  rooms, in this same file.
"""
import json
import zipfile
from pathlib import Path

import pytest

from export.Aseba.aseba_exporter import AsebaExporter
from utils.resource_packager import ResourcePackager


def _project_stub_with_manifest_object():
    """An object whose project.json entry carries NO events at all --
    simulating the drift/manifest case: the real events only live in the
    external objects/<name>.json file."""
    return {
        "name": "TestBot",
        "assets": {
            "objects": {
                "thymio_robot": {
                    "name": "thymio_robot",
                    "asset_type": "object",
                    "is_thymio": True,
                    # No 'events' key here at all -- must come from the file.
                },
            },
        },
    }


_FILE_EVENTS = {
    "events": {
        "thymio_button_forward": {
            "actions": [
                {"action": "thymio_move_forward", "parameters": {"speed": 200}}
            ]
        }
    }
}


@pytest.fixture
def project_with_external_object_file(tmp_path):
    proj_dir = tmp_path / "proj"
    proj_dir.mkdir()
    (proj_dir / "project.json").write_text(
        json.dumps(_project_stub_with_manifest_object()), encoding="utf-8")
    objects_dir = proj_dir / "objects"
    objects_dir.mkdir()
    (objects_dir / "thymio_robot.json").write_text(
        json.dumps({"name": "thymio_robot", "asset_type": "object",
                    "is_thymio": True, **_FILE_EVENTS}),
        encoding="utf-8")
    return proj_dir


def test_aseba_export_merges_events_from_object_file(project_with_external_object_file):
    out = project_with_external_object_file / "aseba_out"
    exporter = AsebaExporter()
    assert exporter.export(
        str(project_with_external_object_file / "project.json"), str(out)) is True

    aesl_file = out / "thymio_robot.aesl"
    assert aesl_file.exists()
    content = aesl_file.read_text(encoding="utf-8")
    # The move-forward action from the external file must have reached the
    # generated AESL -- proof the merge actually happened, not just that
    # SOME file was written.
    assert "motor.left.target" in content or "motor" in content.lower()


def test_aseba_export_without_objects_dir_still_works(tmp_path):
    # No objects/ directory at all -- must fall back to embedded data
    # (legacy/no-external-files project), not crash.
    proj = tmp_path / "project.json"
    data = _project_stub_with_manifest_object()
    data["assets"]["objects"]["thymio_robot"].update(_FILE_EVENTS)  # embedded
    proj.write_text(json.dumps(data), encoding="utf-8")
    out = tmp_path / "out"
    exporter = AsebaExporter()
    assert exporter.export(str(proj), str(out)) is True
    assert (out / "thymio_robot.aesl").exists()


def test_export_object_merges_events_from_object_file(project_with_external_object_file):
    out_pkg = project_with_external_object_file / "thymio_robot.gmobj"
    assert ResourcePackager.export_object(
        project_with_external_object_file, "thymio_robot", out_pkg) is True

    with zipfile.ZipFile(out_pkg) as zf:
        package_data = json.loads(zf.read("package.json"))

    assert package_data["object"]["events"] == _FILE_EVENTS["events"]


def test_export_object_without_object_file_uses_embedded_events(tmp_path):
    proj_dir = tmp_path / "proj"
    proj_dir.mkdir()
    data = _project_stub_with_manifest_object()
    data["assets"]["objects"]["thymio_robot"].update(_FILE_EVENTS)  # embedded only
    (proj_dir / "project.json").write_text(json.dumps(data), encoding="utf-8")

    out_pkg = proj_dir / "thymio_robot.gmobj"
    assert ResourcePackager.export_object(proj_dir, "thymio_robot", out_pkg) is True

    with zipfile.ZipFile(out_pkg) as zf:
        package_data = json.loads(zf.read("package.json"))
    assert package_data["object"]["events"] == _FILE_EVENTS["events"]


def test_export_object_does_not_mutate_caller_visible_project_state(project_with_external_object_file):
    """export_object copies before merging -- it must not leave the merged
    events sitting in some shared/cached structure a caller didn't ask for."""
    out_pkg = project_with_external_object_file / "thymio_robot.gmobj"
    ResourcePackager.export_object(
        project_with_external_object_file, "thymio_robot", out_pkg)

    # The on-disk project.json (the only thing this function is allowed to
    # touch as an input) must be untouched.
    on_disk = json.loads(
        (project_with_external_object_file / "project.json").read_text(encoding="utf-8"))
    assert "events" not in on_disk["assets"]["objects"]["thymio_robot"]
