# Réseau

*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*

> **Сгенерировано автоматически** из реестра действий IDE с помощью `tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.

### Associer une touche réseau

| Свойство | Значение |
|----------|-------|
| **Имя** | `bind_network_input` |
| **Значок** | ⌨️ |
| **Категория** | Réseau |

Associer une touche locale à une « entrée nommée » signalée à l'hôte. L'hôte teste ensuite avec « Si le joueur appuie ». Les flèches et Espace sont déjà associées ("left", "right", "up", "down", "space")

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `name` | Текст | — | Étiquette libre (ex. "jump", "tir") |
| `key` | Текст | — | Nom de touche : "space", "left", "a", "5", "lshift"... |

### Créer un objet réseau

| Свойство | Значение |
|----------|-------|
| **Имя** | `network_spawn` |
| **Значок** | ✨ |
| **Категория** | Réseau |

Hôte uniquement : créer une instance qui apparaît automatiquement chez tous les clients (comme des « fantômes » interpolés). Sans effet chez un client. L'instance créée est pilotée par l'hôte -- guardez sa logique de jeu par global.is_host == 1

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `object` | Объект | — | Type d'objet à créer |
| `x` | Текст | `0` |  |
| `y` | Текст | `0` |  |
| `owner` | Текст | `0` | Joueur qui pilote l'instance (0 = hôte). Souvent global.network_sender dans « Joueur connecté ».; необязательно |
| `relative` | Да/Нет | Нет | Position relative à l'objet qui exécute l'action; необязательно |

### Définir le propriétaire de l'instance

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_instance_owner` |
| **Значок** | 🎮 |
| **Категория** | Réseau |

Assigner quel joueur pilote cette instance synchronisée (0 = hôte, 1, 2, ... = clients). Sur la machine de ce joueur, l'instance tourne localement (réactive) et son état est renvoyé à l'hôte ; ailleurs c'est un fantôme interpolé. À appeler chez l'hôte (guardé par global.is_host == 1)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `player` | Текст | `0` | Numéro de joueur (0 = hôte). Souvent global.network_sender dans « Joueur connecté ». |

### Définir une variable partagée

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_shared_var` |
| **Значок** | 📤 |
| **Категория** | Réseau |

Écrire une variable partagée par toutes les machines. Chez l'hôte : appliquée immédiatement. Chez un client : une demande envoyée à l'hôte. Lisible partout via global.<nom>

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `name` | Текст | — | Identifiant simple (lettres, chiffres, _) -- pas d'espace ni d'opérateur |
| `value` | Текст | `0` | Nombre, texte ou booléen (les objets complexes sont refusés) |

### Démarrer la partie en réseau

| Свойство | Значение |
|----------|-------|
| **Имя** | `start_networked_game` |
| **Значок** | 🚦 |
| **Категория** | Réseau |

Hôte uniquement : faire sortir tout le monde du salon d'attente et lancer la partie. Déclenche l'événement « Partie réseau démarrée » sur toutes les machines

*Параметры:* нет

### Envoyer un message réseau

| Свойство | Значение |
|----------|-------|
| **Имя** | `send_network_message` |
| **Значок** | ✉️ |
| **Категория** | Réseau |

Diffuser un message personnalisé. Déclenche l'événement « Message réseau » sur les machines concernées, avec global.network_event / global.network_data / global.network_sender

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `event` | Текст | — | Étiquette libre que le gestionnaire teste (ex. "buzz", "reponse") |
| `data` | Текст | — | Nombre, texte, booléen ou petite liste; необязательно |
| `target` | Выбор | `all` | all = tout le monde ; host = l'hôte seulement; Варианты: `all`, `host` |

### Héberger une partie

| Свойство | Значение |
|----------|-------|
| **Имя** | `host_game` |
| **Значок** | 🌐 |
| **Категория** | Réseau |

Devenir l'hôte d'une partie multijoueur LAN : les autres joueurs se connectent à cette machine. À appeler une seule fois (par ex. dans l'événement Création du contrôleur de la salle). Définit global.player_id = 0 et global.network_role = "host"

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `game_name` | Текст | `PyGameMaker` | Nom affiché dans la liste des serveurs (découverte réseau, Phase 6); необязательно |
| `max_players` | Число | `8` | Nombre maximal de joueurs, hôte compris (2 à 16); необязательно |
| `port` | Число | `45782` | Port TCP -- doit être identique chez l'hôte et les clients; необязательно |
| `player_name` | Текст | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); необязательно |
| `show_lobby` | Да/Нет | Нет | Afficher un écran « En attente de joueurs… » avec bouton Démarrer avant de lancer la partie; необязательно |

### Lire une variable partagée

| Свойство | Значение |
|----------|-------|
| **Имя** | `get_shared_var` |
| **Значок** | 📥 |
| **Категория** | Réseau |

Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). Équivaut à lire global.<nom> directement

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `name` | Текст | — | Nom de la variable partagée à lire |
| `into` | Текст | — | Nom de la variable globale où écrire la valeur |

### Quitter la partie

| Свойство | Значение |
|----------|-------|
| **Имя** | `leave_game` |
| **Значок** | 🚪 |
| **Категория** | Réseau |

Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales

*Параметры:* нет

### Rejoindre une partie

| Свойство | Значение |
|----------|-------|
| **Имя** | `join_game` |
| **Значок** | 🔌 |
| **Категория** | Réseau |

Se connecter à une partie multijoueur LAN hébergée par une autre machine. global.player_id sera défini par l'hôte (1, 2, ...). Si l'hôte est injoignable, la partie continue en solo

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `host` | Текст | `127.0.0.1` | Adresse IP LAN de l'hôte ("auto" = écran de connexion intégré, Phase 6); необязательно |
| `port` | Число | `45782` | Port TCP -- doit correspondre à celui de l'hôte; необязательно |
| `player_name` | Текст | — | Nom de ce joueur (vide = global.player_name, ou « Joueur »); необязательно |

### Régler la fréquence de synchro

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_sync_rate` |
| **Значок** | ⏱️ |
| **Категория** | Réseau |

Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. À appeler une fois chez l'hôte (et chez les clients pour le délai)

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `hz` | Число | `20` | 10-30 convient sur un réseau local (défaut 20); необязательно |
| `interp_ms` | Число | `100` | Retard d'affichage des fantômes, en millisecondes (défaut 100); необязательно |

### Set Network Mode (v1)

| Свойство | Значение |
|----------|-------|
| **Имя** | `set_network_mode` |
| **Значок** | 🌐 |
| **Категория** | Réseau |

Ancienne action bas niveau : démarre la salle en mode hôte ou client (spectateur seulement -- l'entrée du client n'a aucun effet). Préférez « Héberger une partie » / « Rejoindre une partie ». Conservée pour les projets existants et les drapeaux --net-host / --net-client

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `mode` | Выбор | `host` | Host = les autres se connectent à vous ; Client = vous vous connectez à un hôte; Варианты: `host`, `client` |
| `host` | Текст | `127.0.0.1` | Adresse IP LAN de l'hôte (mode Client uniquement); необязательно |
| `port` | Число | `45782` | Port TCP -- doit être identique chez l'hôte et le client; необязательно |

### Si je pilote cette instance

| Свойство | Значение |
|----------|-------|
| **Имя** | `is_instance_owner` |
| **Значок** | ❓ |
| **Категория** | Réseau |

Condition : vraie si CETTE machine est le propriétaire de l'instance synchronisée. À placer avant un bloc pour ne faire tourner la logique de contrôle que chez le bon joueur

*Параметры:* нет

### Si le joueur appuie

| Свойство | Значение |
|----------|-------|
| **Имя** | `remote_input` |
| **Значок** | ❓ |
| **Категория** | Réseau |

Condition (chez l'hôte) : vraie si le joueur indiqué maintient l'entrée nommée. Permet à l'hôte de réagir aux touches d'un client sans posséder son avatar

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `player` | Текст | `0` | Numéro de joueur (0 = hôte) |
| `name` | Текст | — | L'entrée nommée à tester (ex. "jump") |

### Synchroniser cette instance

| Свойство | Значение |
|----------|-------|
| **Имя** | `sync_instance` |
| **Значок** | 🔗 |
| **Категория** | Réseau |

Marquer l'instance qui exécute l'action comme « synchronisée » : sa position, sa rotation, son image et sa visibilité sont répliquées sur toutes les machines. À appeler dans l'événement Création. Par défaut l'hôte en est le propriétaire ; utilisez « Définir le propriétaire » pour qu'un client la pilote

| Параметр | Тип | По умолч. | Примечания |
|-----------|------|---------|-------|
| `vars` | Текст | — | Noms de variables d'instance à répliquer aussi, séparés par des virgules (ex. "hp, couleur"); необязательно |

---

## Другие Категории

- [Движение](Full-Action-Reference-Movement_ru) (20)
- [Экземпляр](Full-Action-Reference-Instance_ru) (12)
- [Счёт](Full-Action-Reference-Score_ru) (11)
- [Комната](Full-Action-Reference-Room_ru) (13)
- [Время](Full-Action-Reference-Timing_ru) (8)
- [Аудио](Full-Action-Reference-Audio_ru) (6)
- [Игра](Full-Action-Reference-Game_ru) (25)
- [Управление](Full-Action-Reference-Control_ru) (19)
- [Сетка](Full-Action-Reference-Grid_ru) (4)
- [Виды](Full-Action-Reference-Views_ru) (2)
- [3D-вид](Full-Action-Reference-3D-View-Actions_ru) (16)
- [Particles](Full-Action-Reference-Particles_ru) (8)

[← Назад к Полному Справочнику Действий](Full-Action-Reference_ru)
