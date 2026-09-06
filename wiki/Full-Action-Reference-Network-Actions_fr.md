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
| `name` | Texte | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Texte | — | A key name: "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `network_spawn` |
| **Icône** | ✨ |
| **Catégorie** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | The type of object to create |
| `x` | Texte | `0` |  |
| `y` | Texte | `0` |  |
| `owner` | Texte | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; optionnel |
| `relative` | Oui/Non | Non | Position relative to the object running the action; optionnel |

### Héberger une partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `host_game` |
| **Icône** | 🌐 |
| **Catégorie** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `game_name` | Texte | `PyGameMaker` | Name shown in the server list (network discovery); optionnel |
| `max_players` | Nombre | `8` | Largest number of players, host included (2 to 16); optionnel |
| `port` | Nombre | `45782` | TCP port -- must be the same on the host and every client; optionnel |
| `player_name` | Texte | — | This player's name (empty = global.player_name, or "Player"); optionnel |
| `show_lobby` | Oui/Non | Non | Show a "Waiting for players..." screen with a Start button before the game begins; optionnel |

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
| `player` | Texte | `0` | Player number (0 = host) |
| `name` | Texte | — | The named input to test (e.g. "jump") |

### Rejoindre une partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `join_game` |
| **Icône** | 🔌 |
| **Catégorie** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `host` | Texte | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); optionnel |
| `port` | Nombre | `45782` | TCP port -- must match the host's; optionnel |
| `player_name` | Texte | — | This player's name (empty = global.player_name, or "Player"); optionnel |

### Quitter la partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `leave_game` |
| **Icône** | 🚪 |
| **Catégorie** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

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
| `name` | Texte | — | Name of the shared variable to read |
| `into` | Texte | — | Name of the global variable to write the value into |

### Envoyer un message réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `send_network_message` |
| **Icône** | ✉️ |
| **Catégorie** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `event` | Texte | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Texte | — | A number, text, true/false, or a short list; optionnel |
| `target` | Choix | `all` | all = everyone; host = the host only; Choix: `all`, `host` |

### Set Network Mode (v1)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_network_mode` |
| **Icône** | 🌐 |
| **Catégorie** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `mode` | Choix | `host` | Host = others connect to you; Client = you connect to a host; Choix: `host`, `client` |
| `host` | Texte | `127.0.0.1` | The host's LAN IP address (Client mode only); optionnel |
| `port` | Nombre | `45782` | TCP port -- must be the same on the host and the client; optionnel |

### Définir une variable partagée

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_shared_var` |
| **Icône** | 📤 |
| **Catégorie** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `name` | Texte | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Texte | `0` | A number, text or true/false (complex objects are refused) |

### Définir le propriétaire de l'instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_instance_owner` |
| **Icône** | 🎮 |
| **Catégorie** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `player` | Texte | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Régler la fréquence de synchro

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_sync_rate` |
| **Icône** | ⏱️ |
| **Catégorie** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `hz` | Nombre | `20` | 10-30 works well on a local network (default 20); optionnel |
| `interp_ms` | Nombre | `100` | How far behind ghosts are drawn, in milliseconds (default 100); optionnel |

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
| `vars` | Texte | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); optionnel |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (25)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (16)
- [Particules](Full-Action-Reference-Particles_fr) (8)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
