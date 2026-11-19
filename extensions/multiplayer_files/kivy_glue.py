"""Shared-folder (file exchange) multiplayer for the Kivy (Android/iOS) export.

Shipped into the game as ``mp_files/glue.py`` beside the desktop session modules
(``mp_files/session.py``, ``fileio.py``, ``state.py``, byte for byte), so a phone
speaks the same files as the desktop. The session is plain file I/O -- no socket
-- so, unlike the LAN extension, a phone can both HOST and JOIN.

Limits: the connect/lobby screen is desktop-only (``show_lobby`` is ignored, the
round simply runs) and ``folder="auto"`` (typing the folder in that screen) needs
it too, so a phone must be given the folder in the action. The folder has to be
somewhere the app can read and write -- on Android that is its own storage or a
path it was granted; a Dropbox/SMB folder that the desktop sees is generally NOT
visible to a phone app, which is the real practical limit of this on a phone.

Pure Python and duck-typed against the scene (``instances``) so it is testable
without Kivy; the game's globals live in ``main`` (``get_global``/``set_global``).
"""

import logging

log = logging.getLogger("mp_files")

_session = None
_warned = set()

STATUS_GLOBALS = (
    "player_id", "player_count", "is_host", "round_number", "turn_ready",
    "waiting_for_players", "network_sender", "network_player_name",
    "network_event", "network_data",
)


def _main():
    return __import__("main")


def _set_global(name, value):
    _main().set_global(name, value)


def _say(message):
    log.warning(message)
    try:
        _main()._log(message)
    except Exception:
        pass


def _warn_once(key, message):
    if key not in _warned:
        _warned.add(key)
        _say(message)


def _player_name(explicit):
    if explicit:
        return str(explicit)
    try:
        return str(_main().get_global("player_name", "") or "Joueur")
    except Exception:
        return "Joueur"


def _start(session, what, folder):
    global _session
    if not session.start():
        _say("multiplayer_files: could not %s the shared folder %r (is it writable "
             "and reachable from this device?)" % (what, folder))
        return False
    _session = session
    return True


def host(folder, max_players, player_name, round_deadline, show_lobby=False):
    """host_game_files. Never raises."""
    if _session is not None:
        return
    folder = str(folder or "").strip()
    if not folder:
        _say("multiplayer_files: host_game_files needs a shared folder.")
        return
    if show_lobby:
        _warn_once("lobby", "multiplayer_files: the waiting-room screen is desktop-only; "
                            "the round starts at once on this device.")
    from .session import FileSession
    from .state import DEFAULT_MAX_PLAYERS, DEFAULT_ROUND_DEADLINE
    try:
        max_players = int(float(max_players))
    except (TypeError, ValueError):
        max_players = DEFAULT_MAX_PLAYERS
    try:
        round_deadline = float(round_deadline)
    except (TypeError, ValueError):
        round_deadline = DEFAULT_ROUND_DEADLINE
    _start(FileSession(mode="host", folder=folder, max_players=max_players,
                       player_name=_player_name(player_name), round_deadline=round_deadline),
           "create", folder)


def join(folder, player_name):
    """join_game_files. Never raises."""
    if _session is not None:
        return
    folder = str(folder or "").strip()
    if folder == "auto":
        _warn_once("auto", "multiplayer_files: join_game_files(folder='auto') needs the "
                           "desktop connect screen; give the shared folder in the action.")
        return
    if not folder:
        _say("multiplayer_files: join_game_files needs the shared folder to join.")
        return
    from .session import FileSession
    _start(FileSession(mode="client", folder=folder, player_name=_player_name(player_name)),
           "reach", folder)


def leave():
    global _session
    s, _session = _session, None
    if s is not None:
        try:
            s.leave()
            s.close()
        except Exception:
            pass
    try:
        g = _main().get_game_app().globals
        for key in STATUS_GLOBALS:
            g.pop(key, None)
    except Exception:
        pass


def active():
    return _session is not None


def set_shared(name, value):
    if _session is not None and name:
        _session.set_shared(str(name), value)


def get_shared_into(name, into):
    if into:
        _set_global(str(into), _session.get_shared(str(name)) if _session is not None else None)


def send_message(event, data, target):
    if _session is not None and event:
        _session.send_message(str(event), data, target if target in ("all", "host") else "all")


def end_turn():
    if _session is not None:
        _session.end_turn()


def update(scene):
    """Pump the session (its disk I/O is throttled inside), mirror state into the
    globals and fire the lifecycle events. A no-op until a host/join action."""
    s = _session
    if s is None:
        return
    s.pump_before_step()
    _set_global("player_id", s.player_id)
    _set_global("player_count", s.player_count)
    _set_global("is_host", 1 if s.mode == "host" else 0)
    _set_global("round_number", s.round)
    _set_global("turn_ready", 1 if s.turn_ready else 0)
    _set_global("waiting_for_players", 1 if s.waiting_for_players else 0)
    for key, val in s.shared.items():
        _set_global(key, val)
    for event in s.take_events():
        name = event[0]
        if name == "player_joined_files":
            _, slot, pname = event
            _set_global("network_sender", slot)
            _set_global("network_player_name", pname)
        elif name == "player_skipped_round":
            _set_global("network_sender", event[1])
        elif name == "network_message_files":
            _, ev_name, data, sender = event
            _set_global("network_event", ev_name)
            _set_global("network_data", data)
            _set_global("network_sender", sender)
        elif name == "file_session_lost":
            _set_global("turn_ready", 0)
        for inst in list(getattr(scene, "instances", ())):
            handler = getattr(inst, "on_" + name, None)
            if handler is None:
                continue
            try:
                handler()
            except Exception as exc:
                log.warning("multiplayer_files: %s handler raised: %s", name, exc)
    s.pump_after_update()
