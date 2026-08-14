"""save_game/load_game (TODO.md's "UI metadata coverage for runtime actions"
entry lists these among the actions deliberately kept out of the UI "pending
a functional check" — this is that check).

Investigation found the handlers ARE largely real (runtime/action_executor.py
execute_save_game_action/execute_load_game_action write/read real JSON,
restore score/lives/health/global_variables, and _restore_instances matches
saved instances back onto live ones by object_name), but ONE real path was
dead: loading a save whose room differs from the current room set
instance._load_room_name/_load_instances -- attributes runtime/game_runner.py
never once reads. load_game across a room change silently did nothing beyond
logging "Will load room: X".

Fixed by reusing the SAME deferred-room-change mechanism every other
room-changing action already uses (instance.goto_room_target, consumed by
GameRunner.update()'s existing goto_room_target branch, which calls
change_room synchronously) -- a new instance._pending_load_instances rides
alongside it and is restored via ActionExecutor._restore_instances right
after change_room returns, in the same branch, before the frame's `return`.

With the functional check passed and the one real bug fixed, save_game/
load_game are now registered in events/action_types.py (category "Game",
a single `filename` string param, matching the open_webpage/set_room_caption
precedent) -- this file covers both the runtime behavior and that
registration.

Desktop-runtime-only for now, same as many already-registered actions
(TODO.md's "Kivy export — long-tail action coverage": unhandled actions
fall through to a no-op on export, ported opportunistically) -- neither
Kivy nor HTML5 export has codegen for these two, and no bundled sample
uses them yet, so this doesn't regress the export feature-parity matrix.
"""
import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402


def _write_project(tmp_path):
    project = {
        "name": "save_load_syn",
        "room_order": ["room_a", "room_b"],
        "assets": {
            "sprites": {},
            "objects": {
                "obj_player": {"name": "obj_player", "sprite": "", "events": {}},
            },
            "rooms": {
                "room_a": {
                    "name": "room_a", "width": 320, "height": 240,
                    "instances": [{"object_name": "obj_player", "x": 10, "y": 10}],
                },
                "room_b": {
                    "name": "room_b", "width": 320, "height": 240,
                    "instances": [{"object_name": "obj_player", "x": 50, "y": 50}],
                },
            },
        },
        "settings": {},
    }
    proj_dir = tmp_path / "proj"
    proj_dir.mkdir()
    (proj_dir / "project.json").write_text(json.dumps(project), encoding="utf-8")
    return proj_dir


class _FakeClock:
    """Drives the real GameRunner.run_game_loop for a fixed number of frames,
    running a caller-supplied action at each named frame."""

    def __init__(self, runner, actions, max_frames):
        self.runner = runner
        self.actions = actions  # {frame_number: callable}
        self.max_frames = max_frames
        self.frame = 0

    def tick(self, fps=0):
        self.frame += 1
        action = self.actions.get(self.frame)
        if action:
            action()
        if self.frame >= self.max_frames:
            self.runner.running = False
        return 0

    def get_fps(self):
        return 60.0


def _run_with_frame_actions(runner, actions, max_frames=10):
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None

    real_clock = pygame.time.Clock
    pygame.time.Clock = lambda: _FakeClock(runner, actions, max_frames)
    try:
        return runner.run()
    finally:
        pygame.time.Clock = real_clock


def _player(runner):
    return next(i for i in runner.current_room.instances if i.object_name == "obj_player")


class TestActionRegistration:
    def test_save_and_load_game_resolve(self):
        from events.action_types import get_action_type
        for name in ("save_game", "load_game"):
            action_type = get_action_type(name)
            assert action_type is not None, f"{name} not registered"
            assert action_type.category == "Game"
            params = {p.name for p in action_type.parameters}
            assert params == {"filename"}


class TestSaveLoadSameRoom:
    def test_load_restores_position_and_custom_var(self, tmp_path):
        from runtime.game_runner import GameRunner

        proj_dir = _write_project(tmp_path)
        runner = GameRunner(str(proj_dir / "project.json"))

        def do_save():
            player = _player(runner)
            player.x, player.y = 111.0, 222.0
            player.score_bonus = 42  # a custom instance var
            runner.action_executor.execute_save_game_action(
                player, {"filename": "slot1.sav"})

        def mess_up_then_load():
            player = _player(runner)
            player.x, player.y = 0.0, 0.0
            runner.action_executor.execute_load_game_action(
                player, {"filename": "slot1.sav"})

        result = _run_with_frame_actions(
            runner, {2: do_save, 4: mess_up_then_load}, max_frames=6)

        assert result is not False, "game loop reported a fatal crash"
        player = _player(runner)
        assert (player.x, player.y) == (111.0, 222.0)
        assert player.score_bonus == 42

    def test_save_file_written_to_saves_dir(self, tmp_path):
        from runtime.game_runner import GameRunner

        proj_dir = _write_project(tmp_path)
        runner = GameRunner(str(proj_dir / "project.json"))

        def do_save():
            runner.action_executor.execute_save_game_action(
                _player(runner), {"filename": "slot1.sav"})

        _run_with_frame_actions(runner, {2: do_save}, max_frames=3)

        save_file = proj_dir / "saves" / "slot1.sav"
        assert save_file.exists()
        data = json.loads(save_file.read_text(encoding="utf-8"))
        assert data["current_room"] == "room_a"
        assert data["instances"][0]["object_name"] == "obj_player"


class TestSaveLoadCrossRoom:
    """The previously-dead path: the saved room differs from the current
    room. instance._load_room_name/_load_instances were set but never
    consumed anywhere in game_runner.py -- confirmed by grep before fixing."""

    def test_load_switches_room_and_restores_instances(self, tmp_path):
        from runtime.game_runner import GameRunner

        proj_dir = _write_project(tmp_path)
        runner = GameRunner(str(proj_dir / "project.json"))

        def save_in_room_a():
            assert runner.current_room.name == "room_a"
            player = _player(runner)
            player.x, player.y = 77.0, 88.0
            runner.action_executor.execute_save_game_action(
                player, {"filename": "cross.sav"})

        def go_to_room_b():
            runner.change_room("room_b")

        def load_from_room_b():
            assert runner.current_room.name == "room_b"
            player = _player(runner)
            runner.action_executor.execute_load_game_action(
                player, {"filename": "cross.sav"})

        result = _run_with_frame_actions(
            runner,
            {2: save_in_room_a, 3: go_to_room_b, 5: load_from_room_b},
            max_frames=8,
        )

        assert result is not False, "game loop reported a fatal crash"
        assert runner.current_room.name == "room_a", (
            "load_game must switch back to the saved room, not just log it")
        player = _player(runner)
        assert (player.x, player.y) == (77.0, 88.0)

    def test_load_nonexistent_room_does_not_crash(self, tmp_path):
        from runtime.game_runner import GameRunner

        proj_dir = _write_project(tmp_path)
        runner = GameRunner(str(proj_dir / "project.json"))
        saves_dir = proj_dir / "saves"
        saves_dir.mkdir()
        (saves_dir / "bad.sav").write_text(
            json.dumps({"current_room": "no_such_room", "score": 0,
                       "lives": 3, "health": 100, "global_variables": {},
                       "instances": []}),
            encoding="utf-8")

        def load_bad():
            runner.action_executor.execute_load_game_action(
                _player(runner), {"filename": "bad.sav"})

        result = _run_with_frame_actions(runner, {2: load_bad}, max_frames=4)
        assert result is not False


class TestSaveLoadGlobalState:
    def test_score_lives_health_and_globals_round_trip(self, tmp_path):
        from runtime.game_runner import GameRunner

        proj_dir = _write_project(tmp_path)
        runner = GameRunner(str(proj_dir / "project.json"))

        def do_save():
            runner.score = 500
            runner.lives = 7
            runner.health = 33
            runner.global_variables["flag_seen"] = True
            runner.action_executor.execute_save_game_action(
                _player(runner), {"filename": "globals.sav"})

        def mess_up_then_load():
            runner.score = 0
            runner.lives = 1
            runner.health = 1
            runner.global_variables.clear()
            runner.action_executor.execute_load_game_action(
                _player(runner), {"filename": "globals.sav"})

        _run_with_frame_actions(
            runner, {2: do_save, 4: mess_up_then_load}, max_frames=6)

        assert runner.score == 500
        assert runner.lives == 7
        assert runner.health == 33
        assert runner.global_variables.get("flag_seen") is True
