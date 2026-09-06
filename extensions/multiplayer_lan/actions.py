#!/usr/bin/env python3
"""Action SCHEMAS the LAN multiplayer extension contributes to the IDE.

v1 (docs/MULTIPLAYER_LAN_PLAN.md) shipped one action, ``set_network_mode``
(kept below for back-compat with the CLI/env-var launch path). v2's Tier A
(docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 5.2) adds the shared-blackboard API:
host/join, shared variables, and custom messages. Handlers are in
handlers.py (the PluginExecutor class); the loader merges this dict into
ACTION_TYPES at startup (events/plugin_loader.py).

There are no dedicated *condition* actions -- identity is mirrored into
globals (``global.is_host``, ``global.player_id``, ``global.player_count``,
``global.network_role``, ``global.network_connected``) plus every shared
var as ``global.<name>``, so an author gates logic with an ordinary
``if_condition`` expression (``global.is_host == 1``). See the plan's
"Core changes" section for why (v2 ships zero core changes).
"""
from events.action_types import ActionType, ActionParameter

_CATEGORY = "Network"

PLUGIN_ACTIONS = {
    # -- Session lifecycle ------------------------------------------------
    "host_game": ActionType(
        name="host_game",
        display_name="Host a Game",
        description="Become the host of a LAN multiplayer game: the "
                        "other players connect to this machine. Call it "
                        "once (for example in the room controller's "
                        "Create event). Sets global.player_id = 0 and "
                        "global.network_role = \"host\".",
        category=_CATEGORY,
        icon="🌐",
        parameters=[
            ActionParameter(name="game_name", display_name="Game name",
                param_type="string", default_value="PyGameMaker", required=False,
                description="Name shown in the server list (network "
                                "discovery)"),
            ActionParameter(name="max_players", display_name="Max players",
                param_type="number", default_value=8, required=False,
                description="Largest number of players, host included "
                                "(2 to 16)"),
            ActionParameter(name="port", display_name="Port", param_type="number",
                default_value=45782, required=False,
                description="TCP port -- must be the same on the host "
                                "and every client"),
            ActionParameter(name="player_name", display_name="Player name",
                param_type="string", default_value="", required=False,
                description="This player's name (empty = "
                                "global.player_name, or \"Player\")"),
            ActionParameter(name="show_lobby", display_name="Waiting room",
                param_type="boolean", default_value=False, required=False,
                description="Show a \"Waiting for players...\" screen "
                                "with a Start button before the game "
                                "begins"),
        ],
    ),
    "join_game": ActionType(
        name="join_game",
        display_name="Join a Game",
        description="Connect to a LAN multiplayer game hosted by "
                        "another machine. The host sets global.player_id "
                        "(1, 2, ...). If the host cannot be reached, the "
                        "game carries on single-player.",
        category=_CATEGORY,
        icon="🔌",
        parameters=[
            ActionParameter(name="host", display_name="Host address",
                param_type="string", default_value="127.0.0.1", required=False,
                description="The host's LAN IP address (\"auto\" opens "
                                "the built-in connection screen)"),
            ActionParameter(name="port", display_name="Port", param_type="number",
                default_value=45782, required=False,
                description="TCP port -- must match the host's"),
            ActionParameter(name="player_name", display_name="Player name",
                param_type="string", default_value="", required=False,
                description="This player's name (empty = "
                                "global.player_name, or \"Player\")"),
        ],
    ),
    "leave_game": ActionType(
        name="leave_game",
        display_name="Leave the Game",
        description="Disconnect (or stop hosting) and clear the "
                        "global network variables.",
        category=_CATEGORY,
        icon="🚪",
        parameters=[],
    ),
    "start_networked_game": ActionType(
        name="start_networked_game",
        display_name="Start the Networked Game",
        description="Host only: take everyone out of the waiting room "
                        "and begin. Fires the \"Networked game started\" "
                        "event on every machine.",
        category=_CATEGORY,
        icon="🚦",
        parameters=[],
    ),
    # -- Shared blackboard ---------------------------------------------
    "set_shared_var": ActionType(
        name="set_shared_var",
        display_name="Set a Shared Variable",
        description="Write a variable shared by every machine. On the "
                        "host it applies immediately; on a client it is a "
                        "request sent to the host. Readable anywhere as "
                        "global.<name>.",
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
    "get_shared_var": ActionType(
        name="get_shared_var",
        display_name="Read a Shared Variable",
        description="Copy a shared variable into a global variable, "
                        "to use it in a calculation. The same as reading "
                        "global.<name> directly.",
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
    "send_network_message": ActionType(
        name="send_network_message",
        display_name="Send a Network Message",
        description="Broadcast a message of your own. Fires the "
                        "\"Network message\" event on the machines "
                        "concerned, with global.network_event / "
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
                description="all = everyone; host = the host only"),
        ],
    ),
    # -- Tier B: networked instances -------------------------------
    "network_spawn": ActionType(
        name="network_spawn",
        display_name="Create a Networked Object",
        description="Host only: create an instance that appears "
                        "automatically on every client, as a smoothed "
                        "\"ghost\". Does nothing on a client. The host "
                        "drives the instance it creates -- guard its game "
                        "logic with global.is_host == 1.",
        category=_CATEGORY,
        icon="✨",
        parameters=[
            ActionParameter(name="object", display_name="Object", param_type="object",
                default_value="", description="The type of object to create"),
            ActionParameter(name="x", display_name="X", param_type="string",
                default_value="0"),
            ActionParameter(name="y", display_name="Y", param_type="string",
                default_value="0"),
            ActionParameter(name="owner", display_name="Owner",
                param_type="string", default_value="0", required=False,
                description="The player who drives this instance (0 = "
                                "host). Often global.network_sender "
                                "inside \"Player joined\"."),
            ActionParameter(name="relative", display_name="Relative",
                param_type="boolean", default_value=False, required=False,
                description="Position relative to the object running "
                                "the action"),
        ],
    ),
    "sync_instance": ActionType(
        name="sync_instance",
        display_name="Synchronise This Instance",
        description="Mark the instance running this action as "
                        "synchronised: its position, rotation, image and "
                        "visibility are copied to every machine. Call it "
                        "in the Create event. The host owns it by "
                        "default; use \"Set the instance's owner\" to let a "
                        "client drive it.",
        category=_CATEGORY,
        icon="🔗",
        parameters=[
            ActionParameter(name="vars", display_name="Variables to copy",
                param_type="string", default_value="", required=False,
                description="Instance variable names to copy as well, "
                                "separated by commas (e.g. \"hp, colour\")"),
        ],
    ),
    "set_instance_owner": ActionType(
        name="set_instance_owner",
        display_name="Set the Instance's Owner",
        description="Choose which player drives this synchronised "
                        "instance (0 = host, 1, 2, ... = clients). On "
                        "that player's machine the instance runs locally "
                        "and feels responsive, and its state is reported "
                        "back to the host; everywhere else it is a "
                        "smoothed ghost. Call it on the host, guarded by "
                        "global.is_host == 1.",
        category=_CATEGORY,
        icon="🎮",
        parameters=[
            ActionParameter(name="player", display_name="Player", param_type="string",
                default_value="0",
                description="Player number (0 = host). Often "
                                "global.network_sender inside \"Player "
                                "joined\"."),
        ],
    ),
    "is_instance_owner": ActionType(
        name="is_instance_owner",
        display_name="If I Drive This Instance",
        description="A condition: true when THIS machine owns the "
                        "synchronised instance. Put it before a block so "
                        "the control logic only runs on the right "
                        "player's machine.",
        category=_CATEGORY,
        icon="❓",
        parameters=[],
    ),
    "bind_network_input": ActionType(
        name="bind_network_input",
        display_name="Bind a Network Key",
        description="Attach a local key to a \"named input\" reported "
                        "to the host. The host then tests it with \"If the "
                        "player presses\". The arrow keys and Space are "
                        "already bound (\"left\", \"right\", \"up\", \"down\", "
                        "\"space\").",
        category=_CATEGORY,
        icon="⌨️",
        parameters=[
            ActionParameter(name="name", display_name="Input name",
                param_type="string", default_value="",
                description="A label of your choosing (e.g. \"jump\", \"fire\")"),
            ActionParameter(name="key", display_name="Key", param_type="string",
                default_value="",
                description="A key name: \"space\", \"left\", \"a\", \"5\", "
                                "\"lshift\"..."),
        ],
    ),
    "remote_input": ActionType(
        name="remote_input",
        display_name="If the Player Presses",
        description="A condition, on the host: true while the named "
                        "player is holding the named input. It lets the "
                        "host react to a client's keys without owning "
                        "that client's character.",
        category=_CATEGORY,
        icon="❓",
        parameters=[
            ActionParameter(name="player", display_name="Player", param_type="string",
                default_value="0", description="Player number (0 = host)"),
            ActionParameter(name="name", display_name="Input name",
                param_type="string", default_value="",
                description="The named input to test (e.g. \"jump\")"),
        ],
    ),
    "set_sync_rate": ActionType(
        name="set_sync_rate",
        display_name="Set the Sync Rate",
        description="Adjust how often the host sends snapshots, and "
                        "how far behind clients draw them. Call it once "
                        "on the host, and on the clients for the delay.",
        category=_CATEGORY,
        icon="⏱️",
        parameters=[
            ActionParameter(name="hz", display_name="Snapshots per second",
                param_type="number", default_value=20, required=False,
                description="10-30 works well on a local network "
                                "(default 20)"),
            ActionParameter(name="interp_ms", display_name="Smoothing (ms)",
                param_type="number", default_value=100, required=False,
                description="How far behind ghosts are drawn, in "
                                "milliseconds (default 100)"),
        ],
    ),
    # -- v1 back-compat -----------------------------------------------
    "set_network_mode": ActionType(
        name="set_network_mode",
        display_name="Set Network Mode (v1)",
        description="An older low-level action: starts the room in "
                        "host or client mode (spectator only -- a "
                        "client's input has no effect). Prefer \"Host a "
                        "Game\" / \"Join a Game\". Kept for existing "
                        "projects and the --net-host / --net-client "
                        "flags.",
        category=_CATEGORY,
        icon="🌐",
        parameters=[
            ActionParameter(name="mode", display_name="Mode", param_type="choice",
                default_value="host", choices=["host", "client"],
                description="Host = others connect to you; Client = "
                                "you connect to a host"),
            ActionParameter(name="host", display_name="Host Address",
                param_type="string", default_value="127.0.0.1", required=False,
                description="The host's LAN IP address (Client mode only)"),
            ActionParameter(name="port", display_name="Port", param_type="number",
                default_value=45782, required=False,
                description="TCP port -- must be the same on the host "
                                "and the client"),
        ],
    ),
}
