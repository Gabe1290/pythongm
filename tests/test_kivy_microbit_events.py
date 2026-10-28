"""Stage P / K2: micro:bit events and the per-frame step on the Kivy export.

The generated scene steps every board after collision and calls ``on_<event>``
on the board's instance for what the simulator reports. Kivy cannot run in CI,
so the real generated scene/object are imported under a stub ``kivy`` (the K1
harness) and driven; what fires is compared with the desktop mapping
(``events.event_name_for``) for the same simulator script.
"""
import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_microbit_actions import _stub_kivy, _export  # noqa: E402
from test_microbit_export_fallthrough import _action  # noqa: E402

DT = 1.0 / 60.0


def _all_event_names():
    from extensions.microbit.events import MICROBIT_EVENT_TYPES
    return sorted(MICROBIT_EVENT_TYPES)


def _kivy_events():
    return {name: {"actions": [_action("microbit_show_number")]} for name in _all_event_names()}


def _scene_with_boards(game_dir, count=1):
    scene_mod = importlib.import_module("scenes.room0")
    obj_mod = importlib.import_module("objects.microbit_1")
    scene = scene_mod.Room0.__new__(scene_mod.Room0)
    boards = []
    for _ in range(count):
        inst = obj_mod.Microbit1.__new__(obj_mod.Microbit1)
        inst.object_name = "microbit_1"
        boards.append(inst)
    scene.instances = list(boards)
    scene.room_height = 480
    for inst in boards:
        inst._mb_draw = lambda room_h: None      # drawing is tests/test_kivy_microbit_draw.py
    fired = []
    for inst in boards:
        for name in _all_event_names():
            setattr(inst, "on_" + name, lambda n=name, i=inst: fired.append((boards.index(i), n)))
    return scene, boards, fired


def test_every_event_gets_a_handler_and_none_is_reported_unsupported():
    from export.Kivy.code_generator import get_unsupported_events, _UNSUPPORTED_EVENTS
    _UNSUPPORTED_EVENTS.clear()
    game = _export(_kivy_events())
    text = (game / "objects" / "microbit_1.py").read_text(encoding="utf-8")
    for name in _all_event_names():
        assert "def on_%s(self):" % name in text, name
    assert not [e for e in get_unsupported_events() if e.startswith("microbit_")]


def test_the_scene_has_the_frame_hook_after_collision():
    game = _export(_kivy_events())
    text = (game / "scenes" / "room0.py").read_text(encoding="utf-8")
    assert text.index("self._update_extensions(dt)") > text.index("6b. NEGATED COLLISION")
    assert text.index("self._update_extensions(dt)") < text.index("7. END STEP EVENTS")


def test_event_tables_match_events_py():
    from extensions.microbit import events
    ns = {}
    exec((ROOT / "extensions" / "microbit" / "export_kivy.py").read_text(encoding="utf-8"), ns)
    game = _export(_kivy_events())
    with _stub_kivy(game):
        scene = importlib.import_module("scenes.room0").Room0.__new__(
            importlib.import_module("scenes.room0").Room0)
        combos = [("button", d) for d in ("a", "b", "ab", "x")] + [
            ("logo", "touched"), ("pin", 0), ("pin", 1), ("pin", 2), ("pin", 3),
            ("sound", "loud"), ("sound", "quiet"), ("display_done", None),
            ("sound_done", None), ("radio", "hi"), ("radio", 5), ("sound_note", (1, 2)),
            ("gesture", "nonsense")] + [("gesture", g) for g in events.GESTURE_NAMES]
        for kind, detail in combos:
            assert scene._mb_event_name(kind, detail) == events.event_name_for(kind, detail), (kind, detail)
    assert set(ns["EVENT_METHODS"]) == set(events.MICROBIT_EVENT_TYPES)


def _script_a(sim):
    sim.set_button("a", True)


def _script_ab(sim):
    sim.set_button("a", True)
    sim.set_button("b", True)


def _script_shake(sim):
    sim.shake()


def _script_pin_logo(sim):
    sim.set_pin_touched(1, True)
    sim.set_logo_touched(True)


def _script_sound(sim):
    sim.set_sound_level(250)


def _script_display(sim):
    sim.show_number(3)


SCRIPTS = [_script_a, _script_ab, _script_shake, _script_pin_logo, _script_sound, _script_display]


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda s: s.__name__)
def test_events_fired_equal_the_desktop_mapping(script):
    from extensions.microbit.events import event_name_for
    from extensions.microbit.simulator import MicrobitSimulator
    twin = MicrobitSimulator()
    script(twin)
    expected = []
    for _ in range(90):
        expected += [event_name_for(k, d) for k, d in twin.update(DT)]
    expected = [e for e in expected if e]
    assert expected, "script produced no events"
    game = _export(_kivy_events())
    with _stub_kivy(game):
        scene, boards, fired = _scene_with_boards(game)
        script(boards[0]._mb_sim())
        for _ in range(90):
            scene._update_extensions(DT)
    assert [n for _, n in fired] == expected


def test_radio_reaches_the_other_board_in_the_same_group_and_sets_the_variables():
    game = _export(_kivy_events())
    with _stub_kivy(game):
        scene, boards, fired = _scene_with_boards(game, count=2)
        boards[0]._mb_radio_send("hello")
        scene._update_extensions(DT)
        scene._update_extensions(DT)
    assert fired == [(1, "microbit_radio_received")]            # a board never hears itself
    assert boards[1].radio_string == "hello" and boards[1].radio_number == 0
    assert not hasattr(boards[0], "radio_string")


def test_radio_in_another_group_is_not_heard():
    game = _export(_kivy_events())
    with _stub_kivy(game):
        scene, boards, fired = _scene_with_boards(game, count=2)
        boards[1]._mb_radio_set_group(7)
        boards[0]._mb_radio_send(5)
        for _ in range(3):
            scene._update_extensions(DT)
    assert fired == []


def test_a_room_without_a_board_is_untouched():
    game = _export(_kivy_events())
    with _stub_kivy(game):
        scene, boards, fired = _scene_with_boards(game)
        boards[0].object_name = "wall"
        scene._update_extensions(DT)
    assert fired == [] and getattr(boards[0], "_mb_simulator", None) is None


def test_a_long_frame_is_capped():
    """A stalled frame (dt = 5 s) must not run five seconds of simulation."""
    game = _export(_kivy_events())
    with _stub_kivy(game):
        scene, boards, fired = _scene_with_boards(game)
        sim = boards[0]._mb_sim()
        seen = []
        real = sim.update
        sim.update = lambda dt: (seen.append(dt), real(dt))[1]
        scene._update_extensions(5.0)
    assert seen == [0.1]
