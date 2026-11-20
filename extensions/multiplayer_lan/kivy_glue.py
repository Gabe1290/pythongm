"""LAN multiplayer for the Kivy (Android/iOS) export: a CLIENT, and a HOST.

Shipped into the game as ``mp_lan/glue.py`` beside the desktop session code
(``mp_lan/session.py`` and friends, byte for byte -- see export_kivy.py), so the
phone speaks exactly the desktop protocol over raw TCP.

Scope, like the HTML5 export (extensions/multiplayer_lan/export_html5.js): a
phone can JOIN a desktop-hosted game, take part in Tier A (shared variables,
custom messages, identity, the lifecycle events), VIEW the host's networked
instances (ghosts, interpolated) and PLAY the avatar the host assigned to it: an
instance whose snapshot owner is this player is promoted from a puppet to a
locally simulated avatar (its own events run here), and every frame this module
reports its state up to the host ("own" frames) and the held named inputs
("input" frames, arrows and space by default, ``bind_network_input`` to change),
exactly as the desktop client does. ``is_instance_owner`` is true for that
avatar, and for everything while there is no session. It can also take part in an
instance PLACED IN THE ROOM and marked with ``sync_instance`` (every machine loads the same
room, so the same instance gets the same network id ``<object>#<ordinal>`` everywhere): it
follows the host's copy unless the host gave it to this player, in which case it runs here
and is reported up. ``set_instance_owner`` is the host's decision; on a phone it only sets
the local ``_net_owner``, which the next snapshot overrides, exactly as on the desktop
client.

A phone can also HOST (a device can listen on a socket, so the desktop's own host session is used
as it is): ``host_game`` starts it, ``start_networked_game`` ends the waiting room,
``network_spawn`` creates a networked instance for everyone (with an owner), ``sync_instance`` marks
a room-placed instance as host-owned, ``set_instance_owner`` hands one to a player, and
``remote_input`` asks what a player is holding. What a phone does NOT have is the desktop's waiting-
room screen and the discovery beacon (``show_lobby`` is ignored; a joiner types the host's address,
which the game can read from the global ``host_address``), and phones on a school's guest Wi-Fi are
often isolated from each other, so hosting there may be unreachable. ``set_network_mode`` is the
older spectator mode (the host's positions are copied to a joiner's instances).

This module is pure Python and duck-typed against the Kivy scene (``instances``,
``create_instance``, ``destroy_instance``, ``room_height``) so it is testable
without Kivy. The game's globals live in ``main`` (``get_global``/``set_global``).
"""

import logging
import time

log = logging.getLogger("mp_lan")

_session = None
_known = {}          # nid -> object name, every ghost the host has told us about
_known_pos = {}      # nid -> (x, y) the host last placed it at (room coordinates)
_ghosts = {}         # nid -> live instance in the CURRENT scene
_local = set()       # nids of _ghosts this player owns (promoted to avatars)
_scene = None        # the scene _ghosts belong to
_synced_local = {}   # nid -> room-placed instance registered by sync_instance in _sync_scene
_sync_ord = {}       # object name -> how many sync_instance calls so far in _sync_scene
_sync_scene = None   # the scene the two above belong to
_host_synced = {}    # HOST: nid -> instance (sync_instance / network_spawn) replicated to every client
_v1 = None           # the older spectator mode (set_network_mode): {"mode", "net", "scene"}
_warned = set()
_interp_ms = None    # set_sync_rate's interpolation delay, applied to every session

# Named inputs reported to the host: name -> key name. Arrows + space by default.
_bindings = {"left": "left", "right": "right", "up": "up", "down": "down", "space": "space"}
_last_input = None

# The host drops a client that sends more than ~60 frames a second (framing.RateLimiter), and a
# scene's update runs once per display frame -- 90 or 120 a second on a fast phone. So the
# reports are paced here, not per frame: own state at most 30 times a second, and the held
# inputs on every change PLUS a refresh every half second (a change sent just as the host
# drops a frame would otherwise leave an input stuck until the next change).
_OWN_EVERY = 1.0 / 30.0
_INPUT_REFRESH = 0.5
_last_own_at = 0.0
_last_input_at = 0.0

# Kivy keycodes by key name (the generator's _KIVY_KEY_NAME_TO_CODE); a single
# letter or digit is its ord().
_KEYCODES = {"right": 275, "left": 276, "up": 273, "down": 274, "space": 32,
             "enter": 13, "return": 13, "escape": 27, "backspace": 8, "tab": 9}

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
    """Kept for an action added later that a phone cannot do: say so once, then do nothing."""
    _warn_once(name, "a phone cannot do this")


# -- lifecycle -------------------------------------------------------------------

def join(host, port, player_name):
    """join_game: connect to a desktop host over TCP. Never raises."""
    global _session
    if _session is not None or _v1 is not None:
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
    if _interp_ms is not None:
        _session.set_sync_rate(20.0, _interp_ms)


def leave(scene=None):
    """leave_game: close the session, drop the ghosts, clear the identity globals."""
    global _session, _v1
    s, _session = _session, None
    if s is not None:
        try:
            s.close()
        except Exception:
            pass
    v1, _v1 = _v1, None
    if v1 is not None:
        try:
            v1["net"].close()
        except Exception:
            pass
    _host_synced.clear()
    _destroy_ghosts(scene or _scene)
    _known.clear()
    _known_pos.clear()
    _local.clear()
    _synced_local.clear()
    _sync_ord.clear()
    global _last_input, _last_own_at, _last_input_at
    _last_input = None
    _last_own_at = _last_input_at = 0.0
    try:
        g = _main().get_game_app().globals
        for key in NETWORK_GLOBALS + ("host_address",):
            g.pop(key, None)
    except Exception:
        pass


def active():
    return _session is not None or _v1 is not None


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
    still runs single-player); in a session only the avatar the host assigned to
    this player is yours (anything else has no owner, or another player's)."""
    if _session is None:
        return True
    owner = getattr(instance, "_net_owner", None)
    return owner is not None and owner == _session.player_id


def sync_instance(inst, names=""):
    """sync_instance: mark a ROOM-PLACED instance as networked. Its id is ``<object>#<ordinal>`` --
    the ordinal counted per room per object in the order this is called -- so every machine that
    loads the same room and runs its create events in the same order agrees on it with no
    negotiation. It follows the host's copy unless this player owns it. With no session it does
    nothing (as on desktop): join first, then enter the room."""
    global _sync_scene
    if _session is None:
        return
    scene = getattr(inst, "scene", None)
    if scene is not _sync_scene:                 # a new room: its own registry and ordinals
        _synced_local.clear()
        _host_synced.clear()
        _sync_ord.clear()
        _sync_scene = scene
    registry = _host_synced if _session.mode == "host" else _synced_local
    name = str(getattr(inst, "object_name", "") or inst.__class__.__name__)
    nid = getattr(inst, "_net_id", None)
    if not nid:
        nid = "%s#%d" % (name, _sync_ord.get(name, 0))
        _sync_ord[name] = _sync_ord.get(name, 0) + 1
    inst._net_id = nid
    if getattr(inst, "_net_owner", None) is None:
        inst._net_owner = 0                      # the host, until a snapshot says otherwise
    listed = [n.strip() for n in str(names or "").split(",") if n.strip()]
    if listed:
        inst._net_sync_vars = listed
    registry[nid] = inst
    if _session.mode == "host":
        return


def set_instance_owner(inst, player):
    """set_instance_owner: the host decides who drives an instance, so on a phone this only sets the
    local `_net_owner` -- which the next snapshot overrides -- exactly as on the desktop client."""
    if _session is None:
        return
    try:
        inst._net_owner = int(float(player))
    except (TypeError, ValueError):
        inst._net_owner = 0


def bind(name, key):
    """bind_network_input: report the named input ``name`` while ``key`` is held."""
    name = str(name or "").strip()
    if not name:
        return
    key = str(key or "").strip().lower()
    if key.startswith("k_"):
        key = key[2:]
    _bindings[name] = {"ctrl": "control", "esc": "escape"}.get(key, key)


def set_sync_rate(interp_ms):
    """set_sync_rate: only the interpolation delay matters to a client."""
    global _interp_ms
    try:
        ms = float(interp_ms)
    except (TypeError, ValueError):
        return
    if ms >= 0:
        _interp_ms = ms
        if _session is not None:
            _session.set_sync_rate(20.0, ms)


def _held_inputs(scene):
    """The bound named inputs whose key is held right now (scene.keys_pressed is
    a dict keyed by raw Kivy keycode)."""
    keys = getattr(scene, "keys_pressed", None) or {}
    held = []
    for name, key in _bindings.items():
        code = _KEYCODES.get(key)
        if code is None and len(key) == 1 and (key.isalpha() or key.isdigit()):
            code = ord(key)
        if code is not None and keys.get(code, False):
            held.append(name)
    return sorted(held)


# -- per-frame ---------------------------------------------------------------------

def update(scene):
    """Pump the connection, mirror state into globals, fire the lifecycle events
    on the scene's instances, and keep the ghosts in step. Called once a frame
    from the scene's extension hook; a no-op until join_game."""
    s = _session
    if s is None:
        if _v1 is not None:
            _update_v1(scene)
        return
    s.pump_before_step()
    _apply_state(scene, s)
    if s.mode == "host":
        _apply_host_own_state(scene, s)
        _push_host_state(scene, s)
        s.pump_after_update()                    # (the snapshot goes out here)
        return
    _apply_ghosts(scene, s)
    s.pump_after_update()


def _apply_state(scene, s):
    hosting = s.mode == "host"
    connected = (not s.connection_lost) and (hosting or s.player_id >= 0)
    _set_global("player_id", s.player_id)
    _set_global("player_count", s.player_count)
    _set_global("network_role", s.mode)
    _set_global("is_host", 1 if hosting else 0)
    _set_global("is_client", 0 if hosting else 1)
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
            _destroy_ghosts(scene, keep_local=True)
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

def _destroy_ghosts(scene, keep_local=False):
    """Remove the puppets. keep_local: a lost host never sends another snapshot,
    but this player's own avatar keeps running single player."""
    for nid, inst in list(_ghosts.items()):
        if keep_local and nid in _local:
            continue
        try:
            if scene is not None:
                scene.destroy_instance(inst)
        except Exception:
            pass
        del _ghosts[nid]
        _local.discard(nid)


def _engine_attrs(inst):
    """Names a replicated var must not overwrite: whatever the freshly built
    instance already has (its engine attributes) plus every class-level name
    (properties like x/y/pos, methods)."""
    return set(vars(inst)) | set(dir(type(inst)))


def _safe_var_key(inst, key):
    return (isinstance(key, str) and key.isidentifier() and not key.startswith("_")
            and key not in getattr(inst, "_mp_engine_attrs", ()))


def _place(scene, inst, gx, gy):
    """Wire coordinates are room coordinates (y down); Kivy's are y-up and
    anchored at the sprite's bottom-left."""
    height = _finite(getattr(inst, "image_height", 0), 0.0)
    inst.x = _finite(gx, inst.x)
    inst.y = scene.room_height - _finite(gy, 0.0) - height


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
    x, y = _known_pos.get(nid, (0, 0))
    _place(scene, inst, x, y)             # promoted at once must not start at the corner
    return inst


def _finite(value, default):
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return f if f == f and f not in (float("inf"), float("-inf")) else default


def _own_row(scene, nid, inst):
    """The row reporting an instance this player owns, in room coordinates (y down)."""
    height = _finite(getattr(inst, "image_height", 0), 0.0)
    row = {
        "nid": nid, "x": _finite(inst.x, 0.0),
        "y": scene.room_height - _finite(inst.y, 0.0) - height,
        "r": 0, "f": _finite(getattr(inst, "image_index", 0.0), 0.0),
        "v": bool(getattr(inst, "visible", True)),
    }
    names = getattr(inst, "_net_sync_vars", None)
    if names:
        values = {}
        for name in names:
            value = getattr(inst, name, None)
            if isinstance(value, _GHOST_VAR_TYPES) and (not isinstance(value, float) or value == value):
                values[name] = value
        if values:
            row["vars"] = values
    return row


def _apply_synced_local(scene, s, connected, own_rows):
    """Room-placed instances registered by sync_instance: mine (the host gave it to this player)
    runs here and is reported up; anyone else's follows the interpolated snapshot."""
    if scene is not _sync_scene:
        return
    live = set(map(id, getattr(scene, "instances", ())))
    for nid in list(_synced_local):
        inst = _synced_local[nid]
        if id(inst) not in live:
            del _synced_local[nid]
            continue
        owner = s.ghost_owner(nid)
        inst._net_owner = 0 if owner is None else owner
        if connected and owner == s.player_id:
            own_rows.append(_own_row(scene, nid, inst))
            continue
        pos = s.sample_ghost(nid)
        if pos is None:
            continue
        gx, gy, _rot, frame, visible = pos
        _place(scene, inst, gx, gy)
        inst.image_index = _finite(frame, getattr(inst, "image_index", 0.0))
        inst.visible = bool(visible)
        allowed = getattr(inst, "_net_sync_vars", None) or ()
        for key, val in s.ghost_vars(nid).items():
            # only the names the author listed, and never anything the class itself defines
            if (key in allowed and isinstance(val, _GHOST_VAR_TYPES) and not key.startswith("_")
                    and not hasattr(type(inst), key)):
                setattr(inst, key, val)


def _apply_ghosts(scene, s):
    global _scene, _last_input, _last_own_at, _last_input_at
    if scene is not _scene:                      # a room change: rebuild from what we know
        _ghosts.clear()
        _local.clear()
        _scene = scene
        for nid, obj in _known.items():
            if nid in _synced_local:             # the room's own instance stands in for it
                continue
            inst = _spawn(scene, nid, obj)
            if inst is not None:
                _ghosts[nid] = inst
    creates, destroys = s.take_ghost_changes()
    for nid, obj, x, y in creates:
        _known[nid] = obj
        _known_pos[nid] = (x, y)
        if nid not in _ghosts and nid not in _synced_local:
            inst = _spawn(scene, nid, obj)
            if inst is not None:
                _ghosts[nid] = inst
    for nid in destroys:
        _known.pop(nid, None)
        _known_pos.pop(nid, None)
        _local.discard(nid)
        inst = _ghosts.pop(nid, None)
        if inst is not None:
            scene.destroy_instance(inst)
    live = set(map(id, getattr(scene, "instances", ())))
    connected = (not s.connection_lost) and s.player_id >= 0
    own_rows = []
    for nid in list(_ghosts):
        inst = _ghosts[nid]
        if id(inst) not in live:                 # destroyed by the game itself
            del _ghosts[nid]
            _local.discard(nid)
            continue
        owner = s.ghost_owner(nid)
        inst._net_owner = 0 if owner is None else owner
        if connected and owner == s.player_id:
            # Mine: promoted from a puppet to a locally simulated avatar. Its own
            # events move it; this device is the authority for it now.
            _local.add(nid)
            own_rows.append(_own_row(scene, nid, inst))
            continue
        if nid in _local:
            continue                             # lost the host: still mine, keep it running
        pos = s.sample_ghost(nid)
        if pos is None:
            continue
        gx, gy, _rot, frame, visible = pos
        _place(scene, inst, gx, gy)
        inst.image_index = _finite(frame, getattr(inst, "image_index", 0.0))
        inst.visible = bool(visible)
        for key, val in s.ghost_vars(nid).items():
            if isinstance(val, _GHOST_VAR_TYPES) and _safe_var_key(inst, key):
                setattr(inst, key, val)
    _apply_synced_local(scene, s, connected, own_rows)
    if connected:
        now = time.monotonic()
        if now - _last_own_at >= _OWN_EVERY:
            _last_own_at = now
            s.push_own_instances(own_rows)
        held = _held_inputs(scene)
        key = ",".join(held)
        if key != _last_input or now - _last_input_at >= _INPUT_REFRESH:
            _last_input, _last_input_at = key, now
            s._last_input_sent = None            # the session dedups; a refresh must really go out
            s.send_input(held)


# -- hosting ------------------------------------------------------------------------------

def _lan_address(port):
    """This device's address on the local network, as "ip:port" (the address a joiner types)."""
    import socket
    ip = "127.0.0.1"
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("10.255.255.255", 1))     # no packet is sent; it only picks the outgoing interface
        ip = probe.getsockname()[0]
    except OSError:
        pass
    finally:
        probe.close()
    return "%s:%d" % (ip, port)


def host(port, player_name, max_players, show_lobby=False):
    """host_game: listen for players. Never raises (a busy port is logged and the game goes on)."""
    global _session
    if _session is not None or _v1 is not None:
        return
    from .session import NetworkSession
    from .state import DEFAULT_PORT
    try:
        port = int(float(port))
    except (TypeError, ValueError):
        port = DEFAULT_PORT
    try:
        max_players = int(float(max_players))
    except (TypeError, ValueError):
        max_players = 8
    session = NetworkSession(mode="host", port=port, max_players=max_players,
                             player_name=str(player_name or "").strip() or "Joueur")
    try:
        session.start()
    except OSError as exc:
        log.warning("multiplayer: could not host on port %s: %s", port, exc)
        try:
            session.close()
        except Exception:
            pass
        try:
            _main()._log("multiplayer: could not host on port %s (%s)" % (port, exc))
        except Exception:
            pass
        return
    if show_lobby:
        _warn_once("lobby", "the waiting-room screen is desktop-only; the game starts hosting at once "
                            "(read the global host_address to show players where to join)")
    _session = session
    _host_synced.clear()
    if _interp_ms is not None:
        _session.set_sync_rate(20.0, _interp_ms)
    try:
        _set_global("host_address", _lan_address(session.bound_port))
    except Exception:
        pass


def start_networked_game():
    """start_networked_game: end the waiting room (host only): everyone gets network_game_started."""
    if _session is not None and _session.mode == "host":
        _session.start_game()


def network_spawn(inst, object_name, gm_x, gm_y, owner):
    """network_spawn (host only): create an instance of `object_name` at the author's position and
    replicate it to every client, owned by player `owner` (0 = the host). A no-op for a client, as
    on desktop."""
    global _sync_scene
    if _session is None or _session.mode != "host" or not object_name:
        return None
    scene = getattr(inst, "scene", None)
    if scene is not _sync_scene:
        _synced_local.clear()
        _host_synced.clear()
        _sync_ord.clear()
        _sync_scene = scene
    new = inst._create_gm(str(object_name), gm_x, gm_y)
    if new is None:
        return None
    nid = _session.next_netid()
    new._net_id = nid
    try:
        new._net_owner = int(float(owner))
    except (TypeError, ValueError):
        new._net_owner = 0
    _host_synced[nid] = new
    return new


def remote_input(player, name):
    """remote_input (host only): is `player` holding the named input? False everywhere else."""
    if _session is None or _session.mode != "host":
        return False
    return bool(_session.remote_input(player, name))


def _host_row(scene, nid, inst):
    height = _finite(getattr(inst, "image_height", 0), 0.0)
    row = {
        "nid": nid, "o": str(getattr(inst, "object_name", "") or inst.__class__.__name__),
        "x": _finite(inst.x, 0.0), "y": scene.room_height - _finite(inst.y, 0.0) - height,
        "r": 0, "f": _finite(getattr(inst, "image_index", 0.0), 0.0),
        "v": bool(getattr(inst, "visible", True)),
        "own": getattr(inst, "_net_owner", 0) or 0,
    }
    names = getattr(inst, "_net_sync_vars", None)
    if names:
        values = {}
        for name in names:
            value = getattr(inst, name, None)
            if isinstance(value, _GHOST_VAR_TYPES) and (not isinstance(value, float) or value == value):
                values[name] = value
        if values:
            row["vars"] = values
    return row


def _push_host_state(scene, s):
    """Host, every frame: this frame's replicated instances go into the next snapshot, and the held
    named inputs become player 0's (so remote_input(0, ...) works like for a client)."""
    live = set(map(id, getattr(scene, "instances", ())))
    rows = []
    for nid in list(_host_synced):
        inst = _host_synced[nid]
        if id(inst) not in live:
            del _host_synced[nid]
            continue
        rows.append(_host_row(scene, nid, inst))
    s.push_local_instances(rows)
    s.set_local_input(_held_inputs(scene))
    try:
        _set_global("host_address", _lan_address(s.bound_port))
    except Exception:
        pass


def _apply_host_own_state(scene, s):
    """Host: fold each client's reported state for the instances IT owns into the host's copy, so the
    host sim and the outgoing snapshot agree. A claim is accepted only from the recorded owner."""
    for nid, row in s.take_own_state().items():
        inst = _host_synced.get(nid)
        if inst is None or getattr(inst, "_net_owner", 0) != row.get("_from"):
            continue                              # a client cannot take an instance it does not own
        height = _finite(getattr(inst, "image_height", 0), 0.0)
        inst.x = _finite(row.get("x"), inst.x)
        inst.y = scene.room_height - _finite(row.get("y"), 0.0) - height
        inst.image_index = _finite(row.get("f"), getattr(inst, "image_index", 0.0))
        inst.visible = bool(row.get("v", getattr(inst, "visible", True)))
        allowed = getattr(inst, "_net_sync_vars", None) or ()
        for key, val in (row.get("vars") or {}).items():
            if (key in allowed and isinstance(val, _GHOST_VAR_TYPES) and not key.startswith("_")
                    and not hasattr(type(inst), key)):
                setattr(inst, key, val)


# -- the older spectator mode (set_network_mode) ---------------------------------------------

def set_network_mode(mode, host_addr, port):
    """set_network_mode: the v1 spectator sync. A host broadcasts every instance's position; a joiner's
    instances (matched by their order in the room) copy it. Never raises."""
    global _v1
    if _session is not None or _v1 is not None:
        return
    mode = str(mode or "").strip().lower()
    if mode not in ("host", "client"):
        return
    from .network import NetworkClient, NetworkHost
    from .state import DEFAULT_PORT
    try:
        port = int(float(port))
    except (TypeError, ValueError):
        port = DEFAULT_PORT
    try:
        if mode == "host":
            net = NetworkHost(port=port)
            net.start()
        else:
            net = NetworkClient(str(host_addr or "").strip() or "127.0.0.1", port=port)
            net.connect()
    except OSError as exc:
        log.warning("multiplayer: could not start %s mode on port %s: %s", mode, port, exc)
        return
    _v1 = {"mode": mode, "net": net, "scene": None}


def _update_v1(scene):
    v1 = _v1
    if v1["scene"] is not scene:                 # number the room's instances once: both sides load the same room
        v1["scene"] = scene
        for index, inst in enumerate(getattr(scene, "instances", ())):
            inst._sync_id = index
    if v1["mode"] == "host":
        rows = []
        for inst in getattr(scene, "instances", ()):
            sid = getattr(inst, "_sync_id", None)
            if sid is None:
                continue
            height = _finite(getattr(inst, "image_height", 0), 0.0)
            rows.append((sid, _finite(inst.x, 0.0), scene.room_height - _finite(inst.y, 0.0) - height,
                         0, _finite(getattr(inst, "image_index", 0.0), 0.0),
                         bool(getattr(inst, "visible", True))))
        v1["net"].broadcast_snapshot(rows)
        return
    msg = v1["net"].poll()
    if not msg or msg.get("t") != "snap":
        return
    by_id = {}
    for inst in getattr(scene, "instances", ()):
        sid = getattr(inst, "_sync_id", None)
        if sid is not None:
            by_id[sid] = inst
    for row in msg.get("i", ()):
        try:
            sid, x, y, _rot, frame, visible = row
        except (TypeError, ValueError):
            continue
        inst = by_id.get(sid)
        if inst is None:
            continue
        _place(scene, inst, x, y)
        inst.image_index = _finite(frame, getattr(inst, "image_index", 0.0))
        inst.visible = bool(visible)

