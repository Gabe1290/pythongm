#!/usr/bin/env python3
"""File Exchange Multiplayer -- 1990s-DOS-style turn-based multiplayer
over a shared folder (a mapped network drive, a synced Dropbox/OneDrive
folder, a school SMB share), for classroom LANs where a firewall blocks
the direct peer-to-peer connections extensions/multiplayer_lan/ needs.
See docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md for the full design and the
historical grounding (VGA Planets, Stars!, PBM/PBEM Diplomacy) this
pattern comes from.

Host-authoritative rounds, not a live connection: host_game_files /
join_game_files / leave_game_files, a join/welcome handshake, a
shared-variable blackboard staged per round and folded in by the host
(set_shared_var_files / get_shared_var_files / end_turn), custom messages
staged the same way (send_network_message_files), and the round/status
globals + lifecycle events below
(docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md "Proposed phases" Phases 1-2).

Hooks used: the generic per-frame hook (runtime/extension_hooks.py's
register_frame_update) -- the actual disk I/O inside it is gated to once
a second (state.POLL_INTERVAL), not every frame, since a real
network-drive round trip can cost 5-50ms and there is no live connection
to poll continuously. Also the room-change hook, migrating a live session
across change_room/restart_current_room the same way multiplayer_lan
does (M1, docs/FULL_AUDIT_2026-09-07.md). No room renderer -- this draws
nothing.
"""

PLUGIN_NAME = "File Exchange Multiplayer"

from events.event_types import EventType

from .actions import PLUGIN_ACTIONS
from .handlers import (
    PluginExecutor, _frame_update_after_update, _frame_update_before_step,
    _on_room_change,
)

_CATEGORY = "Network"

PLUGIN_EVENTS = {
    "file_session_started": EventType(
        name="file_session_started", display_name="File Session Started",
        description="A client was welcomed by the host -- global.player_id "
                        "is now set. Client-only: the host already knows "
                        "synchronously, right after \"Host a Game (File "
                        "Exchange)\" returns, that hosting worked, so this "
                        "never fires on the host.",
        category=_CATEGORY, icon="🗂️", parameters=[]),
    "player_joined_files": EventType(
        name="player_joined_files", display_name="Player Joined (Files)",
        description="A player joined the game. global.network_sender "
                        "is their number, global.network_player_name "
                        "their name.",
        category=_CATEGORY, icon="➕", parameters=[]),
    "round_resolved": EventType(
        name="round_resolved", display_name="Round Resolved",
        description="A round finished: every joined player's move (or "
                        "the round deadline) was reached and the host "
                        "published new state. Fires on every machine "
                        "once it picks up the update. "
                        "global.round_number is the new round.",
        category=_CATEGORY, icon="🔄", parameters=[]),
    "player_skipped_round": EventType(
        name="player_skipped_round", display_name="Player Skipped Round",
        description="A player's round deadline lapsed without a move "
                        "this round. global.network_sender is their "
                        "number.",
        category=_CATEGORY, icon="⏭️", parameters=[]),
    "network_message_files": EventType(
        name="network_message_files", display_name="Network Message (File Exchange)",
        description="A custom message arrived (sent with \"Send a "
                        "Network Message (File Exchange)\"). "
                        "global.network_event is its label, "
                        "global.network_data its data, "
                        "global.network_sender the sender.",
        category=_CATEGORY, icon="✉️", parameters=[]),
    "file_session_lost": EventType(
        name="file_session_lost", display_name="File Session Lost",
        description="The shared folder became unreadable -- the drive "
                        "disconnected, a permission changed, and so on.",
        category=_CATEGORY, icon="⚠️", parameters=[]),
}

PLUGIN_FRAME_UPDATES = [
    (_frame_update_before_step, "before_step"),
    (_frame_update_after_update, "after_update"),
]

# Migrates a live session across a room change instead of it being
# silently orphaned on the room object being left -- same reasoning as
# multiplayer_lan's own M1 fix (docs/FULL_AUDIT_2026-09-07.md).
PLUGIN_ROOM_CHANGE_HOOKS = [_on_room_change]
