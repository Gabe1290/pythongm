"""The reseau_1 sample -- "Salle partagee" (Phase 8.1).

A Tier B shared room: the host spawns one obj_person per player, each
owned by that player; every machine shows every avatar (its own under
local control, the rest as interpolated ghosts).

TestSinglePlayer runs the real project through the real GameRunner loop
(no networking triggered -- the sample just shows its instruction text).
TestNetworked drives two partial-init GameRunners over a real socket via
the PYGM_NET_AUTO* env vars.
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
from runtime import extension_hooks  # noqa: E402
from extensions.multiplayer_lan.state import peek_multiplayer  # noqa: E402

PROJECT_JSON = str(REPO_ROOT / "samples" / "reseau_1" / "project.json")


def _run(frames):
    from runtime.game_runner import GameRunner
    runner = GameRunner(PROJECT_JSON)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    st = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            st["f"] += 1
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
        pygame.init()
        pygame.display.set_mode((1, 1))
    assert result is not False
    return runner


class TestSinglePlayer:
    def test_runs_without_networking(self):
        runner = _run(20)
        names = [i.object_name for i in runner.current_room.instances]
        assert "obj_ctrl" in names
        assert "obj_person" not in names            # network_spawn no-ops with no session
        assert peek_multiplayer(runner.current_room) is None

    def test_registered_in_welcome_tab_and_smoke(self):
        from widgets.welcome_tab import SAMPLE_PROJECTS
        from tools.smoke_run_samples import SAMPLES
        assert ("samples/reseau_1", "Réseau — Salle partagée") in SAMPLE_PROJECTS
        assert "reseau_1" in SAMPLES

    def test_guides_exist(self):
        base = REPO_ROOT / "samples" / "reseau_1"
        assert (base / "README.md").exists()
        assert (base / "README.fr.md").exists()


def _init(runner):
    assert runner.load_project_data_only(PROJECT_JSON)
    start = runner.find_starting_room()
    runner.current_room = runner.rooms[start]
    runner._visited_rooms.add(start)


def _ctrl(runner):
    return next(i for i in runner.current_room.instances if i.object_name == "obj_ctrl")


def _persons(runner):
    return [i for i in runner.current_room.instances if i.object_name == "obj_person"]


def _tick(*runners):
    for r in runners:
        extension_hooks.run_frame_updates(r, "before_step")
    for r in runners:
        extension_hooks.run_frame_updates(r, "after_update")


class TestNetworked:
    def test_host_spawns_owned_avatars_and_client_sees_them(self, monkeypatch):
        from runtime.game_runner import GameRunner
        monkeypatch.setenv("PYGM_NET_AUTOHOST", "1")
        monkeypatch.setenv("PYGM_NET_PORT", "0")
        monkeypatch.delenv("PYGM_NET_AUTOJOIN", raising=False)
        monkeypatch.delenv("PYGM_NET_MODE", raising=False)

        host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
        _tick(host)                                  # env auto-start
        hst = peek_multiplayer(host.current_room)
        assert hst["session"].mode == "host"
        port = hst["session"].bound_port

        # The partial-init harness doesn't run GameRunner.run()'s startup,
        # so instances have no object_data yet -- give the host controller
        # its object data (so the extension can fire player_joined on it)
        # and fire game_start by hand (spawns the host avatar).
        c = _ctrl(host)
        obj_data = host.project_data["assets"]["objects"]["obj_ctrl"]
        c.set_object_data(obj_data)
        c.action_executor.execute_event(c, "game_start", obj_data["events"])
        _tick(host)
        assert len(_persons(host)) == 1
        assert _persons(host)[0]._net_owner == 0

        monkeypatch.delenv("PYGM_NET_AUTOHOST", raising=False)
        monkeypatch.setenv("PYGM_NET_AUTOJOIN", "127.0.0.1")
        monkeypatch.setenv("PYGM_NET_PORT", str(port))
        client = GameRunner(PROJECT_JSON); client.language = "en"; _init(client)

        try:
            deadline = time.time() + 3.0
            while time.time() < deadline and client.global_variables.get("player_id", -1) != 1:
                _tick(host, client); time.sleep(0.02)
            assert client.global_variables["player_id"] == 1

            # the client joining fired player_joined on the host -> a 2nd
            # avatar, owned by slot 1
            deadline = time.time() + 3.0
            while time.time() < deadline and len(_persons(host)) < 2:
                _tick(host, client); time.sleep(0.02)
            owners = sorted(p._net_owner for p in _persons(host))
            assert owners == [0, 1]

            # the client materialises both avatars (its own + a ghost)
            deadline = time.time() + 3.0
            while time.time() < deadline and len(_persons(client)) < 2:
                _tick(host, client); time.sleep(0.02)
            assert len(_persons(client)) == 2
        finally:
            for r in (host, client):
                s = peek_multiplayer(r.current_room)
                if s and s.get("session"):
                    s["session"].close()
                if s and s.get("beacon"):
                    s["beacon"].stop()
            extension_hooks.clear_frame_updates()
            load_all_plugins(ActionExecutor())
