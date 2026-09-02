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

_CATEGORY = "Réseau"

PLUGIN_ACTIONS = {
    # -- Session lifecycle ------------------------------------------------
    "host_game": ActionType(
        name="host_game",
        display_name="Héberger une partie",
        description="Devenir l'hôte d'une partie multijoueur LAN : les autres "
                    "joueurs se connectent à cette machine. À appeler une "
                    "seule fois (par ex. dans l'événement Création du contrôleur "
                    "de la salle). Définit global.player_id = 0 et "
                    "global.network_role = \"host\".",
        category=_CATEGORY,
        icon="🌐",
        parameters=[
            ActionParameter(name="game_name", display_name="Nom de la partie",
                param_type="string", default_value="PyGameMaker", required=False,
                description="Nom affiché dans la liste des serveurs (découverte "
                            "réseau, Phase 6)"),
            ActionParameter(name="max_players", display_name="Joueurs max",
                param_type="number", default_value=8, required=False,
                description="Nombre maximal de joueurs, hôte compris (2 à 16)"),
            ActionParameter(name="port", display_name="Port", param_type="number",
                default_value=45782, required=False,
                description="Port TCP -- doit être identique chez l'hôte et les clients"),
            ActionParameter(name="player_name", display_name="Nom du joueur",
                param_type="string", default_value="", required=False,
                description="Nom de ce joueur (vide = global.player_name, ou « Joueur »)"),
        ],
    ),
    "join_game": ActionType(
        name="join_game",
        display_name="Rejoindre une partie",
        description="Se connecter à une partie multijoueur LAN hébergée par "
                    "une autre machine. global.player_id sera défini par l'hôte "
                    "(1, 2, ...). Si l'hôte est injoignable, la partie continue "
                    "en solo.",
        category=_CATEGORY,
        icon="🔌",
        parameters=[
            ActionParameter(name="host", display_name="Adresse de l'hôte",
                param_type="string", default_value="127.0.0.1", required=False,
                description="Adresse IP LAN de l'hôte (\"auto\" = écran de "
                            "connexion intégré, Phase 6)"),
            ActionParameter(name="port", display_name="Port", param_type="number",
                default_value=45782, required=False,
                description="Port TCP -- doit correspondre à celui de l'hôte"),
            ActionParameter(name="player_name", display_name="Nom du joueur",
                param_type="string", default_value="", required=False,
                description="Nom de ce joueur (vide = global.player_name, ou « Joueur »)"),
        ],
    ),
    "leave_game": ActionType(
        name="leave_game",
        display_name="Quitter la partie",
        description="Se déconnecter (ou arrêter d'héberger) et effacer les "
                    "variables réseau globales.",
        category=_CATEGORY,
        icon="🚪",
        parameters=[],
    ),
    "start_networked_game": ActionType(
        name="start_networked_game",
        display_name="Démarrer la partie en réseau",
        description="Hôte uniquement : faire sortir tout le monde du salon "
                    "d'attente et lancer la partie. Déclenche l'événement "
                    "« Partie réseau démarrée » sur toutes les machines.",
        category=_CATEGORY,
        icon="🚦",
        parameters=[],
    ),
    # -- Shared blackboard ---------------------------------------------
    "set_shared_var": ActionType(
        name="set_shared_var",
        display_name="Définir une variable partagée",
        description="Écrire une variable partagée par toutes les machines. "
                    "Chez l'hôte : appliquée immédiatement. Chez un client : "
                    "une demande envoyée à l'hôte. Lisible partout via "
                    "global.<nom>.",
        category=_CATEGORY,
        icon="📤",
        parameters=[
            ActionParameter(name="name", display_name="Nom", param_type="string",
                default_value="", description="Identifiant simple (lettres, "
                "chiffres, _) -- pas d'espace ni d'opérateur"),
            ActionParameter(name="value", display_name="Valeur", param_type="string",
                default_value="0",
                description="Nombre, texte ou booléen (les objets complexes "
                            "sont refusés)"),
        ],
    ),
    "get_shared_var": ActionType(
        name="get_shared_var",
        display_name="Lire une variable partagée",
        description="Copier une variable partagée dans une variable globale "
                    "(pour l'utiliser dans un calcul). Équivaut à lire "
                    "global.<nom> directement.",
        category=_CATEGORY,
        icon="📥",
        parameters=[
            ActionParameter(name="name", display_name="Nom partagé",
                param_type="string", default_value="",
                description="Nom de la variable partagée à lire"),
            ActionParameter(name="into", display_name="Variable globale",
                param_type="string", default_value="",
                description="Nom de la variable globale où écrire la valeur"),
        ],
    ),
    "send_network_message": ActionType(
        name="send_network_message",
        display_name="Envoyer un message réseau",
        description="Diffuser un message personnalisé. Déclenche l'événement "
                    "« Message réseau » sur les machines concernées, avec "
                    "global.network_event / global.network_data / "
                    "global.network_sender.",
        category=_CATEGORY,
        icon="✉️",
        parameters=[
            ActionParameter(name="event", display_name="Nom du message",
                param_type="string", default_value="",
                description="Étiquette libre que le gestionnaire teste "
                            "(ex. \"buzz\", \"reponse\")"),
            ActionParameter(name="data", display_name="Donnée", param_type="string",
                default_value="", required=False,
                description="Nombre, texte, booléen ou petite liste"),
            ActionParameter(name="target", display_name="Destinataire",
                param_type="choice", default_value="all", choices=["all", "host"],
                description="all = tout le monde ; host = l'hôte seulement"),
        ],
    ),
    # -- Tier B: networked instances -------------------------------
    "network_spawn": ActionType(
        name="network_spawn",
        display_name="Créer un objet réseau",
        description="Hôte uniquement : créer une instance qui apparaît "
                    "automatiquement chez tous les clients (comme des « fantômes » "
                    "interpolés). Sans effet chez un client. L'instance créée est "
                    "pilotée par l'hôte -- guardez sa logique de jeu par "
                    "global.is_host == 1.",
        category=_CATEGORY,
        icon="✨",
        parameters=[
            ActionParameter(name="object", display_name="Objet", param_type="object",
                default_value="", description="Type d'objet à créer"),
            ActionParameter(name="x", display_name="X", param_type="string",
                default_value="0"),
            ActionParameter(name="y", display_name="Y", param_type="string",
                default_value="0"),
            ActionParameter(name="relative", display_name="Relatif",
                param_type="boolean", default_value=False, required=False,
                description="Position relative à l'objet qui exécute l'action"),
        ],
    ),
    "set_sync_rate": ActionType(
        name="set_sync_rate",
        display_name="Régler la fréquence de synchro",
        description="Ajuster la cadence des instantanés de l'hôte et le délai "
                    "d'interpolation des clients. À appeler une fois chez l'hôte "
                    "(et chez les clients pour le délai).",
        category=_CATEGORY,
        icon="⏱️",
        parameters=[
            ActionParameter(name="hz", display_name="Instantanés / seconde",
                param_type="number", default_value=20, required=False,
                description="10-30 convient sur un réseau local (défaut 20)"),
            ActionParameter(name="interp_ms", display_name="Interpolation (ms)",
                param_type="number", default_value=100, required=False,
                description="Retard d'affichage des fantômes, en millisecondes "
                            "(défaut 100)"),
        ],
    ),
    # -- v1 back-compat -----------------------------------------------
    "set_network_mode": ActionType(
        name="set_network_mode",
        display_name="Set Network Mode (v1)",
        description="Ancienne action bas niveau : démarre la salle en mode "
                    "hôte ou client (spectateur seulement -- l'entrée du "
                    "client n'a aucun effet). Préférez « Héberger une partie » "
                    "/ « Rejoindre une partie ». Conservée pour les projets "
                    "existants et les drapeaux --net-host / --net-client.",
        category=_CATEGORY,
        icon="🌐",
        parameters=[
            ActionParameter(name="mode", display_name="Mode", param_type="choice",
                default_value="host", choices=["host", "client"],
                description="Host = les autres se connectent à vous ; Client = "
                            "vous vous connectez à un hôte"),
            ActionParameter(name="host", display_name="Host Address",
                param_type="string", default_value="127.0.0.1", required=False,
                description="Adresse IP LAN de l'hôte (mode Client uniquement)"),
            ActionParameter(name="port", display_name="Port", param_type="number",
                default_value=45782, required=False,
                description="Port TCP -- doit être identique chez l'hôte et le client"),
        ],
    ),
}
