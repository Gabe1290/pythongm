"""End-to-end smoke test for the multiplayer_lan_1 sample (Phase 3,
docs/MULTIPLAYER_LAN_PLAN.md), mirroring tests/test_block_world_1_sample.py's
pattern: run the REAL project through the REAL GameRunner loop with
injected keyboard events, not a hand-built room.

TestMultiplayerLan1Smoke covers ordinary single-player play (no
networking at all -- proving the sample works standalone, per its own
README). TestMultiplayerLan1NetworkedSmoke goes further: two REAL
GameRunner instances (one --net-host-equivalent, one --net-client-
equivalent, driven the same way run_game.py's CLI flags would configure
them) talking over a real 127.0.0.1 TCP loopback, proving the shipped
sample project -- not just handlers.py in isolation
(tests/test_multiplayer_lan.py already covers that) -- actually
round-trips a position sync end to end.
"""
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from events.plugin_loader import load_all_plugins  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402
from extensions.multiplayer_lan.state import peek_multiplayer  # noqa: E402

PROJECT_JSON = str(REPO_ROOT / "samples" / "multiplayer_lan_1" / "project.json")


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


class TestMultiplayerLan1Smoke:
    def test_runs_standalone_with_no_networking(self):
        runner = _run_with_keys(pygame.K_RIGHT, 15)
        player = next(i for i in runner.current_room.instances
                      if i.object_name == "obj_player")
        assert player.x > 320   # moved right from its start position
        assert peek_multiplayer(runner.current_room) is None

    def test_movement_is_clamped_to_the_room(self):
        # Hold left long enough to hit the left clamp (x >= 16). The clamp
        # runs in Step, but hspeed is applied to position AFTER Step each
        # frame (per the GameMaker-style event order), so the resting value
        # oscillates one movement-step (speed=5) below the clamp rather than
        # sitting exactly on it -- the real point of this assertion is that
        # it never runs away past that band toward large negative x.
        runner = _run_with_keys(pygame.K_LEFT, 120)
        player = next(i for i in runner.current_room.instances
                      if i.object_name == "obj_player")
        assert 11 <= player.x <= 16

    def test_no_key_held_does_not_crash(self):
        runner = _run_with_keys(pygame.K_F1, 10)   # an unbound key -- no-op
        assert runner.current_room is not None


class TestMultiplayerLan1WelcomeTabAndGuide:
    def test_registered_in_the_welcome_tab(self):
        from widgets.welcome_tab import SAMPLE_PROJECTS
        assert ("samples/multiplayer_lan_1", "LAN Multiplayer — Demo") in SAMPLE_PROJECTS

    def test_guide_is_listed_and_renders(self):
        from PySide6.QtWidgets import QApplication
        QApplication.instance() or QApplication([])
        from widgets.welcome_tab import SampleDocsDialog, SAMPLE_PROJECTS

        dlg = SampleDocsDialog(SAMPLE_PROJECTS, REPO_ROOT)
        labels = dlg.sample_labels()
        assert "LAN Multiplayer — Demo" in labels

        row = labels.index("LAN Multiplayer — Demo")
        dlg._show_row(row)
        text = dlg._viewer.toPlainText()
        assert "net-host" in text
        assert "net-client" in text


def _init_room_without_entering_the_game_loop(runner):
    """The same partial-init sequence GameRunner.test_game() itself uses
    before handing off to run_game_loop() -- loads project data and picks
    the starting room, without entering the blocking real-time loop (which
    would need pygame.time.Clock() coordinated across two concurrent
    threads to drive two runners at once). current_room stays None until
    this runs (set only inside .run()/.test_game()), which is exactly what
    the frame-update hooks need populated."""
    assert runner.load_project_data_only(PROJECT_JSON)
    starting_room = runner.find_starting_room()
    runner.current_room = runner.rooms[starting_room]
    runner._visited_rooms.add(starting_room)


class TestMultiplayerLan1NetworkedSmoke:
    """Two real GameRunner instances over the shipped project, talking
    over a real 127.0.0.1 socket -- the strongest automated proof
    available that --net-host/--net-client actually work end to end on
    this specific sample, short of the manual two-process playtest the
    plan doc flags as out of scope for automation."""

    def test_client_instance_mirrors_the_hosts_moved_position(self):
        from runtime.game_runner import GameRunner
        from runtime import extension_hooks

        host_runner = GameRunner(PROJECT_JSON)
        host_runner.language = "en"
        _init_room_without_entering_the_game_loop(host_runner)

        os.environ["PYGM_NET_MODE"] = "host"
        os.environ["PYGM_NET_PORT"] = "0"
        os.environ.pop("PYGM_NET_HOST_ADDR", None)

        # Drive one before_step tick manually (mirrors what the real game
        # loop's first frame does) so the host starts listening and we can
        # read back the OS-assigned port before the client tries to connect.
        extension_hooks.run_frame_updates(host_runner, "before_step")
        host_state = peek_multiplayer(host_runner.current_room)
        assert host_state is not None and host_state["mode"] == "host"
        port = host_state["host"]._listen_sock.getsockname()[1]

        os.environ["PYGM_NET_MODE"] = "client"
        os.environ["PYGM_NET_HOST_ADDR"] = "127.0.0.1"
        os.environ["PYGM_NET_PORT"] = str(port)
        client_runner = GameRunner(PROJECT_JSON)
        client_runner.language = "en"
        _init_room_without_entering_the_game_loop(client_runner)

        try:
            host_player = next(i for i in host_runner.current_room.instances
                                if i.object_name == "obj_player")
            client_player = next(i for i in client_runner.current_room.instances
                                  if i.object_name == "obj_player")

            host_player.x, host_player.y = 500.0, 100.0

            deadline = time.time() + 3.0
            while time.time() < deadline and client_player.x != 500.0:
                extension_hooks.run_frame_updates(host_runner, "after_update")
                time.sleep(0.02)
                extension_hooks.run_frame_updates(client_runner, "before_step")

            assert client_player.x == 500.0
            assert client_player.y == 100.0
        finally:
            h = peek_multiplayer(host_runner.current_room)
            if h and h.get("host"):
                h["host"].close()
            c = peek_multiplayer(client_runner.current_room)
            if c and c.get("client"):
                c["client"].close()
            for var in ("PYGM_NET_MODE", "PYGM_NET_HOST_ADDR", "PYGM_NET_PORT"):
                os.environ.pop(var, None)
            extension_hooks.clear_frame_updates()
            load_all_plugins(ActionExecutor())  # re-register real hooks for later tests
