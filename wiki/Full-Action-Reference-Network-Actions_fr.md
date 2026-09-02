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
| `name` | Texte | — | Étiquette libre (ex. "jump", "tir") |
| `key` | Texte | — | Nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `network_spawn` |
| **Icône** | ✨ |
| **Catégorie** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | Type d'objet à créer |
| `x` | Texte | `0` |  |
| `y` | Texte | `0` |  |
| `owner` | Texte | `0` | Joueur qui pilote l'instance (0 = hôte). Souvent global.network_sender dans « Joueur connecté ».; optionnel |
| `relative` | Oui/Non | Non | Position relative à l'objet qui exécute l'action; optionnel |

### Définir le propriétaire de l'instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_instance_owner` |
| **Icône** | 🎮 |
| **Catégorie** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `player` | Texte | `0` | Numéro de joueur (0 = hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Définir une variable partagée

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_shared_var` |
| **Icône** | 📤 |
| **Catégorie** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `name` | Texte | — | Identifiant simple (lettres, chiffres, _) -- pas d'espace ni d'opérateur |
| `value` | Texte | `0` | Nombre, texte ou booléen (les objets complexes sont refusés) |

### Démarrer la partie en réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `start_networked_game` |
| **Icône** | 🚦 |
| **Catégorie** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Paramètres:* aucun

### Envoyer un message réseau

| Propriété | Valeur |
|----------|-------|
| **Nom** | `send_network_message` |
| **Icône** | ✉️ |
| **Catégorie** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `event` | Texte | — | Étiquette libre que le gestionnaire teste (ex. "buzz", "reponse") |
| `data` | Texte | — | Nombre, texte, booléen ou petite liste; optionnel |
| `target` | Choix | `all` | all = tout le monde ; host = l'hôte seulement; Choix: `all`, `host` |

### Héberger une partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `host_game` |
| **Icône** | 🌐 |
| **Catégorie** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `game_name` | Texte | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau, Phase 6); optionnel |
| `max_players` | Nombre | `8` | Nombre maximal de joueurs, hôte compris (2 à 16); optionnel |
| `port` | Nombre | `45782` | Port TCP -- doit être identique chez l'hôte et les clients; optionnel |
| `player_name` | Texte | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); optionnel |
| `show_lobby` | Oui/Non | Non | Afficher un écran « En attente de joueurs… » avec bouton Démarrer avant de lancer la partie; optionnel |

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
| `into` | Texte | — | Nom de la variable globale où écrire la valeur |

### Quitter la partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `leave_game` |
| **Icône** | 🚪 |
| **Catégorie** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Paramètres:* aucun

### Rejoindre une partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `join_game` |
| **Icône** | 🔌 |
| **Catégorie** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `host` | Texte | `127.0.0.1` | Adresse IP LAN de l'hôte ("auto" = écran de connexion intégré, Phase 6); optionnel |
| `port` | Nombre | `45782` | Port TCP -- doit correspondre à celui de l'hôte; optionnel |
| `player_name` | Texte | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); optionnel |

### Régler la fréquence de synchro

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_sync_rate` |
| **Icône** | ⏱️ |
| **Catégorie** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `hz` | Nombre | `20` | 10-30 convient sur un réseau local (défaut 20); optionnel |
| `interp_ms` | Nombre | `100` | Retard d'affichage des fantômes, en millisecondes (défaut 100); optionnel |

### Set Network Mode (v1)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_network_mode` |
| **Icône** | 🌐 |
| **Catégorie** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `mode` | Choix | `host` | Host = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Choix: `host`, `client` |
| `host` | Texte | `127.0.0.1` | Adresse IP LAN de l'hôte (mode Client uniquement); optionnel |
| `port` | Nombre | `45782` | Port TCP -- doit être identique chez l'hôte et le client; optionnel |

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
| `player` | Texte | `0` | Numéro de joueur (0 = hôte) |
| `name` | Texte | — | L'entrée nommée à tester (ex. "jump") |

### Synchroniser cette instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `sync_instance` |
| **Icône** | 🔗 |
| **Catégorie** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `vars` | Texte | — | Noms de variables d'instance à répliquer aussi, séparés par des virgules (ex. "hp, couleur"); optionnel |

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
- [Particles](Full-Action-Reference-Particles_fr) (8)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
