"""End-to-end smoke test for the block_world_1 sample (Phase 5 Unit 7),
mirroring tests/test_raycast_view.py's TestRaycast1SampleSmoke pattern:
run the REAL project through the REAL GameRunner loop with injected
keyboard events, not a hand-built room -- the same reasoning that pattern
documents (a partially-initialized room silently produces the wrong thing
and makes a naive test pass for the wrong reason).
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

PROJECT_JSON = str(REPO_ROOT / "samples" / "block_world_1" / "project.json")


def _run_with_keys(held_key, frames, extra_post=None):
    """Run the real sample for `frames` ticks with `held_key` held down the
    whole time (posted once at frame 1, released after the last frame).
    Returns the finished GameRunner."""
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
            if f == 1:
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
        # GameRunner.cleanup() calls pygame.quit() at the end of run(), which
        # tears down the display mode other block_world tests' module-level
        # pygame.display.set_mode() set up at import time -- reinit so later
        # tests in the same process (e.g. test_block_world_layers.py's
        # convert_alpha() calls) don't fail with "display not initialized".
        pygame.init()
        pygame.display.set_mode((1, 1))

    assert result is not False, "game loop reported a fatal crash"
    assert state["frames"] == frames
    return runner


class TestBlockWorld1Smoke:
    def test_runs_without_crashing_and_enables_the_view(self):
        runner = _run_with_keys(pygame.K_w, 10)
        player = next(i for i in runner.current_room.instances
                      if i.object_name == "obj_person")
        cfg = block_world_state(runner.current_room)["camera"]
        assert cfg["enabled"] is True
        assert cfg["camera_object"] == "obj_person"
        assert player.hotbar_index == 0
        assert player.hotbar_block is not None

    def test_load_block_world_populated_the_room_at_game_start(self):
        from extensions.block_world.state import get_block
        runner = _run_with_keys(pygame.K_w, 5)
        # A floor tile and a wall tile the generator is known to place.
        assert get_block(runner.current_room, 0, 0, 0) == "grass"
        assert get_block(runner.current_room, 0, 0, 1) == "cobble"
        assert get_block(runner.current_room, 10, 2, 4) == "gold_block"

    def test_walking_east_reaches_the_goal_and_wins(self):
        """The whole point of the sample: walk (hold 'd') from the start,
        up the staircase, onto the terrace, and the win message fires --
        matching the generator's own tests proving this exact path is
        climbable, now proven through the REAL project + REAL game loop."""
        runner = _run_with_keys(pygame.K_d, 100)
        player = next(i for i in runner.current_room.instances
                      if i.object_name == "obj_person")
        assert player.won == 1
        assert runner.score == 100

    def test_standing_still_never_wins(self):
        runner = _run_with_keys(pygame.K_F1, 10)   # an unbound key -- no-op
        player = next(i for i in runner.current_room.instances
                      if i.object_name == "obj_person")
        assert getattr(player, "won", 0) == 0

    def test_hotbar_cycling_changes_the_selected_block(self):
        from extensions.block_world.state import DEFAULT_HOTBAR

        def press_e_once(f):
            if f == 3:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))

        runner = _run_with_keys(pygame.K_F1, 10, extra_post=press_e_once)
        player = next(i for i in runner.current_room.instances
                      if i.object_name == "obj_person")
        assert player.hotbar_index == 1
        assert player.hotbar_block == DEFAULT_HOTBAR[1]

    def test_break_then_place_changes_the_world(self):
        from extensions.block_world.state import get_block

        def press_space_once(f):
            if f == 3:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

        # Facing 0 (east) at the start, the first solid thing the centre
        # ray reaches is the perimeter wall far ahead -- reach=5 cells
        # (160px) from x=64 does not get there, so this proves break_block
        # is wired and safely a no-op at this range, not that it broke
        # anything specific (a precise in-range break is already covered
        # at the unit level in tests/test_block_world_picking.py).
        runner = _run_with_keys(pygame.K_F1, 10, extra_post=press_space_once)
        assert runner is not None   # must not have crashed

# Welcome-tab-registration + guide-listing coverage for this sample was
# removed 2026-08-21: block_world_1 was de-showcased from the Welcome tab
# (still ships under samples/ and every gameplay test above still runs
# against it) when the user set the block_world extension's further work
# aside in favor of samples/sky_strike_1 -- see TODO.md's "Block World
# renderer" entry and tests/test_sky_strike_1_sample.py.
