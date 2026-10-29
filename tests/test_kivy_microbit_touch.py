"""Stage P / K4: touch and keyboard control of the micro:bit on the Kivy export.

``kivy_touch.py`` (shipped as ``microbit_sim/touch.py``) mirrors the desktop's
``input.py``. Both are driven here with the same gestures and key sequences and
the simulator state they leave behind is compared; the generated scene's hooks
are then driven under the stub kivy for coordinates, keycodes, swallowing and
the opt-in keyboard.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_microbit_draw import _board  # noqa: E402
from test_kivy_microbit_actions import _stub_kivy, _export  # noqa: E402

from extensions.microbit import input as desktop  # noqa: E402
from extensions.microbit import kivy_touch as kt  # noqa: E402
from extensions.microbit.layout import layout_for, strip_layout  # noqa: E402
from extensions.microbit.simulator import MicrobitSimulator  # noqa: E402
from extensions.microbit.state import attach_simulator, simulator_of  # noqa: E402


class _Inst:
    def __init__(self, x=450, y=250, **attrs):
        self.x, self.y, self.sprite, self.visible = x, y, None, True
        self.__dict__.update(attrs)
        attach_simulator(self, MicrobitSimulator())


class _Runner:
    def __init__(self, *instances):
        self.current_room = type("R", (), {"instances": list(instances)})()


def _fingerprint(sim):
    return (dict(sim.buttons), sim.logo_touched, dict(sim.pins_touched),
            tuple(sim.acceleration), sim.light_level, sim.temperature,
            sim.compass_heading, sim.sound_level, sim.current_gesture)


def _points(layout):
    strip = strip_layout(layout)
    pts = {"a": layout.buttons["a"][:2], "b": layout.buttons["b"][:2],
           "logo": layout.logo[:2], "off": (5, 5),
           "body": (layout.body[0] + 6, layout.body[1] + 6)}
    for pin in ("0", "1", "2", "3V"):
        x, y, w, h = layout.pads[pin]
        pts["pad" + pin] = (x + w // 2, y + h // 2)
    tx, ty, tw, th = strip.tilt
    pts["tilt_mid"] = (tx + tw // 2, ty + th // 2)
    pts["tilt_corner"] = (tx + tw - 2, ty + 2)
    sx, sy, sw, sh = strip.shake
    pts["shake"] = (sx + sw // 2, sy + sh // 2)
    for name, (kx, ky, kw, kh) in strip.sliders.items():
        pts["slider_" + name] = (kx + kw // 3, ky + kh // 2)
        pts["slider_end_" + name] = (kx + kw + 4, ky + kh // 2)
    return pts


def _gestures():
    layout = layout_for(_Inst())
    pts = _points(layout)
    out = []
    for name, p in pts.items():
        out.append(("left", name, [p]))
        out.append(("right", name, [p]))
    out.append(("left", "tilt drag", [pts["tilt_mid"], pts["tilt_corner"], pts["off"]]))
    out.append(("left", "slider drag", [pts["slider_light"], pts["slider_end_light"], (pts["slider_light"][0] - 40, pts["slider_light"][1])]))
    out.append(("left", "slider temp drag", [pts["slider_temperature"], pts["slider_end_temperature"]]))
    return out


GESTURES = _gestures()


def _run_desktop(button, route):
    inst = _Inst()
    runner = _Runner(inst)
    num = desktop.LEFT if button == "left" else desktop.RIGHT
    desktop._mouse_presses.clear()
    swallowed = [desktop.mouse_down(runner, num, *route[0])]
    for p in route[1:]:
        desktop.follow(*p)
    mid = _fingerprint(simulator_of(inst))
    swallowed.append(desktop.mouse_up(runner, num, *route[-1]))
    return swallowed, mid, _fingerprint(simulator_of(inst))


def _run_kivy(button, route):
    inst = _Inst()
    board = kt.Board(inst, simulator_of(inst), layout_for(inst), True)
    presses = {}
    swallowed = [kt.press([board], presses, button, *route[0])]
    for p in route[1:]:
        kt.follow(presses, *p)
    mid = _fingerprint(board.sim)
    swallowed.append(kt.release(presses, button, *route[-1]))
    return swallowed, mid, _fingerprint(board.sim)


@pytest.mark.parametrize("button,name,route", GESTURES, ids=lambda v: v if isinstance(v, str) else "")
def test_a_gesture_leaves_the_board_as_the_desktop_input_does(button, name, route):
    assert _run_kivy(button, route) == _run_desktop(button, route)


def test_the_gestures_actually_change_something():
    """Guards the differential above against comparing two no-ops."""
    states = {name: _run_kivy(button, route)[1] for button, name, route in GESTURES if button == "left"}
    rest = _fingerprint(_Inst().__dict__["extension_state"]["microbit"]["simulator"])
    changed = [n for n, s in states.items() if s != rest]
    for expected in ("a", "b", "logo", "pad0", "pad1", "pad2", "shake", "tilt_corner",
                     "tilt drag", "slider drag", "slider temp drag"):
        assert expected in changed, expected
    assert not any(n in changed for n in ("off", "body", "pad3V"))


def test_the_strip_can_be_hidden_so_its_controls_do_not_react():
    inst = _Inst()
    board = kt.Board(inst, simulator_of(inst), layout_for(inst), show_strip=False)
    shake = _points(layout_for(inst))["shake"]
    assert kt.press([board], {}, "left", *shake) is False
    assert _fingerprint(board.sim) == _fingerprint(_Inst().__dict__["extension_state"]["microbit"]["simulator"])


def test_the_topmost_board_gets_the_press():
    low, high = _Inst(), _Inst()
    boards = [kt.Board(high, simulator_of(high), layout_for(high)),
              kt.Board(low, simulator_of(low), layout_for(low))]
    kt.press(boards, {}, "left", *layout_for(high).buttons["a"][:2])
    assert simulator_of(high).buttons["a"] and not simulator_of(low).buttons.get("a")


def test_other_mouse_buttons_are_ignored():
    inst = _Inst()
    board = kt.Board(inst, simulator_of(inst), layout_for(inst))
    for name in ("middle", "scrollup", "scrolldown"):
        assert kt.press([board], {}, name, *layout_for(inst).buttons["a"][:2]) is False


# -- keyboard ------------------------------------------------------------------

KEY_RUNS = [
    ["a"], ["b"], ["s"], ["left"], ["right"], ["up"], ["down"], ["x"],
    ["left", "up"], ["left", "right"], ["up", "down", "left"],
]


@pytest.mark.parametrize("enabled", [True, False, "true", "no"])
@pytest.mark.parametrize("keys", KEY_RUNS, ids=lambda k: "+".join(k))
def test_keys_match_the_desktop_input(keys, enabled):
    d = _Inst(microbit_keyboard=enabled)
    k_sim, held = simulator_of(_Inst()), set()
    drove_d, drove_k = [], []
    for key in keys:
        drove_d.append(desktop.key_down(d, key))
        drove_k.append(kt.keyboard_on(enabled) and kt.key_down(k_sim, held, key))
    assert drove_k == drove_d
    assert _fingerprint(k_sim) == _fingerprint(simulator_of(d))
    for key in reversed(keys):
        desktop.key_up(d, key)
        if kt.keyboard_on(enabled):
            kt.key_up(k_sim, held, key)
    assert _fingerprint(k_sim) == _fingerprint(simulator_of(d))


def test_the_kivy_keycodes_name_the_same_keys():
    assert kt.KEY_NAMES == {97: "a", 98: "b", 115: "s", 273: "up", 274: "down",
                            275: "right", 276: "left"}


# -- the generated scene (stub kivy) ----------------------------------------------

def _scene(game, **board_attrs):
    import importlib
    scene_mod = importlib.import_module("scenes.room0")
    scene = scene_mod.Room0.__new__(scene_mod.Room0)
    inst, rendered = _board(**board_attrs)
    scene.instances = [inst]
    scene.room_height = 480
    return scene, inst


def test_a_touch_in_room_coordinates_presses_the_drawn_button_and_is_swallowed():
    game = _export({})
    with _stub_kivy(game):
        scene, inst = _scene(game)
        layout = inst._mb_layout(480)
        ax, ay, _ = layout.buttons["a"]
        assert scene._extension_touch_down(None, ax, ay, "left") is True
        assert inst._mb_sim().buttons["a"]
        assert scene._extension_touch_up(None, ax, ay, "left") is True
        assert not inst._mb_sim().buttons["a"]
        assert scene._extension_touch_down(None, 5, 5, "left") is False


def test_dragging_the_tilt_pad_follows_the_touch_and_springs_back():
    game = _export({})
    with _stub_kivy(game):
        scene, inst = _scene(game)
        tilt = strip_layout(inst._mb_layout(480)).tilt
        mid = (tilt[0] + tilt[2] // 2, tilt[1] + tilt[3] // 2)
        assert scene._extension_touch_move(None, *mid) is False        # nothing held
        scene._extension_touch_down(None, *mid, "left")
        rest = tuple(inst._mb_sim().acceleration)
        assert scene._extension_touch_move(None, tilt[0] + tilt[2] - 2, tilt[1] + 2) is True
        assert tuple(inst._mb_sim().acceleration) != rest
        scene._extension_touch_up(None, *mid, "left")
        assert tuple(inst._mb_sim().acceleration) == (0, 0, -1024)


def test_the_keyboard_is_opt_in_per_instance_variable():
    game = _export({})
    with _stub_kivy(game):
        scene, off = _scene(game)
        scene._extension_key_down(97)
        assert not off._mb_sim().buttons["a"]
        scene, on = _scene(game, microbit_keyboard=True)
        scene._extension_key_down(97)
        assert on._mb_sim().buttons["a"]
        scene._extension_key_up(97)
        assert not on._mb_sim().buttons["a"]
        scene._extension_key_down(276)                                  # left arrow tilts
        assert on._mb_sim().acceleration[0] < 0
        scene._extension_key_up(276)
        assert tuple(on._mb_sim().acceleration) == (0, 0, -1024)
        scene._extension_key_down(65)                                   # an unmapped key
        scene._extension_key_down(115)                                  # s shakes
        assert on._mb_sim().current_gesture == "shake" or on._mb_sim().acceleration != (0, 0, -1024)


def test_an_invisible_board_cannot_be_touched():
    game = _export({})
    with _stub_kivy(game):
        scene, inst = _scene(game, visible=False)
        ax, ay, _ = inst._mb_layout(480).buttons["a"]
        assert scene._extension_touch_down(None, ax, ay, "left") is False


def test_the_scene_calls_the_hooks_before_the_authored_mouse_events_and_has_touch_move():
    game = _export({})
    text = (game / "scenes" / "room0.py").read_text(encoding="utf-8")
    down = text.index("self._extension_touch_down(touch, mx, my, button)")
    assert down < text.index("on_mouse_left_press'", down)
    up = text.index("self._extension_touch_up(touch, mx, my, button)")
    assert up < text.index("on_mouse_left_release'", up)
    assert "def on_touch_move(self, touch):" in text
    assert "self._extension_key_down(key)" in text and "self._extension_key_up(key)" in text


def test_the_shipped_touch_module_is_the_source_and_has_no_toolkit_import():
    game = _export({})
    shipped = (game / "microbit_sim" / "touch.py").read_bytes()
    assert shipped == (ROOT / "extensions/microbit/kivy_touch.py").read_bytes()
    assert b"import pygame" not in shipped and b"import kivy" not in shipped


def test_a_press_after_a_release_we_never_saw_lets_go_of_the_first_control():
    def run_desktop():
        inst = _Inst()
        desktop._mouse_presses.clear()
        pts = _points(layout_for(inst))
        runner = _Runner(inst)
        desktop.mouse_down(runner, desktop.LEFT, *pts["a"])
        desktop.mouse_down(runner, desktop.LEFT, *pts["logo"])
        return _fingerprint(simulator_of(inst))

    inst = _Inst()
    board = kt.Board(inst, simulator_of(inst), layout_for(inst))
    pts = _points(layout_for(inst))
    presses = {}
    kt.press([board], presses, "left", *pts["a"])
    kt.press([board], presses, "left", *pts["logo"])
    assert _fingerprint(board.sim) == run_desktop()
    assert not board.sim.buttons["a"] and board.sim.logo_touched


def test_the_scene_gives_a_press_to_the_topmost_of_two_overlapping_boards():
    game = _export({})
    with _stub_kivy(game):
        scene, low = _scene(game)
        _, high = _scene(game)
        scene.instances = [low, high]                    # later = on top
        ax, ay, _ = low._mb_layout(480).buttons["a"]
        scene._extension_touch_down(None, ax, ay, "left")
        assert high._mb_sim().buttons["a"] and not low._mb_sim().buttons["a"]
