#!/usr/bin/env python3
"""Runtime handlers for the file-exchange multiplayer extension.

Mirrors extensions/multiplayer_lan/handlers.py: a plugin's action
handlers run as methods of a PluginExecutor instance, reaching the engine
through instance.action_executor (the plugins/audio_actions pattern), not
through ActionExecutor directly. The two frame-update functions are plain
``(game_runner) -> None`` callables (see runtime/extension_hooks.py),
registered via PLUGIN_FRAME_UPDATES in __init__.py.

Per-room state lives at room.extension_state["multiplayer_files"] (see
state.py). Unlike multiplayer_lan there is only ever one path here (no
v1/v2 split to carry).
"""

from core.logger import get_logger
from .session import FileSession
from .state import (
    DEFAULT_MAX_PLAYERS, DEFAULT_ROUND_DEADLINE, MULTIPLAYER_FILES_KEY,
    multiplayer_files_state, peek_multiplayer_files,
)

logger = get_logger(__name__)

# Globals the session mirrors into game_runner.global_variables every
# frame, matching multiplayer_lan's own _NETWORK_GLOBALS pattern. Cleared
# by leave_game_files.
_STATUS_GLOBALS = (
    "player_id", "player_count", "is_host", "round_number", "turn_ready",
    "waiting_for_players", "network_sender", "network_player_name",
    "network_event", "network_data",
)


def _pv(ae, instance, raw, default):
    """Parse an action param through the expression evaluator, falling
    back to ``default`` when it's missing/blank/unparseable. For *value*
    params -- NOT for names/labels, which must stay literal."""
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


def _pv_float(ae, instance, raw, default):
    try:
        return float(_pv(ae, instance, raw, default))
    except (TypeError, ValueError):
        return default


def _raw(parameters, key, default=""):
    """A param taken literally -- a name, label or folder path, never run
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


def _notify(ae, message):
    """Surface a shared-folder failure to the player instead of the
    action silently doing nothing -- same pattern (and reasoning) as
    extensions/multiplayer_lan/handlers.py's own _notify."""
    logger.warning("multiplayer_files: %s", message.replace("\n", " "))
    gr = getattr(ae, "game_runner", None)
    fn = getattr(gr, "show_message_dialog", None)
    if callable(fn) and getattr(gr, "screen", None) is not None:
        try:
            fn(message)
        except Exception:
            pass


def _truthy(v):
    return v not in (None, False, 0, "", "0", "false", "False", "no")


def _run_connect_flow(mode, game_runner, *, folder="", roster_fn=None, tick_fn=None):
    """Build and run the modal connect/lobby screen (Phase 4). Returns
    its result string ("folder:<path>" / "start" / "cancel"). On a
    headless runner FileConnectScreen.run() short-circuits to a sensible
    default."""
    from .connect_screen import FileConnectScreen
    cs = FileConnectScreen(
        mode, getattr(game_runner, "screen", None),
        folder=folder, roster_fn=roster_fn, tick_fn=tick_fn)
    return cs.run()


def _lobby_tick(session):
    session.pump_before_step()
    session.pump_after_update()


class PluginExecutor:
    """Handles execution of the file-exchange multiplayer actions."""

    @staticmethod
    def _executor(instance):
        return getattr(instance, "action_executor", None)

    # -- lifecycle ----------------------------------------------------

    def execute_host_game_files_action(self, instance, parameters):
        room, ae = _room_and_executor(instance)
        if room is None:
            return
        st = peek_multiplayer_files(room)
        if st and st.get("session") is not None:
            return  # already networked
        folder = _raw(parameters, "folder")
        if not folder:
            _notify(ae, "Il faut indiquer un dossier partagé pour héberger "
                        "une partie par fichiers.")
            return
        session = FileSession(
            mode="host", folder=folder,
            max_players=_pv_int(
                ae, instance, parameters.get("max_players"), DEFAULT_MAX_PLAYERS),
            player_name=_player_name(ae.game_runner, _raw(parameters, "player_name")),
            round_deadline=_pv_float(
                ae, instance, parameters.get("round_deadline"), DEFAULT_ROUND_DEADLINE),
        )
        if not session.start():
            _notify(ae,
                    "Impossible de créer la partie dans « %s ».\n\n"
                    "Vérifiez que le dossier existe (ou peut être créé), "
                    "qu'il est accessible en écriture, et que le lecteur "
                    "réseau est bien connecté." % folder)
            return
        st = multiplayer_files_state(room)
        st["session"] = session
        st["enabled"] = True

        if _truthy(parameters.get("show_lobby")):
            # Unlike multiplayer_lan's host_game, the round is already
            # running the moment session.start() succeeds -- there is no
            # separate "leave the lobby" step to trigger (no
            # start_networked_game_files action -- see "Proposed action
            # surface"). "start" just dismisses the modal; only "cancel"
            # needs to actually undo anything.
            result = _run_connect_flow(
                "host", ae.game_runner, folder=folder,
                roster_fn=lambda: session.roster,
                tick_fn=lambda: _lobby_tick(session))
            if result == "cancel":
                self._teardown(room, ae)

    def execute_join_game_files_action(self, instance, parameters):
        room, ae = _room_and_executor(instance)
        if room is None:
            return
        st = peek_multiplayer_files(room)
        if st and st.get("session") is not None:
            return
        folder = _raw(parameters, "folder")
        player_name = _player_name(ae.game_runner, _raw(parameters, "player_name"))

        if folder == "auto":
            result = _run_connect_flow("client", ae.game_runner)
            if not result or not result.startswith("folder:"):
                return                     # cancelled -- game continues single-player
            _, _, folder = result.partition("folder:")

        if not folder:
            _notify(ae, "Il faut indiquer le dossier partagé de la partie "
                        "à rejoindre.")
            return
        session = FileSession(mode="client", folder=folder, player_name=player_name)
        if not session.start():
            _notify(ae,
                    "Impossible d'accéder à « %s ».\n\n"
                    "Vérifiez que l'hôte a bien lancé la partie et que ce "
                    "dossier est accessible depuis cette machine." % folder)
            return
        st = multiplayer_files_state(room)
        st["session"] = session
        st["enabled"] = True

    def execute_leave_game_files_action(self, instance, parameters):
        room, ae = _room_and_executor(instance)
        if room is not None:
            self._teardown(room, ae)

    def _teardown(self, room, ae):
        st = peek_multiplayer_files(room)
        if not st:
            return
        session = st.get("session")
        if session is not None:
            try:
                session.leave()
                session.close()
            except Exception:
                pass
        st["session"] = None
        st["enabled"] = False
        gv = getattr(getattr(ae, "game_runner", None), "global_variables", None)
        if isinstance(gv, dict):
            for key in _STATUS_GLOBALS:
                gv.pop(key, None)

    # -- shared blackboard -------------------------------------------

    def execute_set_shared_var_files_action(self, instance, parameters):
        session = self._session_for(instance)
        if session is None:
            return
        ae = self._executor(instance)
        name = _raw(parameters, "name")
        if not name:
            return
        value = _pv(ae, instance, parameters.get("value"), 0)
        session.set_shared(name, value)

    def execute_get_shared_var_files_action(self, instance, parameters):
        session = self._session_for(instance)
        ae = self._executor(instance)
        if ae is None:
            return
        into = _raw(parameters, "into")
        if not into:
            return
        name = _raw(parameters, "name")
        value = session.get_shared(name) if session is not None else None
        gv = getattr(ae.game_runner, "global_variables", None)
        if isinstance(gv, dict):
            gv[into] = value

    def execute_end_turn_action(self, instance, parameters):
        session = self._session_for(instance)
        if session is not None:
            session.end_turn()

    def execute_send_network_message_files_action(self, instance, parameters):
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

    @staticmethod
    def _session_for(instance):
        ae = getattr(instance, "action_executor", None)
        if ae is None or not getattr(ae, "game_runner", None):
            return None
        room = getattr(ae.game_runner, "current_room", None)
        st = peek_multiplayer_files(room) if room is not None else None
        return st.get("session") if st else None


# ---------------------------------------------------------------------------
# Frame-update hooks
# ---------------------------------------------------------------------------

def _fire_event(room, event_name):
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
            logger.exception("multiplayer_files: %s handler raised", event_name)


def _apply_session_state(game_runner, session):
    """Mirror the session's identity/status + shared vars into globals,
    then fire any queued lifecycle events. Runs in the before_step
    phase."""
    gv = getattr(game_runner, "global_variables", None)
    room = getattr(game_runner, "current_room", None)
    if not isinstance(gv, dict) or room is None:
        return

    gv["player_id"] = session.player_id
    gv["player_count"] = session.player_count
    gv["is_host"] = 1 if session.mode == "host" else 0
    gv["round_number"] = session.round
    gv["turn_ready"] = 1 if session.turn_ready else 0
    gv["waiting_for_players"] = 1 if session.waiting_for_players else 0
    for key, val in session.shared.items():
        gv[key] = val

    for event in session.take_events():
        name = event[0]
        if name == "player_joined_files":
            _, slot, pname = event
            gv["network_sender"] = slot
            gv["network_player_name"] = pname
        elif name == "player_skipped_round":
            _, slot = event
            gv["network_sender"] = slot
        elif name == "network_message_files":
            _, ev_name, data, sender = event
            gv["network_event"] = ev_name
            gv["network_data"] = data
            gv["network_sender"] = sender
        elif name == "file_session_lost":
            gv["turn_ready"] = 0
        _fire_event(room, name)


def _resolve_state(game_runner):
    room = getattr(game_runner, "current_room", None)
    if room is None:
        return None, None
    return room, peek_multiplayer_files(room)


def _on_room_change(old_room, new_room):
    """Migrate a live file-exchange session across a room change/restart,
    same reasoning as multiplayer_lan's own _on_room_change (M1,
    docs/FULL_AUDIT_2026-09-07.md): there's no socket to leak here, but
    the session DOES carry in-memory roster/round state a fresh room
    object must not silently lose."""
    if old_room is None:
        return
    old_state = peek_multiplayer_files(old_room)
    if old_state is None or old_state.get("session") is None:
        return

    new_es = getattr(new_room, "extension_state", None)
    if new_es is None:
        new_es = {}
        setattr(new_room, "extension_state", new_es)
    new_es[MULTIPLAYER_FILES_KEY] = old_state

    old_es = getattr(old_room, "extension_state", None)
    if old_es is not None:
        old_es.pop(MULTIPLAYER_FILES_KEY, None)

    logger.debug(
        "multiplayer_files: migrated session from room %r to room %r on "
        "room change",
        getattr(old_room, "name", old_room), getattr(new_room, "name", new_room))


def _frame_update_before_step(game_runner):
    """before_step: pump the session (gated to state.POLL_INTERVAL
    internally) and refresh globals/events so Step handlers see current
    state."""
    room, st = _resolve_state(game_runner)
    if not st or st.get("session") is None:
        return
    session = st["session"]
    session.pump_before_step()
    _apply_session_state(game_runner, session)


def _frame_update_after_update(game_runner):
    """after_update: currently a no-op pump (see FileSession.
    pump_after_update's own docstring) -- kept as its own hook, not
    folded into before_step, so a future author-visible per-frame write
    (Phase 2's send_network_message_files, say) has the same "only after
    the frame's state has settled" timing multiplayer_lan's host
    broadcast relies on."""
    room, st = _resolve_state(game_runner)
    if not st or st.get("session") is None:
        return
    st["session"].pump_after_update()
