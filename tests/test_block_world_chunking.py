"""Tier 7e Phase 1 (docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md): chunked
storage, generation-free. state.py's public API (get_block/set_block/
remove_block/iter_blocks/to_block_list/load_block_list/column_index/
stack_top/ground_layer/can_enter) is unchanged and already covered by
the pre-existing block_world test suite (which stayed green across this
refactor, the "no new gameplay, byte-identical behaviour" proof this
phase's plan explicitly calls for). This file targets what's actually
NEW: the chunk boundary/negative-coordinate math and the per-chunk cache
invalidation the old flat-dict storage never had a concept of.
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
    CHUNK_SIZE, _chunk_key, get_block, set_block, remove_block, iter_blocks,
    to_block_list, load_block_list, column_index, peek_blocks,
)


def _room():
    return GameRoom("bw_chunk_test", {"width": 640, "height": 640}, action_executor=None)


class TestChunkKeyMath:
    def test_origin_chunk(self):
        assert _chunk_key(0, 0) == (0, 0)

    def test_within_the_first_chunk(self):
        assert _chunk_key(CHUNK_SIZE - 1, CHUNK_SIZE - 1) == (0, 0)

    def test_exactly_at_the_next_chunk_boundary(self):
        assert _chunk_key(CHUNK_SIZE, CHUNK_SIZE) == (1, 1)

    def test_negative_coordinates_floor_correctly(self):
        # Python's // floors toward -inf, so -1 belongs to chunk -1 (not
        # chunk 0) -- the same convention a generated world's negative-space
        # chunks (Phase 2+) will rely on.
        assert _chunk_key(-1, -1) == (-1, -1)
        assert _chunk_key(-CHUNK_SIZE, -CHUNK_SIZE) == (-1, -1)
        assert _chunk_key(-CHUNK_SIZE - 1, -CHUNK_SIZE - 1) == (-2, -2)


class TestCrossChunkCorrectness:
    def test_blocks_in_different_chunks_are_independent(self):
        room = _room()
        set_block(room, 0, 0, 0, "stone")
        set_block(room, CHUNK_SIZE, 0, 0, "gold_block")
        assert get_block(room, 0, 0, 0) == "stone"
        assert get_block(room, CHUNK_SIZE, 0, 0) == "gold_block"

        remove_block(room, 0, 0, 0)
        assert get_block(room, 0, 0, 0) is None
        assert get_block(room, CHUNK_SIZE, 0, 0) == "gold_block"

    def test_negative_coordinate_blocks_round_trip(self):
        room = _room()
        set_block(room, -5, -5, -1, "brick")
        assert get_block(room, -5, -5, -1) == "brick"
        assert list(iter_blocks(room)) == [(-5, -5, -1, "brick")]

    def test_iter_blocks_spans_every_chunk(self):
        room = _room()
        set_block(room, 0, 0, 0, "stone")
        set_block(room, CHUNK_SIZE, 0, 0, "brick")
        set_block(room, 0, CHUNK_SIZE, 0, "cobble")
        set_block(room, -CHUNK_SIZE, -CHUNK_SIZE, 0, "wool_red")
        found = sorted((x, y, z, t) for x, y, z, t in iter_blocks(room))
        assert found == [
            (-CHUNK_SIZE, -CHUNK_SIZE, 0, "wool_red"),
            (0, 0, 0, "stone"),
            (0, CHUNK_SIZE, 0, "cobble"),
            (CHUNK_SIZE, 0, 0, "brick"),
        ]

    def test_to_block_list_load_block_list_round_trip_across_chunks(self):
        room = _room()
        set_block(room, 0, 0, 0, "stone")
        set_block(room, CHUNK_SIZE * 3, CHUNK_SIZE * -2, 5, "diamond_block")
        saved = to_block_list(room)

        fresh = _room()
        load_block_list(fresh, saved)
        assert get_block(fresh, 0, 0, 0) == "stone"
        assert get_block(fresh, CHUNK_SIZE * 3, CHUNK_SIZE * -2, 5) == "diamond_block"
        assert sorted(to_block_list(fresh), key=lambda e: (e["x"], e["y"], e["z"])) == \
            sorted(saved, key=lambda e: (e["x"], e["y"], e["z"]))

    def test_column_index_merges_across_chunks(self):
        room = _room()
        set_block(room, 0, 0, 0, "stone")
        set_block(room, 0, 0, 1, "cobble")
        set_block(room, CHUNK_SIZE, 0, 0, "brick")
        index = column_index(room)
        assert index[(0, 0)] == [(0, "stone"), (1, "cobble")]
        assert index[(CHUNK_SIZE, 0)] == [(0, "brick")]


class TestPerChunkCacheInvalidation:
    def test_editing_one_chunk_does_not_rebuild_anothers_cached_columns(self):
        room = _room()
        set_block(room, 0, 0, 0, "stone")
        set_block(room, CHUNK_SIZE, 0, 0, "brick")

        first = column_index(room)
        other_chunk_columns = first[(CHUNK_SIZE, 0)]

        # Edit a DIFFERENT chunk -- the untouched chunk's own per-chunk
        # cache entry must survive (same list object), even though the
        # merged dict column_index() returns is necessarily a new dict.
        set_block(room, 1, 1, 0, "gold_block")
        second = column_index(room)
        assert second[(CHUNK_SIZE, 0)] is other_chunk_columns

    def test_column_index_is_cached_between_calls_when_nothing_changed(self):
        room = _room()
        set_block(room, 1, 1, 0, "dirt")
        assert column_index(room) is column_index(room)

    def test_column_index_cache_is_invalidated_by_a_mutation(self):
        room = _room()
        set_block(room, 1, 1, 0, "dirt")
        first = column_index(room)
        set_block(room, 2, 2, 0, "stone")
        second = column_index(room)
        assert first is not second
        assert (2, 2) in second and (2, 2) not in first

    def test_remove_of_a_never_placed_block_does_not_invalidate_the_cache(self):
        """remove_block on an already-air cell must be a true no-op --
        including not needlessly invalidating a chunk's cache, which
        would otherwise force a pointless rebuild on the next
        column_index() call for a chunk that didn't actually change."""
        room = _room()
        set_block(room, 1, 1, 0, "dirt")
        first = column_index(room)
        remove_block(room, 5, 5, 5)   # never set -- pure no-op
        second = column_index(room)
        assert first is second


class TestPeekBlocksShapeIsChunked:
    def test_peek_blocks_returns_the_chunk_dict(self):
        room = _room()
        set_block(room, 0, 0, 0, "stone")
        set_block(room, CHUNK_SIZE, 0, 0, "brick")
        chunks = peek_blocks(room)
        assert set(chunks.keys()) == {(0, 0), (1, 0)}

    def test_peek_blocks_is_none_for_an_untouched_room(self):
        assert peek_blocks(_room()) is None
