# Réseau

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Associer une touche réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `bind_network_input` |
| **Icône** | ⌨️ |
| **Catégorie** | Réseau |

Associer une touche locale à une « entrée nommée » signalée à l'hôte. L'hôte teste ensuite avec « Si le joueur appuie ». Les flèches et Espace sont déjà associées ("left", "right", "up", "down", "space")

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `name` | Texte | — | Un nom de votre choix (par ex. "jump", "fire") |
| `key` | Texte | — | Un nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `network_spawn` |
| **Icône** | ✨ |
| **Catégorie** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | Le type d'objet à créer |
| `x` | Texte | `0` |  |
| `y` | Texte | `0` |  |
| `owner` | Texte | `0` | Le joueur qui pilote cette instance (0 = l'hôte). Souvent global.network_sender dans « Joueur connecté ».; optionnel |
| `relative` | Oui/Non | Non | Position relative à l'objet qui exécute l'action; optionnel |

### End Turn (File Exchange)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `end_turn` |
| **Icône** | ✅ |
| **Catégorie** | Réseau |

Submit your move for this round: whatever you staged with "Set a Shared Variable (File Exchange)" since your last turn, written as one file for the host to pick up. Call it once per round -- even with nothing staged -- if this game expects every player to respond every round; a player who never calls it is skipped once the round deadline passes

*Paramètres:* aucun

### Héberger une partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `host_game` |
| **Icône** | 🌐 |
| **Catégorie** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `game_name` | Texte | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau); optionnel |
| `max_players` | Nombre | `8` | Nombre maximal de joueurs, hôte compris (de 2 à 16); optionnel |
| `port` | Nombre | `45782` | Port TCP — doit être le même chez l'hôte et chez chaque client; optionnel |
| `player_name` | Texte | — | Nom de ce joueur (vide = global.player_name, sinon "Player"); optionnel |
| `show_lobby` | Oui/Non | Non | Afficher un écran « En attente de joueurs... » avec un bouton Démarrer avant le début de la partie; optionnel |

### Host a Game (File Exchange)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `host_game_files` |
| **Icône** | 🗂️ |
| **Catégorie** | Réseau |

Become the host of a turn-based game played over a shared folder instead of a live connection -- works through a school firewall that blocks direct connections between machines. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.is_host = 1

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `folder` | Texte | — | Path to a folder both machines can reach (a mapped network drive, a synced Dropbox/OneDrive folder, ...) |
| `max_players` | Nombre | `8` | Nombre maximal de joueurs, hôte compris (de 2 à 16); optionnel |
| `player_name` | Texte | — | Nom de ce joueur (vide = global.player_name, sinon "Player"); optionnel |
| `round_deadline` | Nombre | `30` | How long to wait for every joined player's move before advancing the round anyway (a missing player is skipped that round, not left blocking the game forever); optionnel |
| `show_lobby` | Oui/Non | Non | Show a "Waiting for players..." screen with a Start button before handing control back to the game; optionnel |

### Si je pilote cette instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `is_instance_owner` |
| **Icône** | ❓ |
| **Catégorie** | Réseau |

Condition : vraie si CETTE machine est le propriétaire de l'instance synchronisée. À placer avant un bloc pour ne faire tourner la logique de contrôle que chez le bon joueur

*Paramètres:* aucun

### Si le joueur appuie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `remote_input` |
| **Icône** | ❓ |
| **Catégorie** | Réseau |

Condition (chez l'hôte) : vraie si le joueur indiqué maintient l'entrée nommée. Permet à l'hôte de réagir aux touches d'un client sans posséder son avatar

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `player` | Texte | `0` | Numéro de joueur (0 = l'hôte) |
| `name` | Texte | — | L'entrée nommée à tester (par ex. "jump") |

### Rejoindre une partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `join_game` |
| **Icône** | 🔌 |
| **Catégorie** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `host` | Texte | `127.0.0.1` | Adresse IP de l'hôte sur le réseau local ("auto" ouvre l'écran de connexion intégré); optionnel |
| `port` | Nombre | `45782` | Port TCP — doit correspondre à celui de l'hôte; optionnel |
| `player_name` | Texte | — | Nom de ce joueur (vide = global.player_name, sinon "Player"); optionnel |

### Join a Game (File Exchange)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `join_game_files` |
| **Icône** | 🔌 |
| **Catégorie** | Réseau |

Join a turn-based game hosted by another machine through a shared folder. The host assigns global.player_id (1, 2, ...)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `folder` | Texte | — | Path to the SAME shared folder the host used ("auto" opens the built-in screen to type it in) |
| `player_name` | Texte | — | Nom de ce joueur (vide = global.player_name, sinon "Player"); optionnel |

### Quitter la partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `leave_game` |
| **Icône** | 🚪 |
| **Catégorie** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Paramètres:* aucun

### Leave the Game (File Exchange)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `leave_game_files` |
| **Icône** | 🚪 |
| **Catégorie** | Réseau |

Stop hosting or leave the game, and clear the global status variables

*Paramètres:* aucun

### Lire une variable partagée

| Propriété | Valeur |
|----------|-------|
| **Nom** | `get_shared_var` |
| **Icône** | 📥 |
| **Catégorie** | Réseau |

Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). Équivaut à lire global.<nom> directement

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `name` | Texte | — | Nom de la variable partagée à lire |
| `into` | Texte | — | Nom de la variable globale dans laquelle écrire la valeur |

### Read a Shared Variable (File Exchange)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `get_shared_var_files` |
| **Icône** | 📥 |
| **Catégorie** | Réseau |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly -- the value as of the last round the host published, not live

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `name` | Texte | — | Nom de la variable partagée à lire |
| `into` | Texte | — | Nom de la variable globale dans laquelle écrire la valeur |

### Envoyer un message réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `send_network_message` |
| **Icône** | ✉️ |
| **Catégorie** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `event` | Texte | — | Un nom de votre choix que le gestionnaire teste (par ex. "buzz", "answer") |
| `data` | Texte | — | Un nombre, du texte, true/false ou une courte liste; optionnel |
| `target` | Choix | `all` | all = tout le monde ; host = l'hôte uniquement; Choix: `all`, `host` |

### Send a Network Message (File Exchange)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `send_network_message_files` |
| **Icône** | ✉️ |
| **Catégorie** | Réseau |

Stage a message of your own, delivered the same way "Set a Shared Variable (File Exchange)" is -- at the next round boundary, not instantly. Fires the "Network Message (File Exchange)" event, with global.network_event / global.network_data / global.network_sender

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `event` | Texte | — | Un nom de votre choix que le gestionnaire teste (par ex. "buzz", "answer") |
| `data` | Texte | — | Un nombre, du texte, true/false ou une courte liste; optionnel |
| `target` | Choix | `all` | all = everyone, once they pick up the next round; host = the host only, processed immediately when the round resolves; Choix: `all`, `host` |

### Set Network Mode (v1)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_network_mode` |
| **Icône** | 🌐 |
| **Catégorie** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `mode` | Choix | `host` | Hôte = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Choix: `host`, `client` |
| `host` | Texte | `127.0.0.1` | Adresse IP de l'hôte sur le réseau local (mode Client uniquement); optionnel |
| `port` | Nombre | `45782` | Port TCP — doit être le même chez l'hôte et chez le client; optionnel |

### Définir une variable partagée

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_shared_var` |
| **Icône** | 📤 |
| **Catégorie** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `name` | Texte | — | Un identifiant simple (lettres, chiffres, _) — ni espaces ni opérateurs |
| `value` | Texte | `0` | Un nombre, du texte ou true/false (les objets complexes sont refusés) |

### Set a Shared Variable (File Exchange)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_shared_var_files` |
| **Icône** | 📤 |
| **Catégorie** | Réseau |

Stage a variable to publish to everyone. It takes effect once you call "End Turn" and the host folds your move into the next round -- not immediately, since there is no live connection to write over. Readable anywhere as global.<name> once published

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `name` | Texte | — | Un identifiant simple (lettres, chiffres, _) — ni espaces ni opérateurs |
| `value` | Texte | `0` | Un nombre, du texte ou true/false (les objets complexes sont refusés) |

### Définir le propriétaire de l'instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_instance_owner` |
| **Icône** | 🎮 |
| **Catégorie** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `player` | Texte | `0` | Numéro de joueur (0 = l'hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Régler la fréquence de synchro

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_sync_rate` |
| **Icône** | ⏱️ |
| **Catégorie** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `hz` | Nombre | `20` | De 10 à 30 fonctionne bien sur un réseau local (20 par défaut); optionnel |
| `interp_ms` | Nombre | `100` | Retard de dessin des fantômes, en millisecondes (100 par défaut); optionnel |

### Démarrer la partie en réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `start_networked_game` |
| **Icône** | 🚦 |
| **Catégorie** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Paramètres:* aucun

### Synchroniser cette instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `sync_instance` |
| **Icône** | 🔗 |
| **Catégorie** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `vars` | Texte | — | Noms des variables d'instance à copier également, séparés par des virgules (par ex. "hp, colour"); optionnel |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (21)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (6)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (14)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (3)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (18)
- [Dessin](Full-Action-Reference-Drawing_fr) (11)
- [Particules](Full-Action-Reference-Particles_fr) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_fr) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_fr) (16)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
