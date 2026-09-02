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

_CATEGORY = "Réseau"

PLUGIN_EVENTS = {
    "network_started": EventType(
        name="network_started", display_name="Réseau prêt",
        description="La session réseau est établie (l'hôte a accepté ce client, "
                    "ou l'hôte a démarré). global.player_id est défini.",
        category=_CATEGORY, icon="🌐", parameters=[]),
    "player_joined": EventType(
        name="player_joined", display_name="Joueur connecté",
        description="Un joueur a rejoint la partie. global.network_sender = son "
                    "numéro, global.network_player_name = son nom.",
        category=_CATEGORY, icon="➕", parameters=[]),
    "player_left": EventType(
        name="player_left", display_name="Joueur déconnecté",
        description="Un joueur a quitté la partie. global.network_sender = son "
                    "numéro.",
        category=_CATEGORY, icon="➖", parameters=[]),
    "network_message": EventType(
        name="network_message", display_name="Message réseau",
        description="Un message personnalisé est arrivé. global.network_event = "
                    "son étiquette, global.network_data = sa donnée, "
                    "global.network_sender = l'expéditeur.",
        category=_CATEGORY, icon="✉️", parameters=[]),
    "network_game_started": EventType(
        name="network_game_started", display_name="Partie réseau démarrée",
        description="L'hôte a appelé « Démarrer la partie en réseau ». Se "
                    "déclenche sur toutes les machines.",
        category=_CATEGORY, icon="🚦", parameters=[]),
    "connection_lost": EventType(
        name="connection_lost", display_name="Connexion perdue",
        description="Le lien avec l'hôte est rompu (hôte fermé, câble débranché, "
                    "isolation Wi-Fi...).",
        category=_CATEGORY, icon="⚠️", parameters=[]),
}

PLUGIN_FRAME_UPDATES = [
    (_frame_update_apply_inbound, "before_step"),
    (_frame_update_broadcast, "after_update"),
]
