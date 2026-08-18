#!/usr/bin/env python3
"""Action SCHEMA the LAN multiplayer extension contributes to the IDE.

Phase 2 of docs/MULTIPLAYER_LAN_PLAN.md: one action, set_network_mode,
mirroring extensions/block_world/actions.py's enable_block_world_view for
shape -- the handler (handlers.py's PluginExecutor.execute_set_network_mode_action)
does the real work; this file is schema only. The loader merges this into
ACTION_TYPES at startup (events/plugin_loader.py).
"""
from events.action_types import ActionType, ActionParameter

PLUGIN_ACTIONS = {
    "set_network_mode": ActionType(
        name="set_network_mode",
        display_name="Set Network Mode",
        description="Start this room as a LAN multiplayer host or client -- "
                    "call once (e.g. in the Create event of the room's "
                    "controller object). A no-op if this room already has "
                    "networking configured. See also the --net-host / "
                    "--net-client command-line flags, which configure this "
                    "without needing any action at all.",
        category="Multiplayer",
        icon="🌐",
        parameters=[
            ActionParameter(name="mode", display_name="Mode", param_type="choice",
                default_value="host", choices=["host", "client"],
                description="Host = other players connect to you; Client = "
                            "you connect to a host's address"),
            ActionParameter(name="host", display_name="Host Address",
                param_type="string", default_value="127.0.0.1", required=False,
                description="The host's LAN IP address (Client mode only; "
                            "ignored in Host mode)"),
            ActionParameter(name="port", display_name="Port", param_type="number",
                default_value=45782, required=False,
                description="TCP port -- must match between host and client"),
        ]
    ),
}
