# Réseau

*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*

> **Generado automáticamente** a partir del registro de acciones del IDE mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar el generador tras cambiar las acciones. Las traducciones provienen de `tools/action_ref_i18n.py`.

### Associer une touche réseau

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `bind_network_input` |
| **Icono** | ⌨️ |
| **Categoría** | Réseau |

Associer une touche locale à une « entrée nommée » signalée à l'hôte. L'hôte teste ensuite avec « Si le joueur appuie ». Les flèches et Espace sont déjà associées ("left", "right", "up", "down", "space")

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Étiquette libre (ex. "jump", "tir") |
| `key` | Texto | — | Nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `network_spawn` |
| **Icono** | ✨ |
| **Categoría** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Type d'objet à créer |
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `owner` | Texto | `0` | Joueur qui pilote l'instance (0 = hôte). Souvent global.network_sender dans « Joueur connecté ».; opcional |
| `relative` | Sí/No | No | Position relative à l'objet qui exécute l'action; opcional |

### Définir le propriétaire de l'instance

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_instance_owner` |
| **Icono** | 🎮 |
| **Categoría** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Numéro de joueur (0 = hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Définir une variable partagée

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_shared_var` |
| **Icono** | 📤 |
| **Categoría** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Identifiant simple (lettres, chiffres, _) -- pas d'espace ni d'opérateur |
| `value` | Texto | `0` | Nombre, texte ou booléen (les objets complexes sont refusés) |

### Démarrer la partie en réseau

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `start_networked_game` |
| **Icono** | 🚦 |
| **Categoría** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Parámetros:* ninguno

### Envoyer un message réseau

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `send_network_message` |
| **Icono** | ✉️ |
| **Categoría** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | Étiquette libre que le gestionnaire teste (ex. "buzz", "reponse") |
| `data` | Texto | — | Nombre, texte, booléen ou petite liste; opcional |
| `target` | Elección | `all` | all = tout le monde ; host = l'hôte seulement; Opciones: `all`, `host` |

### Héberger une partie

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `host_game` |
| **Icono** | 🌐 |
| **Categoría** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `game_name` | Texto | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau, Phase 6); opcional |
| `max_players` | Número | `8` | Nombre maximal de joueurs, hôte compris (2 à 16); opcional |
| `port` | Número | `45782` | Port TCP -- doit être identique chez l'hôte et les clients; opcional |
| `player_name` | Texto | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); opcional |
| `show_lobby` | Sí/No | No | Afficher un écran « En attente de joueurs… » avec bouton Démarrer avant de lancer la partie; opcional |

### Lire une variable partagée

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `get_shared_var` |
| **Icono** | 📥 |
| **Categoría** | Réseau |

Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). Équivaut à lire global.<nom> directement

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Nom de la variable partagée à lire |
| `into` | Texto | — | Nom de la variable globale où écrire la valeur |

### Quitter la partie

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `leave_game` |
| **Icono** | 🚪 |
| **Categoría** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Parámetros:* ninguno

### Rejoindre une partie

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `join_game` |
| **Icono** | 🔌 |
| **Categoría** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `host` | Texto | `127.0.0.1` | Adresse IP LAN de l'hôte ("auto" = écran de connexion intégré, Phase 6); opcional |
| `port` | Número | `45782` | Port TCP -- doit correspondre à celui de l'hôte; opcional |
| `player_name` | Texto | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); opcional |

### Régler la fréquence de synchro

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_sync_rate` |
| **Icono** | ⏱️ |
| **Categoría** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `hz` | Número | `20` | 10-30 convient sur un réseau local (défaut 20); opcional |
| `interp_ms` | Número | `100` | Retard d'affichage des fantômes, en millisecondes (défaut 100); opcional |

### Set Network Mode (v1)

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `set_network_mode` |
| **Icono** | 🌐 |
| **Categoría** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `mode` | Elección | `host` | Host = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Opciones: `host`, `client` |
| `host` | Texto | `127.0.0.1` | Adresse IP LAN de l'hôte (mode Client uniquement); opcional |
| `port` | Número | `45782` | Port TCP -- doit être identique chez l'hôte et le client; opcional |

### Si je pilote cette instance

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `is_instance_owner` |
| **Icono** | ❓ |
| **Categoría** | Réseau |

Condition : vraie si CETTE machine est le propriétaire de l'instance synchronisée. À placer avant un bloc pour ne faire tourner la logique de contrôle que chez le bon joueur

*Parámetros:* ninguno

### Si le joueur appuie

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `remote_input` |
| **Icono** | ❓ |
| **Categoría** | Réseau |

Condition (chez l'hôte) : vraie si le joueur indiqué maintient l'entrée nommée. Permet à l'hôte de réagir aux touches d'un client sans posséder son avatar

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Numéro de joueur (0 = hôte) |
| `name` | Texto | — | L'entrée nommée à tester (ex. "jump") |

### Synchroniser cette instance

| Propiedad | Valor |
|----------|-------|
| **Nombre** | `sync_instance` |
| **Icono** | 🔗 |
| **Categoría** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Parámetro | Tipo | Predet. | Notas |
|-----------|------|---------|-------|
| `vars` | Texto | — | Noms de variables d'instance à répliquer aussi, séparés par des virgules (ex. "hp, couleur"); opcional |

---

## Otras Categorías

- [Movimiento](Full-Action-Reference-Movement_es) (20)
- [Instancia](Full-Action-Reference-Instance_es) (12)
- [Puntuación](Full-Action-Reference-Score_es) (11)
- [Sala](Full-Action-Reference-Room_es) (13)
- [Tiempo](Full-Action-Reference-Timing_es) (8)
- [Audio](Full-Action-Reference-Audio_es) (6)
- [Juego](Full-Action-Reference-Game_es) (25)
- [Control](Full-Action-Reference-Control_es) (19)
- [Cuadrícula](Full-Action-Reference-Grid_es) (4)
- [Vistas](Full-Action-Reference-Views_es) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_es) (16)
- [Particles](Full-Action-Reference-Particles_es) (8)

[← Volver a la Referencia Completa de Acciones](Full-Action-Reference_es)
