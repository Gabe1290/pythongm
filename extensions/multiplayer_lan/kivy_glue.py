"""LAN multiplayer CLIENT for the Kivy (Android/iOS) export.

Shipped into the game as ``mp_lan/glue.py`` beside the desktop session code
(``mp_lan/session.py`` and friends, byte for byte -- see export_kivy.py), so the
phone speaks exactly the desktop protocol over raw TCP.

Scope, like the HTML5 export (extensions/multiplayer_lan/export_html5.js): a
phone can JOIN a desktop-hosted game and take part in Tier A (shared variables,
custom messages, identity, the lifecycle events) and VIEW the host's networked
instances (ghosts, interpolated). It cannot host (no listening socket on a
phone), and it cannot own a synced instance, so ``host_game``,
``start_networked_game``, ``network_spawn``, ``sync_instance``,
``set_instance_owner``, ``bind_network_input`` and ``set_sync_rate`` warn once
and do nothing, and ``is_instance_owner`` / ``remote_input`` are false while a
session is running.

This module is pure Python and duck-typed against the Kivy scene (``instances``,
``create_instance``, ``destroy_instance``, ``room_height``) so it is testable
without Kivy. The game's globals live in ``main`` (``get_global``/``set_global``).
"""

import logging

log = logging.getLogger("mp_lan")

_session = None
_known = {}          # nid -> object name, every ghost the host has told us about
_ghosts = {}         # nid -> live instance in the CURRENT scene
_scene = None        # the scene _ghosts belong to
_warned = set()

# Identity globals this module owns (cleared again by leave_game).
NETWORK_GLOBALS = (
    "player_id", "player_count", "network_role", "is_host", "is_client",
    "network_connected", "network_event", "network_data", "network_sender",
    "network_player_name",
)

# Instance attributes a replicated var must never overwrite: anything the
# engine's own instance already has is refused (see _engine_attrs).
_GHOST_VAR_TYPES = (int, float, str, bool)


def _main():
    return __import__("main")


def _set_global(name, value):
    _main().set_global(name, value)


def _warn_once(name, why):
    if name in _warned:
        return
    _warned.add(name)
    msg = "multiplayer: %s is not available on this export (%s)." % (name, why)
    log.warning(msg)
    try:
        _main()._log(msg)
    except Exception:
        pass


def unsupported(name):
    """Actions a phone cannot do: say so once, then do nothing."""
    if name in ("host_game", "start_networked_game", "set_network_mode"):
        _warn_once(name, "a phone cannot host a game; host from a desktop export")
    else:
        _warn_once(name, "a phone can view other players' networked instances "
                         "but cannot register or own one")


# -- lifecycle -------------------------------------------------------------------

def join(host, port, player_name):
    """join_game: connect to a desktop host over TCP. Never raises."""
    global _session
    if _session is not None:
        return
    host = str(host or "").strip() or "127.0.0.1"
    if host == "auto":
        _warn_once("join_game(host='auto')",
                   "LAN discovery is not available on a phone; pass the host's address")
        return
    from .session import NetworkSession
    from .state import DEFAULT_PORT
    try:
        port = int(float(port))
    except (TypeError, ValueError):
        port = DEFAULT_PORT
    session = NetworkSession(mode="client", host=host, port=port,
                             player_name=str(player_name or "").strip() or "Joueur")
    try:
        session.start()
    except OSError as exc:
        log.warning("multiplayer: could not connect to %s:%s: %s", host, port, exc)
        try:
            session.close()
        except Exception:
            pass
        try:
            _main()._log("multiplayer: could not connect to %s:%s (%s)" % (host, port, exc))
        except Exception:
            pass
        return
    _session = session


def leave(scene=None):
    """leave_game: close the session, drop the ghosts, clear the identity globals."""
    global _session
    s, _session = _session, None
    if s is not None:
        try:
            s.close()
        except Exception:
            pass
    _destroy_ghosts(scene or _scene)
    _known.clear()
    try:
        g = _main().get_game_app().globals
        for key in NETWORK_GLOBALS:
            g.pop(key, None)
    except Exception:
        pass


def active():
    return _session is not None


# -- Tier A ----------------------------------------------------------------------

def set_shared(name, value):
    if _session is not None and name:
        _session.set_shared(str(name), value)


def get_shared_into(name, into):
    if not into:
        return
    value = _session.get_shared(str(name), 0) if _session is not None else 0
    _set_global(str(into), value)


def send_message(event, data, target):
    if _session is not None and event:
        _session.send_message(str(event), data, target if target in ("all", "host") else "all")


def is_owner(instance):
    """is_instance_owner: with no session you own everything (so control logic
    still runs single-player); in a session a phone owns nothing."""
    return _session is None


# -- per-frame ---------------------------------------------------------------------

def update(scene):
    """Pump the connection, mirror state into globals, fire the lifecycle events
    on the scene's instances, and keep the ghosts in step. Called once a frame
    from the scene's extension hook; a no-op until join_game."""
    s = _session
    if s is None:
        return
    s.pump_before_step()
    _apply_state(scene, s)
    _apply_ghosts(scene, s)
    s.pump_after_update()


def _apply_state(scene, s):
    connected = (not s.connection_lost) and s.player_id >= 0
    _set_global("player_id", s.player_id)
    _set_global("player_count", s.player_count)
    _set_global("network_role", s.mode)
    _set_global("is_host", 0)
    _set_global("is_client", 1)
    _set_global("network_connected", 1 if connected else 0)
    for key, val in s.shared.items():
        _set_global(key, val)
    for event in s.take_events():
        name = event[0]
        if name == "network_message":
            _, ev_name, data, sender = event
            _set_global("network_event", ev_name)
            _set_global("network_data", data)
            _set_global("network_sender", sender)
        elif name in ("player_joined", "player_left"):
            _, slot, pname = event
            _set_global("network_sender", slot)
            _set_global("network_player_name", pname)
        elif name == "connection_lost":
            _set_global("network_connected", 0)
            _destroy_ghosts(scene)        # a lost host never sends another snapshot
        _fire(scene, name)


def _fire(scene, event_name):
    for inst in list(getattr(scene, "instances", ())):
        handler = getattr(inst, "on_" + event_name, None)
        if handler is None:
            continue
        try:
            handler()
        except Exception as exc:
            log.warning("multiplayer: %s handler raised: %s", event_name, exc)


# -- ghosts --------------------------------------------------------------------------

def _destroy_ghosts(scene):
    for inst in list(_ghosts.values()):
        try:
            if scene is not None:
                scene.destroy_instance(inst)
        except Exception:
            pass
    _ghosts.clear()


def _engine_attrs(inst):
    """Names a replicated var must not overwrite: whatever the freshly built
    instance already has (its engine attributes) plus every class-level name
    (properties like x/y/pos, methods)."""
    return set(vars(inst)) | set(dir(type(inst)))


def _safe_var_key(inst, key):
    return (isinstance(key, str) and key.isidentifier() and not key.startswith("_")
            and key not in getattr(inst, "_mp_engine_attrs", ()))


def _spawn(scene, nid, obj):
    inst = scene.create_instance(obj, 0, 0)
    if inst is None:
        log.warning("multiplayer: ghost object %r is not in the project", obj)
        return None
    # A ghost is driven by snapshots, never by its own create event.
    pending = getattr(scene, "_pending_creates", None)
    if pending is not None and inst in pending:
        pending.remove(inst)
    inst._net_ghost = nid
    inst._mp_engine_attrs = _engine_attrs(inst)
    return inst


def _finite(value, default):
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return f if f == f and f not in (float("inf"), float("-inf")) else default


def _apply_ghosts(scene, s):
    global _scene
    if scene is not _scene:                      # a room change: rebuild from what we know
        _ghosts.clear()
        _scene = scene
        for nid, obj in _known.items():
            inst = _spawn(scene, nid, obj)
            if inst is not None:
                _ghosts[nid] = inst
    creates, destroys = s.take_ghost_changes()
    for nid, obj, _x, _y in creates:
        _known[nid] = obj
        if nid not in _ghosts:
            inst = _spawn(scene, nid, obj)
            if inst is not None:
                _ghosts[nid] = inst
    for nid in destroys:
        _known.pop(nid, None)
        inst = _ghosts.pop(nid, None)
        if inst is not None:
            scene.destroy_instance(inst)
    live = set(map(id, getattr(scene, "instances", ())))
    for nid in list(_ghosts):
        inst = _ghosts[nid]
        if id(inst) not in live:                 # destroyed by the game itself
            del _ghosts[nid]
            continue
        pos = s.sample_ghost(nid)
        if pos is None:
            continue
        gx, gy, _rot, frame, visible = pos
        # Wire coordinates are room coordinates (y down); Kivy's are y-up and
        # anchored at the sprite's bottom-left.
        height = _finite(getattr(inst, "image_height", 0), 0.0)
        inst.x = _finite(gx, inst.x)
        inst.y = scene.room_height - _finite(gy, 0.0) - height
        inst.image_index = _finite(frame, getattr(inst, "image_index", 0.0))
        inst.visible = bool(visible)
        for key, val in s.ghost_vars(nid).items():
            if isinstance(val, _GHOST_VAR_TYPES) and _safe_var_key(inst, key):
                setattr(inst, key, val)
