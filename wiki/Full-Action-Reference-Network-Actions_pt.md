# Réseau

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Associer une touche réseau

| Propriedade | Valor |
|----------|-------|
| **Nome** | `bind_network_input` |
| **Ícone** | ⌨️ |
| **Categoria** | Réseau |

Associer une touche locale à une « entrée nommée » signalée à l'hôte. L'hôte teste ensuite avec « Si le joueur appuie ». Les flèches et Espace sont déjà associées ("left", "right", "up", "down", "space")

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Étiquette libre (ex. "jump", "tir") |
| `key` | Texto | — | Nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Propriedade | Valor |
|----------|-------|
| **Nome** | `network_spawn` |
| **Ícone** | ✨ |
| **Categoria** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Type d'objet à créer |
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `owner` | Texto | `0` | Joueur qui pilote l'instance (0 = hôte). Souvent global.network_sender dans « Joueur connecté ».; opcional |
| `relative` | Sim/Não | Não | Position relative à l'objet qui exécute l'action; opcional |

### Définir le propriétaire de l'instance

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_instance_owner` |
| **Ícone** | 🎮 |
| **Categoria** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Numéro de joueur (0 = hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Définir une variable partagée

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_shared_var` |
| **Ícone** | 📤 |
| **Categoria** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Identifiant simple (lettres, chiffres, _) -- pas d'espace ni d'opérateur |
| `value` | Texto | `0` | Nombre, texte ou booléen (les objets complexes sont refusés) |

### Démarrer la partie en réseau

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_networked_game` |
| **Ícone** | 🚦 |
| **Categoria** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Parâmetros:* nenhum

### Envoyer un message réseau

| Propriedade | Valor |
|----------|-------|
| **Nome** | `send_network_message` |
| **Ícone** | ✉️ |
| **Categoria** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | Étiquette libre que le gestionnaire teste (ex. "buzz", "reponse") |
| `data` | Texto | — | Nombre, texte, booléen ou petite liste; opcional |
| `target` | Escolha | `all` | all = tout le monde ; host = l'hôte seulement; Opções: `all`, `host` |

### Héberger une partie

| Propriedade | Valor |
|----------|-------|
| **Nome** | `host_game` |
| **Ícone** | 🌐 |
| **Categoria** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `game_name` | Texto | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau, Phase 6); opcional |
| `max_players` | Número | `8` | Nombre maximal de joueurs, hôte compris (2 à 16); opcional |
| `port` | Número | `45782` | Port TCP -- doit être identique chez l'hôte et les clients; opcional |
| `player_name` | Texto | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); opcional |
| `show_lobby` | Sim/Não | Não | Afficher un écran « En attente de joueurs… » avec bouton Démarrer avant de lancer la partie; opcional |

### Lire une variable partagée

| Propriedade | Valor |
|----------|-------|
| **Nome** | `get_shared_var` |
| **Ícone** | 📥 |
| **Categoria** | Réseau |

Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). Équivaut à lire global.<nom> directement

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Nom de la variable partagée à lire |
| `into` | Texto | — | Nom de la variable globale où écrire la valeur |

### Quitter la partie

| Propriedade | Valor |
|----------|-------|
| **Nome** | `leave_game` |
| **Ícone** | 🚪 |
| **Categoria** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Parâmetros:* nenhum

### Rejoindre une partie

| Propriedade | Valor |
|----------|-------|
| **Nome** | `join_game` |
| **Ícone** | 🔌 |
| **Categoria** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `host` | Texto | `127.0.0.1` | Adresse IP LAN de l'hôte ("auto" = écran de connexion intégré, Phase 6); opcional |
| `port` | Número | `45782` | Port TCP -- doit correspondre à celui de l'hôte; opcional |
| `player_name` | Texto | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); opcional |

### Régler la fréquence de synchro

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_sync_rate` |
| **Ícone** | ⏱️ |
| **Categoria** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `hz` | Número | `20` | 10-30 convient sur un réseau local (défaut 20); opcional |
| `interp_ms` | Número | `100` | Retard d'affichage des fantômes, en millisecondes (défaut 100); opcional |

### Set Network Mode (v1)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_network_mode` |
| **Ícone** | 🌐 |
| **Categoria** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `mode` | Escolha | `host` | Host = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Opções: `host`, `client` |
| `host` | Texto | `127.0.0.1` | Adresse IP LAN de l'hôte (mode Client uniquement); opcional |
| `port` | Número | `45782` | Port TCP -- doit être identique chez l'hôte et le client; opcional |

### Si je pilote cette instance

| Propriedade | Valor |
|----------|-------|
| **Nome** | `is_instance_owner` |
| **Ícone** | ❓ |
| **Categoria** | Réseau |

Condition : vraie si CETTE machine est le propriétaire de l'instance synchronisée. À placer avant un bloc pour ne faire tourner la logique de contrôle que chez le bon joueur

*Parâmetros:* nenhum

### Si le joueur appuie

| Propriedade | Valor |
|----------|-------|
| **Nome** | `remote_input` |
| **Ícone** | ❓ |
| **Categoria** | Réseau |

Condition (chez l'hôte) : vraie si le joueur indiqué maintient l'entrée nommée. Permet à l'hôte de réagir aux touches d'un client sans posséder son avatar

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Numéro de joueur (0 = hôte) |
| `name` | Texto | — | L'entrée nommée à tester (ex. "jump") |

### Synchroniser cette instance

| Propriedade | Valor |
|----------|-------|
| **Nome** | `sync_instance` |
| **Ícone** | 🔗 |
| **Categoria** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `vars` | Texto | — | Noms de variables d'instance à répliquer aussi, séparés par des virgules (ex. "hp, couleur"); opcional |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (25)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Particles](Full-Action-Reference-Particles_pt) (8)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
