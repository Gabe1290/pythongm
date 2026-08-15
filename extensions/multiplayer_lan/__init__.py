#!/usr/bin/env python3
"""LAN multiplayer: authoritative-host position sync over TCP.

See docs/MULTIPLAYER_LAN_PLAN.md for the full plan and design record. A
vertical slice only -- "see where the other player is," not a full
networked-physics model. No client prediction, no interpolation, no
custom-variable sync, no anti-cheat, no NAT traversal (LAN only, by
design). See the plan doc's "Explicitly out of scope" section for the
complete list of what this deliberately does not do.

The one hook this extension needs is NOT a room renderer (it draws
nothing) -- it's the generic per-frame hook
(runtime/extension_hooks.py's register_frame_update, built as this plan's
own Phase 0) that lets it run unconditionally every frame: a client must
apply inbound network state before Step events run against it, and a host
must broadcast only after a frame's state has fully settled.
"""

PLUGIN_NAME = "LAN Multiplayer"

from .actions import PLUGIN_ACTIONS
from .handlers import PluginExecutor, _frame_update_apply_inbound, _frame_update_broadcast

PLUGIN_FRAME_UPDATES = [
    (_frame_update_apply_inbound, "before_step"),
    (_frame_update_broadcast, "after_update"),
]
