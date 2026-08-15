"""Tier 7e Phase 2 (docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md): seed-based
procedural terrain generation, desktop only. Covers the noise function's
determinism, generate_chunk's fill + don't-overwrite-touched-content
guard, ensure_chunks_loaded/unload_distant_chunks' radius math, and the
save/load round-trip (to_touched_block_list/load_world_state) that keeps
a generated world small on disk.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime.game_runner import GameRoom  # noqa: E402
from extensions.block_world.state import (  # noqa: E402
    CHUNK_SIZE, block_world_state, get_block, set_block, remove_block,
    iter_blocks, terrain_height, generate_chunk, ensure_chunks_loaded,
    unload_distant_chunks, to_touched_block_list, load_world_state,
    to_block_list, _chunk_key,
)


def _room():
    return GameRoom("bw_gen_test", {"width": 640, "height": 640}, action_executor=None)


def _seeded_room(seed=42):
    room = _room()
    block_world_state(room)["seed"] = seed
    return room


class TestTerrainHeight:
    def test_deterministic_for_the_same_seed_and_cell(self):
        assert terrain_height(1, 5, 5) == terrain_height(1, 5, 5)

    def test_different_seeds_usually_differ(self):
        # Not a hard guarantee for every single cell, but across a spread
        # of cells two different seeds should disagree somewhere -- if
        # they never do, the seed isn't actually affecting anything.
        heights_a = [terrain_height(1, x, 0) for x in range(40)]
        heights_b = [terrain_height(2, x, 0) for x in range(40)]
        assert heights_a != heights_b

    def test_height_is_always_positive(self):
        for x in range(-20, 20, 3):
            for y in range(-20, 20, 3):
                assert terrain_height(7, x, y) >= 1

    def test_neighbouring_cells_are_usually_close_in_height(self):
        """Value noise should be smooth, not white noise -- adjacent
        columns shouldn't differ wildly. A loose sanity check, not a tight
        bound."""
        diffs = [abs(terrain_height(3, x, 0) - terrain_height(3, x + 1, 0))
                 for x in range(30)]
        assert max(diffs) <= 4   # generous given TERRAIN_AMPLITUDE = 6


class TestGenerateChunk:
    def test_fills_a_chunk_with_a_grass_dirt_column(self):
        room = _seeded_room()
        generate_chunk(room, 0, 0)
        x, y = 3, 3
        h = terrain_height(42, x, y)
        assert get_block(room, x, y, h - 1) == "grass"
        if h > 1:
            assert get_block(room, x, y, 0) == "dirt"
        assert get_block(room, x, y, h) is None   # nothing above the surface

    def test_no_op_without_a_seed(self):
        room = _room()   # seed stays None
        generate_chunk(room, 0, 0)
        assert list(iter_blocks(room)) == []

    def test_does_not_regenerate_or_overwrite_an_already_present_chunk(self):
        room = _seeded_room()
        set_block(room, 0, 0, 0, "gold_block")   # a hand-placed edit
        generate_chunk(room, 0, 0)                # must not touch this chunk
        assert get_block(room, 0, 0, 0) == "gold_block"

    def test_generating_twice_is_a_cheap_no_op_the_second_time(self):
        room = _seeded_room()
        generate_chunk(room, 0, 0)
        first = to_block_list(room)
        generate_chunk(room, 0, 0)
        assert to_block_list(room) == first

    def test_removing_a_generated_block_survives_regeneration_attempts(self):
        room = _seeded_room()
        generate_chunk(room, 0, 0)
        x, y = 3, 3
        h = terrain_height(42, x, y)
        assert get_block(room, x, y, h - 1) == "grass"
        remove_block(room, x, y, h - 1)
        assert get_block(room, x, y, h - 1) is None
        generate_chunk(room, 0, 0)   # must not refill the hole
        assert get_block(room, x, y, h - 1) is None


class TestEnsureChunksLoaded:
    def test_generates_every_chunk_within_radius(self):
        room = _seeded_room()
        ensure_chunks_loaded(room, 0, 0, CHUNK_SIZE)
        chunks_present = {_chunk_key(x, y) for x, y, _z, _t in iter_blocks(room)}
        # At minimum the origin chunk and its immediate neighbours.
        assert (0, 0) in chunks_present

    def test_no_op_without_a_seed(self):
        room = _room()
        ensure_chunks_loaded(room, 0, 0, 50)
        assert list(iter_blocks(room)) == []

    def test_a_far_away_center_generates_far_away_chunks_not_the_origin(self):
        room = _seeded_room()
        far = CHUNK_SIZE * 20
        ensure_chunks_loaded(room, far, far, CHUNK_SIZE // 2)
        chunks_present = {_chunk_key(x, y) for x, y, _z, _t in iter_blocks(room)}
        assert (0, 0) not in chunks_present
        assert _chunk_key(far, far) in chunks_present


class TestUnloadDistantChunks:
    def test_evicts_generated_chunks_outside_the_radius(self):
        room = _seeded_room()
        generate_chunk(room, 0, 0)
        generate_chunk(room, 50, 50)   # far away
        unload_distant_chunks(room, 0, 0, CHUNK_SIZE)
        chunks_present = {_chunk_key(x, y) for x, y, _z, _t in iter_blocks(room)}
        assert (0, 0) in chunks_present
        assert (50, 50) not in chunks_present

    def test_never_evicts_a_touched_chunk(self):
        room = _seeded_room()
        generate_chunk(room, 50, 50)
        set_block(room, 50 * CHUNK_SIZE, 50 * CHUNK_SIZE, 0, "gold_block")
        unload_distant_chunks(room, 0, 0, CHUNK_SIZE)
        assert get_block(room, 50 * CHUNK_SIZE, 50 * CHUNK_SIZE, 0) == "gold_block"

    def test_no_op_without_a_seed(self):
        room = _room()
        set_block(room, 0, 0, 0, "stone")
        unload_distant_chunks(room, 1000, 1000, 1)
        assert get_block(room, 0, 0, 0) == "stone"


class TestSaveLoadRoundTrip:
    def test_only_touched_chunks_are_saved_not_generated_ones(self):
        room = _seeded_room()
        generate_chunk(room, 0, 0)
        generate_chunk(room, 1, 0)   # generated, never edited -- must not be saved
        set_block(room, 0, 0, 99, "gold_block")   # touches chunk (0, 0) only

        saved = to_touched_block_list(room)
        # Touched chunk (0, 0) saves its FULL current content (generated
        # grass/dirt + the edit), not a cell-level diff -- see
        # to_touched_block_list's own docstring for why. What matters here:
        # chunk (1, 0)'s generated content is NOT among it.
        assert {"x": 0, "y": 0, "z": 99, "type": "gold_block"} in saved
        assert all(_chunk_key(e["x"], e["y"]) == (0, 0) for e in saved)
        assert len(saved) > 1   # the generated content came along with the edit

    def test_load_world_state_restores_seed_and_touched_content(self):
        room = _seeded_room()
        generate_chunk(room, 0, 0)
        generate_chunk(room, 1, 0)   # untouched -- must NOT be restored
        set_block(room, 0, 0, 99, "gold_block")
        saved = to_touched_block_list(room)

        fresh = _room()
        load_world_state(fresh, 42, saved)
        assert block_world_state(fresh)["seed"] == 42
        assert get_block(fresh, 0, 0, 99) == "gold_block"
        # Touched chunk (0, 0)'s generated grass/dirt came along with the
        # save (full-chunk-content, not a diff) -- it's already there,
        # not merely regeneratable.
        h = terrain_height(42, 0, 0)
        assert get_block(fresh, 0, 0, h - 1) == "grass"

        # Chunk (1, 0) was generated but never touched, so it was NOT
        # saved -- confirm it comes back only once actually regenerated.
        h1 = terrain_height(42, CHUNK_SIZE, 0)
        assert get_block(fresh, CHUNK_SIZE, 0, h1 - 1) is None
        generate_chunk(fresh, 1, 0)
        assert get_block(fresh, CHUNK_SIZE, 0, h1 - 1) == "grass"

    def test_old_flat_list_format_still_loads_with_no_seed(self):
        """A pre-Phase-2 blocks/<room>.json (a bare list, no generation
        concept) must keep working -- load_block_list's own contract is
        unchanged; a room loaded this way simply never gets a seed."""
        from extensions.block_world.state import load_block_list
        room = _room()
        load_block_list(room, [{"x": 1, "y": 1, "z": 0, "type": "stone"}])
        assert block_world_state(room)["seed"] is None
        assert get_block(room, 1, 1, 0) == "stone"


class TestEditorIOFormatMigration:
    def test_seeded_save_round_trips_through_disk(self, tmp_path):
        from editors.block_world_editor.io import load_room_blocks, save_room_blocks
        import json

        room = _seeded_room(seed=7)
        generate_chunk(room, 0, 0)
        set_block(room, 0, 0, 99, "gold_block")
        path = save_room_blocks(room, tmp_path, "room0")

        on_disk = json.loads(path.read_text(encoding="utf-8"))
        assert on_disk["seed"] == 7
        assert {"x": 0, "y": 0, "z": 99, "type": "gold_block"} in on_disk["blocks"]

        fresh = _room()
        assert load_room_blocks(fresh, tmp_path, "room0") is True
        assert block_world_state(fresh)["seed"] == 7
        assert get_block(fresh, 0, 0, 99) == "gold_block"

    def test_an_unseeded_room_still_saves_the_plain_list_shape(self, tmp_path):
        """Backward compatibility: a room that never used generation must
        keep producing the exact pre-Phase-2 file shape (a bare list), not
        the new dict wrapper -- nothing about an existing save changes
        unless the room actually has a seed."""
        from editors.block_world_editor.io import save_room_blocks
        import json

        room = _room()
        set_block(room, 1, 1, 0, "stone")
        path = save_room_blocks(room, tmp_path, "room0")
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(on_disk, list)
        assert on_disk == [{"x": 1, "y": 1, "z": 0, "type": "stone"}]


class TestLoadBlockWorldActionFormatMigration:
    """extensions/block_world/handlers.py's load_block_world action must
    accept both the old bare-list file shape and the new seeded-dict
    shape -- the same detection editors/block_world_editor/io.py uses."""

    def _room_and_handler(self, tmp_path, data_file_name, payload):
        import json
        from runtime.action_executor import ActionExecutor
        from events.plugin_loader import load_all_plugins

        data_path = tmp_path / data_file_name
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(json.dumps(payload), encoding="utf-8")

        class _Runner:
            def __init__(self):
                self.current_room = _room()
                self.project_path = str(tmp_path)
                self.global_variables = {}

        class _Instance:
            def __init__(self):
                self.object_name = "obj_person"
                self.action_executor = None

        runner = _Runner()
        executor = ActionExecutor(game_runner=runner)
        load_all_plugins(executor)
        instance = _Instance()
        instance.action_executor = executor
        executor.action_handlers["load_block_world"](
            instance, {"data_file": data_file_name})
        return runner.current_room

    def test_loads_the_old_bare_list_shape(self, tmp_path):
        room = self._room_and_handler(
            tmp_path, "blocks/legacy.json",
            [{"x": 2, "y": 2, "z": 0, "type": "brick"}])
        assert get_block(room, 2, 2, 0) == "brick"
        assert block_world_state(room)["seed"] is None

    def test_loads_the_new_seeded_dict_shape(self, tmp_path):
        room = self._room_and_handler(
            tmp_path, "blocks/seeded.json",
            {"seed": 99, "blocks": [{"x": 3, "y": 3, "z": 0, "type": "gold_block"}]})
        assert get_block(room, 3, 3, 0) == "gold_block"
        assert block_world_state(room)["seed"] == 99


class TestGenerationThroughTheRealAction:
    """End-to-end: the enable_block_world_view action's generate/seed
    params actually reach state.py's seed, and render_block_world_view
    actually generates chunks around the camera as a real side effect --
    not just state.py's primitives called directly, which every other
    test class in this file does."""

    def test_render_generates_chunks_around_the_camera(self):
        from runtime.action_executor import ActionExecutor
        from events.plugin_loader import load_all_plugins
        from extensions.block_world.renderer import render_block_world_view

        room = _room()
        from runtime.game_runner import GameInstance
        camera = GameInstance("obj_person", 160, 160, {}, action_executor=None)
        camera._cached_object_data = {"solid": False}
        camera._cached_width = 32
        camera._cached_height = 32
        camera.facing_angle = 0.0
        room.instances.append(camera)

        class _Runner:
            def __init__(self):
                self.current_room = room
                self.global_variables = {}

        executor = ActionExecutor(game_runner=_Runner())
        load_all_plugins(executor)
        camera.action_executor = executor
        executor.action_handlers["enable_block_world_view"](camera, {
            "camera_object": "obj_person", "generate": True, "seed": 5,
            "render_distance": 8, "cell_size": 32,
        })
        assert block_world_state(room)["seed"] == 5
        assert list(iter_blocks(room)) == []   # nothing generated yet

        pygame.display.set_mode((1, 1))
        screen = pygame.Surface((320, 240))
        render_block_world_view(room, screen)

        assert list(iter_blocks(room)) != []   # generation actually ran
        # The camera's own cell (160px / 32 cell_size = cell 5,5) generated
        # real ground under it, at the height terrain_height predicts.
        h = terrain_height(5, 5, 5)
        assert get_block(room, 5, 5, h - 1) == "grass"
