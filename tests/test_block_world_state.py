"""Block World is a new extension (Phase 1 of docs/VOXEL_WORLD_PLAN.md).

These pin the Phase 1 deliverable: the extension loads cleanly with no
actions/renderer yet, and its per-room voxel world data model (state.py)
behaves correctly in isolation. There is no renderer to test yet -- that's
Phase 2.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


class _Room:
    """A bare stand-in -- state.py only needs an object it can (optionally)
    find/attach an `extension_state` dict on, same as raycast's tests use."""


def test_extension_is_discovered_and_enabled_by_default():
    from events.plugin_loader import list_available_extensions
    found = {e["folder"]: e for e in list_available_extensions()}
    assert "block_world" in found, "block_world extension not discovered"
    assert found["block_world"]["enabled"] is True


def test_loading_all_plugins_does_not_raise():
    """No PLUGIN_ACTIONS / PLUGIN_ROOM_RENDERERS declared yet -- the loader
    must skip both via its hasattr guards without error."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()  # would raise/log an error if the manifest or import broke


def test_fresh_real_room_has_no_block_world_state():
    from runtime.game_runner import GameRoom
    room = GameRoom("r", {"width": 64, "height": 64}, action_executor=None)
    assert room.extension_state == {}, "fresh room must not pre-stamp block_world state"

    from extensions.block_world.state import peek_blocks
    assert peek_blocks(room) is None


def test_peek_blocks_does_not_create_state():
    from extensions.block_world.state import peek_blocks
    room = _Room()
    assert peek_blocks(room) is None
    assert peek_blocks(room) is None
    assert not hasattr(room, "extension_state"), "a non-creating peek must not stamp state"


def test_get_block_on_untouched_room_is_air_without_creating_state():
    from extensions.block_world.state import get_block
    room = _Room()
    assert get_block(room, 0, 0, 0) is None
    assert not hasattr(room, "extension_state")


def test_set_get_remove_roundtrip():
    from extensions.block_world.state import set_block, get_block, remove_block
    room = _Room()
    assert get_block(room, 1, 2, 3) is None

    set_block(room, 1, 2, 3, "stone")
    assert get_block(room, 1, 2, 3) == "stone"
    assert get_block(room, 1, 2, 4) is None  # neighboring cell untouched

    set_block(room, 1, 2, 3, "dirt")  # overwrite
    assert get_block(room, 1, 2, 3) == "dirt"

    remove_block(room, 1, 2, 3)
    assert get_block(room, 1, 2, 3) is None

    remove_block(room, 9, 9, 9)  # no-op on an already-air cell, must not raise


def test_negative_and_zero_coordinates():
    from extensions.block_world.state import set_block, get_block
    room = _Room()
    set_block(room, -5, 0, -12, "sand")
    assert get_block(room, -5, 0, -12) == "sand"
    assert get_block(room, 5, 0, 12) is None  # sign matters, not just magnitude


def test_set_block_rejects_unknown_type():
    from extensions.block_world.state import set_block
    room = _Room()
    try:
        set_block(room, 0, 0, 0, "adamantium")
        assert False, "expected KeyError for an unregistered block type"
    except KeyError:
        pass


def test_iter_blocks_and_bounds():
    from extensions.block_world.state import set_block, iter_blocks, bounds
    room = _Room()
    assert bounds(room) is None
    assert list(iter_blocks(room)) == []

    placed = {(0, 0, 0, "grass"), (2, 0, 0, "stone"), (0, 5, -1, "sand")}
    for x, y, z, t in placed:
        set_block(room, x, y, z, t)

    assert set(iter_blocks(room)) == placed
    assert bounds(room) == (0, 0, -1, 2, 5, 0)


def test_to_block_list_and_load_block_list_roundtrip():
    from extensions.block_world.state import (
        set_block, to_block_list, load_block_list, get_block, iter_blocks,
    )
    src = _Room()
    set_block(src, 0, 0, 0, "grass")
    set_block(src, 1, 0, 0, "water")
    set_block(src, 0, 1, 0, "wool_red")

    exported = to_block_list(src)
    assert {"x": 0, "y": 0, "z": 0, "type": "grass"} in exported
    assert len(exported) == 3

    dst = _Room()
    load_block_list(dst, exported)
    assert set(iter_blocks(dst)) == set(iter_blocks(src))
    assert get_block(dst, 1, 0, 0) == "water"


def test_load_block_list_overwrites_existing_world():
    from extensions.block_world.state import set_block, load_block_list, get_block
    room = _Room()
    set_block(room, 0, 0, 0, "stone")
    load_block_list(room, [{"x": 9, "y": 9, "z": 9, "type": "sand"}])
    assert get_block(room, 0, 0, 0) is None, "load_block_list must replace, not merge"
    assert get_block(room, 9, 9, 9) == "sand"


def test_load_block_list_rejects_unknown_type():
    from extensions.block_world.state import load_block_list
    room = _Room()
    try:
        load_block_list(room, [{"x": 0, "y": 0, "z": 0, "type": "unobtainium"}])
        assert False, "expected KeyError for an unregistered block type"
    except KeyError:
        pass


def test_every_registered_block_type_resolves_to_a_real_texture_file():
    """Ties Phase 0's ASSETS.md import to Phase 1's registry: if a texture
    file is ever renamed/removed, this fails immediately instead of silently
    breaking a future renderer."""
    from extensions.block_world.state import BLOCK_TYPES, block_face_textures
    assert len(BLOCK_TYPES) >= 27
    for block_type in BLOCK_TYPES:
        faces = block_face_textures(block_type)
        assert set(faces) == {"top", "bottom", "side"}
        for path in faces.values():
            assert os.path.isfile(path), f"{block_type}: missing texture file {path}"


def test_block_face_textures_unknown_type_raises():
    from extensions.block_world.state import block_face_textures
    try:
        block_face_textures("nonexistent"), "expected KeyError"
    except KeyError:
        pass


def test_solid_and_transparent_flags_are_sane():
    """Spot-check a few physically-meaningful flags rather than asserting on
    the whole registry -- these are the ones later phases (collision,
    occlusion) will actually branch on."""
    from extensions.block_world.state import BLOCK_TYPES
    assert BLOCK_TYPES["water"]["solid"] is False
    assert BLOCK_TYPES["glass"]["transparent"] is True
    assert BLOCK_TYPES["stone"]["solid"] is True
    assert "transparent" not in BLOCK_TYPES["stone"]
