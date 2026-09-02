# Réseau

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Associer une touche réseau

| Proprietà | Valore |
|----------|-------|
| **Nome** | `bind_network_input` |
| **Icona** | ⌨️ |
| **Categoria** | Réseau |

Associer une touche locale à une « entrée nommée » signalée à l'hôte. L'hôte teste ensuite avec « Si le joueur appuie ». Les flèches et Espace sont déjà associées ("left", "right", "up", "down", "space")

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | Étiquette libre (ex. "jump", "tir") |
| `key` | Testo | — | Nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Proprietà | Valore |
|----------|-------|
| **Nome** | `network_spawn` |
| **Icona** | ✨ |
| **Categoria** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Type d'objet à créer |
| `x` | Testo | `0` |  |
| `y` | Testo | `0` |  |
| `owner` | Testo | `0` | Joueur qui pilote l'instance (0 = hôte). Souvent global.network_sender dans « Joueur connecté ».; facoltativo |
| `relative` | Sì/No | No | Position relative à l'objet qui exécute l'action; facoltativo |

### Définir le propriétaire de l'instance

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_instance_owner` |
| **Icona** | 🎮 |
| **Categoria** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `player` | Testo | `0` | Numéro de joueur (0 = hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Définir une variable partagée

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_shared_var` |
| **Icona** | 📤 |
| **Categoria** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | Identifiant simple (lettres, chiffres, _) -- pas d'espace ni d'opérateur |
| `value` | Testo | `0` | Nombre, texte ou booléen (les objets complexes sont refusés) |

### Démarrer la partie en réseau

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_networked_game` |
| **Icona** | 🚦 |
| **Categoria** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Parametri:* nessuno

### Envoyer un message réseau

| Proprietà | Valore |
|----------|-------|
| **Nome** | `send_network_message` |
| **Icona** | ✉️ |
| **Categoria** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `event` | Testo | — | Étiquette libre que le gestionnaire teste (ex. "buzz", "reponse") |
| `data` | Testo | — | Nombre, texte, booléen ou petite liste; facoltativo |
| `target` | Scelta | `all` | all = tout le monde ; host = l'hôte seulement; Scelte: `all`, `host` |

### Héberger une partie

| Proprietà | Valore |
|----------|-------|
| **Nome** | `host_game` |
| **Icona** | 🌐 |
| **Categoria** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `game_name` | Testo | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau, Phase 6); facoltativo |
| `max_players` | Numero | `8` | Nombre maximal de joueurs, hôte compris (2 à 16); facoltativo |
| `port` | Numero | `45782` | Port TCP -- doit être identique chez l'hôte et les clients; facoltativo |
| `player_name` | Testo | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); facoltativo |
| `show_lobby` | Sì/No | No | Afficher un écran « En attente de joueurs… » avec bouton Démarrer avant de lancer la partie; facoltativo |

### Lire une variable partagée

| Proprietà | Valore |
|----------|-------|
| **Nome** | `get_shared_var` |
| **Icona** | 📥 |
| **Categoria** | Réseau |

Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). Équivaut à lire global.<nom> directement

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `name` | Testo | — | Nom de la variable partagée à lire |
| `into` | Testo | — | Nom de la variable globale où écrire la valeur |

### Quitter la partie

| Proprietà | Valore |
|----------|-------|
| **Nome** | `leave_game` |
| **Icona** | 🚪 |
| **Categoria** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Parametri:* nessuno

### Rejoindre une partie

| Proprietà | Valore |
|----------|-------|
| **Nome** | `join_game` |
| **Icona** | 🔌 |
| **Categoria** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `host` | Testo | `127.0.0.1` | Adresse IP LAN de l'hôte ("auto" = écran de connexion intégré, Phase 6); facoltativo |
| `port` | Numero | `45782` | Port TCP -- doit correspondre à celui de l'hôte; facoltativo |
| `player_name` | Testo | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); facoltativo |

### Régler la fréquence de synchro

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_sync_rate` |
| **Icona** | ⏱️ |
| **Categoria** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `hz` | Numero | `20` | 10-30 convient sur un réseau local (défaut 20); facoltativo |
| `interp_ms` | Numero | `100` | Retard d'affichage des fantômes, en millisecondes (défaut 100); facoltativo |

### Set Network Mode (v1)

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_network_mode` |
| **Icona** | 🌐 |
| **Categoria** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `mode` | Scelta | `host` | Host = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Scelte: `host`, `client` |
| `host` | Testo | `127.0.0.1` | Adresse IP LAN de l'hôte (mode Client uniquement); facoltativo |
| `port` | Numero | `45782` | Port TCP -- doit être identique chez l'hôte et le client; facoltativo |

### Si je pilote cette instance

| Proprietà | Valore |
|----------|-------|
| **Nome** | `is_instance_owner` |
| **Icona** | ❓ |
| **Categoria** | Réseau |

Condition : vraie si CETTE machine est le propriétaire de l'instance synchronisée. À placer avant un bloc pour ne faire tourner la logique de contrôle que chez le bon joueur

*Parametri:* nessuno

### Si le joueur appuie

| Proprietà | Valore |
|----------|-------|
| **Nome** | `remote_input` |
| **Icona** | ❓ |
| **Categoria** | Réseau |

Condition (chez l'hôte) : vraie si le joueur indiqué maintient l'entrée nommée. Permet à l'hôte de réagir aux touches d'un client sans posséder son avatar

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `player` | Testo | `0` | Numéro de joueur (0 = hôte) |
| `name` | Testo | — | L'entrée nommée à tester (ex. "jump") |

### Synchroniser cette instance

| Proprietà | Valore |
|----------|-------|
| **Nome** | `sync_instance` |
| **Icona** | 🔗 |
| **Categoria** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `vars` | Testo | — | Noms de variables d'instance à répliquer aussi, séparés par des virgules (ex. "hp, couleur"); facoltativo |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (25)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (16)
- [Particles](Full-Action-Reference-Particles_it) (8)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
