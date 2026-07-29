# Préréglage Débutant

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Préréglage Intermédiaire](Intermediate-Preset_fr)*

Le préréglage **Débutant** est conçu pour les utilisateurs qui découvrent le développement de jeux. Il fournit un ensemble sélectionné d'événements et d'actions essentiels qui couvrent les bases de la création de jeux 2D simples sans submerger les débutants avec trop d'options.

## Aperçu

Le préréglage Débutant comprend :
- **4 Types d'Événements** - Pour réagir aux situations du jeu
- **17 Types d'Actions** - Pour contrôler le comportement du jeu
- **6 Catégories** - Événements, Mouvement, Score/Vies/Santé, Instance, Salle, Sortie

---

## Événements

Les événements sont des déclencheurs qui réagissent à des situations spécifiques dans votre jeu. Lorsqu'un événement se produit, les actions que vous avez définies pour cet événement s'exécutent.

### Événement Create

| Propriété | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_create` |
| **Catégorie** | Événements |
| **Description** | Se déclenche une fois lorsqu'une instance est créée pour la première fois |

**Quand il se déclenche :** Immédiatement lorsqu'une instance d'objet est placée dans une salle ou créée avec l'action « Créer une instance ».

**Utilisations courantes :**
- Initialiser des variables
- Définir la position de départ
- Définir la vitesse ou la direction initiale
- Réinitialiser le score au début du jeu

---

### Événement Step

| Propriété | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_step` |
| **Catégorie** | Événements |
| **Description** | Se déclenche à chaque image (généralement 60 fois par seconde) |

**Quand il se déclenche :** En continu, à chaque image du jeu.

**Utilisations courantes :**
- Mouvement continu
- Vérification des conditions
- Mise à jour de l'état du jeu
- Contrôle de l'animation

---

### Événement Touche Pressée

| Propriété | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_keyboard_press` |
| **Catégorie** | Événements |
| **Description** | Se déclenche une fois lorsqu'une touche spécifique est enfoncée |

**Quand il se déclenche :** Une fois au moment où une touche est pressée (pas pendant qu'elle est maintenue).

**Touches supportées :** Touches fléchées (haut, bas, gauche, droite), Espace, Entrée, lettres (A-Z), chiffres (0-9)

**Utilisations courantes :**
- Contrôles de mouvement du joueur
- Saut
- Tir
- Navigation dans les menus

---

### Événement Collision

| Propriété | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_collision` |
| **Catégorie** | Événements |
| **Description** | Se déclenche lorsque cette instance entre en collision avec un autre objet |

**Quand il se déclenche :** À chaque image où deux instances se chevauchent.

**Variable spéciale :** Dans un événement de collision, `other` fait référence à l'instance avec laquelle il y a collision.

**Utilisations courantes :**
- Collecter des objets (pièces, bonus)
- Subir des dégâts des ennemis
- Heurter des murs ou des obstacles
- Atteindre des objectifs ou des points de contrôle

---

## Actions

Les actions sont des commandes qui s'exécutent lorsqu'un événement est déclenché. Plusieurs actions peuvent être ajoutées à un seul événement et s'exécuteront dans l'ordre.

---

## Actions de Mouvement

### Définir la Vitesse Horizontale

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_hspeed` |
| **Nom du Bloc** | `move_set_hspeed` |
| **Catégorie** | Mouvement |
| **Icône** | ↔️ |

**Description :** Définit la vitesse de mouvement horizontal de l'instance.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Vitesse en pixels par image. Positif = droite, Négatif = gauche |

**Exemple :** Définissez `value` à `4` pour se déplacer vers la droite à 4 pixels par image, ou `-4` pour aller vers la gauche.

---

### Définir la Vitesse Verticale

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_vspeed` |
| **Nom du Bloc** | `move_set_vspeed` |
| **Catégorie** | Mouvement |
| **Icône** | ↕️ |

**Description :** Définit la vitesse de mouvement vertical de l'instance.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Vitesse en pixels par image. Positif = bas, Négatif = haut |

**Exemple :** Définissez `value` à `-4` pour monter à 4 pixels par image, ou `4` pour descendre.

---

### Arrêter le Mouvement

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `stop_movement` |
| **Nom du Bloc** | `move_stop` |
| **Catégorie** | Mouvement |
| **Icône** | 🛑 |

**Description :** Arrête tout mouvement en mettant la vitesse horizontale et verticale à zéro.

**Paramètres :** Aucun

**Utilisations courantes :**
- Arrêter le joueur lorsqu'il heurte un mur
- Arrêter les ennemis lorsqu'ils atteignent une destination
- Mettre le mouvement en pause temporairement

---

### Sauter à une Position

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `jump_to_position` |
| **Nom du Bloc** | `move_jump_to` |
| **Catégorie** | Mouvement |
| **Icône** | 📍 |

**Description :** Déplace instantanément l'instance à une position spécifique (pas de mouvement fluide).

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `x` | Nombre | Coordonnée X cible |
| `y` | Nombre | Coordonnée Y cible |

**Exemple :** Sauter à la position (100, 200) pour téléporter le joueur à cet emplacement.

---

## Actions d'Instance

### Détruire une Instance

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `destroy_instance` |
| **Nom du Bloc** | `instance_destroy` |
| **Catégorie** | Instance |
| **Icône** | 💥 |

**Description :** Supprime une instance du jeu.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `target` | Choix | `self` = détruire cette instance, `other` = détruire l'instance en collision |

**Utilisations courantes :**
- Supprimer les pièces collectées (`target: other` dans l'événement de collision)
- Détruire les balles lorsqu'elles touchent quelque chose
- Supprimer les ennemis lorsqu'ils sont vaincus

---

### Créer une Instance

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `create_instance` |
| **Nom du Bloc** | `instance_create` |
| **Catégorie** | Instance |
| **Icône** | ✨ |

**Description :** Crée une nouvelle instance d'un objet à une position spécifiée.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `object` | Objet | Le type d'objet à créer |
| `x` | Nombre | Coordonnée X pour la nouvelle instance |
| `y` | Nombre | Coordonnée Y pour la nouvelle instance |

**Exemple :** Créer une balle à la position du joueur lorsque Espace est pressé.

---

## Actions de Score

### Définir le Score

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_score` |
| **Nom du Bloc** | `score_set` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | 🏆 |

**Description :** Définit le score à une valeur spécifique, ou ajoute/soustrait au score actuel.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | La valeur du score |
| `relative` | Booléen | Si vrai, ajoute la valeur au score actuel. Si faux, définit le score à la valeur |

**Exemples :**
- Réinitialiser le score : `value: 0`, `relative: false`
- Ajouter 10 points : `value: 10`, `relative: true`
- Soustraire 5 points : `value: -5`, `relative: true`

---

### Ajouter au Score

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `add_score` |
| **Nom du Bloc** | `score_add` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | ➕🏆 |

**Description :** Ajoute une valeur au score actuel (raccourci pour set_score avec relative=true).

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Points à ajouter (peut être négatif pour soustraire) |

---

### Afficher le Score

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `draw_score` |
| **Nom du Bloc** | `draw_score` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | 🖼️🏆 |

**Description :** Affiche le score actuel à l'écran.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `x` | Nombre | Position X pour afficher le score |
| `y` | Nombre | Position Y pour afficher le score |
| `caption` | Chaîne | Texte à afficher avant le score (ex : « Score : ») |

**Note :** Ceci devrait être utilisé dans un événement Draw (disponible dans le préréglage Intermédiaire).

---

## Actions de Salle

### Aller à la Salle Suivante

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `next_room` |
| **Nom du Bloc** | `room_goto_next` |
| **Catégorie** | Salle |
| **Icône** | ➡️ |

**Description :** Passe à la salle suivante dans l'ordre des salles.

**Paramètres :** Aucun

**Note :** Si vous êtes déjà dans la dernière salle, cette action n'a aucun effet (utilisez « Si la Salle Suivante Existe » pour vérifier d'abord).

---

### Aller à la Salle Précédente

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `previous_room` |
| **Nom du Bloc** | `room_goto_previous` |
| **Catégorie** | Salle |
| **Icône** | ⬅️ |

**Description :** Passe à la salle précédente dans l'ordre des salles.

**Paramètres :** Aucun

**Note :** Si vous êtes déjà dans la première salle, cette action n'a aucun effet.

---

### Redémarrer la Salle

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `restart_room` |
| **Nom du Bloc** | `room_restart` |
| **Catégorie** | Salle |
| **Icône** | 🔄 |

**Description :** Redémarre la salle actuelle, réinitialisant toutes les instances à leur état initial.

**Paramètres :** Aucun

**Utilisations courantes :**
- Redémarrer le niveau après la mort du joueur
- Réinitialiser le puzzle après un échec
- Rejouer un mini-jeu

---

### Aller à une Salle

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `goto_room` |
| **Nom du Bloc** | `room_goto` |
| **Catégorie** | Salle |
| **Icône** | 🚪 |

**Description :** Passe à une salle spécifique par son nom.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `room` | Salle | La salle où aller |

---

### Si la Salle Suivante Existe

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `if_next_room_exists` |
| **Nom du Bloc** | `room_if_next_exists` |
| **Catégorie** | Salle |
| **Icône** | ❓➡️ |

**Description :** Bloc conditionnel qui n'exécute les actions contenues que s'il existe une salle suivante.

**Paramètres :** Aucun (les actions sont placées à l'intérieur du bloc)

**Utilisations courantes :**
- Vérifier avant d'aller à la salle suivante
- Afficher un message « Vous avez gagné ! » s'il n'y a plus de salles

---

### Si la Salle Précédente Existe

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `if_previous_room_exists` |
| **Nom du Bloc** | `room_if_previous_exists` |
| **Catégorie** | Salle |
| **Icône** | ❓⬅️ |

**Description :** Bloc conditionnel qui n'exécute les actions contenues que s'il existe une salle précédente.

**Paramètres :** Aucun (les actions sont placées à l'intérieur du bloc)

---

## Actions de Sortie

### Afficher un Message

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `show_message` |
| **Nom du Bloc** | `output_message` |
| **Catégorie** | Sortie |
| **Icône** | 💬 |

**Description :** Affiche une boîte de dialogue popup au joueur.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `message` | Chaîne | Le texte à afficher |

**Note :** Le jeu se met en pause pendant que le message est affiché. Le joueur doit cliquer sur OK pour continuer.

**Utilisations courantes :**
- Instructions du jeu
- Dialogues de l'histoire
- Messages de victoire/défaite
- Informations de débogage

---

### Exécuter du Code

| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `execute_code` |
| **Nom du Bloc** | `execute_code` |
| **Catégorie** | Sortie |
| **Icône** | 💻 |

**Description :** Exécute du code Python personnalisé.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `code` | Chaîne | Code Python à exécuter |

**Note :** Ceci est une fonctionnalité avancée. Utilisez-la avec précaution car un code incorrect peut causer des erreurs.

---

## Résumé des Catégories

| Catégorie | Événements | Actions |
|-----------|------------|---------|
| **Événements** | Create, Step, Touche Pressée, Collision | - |
| **Mouvement** | - | Définir la Vitesse Horizontale, Définir la Vitesse Verticale, Arrêter le Mouvement, Sauter à une Position |
| **Instance** | - | Détruire une Instance, Créer une Instance |
| **Score/Vies/Santé** | - | Définir le Score, Ajouter au Score, Afficher le Score |
| **Salle** | - | Salle Suivante, Salle Précédente, Redémarrer la Salle, Aller à une Salle, Si la Salle Suivante Existe, Si la Salle Précédente Existe |
| **Sortie** | - | Afficher un Message, Exécuter du Code |

---

## Exemple : Jeu Simple de Collecte de Pièces

Voici comment configurer un jeu basique de collecte de pièces en utilisant uniquement les fonctionnalités du préréglage Débutant :

### Objet Joueur (obj_player)

**Touche Pressée (Flèche Gauche) :**
- Définir la Vitesse Horizontale : -4

**Touche Pressée (Flèche Droite) :**
- Définir la Vitesse Horizontale : 4

**Touche Pressée (Flèche Haut) :**
- Définir la Vitesse Verticale : -4

**Touche Pressée (Flèche Bas) :**
- Définir la Vitesse Verticale : 4

**Collision avec obj_coin :**
- Définir le Score : 10 (relative: true)
- Détruire une Instance : other

**Collision avec obj_wall :**
- Arrêter le Mouvement

**Collision avec obj_goal :**
- Définir le Score : 100 (relative: true)
- Salle Suivante

### Objet Pièce (obj_coin)
Aucun événement nécessaire - juste un objet à collecter.

### Objet Mur (obj_wall)
Aucun événement nécessaire - juste un obstacle solide.

### Objet Objectif (obj_goal)
Aucun événement nécessaire - déclenche la fin du niveau lorsque le joueur entre en collision.

---

## Passer au Niveau Intermédiaire

Lorsque vous êtes à l'aise avec le préréglage Débutant, envisagez de passer à l'**Intermédiaire** pour accéder à :
- Événement Draw (pour le rendu personnalisé)
- Événement Destroy (nettoyage lorsqu'une instance est détruite)
- Événements Souris (détection des clics)
- Événements Alarme (actions minutées)
- Systèmes de Vies et de Santé
- Actions de Son et de Musique
- Plus d'options de mouvement (direction, se déplacer vers)

---

## Voir Aussi

- [Tutoriels](Tutorials_fr) - Tous les tutoriels en un seul endroit
- [Préréglage Intermédiaire](Intermediate-Preset_fr) - Fonctionnalités du niveau suivant
- [Référence Complète des Actions](Full-Action-Reference_fr) - Liste complète des actions
- [Référence des Événements](Event-Reference_fr) - Liste complète des événements
- [Événements et Actions](Evenements_Actions_fr) - Concepts fondamentaux
- [Créer Votre Premier Jeu](Premier_Jeu_fr) - Tutoriel étape par étape
- [Tutoriel Pong](Tutorial-Pong_fr) - Créez un jeu Pong classique pour deux joueurs
- [Tutoriel Casse-Briques](Tutorial-Breakout_fr) - Créez un jeu de casse-briques classique
- [Initiation à la Création de Jeux](Getting-Started-Breakout_fr) - Tutoriel complet pour débutants
