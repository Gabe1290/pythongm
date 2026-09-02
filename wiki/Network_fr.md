# Réseau (multijoueur en LAN)

*[Accueil](Home_fr) | [Référence Complète des Actions](Full-Action-Reference-Network-Actions_fr) | [Extensions](Extensions_fr)*

---

PyGameMaker peut transformer un projet en **jeu multijoueur en réseau local
(LAN)** : une machine héberge, les autres rejoignent sur le réseau local, et
les joueurs partagent un état — un tableau de scores, des messages
personnalisés, et même les avatars affichés à l'écran des uns et des autres
— sans serveur, sans compte, et sans internet. Cette fonctionnalité est
fournie par l'**extension Réseau (multijoueur LAN)** intégrée, activée par
défaut (voir [Extensions](Extensions_fr)).

Les exemples fournis **`reseau_1` à `reseau_3`** sont des jeux complets et
jouables : une salle partagée où deux joueurs se déplacent ensemble, un quiz
de classe avec un tableau des scores en direct, et une chasse au trésor
coopérative à deux joueurs.

Pris en charge aujourd'hui : l'export **ordinateur** (pygame), en hôte comme
en client, et l'export **HTML5** en client (une page de navigateur rejoint
un hôte ordinateur ; elle ne peut pas héberger elle-même). Un export
**Kivy/Android** fait tourner le jeu en solo — les actions réseau n'y font
tout simplement rien.

---

## Deux niveaux

**Niveau A — tableau partagé.** Pas d'avatars, juste un état partagé : des
variables que chaque joueur peut lire et écrire, des messages personnalisés,
et qui est connecté. C'est la façon la plus simple d'ajouter du multijoueur
à un projet — un quiz, un tableau des scores partagé, un jeu de buzzer « le
premier qui répond ».

**Niveau B — instances mises en réseau.** Des instances créées par l'hôte
(joueurs, ennemis, objets à ramasser) qui apparaissent et se déplacent
automatiquement sur toutes les machines, plus des avatars possédés par un
joueur, que chacun contrôle localement pendant que tous les autres en voient
une copie interpolée en douceur.

---

## Comment ça fonctionne

- Un joueur exécute **Héberger une partie**, généralement depuis
  l'événement Création d'un objet contrôleur de la salle. Cette machine
  devient l'**hôte** — toutes les autres machines s'y connectent.
  `global.player_id` devient `0`.
- Les autres joueurs exécutent **Rejoindre une partie** avec l'adresse IP
  LAN de l'hôte (ou `"auto"` pour afficher un écran de connexion intégré
  qui trouve automatiquement les hôtes sur le réseau). `global.player_id`
  est assigné par l'hôte (`1`, `2`, ...).
- Si l'hôte est injoignable, **la partie continue en solo** — rejoindre ne
  bloque ni ne fait jamais planter un jeu.
- L'identité du joueur et l'état de connexion sont toujours lisibles via des
  variables globales : `global.is_host`, `global.player_id`,
  `global.player_count`, `global.network_role`, `global.network_connected`.
- **Écrivez votre logique de jeu avec une action « Si » ordinaire**, par
  exemple `global.is_host == 1`, pour ne réserver certaines initialisations
  qu'à l'hôte (comme créer les ennemis) — aucune action « condition réseau »
  spéciale n'est nécessaire.
- Une variable partagée définie avec **Définir une variable partagée** est
  lisible *partout* via `global.<nom>` — y compris sur la machine qui l'a
  écrite.
- Les **messages personnalisés** (**Envoyer un message réseau**) permettent
  de signaler un événement par son nom, avec une petite donnée attachée —
  un buzzer pressé, une réponse choisie, un signal « prêt ».

---

## Les actions (catégorie **Réseau**)

| Action | Ce qu'elle fait |
|--------|-----------------|
| **Héberger une partie** | Devenir l'hôte. Peut afficher un salon d'attente avec un bouton Démarrer. |
| **Rejoindre une partie** | Se connecter à un hôte par adresse (ou `"auto"` pour l'écran de connexion intégré). |
| **Quitter la partie** | Se déconnecter (ou arrêter d'héberger) et effacer les variables réseau globales. |
| **Démarrer la partie en réseau** | Hôte uniquement : terminer le salon d'attente et signaler à tout le monde de commencer. |
| **Définir une variable partagée** | Écrire une variable que toutes les machines peuvent lire via `global.<nom>`. |
| **Lire une variable partagée** | Copier une variable partagée dans une variable globale (pour l'utiliser dans un calcul). |
| **Envoyer un message réseau** | Diffuser un message personnalisé nommé, avec une donnée. |
| **Créer un objet réseau** | Hôte uniquement : créer une instance qui apparaît chez tous les clients. |
| **Synchroniser cette instance** | Marquer l'instance courante comme répliquée sur toutes les machines. |
| **Définir le propriétaire de l'instance** | Donner à un joueur précis le contrôle local d'une instance synchronisée. |
| **Si je pilote cette instance** | Condition : réserve la logique de contrôle à la machine propriétaire. |
| **Associer une touche réseau** | Associer une touche locale à une entrée nommée que l'hôte peut lire. |
| **Si le joueur appuie** | Condition (hôte) : le joueur indiqué maintient-il une entrée nommée ? |
| **Régler la fréquence de synchro** | Ajuster la cadence des instantanés de l'hôte et le délai d'interpolation des clients. |

Voir la [Référence Complète des Actions](Full-Action-Reference-Network-Actions_fr) pour
tous les paramètres.

---

## Les événements (catégorie **Réseau**)

Déclenchés sur chaque instance dont l'objet les gère, sur chaque machine
concernée :

| Événement | Se déclenche quand |
|-----------|---------------------|
| **Réseau prêt** *(Network Ready)* | Un client termine sa connexion à l'hôte (l'hôte ne le déclenche pas pour lui-même). |
| **Joueur connecté** *(Player Joined)* | Un nouveau joueur se connecte. `global.network_sender` / `global.network_player_name` l'identifient. |
| **Joueur déconnecté** *(Player Left)* | Un joueur se déconnecte. |
| **Message réseau** *(Network Message)* | Un **Envoyer un message réseau** arrive — `global.network_event` / `global.network_data` / `global.network_sender`. |
| **Partie réseau démarrée** *(Network Game Started)* | L'hôte exécute **Démarrer la partie en réseau**. |
| **Connexion perdue** *(Connection Lost)* | La connexion d'un client à l'hôte est coupée. La partie continue — seuls les fantômes de ce joueur disparaissent. |

---

## Un exemple minimal de salle partagée (Niveau A)

Dans un objet contrôleur de salle invisible :

- **Création :** `Héberger une partie` si c'est la machine de l'enseignant,
  sinon `Rejoindre une partie` avec son IP (ou `"auto"`).
- **Création :** `Définir une variable partagée` `round = 1` (hôte
  uniquement, gardé par `global.is_host == 1`).
- N'importe où : `draw_text` affichant `global.round` — tous les joueurs
  voient la même valeur.

## Un exemple minimal d'avatars partagés (Niveau B)

Dans l'événement Création de l'objet joueur :

- `Synchroniser cette instance` — cette instance est maintenant répliquée.
- Chez l'**hôte** : `Créer un objet réseau` une instance de joueur par
  joueur qui se connecte (dans un gestionnaire **Joueur connecté**), puis
  `Définir le propriétaire de l'instance` avec le numéro de ce joueur.
- Le code de déplacement gardé par `Si je pilote cette instance` ne
  s'exécute que sur la machine du joueur propriétaire ; ailleurs, l'instance
  est un fantôme interpolé en douceur.

---

## Remarques et limites

- **TCP, réseau local uniquement.** Pas de traversée NAT, pas de jeu par
  internet — les deux machines doivent être joignables sur le même réseau
  local (un Wi-Fi de classe ou un labo câblé). Un Wi-Fi avec isolation
  client (fréquent sur les réseaux scolaires gérés) bloque autant la
  découverte que la connexion directe ; un labo câblé est la configuration
  la plus fiable.
- **Ports 45782 (TCP)** et **45783 (UDP, découverte)** — demandez à votre
  service informatique avant d'utiliser cette fonctionnalité sur un réseau
  géré, et attendez-vous à une invite de pare-feu la première fois que vous
  hébergez.
- Un client navigateur (export HTML5) se connecte sur le port juste
  au-dessus de celui de l'hôte, par exemple `45783` si l'hôte utilise le
  port par défaut — cela se fait automatiquement.
- La perte de l'hôte est gérée en douceur : la partie du client continue ;
  seuls les fantômes des autres joueurs disparaissent, et `Connexion
  perdue` se déclenche pour que vous puissiez afficher un message.
- Si l'extension Réseau (multijoueur LAN) est **désactivée**, ces actions
  et événements ne font simplement rien — voir [Extensions](Extensions_fr).

---

## Voir aussi

- [Extensions](Extensions_fr) — comment le Réseau est fourni et comment le désactiver
- [Référence Complète des Actions](Full-Action-Reference-Network-Actions_fr) — chaque action et paramètre
- [Référence des Événements](Event-Reference_fr) — les six événements réseau en contexte
