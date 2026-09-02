# Réseau

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Associer une touche réseau

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `bind_network_input` |
| **Ikona** | ⌨️ |
| **Kategorija** | Réseau |

Associer une touche locale à une « entrée nommée » signalée à l'hôte. L'hôte teste ensuite avec « Si le joueur appuie ». Les flèches et Espace sont déjà associées ("left", "right", "up", "down", "space")

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | Étiquette libre (ex. "jump", "tir") |
| `key` | Besedilo | — | Nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `network_spawn` |
| **Ikona** | ✨ |
| **Kategorija** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Type d'objet à créer |
| `x` | Besedilo | `0` |  |
| `y` | Besedilo | `0` |  |
| `owner` | Besedilo | `0` | Joueur qui pilote l'instance (0 = hôte). Souvent global.network_sender dans « Joueur connecté ».; neobvezno |
| `relative` | Da/Ne | Ne | Position relative à l'objet qui exécute l'action; neobvezno |

### Définir le propriétaire de l'instance

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_instance_owner` |
| **Ikona** | 🎮 |
| **Kategorija** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `player` | Besedilo | `0` | Numéro de joueur (0 = hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Définir une variable partagée

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_shared_var` |
| **Ikona** | 📤 |
| **Kategorija** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | Identifiant simple (lettres, chiffres, _) -- pas d'espace ni d'opérateur |
| `value` | Besedilo | `0` | Nombre, texte ou booléen (les objets complexes sont refusés) |

### Démarrer la partie en réseau

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_networked_game` |
| **Ikona** | 🚦 |
| **Kategorija** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Parametri:* brez

### Envoyer un message réseau

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `send_network_message` |
| **Ikona** | ✉️ |
| **Kategorija** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `event` | Besedilo | — | Étiquette libre que le gestionnaire teste (ex. "buzz", "reponse") |
| `data` | Besedilo | — | Nombre, texte, booléen ou petite liste; neobvezno |
| `target` | Izbira | `all` | all = tout le monde ; host = l'hôte seulement; Izbire: `all`, `host` |

### Héberger une partie

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `host_game` |
| **Ikona** | 🌐 |
| **Kategorija** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `game_name` | Besedilo | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau, Phase 6); neobvezno |
| `max_players` | Število | `8` | Nombre maximal de joueurs, hôte compris (2 à 16); neobvezno |
| `port` | Število | `45782` | Port TCP -- doit être identique chez l'hôte et les clients; neobvezno |
| `player_name` | Besedilo | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); neobvezno |
| `show_lobby` | Da/Ne | Ne | Afficher un écran « En attente de joueurs… » avec bouton Démarrer avant de lancer la partie; neobvezno |

### Lire une variable partagée

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `get_shared_var` |
| **Ikona** | 📥 |
| **Kategorija** | Réseau |

Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). Équivaut à lire global.<nom> directement

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | Nom de la variable partagée à lire |
| `into` | Besedilo | — | Nom de la variable globale où écrire la valeur |

### Quitter la partie

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `leave_game` |
| **Ikona** | 🚪 |
| **Kategorija** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Parametri:* brez

### Rejoindre une partie

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `join_game` |
| **Ikona** | 🔌 |
| **Kategorija** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `host` | Besedilo | `127.0.0.1` | Adresse IP LAN de l'hôte ("auto" = écran de connexion intégré, Phase 6); neobvezno |
| `port` | Število | `45782` | Port TCP -- doit correspondre à celui de l'hôte; neobvezno |
| `player_name` | Besedilo | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); neobvezno |

### Régler la fréquence de synchro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_sync_rate` |
| **Ikona** | ⏱️ |
| **Kategorija** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `hz` | Število | `20` | 10-30 convient sur un réseau local (défaut 20); neobvezno |
| `interp_ms` | Število | `100` | Retard d'affichage des fantômes, en millisecondes (défaut 100); neobvezno |

### Set Network Mode (v1)

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_network_mode` |
| **Ikona** | 🌐 |
| **Kategorija** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `mode` | Izbira | `host` | Host = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Izbire: `host`, `client` |
| `host` | Besedilo | `127.0.0.1` | Adresse IP LAN de l'hôte (mode Client uniquement); neobvezno |
| `port` | Število | `45782` | Port TCP -- doit être identique chez l'hôte et le client; neobvezno |

### Si je pilote cette instance

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `is_instance_owner` |
| **Ikona** | ❓ |
| **Kategorija** | Réseau |

Condition : vraie si CETTE machine est le propriétaire de l'instance synchronisée. À placer avant un bloc pour ne faire tourner la logique de contrôle que chez le bon joueur

*Parametri:* brez

### Si le joueur appuie

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `remote_input` |
| **Ikona** | ❓ |
| **Kategorija** | Réseau |

Condition (chez l'hôte) : vraie si le joueur indiqué maintient l'entrée nommée. Permet à l'hôte de réagir aux touches d'un client sans posséder son avatar

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `player` | Besedilo | `0` | Numéro de joueur (0 = hôte) |
| `name` | Besedilo | — | L'entrée nommée à tester (ex. "jump") |

### Synchroniser cette instance

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `sync_instance` |
| **Ikona** | 🔗 |
| **Kategorija** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `vars` | Besedilo | — | Noms de variables d'instance à répliquer aussi, séparés par des virgules (ex. "hp, couleur"); neobvezno |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Particles](Full-Action-Reference-Particles_sl) (8)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
