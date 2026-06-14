"""Regression test for the sprite-file merge whitelist (audit L6).

The sprite merge whitelist omitted 'precise', 'frame_width', 'frame_height',
'animation_type' and 'speed', so a hand/external edit to sprites/<name>.json for
those keys was ignored on load and reverted on the next save. Also
'remember_destroyed' was missing from the object whitelist.
"""

from utils.project_file_merge import (
    merge_sprite_file, _SPRITE_FILE_KEYS, _OBJECT_FILE_KEYS,
)


def test_previously_dropped_sprite_keys_now_merge():
    sprite_data = {"name": "spr", "speed": 10.0, "precise": False}
    file_data = {
        "speed": 4.0,
        "precise": True,
        "frame_width": 16,
        "frame_height": 16,
        "animation_type": "strip",
    }
    merge_sprite_file(sprite_data, file_data)
    assert sprite_data["speed"] == 4.0
    assert sprite_data["precise"] is True
    assert sprite_data["frame_width"] == 16
    assert sprite_data["frame_height"] == 16
    assert sprite_data["animation_type"] == "strip"


def test_whitelist_covers_the_documented_keys():
    for key in ("precise", "frame_width", "frame_height", "animation_type", "speed"):
        assert key in _SPRITE_FILE_KEYS


def test_remember_destroyed_in_object_keys():
    assert "remember_destroyed" in _OBJECT_FILE_KEYS


def test_file_takes_precedence_and_unknown_keys_ignored():
    sprite_data = {"width": 32}
    merge_sprite_file(sprite_data, {"width": 64, "not_a_key": "x"})
    assert sprite_data["width"] == 64
    assert "not_a_key" not in sprite_data
