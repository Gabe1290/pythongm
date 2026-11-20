"""LAN multiplayer CLIENT for the Kivy (Android/iOS) export.

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
client. It cannot host (no listening socket on a phone), so ``host_game``,
``start_networked_game`` and ``network_spawn`` warn once and do nothing; ``remote_input``
is host-side and always false.

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
    """Actions a phone cannot do: say so once, then do nothing."""
    if name in ("host_game", "start_networked_game", "set_network_mode"):
        _warn_once(name, "a phone cannot host a game; host from a desktop export")
    else:
        _warn_once(name, "only the host creates networked instances; a phone plays the avatar "
                         "the host gave it")


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
    if _interp_ms is not None:
        _session.set_sync_rate(20.0, _interp_ms)


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
    _known_pos.clear()
    _local.clear()
    _synced_local.clear()
    _sync_ord.clear()
    global _last_input, _last_own_at, _last_input_at
    _last_input = None
    _last_own_at = _last_input_at = 0.0
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
        _sync_ord.clear()
        _sync_scene = scene
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
    _synced_local[nid] = inst


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
