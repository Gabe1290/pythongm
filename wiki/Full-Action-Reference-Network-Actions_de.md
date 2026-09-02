# Réseau

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Associer une touche réseau

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `bind_network_input` |
| **Symbol** | ⌨️ |
| **Kategorie** | Réseau |

Associer une touche locale à une « entrée nommée » signalée à l'hôte. L'hôte teste ensuite avec « Si le joueur appuie ». Les flèches et Espace sont déjà associées ("left", "right", "up", "down", "space")

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | Étiquette libre (ex. "jump", "tir") |
| `key` | Text | — | Nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `network_spawn` |
| **Symbol** | ✨ |
| **Kategorie** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | Type d'objet à créer |
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `owner` | Text | `0` | Joueur qui pilote l'instance (0 = hôte). Souvent global.network_sender dans « Joueur connecté ».; optional |
| `relative` | Ja/Nein | Nein | Position relative à l'objet qui exécute l'action; optional |

### Définir le propriétaire de l'instance

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_instance_owner` |
| **Symbol** | 🎮 |
| **Kategorie** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `player` | Text | `0` | Numéro de joueur (0 = hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Définir une variable partagée

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_shared_var` |
| **Symbol** | 📤 |
| **Kategorie** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | Identifiant simple (lettres, chiffres, _) -- pas d'espace ni d'opérateur |
| `value` | Text | `0` | Nombre, texte ou booléen (les objets complexes sont refusés) |

### Démarrer la partie en réseau

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_networked_game` |
| **Symbol** | 🚦 |
| **Kategorie** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Parameter:* keine

### Envoyer un message réseau

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `send_network_message` |
| **Symbol** | ✉️ |
| **Kategorie** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `event` | Text | — | Étiquette libre que le gestionnaire teste (ex. "buzz", "reponse") |
| `data` | Text | — | Nombre, texte, booléen ou petite liste; optional |
| `target` | Auswahl | `all` | all = tout le monde ; host = l'hôte seulement; Auswahl: `all`, `host` |

### Héberger une partie

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `host_game` |
| **Symbol** | 🌐 |
| **Kategorie** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `game_name` | Text | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau, Phase 6); optional |
| `max_players` | Zahl | `8` | Nombre maximal de joueurs, hôte compris (2 à 16); optional |
| `port` | Zahl | `45782` | Port TCP -- doit être identique chez l'hôte et les clients; optional |
| `player_name` | Text | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); optional |
| `show_lobby` | Ja/Nein | Nein | Afficher un écran « En attente de joueurs… » avec bouton Démarrer avant de lancer la partie; optional |

### Lire une variable partagée

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `get_shared_var` |
| **Symbol** | 📥 |
| **Kategorie** | Réseau |

Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). Équivaut à lire global.<nom> directement

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | Nom de la variable partagée à lire |
| `into` | Text | — | Nom de la variable globale où écrire la valeur |

### Quitter la partie

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `leave_game` |
| **Symbol** | 🚪 |
| **Kategorie** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Parameter:* keine

### Rejoindre une partie

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `join_game` |
| **Symbol** | 🔌 |
| **Kategorie** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `host` | Text | `127.0.0.1` | Adresse IP LAN de l'hôte ("auto" = écran de connexion intégré, Phase 6); optional |
| `port` | Zahl | `45782` | Port TCP -- doit correspondre à celui de l'hôte; optional |
| `player_name` | Text | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); optional |

### Régler la fréquence de synchro

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_sync_rate` |
| **Symbol** | ⏱️ |
| **Kategorie** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `hz` | Zahl | `20` | 10-30 convient sur un réseau local (défaut 20); optional |
| `interp_ms` | Zahl | `100` | Retard d'affichage des fantômes, en millisecondes (défaut 100); optional |

### Set Network Mode (v1)

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_network_mode` |
| **Symbol** | 🌐 |
| **Kategorie** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `mode` | Auswahl | `host` | Host = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Auswahl: `host`, `client` |
| `host` | Text | `127.0.0.1` | Adresse IP LAN de l'hôte (mode Client uniquement); optional |
| `port` | Zahl | `45782` | Port TCP -- doit être identique chez l'hôte et le client; optional |

### Si je pilote cette instance

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `is_instance_owner` |
| **Symbol** | ❓ |
| **Kategorie** | Réseau |

Condition : vraie si CETTE machine est le propriétaire de l'instance synchronisée. À placer avant un bloc pour ne faire tourner la logique de contrôle que chez le bon joueur

*Parameter:* keine

### Si le joueur appuie

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `remote_input` |
| **Symbol** | ❓ |
| **Kategorie** | Réseau |

Condition (chez l'hôte) : vraie si le joueur indiqué maintient l'entrée nommée. Permet à l'hôte de réagir aux touches d'un client sans posséder son avatar

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `player` | Text | `0` | Numéro de joueur (0 = hôte) |
| `name` | Text | — | L'entrée nommée à tester (ex. "jump") |

### Synchroniser cette instance

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `sync_instance` |
| **Symbol** | 🔗 |
| **Kategorie** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `vars` | Text | — | Noms de variables d'instance à répliquer aussi, séparés par des virgules (ex. "hp, couleur"); optional |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Particles](Full-Action-Reference-Particles_de) (8)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
