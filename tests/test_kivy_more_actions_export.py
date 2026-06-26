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


@pytest.mark.parametrize("action_type", ["play_sound", "move_to_contact", "show_highscore"])
def test_unsupported_actions_emit_honest_noop_not_silent_drop(action_type):
    out = _gen(action_type, {"sound": "snd_x"})
    assert "TODO" not in out, "should be an explicit branch, not the unknown default"
    assert "not yet supported" in out or "not supported" in out
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
