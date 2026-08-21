"""End-to-end smoke test for the sky_strike_1 sample -- a Xevious-style
vertical shooter (player ship, air-to-air bullets, air-to-ground bombs),
mirroring tests/test_block_world_1_sample.py's pattern: run the REAL
project through the REAL GameRunner loop with injected keyboard events
and, for the collision assertions, real create_instance calls -- not a
hand-built room, matching that file's own reasoning (a partially
initialized room silently produces the wrong thing and makes a naive
test pass for the wrong reason).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame, skip_without_pyside6

pytestmark = skip_without_pygame

import pygame
pygame.init()

PROJECT_JSON = str(REPO_ROOT / "samples" / "sky_strike_1" / "project.json")


def _run(frames, on_tick=None):
    """Run the real sample for `frames` ticks, calling on_tick(frame_number,
    runner) before each simulated tick so a test can inject input or spawn
    instances at exact frames. Returns the finished GameRunner."""
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
            if on_tick:
                on_tick(f, runner)
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
        # GameRunner.cleanup() calls pygame.quit(); reinit so later tests in
        # the same process aren't left with a torn-down display (same fixup
        # test_block_world_1_sample.py's _run_with_keys needs).
        pygame.init()
        pygame.display.set_mode((1, 1))

    assert result is not False, "game loop reported a fatal crash"
    assert state["frames"] == frames
    return runner


def _spawn(runner, obj_name, x, y):
    """Spawn an instance via the real create_instance action path (the same
    one the sample's own alarm handlers and this test both go through), so
    the instance is wired up exactly like a normally-spawned one."""
    room = runner.current_room
    player = next(i for i in room.instances if i.object_name == "obj_player")
    runner.action_executor.execute_create_instance_action(
        player, {"object": obj_name, "x": x, "y": y, "relative": False})
    return room.instances[-1]


class TestSkyStrike1Smoke:
    def test_runs_without_crashing_and_sets_up_the_scrolling_ground(self):
        runner = _run(10)
        room = runner.current_room
        assert room is not None
        assert room.name == "room0"
        # game_start's set_background configured continuous downward scroll.
        assert room.bg_vspeed == 2.0
        assert room.tile_vertical is True
        assert runner.score == 0
        assert runner.lives == 3

    def test_player_movement_clamps_to_the_room_bounds(self):
        def hold_left(f, runner):
            if f == 1:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))

        runner = _run(60, on_tick=hold_left)
        player = next(i for i in runner.current_room.instances
                      if i.object_name == "obj_player")
        assert player.x >= 4  # never crosses the left edge clamp

    def test_alarms_spawn_enemy_planes_and_ground_targets(self):
        """A plane is due at step 40, a ground target at step 70 (set in
        game_start) -- both must survive their own creation (the sample's
        one real authoring bug this session: spawning fully off-screen at
        y=-30/-40 triggered an IMMEDIATE outside_room self-destruct, since
        that event fires once a sprite is entirely outside the room, at
        creation time as much as in flight)."""
        runner = _run(75)
        from collections import Counter
        counts = Counter(i.object_name for i in runner.current_room.instances)
        assert counts["obj_enemy_plane"] >= 1
        assert counts["obj_ground_target"] >= 1

    def test_bullet_destroys_enemy_plane_and_scores(self):
        def place(f, runner):
            if f == 3:
                _spawn(runner, "obj_enemy_plane", 200, 300)
                _spawn(runner, "obj_bullet", 200, 305)

        runner = _run(15, on_tick=place)
        assert runner.score == 50
        assert not any(i.object_name == "obj_enemy_plane"
                       for i in runner.current_room.instances)

    def test_bomb_destroys_ground_target_and_scores(self):
        def place(f, runner):
            if f == 3:
                _spawn(runner, "obj_ground_target", 100, 300)
                _spawn(runner, "obj_bomb", 100, 295)

        runner = _run(15, on_tick=place)
        assert runner.score == 100
        assert not any(i.object_name == "obj_ground_target"
                       for i in runner.current_room.instances)

    def test_bullet_does_not_destroy_ground_targets(self):
        """The whole point of the sample: bullets are air-to-air only."""
        def place(f, runner):
            if f == 3:
                _spawn(runner, "obj_ground_target", 100, 300)
                _spawn(runner, "obj_bullet", 100, 305)

        runner = _run(20, on_tick=place)
        assert runner.score == 0
        assert any(i.object_name == "obj_ground_target"
                  for i in runner.current_room.instances)

    def test_bomb_does_not_destroy_enemy_planes(self):
        """And bombs are air-to-ground only -- no collision handler exists
        for obj_bomb x obj_enemy_plane, so nothing should happen at all."""
        def place(f, runner):
            if f == 3:
                _spawn(runner, "obj_enemy_plane", 200, 300)
                _spawn(runner, "obj_bomb", 200, 305)

        runner = _run(20, on_tick=place)
        assert runner.score == 0
        assert any(i.object_name == "obj_enemy_plane"
                  for i in runner.current_room.instances)

    def test_colliding_with_an_enemy_plane_costs_a_life(self):
        def crash(f, runner):
            if f == 3:
                player = next(i for i in runner.current_room.instances
                             if i.object_name == "obj_player")
                _spawn(runner, "obj_enemy_plane", player.x, player.y)

        runner = _run(15, on_tick=crash)
        assert runner.lives == 2
        assert not any(i.object_name == "obj_enemy_plane"
                       for i in runner.current_room.instances)

    def test_no_more_lives_restarts_the_game(self):
        def deplete(f, runner):
            if f == 3:
                runner.score = 500
                runner.lives = 1
                player = next(i for i in runner.current_room.instances
                             if i.object_name == "obj_player")
                _spawn(runner, "obj_enemy_plane", player.x, player.y)

        runner = _run(20, on_tick=deplete)
        # restart_game re-runs game_start, which resets both to their
        # starting values -- confirms the whole game-over loop closes.
        assert runner.score == 0
        assert runner.lives == 3


class TestSkyStrike1WelcomeTabAndGuide:
    """Registration + guide lookup, mirroring the equivalent coverage that
    used to pin block_world_1 here before it was de-showcased (see TODO.md's
    "Block World renderer" entry) -- same real-offscreen-QApplication
    pattern as tests/test_sample_docs_dialog.py. Needs PySide6 on top of
    this module's pygame requirement, hence the extra class-level mark."""

    pytestmark = skip_without_pyside6

    def test_registered_in_the_welcome_tab(self):
        from widgets.welcome_tab import SAMPLE_PROJECTS
        assert ("samples/sky_strike_1", "Sky Strike — Level 1") in SAMPLE_PROJECTS

    def test_guide_is_listed_and_renders(self, monkeypatch):
        from PySide6.QtWidgets import QApplication
        QApplication.instance() or QApplication([])
        from widgets.welcome_tab import SampleDocsDialog, SAMPLE_PROJECTS

        # Pin the guide language -- see test_sample_docs_dialog.py's own
        # note: guide_path() resolves README.<lang>.md next to README.md, so
        # on a French-configured machine this would correctly show
        # README.fr.md and the English assertions below would fail for
        # entirely the wrong reason.
        monkeypatch.setattr(SampleDocsDialog, "_guide_language",
                            staticmethod(lambda: "en"))

        dlg = SampleDocsDialog(SAMPLE_PROJECTS, REPO_ROOT)
        labels = dlg.sample_labels()
        assert "Sky Strike — Level 1" in labels

        row = labels.index("Sky Strike — Level 1")
        dlg._show_row(row)
        text = dlg._viewer.toPlainText()
        assert "Sky Strike" in text
        assert "xevious" in text.lower()
