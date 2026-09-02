#!/usr/bin/env python3
"""Snapshot build (host) and apply/interpolate (client) -- pure logic.

docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 4.3. No socket, no pygame: everything
here works on plain data. The Phase 5 session layer is what pulls primitive
state out of live instances to feed ``SnapshotBuilder``, and turns
``SnapshotApplier``'s create/destroy lists + interpolated samples back into
real ghost instances.

Three pieces:

* ``NetIdAllocator`` -- monotonic per-instance network ids (distinct from
  ``id(inst)`` and from v1's positional ``_sync_id``). Never reused, so a
  spawn/despawn can't be confused with a moved instance.
* ``SnapshotBuilder`` -- host side. Turns "here is every synced instance's
  state right now, and the shared-var dict" into a ``snap`` frame carrying
  only what changed since the last one: a ``shared`` delta, a ``spawn``
  list (netids new this frame), a ``despawn`` list (netids gone), and the
  full ``i`` position list.
* ``SnapshotApplier`` -- client side. Feeds incoming ``snap`` frames into a
  per-ghost interpolation buffer; ``sample(nid, render_time)`` returns the
  position to draw that ghost at, lerped between the two buffered states
  bracketing ``render_time`` (the caller picks ``render_time`` = now minus
  its interpolation delay). Discrete fields (frame index, visibility) are
  not interpolated -- they take the value of the earlier bracket.
"""

from collections import deque

# Per-ghost interpolation buffer: keep a little history, drop the rest.
_BUFFER_LEN = 12


class NetIdAllocator:
    """Hands out 1, 2, 3, ... and never repeats."""

    def __init__(self, start: int = 1):
        self._next = int(start)

    def allocate(self) -> int:
        nid = self._next
        self._next += 1
        return nid

    @property
    def peek_next(self) -> int:
        return self._next


def _shared_delta(prev: dict, current: dict) -> dict:
    """Keys whose value changed (or appeared), plus removed keys mapped to
    ``None``. A first call (empty ``prev``) yields all of ``current``."""
    delta = {}
    for key, val in current.items():
        if key not in prev or prev[key] != val:
            delta[key] = val
    for key in prev:
        if key not in current:
            delta[key] = None
    return delta


class SnapshotBuilder:
    """Host side: builds delta-compressed ``snap`` frames.

    ``build(instances, shared, tick, time_ms)`` -- ``instances`` is a list
    of dicts ``{"nid", "o", "x", "y", "r", "f", "v", "vars"}`` (``o`` = the
    object name, needed only so a client can create the ghost; ``vars`` an
    optional dict of replicated instance variables). Returns the ``snap``
    dict to send.
    """

    def __init__(self):
        self._last_shared = {}
        self._known = {}          # nid -> object name last seen

    def reset(self) -> None:
        """Forget history so the next ``build`` is a full one -- call on a
        room change / restart."""
        self._last_shared = {}
        self._known = {}

    def build(self, instances, shared, tick: int = 0, time_ms: int = 0) -> dict:
        shared = shared or {}
        current = {}
        rows = []
        spawn = []
        for inst in instances:
            nid = inst["nid"]
            obj = inst.get("o", "")
            current[nid] = obj
            if nid not in self._known:
                spawn.append({"nid": nid, "o": obj,
                              "x": inst.get("x", 0), "y": inst.get("y", 0)})
            row = {
                "nid": nid,
                "x": inst.get("x", 0), "y": inst.get("y", 0),
                "r": inst.get("r", 0), "f": inst.get("f", 0),
                "v": 1 if inst.get("v", True) else 0,
            }
            iv = inst.get("vars")
            if iv:
                row["vars"] = dict(iv)
            if inst.get("own") is not None:
                row["own"] = inst["own"]
            rows.append(row)

        despawn = [nid for nid in self._known if nid not in current]

        frame = {"t": "snap", "tick": int(tick), "time": int(time_ms), "i": rows}
        delta = _shared_delta(self._last_shared, shared)
        if delta:
            frame["shared"] = delta
        if spawn:
            frame["spawn"] = spawn
        if despawn:
            frame["despawn"] = despawn

        self._last_shared = dict(shared)
        self._known = current
        return frame


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_angle(a: float, b: float, t: float) -> float:
    """Shortest-arc angle interpolation, so 350 -> 10 goes forward through
    0 rather than backward through 180."""
    d = (b - a + 180.0) % 360.0 - 180.0
    return a + d * t


class _Ghost:
    __slots__ = ("obj", "vars", "samples", "owner")

    def __init__(self, obj: str):
        self.obj = obj
        self.vars = {}
        self.owner = None          # player slot that owns this instance, or None (host)
        self.samples = deque(maxlen=_BUFFER_LEN)   # (recv_time, x, y, r, f, v)


class SnapshotApplier:
    """Client side: ingest ``snap`` frames, interpolate ghost positions.

    ``ingest(frame, now)`` returns ``(to_create, to_destroy)`` where
    ``to_create`` is ``[(nid, object_name, x, y), ...]`` and ``to_destroy``
    is ``[nid, ...]`` -- the session creates/removes the real instances.
    ``sample(nid, render_time)`` returns ``(x, y, r, f, v)`` or ``None``.
    ``shared`` is the running mirror of the host's shared-var dict.
    """

    def __init__(self):
        self._ghosts = {}         # nid -> _Ghost
        self.shared = {}
        self.last_tick = -1
        self.last_time = 0

    def reset(self) -> None:
        self._ghosts.clear()
        self.shared = {}
        self.last_tick = -1
        self.last_time = 0

    def ghost_ids(self) -> list:
        return list(self._ghosts)

    def ghost_vars(self, nid: int) -> dict:
        g = self._ghosts.get(nid)
        return g.vars if g is not None else {}

    def ghost_owner(self, nid: int):
        g = self._ghosts.get(nid)
        return g.owner if g is not None else None

    def ingest(self, frame: dict, now: float):
        to_create = []
        to_destroy = []

        for key, val in (frame.get("shared") or {}).items():
            self.shared[key] = val

        for spec in frame.get("spawn") or ():
            nid = spec.get("nid")
            if nid is None or nid in self._ghosts:
                continue
            self._ghosts[nid] = _Ghost(spec.get("o", ""))
            to_create.append((nid, spec.get("o", ""),
                              spec.get("x", 0), spec.get("y", 0)))

        for nid in frame.get("despawn") or ():
            if self._ghosts.pop(nid, None) is not None:
                to_destroy.append(nid)

        for row in frame.get("i") or ():
            nid = row.get("nid")
            g = self._ghosts.get(nid)
            if g is None:
                # A position row for a ghost we were never told to spawn
                # (joined mid-game, missed the spawn frame). Adopt it so
                # the session can still create it.
                g = self._ghosts.setdefault(nid, _Ghost(row.get("o", "")))
                to_create.append((nid, g.obj, row.get("x", 0), row.get("y", 0)))
            g.samples.append((
                now,
                float(row.get("x", 0)), float(row.get("y", 0)),
                float(row.get("r", 0)), row.get("f", 0),
                bool(row.get("v", 1)),
            ))
            if "vars" in row and isinstance(row["vars"], dict):
                g.vars.update(row["vars"])
            if "own" in row:
                g.owner = row["own"]

        if "tick" in frame:
            self.last_tick = int(frame["tick"])
        if "time" in frame:
            self.last_time = int(frame["time"])
        return to_create, to_destroy

    def sample(self, nid: int, render_time: float):
        g = self._ghosts.get(nid)
        if g is None or not g.samples:
            return None
        buf = g.samples
        if len(buf) == 1 or render_time <= buf[0][0]:
            t, x, y, r, f, v = buf[0]
            return (x, y, r, f, v)
        if render_time >= buf[-1][0]:
            t, x, y, r, f, v = buf[-1]
            return (x, y, r, f, v)

        for i in range(len(buf) - 1):
            t0 = buf[i][0]
            t1 = buf[i + 1][0]
            if t0 <= render_time <= t1:
                span = t1 - t0
                alpha = 0.0 if span <= 0 else (render_time - t0) / span
                _, x0, y0, r0, f0, v0 = buf[i]
                _, x1, y1, r1, _f1, _v1 = buf[i + 1]
                return (
                    _lerp(x0, x1, alpha),
                    _lerp(y0, y1, alpha),
                    _lerp_angle(r0, r1, alpha),
                    f0,      # discrete: hold the earlier bracket
                    v0,
                )
        # Unreachable given the bracket checks above, but be safe.
        _, x, y, r, f, v = buf[-1]
        return (x, y, r, f, v)
