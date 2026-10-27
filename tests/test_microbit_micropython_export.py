"""Regression tests for the micro:bit MicroPython exporter (Stage X, units
X1-X2). docs/MICROBIT_STAGE_X_PLAN.md is the plan. X1 is discovery/merge/
file-layout; X2 is the display+sound action translators (golden-output,
one per mapping-table row) plus the two real scale conversions found while
building the plan (brightness 255->9, melody tempo as a tuple). Radio/
sensor/condition/generic-variable translators land in X3-X4, so any action
outside the X2 set is still correctly reported as unsupported here --
that's the honest state for this stage, not a bug.
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
        # The file-backed action list, not the stale embedded one, must be
        # what's scanned -- and scanned exactly once (not both merged
        # together into two display.show() calls).
        assert "Image('FRESH')" in source
        assert "STALE" not in source
        assert source.count("display.show(") == 1


class TestUnsupportedActionsAreNamedNotDropped:
    def test_still_unsupported_actions_are_named_before_x3_x4_translators_exist(self, tmp_path):
        # microbit_radio_send (X3) and set_variable (X4) aren't translated
        # yet at this point in the plan -- still correctly unsupported.
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "microbit_1": {"events": {"create": {"actions": [
                    {"action": "microbit_radio_send", "parameters": {"value": "1"}},
                ]}}},
            }},
        }), encoding="utf-8")
        out = tmp_path / "out"
        export(str(proj), str(out))
        source = (out / "microbit_1" / "main.py").read_text(encoding="utf-8")
        assert "Not exported" in source
        assert "microbit_radio_send" in source


class TestValidPython:
    def test_generated_file_compiles(self, project_dir, tmp_path):
        out = project_dir / "out"
        export(str(project_dir / "project.json"), str(out))
        main_py = out / "microbit_1" / "main.py"
        # py_compile only checks syntax -- it doesn't execute "import
        # microbit", so no stub module is needed for this check.
        py_compile.compile(str(main_py), doraise=True)


class TestExporterInstanceReset:
    def test_translated_actions_do_not_leak_between_objects(self, tmp_path):
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
        assert "music.pitch" not in a
        assert "display.show" not in b

    def test_unsupported_set_does_not_leak_between_objects(self, tmp_path):
        # Both action types are still unsupported at this point in the
        # plan (X3/X4) -- a real canary for self.unsupported leaking
        # across the per-object loop in export().
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "microbit_a": {"events": {"create": {"actions": [
                    {"action": "microbit_radio_send", "parameters": {"value": "1"}},
                ]}}},
                "microbit_b": {"events": {"create": {"actions": [
                    {"action": "set_variable", "parameters": {"variable": "x", "value": "1"}},
                ]}}},
            }},
        }), encoding="utf-8")
        out = tmp_path / "out"
        exporter = MicropythonExporter()
        exporter.export(str(proj), str(out))
        a = (out / "microbit_a" / "main.py").read_text(encoding="utf-8")
        b = (out / "microbit_b" / "main.py").read_text(encoding="utf-8")
        assert "set_variable" not in a
        assert "microbit_radio_send" not in b


def _setup_lines(action, parameters, tmp_path):
    """The Create-event setup lines generated for one action -- the
    golden-output unit for X2's per-action mapping table."""
    proj = tmp_path / "project.json"
    proj.write_text(json.dumps({
        "name": "TestProject",
        "assets": {"objects": {
            "microbit_1": {"events": {"create": {"actions": [
                {"action": action, "parameters": parameters},
            ]}}},
        }},
    }), encoding="utf-8")
    out = tmp_path / "out"
    export(str(proj), str(out))
    return (out / "microbit_1" / "main.py").read_text(encoding="utf-8")


class TestX2DisplayTranslators:
    """One test per `extensions/microbit/export/micropython_exporter.py`
    display translator, matching the mapping table in
    docs/MICROBIT_STAGE_X_PLAN.md exactly."""

    def test_show_image_builtin_name(self, tmp_path):
        source = _setup_lines("microbit_show_image", {"image": "HEART"}, tmp_path)
        assert "display.show(Image.HEART)" in source

    def test_show_image_custom_grid_passes_through_as_image_literal(self, tmp_path):
        source = _setup_lines("microbit_show_image",
                               {"image": "09090:99999:99999:09990:00900"}, tmp_path)
        assert "display.show(Image('09090:99999:99999:09990:00900'))" in source

    def test_show_image_hold_adds_sleep_ms(self, tmp_path):
        source = _setup_lines("microbit_show_image",
                               {"image": "HEART", "hold": 500}, tmp_path)
        assert "display.show(Image.HEART)" in source
        assert "sleep_ms(500)" in source

    def test_show_image_zero_hold_adds_no_sleep(self, tmp_path):
        source = _setup_lines("microbit_show_image",
                               {"image": "HEART", "hold": 0}, tmp_path)
        assert "sleep_ms" not in source

    def test_scroll_text_quoted_literal(self, tmp_path):
        source = _setup_lines("microbit_scroll_text",
                               {"text": '"Hello"', "delay": 150}, tmp_path)
        assert 'display.scroll("Hello", delay=150)' in source

    def test_scroll_text_variable_expression_passes_through(self, tmp_path):
        source = _setup_lines("microbit_scroll_text", {"text": "rolls"}, tmp_path)
        assert "display.scroll(rolls, delay=150)" in source

    def test_show_number_literal(self, tmp_path):
        source = _setup_lines("microbit_show_number", {"value": "7"}, tmp_path)
        assert "display.show(7)" in source

    def test_show_number_variable_expression_passes_through(self, tmp_path):
        source = _setup_lines("microbit_show_number", {"value": "rolls"}, tmp_path)
        assert "display.show(rolls)" in source

    def test_set_pixel(self, tmp_path):
        source = _setup_lines("microbit_set_pixel",
                               {"x": 2, "y": 3, "brightness": 9}, tmp_path)
        assert "display.set_pixel(2, 3, 9)" in source

    def test_clear_display(self, tmp_path):
        source = _setup_lines("microbit_clear_display", {}, tmp_path)
        assert "display.clear()" in source

    def test_set_brightness_scale_conversion_255_to_9(self, tmp_path):
        # The real-device finding from the plan: our schema/simulator use
        # 0-255, display.set_brightness() on the device takes 0-9.
        source = _setup_lines("microbit_set_brightness", {"brightness": 255}, tmp_path)
        assert "display.set_brightness(round((255) / 255 * 9))" in source

    def test_set_brightness_mid_value_rounds_correctly_at_runtime(self, tmp_path):
        source = _setup_lines("microbit_set_brightness", {"brightness": 128}, tmp_path)
        # Computed on the device, not pre-folded at export time -- the
        # same expression works whether brightness is a literal or a
        # variable. Confirm the arithmetic itself is correct: round(128/255*9) == 5.
        assert round(128 / 255 * 9) == 5
        assert "display.set_brightness(round((128) / 255 * 9))" in source


class TestX2SoundTranslators:
    def test_play_tone(self, tmp_path):
        source = _setup_lines("microbit_play_tone",
                               {"frequency": 440, "duration": 500}, tmp_path)
        assert "music.pitch(440, 500)" in source

    def test_play_melody_builtin_name(self, tmp_path):
        source = _setup_lines("microbit_play_melody",
                               {"melody": "DADADADUM", "tempo": 120}, tmp_path)
        assert "music.DADADADUM" in source
        # A built-in name has no tempo argument on the device -- it's a
        # module constant, not a music.play() call.
        assert "music.play" not in source

    def test_play_melody_custom_notes_quoted(self, tmp_path):
        source = _setup_lines("microbit_play_melody",
                               {"melody": '"C4:4 E G"', "tempo": 90}, tmp_path)
        assert "music.play('C4:4 E G', tempo=(4, 90))" in source

    def test_play_melody_custom_notes_unquoted_fallback(self, tmp_path):
        # handlers.py's own fallback: an unquoted value that isn't a
        # built-in name is still used as literal note text.
        source = _setup_lines("microbit_play_melody",
                               {"melody": "C4:4 E G", "tempo": 90}, tmp_path)
        assert "music.play('C4:4 E G', tempo=(4, 90))" in source

    def test_stop_sound(self, tmp_path):
        source = _setup_lines("microbit_stop_sound", {}, tmp_path)
        assert "music.stop()" in source


class TestX2ConditionalImports:
    def test_music_import_only_when_sound_action_used(self, tmp_path):
        source = _setup_lines("microbit_play_tone", {"frequency": 440}, tmp_path)
        assert "import music" in source

    def test_no_music_import_for_display_only_object(self, tmp_path):
        source = _setup_lines("microbit_show_image", {"image": "HEART"}, tmp_path)
        assert "import music" not in source
        assert "from microbit import *" in source
