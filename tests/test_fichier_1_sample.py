"""The fichier_1 sample -- "File Exchange -- Tic-Tac-Toe".

docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md Phase 2: the bundled, finished
sample for extensions/multiplayer_files/. Two-player Tic-Tac-Toe played
over a shared folder instead of a live connection, joinable straight
from Test Game (H hosts, J joins) the same way reseau_4 is for
multiplayer_lan.

TestSinglePlayer: the real project through the real GameRunner loop (no
networking -- just the H/J menu text).
TestWiring: the H/J -> host_game_files/join_game_files authoring is
actually present, and the round-based turn logic exists.
TestNetworked: two real GameRunner instances driven through their real
action lists (not the full pygame input loop, matching
test_reseau_4_sample.py's own _run_sub/_tick pattern) over a real
tempfile.TemporaryDirectory() shared folder -- a full game played to a
win, and a full game played to a draw. Found two real bugs this way
during development (host not republishing session.json on a bare join,
and only the winning player's own instance ever learning the game
ended) -- both fixed in extensions/multiplayer_files/session.py and the
sample's own win-check design, not worked around here.
"""
import copy
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

from runtime import extension_hooks  # noqa: E402
from extensions.multiplayer_files.state import peek_multiplayer_files  # noqa: E402

PROJECT_JSON = str(REPO_ROOT / "samples" / "fichier_1" / "project.json")
GRID_X0, GRID_Y0, CELL = 170, 90, 100


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
        assert "obj_game" in names
        assert peek_multiplayer_files(runner.current_room) is None

    def test_registered_in_welcome_tab_and_smoke(self):
        from widgets.welcome_tab import SAMPLE_PROJECTS
        from tools.smoke_run_samples import SAMPLES
        assert ("samples/fichier_1", "File Exchange — Tic-Tac-Toe") in SAMPLE_PROJECTS
        assert "fichier_1" in SAMPLES

    def test_guides_exist(self):
        base = REPO_ROOT / "samples" / "fichier_1"
        assert (base / "README.md").exists()
        assert (base / "README.fr.md").exists()

    def test_excluded_from_the_beginner_edition(self):
        from config.editions import EDITIONS
        assert "fichier_1" not in EDITIONS["beginner"]["sample_folders"]


class TestWiring:
    def _events(self):
        import json
        d = json.loads((REPO_ROOT / "samples" / "fichier_1" / "project.json").read_text())
        return d["assets"]["objects"]["obj_game"]["events"]

    def test_h_hosts_and_becomes_x(self):
        acts = self._events()["keyboard_press"]["h"]["actions"]
        blob = repr(acts)
        assert "host_game_files" in blob
        assert "'X'" in blob or '"X"' in blob

    def test_j_joins_via_the_connect_screen(self):
        acts = self._events()["keyboard_press"]["j"]["actions"]
        blob = repr(acts)
        assert "join_game_files" in blob
        assert "'auto'" in blob or '"auto"' in blob

    def test_becomes_o_only_once_actually_welcomed(self):
        """my_mark/connected are set from file_session_started (fires
        once the client is genuinely welcomed), not synchronously right
        after the keypress -- folder="auto" can be cancelled at the
        connect screen, and setting them unconditionally in "j" would
        have left the game thinking it was playing when it wasn't."""
        blob = repr(self._events()["file_session_started"])
        assert "'O'" in blob or '"O"' in blob
        assert "connected" in blob

    def test_step_ends_turn_on_the_non_active_player(self):
        assert "end_turn" in repr(self._events()["step"])

    def test_mouse_click_stages_a_mark_and_ends_turn(self):
        blob = repr(self._events()["mouse_left_press"])
        assert "set_shared_var_files" in blob
        assert "end_turn" in blob

    def test_win_check_covers_both_marks_not_just_my_own(self):
        """The bug found during development: an earlier draft only
        checked "did MY mark win", so a losing player's own instance
        never set won=1 at all."""
        blob = repr(self._events()["step"])
        assert "== 'X'" in blob or '== "X"' in blob
        assert "== 'O'" in blob or '== "O"' in blob


def _init(runner):
    assert runner.load_project_data_only(PROJECT_JSON)
    start = runner.find_starting_room()
    runner.current_room = runner.rooms[start]
    runner._visited_rooms.add(start)


def _ctrl(runner):
    c = next(i for i in runner.current_room.instances if i.object_name == "obj_game")
    if getattr(c, "_cached_object_data", None) is None:
        c.set_object_data(runner.project_data["assets"]["objects"]["obj_game"])
    return c


def _run_sub(inst, event_key, sub_key=None, **override):
    node = inst._cached_object_data["events"][event_key]
    if sub_key is not None:
        node = node[sub_key]
    data = copy.deepcopy(node["actions"])

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


def _run_event(inst, event_key):
    data = inst._cached_object_data["events"][event_key]["actions"]
    inst.action_executor.execute_action_list(inst, data)


def _tick(*runners):
    """Force each runner's FileSession poll gate open before pumping, so
    these tests run in a fraction of a second instead of being bound by
    the real 1-second state.POLL_INTERVAL -- the gate itself is already
    covered at the session level (test_multiplayer_files_session.py's
    own TestPollGating)."""
    for r in runners:
        st = peek_multiplayer_files(r.current_room)
        if st and st.get("session") is not None:
            st["session"]._last_poll = 0.0
        extension_hooks.run_frame_updates(r, "before_step")
    for r in runners:
        extension_hooks.run_frame_updates(r, "after_update")


def _click(inst, col, row):
    inst.mouse_x = GRID_X0 + col * CELL + CELL // 2
    inst.mouse_y = GRID_Y0 + row * CELL + CELL // 2
    _run_event(inst, "mouse_left_press")


def _connect(tmp, timeout=8.0):
    from runtime.game_runner import GameRunner

    host = GameRunner(PROJECT_JSON); host.language = "en"
    host.show_message_dialog = lambda *a, **k: None
    _init(host)
    hc = _ctrl(host)
    _run_sub(hc, "create")
    _run_sub(hc, "keyboard_press", "h", folder=tmp)

    client = GameRunner(PROJECT_JSON); client.language = "en"
    client.show_message_dialog = lambda *a, **k: None
    _init(client)
    cc = _ctrl(client)
    _run_sub(cc, "create")
    _run_sub(cc, "keyboard_press", "j", folder=tmp)

    deadline = time.time() + timeout
    while time.time() < deadline and client.global_variables.get("player_id", -1) != 1:
        _tick(host, client)
        time.sleep(0.02)
    assert client.global_variables.get("player_id") == 1, "client never got welcomed"

    deadline = time.time() + timeout
    while time.time() < deadline and (
        host.global_variables.get("waiting_for_players", 1) != 0
        or client.global_variables.get("waiting_for_players", 1) != 0
    ):
        _tick(host, client)
        time.sleep(0.02)
    assert host.global_variables.get("waiting_for_players") == 0
    assert client.global_variables.get("waiting_for_players") == 0, (
        "client's own waiting_for_players never cleared -- the host "
        "must republish session.json as soon as a player joins, not "
        "only when a round resolves")

    return host, hc, client, cc


def _play_move(host, hc, client, cc, who, col, row, timeout=8.0):
    inst = hc if who == "host" else cc
    deadline = time.time() + timeout
    while True:
        _run_event(hc, "step")
        _run_event(cc, "step")
        _tick(host, client)
        if inst.my_turn == 1 or inst.won == 1:
            break
        if time.time() > deadline:
            raise AssertionError(f"never became {who}'s turn for ({col},{row})")
        time.sleep(0.02)
    if inst.won == 1:
        return True  # game already ended (a win/draw was reached earlier)
    _click(inst, col, row)
    target_round = host.global_variables.get("round_number", 1) + 1
    deadline = time.time() + timeout
    while (host.global_variables.get("round_number", 0) < target_round or
           client.global_variables.get("round_number", 0) < target_round):
        _tick(host, client)
        time.sleep(0.02)
        if time.time() > deadline:
            raise AssertionError("round did not resolve")
    return False


class TestNetworked:
    def test_join_and_waiting_for_players_settle_on_both_sides(self, tmp_path):
        host, hc, client, cc = _connect(str(tmp_path))
        assert hc.my_mark == "X"
        assert cc.my_mark == "O"
        assert host.global_variables.get("player_count") == 2

    def test_x_wins_the_top_row_and_both_sides_learn_it(self, tmp_path):
        host, hc, client, cc = _connect(str(tmp_path))
        # X: (0,0) (1,0) (2,0) -- top row. O: (0,1) (1,1) -- anywhere else.
        moves = [("host", 0, 0), ("client", 0, 1), ("host", 1, 0),
                 ("client", 1, 1), ("host", 2, 0)]
        for who, c, r in moves:
            _play_move(host, hc, client, cc, who, c, r)
        _run_event(hc, "step")
        _run_event(cc, "step")
        assert hc.won == 1, "the winner's own instance must know it won"
        assert cc.won == 1, "the LOSER's own instance must also know the game ended"
        board = {k: v for k, v in host.global_variables.items() if k.startswith("cell_")}
        assert board["cell_0_0"] == board["cell_1_0"] == board["cell_2_0"] == "X"
        assert board == {k: v for k, v in client.global_variables.items()
                          if k.startswith("cell_")}, "both machines must agree on the board"

    def test_a_full_board_with_no_line_is_a_draw(self, tmp_path):
        host, hc, client, cc = _connect(str(tmp_path))
        # X O X / X O O / O X X -- full board, no line anywhere.
        plan = [("host", 0, 0), ("client", 1, 0), ("host", 2, 0), ("client", 1, 1),
                ("host", 0, 1), ("client", 0, 2), ("host", 2, 2), ("client", 2, 1),
                ("host", 1, 2)]
        for who, c, r in plan:
            ended = _play_move(host, hc, client, cc, who, c, r)
            if ended:
                break
        _run_event(hc, "step")
        _run_event(cc, "step")
        assert hc.won == 1 and cc.won == 1
        board = {k: v for k, v in host.global_variables.items() if k.startswith("cell_")}
        assert all(v != 0 for v in board.values()), "board should be completely full"

    def test_a_click_out_of_turn_is_ignored(self, tmp_path):
        host, hc, client, cc = _connect(str(tmp_path))
        # Round 1 is X's turn -- a client click must not place a mark.
        _run_event(hc, "step")
        _run_event(cc, "step")
        assert cc.my_turn == 0
        _click(cc, 1, 1)
        assert host.global_variables.get("cell_1_1", 0) == 0
        assert client.global_variables.get("cell_1_1", 0) == 0
