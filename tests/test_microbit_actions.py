"""micro:bit actions (docs/MICROBIT_EXTENSION_PLAN.md, Stage S3).

Schemas reach ``ACTION_TYPES`` through the loader; handlers are dispatched
through ``ex.action_handlers`` after ``load_all_plugins`` (the plugin
landmines in the plan), and the conditions are driven through the real
``execute_action_list`` so the then/else wiring is covered too.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest

from events.plugin_loader import load_all_plugins
from runtime.action_executor import ActionExecutor

ACTION_NAMES = [
    "microbit_show_image", "microbit_scroll_text", "microbit_show_number",
    "microbit_set_pixel", "microbit_clear_display", "microbit_set_brightness",
    "microbit_read_sensor", "microbit_if_button", "microbit_if_gesture",
    "microbit_if_tilt", "microbit_if_pixel",
]


class _Room:
    def __init__(self):
        self.instances = []
        self.extension_state = {}


class _GR:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}


class _Inst:
    def __init__(self, name="microbit_1"):
        self.object_name = name
        self.action_executor = None
        self.extension_state = {}
        self.x = self.y = 0.0


@pytest.fixture
def board():
    """(executor, a micro:bit instance with a simulator, its simulator)."""
    from runtime.game_runner import GameRoom
    gr = _GR(_Room())
    ex = ActionExecutor(game_runner=gr)
    load_all_plugins(ex)
    room = GameRoom("r", {"width": 100, "height": 100, "instances": [
        {"object": "microbit_1", "x": 0, "y": 0}]}, action_executor=None)
    inst = room.instances[0]
    inst.action_executor = ex
    sim = inst.extension_state["microbit"]["simulator"]
    return ex, inst, sim


def _do(ex, inst, name, **params):
    return ex.action_handlers[name](inst, params)


# --- schemas -----------------------------------------------------------------

def test_schemas_register_under_the_plugin_category():
    load_all_plugins()
    from events.action_types import ACTION_TYPES, get_action_type
    for name in ACTION_NAMES:
        assert name in ACTION_TYPES, name
        action = get_action_type(name)
        assert action.category == "micro:bit"
        assert action.display_name and action.description


def test_schemas_are_english_and_plugin_owned():
    # Plugin actions must NOT also be in the static dict (shadowing landmine);
    # reading the source avoids the loader having already merged them.
    src = (REPO_ROOT / "events" / "action_types.py").read_text(encoding="utf-8")
    assert "microbit_" not in src


def test_manifest_lists_exactly_the_actions_provided():
    import json
    manifest = json.loads((REPO_ROOT / "extensions" / "microbit"
                           / "extension.json").read_text(encoding="utf-8"))
    assert sorted(manifest["provides_actions"]) == sorted(ACTION_NAMES)


def test_every_action_has_a_handler(board):
    ex, _, _ = board
    for name in ACTION_NAMES:
        assert name in ex.action_handlers, name


def test_picker_tab_is_registered():
    load_all_plugins()
    from actions.core import GM80_ACTION_TABS
    assert GM80_ACTION_TABS["microbit"]["name"] == "micro:bit"


def test_extension_is_offered_in_project_settings(qapp):
    load_all_plugins()
    from dialogs.project_dialogs import ProjectSettingsDialog
    dlg = ProjectSettingsDialog(None, {"name": "t", "settings": {}})
    try:
        assert "microbit" in dlg.extension_checks
    finally:
        dlg.deleteLater()


# --- display -----------------------------------------------------------------

def test_show_image_by_name_and_by_grid(board):
    ex, inst, sim = board
    _do(ex, inst, "microbit_show_image", image="HEART")
    assert sim.display[0] == [0, 9, 0, 9, 0]
    sim.clear()
    _do(ex, inst, "microbit_show_image", image="90000:09000:00900:00090:00009")
    assert [sim.display[i][i] for i in range(5)] == [9] * 5
    assert sim.display[0][4] == 0


def test_show_image_bad_name_is_ignored_not_fatal(board):
    ex, inst, sim = board
    _do(ex, inst, "microbit_show_image", image="NOT_AN_IMAGE")
    assert sim.display == [[0] * 5 for _ in range(5)]
    assert not sim.busy


def test_show_image_hold_keeps_it_before_the_next_item(board):
    ex, inst, sim = board
    _do(ex, inst, "microbit_show_image", image="HEART", hold=500)
    _do(ex, inst, "microbit_show_image", image="SAD")
    heart = [row[:] for row in sim.display]
    sim.update(0.4)
    assert sim.display == heart
    sim.update(0.2)
    assert sim.display[3] == [0, 9, 9, 9, 0]   # SAD's mouth


def test_scroll_text_queues_and_plays_with_the_delay(board):
    ex, inst, sim = board
    _do(ex, inst, "microbit_scroll_text", text='"Hi"', delay=100)
    assert sim.busy
    events = []
    for _ in range(100):
        events += sim.update(0.1)
    assert ("display_done", None) in events
    assert not sim.busy


def test_scroll_text_quoted_text_with_a_dash_is_not_evaluated(board):
    ex, inst, sim = board
    seen = []
    sim.scroll_text = lambda text, delay=0.15: seen.append(text)
    _do(ex, inst, "microbit_scroll_text", text='"W A S D - Move"')
    assert seen == ["W A S D - Move"]


def test_scroll_text_evaluates_expressions_and_variables(board):
    ex, inst, sim = board
    inst.score = 4
    seen = []
    sim.scroll_text = lambda text, delay=0.15: seen.append(text)
    _do(ex, inst, "microbit_scroll_text", text="2 + 3")
    assert seen == ["5"]


def test_show_number_single_digit_is_still_longer_scrolls(board):
    ex, inst, sim = board
    from extensions.microbit.simulator import glyph_image
    _do(ex, inst, "microbit_show_number", value="7")
    assert sim.display == glyph_image("7")
    sim.update(1.0)
    assert sim.display == glyph_image("7")      # a single digit holds
    _do(ex, inst, "microbit_show_number", value="42")
    assert sim.busy                              # two characters scroll


def test_show_number_accepts_an_expression(board):
    ex, inst, sim = board
    seen = []
    sim.show_number = lambda v, delay=0.15: seen.append(v)
    _do(ex, inst, "microbit_show_number", value="3 * 2")
    assert seen == [6]
    assert isinstance(seen[0], int)


def test_set_pixel_and_clear(board):
    ex, inst, sim = board
    _do(ex, inst, "microbit_set_pixel", x=2, y=3, brightness=7)
    assert sim.get_pixel(2, 3) == 7
    _do(ex, inst, "microbit_set_pixel", x=1, y=1)           # default 9
    assert sim.get_pixel(1, 1) == 9
    _do(ex, inst, "microbit_set_pixel", x=9, y=9, brightness=9)  # off-board
    _do(ex, inst, "microbit_clear_display")
    assert sim.display == [[0] * 5 for _ in range(5)]


def test_set_brightness_clamps(board):
    ex, inst, sim = board
    _do(ex, inst, "microbit_set_brightness", brightness=128)
    assert sim.brightness == 128
    _do(ex, inst, "microbit_set_brightness", brightness=999)
    assert sim.brightness == 255


def test_actions_on_a_non_microbit_instance_do_nothing(board):
    ex, _, _ = board
    other = _Inst("obj_player")
    other.action_executor = ex
    for name in ACTION_NAMES:
        result = ex.action_handlers[name](other, {})
        assert result in (None, False)


# --- sensors -----------------------------------------------------------------

def test_read_sensor_into_an_instance_variable(board):
    ex, inst, sim = board
    sim.set_acceleration(120, -340, -1000)
    sim.set_compass_heading(270)
    sim.set_light_level(88)
    sim.set_temperature(19)
    sim.set_sound_level(50)
    sim.set_pin_analog(1, 512)
    expected = {
        "accelerometer x": 120, "accelerometer y": -340,
        "accelerometer z": -1000, "compass heading": 270, "light level": 88,
        "temperature": 19, "sound level": 50, "pin 1 analog": 512,
        "pin 0 analog": 0,
    }
    for sensor, value in expected.items():
        _do(ex, inst, "microbit_read_sensor", sensor=sensor, variable="reading")
        assert inst.reading == value, sensor
    _do(ex, inst, "microbit_read_sensor", sensor="acceleration strength",
        variable="reading")
    assert inst.reading == round((120 ** 2 + 340 ** 2 + 1000 ** 2) ** 0.5)


def test_read_sensor_into_a_global_variable(board):
    ex, inst, sim = board
    sim.set_light_level(200)
    _do(ex, inst, "microbit_read_sensor", sensor="light level",
        variable="global.lux")
    assert ex.game_runner.global_variables["lux"] == 200


def test_read_sensor_unknown_sensor_writes_nothing(board):
    ex, inst, sim = board
    _do(ex, inst, "microbit_read_sensor", sensor="gravity", variable="v")
    assert not hasattr(inst, "v")


def test_every_listed_sensor_is_readable(board):
    from extensions.microbit.actions import SENSORS
    from extensions.microbit.handlers import read_sensor
    _, _, sim = board
    for sensor in SENSORS:
        assert read_sensor(sim, sensor) is not None, sensor


# --- conditions --------------------------------------------------------------

def test_if_button_reflects_held_state(board):
    ex, inst, sim = board
    assert _do(ex, inst, "microbit_if_button", button="a") is False
    sim.set_button("a", True)
    assert _do(ex, inst, "microbit_if_button", button="a") is True
    assert _do(ex, inst, "microbit_if_button", button="b") is False
    assert _do(ex, inst, "microbit_if_button", button="ab") is False
    sim.set_button("b", True)
    assert _do(ex, inst, "microbit_if_button", button="ab") is True
    sim.set_logo_touched(True)
    assert _do(ex, inst, "microbit_if_button", button="logo") is True


def test_if_gesture_tracks_the_current_posture(board):
    ex, inst, sim = board
    assert _do(ex, inst, "microbit_if_gesture", gesture="face up") is False
    sim.update(0.2)   # a resting board settles to "face up" (plan, S2)
    assert _do(ex, inst, "microbit_if_gesture", gesture="face up") is True
    assert _do(ex, inst, "microbit_if_gesture", gesture="shake") is False


def test_if_tilt_comparisons(board):
    ex, inst, sim = board
    sim.set_acceleration(500, -200, -900)
    check = lambda **p: _do(ex, inst, "microbit_if_tilt", **p)
    assert check(axis="x", comparison=">", value=300) is True
    assert check(axis="x", comparison="<", value=300) is False
    assert check(axis="y", comparison="<=", value=-200) is True
    assert check(axis="y", comparison="==", value=-200) is True
    assert check(axis="z", comparison="!=", value=-900) is False
    assert check(axis="q", comparison=">", value=0) is False
    assert check(axis="x", comparison="nonsense", value=100) is True  # > default


def test_if_pixel(board):
    ex, inst, sim = board
    assert _do(ex, inst, "microbit_if_pixel", x=2, y=2) is False
    sim.set_pixel(2, 2, 5)
    assert _do(ex, inst, "microbit_if_pixel", x=2, y=2) is True
    assert _do(ex, inst, "microbit_if_pixel", x=2, y=2,
               comparison="==", value=5) is True
    assert _do(ex, inst, "microbit_if_pixel", x=7, y=0) is False


def test_condition_drives_then_and_else_branches(board):
    ex, inst, sim = board
    sim.set_button("a", True)
    ex.execute_action_list(inst, [{
        "action": "microbit_if_button",
        "parameters": {
            "button": "a",
            "then_actions": [{"action": "microbit_set_pixel",
                              "parameters": {"x": 0, "y": 0, "brightness": 9}}],
            "else_actions": [{"action": "microbit_set_pixel",
                              "parameters": {"x": 4, "y": 4, "brightness": 9}}],
        },
    }])
    assert sim.get_pixel(0, 0) == 9 and sim.get_pixel(4, 4) == 0
    sim.set_button("a", False)
    ex.execute_action_list(inst, [{
        "action": "microbit_if_button",
        "parameters": {
            "button": "a",
            "then_actions": [{"action": "microbit_set_pixel",
                              "parameters": {"x": 1, "y": 1}}],
            "else_actions": [{"action": "microbit_set_pixel",
                              "parameters": {"x": 4, "y": 4}}],
        },
    }])
    assert sim.get_pixel(1, 1) == 0 and sim.get_pixel(4, 4) == 9


def test_false_condition_skips_the_next_action_in_a_flat_list(board):
    ex, inst, sim = board
    ex.execute_action_list(inst, [
        {"action": "microbit_if_button", "parameters": {"button": "a"}},
        {"action": "microbit_set_pixel", "parameters": {"x": 0, "y": 0}},
        {"action": "microbit_set_pixel", "parameters": {"x": 1, "y": 0}},
    ])
    assert sim.get_pixel(0, 0) == 0     # guarded -> skipped
    assert sim.get_pixel(1, 0) == 9     # unguarded -> ran
