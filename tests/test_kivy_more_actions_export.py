"""Regression tests: previously-unsupported actions in the Kivy export.

These action types hit the generator's "Unknown action type" default and were
silently dropped (a `pass # TODO` with a console warning), so exported games
lost sprite changes, directional movement, restart, etc. The warning spam was
user-reported (2026-06-26):

    pygm.export.Kivy.code_generator - WARNING: Unknown action type 'set_sprite'
    ... 'play_sound' / 'start_moving_direction' / 'restart_game' / 'move_to_contact' / 'show_highscore'

Now handled:
- set_sprite            -> self.set_sprite('assets/images/<file>') (+ image_index/speed)
- start_moving_direction-> reuses move_fixed (named direction + speed)
- restart_game          -> reuses the app's _switch_to_room(0)
- play_sound / move_to_contact / show_highscore -> honest no-op comments
  (audio + sweep-to-contact aren't wired into the export yet) instead of a
  silent drop.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def _gen(action_type, params, sprite_paths=None, event_type="step"):
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=2, sprite_paths=sprite_paths or {})
    g.process_action({"action_type": action_type, "parameters": params}, event_type)
    return g.get_code()


def _valid(src):
    wrapper = "class _C:\n    def m(self, other=None):\n" + src + "\n"
    try:
        compile(wrapper, "<gen>", "exec")
        return True
    except SyntaxError:
        return False


def test_set_sprite_resolves_name_to_export_path():
    out = _gen("set_sprite", {"sprite": "spr_run"},
               sprite_paths={"spr_run": "assets/images/spr_run.png"})
    assert "self.set_sprite('assets/images/spr_run.png')" in out
    assert _valid(out)


def test_set_sprite_sets_subimage_and_speed():
    out = _gen("set_sprite", {"sprite": "spr_run", "subimage": 2, "speed": 0.5},
               sprite_paths={"spr_run": "assets/images/spr_run.png"})
    assert "self.image_index = 2" in out
    assert "self.image_speed = 0.5" in out
    assert _valid(out)


def test_set_sprite_self_keeps_sprite():
    # '<self>' must NOT emit a set_sprite call (keep current art), only frame.
    out = _gen("set_sprite", {"sprite": "<self>", "subimage": 3})
    assert "set_sprite(" not in out
    assert "self.image_index = 3" in out
    assert _valid(out)


def test_set_sprite_unknown_name_is_honest_noop():
    out = _gen("set_sprite", {"sprite": "spr_missing"})  # no map entry
    assert "set_sprite(" not in out
    assert "not found" in out
    assert _valid(out)


def test_start_moving_direction_sets_direction_and_speed():
    out = _gen("start_moving_direction", {"directions": ["up"], "speed": 6})
    assert "self.direction = 90" in out  # GameMaker: up = 90°
    assert "self.speed = 6" in out
    assert _valid(out)


def test_start_moving_direction_stop():
    out = _gen("start_moving_direction", {"directions": ["stop"]})
    assert "self.speed = 0" in out
    assert _valid(out)


def test_restart_game_switches_to_first_room():
    out = _gen("restart_game", {})
    assert "_switch_to_room(0)" in out
    assert "get_game_app" in out
    assert _valid(out)


def test_play_sound_resolves_and_calls_helper():
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=2, sound_paths={"snd_jump": "assets/sounds/jump.wav"})
    g.process_action({"action_type": "play_sound",
                      "parameters": {"sound": "snd_jump", "volume": 0.8}}, "step")
    out = g.get_code()
    assert "from main import play_sound" in out
    assert "play_sound('assets/sounds/jump.wav', 0.8)" in out
    assert _valid(out)


def test_play_sound_unknown_is_honest_noop():
    out = _gen("play_sound", {"sound": "snd_missing"})  # no map entry
    assert "play_sound(" not in out or "from main import" not in out
    assert "not found" in out
    assert _valid(out)


def test_move_to_contact_emits_step_loop():
    out = _gen("move_to_contact",
               {"direction": 270, "max_distance": 64, "object": "solid"})
    assert "math.radians(270)" in out
    assert "for _ in range(int(64)):" in out
    assert "check_collision_at(self.x + _sx, self.y + _sy, 'solid')" in out
    assert "break" in out
    assert _valid(out)


def test_move_to_contact_all_maps_to_any():
    out = _gen("move_to_contact", {"object": "all"})
    assert "'any'" in out
    assert _valid(out)


def test_move_to_contact_direction_expression_resolves():
    # The 'direction' param is often the bare word "direction" (the instance's
    # current heading); it must bind to self.direction, not stay a NameError.
    out = _gen("move_to_contact",
               {"direction": "direction", "max_distance": 32, "object": "obj_brique"})
    assert "math.radians(self.direction)" in out
    assert "math.radians(direction)" not in out  # the reported crash
    assert _valid(out)


def test_move_to_contact_numeric_direction_unchanged():
    out = _gen("move_to_contact", {"direction": 270})
    assert "math.radians(270)" in out
    assert _valid(out)


def test_move_to_contact_max_distance_expression_resolves():
    out = _gen("move_to_contact", {"direction": 0, "max_distance": "speed * 2"})
    assert "range(int(self.speed * 2))" in out
    assert _valid(out)


def test_show_highscore_calls_module():
    out = _gen("show_highscore", {})
    assert "from highscore import show_highscore" in out
    assert "show_highscore(allow_new_entry=True)" in out
    assert _valid(out)


def test_show_highscore_respects_allow_new_entry_flag():
    out = _gen("show_highscore", {"allow_new_entry": False})
    assert "show_highscore(allow_new_entry=False)" in out
    assert _valid(out)


def test_clear_highscore_calls_module():
    out = _gen("clear_highscore", {})
    assert "from highscore import clear_highscore" in out
    assert "clear_highscore()" in out
    assert _valid(out)
    assert _valid(out)


def test_set_sprite_guarded_by_conditional_nests_correctly():
    """set_sprite as the guarded unit of a test_expression lands inside the if."""
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=2, sprite_paths={"s": "assets/images/s.png"})
    g.process_action({"action_type": "test_expression",
                      "parameters": {"expression": "hspeed > 0"}}, "step")
    g.process_action({"action_type": "set_sprite",
                      "parameters": {"sprite": "s"}}, "step")
    out = g.get_code()
    lines = [ln for ln in out.split("\n") if ln.strip()]
    if_line = next(ln for ln in lines if ln.lstrip().startswith("if "))
    body = next(ln for ln in lines if "set_sprite(" in ln)
    assert (len(body) - len(body.lstrip())) > (len(if_line) - len(if_line.lstrip()))
    assert _valid(out)
