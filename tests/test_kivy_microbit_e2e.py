"""Stage P / K6: the real ``microbit_1`` sample, exported for Kivy and played.

Kivy cannot run in CI, so the whole generated game (scene + objects + shipped
``microbit_sim`` package) is imported under the stub kivy of the K1 harness and
driven the way a player would: create event, touch the buttons on the drawn
board, shake it, touch the logo. What happens is compared with a twin
``MicrobitSimulator`` driven directly, so the check is "the exported game does
what the simulator does", not a re-statement of the sample.
"""
import importlib
import json
import py_compile
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_microbit_actions import _stub_kivy  # noqa: E402

from extensions.microbit.layout import strip_layout  # noqa: E402
from extensions.microbit.simulator import MicrobitSimulator  # noqa: E402

SAMPLE = ROOT / "samples" / "microbit_1"
DT = 1.0 / 60.0


@pytest.fixture(scope="module")
def exported():
    from core.project_manager import merge_object_file
    from export.Kivy import code_generator
    from export.Kivy.kivy_exporter import KivyExporter
    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        merge_object_file(obj, json.loads(
            (SAMPLE / "objects" / f"{name}.json").read_text(encoding="utf-8")))
    data["assets"]["rooms"]["room0"] = json.loads(
        (SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    code_generator._UNSUPPORTED_EVENTS.clear()
    code_generator._UNSUPPORTED_ACTIONS.clear()
    out = Path(tempfile.mkdtemp(prefix="mb1_e2e_")) / "export"
    assert KivyExporter(data, SAMPLE, out).export()
    return out, data, code_generator.get_unsupported_events(), code_generator.get_unsupported_actions()


def _start(game):
    scene_mod = importlib.import_module("scenes.room0")
    scene = scene_mod.Room0.__new__(scene_mod.Room0)
    cls = importlib.import_module("objects.microbit_1").Microbit1
    board = cls.__new__(cls)
    board.object_name, board.visible, board.has_sprite = "microbit_1", True, False
    board.x, board.y, board.width, board.height = 100, 150, 32, 32
    board.alarms = [-1] * 12
    group = type("G", (), {"clear": lambda s: None})
    sys.modules["objects.base_object"].InstructionGroup = lambda: group()
    board.canvas = type("C", (), {"after": type("A", (), {"add": lambda s, g: None})()})()
    board._dq_render_cmd = lambda *a: None
    scene.instances, scene.room_height = [board], 480
    board.on_create()                                          # the sample's Create event
    return scene, board


def _frames(scene, n=1):
    for _ in range(n):
        scene._update_extensions(DT)


def _tap(scene, x, y, button="left", frames=2):
    scene._extension_touch_down(None, x, y, button)
    _frames(scene, frames)
    scene._extension_touch_up(None, x, y, button)
    _frames(scene, frames)


def _twin_after(spec, frames):
    sim = MicrobitSimulator()
    sim.show_image(spec)
    for _ in range(frames):
        sim.update(DT)
    return sim.display


def test_the_whole_export_compiles_and_nothing_micro_bit_is_dropped(exported):
    out, _, events, actions = exported
    for path in out.rglob("*.py"):
        py_compile.compile(str(path), doraise=True)
    assert not [e for e in events if e.startswith("microbit_")], events
    assert not [a for a in actions if a.startswith("microbit_")], actions


def test_the_support_package_is_complete(exported):
    pkg = exported[0] / "game" / "microbit_sim"
    assert sorted(p.name for p in pkg.glob("*.py")) == sorted([
        "__init__.py", "simulator.py", "font.py", "images.py", "sound.py", "melodies.py",
        "radio.py", "layout.py", "state.py", "draw.py", "touch.py", "speaker.py"])


def test_the_create_event_runs_and_sets_the_variable_and_the_heart(exported):
    with _stub_kivy(exported[0] / "game"):
        scene, board = _start(exported[0] / "game")
        _frames(scene, 2)
        assert board.rolls == 0
        assert board._mb_sim().display == _twin_after("HEART", 2)


def test_touching_button_a_then_b_shows_happy_then_sad(exported):
    with _stub_kivy(exported[0] / "game"):
        scene, board = _start(exported[0] / "game")
        layout = board._mb_layout(480)
        _tap(scene, *layout.buttons["a"][:2])
        assert board._mb_sim().display == _twin_after("HAPPY", 4)
        _tap(scene, *layout.buttons["b"][:2])
        assert board._mb_sim().display == _twin_after("SAD", 4)


def test_the_right_click_chord_presses_both_buttons_and_fires_what_the_simulator_fires(exported):
    """The sample authors button A and button B (not A+B). Pressing both at once
    fires every event the simulator reports for it, in that order."""
    from extensions.microbit.events import event_name_for
    twin = MicrobitSimulator()
    twin.set_button("a", True)
    twin.set_button("b", True)
    expected = [event_name_for(k, d) for k, d in twin.update(DT)]
    assert "microbit_button_ab" in expected
    with _stub_kivy(exported[0] / "game"):
        scene, board = _start(exported[0] / "game")
        fired = []
        for name in ("microbit_button_a", "microbit_button_b"):
            real = getattr(board, "on_" + name)
            setattr(board, "on_" + name, lambda n=name, r=real: (fired.append(n), r()))
        scene._extension_touch_down(None, *board._mb_layout(480).buttons["a"][:2], "right")
        _frames(scene, 1)
        assert fired == [n for n in expected if n in ("microbit_button_a", "microbit_button_b")]
        assert board._mb_sim().buttons["a"] and board._mb_sim().buttons["b"]


def _dice_faces():
    obj = json.loads((SAMPLE / "objects" / "microbit_1.json").read_text(encoding="utf-8"))
    actions = obj["events"]["microbit_gesture_shake"]
    actions = actions["actions"] if isinstance(actions, dict) else actions
    faces, current = {}, None
    for action in actions:
        if action["action"] == "test_variable":
            current = int(action["parameters"]["value"])
        elif action["action"] == "microbit_show_image" and current is not None:
            faces[current] = action["parameters"]["image"]
    return faces


def test_shaking_the_board_rolls_a_die_and_shows_its_face(exported):
    faces = _dice_faces()
    assert sorted(faces) == [1, 2, 3, 4, 5, 6]
    with _stub_kivy(exported[0] / "game"):
        scene, board = _start(exported[0] / "game")
        sx, sy, sw, sh = strip_layout(board._mb_layout(480)).shake
        _tap(scene, sx + sw // 2, sy + sh // 2, frames=3)
        _frames(scene, 6)
        assert 1 <= board.roll <= 6
        assert board._mb_sim().display == _twin_after(faces[int(board.roll)], 6)


def test_touching_the_logo_scrolls_the_word_then_shows_the_count(exported):
    with _stub_kivy(exported[0] / "game"):
        scene, board = _start(exported[0] / "game")
        lx, ly, _, _ = board._mb_layout(480).logo
        _tap(scene, lx, ly)
        twin = MicrobitSimulator()
        twin.scroll_text("Rolls", 0.12)
        twin.show_number(0)
        seen_scroll = False
        for _ in range(400):
            _frames(scene, 1)
            twin.update(DT)
            seen_scroll = seen_scroll or board._mb_sim().display != _twin_after("HEART", 0)
        assert seen_scroll
        assert board._mb_sim().display == twin.display


def test_the_keyboard_is_off_unless_the_instance_opts_in(exported):
    with _stub_kivy(exported[0] / "game"):
        scene, board = _start(exported[0] / "game")
        scene._extension_key_down(97)
        _frames(scene, 3)
        assert board._mb_sim().display == _twin_after("HEART", 3)
        board.microbit_keyboard = True
        scene._extension_key_down(97)
        _frames(scene, 3)
        assert board._mb_sim().display == _twin_after("HAPPY", 3)


def test_the_board_is_drawn_every_frame(exported):
    with _stub_kivy(exported[0] / "game"):
        scene, board = _start(exported[0] / "game")
        drawn = []
        board._dq_render_cmd = lambda group, cmd, room_h: drawn.append(cmd["type"])
        _frames(scene, 1)
        assert {"rectangle", "circle", "ellipse", "scaled_text"} <= set(drawn)
