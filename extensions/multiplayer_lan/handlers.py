#!/usr/bin/env python3
"""Runtime handlers for the LAN multiplayer extension.

Mirrors extensions/block_world/handlers.py: a plugin's action handlers run
as methods of a PluginExecutor instance, reaching the engine through
instance.action_executor (the plugins/audio_actions pattern), not through
ActionExecutor directly. The two frame-update functions are plain
``(game_runner) -> None`` callables (see runtime/extension_hooks.py),
registered via PLUGIN_FRAME_UPDATES in __init__.py -- they are NOT
PluginExecutor methods, since the frame-update hook contract takes only
the game_runner, not an acting instance.
"""

import os

from .network import NetworkClient, NetworkHost
from .state import DEFAULT_PORT, multiplayer_state, peek_multiplayer

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
    """The actual connect/listen step, shared by the action handler and
    the env-var auto-init fallback. Mutates room's multiplayer state in
    place. Never raises -- a failed connect/listen degrades to "no
    networking this session" rather than crashing the game (matches
    render_room/run_frame_updates' own "a broken extension must not take
    the game down" contract elsewhere in this codebase)."""
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
        # Bind/connect failure (port in use, host unreachable, ...) --
        # leave this room's multiplayer state disabled rather than crash.
        st["mode"] = None
        st["host"] = None
        st["client"] = None
        return

    st["enabled"] = True


class PluginExecutor:
    """Handles execution of the LAN multiplayer actions."""

    @staticmethod
    def _executor(instance):
        return getattr(instance, "action_executor", None)

    def execute_set_network_mode_action(self, instance, parameters):
        """Configure this room for LAN multiplayer -- host or client.

        Mirrors the stashed prototype's GameRunner.set_network_mode +
        _init_network, but scoped to the room's own extension_state rather
        than new GameRunner attributes (see state.py's docstring on why).
        A no-op if this room already has multiplayer configured (can't
        switch host/client mode mid-session).

        Parameters:
            mode: "host" or "client"
            host: the host's address (client mode only; ignored for host)
            port: TCP port (default state.DEFAULT_PORT)
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room

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


def _frame_update_apply_inbound(game_runner):
    """Client: drain pending snapshots and apply the most recent one to
    matching instances. Phase "before_step" -- runs before Step events so
    they see this frame's fresh network state, mirroring the stashed
    prototype's own ordering. No-op for a host, or a room with no
    multiplayer state (checked without CREATING any -- this hook runs
    every frame for every room, multiplayer or not)."""
    room = getattr(game_runner, "current_room", None)
    if room is None:
        return

    st = peek_multiplayer(room)
    if st is None:
        env = _env_config()
        if env is not None:
            mode, host, port = env
            _start_network(room, mode, host, port)
            st = peek_multiplayer(room)

    if st is None or st.get("mode") != "client":
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
    """Host: snapshot all synced instances and broadcast. Phase
    "after_update" -- runs after movement/collision/destroy cleanup, so
    the snapshot reflects this frame's settled state. No-op for a client,
    or a room with no multiplayer state."""
    room = getattr(game_runner, "current_room", None)
    if room is None:
        return

    st = peek_multiplayer(room)
    if st is None:
        env = _env_config()
        if env is not None:
            mode, host, port = env
            _start_network(room, mode, host, port)
            st = peek_multiplayer(room)

    if st is None or st.get("mode") != "host":
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
