"""The mon_bloc_1 sample -- "My Blocks — Lesson 1" (docs/
BLOCKLY_SCRATCH_PARITY_PLAN.md item 7: "a bundled sample or tutorial
lesson teaching 'make your own block' — this project's own established
convention for a new teaching feature, not built").

A small coin-collecting game whose real teaching point is in its own
Blockly workspace, not the gameplay: obj_joueur has three collision
events (one per coin colour) that deliberately share the exact same
2-action shape (destroy the coin + add its points) with only the point
value differing -- the obvious repetition the README asks the student to
notice and replace with one custom block (donner_points(montant)).

TestGameplay runs the real project through the real GameRunner loop (no
Blockly/JS involved at all -- the saved project.json is plain actions,
same as every other bundled sample; "My Blocks" is purely an authoring-
time convenience that's already expanded away by the time anything is
saved, confirmed by docs/BLOCKLY_SCRATCH_PARITY_PLAN.md's own design).
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402

PROJECT_JSON = str(REPO_ROOT / "samples" / "mon_bloc_1" / "project.json")
SAMPLE_DIR = REPO_ROOT / "samples" / "mon_bloc_1"


def _run(frames, on_frame=None):
    from runtime.game_runner import GameRunner
    runner = GameRunner(PROJECT_JSON)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None
    st = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            st["f"] += 1
            if on_frame is not None:
                on_frame(st["f"], runner)
            if st["f"] >= frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        result = runner.run()
    finally:
        pygame.time.Clock = real
    assert result is not False
    return runner


def _player(runner):
    for inst in runner.current_room.instances:
        if inst.object_name == "obj_joueur":
            return inst
    return None


class TestGameplay:
    def test_runs_without_crashing(self):
        runner = _run(15)
        names = [i.object_name for i in runner.current_room.instances]
        assert "obj_joueur" in names
        assert "obj_hud" in names

    def test_bronze_coin_awards_five_points(self):
        def on_frame(f, runner):
            if f == 3:
                p = _player(runner)
                p.x, p.y = 60 - 12, 60 - 12  # bronze coin position

        runner = _run(10, on_frame)
        assert runner.score == 5

    def test_silver_coin_awards_ten_points(self):
        def on_frame(f, runner):
            if f == 3:
                p = _player(runner)
                p.x, p.y = 160 - 12, 40 - 12  # silver coin position

        runner = _run(10, on_frame)
        assert runner.score == 10

    def test_gold_coin_awards_twenty_five_points(self):
        def on_frame(f, runner):
            if f == 3:
                p = _player(runner)
                p.x, p.y = 420 - 12, 60 - 12  # gold coin position

        runner = _run(10, on_frame)
        assert runner.score == 25

    def test_collecting_a_coin_destroys_only_that_instance(self):
        def on_frame(f, runner):
            if f == 3:
                p = _player(runner)
                p.x, p.y = 60 - 12, 60 - 12

        runner = _run(10, on_frame)
        remaining = [i.object_name for i in runner.current_room.instances]
        assert remaining.count("obj_piece_bronze") == 1  # started with 2
        assert remaining.count("obj_piece_argent") == 2
        assert remaining.count("obj_piece_or") == 2

    def test_arrow_key_movement_does_not_crash(self):
        def on_frame(f, runner):
            if f == 5:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
            if f == 15:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_RIGHT))
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
            if f == 25:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_UP))

        runner = _run(30, on_frame)
        assert _player(runner) is not None


class TestTheDocumentedRepetitionActuallyExists:
    """Pins the exact "before" shape the README's lesson walks the
    student through replacing -- if a future edit to this sample
    accidentally fixes the repetition in place, this must be updated
    deliberately, not silently."""

    def _events(self):
        data = json.loads((SAMPLE_DIR / "objects" / "obj_joueur.json").read_text(encoding="utf-8"))
        return data["events"]

    def test_three_collision_events_share_the_destroy_then_score_shape(self):
        events = self._events()
        for coin_object, points in (
            ("obj_piece_bronze", 5), ("obj_piece_argent", 10), ("obj_piece_or", 25),
        ):
            event = events[f"collision_with_{coin_object}"]
            assert event["target_object"] == coin_object
            actions = event["actions"]
            assert len(actions) == 2
            assert actions[0]["action"] == "destroy_instance"
            assert actions[0]["parameters"]["target"] == "other"
            assert actions[1]["action"] == "set_score"
            assert actions[1]["parameters"]["value"] == str(points)
            assert actions[1]["parameters"]["relative"] is True

    def test_only_the_point_value_differs_between_the_three(self):
        """The whole teaching point: strip out the one value that
        differs and the three action lists become byte-identical."""
        events = self._events()
        normalized = []
        for coin_object in ("obj_piece_bronze", "obj_piece_argent", "obj_piece_or"):
            actions = events[f"collision_with_{coin_object}"]["actions"]
            stripped = json.loads(json.dumps(actions))
            stripped[1]["parameters"]["value"] = "N"
            normalized.append(stripped)
        assert normalized[0] == normalized[1] == normalized[2]


class TestSampleRegistration:
    def test_registered_in_welcome_tab_and_smoke(self):
        from widgets.welcome_tab import SAMPLE_PROJECTS
        from tools.smoke_run_samples import SAMPLES
        assert ("samples/mon_bloc_1", "My Blocks — Lesson 1") in SAMPLE_PROJECTS
        assert "mon_bloc_1" in SAMPLES

    def test_guides_exist(self):
        assert (SAMPLE_DIR / "README.md").exists()
        assert (SAMPLE_DIR / "README.fr.md").exists()

    def test_credits_file_exists(self):
        assert (SAMPLE_DIR / "CREDITS.txt").exists()

    def test_excluded_from_junior_and_beginner_sample_folders(self):
        """My Blocks is itself excluded from junior's Blockly toolbox
        (Feature 2's own product decision) -- a sample teaching it has
        no place in a tier that can't show the feature at all."""
        from config.editions import EDITIONS
        for tier in ("junior", "beginner"):
            folders = EDITIONS[tier]["sample_folders"]
            assert folders is not None
            assert "mon_bloc_1" not in folders
