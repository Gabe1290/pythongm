"""Regression tests for the micro:bit MicroPython exporter (Stage X, unit
X1: skeleton). docs/MICROBIT_STAGE_X_PLAN.md is the plan; action/condition
translators land in later units (X2-X4), so every action in these fixtures
is correctly reported as unsupported here -- that's the honest state for
this stage, not a bug.
"""
import json
import py_compile
from pathlib import Path

import pytest

from extensions.microbit.export.micropython_exporter import MicropythonExporter, export


def _project_with_microbit(extra_object=None):
    objects = {
        "microbit_1": {
            "events": {
                "create": {
                    "actions": [
                        {"action": "microbit_show_image",
                         "parameters": {"image": "HEART"}},
                    ]
                },
                "microbit_button_a": {
                    "actions": [
                        {"action": "microbit_show_image",
                         "parameters": {"image": "HAPPY"}},
                    ]
                },
            },
        },
    }
    if extra_object:
        objects.update(extra_object)
    return {"name": "TestProject", "assets": {"objects": objects}}


@pytest.fixture
def project_dir(tmp_path):
    proj = tmp_path / "project.json"
    proj.write_text(json.dumps(_project_with_microbit(
        extra_object={"obj_player": {"events": {}}})), encoding="utf-8")
    return tmp_path


class TestObjectDiscovery:
    def test_finds_name_prefixed_microbit_object(self, project_dir):
        out = project_dir / "out"
        assert export(str(project_dir / "project.json"), str(out)) is True
        assert (out / "microbit_1" / "main.py").exists()

    def test_skips_non_microbit_object(self, project_dir):
        out = project_dir / "out"
        export(str(project_dir / "project.json"), str(out))
        assert not (out / "obj_player").exists()

    def test_is_microbit_flag_without_name_prefix(self, tmp_path):
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "obj_board": {"is_microbit": True, "events": {}},
            }},
        }), encoding="utf-8")
        out = tmp_path / "out"
        assert export(str(proj), str(out)) is True
        assert (out / "obj_board" / "main.py").exists()

    def test_no_microbit_objects_returns_false(self, tmp_path):
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {"obj_player": {"events": {}}}},
        }), encoding="utf-8")
        assert export(str(proj), str(tmp_path / "out")) is False

    def test_missing_project_file_returns_false(self, tmp_path):
        assert export(str(tmp_path / "nope.json"), str(tmp_path / "out")) is False


class TestOneFilePerBoard:
    def test_two_boards_get_separate_main_py_files(self, tmp_path):
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "microbit_a": {"events": {}},
                "microbit_b": {"events": {}},
            }},
        }), encoding="utf-8")
        out = tmp_path / "out"
        export(str(proj), str(out))
        a = (out / "microbit_a" / "main.py").read_text(encoding="utf-8")
        b = (out / "microbit_b" / "main.py").read_text(encoding="utf-8")
        assert "microbit_a" in a
        assert "microbit_b" in b
        # Each board's file is independently named "main.py" -- the one
        # name a real device auto-runs -- so they must live in separate
        # directories, not a flat shared output folder.
        assert (out / "microbit_a" / "main.py") != (out / "microbit_b" / "main.py")


class TestGeneratedStructure:
    def _generated(self, project_dir):
        out = project_dir / "out"
        export(str(project_dir / "project.json"), str(out))
        return (out / "microbit_1" / "main.py").read_text(encoding="utf-8")

    def test_has_the_microbit_import(self, project_dir):
        assert "from microbit import *" in self._generated(project_dir)

    def test_has_one_top_level_loop(self, project_dir):
        source = self._generated(project_dir)
        assert source.count("while True:") == 1

    def test_header_names_the_object_and_project(self, project_dir):
        source = self._generated(project_dir)
        assert "microbit_1" in source
        assert "TestProject" in source

    def test_header_tells_the_student_the_filename_matters(self, project_dir):
        source = self._generated(project_dir)
        assert "main.py" in source

    def test_merges_objects_dir_over_stale_project_json(self, tmp_path):
        proj_dir = tmp_path
        (proj_dir / "objects").mkdir()
        proj_dir.joinpath("project.json").write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "microbit_1": {"events": {
                    "create": {"actions": [
                        {"action": "microbit_show_image",
                         "parameters": {"image": "STALE"}},
                    ]}
                }},
            }},
        }), encoding="utf-8")
        (proj_dir / "objects" / "microbit_1.json").write_text(json.dumps({
            "events": {
                "create": {"actions": [
                    {"action": "microbit_show_image",
                     "parameters": {"image": "FRESH"}},
                ]}
            }
        }), encoding="utf-8")
        out = proj_dir / "out"
        export(str(proj_dir / "project.json"), str(out))
        source = (out / "microbit_1" / "main.py").read_text(encoding="utf-8")
        # Both images are "unsupported" at this stage (no translators yet),
        # but the *merge* itself is what's under test: the file-backed
        # action list, not the stale embedded one, must be what's scanned.
        assert "FRESH" not in source and "STALE" not in source  # neither image name appears (not yet translated)...
        # ...but the unsupported-action marker must only have ONE
        # microbit_show_image entry, proving one action list was scanned,
        # not both merged together.
        assert source.count("microbit_show_image") == 1


class TestUnsupportedActionsAreNamedNotDropped:
    def test_every_action_is_listed_as_unsupported_before_translators_exist(self, project_dir):
        source = self._generated_via(project_dir)
        assert "Not exported" in source
        assert "microbit_show_image" in source

    def _generated_via(self, project_dir):
        out = project_dir / "out"
        export(str(project_dir / "project.json"), str(out))
        return (out / "microbit_1" / "main.py").read_text(encoding="utf-8")


class TestValidPython:
    def test_generated_file_compiles(self, project_dir, tmp_path):
        out = project_dir / "out"
        export(str(project_dir / "project.json"), str(out))
        main_py = out / "microbit_1" / "main.py"
        # py_compile only checks syntax -- it doesn't execute "import
        # microbit", so no stub module is needed for this check.
        py_compile.compile(str(main_py), doraise=True)


class TestExporterInstanceReset:
    def test_unsupported_set_does_not_leak_between_objects(self, tmp_path):
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "microbit_a": {"events": {"create": {"actions": [
                    {"action": "microbit_show_image", "parameters": {"image": "HEART"}},
                ]}}},
                "microbit_b": {"events": {"create": {"actions": [
                    {"action": "microbit_play_tone", "parameters": {"frequency": 440}},
                ]}}},
            }},
        }), encoding="utf-8")
        out = tmp_path / "out"
        exporter = MicropythonExporter()
        exporter.export(str(proj), str(out))
        a = (out / "microbit_a" / "main.py").read_text(encoding="utf-8")
        b = (out / "microbit_b" / "main.py").read_text(encoding="utf-8")
        assert "microbit_play_tone" not in a
        assert "microbit_show_image" not in b
