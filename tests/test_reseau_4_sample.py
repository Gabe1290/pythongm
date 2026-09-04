"""The reseau_4 sample -- "Salle partagee - Test Game".

Same shared-room mechanic as reseau_1 (host spawns one owned obj_person
per player; every machine shows every avatar), but joinable straight from
the IDE's Test Game button: obj_ctrl's `h` / `j` keyboard sub-events call
`host_game(show_lobby=true)` / `join_game(host="auto")`, so no
PYGM_NET_AUTO* env vars are needed.

TestSinglePlayer: the real project through the real GameRunner loop (no
networking -- just the H/J menu text).
TestWiring: the H/J -> host_game/join_game authoring is actually present.
TestNetworked: two partial-init GameRunners over a real 127.0.0.1 socket,
driven by executing the `h` / `j` action lists (the client's join is
given an explicit host:port rather than "auto" so the test doesn't depend
on the headless connect-screen default port).
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

PROJECT_JSON = str(REPO_ROOT / "samples" / "reseau_4" / "project.json")


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
        assert "obj_person" not in names           # nothing spawns until a session exists
        assert peek_multiplayer(runner.current_room) is None

    def test_registered_in_welcome_tab_and_smoke(self):
        from widgets.welcome_tab import SAMPLE_PROJECTS
        from tools.smoke_run_samples import SAMPLES
        assert ("samples/reseau_4", "Réseau — Salle partagée (Test Game)") in SAMPLE_PROJECTS
        assert "reseau_4" in SAMPLES

    def test_guides_exist(self):
        base = REPO_ROOT / "samples" / "reseau_4"
        assert (base / "README.md").exists()
        assert (base / "README.fr.md").exists()


class TestWiring:
    def _ctrl_events(self):
        import json
        d = json.loads((REPO_ROOT / "samples" / "reseau_4" / "objects" / "obj_ctrl.json").read_text())
        return d["events"]

    def test_h_hosts_with_a_lobby(self):
        acts = self._ctrl_events()["keyboard"]["h"]["actions"]
        blob = repr(acts)
        assert "host_game" in blob and "'show_lobby': True" in blob

    def test_j_joins_via_the_connect_screen(self):
        acts = self._ctrl_events()["keyboard"]["j"]["actions"]
        blob = repr(acts)
        assert "join_game" in blob and "'host': 'auto'" in blob

    def test_spawn_is_deferred_to_network_game_started(self):
        ev = self._ctrl_events()
        # not game_start (session doesn't exist yet in the menu flow)
        assert "game_start" not in ev
        assert "network_spawn" in repr(ev["network_game_started"])
        assert "network_spawn" in repr(ev["player_joined"])


def _init(runner):
    assert runner.load_project_data_only(PROJECT_JSON)
    start = runner.find_starting_room()
    runner.current_room = runner.rooms[start]
    runner._visited_rooms.add(start)


def _ctrl(runner):
    c = next(i for i in runner.current_room.instances if i.object_name == "obj_ctrl")
    if getattr(c, "_cached_object_data", None) is None:
        c.set_object_data(runner.project_data["assets"]["objects"]["obj_ctrl"])
    return c


def _persons(runner):
    return [i for i in runner.current_room.instances if i.object_name == "obj_person"]


def _run_sub(inst, event_key, sub_key, **override):
    import copy
    data = copy.deepcopy(inst._cached_object_data["events"][event_key][sub_key]["actions"])

    def _walk(actions):
        for a in actions:
            params = a.get("parameters", {})
            for k, v in override.items():
                if k in params:
                    params[k] = v
            _walk(params.get("then_actions") or [])
            _walk(params.get("else_actions") or [])
    if override:
        _walk(data)
    inst.action_executor.execute_action_list(inst, data)


def _tick(*runners):
    for r in runners:
        extension_hooks.run_frame_updates(r, "before_step")
    for r in runners:
        extension_hooks.run_frame_updates(r, "after_update")


class TestNetworked:
    def test_h_hosts_j_joins_and_avatars_mirror(self):
        from runtime.game_runner import GameRunner

        host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
        hc = _ctrl(host)
        # 'h' -> host_game(show_lobby=true); headless connect flow returns
        # "start" immediately, so the session starts and network_game_started
        # is queued.
        _run_sub(hc, "keyboard", "h")
        _tick(host)                                  # drain network_game_started
        hst = peek_multiplayer(host.current_room)
        assert hst and hst["session"].mode == "host"
        assert len(_persons(host)) == 1 and _persons(host)[0]._net_owner == 0
        port = hst["session"].bound_port

        client = GameRunner(PROJECT_JSON); client.language = "en"; _init(client)
        cc = _ctrl(client)
        # drive 'j' with an explicit host:port instead of "auto" so the test
        # doesn't ride on the headless connect-screen default port.
        _run_sub(cc, "keyboard", "j", host="127.0.0.1", port=port)

        try:
            deadline = time.time() + 3.0
            while time.time() < deadline and client.global_variables.get("player_id", -1) != 1:
                _tick(host, client); time.sleep(0.02)
            assert client.global_variables["player_id"] == 1

            deadline = time.time() + 3.0
            while time.time() < deadline and len(_persons(host)) < 2:
                _tick(host, client); time.sleep(0.02)
            assert sorted(p._net_owner for p in _persons(host)) == [0, 1]

            deadline = time.time() + 3.0
            while time.time() < deadline and len(_persons(client)) < 2:
                _tick(host, client); time.sleep(0.02)
            assert len(_persons(client)) == 2

            # client moves its own avatar; host sees the ghost follow
            mine = next(p for p in _persons(client) if getattr(p, "_net_owner", None) == 1)
            mine.x += 40
            for _ in range(30):
                _tick(host, client); time.sleep(0.02)
            ghost = next(p for p in _persons(host) if getattr(p, "_net_owner", None) == 1)
            assert ghost.x > 120        # moved from its spawn x (120 + 1*90 = 210 ... > 120)
        finally:
            for r in (host, client):
                s = peek_multiplayer(r.current_room)
                if s and s.get("session"):
                    s["session"].close()
                if s and s.get("beacon"):
                    s["beacon"].stop()
                if s and s.get("listener"):
                    s["listener"].stop()
            extension_hooks.clear_frame_updates()
            load_all_plugins(ActionExecutor())
