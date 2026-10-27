"""Regression tests for the micro:bit MicroPython exporter (Stage X, units
X1-X5). docs/MICROBIT_STAGE_X_PLAN.md is the plan. X1 is discovery/merge/
file-layout; X2 is the display+sound action translators; X3 is radio +
sensor-read translators, plus the V1/V2 export choice (O6) and the
skip-and-warn behaviour for V2-only actions on a V1 export (O2); X4 is the
four condition translators plus the generic set_variable/test_variable/
comment/block-structure subset, with the flat-list-to-nested-Python
control-flow translation that needs; X5 is event polling -- every
microbit_* event joins the while-loop body as a guard, with hand-rolled
edge tracking for buttons/logo/pins/sound (no native edge-triggered call
on the device) and the native was_gesture()/radio.receive() for
everything else. Anything outside this plan's scope entirely (ordinary
core actions with no micro:bit meaning) is still correctly reported as
unsupported.
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
    def test_actions_outside_the_exporters_scope_are_named_not_dropped(self, tmp_path):
        # A generic action with no micro:bit meaning and outside X4's
        # small generic subset -- still correctly unsupported at every
        # unit in this plan.
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "microbit_1": {"events": {"create": {"actions": [
                    {"action": "move_towards_point", "parameters": {"x": "0", "y": "0"}},
                ]}}},
            }},
        }), encoding="utf-8")
        out = tmp_path / "out"
        export(str(proj), str(out))
        source = (out / "microbit_1" / "main.py").read_text(encoding="utf-8")
        assert "Not exported" in source
        assert "move_towards_point" in source


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
        # Both action types are still outside the exporter's scope -- a
        # real canary for self.unsupported leaking across the per-object
        # loop in export().
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "microbit_a": {"events": {"create": {"actions": [
                    {"action": "move_towards_point", "parameters": {"x": "0", "y": "0"}},
                ]}}},
                "microbit_b": {"events": {"create": {"actions": [
                    {"action": "set_sprite", "parameters": {"sprite": "spr_x"}},
                ]}}},
            }},
        }), encoding="utf-8")
        out = tmp_path / "out"
        exporter = MicropythonExporter()
        exporter.export(str(proj), str(out))
        a = (out / "microbit_a" / "main.py").read_text(encoding="utf-8")
        b = (out / "microbit_b" / "main.py").read_text(encoding="utf-8")
        assert "set_sprite" not in a
        assert "move_towards_point" not in b


def _setup_lines(action, parameters, tmp_path, board_version="v2"):
    """The Create-event setup lines generated for one action -- the
    golden-output unit for the plan's per-action mapping table."""
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
    export(str(proj), str(out), board_version=board_version)
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


class TestX3RadioTranslators:
    def test_radio_set_group(self, tmp_path):
        source = _setup_lines("microbit_radio_set_group", {"group": 7}, tmp_path)
        assert "radio.config(group=7)" in source

    def test_radio_set_group_injects_radio_on_once(self, tmp_path):
        source = _setup_lines("microbit_radio_set_group", {"group": 7}, tmp_path)
        assert source.count("radio.on()") == 1
        assert "import radio" in source

    def test_radio_send_wraps_value_in_str(self, tmp_path):
        source = _setup_lines("microbit_radio_send", {"value": "1"}, tmp_path)
        assert "radio.send(str(1))" in source

    def test_radio_send_variable_expression_passes_through(self, tmp_path):
        source = _setup_lines("microbit_radio_send", {"value": "score"}, tmp_path)
        assert "radio.send(str(score))" in source

    def test_no_radio_import_without_a_radio_action(self, tmp_path):
        source = _setup_lines("microbit_show_image", {"image": "HEART"}, tmp_path)
        assert "import radio" not in source
        assert "radio.on()" not in source


class TestX3SensorTranslator:
    def test_accelerometer_axes(self, tmp_path):
        for axis, call in [("x", "get_x"), ("y", "get_y"), ("z", "get_z")]:
            source = _setup_lines("microbit_read_sensor",
                                   {"sensor": f"accelerometer {axis}", "variable": "v"}, tmp_path)
            assert f"v = accelerometer.{call}()" in source

    def test_acceleration_strength(self, tmp_path):
        source = _setup_lines("microbit_read_sensor",
                               {"sensor": "acceleration strength", "variable": "v"}, tmp_path)
        assert "v = accelerometer.get_strength()" in source

    def test_light_level(self, tmp_path):
        source = _setup_lines("microbit_read_sensor",
                               {"sensor": "light level", "variable": "v"}, tmp_path)
        assert "v = display.read_light_level()" in source

    def test_temperature(self, tmp_path):
        source = _setup_lines("microbit_read_sensor",
                               {"sensor": "temperature", "variable": "v"}, tmp_path)
        assert "v = temperature()" in source

    def test_pin_analog(self, tmp_path):
        for n in (0, 1, 2):
            source = _setup_lines("microbit_read_sensor",
                                   {"sensor": f"pin {n} analog", "variable": "v"}, tmp_path)
            assert f"v = pin{n}.read_analog()" in source

    def test_global_prefixed_variable_becomes_a_plain_name(self, tmp_path):
        # A real export is one board, one standalone file -- "global." and
        # a plain name both collapse to the same top-level Python global.
        source = _setup_lines("microbit_read_sensor",
                               {"sensor": "temperature", "variable": "global.temp"}, tmp_path)
        assert "temp = temperature()" in source
        assert "global.temp" not in source

    def test_compass_heading_calibrates_once(self, tmp_path):
        source = _setup_lines("microbit_read_sensor",
                               {"sensor": "compass heading", "variable": "h"}, tmp_path)
        assert "h = compass.heading()" in source
        assert source.count("compass.calibrate()") == 1

    def test_no_compass_calibrate_without_compass_use(self, tmp_path):
        source = _setup_lines("microbit_read_sensor",
                               {"sensor": "temperature", "variable": "v"}, tmp_path)
        assert "compass.calibrate()" not in source


class TestO2V1V2SoundLevelSensor:
    """O2, resolved concretely: a V1 export skips + warns on V2-only
    actions instead of emitting code that fails on the device."""

    def test_sound_level_translates_on_v2(self, tmp_path):
        source = _setup_lines("microbit_read_sensor",
                               {"sensor": "sound level", "variable": "v"},
                               tmp_path, board_version="v2")
        assert "v = microphone.sound_level()" in source
        assert "Not exported" not in source

    def test_sound_level_skipped_and_warned_on_v1(self, tmp_path):
        source = _setup_lines("microbit_read_sensor",
                               {"sensor": "sound level", "variable": "v"},
                               tmp_path, board_version="v1")
        assert "microphone" not in source
        assert "Not exported -- needs a V2 board" in source
        assert "sound level" in source

    def test_v2_is_the_default_board_version(self, tmp_path):
        # export()'s own default, not just the test helper's.
        proj = tmp_path / "project.json"
        proj.write_text(json.dumps({
            "name": "TestProject",
            "assets": {"objects": {
                "microbit_1": {"events": {"create": {"actions": [
                    {"action": "microbit_read_sensor",
                     "parameters": {"sensor": "sound level", "variable": "v"}},
                ]}}},
            }},
        }), encoding="utf-8")
        out = tmp_path / "out"
        export(str(proj), str(out))  # no board_version passed
        source = (out / "microbit_1" / "main.py").read_text(encoding="utf-8")
        assert "v = microphone.sound_level()" in source


def _create_actions(actions, tmp_path, board_version="v2"):
    """Like _setup_lines, but for a whole Create-event action LIST --
    X4's block-structure tests need to see how several actions interact,
    not just one at a time."""
    proj = tmp_path / "project.json"
    proj.write_text(json.dumps({
        "name": "TestProject",
        "assets": {"objects": {
            "microbit_1": {"events": {"create": {"actions": actions}}},
        }},
    }), encoding="utf-8")
    out = tmp_path / "out"
    export(str(proj), str(out), board_version=board_version)
    return (out / "microbit_1" / "main.py").read_text(encoding="utf-8")


class TestX4ConditionTranslators:
    def test_if_button_a(self, tmp_path):
        source = _setup_lines("microbit_if_button", {"button": "a"}, tmp_path)
        assert "button_a.is_pressed()" in source

    def test_if_button_b(self, tmp_path):
        source = _setup_lines("microbit_if_button", {"button": "b"}, tmp_path)
        assert "button_b.is_pressed()" in source

    def test_if_button_ab_chord(self, tmp_path):
        source = _setup_lines("microbit_if_button", {"button": "ab"}, tmp_path)
        assert "button_a.is_pressed() and button_b.is_pressed()" in source

    def test_if_button_logo_on_v2(self, tmp_path):
        source = _setup_lines("microbit_if_button", {"button": "logo"},
                               tmp_path, board_version="v2")
        assert "pin_logo.is_touched()" in source

    def test_if_button_logo_skipped_and_warned_on_v1(self, tmp_path):
        source = _setup_lines("microbit_if_button", {"button": "logo"},
                               tmp_path, board_version="v1")
        assert "pin_logo" not in source
        assert "Not exported -- needs a V2 board" in source
        assert "logo" in source

    def test_if_gesture(self, tmp_path):
        source = _setup_lines("microbit_if_gesture", {"gesture": "shake"}, tmp_path)
        assert "accelerometer.is_gesture('shake')" in source

    def test_if_gesture_two_word_name(self, tmp_path):
        source = _setup_lines("microbit_if_gesture", {"gesture": "face up"}, tmp_path)
        assert "accelerometer.is_gesture('face up')" in source

    def test_if_tilt(self, tmp_path):
        source = _setup_lines("microbit_if_tilt",
                               {"axis": "x", "comparison": ">", "value": "300"}, tmp_path)
        assert "accelerometer.get_x() > (300)" in source

    def test_if_pixel_default_is_it_lit(self, tmp_path):
        source = _setup_lines("microbit_if_pixel", {"x": 2, "y": 2}, tmp_path)
        assert "display.get_pixel(2, 2) > (0)" in source

    def test_test_variable_equal(self, tmp_path):
        source = _setup_lines("test_variable",
                               {"variable": "roll", "value": "1", "operation": "equal"}, tmp_path)
        assert "roll == (1)" in source

    def test_test_variable_every_operation(self, tmp_path):
        for op, symbol in [("equal", "=="), ("not_equal", "!="), ("less", "<"),
                            ("less_equal", "<="), ("greater", ">"), ("greater_equal", ">=")]:
            source = _setup_lines("test_variable",
                                   {"variable": "x", "value": "5", "operation": op}, tmp_path)
            assert f"x {symbol} (5)" in source

    def test_test_variable_other_scope_is_unsupported(self, tmp_path):
        source = _setup_lines("test_variable",
                               {"variable": "x", "value": "5", "scope": "other"}, tmp_path)
        assert "Not exported" in source
        assert "other scope" in source


class TestX4GenericVariableAndComment:
    def test_set_variable_plain_assignment(self, tmp_path):
        source = _setup_lines("set_variable", {"variable": "score", "value": "0"}, tmp_path)
        assert "score = 0" in source

    def test_set_variable_relative_becomes_augmented_assignment(self, tmp_path):
        source = _setup_lines("set_variable",
                               {"variable": "score", "value": "1", "relative": True}, tmp_path)
        assert "score += (1)" in source

    def test_set_variable_global_prefixed_still_becomes_a_plain_name(self, tmp_path):
        source = _setup_lines("set_variable",
                               {"variable": "x", "value": "1", "scope": "global"}, tmp_path)
        assert "x = 1" in source

    def test_set_variable_other_scope_is_unsupported(self, tmp_path):
        source = _setup_lines("set_variable",
                               {"variable": "x", "value": "1", "scope": "other"}, tmp_path)
        assert "Not exported" in source
        assert "other scope" in source

    def test_comment_becomes_a_hash_line(self, tmp_path):
        source = _setup_lines("comment", {"text": "wire up the dice"}, tmp_path)
        assert "# wire up the dice" in source

    def test_empty_comment_emits_nothing(self, tmp_path):
        source = _setup_lines("comment", {"text": ""}, tmp_path)
        # No setup section at all, and the loop body is just "pass" --
        # an empty comment contributes no lines anywhere.
        assert "# -- setup" not in source
        assert "while True:\n    pass" in source


class TestX4GmBuiltinRewriting:
    def test_irandom_becomes_random_randint(self, tmp_path):
        source = _setup_lines("set_variable",
                               {"variable": "roll", "value": "irandom(5) + 1"}, tmp_path)
        assert "roll = random.randint(0, 5) + 1" in source
        assert "import random" in source

    def test_random_becomes_random_uniform(self, tmp_path):
        source = _setup_lines("set_variable",
                               {"variable": "speed", "value": "random(4)"}, tmp_path)
        assert "speed = random.uniform(0, 4)" in source

    def test_choose_becomes_random_choice_of_a_list(self, tmp_path):
        source = _setup_lines("set_variable",
                               {"variable": "pick", "value": "choose(1, 2, 3)"}, tmp_path)
        assert "pick = random.choice([1, 2, 3])" in source

    def test_no_random_import_without_a_gm_builtin(self, tmp_path):
        source = _setup_lines("set_variable", {"variable": "x", "value": "5"}, tmp_path)
        assert "import random" not in source


class TestX4RealDiceRollChain:
    """samples/microbit_1's actual gesture_shake event: a chain of
    test_variable guards each followed by exactly one microbit_show_image,
    ending with an unconditional relative set_variable -- the real-world
    shape this exporter has to get right, not just a synthetic case."""

    def test_chain_of_guarded_single_actions(self, tmp_path):
        source = _create_actions([
            {"action": "set_variable", "parameters": {"variable": "roll", "value": "irandom(5) + 1"}},
            {"action": "test_variable",
             "parameters": {"variable": "roll", "value": "1", "operation": "equal"}},
            {"action": "microbit_show_image", "parameters": {"image": "HEART"}},
            {"action": "test_variable",
             "parameters": {"variable": "roll", "value": "2", "operation": "equal"}},
            {"action": "microbit_show_image", "parameters": {"image": "HAPPY"}},
            {"action": "set_variable",
             "parameters": {"variable": "rolls", "value": "1", "relative": True}},
        ], tmp_path)
        assert "roll = random.randint(0, 5) + 1" in source
        assert "if roll == (1):\n    display.show(Image.HEART)" in source
        assert "if roll == (2):\n    display.show(Image.HAPPY)" in source
        # The final relative set is unconditional -- not nested under
        # either guard, same as the flat list's own semantics.
        assert source.count("    rolls") == 0
        assert "\nrolls += (1)" in source

    def test_compiles(self, tmp_path):
        source = _create_actions([
            {"action": "set_variable", "parameters": {"variable": "roll", "value": "irandom(5) + 1"}},
            {"action": "test_variable",
             "parameters": {"variable": "roll", "value": "1", "operation": "equal"}},
            {"action": "microbit_show_image", "parameters": {"image": "HEART"}},
        ], tmp_path)
        # Exercise py_compile directly on this exact source via a temp file,
        # matching TestValidPython's own no-stub-needed reasoning.
        import py_compile
        f = tmp_path / "chain_main.py"
        f.write_text(source, encoding="utf-8")
        py_compile.compile(str(f), doraise=True)


class TestX4StartBlockAndElse:
    def test_start_block_group_as_the_guarded_unit(self, tmp_path):
        source = _create_actions([
            {"action": "microbit_if_button", "parameters": {"button": "a"}},
            {"action": "start_block", "parameters": {}},
            {"action": "set_variable", "parameters": {"variable": "score", "value": "1", "relative": True}},
            {"action": "microbit_show_image", "parameters": {"image": "HAPPY"}},
            {"action": "end_block", "parameters": {}},
        ], tmp_path)
        assert ("if button_a.is_pressed():\n"
                "    score += (1)\n"
                "    display.show(Image.HAPPY)") in source

    def test_else_action_after_a_single_guarded_action(self, tmp_path):
        source = _create_actions([
            {"action": "microbit_if_button", "parameters": {"button": "a"}},
            {"action": "microbit_show_image", "parameters": {"image": "HAPPY"}},
            {"action": "else_action", "parameters": {}},
            {"action": "microbit_show_image", "parameters": {"image": "SAD"}},
        ], tmp_path)
        assert ("if button_a.is_pressed():\n"
                "    display.show(Image.HAPPY)\n"
                "else:\n"
                "    display.show(Image.SAD)") in source

    def test_else_action_after_a_start_block_group(self, tmp_path):
        source = _create_actions([
            {"action": "microbit_if_button", "parameters": {"button": "a"}},
            {"action": "start_block", "parameters": {}},
            {"action": "microbit_show_image", "parameters": {"image": "HAPPY"}},
            {"action": "microbit_play_tone", "parameters": {"frequency": 440}},
            {"action": "end_block", "parameters": {}},
            {"action": "else_action", "parameters": {}},
            {"action": "microbit_show_image", "parameters": {"image": "SAD"}},
        ], tmp_path)
        assert ("if button_a.is_pressed():\n"
                "    display.show(Image.HAPPY)\n"
                "    music.pitch(440, 500)\n"
                "else:\n"
                "    display.show(Image.SAD)") in source

    def test_bare_block_with_no_guard_is_transparent(self, tmp_path):
        # start_block/end_block with no preceding question is a no-op
        # marker at runtime (runtime/action_executor.py only gives it
        # meaning while skipping) -- same indentation as its surroundings.
        source = _create_actions([
            {"action": "start_block", "parameters": {}},
            {"action": "microbit_show_image", "parameters": {"image": "HEART"}},
            {"action": "end_block", "parameters": {}},
        ], tmp_path)
        assert "\ndisplay.show(Image.HEART)" in source
        assert "    display.show(Image.HEART)" not in source

    def test_nested_start_blocks(self, tmp_path):
        source = _create_actions([
            {"action": "microbit_if_button", "parameters": {"button": "a"}},
            {"action": "start_block", "parameters": {}},
            {"action": "microbit_if_button", "parameters": {"button": "b"}},
            {"action": "start_block", "parameters": {}},
            {"action": "microbit_show_image", "parameters": {"image": "HAPPY"}},
            {"action": "end_block", "parameters": {}},
            {"action": "microbit_play_tone", "parameters": {"frequency": 880}},
            {"action": "end_block", "parameters": {}},
        ], tmp_path)
        assert ("if button_a.is_pressed():\n"
                "    if button_b.is_pressed():\n"
                "        display.show(Image.HAPPY)\n"
                "    music.pitch(880, 500)") in source

    def test_chained_guarded_question_as_the_guarded_unit(self, tmp_path):
        # A question guarding another bare question (no start_block) --
        # the recursive design produces well-defined nested if/else here,
        # a deliberate, documented improvement over the live simulator's
        # own single condition_was_false-flag ambiguity for this shape
        # (not relevant to any currently authored content -- Blockly
        # always wraps a multi-action guard in start_block/end_block).
        source = _create_actions([
            {"action": "microbit_if_button", "parameters": {"button": "a"}},
            {"action": "microbit_if_gesture", "parameters": {"gesture": "shake"}},
            {"action": "microbit_show_image", "parameters": {"image": "HAPPY"}},
        ], tmp_path)
        assert ("if button_a.is_pressed():\n"
                "    if accelerometer.is_gesture('shake'):\n"
                "        display.show(Image.HAPPY)") in source


def _events_main(events, tmp_path, board_version="v2"):
    """A main.py generated for an object with an arbitrary ``events``
    dict -- X5's event-polling tests need several different event names
    at once, not just one action at a time."""
    proj = tmp_path / "project.json"
    proj.write_text(json.dumps({
        "name": "TestProject",
        "assets": {"objects": {"microbit_1": {"events": events}}},
    }), encoding="utf-8")
    out = tmp_path / "out"
    export(str(proj), str(out), board_version=board_version)
    return (out / "microbit_1" / "main.py").read_text(encoding="utf-8")


def _one_event(name, action, parameters):
    return {name: {"actions": [{"action": action, "parameters": parameters}]}}


class TestX5ButtonEvents:
    def test_button_a_alone(self, tmp_path):
        source = _events_main(
            _one_event("microbit_button_a", "microbit_show_image", {"image": "HAPPY"}),
            tmp_path)
        assert "_button_a_now = button_a.is_pressed()" in source
        assert "if _button_a_edge:" in source
        assert "display.show(Image.HAPPY)" in source
        # b/ab aren't authored -- no guard for them, but the shared
        # state they'd need is still computed (button_a/b share it).
        assert "if _button_b_edge:" not in source
        assert "(_button_a_edge and _button_b_now)" not in source

    def test_button_b_alone(self, tmp_path):
        source = _events_main(
            _one_event("microbit_button_b", "microbit_show_image", {"image": "SAD"}),
            tmp_path)
        assert "if _button_b_edge:" in source
        assert "if _button_a_edge:" not in source

    def test_button_ab_combo(self, tmp_path):
        source = _events_main(
            _one_event("microbit_button_ab", "microbit_stop_sound", {}),
            tmp_path)
        assert ("if (_button_a_edge and _button_b_now) or "
                "(_button_b_edge and _button_a_now):") in source
        assert "music.stop()" in source

    def test_no_button_state_without_any_button_event(self, tmp_path):
        source = _events_main(
            _one_event("microbit_gesture_shake", "microbit_stop_sound", {}),
            tmp_path)
        assert "_prev_button_a" not in source
        assert "button_a.is_pressed()" not in source

    def test_all_three_button_events_together(self, tmp_path):
        source = _events_main({
            "microbit_button_a": {"actions": [
                {"action": "microbit_show_image", "parameters": {"image": "HAPPY"}}]},
            "microbit_button_b": {"actions": [
                {"action": "microbit_show_image", "parameters": {"image": "SAD"}}]},
            "microbit_button_ab": {"actions": [
                {"action": "microbit_play_tone", "parameters": {"frequency": 880}}]},
        }, tmp_path)
        assert "if _button_a_edge:" in source
        assert "if _button_b_edge:" in source
        assert "(_button_a_edge and _button_b_now)" in source
        # Shared state initialised exactly once, not once per event.
        assert source.count("_prev_button_a = False") == 1


class TestX5LogoAndPinEvents:
    def test_logo_touched_on_v2(self, tmp_path):
        source = _events_main(
            _one_event("microbit_logo_touched", "microbit_clear_display", {}),
            tmp_path, board_version="v2")
        assert "pin_logo.is_touched()" in source
        assert "display.clear()" in source

    def test_logo_touched_skipped_and_warned_on_v1(self, tmp_path):
        source = _events_main(
            _one_event("microbit_logo_touched", "microbit_clear_display", {}),
            tmp_path, board_version="v1")
        assert "pin_logo" not in source
        assert "display.clear()" not in source
        assert "Not exported -- needs a V2 board" in source
        assert "microbit_logo_touched" in source

    def test_pin_0_1_2(self, tmp_path):
        for n in (0, 1, 2):
            source = _events_main(
                _one_event(f"microbit_pin_{n}", "microbit_clear_display", {}),
                tmp_path)
            assert f"pin{n}.is_touched()" in source
            assert f"_prev_pin{n} = False" in source

    def test_unused_pins_get_no_state(self, tmp_path):
        source = _events_main(
            _one_event("microbit_pin_0", "microbit_clear_display", {}),
            tmp_path)
        assert "_prev_pin1" not in source
        assert "_prev_pin2" not in source


class TestX5GestureEvents:
    def test_every_gesture_event_maps_to_its_raw_name(self, tmp_path):
        cases = [
            ("microbit_gesture_shake", "shake"),
            ("microbit_gesture_logo_up", "up"),
            ("microbit_gesture_logo_down", "down"),
            ("microbit_gesture_tilt_left", "left"),
            ("microbit_gesture_tilt_right", "right"),
            ("microbit_gesture_screen_up", "face up"),
            ("microbit_gesture_screen_down", "face down"),
            ("microbit_gesture_free_fall", "freefall"),
            ("microbit_gesture_2g", "2g"),
            ("microbit_gesture_3g", "3g"),
            ("microbit_gesture_6g", "6g"),
            ("microbit_gesture_8g", "8g"),
        ]
        for event_name, raw in cases:
            source = _events_main(
                _one_event(event_name, "microbit_stop_sound", {}), tmp_path)
            assert f"accelerometer.was_gesture({raw!r})" in source

    def test_gestures_need_no_hand_rolled_state(self, tmp_path):
        source = _events_main(
            _one_event("microbit_gesture_shake", "microbit_stop_sound", {}),
            tmp_path)
        assert "_prev" not in source


class TestX5SoundEvents:
    def test_loud_sound_on_v2(self, tmp_path):
        source = _events_main(
            _one_event("microbit_loud_sound", "microbit_show_image", {"image": "YES"}),
            tmp_path, board_version="v2")
        assert "microphone.sound_level()" in source
        assert '_sound_state != "loud" and _sound_level_now > 196' in source
        assert "display.show(Image.YES)" in source

    def test_quiet_sound_on_v2(self, tmp_path):
        source = _events_main(
            _one_event("microbit_quiet_sound", "microbit_show_image", {"image": "NO"}),
            tmp_path, board_version="v2")
        assert '_sound_state != "quiet" and _sound_level_now < 118' in source
        assert "display.show(Image.NO)" in source

    def test_both_loud_and_quiet_share_one_state_machine(self, tmp_path):
        source = _events_main({
            "microbit_loud_sound": {"actions": [
                {"action": "microbit_show_image", "parameters": {"image": "YES"}}]},
            "microbit_quiet_sound": {"actions": [
                {"action": "microbit_show_image", "parameters": {"image": "NO"}}]},
        }, tmp_path)
        assert source.count('_sound_state = "quiet"') == 2  # init + the elif branch
        assert "elif" in source

    def test_sound_events_skipped_and_warned_on_v1(self, tmp_path):
        source = _events_main(
            _one_event("microbit_loud_sound", "microbit_show_image", {"image": "YES"}),
            tmp_path, board_version="v1")
        assert "microphone" not in source
        assert "Not exported -- needs a V2 board" in source
        assert "microbit_loud_sound" in source


class TestX5RadioReceivedEvent:
    def test_radio_received_sets_both_variables(self, tmp_path):
        source = _events_main(
            _one_event("microbit_radio_received", "set_variable",
                       {"variable": "last", "value": "radio_number"}),
            tmp_path)
        assert "_radio_msg = radio.receive()" in source
        assert "if _radio_msg is not None:" in source
        assert "radio_string = _radio_msg" in source
        assert "radio_number = _radio_as_number(_radio_msg)" in source
        assert "last = radio_number" in source

    def test_radio_as_number_helper_mirrors_radio_py(self, tmp_path):
        source = _events_main(
            _one_event("microbit_radio_received", "set_variable",
                       {"variable": "last", "value": "radio_number"}),
            tmp_path)
        assert "def _radio_as_number(value):" in source
        assert "int(n) if n == int(n) else n" in source

    def test_no_radio_as_number_helper_without_the_event(self, tmp_path):
        source = _setup_lines("microbit_radio_send", {"value": "1"}, tmp_path)
        assert "_radio_as_number" not in source

    def test_radio_on_injected_once_for_the_event_alone(self, tmp_path):
        # Confirms the event (not just the radio_send/radio_set_group
        # actions from X3) also triggers the one-time radio.on().
        source = _events_main(
            _one_event("microbit_radio_received", "microbit_stop_sound", {}),
            tmp_path)
        assert source.count("radio.on()") == 1


class TestX5UnsupportedDoneEvents:
    def test_display_done_is_unsupported_not_dropped(self, tmp_path):
        source = _events_main(
            _one_event("microbit_display_done", "microbit_clear_display", {}),
            tmp_path)
        assert "display.clear()" not in source
        assert "Not exported" in source
        assert "microbit_display_done" in source

    def test_sound_done_is_unsupported_not_dropped(self, tmp_path):
        source = _events_main(
            _one_event("microbit_sound_done", "microbit_stop_sound", {}),
            tmp_path)
        assert "music.stop()" not in source
        assert "Not exported" in source
        assert "microbit_sound_done" in source

    def test_empty_done_events_are_silent(self, tmp_path):
        # An event present in the JSON with no actions at all (e.g. an
        # authored-then-emptied handler) shouldn't appear as a warning.
        source = _events_main({"microbit_display_done": {"actions": []}}, tmp_path)
        assert "microbit_display_done" not in source


class TestX5RealSampleEndToEnd:
    """samples/microbit_1 end to end: Create + button_a/b + gesture_shake
    (the dice chain) + logo_touched (scroll + show_number) all together,
    through the real sample file -- not a synthetic fixture."""

    def _generated(self):
        import tempfile
        out = tempfile.mkdtemp()
        export("samples/microbit_1/project.json", out)
        from pathlib import Path
        return (Path(out) / "microbit_1" / "main.py").read_text(encoding="utf-8")

    def test_compiles(self):
        import py_compile
        import tempfile
        out = tempfile.mkdtemp()
        export("samples/microbit_1/project.json", out)
        from pathlib import Path
        py_compile.compile(str(Path(out) / "microbit_1" / "main.py"), doraise=True)

    def test_create_event_setup(self):
        source = self._generated()
        assert "rolls = 0" in source
        assert "display.show(Image.HEART)" in source

    def test_button_events(self):
        source = self._generated()
        assert "if _button_a_edge:\n        display.show(Image.HAPPY)" in source
        assert "if _button_b_edge:\n        display.show(Image.SAD)" in source

    def test_gesture_shake_dice_chain(self):
        source = self._generated()
        assert "if accelerometer.was_gesture('shake'):" in source
        assert "roll = random.randint(0, 5) + 1" in source
        assert "if roll == (6):" in source
        assert "rolls += (1)" in source

    def test_logo_touched_scroll_and_number(self):
        source = self._generated()
        assert 'display.scroll("Rolls", delay=150)' in source
        assert "display.show(rolls)" in source

    def test_only_one_while_loop(self):
        source = self._generated()
        assert source.count("while True:") == 1
