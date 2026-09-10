#!/usr/bin/env python3
"""FileSession -- ties the shared-folder transport (fileio.py) to one
running game, without importing pygame or GameRunner. Named and shaped to
read as the file-exchange sibling of extensions/multiplayer_lan/
session.py's NetworkSession, but the underlying model is a genuinely
different thing: host-authoritative ROUNDS over a shared folder, not a
persistent connection polled every frame -- see
docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md's "Why this is a real option, and
why it's a different thing from multiplayer_lan".

Deliberately GameRunner-agnostic: exposes ``shared`` and a queue of
``(event_name, *payload)`` tuples via ``take_events()``; handlers.py is
what mirrors those into game_runner.global_variables and fires events on
the room's instances. That keeps this file testable against two real
FileSession instances pointed at the same real
``tempfile.TemporaryDirectory()``, no mocking, no engine at all -- the
plan's own Phase 1 testing note.

Round model (host-authoritative lockstep, the plan's "Design decision"):
each round, every player currently in the roster submits exactly one
move file (``end_turn()``), containing whatever they staged via
``set_shared(name, value)`` / ``send_message(event, data, target)``
since the round began. The host polls, resolves the round once it has a
move from everyone currently in the roster (or ``round_deadline``
seconds pass, whichever comes first), folds every move's vars into
``shared`` -- host's own pending vars first, then each client's in
ascending slot order, so the LAST write for a given name wins (the
plan's own "no merge engine, just last write wins per named var"
out-of-scope note) -- and publishes an incremented ``session.json``,
including every ``target="all"`` message from the round so every
machine fires ``network_message_files`` once it picks up the update (a
``target="host"`` message is delivered by being processed locally on
the host only, during the same resolve -- never published, since no one
else is meant to see it). A player who missed the deadline is reported
as skipped, never as blocking the round forever -- including a player
who joins mid-round and hasn't had a chance to move yet: they are simply
skipped that one round (a generous ``round_deadline`` is the author's
lever for how much grace a fresh joiner gets) and participate normally
from the next round on.
"""

import time
import uuid
from pathlib import Path

from core.logger import get_logger
from . import fileio
from .state import (
    CONSECUTIVE_FAILURES_BEFORE_LOST, DEFAULT_MAX_PLAYERS,
    DEFAULT_ROUND_DEADLINE, MAX_STR_LEN, MIN_ROUND_DEADLINE, POLL_INTERVAL,
    SESSION_FILE, is_valid_shared_name, join_file_name, leave_file_name,
    move_file_name, sanitize_name, sanitize_value, welcome_file_name,
)

logger = get_logger(__name__)

_MAX_PLAYERS_CEIL = 16


class FileSession:
    """One machine's view of a file-exchange game. ``mode`` is ``"host"``
    or ``"client"``. Call ``start()`` once, then ``pump_before_step()`` /
    ``pump_after_update()`` from the two frame-update hooks (the actual
    disk I/O inside them is gated to once every ``state.POLL_INTERVAL``
    seconds, not every frame), and drain ``take_events()`` after each
    before-step pump."""

    def __init__(self, *, mode: str, folder, player_name: str = "Joueur",
                 max_players: int = DEFAULT_MAX_PLAYERS,
                 round_deadline: float = DEFAULT_ROUND_DEADLINE):
        if mode not in ("host", "client"):
            raise ValueError(f"mode must be 'host' or 'client', not {mode!r}")
        self.mode = mode
        self.folder = Path(folder)
        self.player_name = sanitize_name(player_name)
        self.max_players = max(2, min(_MAX_PLAYERS_CEIL, int(max_players)))
        self.round_deadline = max(MIN_ROUND_DEADLINE, float(round_deadline))

        self.player_id = 0 if mode == "host" else -1
        self.player_count = 1 if mode == "host" else 0
        self.round = 1
        self.shared = {}
        self.connection_lost = False
        self._has_synced = False       # session.json read/published at least once

        self.client_id = uuid.uuid4().hex[:16]
        self._join_written = False

        # host-only roster bookkeeping: slot -> {"name": str}. Everyone
        # currently in the roster is expected to move every round -- a
        # player who just joined mid-round and hasn't seen the board yet
        # either still makes it in before the deadline (a generous
        # round_deadline is the author's lever for that) or is reported
        # skipped for that one round and participates normally from the
        # next round on. No separate "not yet expected" bookkeeping is
        # needed on top of that -- see docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md.
        self._roster = {}
        self._next_slot = 1
        self._seen_joins = set()       # join_<id> client ids already welcomed
        self._seen_leaves = set()      # left_<id> client ids already processed

        # this round's collected moves (host): slot -> vars dict
        self._round_moves = {}
        self._round_started_at = time.monotonic()

        # staged writes not yet submitted this round (both host and client)
        self._pending_vars = {}
        self._pending_messages = []      # [{"event", "data", "target"}, ...]
        self._move_submitted_round = 0   # client: last round a move file was written for

        self._events = []
        self._last_poll = 0.0
        self._consecutive_failures = 0

    # -- lifecycle ------------------------------------------------------

    def start(self) -> bool:
        """Create (host) or just record (client) the shared folder. Never
        raises -- a folder that can't be created/reached degrades to a
        failed start the caller reports, matching every other
        never-raises operation in this module."""
        if self.mode == "host":
            if not fileio.ensure_folder(self.folder):
                return False
            self._publish_session()
            return self._has_synced
        return True

    def close(self) -> None:
        pass  # nothing to release -- no open handle, no socket, no thread

    # -- author-facing operations ----------------------------------

    def is_host(self) -> bool:
        return self.mode == "host"

    @property
    def turn_ready(self) -> bool:
        """True once this machine has read (client) or published (host)
        at least one session.json -- the point at which
        global.round_number and every shared var reflect real, published
        state rather than just this machine's own local defaults."""
        return self._has_synced

    @property
    def waiting_for_players(self) -> bool:
        return self.player_count < self.max_players

    @property
    def roster(self) -> list:
        """Host: ``[(slot, name), ...]`` including the host itself (slot
        0) -- mirrors multiplayer_lan's own NetworkSession.roster, so
        connect_screen.py's host-mode lobby display can be driven the
        same way on both extensions."""
        out = [(0, self.player_name)]
        out.extend((slot, info["name"]) for slot, info in sorted(self._roster.items()))
        return out

    def set_shared(self, name: str, value) -> None:
        if not is_valid_shared_name(name):
            logger.warning(
                "multiplayer_files: ignoring invalid shared-var name %r", name)
            return
        self._pending_vars[name] = sanitize_value(value)

    def get_shared(self, name: str, default=None):
        return self.shared.get(name, default)

    def send_message(self, event: str, data=None, target: str = "all") -> None:
        """Stage a custom message, delivered the same way a shared-var
        write is: folded in at the next round boundary, not instantly --
        there's no live connection to deliver it over immediately.
        ``target="host"`` is processed locally on the host only during
        that resolve and never published; ``target="all"`` (the default)
        reaches every machine via the round's published session.json."""
        target = target if target in ("all", "host") else "all"
        self._pending_messages.append({
            "event": str(event)[:MAX_STR_LEN],
            "data": sanitize_value(data),
            "target": target,
        })

    def end_turn(self) -> None:
        """Submit this round's move: whatever was staged via
        ``set_shared``/``send_message`` since the last call, as one file
        (client) or folded straight into the host's own pending state
        (host -- it never needs to write and then re-read its own move,
        since it is already the authority). Calling it again with
        nothing new staged this round is a harmless no-op."""
        if self.mode == "host":
            self._round_moves[0] = {
                "vars": dict(self._pending_vars),
                "messages": list(self._pending_messages),
            }
            self._pending_vars = {}
            self._pending_messages = []
            return
        if self.player_id < 0 or self._move_submitted_round == self.round:
            return
        path = self.folder / move_file_name(self.player_id, self.round)
        payload = {
            "vars": dict(self._pending_vars),
            "messages": list(self._pending_messages),
        }
        if fileio.atomic_write_json(path, payload):
            self._move_submitted_round = self.round
            self._pending_vars = {}
            self._pending_messages = []

    def leave(self) -> None:
        """Client: leave a mark the host will notice and drop from the
        roster. Matches the one-writer-per-file rule -- even leaving
        writes only this client's own file, never anyone else's. A host
        calling this is a no-op; hosting simply stops (handlers.py's
        teardown discards the session object)."""
        if self.mode == "client" and self.player_id >= 0:
            fileio.atomic_write_json(
                self.folder / leave_file_name(self.client_id),
                {"player_id": self.player_id})

    def take_events(self) -> list:
        evs = self._events
        self._events = []
        return evs

    # -- frame pumps -----------------------------------------------

    def pump_before_step(self) -> None:
        now = time.monotonic()
        if now - self._last_poll < POLL_INTERVAL:
            return
        self._last_poll = now
        if self.mode == "host":
            self._host_poll()
        else:
            self._client_poll()

    def pump_after_update(self) -> None:
        # Every write already happens inline in the poll methods / in
        # end_turn -- there is no outbound buffer to flush the way a
        # socket connection needs one.
        pass

    # -- host internals -----------------------------------------------

    def _host_poll(self) -> None:
        ok_joins, joins_changed = self._accept_joins()
        ok_leaves, leaves_changed = self._accept_leaves()
        self._collect_moves()
        self._note_result(ok_joins and ok_leaves)
        if joins_changed or leaves_changed:
            # A join/leave changes player_count/roster/waiting_for_players
            # -- publish right away rather than waiting for the next round
            # to resolve. Without this, a client's own view of
            # player_count stays stuck at whatever session.json said at
            # the last publish (its own welcome, at the latest), which
            # can never self-correct if gameplay itself is gated on
            # global.waiting_for_players reaching 0 -- an author who
            # (reasonably) waits for that before letting anyone move
            # would deadlock forever, since the round that would have
            # refreshed it never gets permission to start. Found via
            # testing the bundled fichier_1 sample end to end, not code
            # review.
            self._publish_session(skipped=[], messages=[])
        self._maybe_resolve_round()

    def _accept_joins(self):
        """Returns (ok, changed): ok is False if the folder couldn't be
        listed; changed is True if at least one new player was welcomed
        this poll."""
        names = fileio.list_files(self.folder, "join_")
        if names is None:
            return False, False
        changed = False
        for name in names:
            client_id = name[len("join_"):-len(".json")]
            if client_id in self._seen_joins:
                continue
            if len(self._roster) + 1 >= self.max_players:
                # Game full -- try again next poll. Deliberately NOT
                # added to _seen_joins, so a later leave freeing a slot
                # lets this same join request through with no extra
                # action needed from the waiting client.
                continue
            data = fileio.read_json(self.folder / name)
            if data is None:
                continue          # not fully written yet -- try again next poll
            self._seen_joins.add(client_id)
            slot = self._next_slot
            self._next_slot += 1
            player_name = sanitize_name(data.get("name"))
            self._roster[slot] = {"name": player_name}
            self.player_count = 1 + len(self._roster)
            fileio.atomic_write_json(
                self.folder / welcome_file_name(client_id),
                {"player_id": slot, "round": self.round})
            self._queue_event("player_joined_files", slot, player_name)
            changed = True
        return True, changed

    def _accept_leaves(self):
        """Returns (ok, changed) -- see _accept_joins."""
        names = fileio.list_files(self.folder, "left_")
        if names is None:
            return False, False
        changed = False
        for name in names:
            client_id = name[len("left_"):-len(".json")]
            if client_id in self._seen_leaves:
                continue
            data = fileio.read_json(self.folder / name)
            if data is None:
                continue
            self._seen_leaves.add(client_id)
            slot = data.get("player_id")
            if isinstance(slot, int) and slot in self._roster:
                self._roster.pop(slot, None)
                self._round_moves.pop(slot, None)
                self.player_count = 1 + len(self._roster)
                changed = True
        return True, changed

    def _collect_moves(self) -> None:
        for slot in self._roster:
            if slot in self._round_moves:
                continue
            data = fileio.read_json(self.folder / move_file_name(slot, self.round))
            if data is None:
                continue
            vars_ = data.get("vars")
            messages_ = data.get("messages")
            self._round_moves[slot] = {
                "vars": vars_ if isinstance(vars_, dict) else {},
                "messages": messages_ if isinstance(messages_, list) else [],
            }

    def _maybe_resolve_round(self) -> None:
        expected = set(self._roster.keys())
        have_all = expected.issubset(self._round_moves.keys())
        host_ready = 0 in self._round_moves
        deadline_hit = (
            time.monotonic() - self._round_started_at >= self.round_deadline)
        if (have_all and host_ready) or deadline_hit:
            self._resolve_round(expected)

    def _resolve_round(self, expected) -> None:
        skipped = sorted(expected - self._round_moves.keys())

        merged = dict(self._round_moves.get(0, {}).get("vars", {}))
        for slot in sorted(s for s in self._round_moves if s != 0):
            merged.update(self._round_moves[slot].get("vars", {}))
        changed = {k: v for k, v in merged.items() if self.shared.get(k) != v}
        self.shared.update(changed)

        published_messages = []
        move_slots = [0] + sorted(s for s in self._round_moves if s != 0)
        for slot in move_slots:
            row = self._round_moves.get(slot)
            if not row:
                continue
            for msg in row.get("messages") or ():
                if not isinstance(msg, dict):
                    continue
                event = msg.get("event")
                if not isinstance(event, str) or not event:
                    continue
                data = sanitize_value(msg.get("data"))
                target = msg.get("target") if msg.get("target") in ("all", "host") else "all"
                # The host fires every message locally regardless of
                # target -- for target="all" this is the same event
                # every OTHER machine gets once it picks up the
                # published round; for target="host" this IS the
                # delivery, since it's never published at all.
                self._queue_event("network_message_files", event, data, slot)
                if target == "all":
                    published_messages.append(
                        {"event": event, "data": data, "sender": slot})

        self.round += 1
        self._round_moves = {}
        self._round_started_at = time.monotonic()

        self._publish_session(skipped=skipped, messages=published_messages)
        self._queue_event("round_resolved")
        for slot in skipped:
            self._queue_event("player_skipped_round", slot)

    def _publish_session(self, skipped=None, messages=None) -> None:
        payload = {
            "round": self.round,
            "shared": self.shared,
            "roster": [list(entry) for entry in self.roster],
            "player_count": self.player_count,
            "max_players": self.max_players,
            "skipped": list(skipped or []),
            "messages": list(messages or []),
        }
        ok = fileio.atomic_write_json(self.folder / SESSION_FILE, payload)
        self._note_result(ok)
        if ok:
            self._has_synced = True

    # -- client internals -----------------------------------------

    def _client_poll(self) -> None:
        if self.player_id < 0:
            self._await_welcome()
            return
        self._read_session()

    def _await_welcome(self) -> None:
        if not self._join_written:
            ok = fileio.atomic_write_json(
                self.folder / join_file_name(self.client_id),
                {"name": self.player_name})
            self._join_written = ok
            self._note_result(ok)
            if not ok:
                return
        data = fileio.read_json(self.folder / welcome_file_name(self.client_id))
        if data is None:
            return
        slot = data.get("player_id")
        if not isinstance(slot, int):
            return
        self.player_id = slot
        rnd = data.get("round")
        if isinstance(rnd, int):
            self.round = rnd
        self._queue_event("file_session_started")

    def _read_session(self) -> None:
        data = fileio.read_json(self.folder / SESSION_FILE)
        if data is None:
            self._note_result(False)
            return
        self._note_result(True)
        self._has_synced = True

        shared = data.get("shared")
        if isinstance(shared, dict):
            self.shared = shared
        try:
            self.player_count = int(data.get("player_count", self.player_count))
            self.max_players = int(data.get("max_players", self.max_players))
        except (TypeError, ValueError):
            pass

        new_round = data.get("round")
        if isinstance(new_round, int) and new_round > self.round:
            self.round = new_round
            self._pending_vars = {}      # last round's stale staged vars
            self._pending_messages = []  # last round's stale staged messages
            self._queue_event("round_resolved")
            for slot in data.get("skipped") or ():
                if isinstance(slot, int):
                    self._queue_event("player_skipped_round", slot)
            for msg in data.get("messages") or ():
                if not isinstance(msg, dict):
                    continue
                event = msg.get("event")
                if not isinstance(event, str) or not event:
                    continue
                self._queue_event(
                    "network_message_files", event, msg.get("data"), msg.get("sender", -1))

    # -- internals ---------------------------------------------------

    def _queue_event(self, name: str, *payload) -> None:
        self._events.append((name, *payload))

    def _note_result(self, ok: bool) -> None:
        if ok:
            self._consecutive_failures = 0
            return
        self._consecutive_failures += 1
        if (self._consecutive_failures >= CONSECUTIVE_FAILURES_BEFORE_LOST
                and not self.connection_lost):
            self.connection_lost = True
            logger.warning(
                "multiplayer_files: shared folder unreachable, "
                "flagging file_session_lost")
            self._queue_event("file_session_lost")
