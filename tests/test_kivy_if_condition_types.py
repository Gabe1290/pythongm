"""Kivy export: if_condition understands key_pressed, random_chance and variable_compare.

The generator only knew instance_count and expression; every other condition_type became
``if True:``. A key-steered avatar (the reseau samples: four key_pressed conditions in one step)
therefore moved in every direction at once on Android/iOS. The generated code is executed here.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402


def _gen(params, event_type="step"):
    g = ActionCodeGenerator(base_indent=2)
    g.process_action({"action_type": "if_condition", "parameters": params}, event_type)
    return g.get_code()


def _run(code, **attrs):
    src = "class _C:\n    def m(self):\n        self.out = []\n" + code + "\n"
    ns = {}
    exec(compile(src, "<gen>", "exec"), ns)
    inst = ns["_C"]()
    for k, v in attrs.items():
        setattr(inst, k, v)
    inst.m()
    return inst


class _Scene:
    def __init__(self, keys):
        self.keys_pressed = keys


def _branches(cond_params, **attrs):
    then = [{"action": "set_variable", "parameters": {"variable": "hit", "value": "1", "scope": "self"}}]
    other = [{"action": "set_variable", "parameters": {"variable": "hit", "value": "2", "scope": "self"}}]
    code = _gen({**cond_params, "then_actions": then, "else_actions": other})
    return _run(code, **attrs)


def test_key_pressed_follows_the_held_keys_by_kivy_keycode():
    held = _branches({"condition_type": "key_pressed", "key": "right"}, scene=_Scene({275: True}))
    idle = _branches({"condition_type": "key_pressed", "key": "right"}, scene=_Scene({}))
    other = _branches({"condition_type": "key_pressed", "key": "right"}, scene=_Scene({276: True}))
    assert (held.hit, idle.hit, other.hit) == (1, 2, 2)


def test_key_pressed_names_letters_space_and_the_legacy_arrow_spelling():
    assert _branches({"condition_type": "key_pressed", "key": "a"}, scene=_Scene({97: True})).hit == 1
    assert _branches({"condition_type": "key_pressed", "key": "Space"}, scene=_Scene({32: True})).hit == 1
    assert _branches({"condition_type": "key_pressed", "key": "Left Arrow"}, scene=_Scene({276: True})).hit == 1
    assert _branches({"condition_type": "key_pressed", "key": "5"}, scene=_Scene({53: True})).hit == 1


def test_key_pressed_with_no_or_an_unknown_key_is_false_as_on_desktop():
    assert _branches({"condition_type": "key_pressed", "key": ""}, scene=_Scene({})).hit == 2
    assert _branches({"condition_type": "key_pressed", "key": "f13"}, scene=_Scene({})).hit == 2


def test_the_flat_form_guards_the_next_action_too():
    code = _gen({"condition_type": "key_pressed", "key": "up"})
    assert "self.scene.keys_pressed.get(273, False)" in code


def test_variable_compare_reads_the_instance_variable_with_a_safe_operator():
    yes = _branches({"condition_type": "variable_compare", "variable": "hp", "operator": ">", "value": "3"}, hp=5)
    no = _branches({"condition_type": "variable_compare", "variable": "hp", "operator": ">", "value": "3"}, hp=2)
    assert (yes.hit, no.hit) == (1, 2)
    code = _gen({"condition_type": "variable_compare", "variable": "hp",
                 "operator": "; import os", "value": "3"})
    assert "import os" not in code and "== 3" in code           # an unknown operator becomes ==
    assert _branches({"condition_type": "variable_compare", "variable": ""}).hit == 2


def test_random_chance_is_a_percentage():
    always = _branches({"condition_type": "random_chance", "chance": 100})
    never = _branches({"condition_type": "random_chance", "chance": 0})
    assert (always.hit, never.hit) == (1, 2)
    assert "<= 50" in _gen({"condition_type": "random_chance", "chance": "junk"})


def test_the_existing_condition_types_are_unchanged():
    assert "count_instances('obj_gem') == 0" in _gen({"condition_type": "instance_count",
                                                      "object_name": "obj_gem", "operator": "==", "value": 0})
    assert "if True" in _gen({"expression": ""}) or "if " in _gen({"expression": "score > 3"})


# ---------------------------------------------------------------- position_check / collision_check

class _Room:
    room_height = 480


def test_position_check_x_compares_the_instance_x():
    pc = {"condition_type": "position_check", "check_type": "x position", "operator": ">=", "value": 100}
    assert _branches(pc, x=100, scene=_Room()).hit == 1
    assert _branches(pc, x=99, scene=_Room()).hit == 2


def test_position_check_y_is_the_authors_y_down_from_the_sprite_top():
    """Kivy's y is up from the sprite's BOTTOM; the author's is down from its TOP: a 32 px
    sprite whose Kivy y is 400 in a 480 px room is at the author's y = 480 - 400 - 32 = 48."""
    pc = {"condition_type": "position_check", "check_type": "y position", "operator": "==", "value": 48}
    assert _branches(pc, y=400, image_height=32, grid_size=32, scene=_Room()).hit == 1
    assert _branches(pc, y=401, image_height=32, grid_size=32, scene=_Room()).hit == 2
    # a spriteless instance falls back to the grid size, as the rest of the generator does
    pc2 = {**pc, "value": 480 - 400 - 32}
    assert _branches(pc2, y=400, image_height=0, grid_size=32, scene=_Room()).hit == 1


def test_position_check_operator_names_junk_values_and_the_default_axis():
    base = {"condition_type": "position_check", "check_type": "x position"}
    assert _branches({**base, "operator": "greater", "value": 5}, x=9, scene=_Room()).hit == 1
    assert _branches({**base, "operator": "not_equal", "value": 9}, x=9, scene=_Room()).hit == 2
    assert _branches({**base, "operator": "==", "value": "junk"}, x=0, scene=_Room()).hit == 1   # int() or 0
    assert _branches({**base, "operator": "; import os", "value": 3}, x=3, scene=_Room()).hit == 1
    assert "import os" not in _gen({**base, "operator": "; import os", "value": 3})
    # anything without an "x" in check_type is the y axis, as on desktop
    assert "room_height - self.y" in _gen({"condition_type": "position_check", "check_type": "Vertical"})


class _Probe:
    """Stand-in for a GameObject: records the collision question it is asked."""

    def __init__(self, answer):
        self.answer, self.asked = answer, []

    def check_collision_at(self, x, y, obj):
        self.asked.append((x, y, obj))
        return self.answer


def _collision(params, answer, **attrs):
    then = [{"action": "set_variable", "parameters": {"variable": "hit", "value": "1", "scope": "self"}}]
    other = [{"action": "set_variable", "parameters": {"variable": "hit", "value": "2", "scope": "self"}}]
    code = _gen({"condition_type": "collision_check", **params, "then_actions": then, "else_actions": other})
    src = ("class _C:\n    def m(self):\n        self.out = []\n" + code + "\n")
    ns = {}
    exec(compile(src, "<gen>", "exec"), ns)
    probe = _Probe(answer)
    inst = type("_I", (ns["_C"], _Probe), {})(answer)
    for k, v in attrs.items():
        setattr(inst, k, v)
    inst.m()
    return inst


def test_collision_check_asks_at_the_offset_with_the_y_flip():
    inst = _collision({"object": "obj_wall", "offset_x": 4, "offset_y": 8}, True, x=100, y=200)
    assert inst.hit == 1
    # +8 is DOWN for the author, so one step towards the floor is y - 8 in Kivy
    assert inst.asked == [(104, 192, "obj_wall")]
    assert _collision({"object": "obj_wall"}, False, x=1, y=2).hit == 2


def test_collision_check_translates_desktops_any_and_all():
    assert _collision({"object": "any"}, True, x=0, y=0).asked[0][2] == "solid"
    assert _collision({"object": "all"}, True, x=0, y=0).asked[0][2] == "any"


def test_collision_check_without_an_object_is_false_and_offsets_may_be_expressions():
    assert "False" in _gen({"condition_type": "collision_check", "object": ""})
    inst = _collision({"object": "obj_wall", "offset_x": "hspeed + 2", "offset_y": 0}, True, x=10, y=5, hspeed=3)
    assert inst.asked[0][0] == 15
