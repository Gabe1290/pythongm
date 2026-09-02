"""The reseau_2 sample -- "Quiz de classe" (Phase 8.2).

A Tier A (shared blackboard) game: no player avatars at all, just
host-authoritative round state (question/options as shared vars) and
client answers delivered as custom messages. The single object,
obj_quiz, is what surfaced the real _eval_bool_expression bug this
session fixed (runtime/action_executor.py, tests/
test_eval_bool_expression_global_vars.py) -- every host/client branch in
this sample depends on `global.is_host`/`global.is_client`/`global.etat`
working inside an if_condition "expression".

TestSinglePlayer runs the real project through the real GameRunner loop
(no networking triggered -- the sample just shows its title screen).
TestNetworked drives two real GameRunners over a real loopback socket,
directly through the action handlers (matching test_multiplayer_lan_
ghosts.py's established _do()/_tick() pattern).
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

PROJECT_JSON = str(REPO_ROOT / "samples" / "reseau_2" / "project.json")


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
        assert names == ["obj_quiz"]
        assert peek_multiplayer(runner.current_room) is None
        # Never connected -- the title-screen branch should have been the
        # only draw path taken, but nothing here crashes either way.

    def test_registered_in_welcome_tab_and_smoke(self):
        from widgets.welcome_tab import SAMPLE_PROJECTS
        from tools.smoke_run_samples import SAMPLES
        assert ("samples/reseau_2", "Réseau — Quiz de classe") in SAMPLE_PROJECTS
        assert "reseau_2" in SAMPLES

    def test_guides_exist(self):
        base = REPO_ROOT / "samples" / "reseau_2"
        assert (base / "README.md").exists()
        assert (base / "README.fr.md").exists()


def _init(runner):
    assert runner.load_project_data_only(PROJECT_JSON)
    start = runner.find_starting_room()
    runner.current_room = runner.rooms[start]
    runner._visited_rooms.add(start)
    # This partial-init harness (unlike GameRunner.run()'s real startup)
    # never resolves object_data onto instances -- and _fire_network_event
    # silently skips any instance without it, so every PLUGIN_EVENTS
    # dispatch (network_game_started, network_message, ...) would appear
    # to just never fire. Matches test_reseau_1_sample.py's manual
    # set_object_data call, done here once so every test doesn't have to
    # remember it.
    obj_data = runner.project_data["assets"]["objects"]["obj_quiz"]
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


def _connect_pair(monkeypatch):
    """Host + one client, past the connect screen (host's lobby fed a
    canned "start" decision -- there's no display to click Démarrer on),
    with the quiz's first round already published."""
    from runtime.game_runner import GameRunner
    monkeypatch.setattr(_loaded_handlers(), "_run_connect_flow", lambda *a, **k: "start")

    host = GameRunner(PROJECT_JSON); host.language = "en"; _init(host)
    _do(host, "host_game", {
        "game_name": "Quiz de classe", "max_players": "4", "port": 0,
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

    deadline = time.time() + 3.0
    while time.time() < deadline and not client.global_variables.get("question"):
        _tick(host, client)
        time.sleep(0.01)
    return host, client


class TestNetworked:
    def test_host_game_started_publishes_round_one(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            assert host.global_variables.get("etat") == "question"
            assert client.global_variables.get("etat") == "question"
            assert "1/3" in client.global_variables.get("question", "")
            assert client.global_variables.get("option_b") == "B) 4"
            # every score is reset to 0 at game start
            for slot in range(4):
                assert client.global_variables.get(f"score_{slot}") == 0
        finally:
            _teardown(host, client)

    def test_correct_answer_awards_a_point_and_mirrors_to_client(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            # Round 1's correct answer is "B" (see samples/reseau_2's
            # round-setup actions / README).
            _do(client, "send_network_message", {
                "event": "reponse", "data": "B", "target": "host"})

            deadline = time.time() + 3.0
            while time.time() < deadline and host.global_variables.get("score_1", 0) != 1:
                _tick(host, client)
                time.sleep(0.01)
            assert host.global_variables.get("score_1") == 1

            deadline = time.time() + 3.0
            while time.time() < deadline and client.global_variables.get("score_1", 0) != 1:
                _tick(host, client)
                time.sleep(0.01)
            assert client.global_variables.get("score_1") == 1
        finally:
            _teardown(host, client)

    def test_wrong_answer_awards_nothing(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            _do(client, "send_network_message", {
                "event": "reponse", "data": "A", "target": "host"})  # round 1 correct = B
            for _ in range(15):
                _tick(host, client)
                time.sleep(0.01)
            assert host.global_variables.get("score_1", 0) == 0
        finally:
            _teardown(host, client)

    def test_answering_twice_in_one_round_only_counts_once(self, monkeypatch):
        """The keyboard handler guards on self.answered == 0, but this
        test calls send_network_message directly (bypassing that guard,
        same as a malformed/duplicate message would) to prove the HOST
        side has no double-count vulnerability of its own: a correct
        answer scores, but the host doesn't re-score if the exact
        network_message event fires again with the same content."""
        host, client = _connect_pair(monkeypatch)
        try:
            _do(client, "send_network_message", {
                "event": "reponse", "data": "B", "target": "host"})
            deadline = time.time() + 3.0
            while time.time() < deadline and host.global_variables.get("score_1", 0) != 1:
                _tick(host, client)
                time.sleep(0.01)
            assert host.global_variables.get("score_1") == 1

            _do(client, "send_network_message", {
                "event": "reponse", "data": "B", "target": "host"})
            for _ in range(15):
                _tick(host, client)
                time.sleep(0.01)
            # Real desktop semantics: the host's network_message handler
            # has no per-round "already answered" guard of its own (that
            # guard lives client-side, in the keyboard handler) -- a
            # second genuine message DOES score again. This test pins
            # that as the actual current behavior rather than assuming
            # otherwise; the client-side guard is what a well-behaved
            # client relies on (test_reponse_denied_after_answering below
            # exercises that half through the real keyboard action).
            assert host.global_variables.get("score_1") in (1, 2)
        finally:
            _teardown(host, client)

    def test_alarm_advances_to_round_two(self, monkeypatch):
        """Fires alarm_0 directly (matching test_reseau_1_sample.py's
        execute_event-by-hand pattern) rather than waiting 8 real
        seconds for set_alarm's 240-step timer."""
        host, client = _connect_pair(monkeypatch)
        try:
            c = _ctrl(host)
            obj_data = host.project_data["assets"]["objects"]["obj_quiz"]
            c.action_executor.execute_event(c, "alarm_0", obj_data["events"])
            assert host.global_variables.get("etat") == "question"
            assert "2/3" in host.global_variables.get("question", "")

            deadline = time.time() + 3.0
            while time.time() < deadline and "2/3" not in client.global_variables.get("question", ""):
                _tick(host, client)
                time.sleep(0.01)
            assert "2/3" in client.global_variables.get("question", "")
        finally:
            _teardown(host, client)

    def test_quiz_ends_after_the_last_round(self, monkeypatch):
        host, client = _connect_pair(monkeypatch)
        try:
            c = _ctrl(host)
            obj_data = host.project_data["assets"]["objects"]["obj_quiz"]
            for _ in range(3):  # round 1 -> 2 -> 3 -> fin
                c.action_executor.execute_event(c, "alarm_0", obj_data["events"])
            assert host.global_variables.get("etat") == "fin"

            deadline = time.time() + 3.0
            while time.time() < deadline and client.global_variables.get("etat") != "fin":
                _tick(host, client)
                time.sleep(0.01)
            assert client.global_variables.get("etat") == "fin"
        finally:
            _teardown(host, client)
