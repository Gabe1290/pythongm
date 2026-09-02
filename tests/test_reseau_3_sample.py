"""The reseau_3 sample -- "Recolte en equipe" (Phase 8.2).

A Tier B networked-instances game built on reseau_1's avatar pattern:
the host spawns owned player avatars (network_spawn), a host-simulated
patrolling monster, and 5 host-authoritative gems. Every gameplay-
affecting action (gem pickup, monster contact) is guarded by
global.is_host == 1 -- the same real _eval_bool_expression fix
(36311d0) reseau_2 needed.

TestSinglePlayer runs the real project through the real GameRunner loop
(no networking triggered). TestNetworked drives two real GameRunners
over a real loopback socket via host_game/join_game, matching
test_reseau_2_sample.py's established _do()/_tick()/_connect_pair
pattern, plus direct execute_collision_event calls (matching this
runtime's own established "fire it directly rather than waiting for
physical overlap" test convention) to exercise the gem/monster
collision handlers deterministically.
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
import extensions.multiplayer_lan.handlers as mp_handlers  # noqa: E402

PROJECT_JSON = str(REPO_ROOT / "samples" / "reseau_3" / "project.json")


def _loaded_handlers():
    import sys as _sys
    for func, _phase in extension_hooks.get_frame_updates():
        if getattr(func, "__name__", "") == "_frame_update_broadcast":
            return _sys.modules[func.__module__]
    return mp_handlers


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
        assert names == ["obj_ctrl"]           # nothing network_spawn'd -- no session
        assert peek_multiplayer(runner.current_room) is None

    def test_registered_in_welcome_tab_and_smoke(self):
        from widgets.welcome_tab import SAMPLE_PROJECTS
        from tools.smoke_run_samples import SAMPLES
        assert ("samples/reseau_3", "Réseau — Récolte en équipe") in SAMPLE_PROJECTS
        assert "reseau_3" in SAMPLES

    def test_guides_exist(self):
        base = REPO_ROOT / "samples" / "reseau_3"
        assert (base / "README.md").exists()
        assert (base / "README.fr.md").exists()


def _init(runner):
    assert runner.load_project_data_only(PROJECT_JSON)
    start = runner.find_starting_room()
    runner.current_room = runner.rooms[start]
    runner._visited_rooms.add(start)
    # _fire_network_event (player_joined etc.) silently skips any instance
    # without object_data -- this partial-init harness never resolves it
    # the way GameRunner.run()'s real startup does.
    obj_data = runner.project_data["assets"]["objects"]["obj_ctrl"]
    for inst in runner.current_room.instances:
        inst.set_object_data(obj_data)


def _ctrl(runner):
    inst = runner.current_room.instances[0]
    inst.action_executor = runner.action_executor
    return inst


def _do(runner, name, params):
    inst = _ctrl(runner)
    return runner.action_executor.action_handlers[name](inst, params)


def _tick(*runners):
    for r in runners:
        extension_hooks.run_frame_updates(r, "before_step")
    for r in runners:
        extension_hooks.run_frame_updates(r, "after_update")


def _teardown(*runners):
    for r in runners:
        try:
            _do(r, "leave_game", {})
        except Exception:
            st = peek_multiplayer(r.current_room)
            if st and st.get("session"):
                st["session"].close()
    extension_hooks.clear_frame_updates()
    load_all_plugins(ActionExecutor())


def _by_object(runner, object_name):
    return [i for i in runner.current_room.instances if i.object_name == object_name]


def _connect_pair(monkeypatch):
    from runtime.game_runner import GameRunner
    monkeypatch.setattr(_loaded_handlers(), "_run_connect_flow", lambda *a, **k: "start")

    host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
    _do(host, "host_game", {
        "game_name": "Récolte en équipe", "max_players": "4", "port": 0,
        "show_lobby": True,
    })
    port = peek_multiplayer(host.current_room)["session"].bound_port

    client = GameRunner(PROJECT_JSON); client.language = "en"; _init(client)
    _do(client, "join_game", {"host": "127.0.0.1", "port": port})

    deadline = time.time() + 3.0
    while time.time() < deadline and client.global_variables.get("player_id", -1) != 1:
        _tick(host, client)
        time.sleep(0.01)
    assert client.global_variables.get("player_id") == 1

    # Wait for the host to have spawned everything (avatar + monster + 5
    # gems) -- host_game's own then_actions run inline, synchronously,
    # the moment "h" is pressed, so this should already be true by the
    # time join completes, but the client's ghost materialisation is
    # still snapshot-driven and needs real ticks.
    deadline = time.time() + 3.0
    while time.time() < deadline and len(_by_object(host, "obj_gem")) < 5:
        _tick(host, client)
        time.sleep(0.01)
    return host, client


class TestNetworked:
    def test_host_spawns_avatar_monster_and_gems(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            # >= 1: the host's own avatar; by the time _connect_pair
            # finishes (waiting for all 5 gems), the client has typically
            # also already joined and gotten its own avatar via
            # player_joined -- test_player_joined_spawns_a_second_avatar
            # below pins that exact count deterministically.
            assert len(_by_object(host, "obj_person")) >= 1
            assert len(_by_object(host, "obj_monster")) == 1
            assert len(_by_object(host, "obj_gem")) == 5
            assert host.global_variables.get("team_score") == 0
        finally:
            _teardown(host, client)

    def test_player_joined_spawns_a_second_avatar(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            deadline = time.time() + 3.0
            while time.time() < deadline and len(_by_object(host, "obj_person")) < 2:
                _tick(host, client)
                time.sleep(0.01)
            avatars = _by_object(host, "obj_person")
            assert len(avatars) == 2
            owners = sorted(getattr(a, "_net_owner", None) for a in avatars)
            assert owners == [0, 1]
        finally:
            _teardown(host, client)

    def test_client_materialises_gem_and_monster_ghosts(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            deadline = time.time() + 3.0
            while time.time() < deadline and (
                    len(_by_object(client, "obj_gem")) < 5
                    or not _by_object(client, "obj_monster")):
                _tick(host, client)
                time.sleep(0.01)
            assert len(_by_object(client, "obj_gem")) == 5
            assert len(_by_object(client, "obj_monster")) == 1
        finally:
            _teardown(host, client)

    def test_gem_collision_awards_team_score_and_destroys_the_gem(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            avatar = _by_object(host, "obj_person")[0]
            gem = _by_object(host, "obj_gem")[0]
            obj_data = host.project_data["assets"]["objects"]["obj_person"]
            avatar.action_executor.execute_collision_event(
                avatar, "collision_with_obj_gem", obj_data["events"], gem)

            assert host.global_variables.get("team_score") == 1
            assert getattr(gem, "to_destroy", False) is True

            deadline = time.time() + 3.0
            while time.time() < deadline and client.global_variables.get("team_score", 0) != 1:
                _tick(host, client)
                time.sleep(0.01)
            assert client.global_variables.get("team_score") == 1
        finally:
            _teardown(host, client)

    def test_monster_collision_docks_a_point_not_below_zero(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            avatar = _by_object(host, "obj_person")[0]
            monster = _by_object(host, "obj_monster")[0]
            obj_data = host.project_data["assets"]["objects"]["obj_person"]

            # Already at 0 -- must clamp, never go negative.
            avatar.action_executor.execute_collision_event(
                avatar, "collision_with_obj_monster", obj_data["events"], monster)
            assert host.global_variables.get("team_score") == 0

            # Score a gem first, then get hit -- should go back to 0, not -1.
            gem = _by_object(host, "obj_gem")[0]
            avatar.action_executor.execute_collision_event(
                avatar, "collision_with_obj_gem", obj_data["events"], gem)
            assert host.global_variables.get("team_score") == 1
            avatar.action_executor.execute_collision_event(
                avatar, "collision_with_obj_monster", obj_data["events"], monster)
            assert host.global_variables.get("team_score") == 0
        finally:
            _teardown(host, client)

    def test_monster_patrol_is_host_simulated_only(self, monkeypatch):
        """The monster's step event is guarded by global.is_host == 1 --
        firing it directly on a CLIENT's ghost copy (which normally never
        even runs step logic, but this pins the guard itself) must not
        move it."""
        host, client = _connect_pair(monkeypatch)
        try:
            deadline = time.time() + 3.0
            while time.time() < deadline and not _by_object(client, "obj_monster"):
                _tick(host, client)
                time.sleep(0.01)
            ghost = _by_object(client, "obj_monster")[0]
            before_x = ghost.x
            obj_data = client.project_data["assets"]["objects"]["obj_monster"]
            ghost.action_executor.execute_event(ghost, "step", obj_data["events"])
            assert ghost.x == before_x
        finally:
            _teardown(host, client)
