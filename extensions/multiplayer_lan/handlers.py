#!/usr/bin/env python3
"""Runtime handlers for the LAN multiplayer extension.

Mirrors extensions/block_world/handlers.py: a plugin's action handlers run
as methods of a PluginExecutor instance, reaching the engine through
instance.action_executor (the plugins/audio_actions pattern), not through
ActionExecutor directly. The two frame-update functions are plain
``(game_runner) -> None`` callables (see runtime/extension_hooks.py),
registered via PLUGIN_FRAME_UPDATES in __init__.py.

Two paths coexist, keyed off ``room.extension_state["multiplayer_lan"]``:

* **v1** (``set_network_mode`` action, or the ``PYGM_NET_*`` env vars set
  by run_game.py's --net-host/--net-client flags) -- a raw
  ``NetworkHost``/``NetworkClient`` in ``st["host"]``/``st["client"]``,
  spectator-only position sync. Unchanged.
* **v2 Tier A** (``host_game`` / ``join_game``) -- a ``NetworkSession`` in
  ``st["session"]``: shared variables, custom messages, player identity,
  and the ``PLUGIN_EVENTS`` lifecycle events. When a session is present it
  takes over both frame-update hooks and the v1 path is skipped.
"""

import os

from core.logger import get_logger
from .network import NetworkClient, NetworkHost
from .session import NetworkSession
from .state import DEFAULT_PORT, multiplayer_state, peek_multiplayer

logger = get_logger(__name__)

# Env vars run_game.py's --net-host/--net-client/--net-port CLI flags set
# (docs/MULTIPLAYER_LAN_PLAN.md Phase 2) -- a fallback for when no
# set_network_mode action was ever authored, so a game with zero
# multiplayer UI still works purely from the command line for quick
# testing. run_game.py sets these directly; it does NOT import this
# extension, keeping that generic bootstrap script unaware networking
# exists at all.
ENV_MODE = "PYGM_NET_MODE"
ENV_HOST = "PYGM_NET_HOST_ADDR"
ENV_PORT = "PYGM_NET_PORT"

# Globals the session mirrors into game_runner.global_variables every frame
# so an author can read identity / connection state with an ordinary
# ``global.<name>`` expression (no core change -- see the plan's "Core
# changes"). Cleared by leave_game.
_NETWORK_GLOBALS = (
    "player_id", "player_count", "network_role", "is_host", "is_client",
    "network_connected", "network_event", "network_data", "network_sender",
    "network_player_name",
)


def _env_config():
    """(mode, host, port) from the PYGM_NET_* env vars, or None if
    PYGM_NET_MODE isn't set to a recognized value."""
    mode = os.environ.get(ENV_MODE)
    if mode not in ("host", "client"):
        return None
    host = os.environ.get(ENV_HOST) or None
    try:
        port = int(os.environ.get(ENV_PORT, DEFAULT_PORT))
    except (TypeError, ValueError):
        port = DEFAULT_PORT
    return mode, host, port


def _assign_sync_ids(room):
    """Deterministic sync IDs: enumerate the room's current instances in
    order. Both sides load the same project and start from the same room,
    so indices match without any negotiation -- mirrors the stashed
    prototype's own _init_network exactly."""
    for idx, inst in enumerate(room.instances):
        inst._sync_id = idx


def _start_network(room, mode, host, port):
    """v1 connect/listen step, shared by set_network_mode and the env-var
    fallback. Never raises -- a failed connect/listen degrades to "no
    networking this session" rather than crashing the game."""
    st = multiplayer_state(room)
    if st["mode"] is not None:
        return  # already initialized for this room -- don't double-connect
    st["mode"] = mode

    if not st["sync_ids_assigned"]:
        _assign_sync_ids(room)
        st["sync_ids_assigned"] = True

    try:
        if mode == "host":
            net_host = NetworkHost(port=port)
            net_host.start()
            st["host"] = net_host
        elif mode == "client":
            net_client = NetworkClient(host or "127.0.0.1", port=port)
            net_client.connect()
            st["client"] = net_client
    except OSError:
        st["mode"] = None
        st["host"] = None
        st["client"] = None
        return

    st["enabled"] = True


# ---------------------------------------------------------------------------
# v2 helpers
# ---------------------------------------------------------------------------

def _pv(ae, instance, raw, default):
    """Parse an action param through the expression evaluator, falling back
    to ``default`` when it's missing/blank/unparseable. For *value* params
    (a shared-var's value, a message's data) -- NOT for names/labels, which
    must stay literal (``_parse_value`` turns the bare word ``score`` into
    the number 0)."""
    if raw is None or raw == "":
        return default
    try:
        val = ae._parse_value(raw, instance)
    except Exception:
        return default
    return default if val is None or val == "" else val


def _pv_int(ae, instance, raw, default):
    try:
        return int(float(_pv(ae, instance, raw, default)))
    except (TypeError, ValueError):
        return default


def _raw(parameters, key, default=""):
    """A param taken literally -- a name, label or address, never run
    through the expression evaluator."""
    val = parameters.get(key)
    if val is None:
        return default
    val = str(val).strip()
    return val if val else default


def _player_name(game_runner, explicit):
    if explicit:
        return str(explicit)
    gv = getattr(game_runner, "global_variables", {}) or {}
    return str(gv.get("player_name") or "Joueur")


def _room_and_executor(instance):
    ae = getattr(instance, "action_executor", None)
    if ae is None or not getattr(ae, "game_runner", None):
        return None, None
    return getattr(ae.game_runner, "current_room", None), ae


def _start_session(room, session):
    """Try to start a NetworkSession; stash it on room state or discard it
    on failure. Never raises."""
    try:
        session.start()
    except OSError as exc:
        logger.warning("multiplayer: could not start %s session: %s", session.mode, exc)
        try:
            session.close()
        except Exception:
            pass
        return False
    st = multiplayer_state(room)
    st["session"] = session
    st["mode"] = session.mode
    st["enabled"] = True
    return True


class PluginExecutor:
    """Handles execution of the LAN multiplayer actions."""

    @staticmethod
    def _executor(instance):
        return getattr(instance, "action_executor", None)

    # -- v1 --------------------------------------------------------------

    def execute_set_network_mode_action(self, instance, parameters):
        """v1 low-level: start this room as a raw host or client (spectator
        position sync only). A no-op if this room already has any
        networking configured."""
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room
        if peek_multiplayer(room) and peek_multiplayer(room).get("session") is not None:
            return  # a v2 session already owns this room

        mode = ae._parse_value(parameters.get("mode", ""), instance)
        mode = str(mode) if mode else ""
        if mode not in ("host", "client"):
            return

        host = parameters.get("host")
        host = str(ae._parse_value(host, instance)) if host else None

        try:
            port = int(float(ae._parse_value(parameters.get("port", DEFAULT_PORT), instance)))
        except (TypeError, ValueError):
            port = DEFAULT_PORT

        _start_network(room, mode, host, port)

    # -- v2 Tier A: lifecycle ----------------------------------------

    def execute_host_game_action(self, instance, parameters):
        room, ae = _room_and_executor(instance)
        if room is None:
            return
        st = peek_multiplayer(room)
        if st and (st.get("session") is not None or st.get("mode") is not None):
            return  # already networked
        session = NetworkSession(
            mode="host",
            port=_pv_int(ae, instance, parameters.get("port"), DEFAULT_PORT),
            max_players=_pv_int(ae, instance, parameters.get("max_players"), 8),
            player_name=_player_name(ae.game_runner, _raw(parameters, "player_name")),
        )
        _start_session(room, session)

    def execute_join_game_action(self, instance, parameters):
        room, ae = _room_and_executor(instance)
        if room is None:
            return
        st = peek_multiplayer(room)
        if st and (st.get("session") is not None or st.get("mode") is not None):
            return
        host = _raw(parameters, "host", "127.0.0.1")
        if host == "auto":
            # Phase 6 opens the built-in connect screen here; for now fall
            # back to loopback so a single-box test still connects.
            host = "127.0.0.1"
        session = NetworkSession(
            mode="client", host=host,
            port=_pv_int(ae, instance, parameters.get("port"), DEFAULT_PORT),
            player_name=_player_name(ae.game_runner, _raw(parameters, "player_name")),
        )
        _start_session(room, session)

    def execute_leave_game_action(self, instance, parameters):
        room, ae = _room_and_executor(instance)
        if room is None:
            return
        st = peek_multiplayer(room)
        if not st:
            return
        session = st.get("session")
        if session is not None:
            try:
                session.close()
            except Exception:
                pass
        for inst in (st.get("ghosts") or {}).values():
            inst.to_destroy = True
        st["session"] = None
        st["host"] = None
        st["client"] = None
        st["mode"] = None
        st["enabled"] = False
        st["synced"] = None
        st["ghosts"] = None
        st["synced_local"] = None
        st["sync_ord"] = None
        gv = getattr(ae.game_runner, "global_variables", None)
        if isinstance(gv, dict):
            for key in _NETWORK_GLOBALS:
                gv.pop(key, None)

    def execute_start_networked_game_action(self, instance, parameters):
        session = self._session_for(instance)
        if session is not None:
            session.start_game()

    # -- v2 Tier A: shared blackboard + messages -------------------

    def execute_set_shared_var_action(self, instance, parameters):
        session = self._session_for(instance)
        if session is None:
            return
        ae = self._executor(instance)
        name = _raw(parameters, "name")
        if not name:
            return
        value = _pv(ae, instance, parameters.get("value"), 0)
        session.set_shared(name, value)
        # Reflect the host's own write locally this frame so a following
        # action in the same event sees it (the mirror otherwise lands next
        # frame). A client write is only a request -- don't fake it.
        if session.is_host():
            gv = getattr(ae.game_runner, "global_variables", None)
            if isinstance(gv, dict) and name in session.shared:
                gv[name] = session.shared[name]

    def execute_get_shared_var_action(self, instance, parameters):
        session = self._session_for(instance)
        ae = self._executor(instance)
        if ae is None:
            return
        name = _raw(parameters, "name")
        into = _raw(parameters, "into")
        if not into:
            return
        value = session.get_shared(name) if session is not None else None
        gv = getattr(ae.game_runner, "global_variables", None)
        if isinstance(gv, dict):
            gv[into] = value

    def execute_send_network_message_action(self, instance, parameters):
        session = self._session_for(instance)
        if session is None:
            return
        ae = self._executor(instance)
        event = _raw(parameters, "event")
        if not event:
            return
        data = _pv(ae, instance, parameters.get("data"), None)
        target = parameters.get("target", "all")
        target = target if target in ("all", "host") else "all"
        session.send_message(event, data, target)

    # -- v2 Tier B: networked instances --------------------------

    def execute_network_spawn_action(self, instance, parameters):
        """Host-only replicated create. Reuses the engine's own
        create_instance path (so the host copy is a fully normal instance,
        create event and all), then tags it with a network id so the
        frame-update hook includes it in the snapshot."""
        session = self._session_for(instance)
        if session is None or not session.is_host():
            return
        ae = self._executor(instance)
        room = getattr(ae.game_runner, "current_room", None)
        if room is None:
            return
        object_name = _raw(parameters, "object")
        if not object_name:
            return

        before = {id(i) for i in room.instances}
        ae.execute_create_instance_action(instance, {
            "object": object_name,
            "x": parameters.get("x", 0),
            "y": parameters.get("y", 0),
            "relative": parameters.get("relative", False),
        })
        new_insts = [i for i in room.instances if id(i) not in before]
        if not new_insts:
            return
        synced = multiplayer_state(room).setdefault("synced", {})
        for inst in new_insts:
            nid = session.next_netid()
            inst._net_id = nid
            synced[nid] = inst

    def execute_set_sync_rate_action(self, instance, parameters):
        session = self._session_for(instance)
        if session is None:
            return
        ae = self._executor(instance)
        session.set_sync_rate(
            _pv(ae, instance, parameters.get("hz"), 20.0),
            _pv(ae, instance, parameters.get("interp_ms"), 100.0),
        )

    def execute_sync_instance_action(self, instance, parameters):
        """Mark the acting instance as network-synced. Host: it becomes a
        host-owned replicated instance. Client: it's registered as the
        local stand-in for a shared netid (driven by snapshots unless this
        player owns it). The netid is ``<object>#<ordinal>`` -- deterministic
        across machines because both load the same room and run this action
        in the same create-event order."""
        session = self._session_for(instance)
        if session is None:
            return
        ae = self._executor(instance)
        room = getattr(ae.game_runner, "current_room", None)
        if room is None:
            return
        st = multiplayer_state(room)
        nid = getattr(instance, "_net_id", None) or _deterministic_netid(st, instance.object_name)
        instance._net_id = nid
        if getattr(instance, "_net_owner", None) is None:
            instance._net_owner = 0            # host by default

        raw_vars = _raw(parameters, "vars")
        if raw_vars:
            instance._net_sync_vars = [v.strip() for v in raw_vars.split(",") if v.strip()]

        if session.is_host():
            st.setdefault("synced", {})[nid] = instance
        else:
            st.setdefault("synced_local", {})[nid] = instance

    def execute_set_instance_owner_action(self, instance, parameters):
        session = self._session_for(instance)
        if session is None:
            return
        ae = self._executor(instance)
        try:
            instance._net_owner = int(float(_pv(ae, instance, parameters.get("player"), 0)))
        except (TypeError, ValueError):
            instance._net_owner = 0

    def execute_is_instance_owner_action(self, instance, parameters):
        """Condition: True iff this machine owns the acting instance."""
        session = self._session_for(instance)
        if session is None:
            return False
        owner = getattr(instance, "_net_owner", None)
        return owner is not None and owner == session.player_id

    # -- internals -----------------------------------------------

    @staticmethod
    def _session_for(instance):
        ae = getattr(instance, "action_executor", None)
        if ae is None or not getattr(ae, "game_runner", None):
            return None
        room = getattr(ae.game_runner, "current_room", None)
        st = peek_multiplayer(room) if room is not None else None
        return st.get("session") if st else None


# ---------------------------------------------------------------------------
# Frame-update hooks
# ---------------------------------------------------------------------------

def _fire_network_event(room, event_name):
    """Run ``event_name`` on every instance in the room that handles it."""
    for inst in list(getattr(room, "instances", ())):
        ae = getattr(inst, "action_executor", None)
        obj_data = getattr(inst, "object_data", None)
        if ae is None or not isinstance(obj_data, dict):
            continue
        events = obj_data.get("events")
        if not isinstance(events, dict) or event_name not in events:
            continue
        try:
            ae.execute_event(inst, event_name, events)
        except Exception:
            logger.exception("multiplayer: %s handler raised", event_name)


def _apply_session_state(game_runner, session):
    """Mirror the session's identity + shared vars into globals, then fire
    any queued lifecycle events. Runs in the before_step phase."""
    gv = getattr(game_runner, "global_variables", None)
    room = getattr(game_runner, "current_room", None)
    if not isinstance(gv, dict) or room is None:
        return

    connected = not session.connection_lost and (
        session.mode == "host" or session.player_id >= 0)
    gv["player_id"] = session.player_id
    gv["player_count"] = session.player_count
    gv["network_role"] = session.mode
    gv["is_host"] = 1 if session.mode == "host" else 0
    gv["is_client"] = 1 if session.mode == "client" else 0
    gv["network_connected"] = 1 if connected else 0
    for key, val in session.shared.items():
        gv[key] = val

    for event in session.take_events():
        name = event[0]
        if name == "network_message":
            _, ev_name, data, sender = event
            gv["network_event"] = ev_name
            gv["network_data"] = data
            gv["network_sender"] = sender
        elif name in ("player_joined", "player_left"):
            _, slot, pname = event
            gv["network_sender"] = slot
            gv["network_player_name"] = pname
        elif name == "connection_lost":
            gv["network_connected"] = 0
        _fire_network_event(room, name)


_GHOST_VAR_WHITELIST_TYPES = (int, float, str, bool)


def _deterministic_netid(st, object_name):
    """``<object>#<ordinal>`` -- ordinal counted per room per object type in
    the order ``sync_instance`` is called. Both machines load the same room
    and run create events in the same order, so the same instance gets the
    same id on every machine with no coordination."""
    ords = st.setdefault("sync_ord", {})
    n = ords.get(object_name, 0)
    ords[object_name] = n + 1
    return "{}#{}".format(object_name, n)


def _instance_vars_row(inst):
    names = getattr(inst, "_net_sync_vars", None)
    if not names:
        return None
    out = {}
    for name in names:
        if hasattr(inst, name):
            val = getattr(inst, name)
            if isinstance(val, _GHOST_VAR_WHITELIST_TYPES):
                out[name] = val
    return out or None


def _row_from_instance(nid, inst):
    row = {
        "nid": nid, "o": inst.object_name,
        "x": inst.x, "y": inst.y,
        "r": getattr(inst, "rotation", 0),
        "f": getattr(inst, "image_index", 0),
        "v": bool(getattr(inst, "visible", True)),
        "own": getattr(inst, "_net_owner", 0),
    }
    iv = _instance_vars_row(inst)
    if iv:
        row["vars"] = iv
    return row


def _spawn_ghost(game_runner, object_name, x, y, nid):
    """Create a client-side puppet of a host-owned networked instance. Like
    execute_create_instance_action's build path, but the ``create`` event
    is suppressed -- a ghost is driven entirely by snapshots, not by its
    own authored logic (open Q#3). Returns the instance or None."""
    room = getattr(game_runner, "current_room", None)
    if room is None:
        return None
    objects_data = (getattr(game_runner, "project_data", {}) or {}).get(
        "assets", {}).get("objects", {})
    if object_name not in objects_data:
        logger.warning("multiplayer: ghost object %r not in project", object_name)
        return None
    object_data = objects_data[object_name]

    from runtime.game_runner import GameInstance, resolve_parent_inheritance

    inst = GameInstance(object_name, float(x), float(y),
                        {"visible": True}, action_executor=game_runner.action_executor)
    merged = resolve_parent_inheritance(object_data, getattr(game_runner, "_objects_data", {}))
    inst.set_object_data(merged)
    sprite_name = object_data.get("sprite", "")
    sprites = getattr(game_runner, "sprites", {}) or {}
    if sprite_name and sprite_name in sprites:
        inst.set_sprite(sprites[sprite_name])
    inst._create_fired = True          # a ghost never runs its create event
    inst._net_ghost = nid

    room.instances.append(inst)
    if hasattr(room, "_add_to_grid"):
        room._add_to_grid(inst)
    room._depth_dirty = True
    if hasattr(room, "invalidate_collision_listened_types"):
        room.invalidate_collision_listened_types()
    return inst


def _apply_host_own_state(st, session):
    """Host, before_step: fold each client's latest reported state for the
    instances it owns into the host's own copy, so the host sim and the
    outgoing snapshot agree. A row is only accepted if the claiming client
    really is the recorded owner."""
    synced = st.get("synced")
    if not synced:
        return
    for nid, row in session.take_own_state().items():
        inst = synced.get(nid)
        if inst is None:
            continue
        if getattr(inst, "_net_owner", 0) != row.get("_from"):
            continue                       # a client can't grab an instance it doesn't own
        inst.x = row.get("x", inst.x)
        inst.y = row.get("y", inst.y)
        inst.rotation = row.get("r", getattr(inst, "rotation", 0))
        inst.image_index = row.get("f", getattr(inst, "image_index", 0))
        inst.visible = bool(row.get("v", getattr(inst, "visible", True)))
        for key, val in (row.get("vars") or {}).items():
            if isinstance(val, _GHOST_VAR_WHITELIST_TYPES):
                setattr(inst, key, val)


def _collect_synced_rows(room, st):
    """Host: primitive rows for every live networked instance, pruning any
    that were destroyed."""
    synced = st.get("synced")
    if not synced:
        return []
    live = set(id(i) for i in getattr(room, "instances", ()))
    rows = []
    for nid in list(synced):
        inst = synced[nid]
        if id(inst) not in live or getattr(inst, "to_destroy", False):
            del synced[nid]
            continue
        rows.append(_row_from_instance(nid, inst))
    return rows


def _apply_ghosts(game_runner, st, session):
    """Client: create / destroy / interpolate the ghost instances that
    mirror the host's networked instances. Runs after _apply_session_state
    in the before_step phase, so Step events see this frame's positions."""
    room = getattr(game_runner, "current_room", None)
    if room is None:
        return
    ghosts = st.setdefault("ghosts", {})

    synced_local = st.get("synced_local") or {}
    to_create, to_destroy = session.take_ghost_changes()
    for nid, obj, x, y in to_create:
        if nid in ghosts or nid in synced_local:
            continue                       # client already has a real copy of this netid
        inst = _spawn_ghost(game_runner, obj, x, y, nid)
        if inst is not None:
            ghosts[nid] = inst
    for nid in to_destroy:
        inst = ghosts.pop(nid, None)
        if inst is not None:
            inst.to_destroy = True

    for nid in list(ghosts):
        inst = ghosts[nid]
        if getattr(inst, "to_destroy", False):
            del ghosts[nid]
            continue
        pos = session.sample_ghost(nid)
        if pos is None:
            continue
        gx, gy, gr, gf, gv = pos
        inst.x = gx
        inst.y = gy
        inst.rotation = gr
        inst.image_index = gf
        inst.visible = bool(gv)
        for key, val in session.ghost_vars(nid).items():
            if isinstance(val, _GHOST_VAR_WHITELIST_TYPES):
                setattr(inst, key, val)


def _apply_synced_local(game_runner, st, session):
    """Client, before_step: for each room instance registered via
    sync_instance, either leave it under local control (this player owns
    it) or drive it from the interpolated snapshot (a ghost of the host's
    / another player's copy)."""
    synced_local = st.get("synced_local")
    if not synced_local:
        return
    room = getattr(game_runner, "current_room", None)
    live = set(id(i) for i in getattr(room, "instances", ())) if room else set()
    for nid in list(synced_local):
        inst = synced_local[nid]
        if id(inst) not in live or getattr(inst, "to_destroy", False):
            del synced_local[nid]
            continue
        owner = session.ghost_owner(nid)
        inst._net_owner = 0 if owner is None else owner
        if inst._net_owner == session.player_id:
            continue                       # mine -- local sim is authoritative here
        pos = session.sample_ghost(nid)
        if pos is None:
            continue
        gx, gy, gr, gf, gv = pos
        inst.x = gx
        inst.y = gy
        inst.rotation = gr
        inst.image_index = gf
        inst.visible = bool(gv)
        for key, val in session.ghost_vars(nid).items():
            if isinstance(val, _GHOST_VAR_WHITELIST_TYPES):
                setattr(inst, key, val)


def _send_owned(st, session):
    """Client, after_update: report this frame's state for every synced
    instance this player owns, up to the host."""
    synced_local = st.get("synced_local")
    if not synced_local:
        return
    rows = [
        _row_from_instance(nid, inst)
        for nid, inst in synced_local.items()
        if getattr(inst, "_net_owner", 0) == session.player_id
        and not getattr(inst, "to_destroy", False)
    ]
    session.push_own_instances(rows)


def _resolve_state(game_runner):
    """This room's multiplayer state, auto-initialising the v1 env-var
    path if configured. None if this room has no networking."""
    room = getattr(game_runner, "current_room", None)
    if room is None:
        return None, None
    st = peek_multiplayer(room)
    if st is None:
        env = _env_config()
        if env is not None:
            _start_network(room, *env)
            st = peek_multiplayer(room)
    return room, st


def _frame_update_apply_inbound(game_runner):
    """before_step: drain inbound network state so Step events see it.

    v2 session present -> pump it and refresh globals/events. Otherwise the
    v1 spectator path: a client applies the latest position snapshot to
    its ``_sync_id``-matched instances."""
    room, st = _resolve_state(game_runner)
    if st is None:
        return

    session = st.get("session")
    if session is not None:
        session.pump_before_step()
        _apply_session_state(game_runner, session)
        if session.mode == "host":
            _apply_host_own_state(st, session)
        else:
            _apply_ghosts(game_runner, st, session)
            _apply_synced_local(game_runner, st, session)
        return

    if st.get("mode") != "client":
        return
    client = st.get("client")
    if client is None:
        return

    msg = client.poll()
    if not msg or msg.get("t") != "snap":
        return

    by_id = {}
    for inst in room.instances:
        sid = getattr(inst, "_sync_id", None)
        if sid is not None:
            by_id[sid] = inst

    for row in msg.get("i", ()):
        try:
            sid, x, y, rot, frame, vis = row
        except (TypeError, ValueError):
            continue
        inst = by_id.get(sid)
        if inst is None:
            continue
        inst.x = x
        inst.y = y
        inst.rotation = rot
        inst.image_index = frame
        inst.visible = bool(vis)


def _frame_update_broadcast(game_runner):
    """after_update: send this frame's outbound network state.

    v2 session present -> pump it (host snapshot / client flush). Otherwise
    the v1 spectator path: a host broadcasts every synced instance's
    position."""
    room, st = _resolve_state(game_runner)
    if st is None:
        return

    session = st.get("session")
    if session is not None:
        if session.mode == "host":
            session.push_local_instances(_collect_synced_rows(room, st))
        else:
            _send_owned(st, session)
        session.pump_after_update()
        return

    if st.get("mode") != "host":
        return
    net_host = st.get("host")
    if net_host is None:
        return

    rows = []
    for inst in room.instances:
        sid = getattr(inst, "_sync_id", None)
        if sid is None:
            continue
        rows.append((sid, inst.x, inst.y, inst.rotation, inst.image_index, bool(inst.visible)))
    net_host.broadcast_snapshot(rows)
