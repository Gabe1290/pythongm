"""utils/asset_usage.py — DEFERRED_ITEMS_PLAN.md item 10 (Asset Manager)
Tier 1. See docs/ASSET_MANAGER_PLAN.md.

Hand-built project dicts for each reference kind the module claims to
find, plus a real-sample smoke test (samples/plateforme_3) as a sanity
check against realistic data — including the play_sound landmine (a
plugin action, invisible until load_all_plugins() runs; the module must
handle this internally, not push it onto every caller).
"""
import json
from pathlib import Path

import pytest

from utils.asset_usage import find_asset_usages, find_unused_assets

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_object_sprite_field():
    data = {"assets": {"objects": {
        "obj_a": {"sprite": "spr_hero", "events": {}},
        "obj_b": {"sprite": "spr_other", "events": {}},
    }, "rooms": {}}}
    usages = find_asset_usages(data, "sprites", "spr_hero")
    assert len(usages) == 1
    assert usages[0].kind == "object_sprite"
    assert usages[0].object_name == "obj_a"


def test_object_parent_field():
    data = {"assets": {"objects": {
        "obj_child": {"parent": "obj_base", "events": {}},
        "obj_base": {"events": {}},
    }, "rooms": {}}}
    usages = find_asset_usages(data, "objects", "obj_base")
    kinds = {u.kind for u in usages}
    assert "object_parent" in kinds


def test_typed_action_param_sprite():
    data = {"assets": {"objects": {
        "obj_a": {"events": {"create": {"actions": [
            {"action": "set_sprite", "parameters": {"sprite": "spr_hero", "subimage": "0", "speed": "0"}},
        ]}}},
    }, "rooms": {}}}
    usages = find_asset_usages(data, "sprites", "spr_hero")
    assert any(u.kind == "action_param" and "set_sprite" in u.location for u in usages)


def test_typed_action_param_nested_then_else():
    data = {"assets": {"objects": {
        "obj_a": {"events": {"step": {"actions": [
            {"action": "test_expression", "parameters": {
                "expression": "x > 0",
                "then_actions": [
                    {"action": "set_sprite", "parameters": {"sprite": "spr_deep", "subimage": "0", "speed": "0"}},
                ],
                "else_actions": [],
            }},
        ]}}},
    }, "rooms": {}}}
    usages = find_asset_usages(data, "sprites", "spr_deep")
    assert len(usages) == 1
    assert "step" in usages[0].location


def test_container_event_keyboard():
    data = {"assets": {"objects": {
        "obj_a": {"events": {"keyboard": {"right": {"actions": [
            {"action": "set_sprite", "parameters": {"sprite": "spr_right", "subimage": "0", "speed": "0"}},
        ]}}}},
    }, "rooms": {}}}
    usages = find_asset_usages(data, "sprites", "spr_right")
    assert len(usages) == 1
    assert "keyboard:right" in usages[0].location


def test_collision_target_object():
    data = {"assets": {"objects": {
        "obj_a": {"events": {"collision_with_obj_b": {
            "actions": [],
            "target_object": "obj_b",
        }}},
        "obj_b": {"events": {}},
    }, "rooms": {}}}
    usages = find_asset_usages(data, "objects", "obj_b")
    assert any(u.kind == "collision_target" for u in usages)


def test_room_instance_object_name():
    data = {"assets": {"objects": {"obj_enemy": {"events": {}}},
                        "rooms": {"rm_1": {"instances": [
                            {"object_name": "obj_enemy", "x": 0, "y": 0},
                        ]}}}}
    usages = find_asset_usages(data, "objects", "obj_enemy")
    assert any(u.kind == "room_instance" and u.room_name == "rm_1" for u in usages)


def test_room_background_image():
    data = {"assets": {"objects": {},
                        "rooms": {"rm_1": {"background_image": "bg_sky"}}}}
    usages = find_asset_usages(data, "backgrounds", "bg_sky")
    assert any(u.kind == "room_background" for u in usages)


def test_room_tile_background_name():
    data = {"assets": {"objects": {},
                        "rooms": {"rm_1": {"tiles": [
                            {"background_name": "bg_tiles", "x": 0, "y": 0},
                        ]}}}}
    usages = find_asset_usages(data, "backgrounds", "bg_tiles")
    assert any(u.kind == "room_tile" for u in usages)


def test_draw_background_untyped_param():
    data = {"assets": {"objects": {
        "obj_a": {"events": {"draw": {"actions": [
            {"action": "draw_background", "parameters": {"background": "bg_x", "x": 0, "y": 0, "tiled": False}},
        ]}}},
    }, "rooms": {}}}
    usages = find_asset_usages(data, "backgrounds", "bg_x")
    assert any(u.kind == "action_param" and "draw_background" in u.location for u in usages)


def test_play_sound_plugin_action_is_found():
    # play_sound lives in plugins/audio_actions.py, not the static
    # ACTION_TYPES dict — get_action_type() returns None for it until
    # load_all_plugins() runs. This must work without the caller having
    # to know that.
    data = {"assets": {"objects": {
        "obj_a": {"events": {"create": {"actions": [
            {"action": "play_sound", "parameters": {"sound": "snd_boom", "volume": "1.0"}},
        ]}}},
    }, "rooms": {}}}
    usages = find_asset_usages(data, "sounds", "snd_boom")
    assert len(usages) == 1
    assert usages[0].kind == "action_param"


def test_no_usages_returns_empty_list():
    data = {"assets": {"objects": {"obj_a": {"events": {}}}, "rooms": {}}}
    assert find_asset_usages(data, "sprites", "spr_nowhere") == []


def test_tolerant_of_malformed_data():
    # Must not crash on None/wrong-type values in odd places.
    data = {"assets": {"objects": {
        "obj_a": {"events": {"step": {"actions": [
            {"action": "set_sprite", "parameters": None},
            {"action": None, "parameters": {}},
            "not_a_dict",
        ]}}},
        "obj_b": "not_a_dict",
    }, "rooms": {"rm_1": "not_a_dict"}}}
    assert find_asset_usages(data, "sprites", "spr_anything") == []


def test_find_unused_assets_basic():
    # obj_a is referenced by nothing (no room instance/parent/collision
    # target/action param names it), so it's correctly "unused" itself —
    # using spr_used doesn't make obj_a used, only spr_used used.
    # obj_b's room instance is what keeps obj_b out of the unused list.
    data = {"assets": {
        "sprites": {"spr_used": {}, "spr_unused": {}},
        "sounds": {}, "backgrounds": {},
        "rooms": {"rm_1": {"instances": [{"object_name": "obj_b", "x": 0, "y": 0}]}},
        "objects": {
            "obj_a": {"sprite": "spr_used", "events": {}},
            "obj_b": {"events": {}},
        },
    }}
    unused = find_unused_assets(data)
    assert unused.get("sprites") == ["spr_unused"]
    assert unused.get("objects") == ["obj_a"]


# ---------------------------------------------------------------------------
# Real-sample smoke test
# ---------------------------------------------------------------------------

SAMPLE = REPO_ROOT / "samples" / "plateforme_3"


@pytest.fixture(scope="module")
def sample_project_data():
    from utils.project_file_merge import merge_object_file
    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = SAMPLE / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        side = SAMPLE / "rooms" / f"{name}.json"
        if side.exists():
            data["assets"]["rooms"][name] = json.loads(side.read_text(encoding="utf-8"))
    return data


def test_sample_sprite_usage(sample_project_data):
    usages = find_asset_usages(sample_project_data, "sprites", "spr_pingus_dr")
    assert any(u.kind == "object_sprite" for u in usages)
    assert any(u.kind == "action_param" for u in usages)


def test_sample_object_collision_and_room_instance(sample_project_data):
    usages = find_asset_usages(sample_project_data, "objects", "obj_power")
    kinds = {u.kind for u in usages}
    assert "collision_target" in kinds
    assert "room_instance" in kinds


def test_sample_plugin_sound_action_found(sample_project_data):
    # play_sound is a plugin action (audio_actions.py) — real regression
    # coverage for the load_all_plugins() landmine against real data, not
    # just the hand-built case above.
    usages = find_asset_usages(sample_project_data, "sounds", "son_bonus")
    assert len(usages) >= 1
    assert all(u.kind == "action_param" for u in usages)


def test_sample_unused_assets_no_false_positive_on_used_sound(sample_project_data):
    unused = find_unused_assets(sample_project_data)
    assert "son_bonus" not in unused.get("sounds", [])
