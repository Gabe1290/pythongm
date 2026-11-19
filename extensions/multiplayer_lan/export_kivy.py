"""LAN multiplayer on the Kivy (Android/iOS) export.

A phone is a CLIENT: it joins a desktop-hosted game, takes part in Tier A (shared
variables, messages, identity, the Reseau events), sees the host's networked
instances as interpolated ghosts and plays the avatar the host assigned to it
(own/input frames, named input). Hosting is not available there (see kivy_glue.py). The desktop session code is
shipped verbatim as the ``mp_lan`` package, so the wire protocol is the host's own.

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


def _unsupported(name):
    def _cg(gen, params, event_type):
        return f"from mp_lan.glue import unsupported; unsupported({name!r})"
    return _cg


ACTION_CODEGEN = {
    "join_game": _cg_join_game,
    "leave_game": _cg_leave_game,
    "set_shared_var": _cg_set_shared_var,
    "get_shared_var": _cg_get_shared_var,
    "send_network_message": _cg_send_network_message,
    "bind_network_input": _cg_bind_network_input,
    "set_sync_rate": _cg_set_sync_rate,
}
# Host-side, so a phone cannot do these (see the module docstring): one warning, then a no-op.
for _name in ("host_game", "start_networked_game", "set_network_mode", "network_spawn",
              "sync_instance", "set_instance_owner"):
    ACTION_CODEGEN[_name] = _unsupported(_name)


def _cc_is_instance_owner(gen, params, event_type):
    return "__import__('mp_lan.glue', fromlist=['is_owner']).is_owner(self)"


def _cc_remote_input(gen, params, event_type):
    return "False"          # host-side only: a phone never hosts


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
