"""Regression tests for AssetManager.rename_asset (audit M3, M4, M5).

- M3: renaming a room did del-old + append-new on the cache OrderedDict,
  moving the room to the END of the order. Dict order IS the room order
  (no code writes 'room_order'; the runtime falls back to key order for
  the start room), so renaming the first room silently changed which room
  the game starts in.
- M4: the backgrounds rename branch rewrote only the legacy single
  room_data['background_image'], not the per-layer room_data['backgrounds']
  list that the properties panel writes and the runtime renders.
- M5: reference updates walked only event_data['actions'] and one level of
  sub-events; nested parameters['then_actions']/['else_actions'] (a fully
  supported structure) kept stale names.
"""

from unittest.mock import patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _manager(tmp_path):
    with patch('pygame.mixer.init'):
        from core.asset_manager import AssetManager
    am = AssetManager()
    am.set_project_directory(tmp_path)
    return am


class TestRoomRenamePreservesOrder:
    def test_rename_keeps_room_position(self, tmp_path):
        am = _manager(tmp_path)
        am.assets_cache["rooms"] = {
            "room0": {"name": "room0", "asset_type": "room", "instances": []},
            "room1": {"name": "room1", "asset_type": "room", "instances": []},
            "room2": {"name": "room2", "asset_type": "room", "instances": []},
        }
        assert am.rename_asset("rooms", "room0", "menu") is True

        # 'menu' must stay first (it was room0), not get pushed to the end.
        assert list(am.assets_cache["rooms"].keys()) == ["menu", "room1", "room2"]

    def test_rename_middle_room_keeps_position(self, tmp_path):
        am = _manager(tmp_path)
        am.assets_cache["rooms"] = {
            "a": {"name": "a", "asset_type": "room", "instances": []},
            "b": {"name": "b", "asset_type": "room", "instances": []},
            "c": {"name": "c", "asset_type": "room", "instances": []},
        }
        assert am.rename_asset("rooms", "b", "middle") is True
        assert list(am.assets_cache["rooms"].keys()) == ["a", "middle", "c"]

    def test_rename_preserves_cache_alias(self, tmp_path):
        """The bucket object identity is preserved (clear+reinsert in place),
        so a current_project_data alias to it stays valid."""
        am = _manager(tmp_path)
        bucket = {
            "room0": {"name": "room0", "asset_type": "room", "instances": []},
            "room1": {"name": "room1", "asset_type": "room", "instances": []},
        }
        am.assets_cache["rooms"] = bucket
        am.rename_asset("rooms", "room1", "level1")
        assert am.assets_cache["rooms"] is bucket  # same object
        assert list(bucket.keys()) == ["room0", "level1"]


class TestBackgroundLayerRename:
    def test_rename_updates_layer_list(self, tmp_path):
        am = _manager(tmp_path)
        am.assets_cache["backgrounds"] = {
            "sky": {"name": "sky", "asset_type": "background"},
        }
        am.assets_cache["rooms"] = {
            "room0": {
                "name": "room0", "asset_type": "room", "instances": [],
                "background_image": "sky",  # legacy single
                "backgrounds": [  # 8-layer list
                    {"background_image": "sky", "visible": True},
                    {"background_image": "", "visible": False},
                ],
            }
        }
        assert am.rename_asset("backgrounds", "sky", "ciel") is True

        room = am.assets_cache["rooms"]["room0"]
        assert room["background_image"] == "ciel"  # legacy still works
        assert room["backgrounds"][0]["background_image"] == "ciel"  # M4
        assert room["backgrounds"][1]["background_image"] == ""  # untouched


class TestNestedActionReferenceRename:
    def _object_with_nested(self, room_param_value):
        return {
            "name": "obj_ctrl", "asset_type": "object",
            "events": {
                "step": {
                    "actions": [
                        {"action": "if_condition", "parameters": {
                            "condition": "self.lives <= 0",
                            "then_actions": [
                                {"action": "goto_room",
                                 "parameters": {"room": room_param_value}},
                            ],
                            "else_actions": [
                                {"action": "create_instance",
                                 "parameters": {"object": "obj_ghost"}},
                            ],
                        }},
                    ]
                }
            },
        }

    def test_room_rename_updates_nested_then_action(self, tmp_path):
        am = _manager(tmp_path)
        am.assets_cache["rooms"] = {
            "game_over": {"name": "game_over", "asset_type": "room", "instances": []},
        }
        am.assets_cache["objects"] = {"obj_ctrl": self._object_with_nested("game_over")}

        assert am.rename_asset("rooms", "game_over", "ecran_fin") is True

        then_action = (am.assets_cache["objects"]["obj_ctrl"]["events"]["step"]
                       ["actions"][0]["parameters"]["then_actions"][0])
        assert then_action["parameters"]["room"] == "ecran_fin"  # M5

    def test_object_rename_updates_nested_else_action(self, tmp_path):
        am = _manager(tmp_path)
        am.assets_cache["objects"] = {
            "obj_ghost": {"name": "obj_ghost", "asset_type": "object", "events": {}},
            "obj_ctrl": self._object_with_nested("game_over"),
        }
        assert am.rename_asset("objects", "obj_ghost", "obj_spook") is True

        else_action = (am.assets_cache["objects"]["obj_ctrl"]["events"]["step"]
                       ["actions"][0]["parameters"]["else_actions"][0])
        assert else_action["parameters"]["object"] == "obj_spook"  # M5
