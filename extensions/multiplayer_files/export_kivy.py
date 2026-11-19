"""Shared-folder (file exchange) multiplayer on the Kivy (Android/iOS) export.

The session is plain file I/O, so a phone can host AND join (the LAN extension's
phone support is client-only). The session modules ship verbatim as the
``mp_files`` package plus ``kivy_glue.py`` (``mp_files.glue``). Not available on a
phone: the connect/lobby screen (``show_lobby`` is ignored, ``folder="auto"`` needs
it) -- see kivy_glue.py for the practical limit on which folders a phone can reach.

The extension loader ``exec``s this file without ``__file__``, so everything here
is plain data.
"""

# {path under the game folder: source path relative to this extension's folder}
SUPPORT_FILES = {
    "mp_files/__init__.py": "kivy_pkg_init.py",
    "mp_files/state.py": "state.py",
    "mp_files/fileio.py": "fileio.py",
    "mp_files/session.py": "session.py",
    "mp_files/glue.py": "kivy_glue.py",
}


def _helpers():
    from export.Kivy.code_generator import _num_code, _value_code
    return _num_code, _value_code


def _raw(params, key, default=""):
    value = params.get(key, default)
    return str(value if value is not None else default).strip()


def _truthy(value):
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "no")
    return bool(value)


def _cg_host_game_files(gen, params, event_type):
    num, _ = _helpers()
    return ("from mp_files.glue import host; "
            f"host({_raw(params, 'folder')!r}, {num(params.get('max_players'), 8)}, "
            f"{_raw(params, 'player_name')!r}, {num(params.get('round_deadline'), 30)}, "
            f"{_truthy(params.get('show_lobby'))!r})")


def _cg_join_game_files(gen, params, event_type):
    return ("from mp_files.glue import join; "
            f"join({_raw(params, 'folder')!r}, {_raw(params, 'player_name')!r})")


def _cg_leave_game_files(gen, params, event_type):
    return "from mp_files.glue import leave; leave()"


def _cg_set_shared_var_files(gen, params, event_type):
    _, value = _helpers()
    return ("from mp_files.glue import set_shared; "
            f"set_shared({_raw(params, 'name')!r}, {value(params.get('value', 0))})")


def _cg_get_shared_var_files(gen, params, event_type):
    return ("from mp_files.glue import get_shared_into; "
            f"get_shared_into({_raw(params, 'name')!r}, {_raw(params, 'into')!r})")


def _cg_end_turn(gen, params, event_type):
    return "from mp_files.glue import end_turn; end_turn()"


def _cg_send_network_message_files(gen, params, event_type):
    _, value = _helpers()
    data = params.get("data")
    expr = "None" if data is None or str(data).strip() == "" else value(data)
    return ("from mp_files.glue import send_message; "
            f"send_message({_raw(params, 'event')!r}, {expr}, {_raw(params, 'target', 'all')!r})")


ACTION_CODEGEN = {
    "host_game_files": _cg_host_game_files,
    "join_game_files": _cg_join_game_files,
    "leave_game_files": _cg_leave_game_files,
    "set_shared_var_files": _cg_set_shared_var_files,
    "get_shared_var_files": _cg_get_shared_var_files,
    "end_turn": _cg_end_turn,
    "send_network_message_files": _cg_send_network_message_files,
}

EVENT_METHODS = {name: "on_" + name for name in (
    "file_session_started", "player_joined_files", "round_resolved",
    "player_skipped_round", "network_message_files", "file_session_lost")}

# Scene class-body code (post-.format, single braces): step the session once a frame;
# nothing (and no import) until a host/join action has loaded the glue.
SCENE_CODE = '''\n    # -- shared-folder multiplayer (extension: multiplayer_files) ---------
    def _ext_update__multiplayer_files(self, dt):
        import sys
        glue = sys.modules.get('mp_files.glue')
        if glue is not None and glue.active():
            glue.update(self)
'''
