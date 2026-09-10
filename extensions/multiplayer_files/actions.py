#!/usr/bin/env python3
"""Action SCHEMAS the file-exchange multiplayer extension contributes to
the IDE. Handlers are in handlers.py (the PluginExecutor class); the
loader merges this dict into ACTION_TYPES at startup
(events/plugin_loader.py).

Two of these -- "Set a Shared Variable (File Exchange)" / "Read a Shared
Variable (File Exchange)" -- read as the file-exchange sibling of
extensions/multiplayer_lan/actions.py's own set_shared_var/
get_shared_var, but are deliberately NAMED set_shared_var_files /
get_shared_var_files rather than reusing those exact action names:
plugin_loader.py's _load_actions skips any plugin action whose name
already exists in ACTION_TYPES (the landmine CLAUDE.md documents for the
static-vs-plugin case; the same mechanism applies plugin-vs-plugin).
Registering an IDENTICALLY-named action from a second extension would
silently shadow whichever extension's folder happens to sort first --
"multiplayer_files" sorts before "multiplayer_lan" in the loader's
``sorted(extension_dir.iterdir())`` walk, so without the rename this
extension would have silently disabled the already-shipped LAN version's
own set_shared_var/get_shared_var the moment both were installed. Same
reasoning applies to send_network_message_files below (its socket-version
sibling is named send_network_message) and to the event name it fires --
"network_message_files", not "network_message", for the identical reason
one level up: events/plugin_loader.py's _load_events has the same
skip-if-already-registered behaviour for EVENT_TYPES as _load_actions has
for ACTION_TYPES. Recorded in
docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md's "Proposed action surface" too.

There are no dedicated *condition* actions here either, matching
multiplayer_lan's own reasoning: identity/status is mirrored into globals
(global.is_host, global.player_id, global.player_count,
global.round_number, global.turn_ready, global.waiting_for_players) plus
every shared var as global.<name>, so an author gates logic with an
ordinary if_condition expression.
"""
from events.action_types import ActionType, ActionParameter

_CATEGORY = "Network"

PLUGIN_ACTIONS = {
    "host_game_files": ActionType(
        name="host_game_files",
        display_name="Host a Game (File Exchange)",
        description="Become the host of a turn-based game played over a "
                        "shared folder instead of a live connection -- "
                        "works through a school firewall that blocks "
                        "direct connections between machines. Call it "
                        "once (for example in the room controller's "
                        "Create event). Sets global.player_id = 0 and "
                        "global.is_host = 1.",
        category=_CATEGORY,
        icon="🗂️",
        parameters=[
            ActionParameter(name="folder", display_name="Shared folder",
                param_type="string", default_value="", required=True,
                description="Path to a folder both machines can reach "
                                "(a mapped network drive, a synced "
                                "Dropbox/OneDrive folder, ...)"),
            ActionParameter(name="max_players", display_name="Max players",
                param_type="number", default_value=8, required=False,
                description="Largest number of players, host included "
                                "(2 to 16)"),
            ActionParameter(name="player_name", display_name="Player name",
                param_type="string", default_value="", required=False,
                description="This player's name (empty = "
                                "global.player_name, or \"Player\")"),
            ActionParameter(name="round_deadline", display_name="Round deadline (s)",
                param_type="number", default_value=30, required=False,
                description="How long to wait for every joined player's "
                                "move before advancing the round anyway "
                                "(a missing player is skipped that round, "
                                "not left blocking the game forever)"),
            ActionParameter(name="show_lobby", display_name="Waiting room",
                param_type="boolean", default_value=False, required=False,
                description="Show a \"Waiting for players...\" screen "
                                "with a Start button before handing "
                                "control back to the game"),
        ],
    ),
    "join_game_files": ActionType(
        name="join_game_files",
        display_name="Join a Game (File Exchange)",
        description="Join a turn-based game hosted by another machine "
                        "through a shared folder. The host assigns "
                        "global.player_id (1, 2, ...).",
        category=_CATEGORY,
        icon="🔌",
        parameters=[
            ActionParameter(name="folder", display_name="Shared folder",
                param_type="string", default_value="", required=True,
                description="Path to the SAME shared folder the host used "
                                "(\"auto\" opens the built-in screen to "
                                "type it in)"),
            ActionParameter(name="player_name", display_name="Player name",
                param_type="string", default_value="", required=False,
                description="This player's name (empty = "
                                "global.player_name, or \"Player\")"),
        ],
    ),
    "leave_game_files": ActionType(
        name="leave_game_files",
        display_name="Leave the Game (File Exchange)",
        description="Stop hosting or leave the game, and clear the "
                        "global status variables.",
        category=_CATEGORY,
        icon="🚪",
        parameters=[],
    ),
    "set_shared_var_files": ActionType(
        name="set_shared_var_files",
        display_name="Set a Shared Variable (File Exchange)",
        description="Stage a variable to publish to everyone. It takes "
                        "effect once you call \"End Turn\" and the host "
                        "folds your move into the next round -- not "
                        "immediately, since there is no live connection "
                        "to write over. Readable anywhere as "
                        "global.<name> once published.",
        category=_CATEGORY,
        icon="📤",
        parameters=[
            ActionParameter(name="name", display_name="Name", param_type="string",
                default_value="", description="A plain identifier (letters, "
                                                  "digits, _) -- no spaces or "
                                                  "operators"),
            ActionParameter(name="value", display_name="Value", param_type="string",
                default_value="0",
                description="A number, text or true/false (complex "
                                "objects are refused)"),
        ],
    ),
    "get_shared_var_files": ActionType(
        name="get_shared_var_files",
        display_name="Read a Shared Variable (File Exchange)",
        description="Copy a shared variable into a global variable, to "
                        "use it in a calculation. The same as reading "
                        "global.<name> directly -- the value as of the "
                        "last round the host published, not live.",
        category=_CATEGORY,
        icon="📥",
        parameters=[
            ActionParameter(name="name", display_name="Shared name",
                param_type="string", default_value="",
                description="Name of the shared variable to read"),
            ActionParameter(name="into", display_name="Global variable",
                param_type="string", default_value="",
                description="Name of the global variable to write the "
                                "value into"),
        ],
    ),
    "end_turn": ActionType(
        name="end_turn",
        display_name="End Turn (File Exchange)",
        description="Submit your move for this round: whatever you "
                        "staged with \"Set a Shared Variable (File "
                        "Exchange)\" since your last turn, written as one "
                        "file for the host to pick up. Call it once per "
                        "round -- even with nothing staged -- if this "
                        "game expects every player to respond every "
                        "round; a player who never calls it is skipped "
                        "once the round deadline passes.",
        category=_CATEGORY,
        icon="✅",
        parameters=[],
    ),
    "send_network_message_files": ActionType(
        name="send_network_message_files",
        display_name="Send a Network Message (File Exchange)",
        description="Stage a message of your own, delivered the same "
                        "way \"Set a Shared Variable (File Exchange)\" is "
                        "-- at the next round boundary, not instantly. "
                        "Fires the \"Network Message (File Exchange)\" "
                        "event, with global.network_event / "
                        "global.network_data / global.network_sender.",
        category=_CATEGORY,
        icon="✉️",
        parameters=[
            ActionParameter(name="event", display_name="Message name",
                param_type="string", default_value="",
                description="A label of your choosing that the "
                                "handler tests (e.g. \"buzz\", \"answer\")"),
            ActionParameter(name="data", display_name="Data", param_type="string",
                default_value="", required=False,
                description="A number, text, true/false, or a short list"),
            ActionParameter(name="target", display_name="Send to",
                param_type="choice", default_value="all", choices=["all", "host"],
                description="all = everyone, once they pick up the next "
                                "round; host = the host only, processed "
                                "immediately when the round resolves"),
        ],
    ),
}
