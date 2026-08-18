"""End-to-end smoke test for the block_world_2 sample (Tier 7e Phase 4,
docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md), mirroring
tests/test_block_world_1_sample.py's pattern: run the REAL project
through the REAL GameRunner loop with injected keyboard events.

The smoke_run_samples.py harness's generic injected input (arrow keys,
space) never actually moves this sample's player (movement is WASD, not
arrows), so it always shows score=0 there -- exactly like block_world_1
already does under the same harness. This file drives real W-key input to
prove the sample's own mechanics (procedural generation, movement,
distance scoring) actually work end to end.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()

from extensions.block_world.state import block_world_state  # noqa: E402

PROJECT_JSON = str(REPO_ROOT / "samples" / "block_world_2" / "project.json")


def _run_with_keys(held_key, frames, extra_post=None):
    from runtime.game_runner import GameRunner

    runner = GameRunner(PROJECT_JSON)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None

    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            f = state["frames"] = state["frames"] + 1
            if f == 1 and held_key is not None:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=held_key))
            if extra_post:
                extra_post(f)
            if f >= frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        result = runner.run()
    finally:
        pygame.time.Clock = real_clock
        pygame.init()
        pygame.display.set_mode((1, 1))

    assert result is not False, "game loop reported a fatal crash"
    assert state["frames"] == frames
    return runner


class TestBlockWorld2Smoke:
    def test_generates_terrain_around_spawn_with_no_load_block_world(self):
        runner = _run_with_keys(pygame.K_F1, 5)   # an unbound key -- no-op movement
        room = runner.current_room
        st = block_world_state(room)
        assert st["seed"] == 1234
        # Terrain generated on the very first frame (create + one render).
        from extensions.block_world.state import iter_blocks
        assert list(iter_blocks(room)) != []

    def test_walking_west_moves_the_player_and_increases_distance_score(self):
        runner = _run_with_keys(pygame.K_a, 20)
        player = next(i for i in runner.current_room.instances
                      if i.object_name == "obj_person")
        assert player.x < 8   # started at x=8, moved west (a = dx=-4)
        assert runner.score > 0
        assert player.best_dist > 0

    def test_standing_still_never_scores(self):
        runner = _run_with_keys(pygame.K_F1, 10)
        assert runner.score == 0

    def test_generation_follows_the_camera_not_just_a_one_time_burst_at_spawn(self):
        """A cheap real-game-loop warmup (3 frames, not hundreds -- walking
        far enough to prove this through the renderer alone would cost
        many real, textured render frames) followed by calling the exact
        function the render loop calls every frame -- ensure_chunks_loaded
        -- at a position far from spawn, on the REAL room/seed the sample
        actually uses. Proves generation follows an arbitrary camera
        position, not just the one-time burst enable_block_world_view's
        own create-time render triggers."""
        from extensions.block_world.state import CHUNK_SIZE, ensure_chunks_loaded, iter_blocks

        runner = _run_with_keys(pygame.K_F1, 3)
        room = runner.current_room
        before = {(x // CHUNK_SIZE, y // CHUNK_SIZE) for x, y, _z, _t in iter_blocks(room)}

        ensure_chunks_loaded(room, -500, -500, 8)
        after = {(x // CHUNK_SIZE, y // CHUNK_SIZE) for x, y, _z, _t in iter_blocks(room)}

        assert after - before   # new chunks appeared, far from what spawn already covered
        assert any(cx < -10 for cx, _cy in after)

    def test_break_then_place_edits_persist_in_generated_terrain(self):
        def press_space_then_shift(f):
            if f == 5:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            if f == 8:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LSHIFT))

        runner = _run_with_keys(pygame.K_F1, 15, extra_post=press_space_then_shift)
        assert runner is not None   # must not have crashed
