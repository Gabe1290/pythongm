#!/usr/bin/env python3
"""NetworkSession -- ties the transport (network.py) and the snapshot
codec (replication.py) to one running game, without importing pygame or
GameRunner.

docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 5.1. This is the Tier A core: player
identity, a shared-variable blackboard, and custom messages, plus the
lifecycle events an author reacts to. Tier B (networked instances, ghost
creation, owned avatars, named input) layers on later -- INPUT / OWN wire
frames are accepted and ignored here.

The session is deliberately GameRunner-agnostic: it exposes ``shared`` and
a queue of ``(event_name, *payload)`` tuples via ``take_events()``. The
handlers.py frame-update glue (Phase 5.2) is what mirrors ``shared`` into
``game_runner.global_variables``, sets the identity globals, and fires the
queued events on the room's instances. That keeps this file testable over
a real ``127.0.0.1`` socket with no engine at all.
"""

import time
from collections import deque
from typing import Optional

from core.logger import get_logger
from .network import CONN_CLOSED, CONN_OPENED, NetworkClient, NetworkHost
from .replication import NetIdAllocator, SnapshotApplier, SnapshotBuilder
from .state import (
    DEFAULT_PORT, MAX_STR_LEN, MSG_BYE, MSG_GAME_START, MSG_HELLO, MSG_JOIN,
    MSG_LEAVE, MSG_MSG, MSG_OWN, MSG_SHARED_SET, MSG_SNAP, MSG_WELCOME,
    PROTO_VER, is_valid_shared_name, sanitize_name, sanitize_value,
)

logger = get_logger(__name__)

# How many "after_update" pumps between host snapshots. 3 @ 60 fps ~= 20 Hz,
# the plan's default snapshot rate. A shared-var change forces one out
# immediately regardless.
_SNAP_EVERY = 3

_MAX_PLAYERS_CEIL = 16

# Default interpolation delay: a client renders a ghost as it was this many
# seconds ago, lerping between the two snapshots that bracket that instant.
# ~= 2 snapshot intervals at 20 Hz -- enough to always have a "next" sample
# to interpolate toward on a LAN.
_DEFAULT_INTERP_DELAY = 0.10


class NetworkSession:
    """One machine's view of a LAN game. ``mode`` is ``"host"`` or
    ``"client"``. Call ``start()`` once, then ``pump_before_step()`` /
    ``pump_after_update()`` from the two frame-update hooks, and drain
    ``take_events()`` after each before-step pump."""

    def __init__(self, *, mode: str, host: Optional[str] = None,
                 port: int = DEFAULT_PORT, player_name: str = "Joueur",
                 max_players: int = 8):
        if mode not in ("host", "client"):
            raise ValueError(f"mode must be 'host' or 'client', not {mode!r}")
        self.mode = mode
        self.host_addr = host or "127.0.0.1"
        self.port = int(port)
        self.player_name = sanitize_name(player_name)
        self.max_players = max(2, min(_MAX_PLAYERS_CEIL, int(max_players)))

        self.player_id = 0 if mode == "host" else -1
        self.player_count = 1 if mode == "host" else 0
        self.shared = {}
        self.started = False
        self.connection_lost = False

        self._host: Optional[NetworkHost] = None
        self._client: Optional[NetworkClient] = None
        self._builder = SnapshotBuilder()
        self._applier = SnapshotApplier()

        # host-only roster bookkeeping
        self._roster = {}              # slot -> {"cid": int, "name": str}
        self._conn_slot = {}          # cid -> slot
        self._pending = set()         # cids accepted, awaiting a valid hello
        self._next_slot = 1

        self._events = deque()
        self._tick = 0
        self._since_snap = 0
        self._snap_every = _SNAP_EVERY
        self._shared_dirty = False

        # Tier B: networked instances.
        self._netids = NetIdAllocator()
        self._local_instances = []     # host: rows for the next snapshot
        self._ghost_creates = []       # client: accumulated (nid, obj, x, y)
        self._ghost_destroys = []      # client: accumulated nid
        self._own_state = {}           # host: nid -> latest client-owned row
        self.interp_delay = _DEFAULT_INTERP_DELAY

    # -- lifecycle ----------------------------------------------------

    def start(self) -> None:
        if self.mode == "host":
            self._host = NetworkHost(self.port)
            self._host.start()
        else:
            self._client = NetworkClient(self.host_addr, self.port)
            self._client.connect()
            self._client.send({"t": MSG_HELLO, "name": self.player_name,
                               "proto_ver": PROTO_VER})

    def close(self) -> None:
        if self._host is not None:
            self._host.close()
            self._host = None
        if self._client is not None:
            self._client.close()
            self._client = None

    @property
    def bound_port(self) -> int:
        """The port the host is actually listening on (useful when started
        with port 0). 0 if not a host / not started."""
        if self._host is not None and self._host._listen_sock is not None:
            return self._host._listen_sock.getsockname()[1]
        return 0

    @property
    def roster(self) -> list:
        """Host: ``[(slot, name), ...]`` including the host itself (slot 0)."""
        out = [(0, self.player_name)]
        out.extend((slot, r["name"]) for slot, r in sorted(self._roster.items()))
        return out

    # -- author-facing operations ----------------------------------

    def is_host(self) -> bool:
        return self.mode == "host"

    def set_shared(self, name: str, value) -> None:
        if not is_valid_shared_name(name):
            logger.warning("multiplayer: ignoring invalid shared-var name %r", name)
            return
        clean = sanitize_value(value)
        if self.mode == "host":
            if self.shared.get(name) != clean:
                self.shared[name] = clean
                self._shared_dirty = True
        elif self._client is not None:
            self._client.send({"t": MSG_SHARED_SET, "name": name, "value": clean})

    def get_shared(self, name: str, default=None):
        return self.shared.get(name, default)

    def send_message(self, event: str, data=None, target: str = "all") -> None:
        target = target if target in ("all", "host") else "all"
        payload = {
            "t": MSG_MSG,
            "event": str(event)[:MAX_STR_LEN],
            "data": sanitize_value(data),
            "sender": self.player_id,
            "target": target,
        }
        if self.mode == "host":
            self._queue_event("network_message", payload["event"],
                              payload["data"], self.player_id)
            if self._host is not None and target == "all":
                self._host.broadcast(payload)
        elif self._client is not None:
            self._client.send(payload)

    def start_game(self) -> None:
        """Host: leave the lobby, tell everyone to begin."""
        if self.mode != "host" or self.started:
            return
        self.started = True
        if self._host is not None:
            self._host.broadcast({"t": MSG_GAME_START})
        self._queue_event("network_game_started")

    def take_events(self) -> list:
        evs = list(self._events)
        self._events.clear()
        return evs

    # -- Tier B: networked instances -----------------------------

    def next_netid(self) -> int:
        """Host: allocate a stable network id for a newly synced instance."""
        return self._netids.allocate()

    def push_local_instances(self, rows) -> None:
        """Host: the rows for the next snapshot -- a list of dicts
        ``{"nid","o","x","y","r","f","v","vars"}``, one per host-owned
        synced instance. Call once per frame before ``pump_after_update``."""
        self._local_instances = list(rows or ())

    def take_ghost_changes(self):
        """Client: ``(to_create, to_destroy)`` accumulated since the last
        call. ``to_create`` is ``[(nid, object_name, x, y), ...]``;
        ``to_destroy`` is ``[nid, ...]``. Then cleared."""
        creates, self._ghost_creates = self._ghost_creates, []
        destroys, self._ghost_destroys = self._ghost_destroys, []
        return creates, destroys

    def ghost_ids(self) -> list:
        return self._applier.ghost_ids()

    def ghost_vars(self, nid: int) -> dict:
        return self._applier.ghost_vars(nid)

    def ghost_owner(self, nid):
        """Client: the player slot that owns netid ``nid`` per the latest
        snapshot (``None`` = host-owned / unassigned)."""
        return self._applier.ghost_owner(nid)

    def push_own_instances(self, rows) -> None:
        """Client: send this frame's state for the instances *this* player
        owns, up to the host. A no-op with no rows."""
        rows = list(rows or ())
        if rows and self._client is not None:
            self._client.send({"t": MSG_OWN, "i": rows})

    def take_own_state(self) -> dict:
        """Host: ``{nid: row}`` -- the latest client-reported state for each
        client-owned instance since the last call. Then cleared."""
        state, self._own_state = self._own_state, {}
        return state

    def sample_ghost(self, nid: int):
        """Client: the ``(x, y, r, f, v)`` to draw ghost ``nid`` at right
        now (interpolated ``interp_delay`` seconds in the past), or
        ``None``."""
        return self._applier.sample(nid, time.monotonic() - self.interp_delay)

    def set_sync_rate(self, hz: float = 20.0, interp_ms: float = 100.0) -> None:
        """Tune the host snapshot rate and the client interpolation delay.
        ``hz`` is converted to a whole number of 60 fps frames per snapshot
        (>=1)."""
        try:
            hz = float(hz)
        except (TypeError, ValueError):
            hz = 20.0
        self._snap_every = max(1, round(60.0 / hz)) if hz > 0 else _SNAP_EVERY
        try:
            self.interp_delay = max(0.0, float(interp_ms) / 1000.0)
        except (TypeError, ValueError):
            self.interp_delay = _DEFAULT_INTERP_DELAY

    # -- frame pumps ----------------------------------------------

    def pump_before_step(self) -> None:
        if self.mode == "host":
            self._host_drain()
        else:
            self._client_drain()

    def pump_after_update(self) -> None:
        if self.mode == "host":
            self._host_drain()          # dispatch anything that arrived mid-frame, flush
            self._maybe_send_snapshot()
        elif self._client is not None:
            # before-step already drained inbound; just retry queued output.
            self._client.flush()

    def _maybe_send_snapshot(self) -> None:
        if self._host is None:
            return
        self._tick += 1
        self._since_snap += 1
        if self._shared_dirty or self._since_snap >= self._snap_every:
            frame = self._builder.build(
                self._local_instances, self.shared, tick=self._tick,
                time_ms=int(time.monotonic() * 1000))
            self._host.broadcast(frame)
            self._since_snap = 0
            self._shared_dirty = False

    # -- internals -----------------------------------------------

    def _queue_event(self, name: str, *payload) -> None:
        self._events.append((name, *payload))

    def _host_drain(self) -> None:
        if self._host is None:
            return
        for cid, frame in self._host.poll():
            t = frame.get("t")
            if t == CONN_OPENED:
                self._pending.add(cid)
            elif t == CONN_CLOSED:
                self._drop_conn(cid)
            elif t == MSG_HELLO:
                self._on_hello(cid, frame)
            elif t == MSG_SHARED_SET:
                self._on_shared_set(frame)
            elif t == MSG_MSG:
                self._on_client_msg(cid, frame)
            elif t == MSG_OWN:
                self._on_client_own(cid, frame)
            # MSG_INPUT: Tier B named input, not here yet.

    def _on_hello(self, cid: int, frame: dict) -> None:
        if cid not in self._pending:
            return
        self._pending.discard(cid)
        if frame.get("proto_ver") != PROTO_VER:
            self._host.send(cid, {"t": MSG_BYE, "reason": "protocol version mismatch"})
            self._host.disconnect(cid)
            return
        if len(self._roster) + 1 >= self.max_players:
            self._host.send(cid, {"t": MSG_BYE, "reason": "game full"})
            self._host.disconnect(cid)
            return
        slot = self._next_slot
        self._next_slot += 1
        name = sanitize_name(frame.get("name"))
        self._roster[slot] = {"cid": cid, "name": name}
        self._conn_slot[cid] = slot
        self.player_count = 1 + len(self._roster)
        self._host.send(cid, {
            "t": MSG_WELCOME,
            "player_id": slot,
            "player_count": self.player_count,
            "shared": dict(self.shared),
            "roster": self.roster,
            "tick": self._tick,
        })
        self._host.broadcast({"t": MSG_JOIN, "player_id": slot, "name": name},
                             exclude=cid)
        self._queue_event("player_joined", slot, name)

    def _drop_conn(self, cid: int) -> None:
        self._pending.discard(cid)
        slot = self._conn_slot.pop(cid, None)
        if slot is None:
            return
        name = self._roster.pop(slot, {}).get("name", "")
        self.player_count = 1 + len(self._roster)
        if self._host is not None:
            self._host.broadcast({"t": MSG_LEAVE, "player_id": slot, "name": name})
        self._queue_event("player_left", slot, name)

    def _on_shared_set(self, frame: dict) -> None:
        name = frame.get("name")
        if not is_valid_shared_name(name):
            return
        clean = sanitize_value(frame.get("value"))
        if self.shared.get(name) != clean:
            self.shared[name] = clean
            self._shared_dirty = True

    def _on_client_msg(self, cid: int, frame: dict) -> None:
        sender = self._conn_slot.get(cid, -1)      # trust the slot we assigned
        event = str(frame.get("event", ""))[:MAX_STR_LEN]
        data = sanitize_value(frame.get("data"))
        target = frame.get("target", "all")
        self._queue_event("network_message", event, data, sender)
        if target == "all" and self._host is not None:
            self._host.broadcast(
                {"t": MSG_MSG, "event": event, "data": data,
                 "sender": sender, "target": "all"},
                exclude=cid)

    def _on_client_own(self, cid: int, frame: dict) -> None:
        slot = self._conn_slot.get(cid)
        if slot is None:
            return
        for row in frame.get("i") or ():
            nid = row.get("nid")
            if nid is None:
                continue
            iv = row.get("vars")
            self._own_state[nid] = {
                "nid": nid,
                "x": row.get("x", 0), "y": row.get("y", 0),
                "r": row.get("r", 0), "f": row.get("f", 0),
                "v": bool(row.get("v", 1)),
                "vars": iv if isinstance(iv, dict) else None,
                "_from": slot,           # which client claimed it -- host verifies
            }

    def _client_drain(self) -> None:
        if self._client is None:
            return
        frames = self._client.take_frames()
        for frame in frames:
            t = frame.get("t")
            if t == MSG_WELCOME:
                self.player_id = int(frame.get("player_id", -1))
                self.player_count = int(frame.get("player_count", 1))
                self.shared = dict(frame.get("shared") or {})
                self._applier.shared = dict(self.shared)
                self._queue_event("network_started")
            elif t == MSG_JOIN:
                self.player_count += 1
                self._queue_event("player_joined", frame.get("player_id"),
                                  frame.get("name", ""))
            elif t == MSG_LEAVE:
                self.player_count = max(1, self.player_count - 1)
                self._queue_event("player_left", frame.get("player_id"),
                                  frame.get("name", ""))
            elif t == MSG_MSG:
                self._queue_event("network_message", str(frame.get("event", "")),
                                  sanitize_value(frame.get("data")),
                                  frame.get("sender", -1))
            elif t == MSG_SNAP:
                created, destroyed = self._applier.ingest(frame, time.monotonic())
                self._ghost_creates.extend(created)
                self._ghost_destroys.extend(destroyed)
                self.shared = dict(self._applier.shared)
            elif t == MSG_GAME_START:
                if not self.started:
                    self.started = True
                    self._queue_event("network_game_started")
            elif t == MSG_BYE:
                self._flag_lost(frame.get("reason", ""))

        if not self._client.connected and not self.connection_lost:
            self._flag_lost("connection closed")

    def _flag_lost(self, reason: str) -> None:
        if self.connection_lost:
            return
        self.connection_lost = True
        logger.info("multiplayer: connection lost (%s)", reason)
        self._queue_event("connection_lost", reason)
