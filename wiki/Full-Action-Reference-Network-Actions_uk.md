# Réseau

*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*

> **Згенеровано автоматично** з реєстру дій IDE за допомогою `tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.

### Associer une touche réseau

| Властивість | Значення |
|----------|-------|
| **Назва** | `bind_network_input` |
| **Значок** | ⌨️ |
| **Категорія** | Réseau |

Associer une touche locale à une « entrée nommée » signalée à l'hôte. L'hôte teste ensuite avec « Si le joueur appuie ». Les flèches et Espace sont déjà associées ("left", "right", "up", "down", "space")

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `name` | Текст | — | Étiquette libre (ex. "jump", "tir") |
| `key` | Текст | — | Nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Властивість | Значення |
|----------|-------|
| **Назва** | `network_spawn` |
| **Значок** | ✨ |
| **Категорія** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `object` | Об'єкт | — | Type d'objet à créer |
| `x` | Текст | `0` |  |
| `y` | Текст | `0` |  |
| `owner` | Текст | `0` | Joueur qui pilote l'instance (0 = hôte). Souvent global.network_sender dans « Joueur connecté ».; необов'язково |
| `relative` | Так/Ні | Ні | Position relative à l'objet qui exécute l'action; необов'язково |

### Définir le propriétaire de l'instance

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_instance_owner` |
| **Значок** | 🎮 |
| **Категорія** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `player` | Текст | `0` | Numéro de joueur (0 = hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Définir une variable partagée

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_shared_var` |
| **Значок** | 📤 |
| **Категорія** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `name` | Текст | — | Identifiant simple (lettres, chiffres, _) -- pas d'espace ni d'opérateur |
| `value` | Текст | `0` | Nombre, texte ou booléen (les objets complexes sont refusés) |

### Démarrer la partie en réseau

| Властивість | Значення |
|----------|-------|
| **Назва** | `start_networked_game` |
| **Значок** | 🚦 |
| **Категорія** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Параметри:* немає

### Envoyer un message réseau

| Властивість | Значення |
|----------|-------|
| **Назва** | `send_network_message` |
| **Значок** | ✉️ |
| **Категорія** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `event` | Текст | — | Étiquette libre que le gestionnaire teste (ex. "buzz", "reponse") |
| `data` | Текст | — | Nombre, texte, booléen ou petite liste; необов'язково |
| `target` | Вибір | `all` | all = tout le monde ; host = l'hôte seulement; Варіанти: `all`, `host` |

### Héberger une partie

| Властивість | Значення |
|----------|-------|
| **Назва** | `host_game` |
| **Значок** | 🌐 |
| **Категорія** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `game_name` | Текст | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau, Phase 6); необов'язково |
| `max_players` | Число | `8` | Nombre maximal de joueurs, hôte compris (2 à 16); необов'язково |
| `port` | Число | `45782` | Port TCP -- doit être identique chez l'hôte et les clients; необов'язково |
| `player_name` | Текст | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); необов'язково |
| `show_lobby` | Так/Ні | Ні | Afficher un écran « En attente de joueurs… » avec bouton Démarrer avant de lancer la partie; необов'язково |

### Lire une variable partagée

| Властивість | Значення |
|----------|-------|
| **Назва** | `get_shared_var` |
| **Значок** | 📥 |
| **Категорія** | Réseau |

Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). Équivaut à lire global.<nom> directement

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `name` | Текст | — | Nom de la variable partagée à lire |
| `into` | Текст | — | Nom de la variable globale où écrire la valeur |

### Quitter la partie

| Властивість | Значення |
|----------|-------|
| **Назва** | `leave_game` |
| **Значок** | 🚪 |
| **Категорія** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Параметри:* немає

### Rejoindre une partie

| Властивість | Значення |
|----------|-------|
| **Назва** | `join_game` |
| **Значок** | 🔌 |
| **Категорія** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `host` | Текст | `127.0.0.1` | Adresse IP LAN de l'hôte ("auto" = écran de connexion intégré, Phase 6); необов'язково |
| `port` | Число | `45782` | Port TCP -- doit correspondre à celui de l'hôte; необов'язково |
| `player_name` | Текст | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); необов'язково |

### Régler la fréquence de synchro

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_sync_rate` |
| **Значок** | ⏱️ |
| **Категорія** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `hz` | Число | `20` | 10-30 convient sur un réseau local (défaut 20); необов'язково |
| `interp_ms` | Число | `100` | Retard d'affichage des fantômes, en millisecondes (défaut 100); необов'язково |

### Set Network Mode (v1)

| Властивість | Значення |
|----------|-------|
| **Назва** | `set_network_mode` |
| **Значок** | 🌐 |
| **Категорія** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `mode` | Вибір | `host` | Host = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Варіанти: `host`, `client` |
| `host` | Текст | `127.0.0.1` | Adresse IP LAN de l'hôte (mode Client uniquement); необов'язково |
| `port` | Число | `45782` | Port TCP -- doit être identique chez l'hôte et le client; необов'язково |

### Si je pilote cette instance

| Властивість | Значення |
|----------|-------|
| **Назва** | `is_instance_owner` |
| **Значок** | ❓ |
| **Категорія** | Réseau |

Condition : vraie si CETTE machine est le propriétaire de l'instance synchronisée. À placer avant un bloc pour ne faire tourner la logique de contrôle que chez le bon joueur

*Параметри:* немає

### Si le joueur appuie

| Властивість | Значення |
|----------|-------|
| **Назва** | `remote_input` |
| **Значок** | ❓ |
| **Категорія** | Réseau |

Condition (chez l'hôte) : vraie si le joueur indiqué maintient l'entrée nommée. Permet à l'hôte de réagir aux touches d'un client sans posséder son avatar

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `player` | Текст | `0` | Numéro de joueur (0 = hôte) |
| `name` | Текст | — | L'entrée nommée à tester (ex. "jump") |

### Synchroniser cette instance

| Властивість | Значення |
|----------|-------|
| **Назва** | `sync_instance` |
| **Значок** | 🔗 |
| **Категорія** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Параметр | Тип | За замовч. | Примітки |
|-----------|------|---------|-------|
| `vars` | Текст | — | Noms de variables d'instance à répliquer aussi, séparés par des virgules (ex. "hp, couleur"); необов'язково |

---

## Інші Категорії

- [Рух](Full-Action-Reference-Movement_uk) (20)
- [Екземпляр](Full-Action-Reference-Instance_uk) (12)
- [Рахунок](Full-Action-Reference-Score_uk) (11)
- [Кімната](Full-Action-Reference-Room_uk) (13)
- [Час](Full-Action-Reference-Timing_uk) (8)
- [Аудіо](Full-Action-Reference-Audio_uk) (6)
- [Гра](Full-Action-Reference-Game_uk) (25)
- [Керування](Full-Action-Reference-Control_uk) (19)
- [Сітка](Full-Action-Reference-Grid_uk) (4)
- [Вигляди](Full-Action-Reference-Views_uk) (2)
- [3D-вигляд](Full-Action-Reference-3D-View-Actions_uk) (16)
- [Particles](Full-Action-Reference-Particles_uk) (8)

[← Назад до Повного Довідника Дій](Full-Action-Reference_uk)
