"""File-exchange multiplayer -- FileSession loopback tests (Phase 1).

docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md Phase 1:
extensions/multiplayer_files/session.py. Real files against a real
tempfile.TemporaryDirectory(), no mocking, no sockets -- the session is
GameRunner-agnostic, so it can be driven directly here (the engine glue
is tested separately in test_multiplayer_files_tier_a.py). Matches the
plan's own Phase 1 testing note: "this is easier to test solidly than
sockets ever were".
"""
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.multiplayer_files import fileio  # noqa: E402
from extensions.multiplayer_files.session import FileSession  # noqa: E402
from extensions.multiplayer_files.state import is_valid_shared_name  # noqa: E402


def _pump(*sessions):
    """Force each session's internal POLL_INTERVAL gate open and pump
    once. Tests drive many pumps in a tight loop rather than sleeping a
    real second between each -- the gate itself is covered separately
    (TestPollGating)."""
    for s in sessions:
        s._last_poll = 0.0
        s.pump_before_step()
        s.pump_after_update()


class _EventLog:
    def __init__(self, session):
        self.session = session
        self.events = []

    def collect(self):
        self.events.extend(self.session.take_events())
        return self.events

    def names(self):
        return [e[0] for e in self.events]

    def find(self, name):
        return [e for e in self.events if e[0] == name]


def _joined_pair(tmp, **client_kw):
    host = FileSession(mode="host", folder=tmp, player_name="Prof",
                        round_deadline=100)
    assert host.start()
    client_kw.setdefault("player_name", "Ada")
    client = FileSession(mode="client", folder=tmp, **client_kw)
    assert client.start()
    hlog, clog = _EventLog(host), _EventLog(client)
    for _ in range(10):
        _pump(client, host, client)
        hlog.collect(); clog.collect()
        if client.player_id >= 0:
            break
    return host, client, hlog, clog


class TestJoinHandshake:
    def test_client_gets_a_slot_and_file_session_started(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client, hlog, clog = _joined_pair(tmp)
            assert client.player_id == 1
            assert host.player_count == 2
            assert client.player_count == 0  # not yet refreshed by a session.json read
            assert "file_session_started" in clog.names()
            assert hlog.find("player_joined_files") == [("player_joined_files", 1, "Ada")]

    def test_two_clients_get_distinct_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, c1, _, l1 = _joined_pair(tmp, player_name="Ada")
            c2 = FileSession(mode="client", folder=tmp, player_name="Bo")
            assert c2.start()
            l2 = _EventLog(c2)
            for _ in range(10):
                _pump(c2, host, c2)
                l2.collect()
                if c2.player_id >= 0:
                    break
            assert {c1.player_id, c2.player_id} == {1, 2}
            assert host.player_count == 3

    def test_game_full_leaves_extra_join_waiting_then_admits_once_a_slot_frees(self):
        with tempfile.TemporaryDirectory() as tmp:
            host = FileSession(mode="host", folder=tmp, max_players=2, round_deadline=100)
            assert host.start()
            c1 = FileSession(mode="client", folder=tmp, player_name="Ada")
            assert c1.start()
            for _ in range(10):
                _pump(c1, host, c1)
                if c1.player_id >= 0:
                    break
            assert c1.player_id == 1  # host(1) + c1 fills max_players=2

            c2 = FileSession(mode="client", folder=tmp, player_name="Bo")
            assert c2.start()
            for _ in range(5):
                _pump(c2, host, c2)
            assert c2.player_id == -1     # game full -- left waiting, not crashed

            c1.leave()
            for _ in range(10):
                _pump(host, c2, host, c2)
                if c2.player_id >= 0:
                    break
            # slot numbers are never recycled (same as multiplayer_lan's own
            # _next_slot) -- c2 is simply admitted once the game is no
            # longer full, with no client-side retry logic of its own
            assert c2.player_id == 2


class TestRoundResolution:
    def test_host_and_client_vars_both_land_in_shared(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client, hlog, clog = _joined_pair(tmp)
            host.set_shared("board_0", "X")
            host.end_turn()
            client.set_shared("note", "hi")
            client.end_turn()
            for _ in range(5):
                _pump(host, client)
                hlog.collect(); clog.collect()
                if client.round == 2:
                    break
            assert host.round == 2
            assert client.shared == {"board_0": "X", "note": "hi"}
            assert "round_resolved" in hlog.names()
            assert "round_resolved" in clog.names()

    def test_round_resolves_as_soon_as_everyone_moves_not_only_on_deadline(self):
        """round_deadline is huge here -- if the round only advanced on
        deadline this test would time out, not just fail slowly."""
        with tempfile.TemporaryDirectory() as tmp:
            host = FileSession(mode="host", folder=tmp, round_deadline=3600)
            assert host.start()
            client = FileSession(mode="client", folder=tmp)
            assert client.start()
            for _ in range(10):
                _pump(client, host, client)
                if client.player_id >= 0:
                    break
            host.end_turn()
            client.end_turn()
            for _ in range(5):
                _pump(host, client)
                if host.round == 2:
                    break
            assert host.round == 2
            assert client.round == 2

    def test_last_write_wins_host_first_then_ascending_slot(self):
        """Both a client and the host stage the SAME var name in one
        round -- the plan's own "no merge engine, last write wins"
        out-of-scope note. Host applies first, so a client's value for
        the same name always wins over the host's own."""
        with tempfile.TemporaryDirectory() as tmp:
            host, client, _, _ = _joined_pair(tmp)
            host.set_shared("turn", "host-value")
            host.end_turn()
            client.set_shared("turn", "client-value")
            client.end_turn()
            for _ in range(5):
                _pump(host, client)
                if host.round == 2:
                    break
            assert host.shared["turn"] == "client-value"

    def test_a_mid_round_joiner_who_never_moves_is_just_skipped_once(self):
        """Everyone currently in the roster is expected to move every
        round -- including someone who just joined. There's no separate
        "not yet expected" bookkeeping (see session.py's own module
        docstring): a fresh joiner who doesn't make it in before the
        deadline is reported skipped for that one round, then
        participates normally starting the next one."""
        with tempfile.TemporaryDirectory() as tmp:
            host = FileSession(mode="host", folder=tmp, round_deadline=0.05)
            assert host.start()
            client = FileSession(mode="client", folder=tmp)
            assert client.start()
            for _ in range(10):
                _pump(client, host, client)
                if client.player_id >= 0:
                    break
            host.set_shared("solo", 1)
            host.end_turn()
            host._round_started_at -= 1000    # force the deadline deterministically
            _pump(host, client)
            assert host.round == 2
            assert host.shared.get("solo") == 1

            # round 2: both move normally from here on
            host.end_turn()
            client.end_turn()
            for _ in range(5):
                _pump(host, client)
                if host.round == 3:
                    break
            assert host.round == 3


class TestDeadlineSkip:
    def test_a_player_who_never_submits_is_skipped_once_the_deadline_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client, hlog, clog = _joined_pair(tmp)
            host.round_deadline = 0.05
            host.set_shared("x", 1)
            host.end_turn()
            # force the deadline deterministically instead of a real sleep
            host._round_started_at -= 1000
            _pump(host)
            hlog.collect()
            assert host.round == 2
            assert ("player_skipped_round", 1) in hlog.events
            _pump(client)
            clog.collect()
            assert ("player_skipped_round", 1) in clog.events

    def test_a_stale_staged_var_is_dropped_after_being_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client, _, _ = _joined_pair(tmp)
            host.round_deadline = 0.05
            client.set_shared("never_sent", "oops")
            host.set_shared("go", 1)
            host.end_turn()
            host._round_started_at -= 1000
            _pump(host, client)
            assert client._pending_vars == {}
            assert "never_sent" not in host.shared


class TestLeave:
    def test_leaving_drops_the_roster_slot_and_player_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            host, client, _, _ = _joined_pair(tmp)
            client.leave()
            _pump(host)
            assert client.player_id not in host._roster
            assert host.player_count == 1

    def test_host_leave_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as tmp:
            host = FileSession(mode="host", folder=tmp)
            assert host.start()
            host.leave()  # must not raise


class TestFileSessionLost:
    def test_unreachable_folder_flags_file_session_lost_after_a_few_failures(self):
        import uuid
        ghost = Path(tempfile.gettempdir()) / ("pygm_ghost_" + uuid.uuid4().hex)
        client = FileSession(mode="client", folder=str(ghost))
        assert client.start()          # never raises -- degrades instead
        log = _EventLog(client)
        for _ in range(6):
            _pump(client)
            log.collect()
            if client.connection_lost:
                break
        assert client.connection_lost
        assert "file_session_lost" in log.names()

    def test_a_single_transient_failure_does_not_flag_lost(self):
        """One bad poll (a file mid-write, a momentary lock) must not
        flap the whole session -- only CONSECUTIVE_FAILURES_BEFORE_LOST
        in a row does."""
        with tempfile.TemporaryDirectory() as tmp:
            client = FileSession(mode="client", folder=tmp)
            assert client.start()
            client._note_result(False)
            client._note_result(True)   # a good poll resets the streak
            client._note_result(False)
            assert not client.connection_lost


class TestSlowFilesystem:
    def test_round_resolution_still_works_with_artificial_read_write_latency(self, monkeypatch):
        """Simulates a real network-drive round trip (the plan's own
        "5-50ms or more" estimate) without the test itself taking
        anywhere near that in wall time to run -- proves the protocol
        doesn't assume instantaneous I/O."""
        real_write = fileio.atomic_write_json
        real_read = fileio.read_json

        def slow_write(path, data):
            time.sleep(0.01)
            return real_write(path, data)

        def slow_read(path):
            time.sleep(0.01)
            return real_read(path)

        monkeypatch.setattr(fileio, "atomic_write_json", slow_write)
        monkeypatch.setattr(fileio, "read_json", slow_read)

        with tempfile.TemporaryDirectory() as tmp:
            host = FileSession(mode="host", folder=tmp, round_deadline=100)
            assert host.start()
            client = FileSession(mode="client", folder=tmp)
            assert client.start()
            for _ in range(15):
                _pump(client, host, client)
                if client.player_id >= 0:
                    break
            assert client.player_id == 1
            host.end_turn()
            client.set_shared("v", 42)
            client.end_turn()
            for _ in range(10):
                _pump(host, client)
                if client.round == 2:
                    break
            assert client.shared.get("v") == 42


class TestPollGating:
    def test_pump_before_step_is_a_no_op_within_the_poll_interval(self):
        """Calling pump_before_step every frame (as the real frame-update
        hook does) must not touch disk 60 times a second -- only once
        per state.POLL_INTERVAL, per the plan's own reasoning against
        hammering a real file server."""
        with tempfile.TemporaryDirectory() as tmp:
            host = FileSession(mode="host", folder=tmp)
            assert host.start()
            host.pump_before_step()          # first call -- polls immediately
            first_poll = host._last_poll
            host.pump_before_step()          # called again right away
            assert host._last_poll == first_poll  # the gate held -- no second poll ran


class TestSharedVarValidation:
    def test_reserved_names_are_rejected(self):
        assert not is_valid_shared_name("is_host")
        assert not is_valid_shared_name("round_number")
        assert not is_valid_shared_name("network_sender")

    def test_an_operator_in_the_name_is_rejected(self):
        """The _parse_value landmine (CLAUDE.md): a shared-var name must
        never be able to reach the expression evaluator."""
        with tempfile.TemporaryDirectory() as tmp:
            host = FileSession(mode="host", folder=tmp)
            assert host.start()
            host.set_shared("a+b", "should be ignored")
            assert host._pending_vars == {}
