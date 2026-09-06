#!/usr/bin/env python3
"""LAN multiplayer.

v1 (docs/MULTIPLAYER_LAN_PLAN.md): authoritative-host position sync over
TCP -- "see where the other player is", spectator-only.

v2 Tier A (docs/MULTIPLAYER_LAN_V2_PLAN.md): a shared-variable blackboard,
custom messages, and player identity, so students can actually build
multiplayer games (quizzes, turn-based, draw-together, co-op-lite). Tier B
(networked instances, owned avatars, named input) is still to come.

Hooks used: the generic per-frame hook (runtime/extension_hooks.py's
register_frame_update) -- a client applies inbound state before Step, a
host sends after the frame settles. No room renderer (this draws nothing;
the Phase 6 connect screen will add one).
"""

PLUGIN_NAME = "LAN Multiplayer"

from events.event_types import EventType

from .actions import PLUGIN_ACTIONS
from .handlers import PluginExecutor, _frame_update_apply_inbound, _frame_update_broadcast

_CATEGORY = "Network"

PLUGIN_EVENTS = {
    "network_started": EventType(
        name="network_started", display_name="Network Ready",
        description="The network session is up -- the host accepted "
                        "this client, or the host started. "
                        "global.player_id is set.",
        category=_CATEGORY, icon="🌐", parameters=[]),
    "player_joined": EventType(
        name="player_joined", display_name="Player Joined",
        description="A player joined the game. global.network_sender "
                        "is their number, global.network_player_name "
                        "their name.",
        category=_CATEGORY, icon="➕", parameters=[]),
    "player_left": EventType(
        name="player_left", display_name="Player Left",
        description="A player left the game. global.network_sender is "
                        "their number.",
        category=_CATEGORY, icon="➖", parameters=[]),
    "network_message": EventType(
        name="network_message", display_name="Network Message",
        description="A custom message arrived. global.network_event "
                        "is its label, global.network_data its data, "
                        "global.network_sender the sender.",
        category=_CATEGORY, icon="✉️", parameters=[]),
    "network_game_started": EventType(
        name="network_game_started", display_name="Networked Game Started",
        description="The host called \"Start the Networked Game\". "
                        "Fires on every machine.",
        category=_CATEGORY, icon="🚦", parameters=[]),
    "connection_lost": EventType(
        name="connection_lost", display_name="Connection Lost",
        description="The link to the host broke -- host closed, cable "
                        "unplugged, Wi-Fi client isolation, and so on.",
        category=_CATEGORY, icon="⚠️", parameters=[]),
}

PLUGIN_FRAME_UPDATES = [
    (_frame_update_apply_inbound, "before_step"),
    (_frame_update_broadcast, "after_update"),
]
