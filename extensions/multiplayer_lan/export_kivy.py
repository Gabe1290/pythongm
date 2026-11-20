"""LAN multiplayer on the Kivy (Android/iOS) export.

A phone can JOIN a desktop-hosted game (Tier A: shared variables, messages, identity, the
Reseau events; the host's networked instances as interpolated ghosts; the avatar the host assigned,
with own/input frames and named input; room-placed instances marked with sync_instance) and can
HOST one (host_game, start_networked_game, network_spawn, host-owned sync_instance,
set_instance_owner, remote_input, and the older set_network_mode). Not on a phone: the waiting-room
screen and the discovery beacon -- see kivy_glue.py. The desktop session code is shipped verbatim
as the ``mp_lan`` package, so the wire protocol is the host's own.

The extension loader ``exec``s this file without ``__file__``, so everything here
is plain data.
"""

# {path under the game folder: source path relative to this extension's folder}
SUPPORT_FILES = {
    "mp_lan/__init__.py": "kivy_pkg_init.py",
    "mp_lan/state.py": "state.py",
    "mp_lan/framing.py": "framing.py",
    "mp_lan/network.py": "network.py",
    "mp_lan/replication.py": "replication.py",
    "mp_lan/ws_transport.py": "ws_transport.py",
    "mp_lan/session.py": "session.py",
    "mp_lan/glue.py": "kivy_glue.py",
}


def _helpers():
    from export.Kivy.code_generator import _num_code, _value_code
    return _num_code, _value_code


def _raw(params, key, default=""):
    value = params.get(key, default)
    return str(value if value is not None else default).strip()


def _cg_join_game(gen, params, event_type):
    num, _ = _helpers()
    return ("from mp_lan.glue import join; "
            f"join({_raw(params, 'host', '127.0.0.1')!r}, {num(params.get('port'), 45782)}, "
            f"{_raw(params, 'player_name')!r})")


def _cg_leave_game(gen, params, event_type):
    return "from mp_lan.glue import leave; leave(self.scene)"


def _cg_set_shared_var(gen, params, event_type):
    _, value = _helpers()
    return ("from mp_lan.glue import set_shared; "
            f"set_shared({_raw(params, 'name')!r}, {value(params.get('value', 0))})")


def _cg_get_shared_var(gen, params, event_type):
    return ("from mp_lan.glue import get_shared_into; "
            f"get_shared_into({_raw(params, 'name')!r}, {_raw(params, 'into')!r})")


def _cg_send_network_message(gen, params, event_type):
    _, value = _helpers()
    data = params.get("data")
    expr = "None" if data is None or str(data).strip() == "" else value(data)
    target = _raw(params, "target", "all")
    return ("from mp_lan.glue import send_message; "
            f"send_message({_raw(params, 'event')!r}, {expr}, {target!r})")


def _cg_bind_network_input(gen, params, event_type):
    return ("from mp_lan.glue import bind; "
            f"bind({_raw(params, 'name')!r}, {_raw(params, 'key')!r})")


def _cg_set_sync_rate(gen, params, event_type):
    num, _ = _helpers()
    return f"from mp_lan.glue import set_sync_rate; set_sync_rate({num(params.get('interp_ms'), 100)})"


def _cg_sync_instance(gen, params, event_type):
    return ("from mp_lan.glue import sync_instance; "
            f"sync_instance(self, {_raw(params, 'vars')!r})")


def _cg_set_instance_owner(gen, params, event_type):
    num, _ = _helpers()
    return ("from mp_lan.glue import set_instance_owner; "
            f"set_instance_owner(self, {num(params.get('player'), 0)})")


def _truthy(value):
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "no")
    return bool(value)


def _cg_host_game(gen, params, event_type):
    num, _ = _helpers()
    return ("from mp_lan.glue import host; "
            f"host({num(params.get('port'), 45782)}, {_raw(params, 'player_name')!r}, "
            f"{num(params.get('max_players'), 8)}, {_truthy(params.get('show_lobby'))!r})")


def _cg_start_networked_game(gen, params, event_type):
    return "from mp_lan.glue import start_networked_game; start_networked_game()"


def _cg_set_network_mode(gen, params, event_type):
    num, _ = _helpers()
    return ("from mp_lan.glue import set_network_mode; "
            f"set_network_mode({_raw(params, 'mode')!r}, {_raw(params, 'host')!r}, "
            f"{num(params.get('port'), 45782)})")


def _cg_network_spawn(gen, params, event_type):
    num, _ = _helpers()
    x, y = num(params.get('x'), 0), num(params.get('y'), 0)
    if _truthy(params.get('relative')):
        x, y = f"self.x + {x}", f"self._gm_y() + {y}"            # the author's y: down from the top
    return ("from mp_lan.glue import network_spawn; "
            f"network_spawn(self, {_raw(params, 'object')!r}, {x}, {y}, {num(params.get('owner'), 0)})")


ACTION_CODEGEN = {
    "join_game": _cg_join_game,
    "leave_game": _cg_leave_game,
    "set_shared_var": _cg_set_shared_var,
    "get_shared_var": _cg_get_shared_var,
    "send_network_message": _cg_send_network_message,
    "bind_network_input": _cg_bind_network_input,
    "set_sync_rate": _cg_set_sync_rate,
    "sync_instance": _cg_sync_instance,
    "set_instance_owner": _cg_set_instance_owner,
    "host_game": _cg_host_game,
    "start_networked_game": _cg_start_networked_game,
    "set_network_mode": _cg_set_network_mode,
    "network_spawn": _cg_network_spawn,
}


def _cc_is_instance_owner(gen, params, event_type):
    return "__import__('mp_lan.glue', fromlist=['is_owner']).is_owner(self)"


def _cc_remote_input(gen, params, event_type):
    num, _ = _helpers()
    return ("__import__('mp_lan.glue', fromlist=['remote_input']).remote_input("
            f"{num(params.get('player'), 0)}, {_raw(params, 'name')!r})")


CONDITION_CODEGEN = {
    "is_instance_owner": _cc_is_instance_owner,
    "remote_input": _cc_remote_input,
}

EVENT_METHODS = {name: "on_" + name for name in (
    "network_started", "player_joined", "player_left", "network_message",
    "network_game_started", "connection_lost")}

# Scene class-body code (post-.format, single braces). Steps the connection once a
# frame; does nothing (and imports nothing) until a join_game action has loaded it.
SCENE_CODE = '''\n    # -- LAN multiplayer client (extension: multiplayer_lan) -------------
    def _ext_update__multiplayer_lan(self, dt):
        import sys
        glue = sys.modules.get('mp_lan.glue')
        if glue is not None and glue.active():
            glue.update(self)
'''
