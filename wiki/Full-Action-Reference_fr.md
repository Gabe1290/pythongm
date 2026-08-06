# Référence Complète des Actions

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

Cette page liste l'ensemble des **109** actions disponibles dans PyGameMaker, exactement telles qu'elles apparaissent dans le sélecteur d'actions de l'IDE (y compris le plugin Audio et l'extension Vue 3D). Les actions sont des commandes qui s'exécutent lorsqu'un événement se déclenche.

## Catégories

- [Mouvement](#movement) (20)
- [Instance](#instance) (12)
- [Score](#score) (11)
- [Salle](#room) (9)
- [Minuterie](#timing) (2)
- [Audio](#audio) (6)
- [Jeu](#game) (20)
- [Contrôle](#control) (19)
- [Grille](#grid) (4)
- [Vues](#views) (2)
- [Vue 3D](#3d-view) (4)

---

<a id="movement"></a>
## Mouvement

### Rebondir

| Propriété | Valeur |
|----------|-------|
| **Nom** | `bounce` |
| **Catégorie** | Mouvement |

Rebondir sur les objets solides

*Paramètres:* aucun

### Sauter à une position

| Propriété | Valeur |
|----------|-------|
| **Nom** | `jump_to_position` |
| **Icône** | 📍 |
| **Catégorie** | Mouvement |

Se déplacer instantanément à une position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `relative` | Oui/Non | Non | Ajouter à la position actuelle au lieu de définir une position absolue |

### Sauter à une position aléatoire

| Propriété | Valeur |
|----------|-------|
| **Nom** | `jump_to_random` |
| **Icône** | 🎲↪️ |
| **Catégorie** | Mouvement |

Se téléporter à une position aléatoire (éventuellement alignée sur la grille)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `snap_h` | Nombre | `1` | Alignement horizontal sur la grille (1 = aucun) |
| `snap_v` | Nombre | `1` | Alignement vertical sur la grille (1 = aucun) |

### Sauter à la position de départ

| Propriété | Valeur |
|----------|-------|
| **Nom** | `jump_to_start` |
| **Icône** | ↩️ |
| **Catégorie** | Mouvement |

Ramener l'instance à sa position de création

*Paramètres:* aucun

### Déplacement libre

| Propriété | Valeur |
|----------|-------|
| **Nom** | `move_free` |
| **Icône** | 🧭 |
| **Catégorie** | Mouvement |

Se déplacer dans une direction précise (0-360 degrés)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `direction` | Nombre | `0` | Direction en degrés (0=droite, 90=haut, sens antihoraire) |
| `speed` | Nombre | `4.0` | Vitesse de déplacement |

### Déplacer sur la grille

| Propriété | Valeur |
|----------|-------|
| **Nom** | `move_grid` |
| **Icône** | ▦ |
| **Catégorie** | Mouvement |

Se déplacer d'une case de grille dans la direction indiquée

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `direction` | Choix | `right` | Direction du déplacement; Choix: `left`, `right`, `up`, `down` |
| `grid_size` | Nombre | `32` | Taille de la case de grille en pixels |

### Se déplacer vers un point

| Propriété | Valeur |
|----------|-------|
| **Nom** | `move_towards_point` |
| **Icône** | 🎯 |
| **Catégorie** | Mouvement |

Se déplacer vers un point à une vitesse donnée

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | X cible |
| `y` | Nombre | `0` | Y cible |
| `speed` | Nombre | `4.0` | Vitesse de déplacement |

### Déplacer jusqu'au contact

| Propriété | Valeur |
|----------|-------|
| **Nom** | `move_to_contact` |
| **Icône** | 🎯 |
| **Catégorie** | Mouvement |

Se déplacer dans une direction jusqu'à toucher un objet (ou une distance maximale)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `direction` | Texte | `direction` | Direction en degrés (0=droite, 90=haut, 180=gauche, 270=bas), ou une expression. Par défaut « direction » = le cap actuel de l'instance (alignement sur collision). |
| `max_distance` | Nombre | `1000` | Distance maximale de déplacement, en pixels |
| `object` | Objet | `all` | S'arrêter au contact de : « all » toutes les instances, « solid » uniquement les objets solides, ou un nom d'objet spécifique.; Choix: `all`, `solid`; optionnel |

### Inverser horizontalement

| Propriété | Valeur |
|----------|-------|
| **Nom** | `reverse_horizontal` |
| **Icône** | ↔️ |
| **Catégorie** | Mouvement |

Inverser la direction du mouvement horizontal

*Paramètres:* aucun

### Inverser verticalement

| Propriété | Valeur |
|----------|-------|
| **Nom** | `reverse_vertical` |
| **Icône** | ↕️ |
| **Catégorie** | Mouvement |

Inverser la direction du mouvement vertical

*Paramètres:* aucun

### Définir la direction

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_direction` |
| **Icône** | 🧭 |
| **Catégorie** | Mouvement |

Définir la direction du mouvement

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `direction` | Nombre | `0` | Direction en degrés (0=droite, 90=haut) |

### Définir direction et vitesse

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_direction_speed` |
| **Icône** | 🧭 |
| **Catégorie** | Mouvement |

Définir la direction (en degrés) et la magnitude de vitesse de l'instance

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `direction` | Nombre | `0` | Direction en degrés (0=droite, 90=haut) |
| `speed` | Nombre | `4.0` | Vitesse en pixels par image |

### Définir le frottement

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_friction` |
| **Icône** | 🛑 |
| **Catégorie** | Mouvement |

Définir le frottement (décélération)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `friction` | Nombre | `0.1` | Quantité de frottement (soustraite de la vitesse à chaque étape) |

### Définir la gravité

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_gravity` |
| **Icône** | ⬇️ |
| **Catégorie** | Mouvement |

Définir la direction et l'intensité de la gravité

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `direction` | Nombre | `270` | Direction de la gravité en degrés (270=bas) |
| `gravity` | Nombre | `0.5` | Intensité de la gravité (ajoutée à chaque étape) |

### Définir la vitesse horizontale

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_hspeed` |
| **Icône** | ↔️ |
| **Catégorie** | Mouvement |

Définir la vitesse de déplacement horizontale

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `speed` | Nombre | `0` | Vitesse en pixels par image |

### Définir la vitesse

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_speed` |
| **Icône** | ⚡ |
| **Catégorie** | Mouvement |

Définir la vitesse de déplacement (magnitude)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `speed` | Nombre | `0` | Vitesse de déplacement |

### Définir la vitesse verticale

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_vspeed` |
| **Icône** | ↕️ |
| **Catégorie** | Mouvement |

Définir la vitesse de déplacement verticale

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `speed` | Nombre | `0` | Vitesse en pixels par image |

### Commencer à bouger (direction)

| Propriété | Valeur |
|----------|-------|
| **Nom** | `start_moving_direction` |
| **Icône** | ➡️ |
| **Catégorie** | Mouvement |

Commencer à se déplacer dans une direction à une vitesse donnée

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `directions` | Choix multiple | right | Direction(s) de déplacement — en cocher une, ou plusieurs pour en choisir une au hasard à chaque étape. La case centrale est l'arrêt.; Choix: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Texte | — | Alternative : expression libre évaluée en degrés; optionnel |
| `speed` | Nombre | `4.0` | Vitesse en pixels par image |

### Arrêter le mouvement

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_movement` |
| **Icône** | 🛑 |
| **Catégorie** | Mouvement |

Mettre les deux vitesses à zéro

*Paramètres:* aucun

### Boucler autour de la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `wrap_around_room` |
| **Icône** | 🔄 |
| **Catégorie** | Mouvement |

Réapparaître du côté opposé de la salle

*Paramètres:* aucun

---

<a id="instance"></a>
## Instance

### Changer d'instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `change_instance` |
| **Icône** | 🔄 |
| **Catégorie** | Instance |
| **S'applique à** | self / other / object |

Se transformer en un autre type d'objet

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | Nouveau type d'objet |
| `perform_events` | Oui/Non | Oui | Exécuter les événements destruction/création |

### Créer une instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_instance` |
| **Icône** | ✨ |
| **Catégorie** | Instance |

Créer une nouvelle instance

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | Objet à créer |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `relative` | Oui/Non | Non | Position relative à l'instance actuelle |

### Créer une instance en mouvement

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_moving_instance` |
| **Icône** | ✨➡️ |
| **Catégorie** | Instance |

Créer une instance et la faire se déplacer dans une direction

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | Objet à créer |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `speed` | Nombre | `0` | Magnitude de vitesse initiale |
| `direction` | Nombre | `0` | Direction initiale en degrés |

### Créer une instance aléatoire

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_random_instance` |
| **Icône** | 🎲 |
| **Catégorie** | Instance |

Créer l'un de plusieurs types d'objets choisi au hasard

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `object1` | Objet | — | Premier objet candidat; optionnel |
| `object2` | Objet | — | Deuxième objet candidat; optionnel |
| `object3` | Objet | — | Troisième objet candidat; optionnel |
| `object4` | Objet | — | Quatrième objet candidat; optionnel |

### Détruire une instance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `destroy_instance` |
| **Icône** | 💥 |
| **Catégorie** | Instance |
| **S'applique à** | self / other / object |

Détruire une instance

*Paramètres:* aucun

### Détruire à une position

| Propriété | Valeur |
|----------|-------|
| **Nom** | `destroy_at_position` |
| **Icône** | 💣 |
| **Catégorie** | Instance |

Détruire les instances dans un rayon autour de (x, y)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | `all` | Quel type d'objet détruire. « all » détruit toutes les instances à portée ; « solid » uniquement les solides (par ex. les murs) ; « non-solid » tout sauf les solides.; Choix: `all`, `solid`, `non-solid` |
| `x` | Texte | `self.x` | Position X (expression acceptée, par ex. self.x) |
| `y` | Texte | `self.y` | Position Y (expression acceptée, par ex. self.y) |
| `relative` | Oui/Non | Non | Traiter X/Y comme des décalages par rapport à la position de cette instance au lieu de coordonnées absolues; optionnel |
| `radius` | Nombre | `32` | Rayon en pixels autour de (x, y). Par défaut 32 = ~une case de grille. |

### Définir l'image d'animation

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_image_index` |
| **Icône** | 🖼️ |
| **Catégorie** | Instance |

Définir l'image d'animation actuelle du sprite de l'instance

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `frame` | Nombre | `0` | Index de l'image |

### Définir la vitesse d'animation

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_image_speed` |
| **Icône** | ⏩ |
| **Catégorie** | Instance |

Définir la vitesse de lecture de l'animation du sprite de l'instance

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `speed` | Nombre | `1.0` | Images avancées par étape (0 = en pause) |

### Définir le sprite

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_sprite` |
| **Icône** | 🖼️ |
| **Catégorie** | Instance |

Changer le sprite et/ou l'image/la vitesse d'animation d'une instance

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite à utiliser (ou « <self> » pour conserver l'actuel) |
| `subimage` | Nombre | `-1` | Index d'image à définir ; -1 pour laisser inchangé |
| `speed` | Nombre | `-1` | Vitesse d'animation ; -1 pour laisser inchangé |

### Démarrer l'animation

| Propriété | Valeur |
|----------|-------|
| **Nom** | `start_animation` |
| **Icône** | ▶️ |
| **Catégorie** | Instance |

Reprendre l'animation du sprite de l'instance (image_speed = 1)

*Paramètres:* aucun

### Arrêter l'animation

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_animation` |
| **Icône** | ⏸️ |
| **Catégorie** | Instance |

Mettre en pause l'animation du sprite de l'instance (image_speed = 0)

*Paramètres:* aucun

### Tester le nombre d'instances

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_instance_count` |
| **Icône** | ❓🔢 |
| **Catégorie** | Instance |

Condition : comparer le nombre d'instances d'un objet

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | Objet à compter |
| `number` | Nombre | `0` | Valeur de comparaison |
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="score"></a>
## Score

### Effacer le tableau des scores

| Propriété | Valeur |
|----------|-------|
| **Nom** | `clear_highscore` |
| **Icône** | 🗑️🏆 |
| **Catégorie** | Score |

Effacer toutes les entrées du tableau des scores

*Paramètres:* aucun

### Dessiner la barre de santé

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_health_bar` |
| **Icône** | 🩺 |
| **Catégorie** | Score |

Dessiner la santé actuelle sous forme de barre à deux couleurs

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x1` | Nombre | `0` | X gauche |
| `y1` | Nombre | `0` | Y supérieur |
| `x2` | Nombre | `100` | X droit |
| `y2` | Nombre | `20` | Y inférieur |
| `back_color` | Couleur | `#FF0000` | Couleur de l'arrière-plan (vide) |
| `bar_color` | Couleur | `#00FF00` | Couleur de remplissage (santé) |

### Dessiner les vies

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_lives` |
| **Icône** | 🖍️❤️ |
| **Catégorie** | Score |

Dessiner le nombre de vies actuel sous forme d'images de sprite répétées

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `sprite` | Sprite | — | Sprite dessiné une fois par vie restante; optionnel |
| `scale` | Nombre | `1.0` | Facteur d'échelle uniforme pour l'icône de vie (1.0 = taille native); optionnel |
| `relative` | Oui/Non | Non | Dessiner par rapport à la position de cette instance au lieu de coordonnées d'écran absolues; optionnel |

### Dessiner le score

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_score` |
| **Icône** | 🖍️🏆 |
| **Catégorie** | Score |

Dessiner le score actuel à l'écran

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `caption` | Texte | `Score: ` | Texte affiché avant la valeur du score; optionnel |
| `relative` | Oui/Non | Non | Dessiner par rapport à la position de cette instance au lieu de coordonnées d'écran absolues; optionnel |

### Définir la santé

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_health` |
| **Icône** | 💚 |
| **Catégorie** | Score |

Définir la santé, ou l'incrémenter avec Relatif

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `100` | Valeur de santé (0-100) |
| `relative` | Oui/Non | Non | Ajouter à la santé actuelle au lieu de la remplacer |

### Définir les vies

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_lives` |
| **Icône** | ❤️ |
| **Catégorie** | Score |

Définir les vies, ou les incrémenter avec Relatif

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `3` | Nombre de vies |
| `relative` | Oui/Non | Non | Ajouter aux vies actuelles au lieu de les remplacer |

### Définir le score

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_score` |
| **Icône** | 🏆 |
| **Catégorie** | Score |

Définir le score, ou l'incrémenter avec Relatif

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `0` | Valeur de score à définir |
| `relative` | Oui/Non | Non | Ajouter au score actuel au lieu de le remplacer |

### Afficher le tableau des scores

| Propriété | Valeur |
|----------|-------|
| **Nom** | `show_highscore` |
| **Icône** | 🏆 |
| **Catégorie** | Score |

Afficher la boîte de dialogue du tableau des meilleurs scores

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `background` | Couleur | `#FFFFDD` | Couleur d'arrière-plan de la boîte de dialogue; optionnel |
| `new_color` | Couleur | `#FF0000` | Couleur utilisée pour la nouvelle entrée (qualifiée); optionnel |
| `other_color` | Couleur | `#000000` | Couleur utilisée pour les autres entrées; optionnel |
| `allow_new_entry` | Oui/Non | Oui | Demander le nom si le score actuel se qualifie |

### Tester la santé

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_health` |
| **Icône** | ❓💚 |
| **Catégorie** | Score |

Condition : comparer la santé actuelle à une valeur

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Nombre | `0` | Valeur de comparaison |

### Tester les vies

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_lives` |
| **Icône** | ❓❤️ |
| **Catégorie** | Score |

Condition : comparer le nombre de vies à une valeur

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `0` | Valeur de comparaison |
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Tester le score

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_score` |
| **Icône** | ❓🏆 |
| **Catégorie** | Score |

Condition : comparer le score à une valeur

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `0` | Valeur de comparaison |
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="room"></a>
## Salle

### Vérifier la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `check_room` |
| **Icône** | ❓🚪 |
| **Catégorie** | Salle |

Condition : vrai si la salle actuelle correspond

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `room` | Salle | — | Salle à comparer |
| `not_flag` | Oui/Non | Non | Inverser le résultat; optionnel |

### Terminer le jeu

| Propriété | Valeur |
|----------|-------|
| **Nom** | `game_end` |
| **Icône** | 🛑🎮 |
| **Catégorie** | Salle |

Terminer le jeu

*Paramètres:* aucun

### Aller à la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `goto_room` |
| **Icône** | 🚪 |
| **Catégorie** | Salle |

Basculer vers une salle spécifique

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `room` | Salle | — | Nom de la salle cible |
| `transition` | Choix | `none` | Effet de transition (actuellement accepté mais non rendu); Choix: `none`; optionnel |

### Si salle suivante existe

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_next_room_exists` |
| **Icône** | ❓➡️ |
| **Catégorie** | Salle |

Vérifier s'il existe une salle après la salle actuelle

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `then_actions` | Liste d'actions | — | Actions si la salle suivante existe |
| `else_actions` | Liste d'actions | — | Actions si la salle suivante n'existe pas |

### Si salle précédente existe

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_previous_room_exists` |
| **Icône** | ❓⬅️ |
| **Catégorie** | Salle |

Vérifier s'il existe une salle avant la salle actuelle

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `then_actions` | Liste d'actions | — | Actions si la salle précédente existe |
| `else_actions` | Liste d'actions | — | Actions si la salle précédente n'existe pas |

### Salle suivante

| Propriété | Valeur |
|----------|-------|
| **Nom** | `next_room` |
| **Icône** | ➡️ |
| **Catégorie** | Salle |

Aller à la salle suivante

*Paramètres:* aucun

### Salle précédente

| Propriété | Valeur |
|----------|-------|
| **Nom** | `previous_room` |
| **Icône** | ⬅️ |
| **Catégorie** | Salle |

Aller à la salle précédente

*Paramètres:* aucun

### Redémarrer la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `restart_room` |
| **Icône** | 🔄 |
| **Catégorie** | Salle |

Redémarrer la salle actuelle

*Paramètres:* aucun

### Définir le titre de la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_room_caption` |
| **Icône** | 🏷️ |
| **Catégorie** | Salle |

Définir le titre de la fenêtre de jeu

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `caption` | Texte | — | Texte du titre de la fenêtre |

---

<a id="timing"></a>
## Minuterie

### Régler une alarme

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_alarm` |
| **Icône** | ⏰ |
| **Catégorie** | Minuterie |

Régler une alarme

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `alarm_number` | Nombre | `0` | Quelle alarme (0-11) |
| `steps` | Nombre | `30` | Nombre d'étapes avant le déclenchement de l'alarme (30 = 0,5 s à 60 IPS) |

### Attendre

| Propriété | Valeur |
|----------|-------|
| **Nom** | `sleep` |
| **Icône** | 💤 |
| **Catégorie** | Minuterie |

Mettre le jeu en pause pendant un certain nombre de millisecondes, puis continuer. Les sons continuent de jouer pendant la pause (par exemple pour laisser un son se terminer avant de changer de salle). Remarque : le rendu et les entrées sont figés pendant l'attente, gardez donc des durées courtes

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `milliseconds` | Nombre | `1000` | Durée de la pause, en millisecondes (1000 = 1 seconde) |

---

<a id="audio"></a>
## Audio

### Vérifier si un son joue

| Propriété | Valeur |
|----------|-------|
| **Nom** | `check_sound` |
| **Icône** | ❓🔊 |
| **Catégorie** | Audio |

Condition : vrai si le son indiqué est en cours de lecture

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sound` | Son | — | Son à vérifier |
| `not_flag` | Oui/Non | Non | Inverser le résultat; optionnel |

### Jouer une musique

| Propriété | Valeur |
|----------|-------|
| **Nom** | `play_music` |
| **Icône** | 🎵 |
| **Catégorie** | Audio |

Jouer une musique de fond (en boucle)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `music` | Son | — | Fichier de musique à jouer |
| `loop` | Oui/Non | Oui | Jouer la musique en boucle |
| `volume` | Nombre | `0.7` | Volume (0.0 à 1.0) |

### Jouer un son

| Propriété | Valeur |
|----------|-------|
| **Nom** | `play_sound` |
| **Icône** | 🔊 |
| **Catégorie** | Audio |

Jouer un effet sonore une fois

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sound` | Son | — | Son à jouer |
| `volume` | Nombre | `1.0` | Volume (0.0 à 1.0) |

### Définir le volume

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_volume` |
| **Icône** | 🔉 |
| **Catégorie** | Audio |

Définir le volume global des sons/de la musique

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `volume` | Nombre | `1.0` | Volume (0.0 à 1.0) |

### Arrêter la musique

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_music` |
| **Icône** | 🔇 |
| **Catégorie** | Audio |

Arrêter la musique de fond

*Paramètres:* aucun

### Arrêter un son

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_sound` |
| **Icône** | 🔇 |
| **Catégorie** | Audio |

Arrêter un son en cours de lecture

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sound` | Son | — | Son à arrêter |

---

<a id="game"></a>
## Jeu

### Dessiner une flèche

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_arrow` |
| **Icône** | ➡️ |
| **Catégorie** | Jeu |

Dessiner une flèche d'un point à un autre

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x1` | Nombre | `0` | X de départ |
| `y1` | Nombre | `0` | Y de départ |
| `x2` | Nombre | `100` | X de la pointe |
| `y2` | Nombre | `100` | Y de la pointe |
| `tip_size` | Nombre | `10` | Taille de la pointe de flèche en pixels |

### Dessiner un arrière-plan

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_background` |
| **Icône** | 🌄 |
| **Catégorie** | Jeu |

Dessiner une image d'arrière-plan, éventuellement répétée sur tout l'écran

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `background` | Texte | — | Nom de l'arrière-plan |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `tiled` | Oui/Non | Non | Répéter sur tout l'écran; optionnel |

### Dessiner un cercle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_circle` |
| **Icône** | ⭕ |
| **Catégorie** | Jeu |

Dessiner un cercle plein ou en contour

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | X du centre |
| `y` | Nombre | `0` | Y du centre |
| `radius` | Nombre | `50` | Rayon du cercle |
| `filled` | Oui/Non | Oui | Plein, ou contour seulement; optionnel |

### Dessiner une ellipse

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_ellipse` |
| **Icône** | 🥚 |
| **Catégorie** | Jeu |

Dessiner une ellipse pleine ou en contour dans un cadre englobant

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x1` | Nombre | `0` | X gauche |
| `y1` | Nombre | `0` | Y supérieur |
| `x2` | Nombre | `100` | X droit |
| `y2` | Nombre | `100` | Y inférieur |
| `filled` | Oui/Non | Oui | Plein, ou contour seulement; optionnel |

### Dessiner une ligne

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_line` |
| **Icône** | 📏 |
| **Catégorie** | Jeu |

Dessiner une ligne entre deux points

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x1` | Nombre | `0` | X de départ |
| `y1` | Nombre | `0` | Y de départ |
| `x2` | Nombre | `100` | X de fin |
| `y2` | Nombre | `100` | Y de fin |

### Dessiner un rectangle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_rectangle` |
| **Icône** | 🟥 |
| **Catégorie** | Jeu |

Dessiner un rectangle plein ou en contour

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x1` | Nombre | `0` | X gauche |
| `y1` | Nombre | `0` | Y supérieur |
| `x2` | Nombre | `100` | X droit |
| `y2` | Nombre | `100` | Y inférieur |
| `filled` | Oui/Non | Oui | Plein, ou contour seulement; optionnel |

### Dessiner du texte mis à l'échelle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_scaled_text` |
| **Icône** | 🖍️ |
| **Catégorie** | Jeu |

Dessiner du texte à une échelle arbitraire

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `text` | Texte | — | Texte à dessiner |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `xscale` | Nombre | `1.0` | Facteur d'échelle horizontal |
| `yscale` | Nombre | `1.0` | Facteur d'échelle vertical |

### Dessiner un sprite

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_sprite` |
| **Icône** | 🖼️ |
| **Catégorie** | Jeu |

Dessiner une image de sprite à une position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite à dessiner |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `subimage` | Nombre | `0` | Index de l'image à dessiner |

### Dessiner du texte

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_text` |
| **Icône** | 🖍️ |
| **Catégorie** | Jeu |

Dessiner une chaîne de texte à une position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `text` | Texte | — | Texte à dessiner (prend en charge les expressions) |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `relative` | Oui/Non | Non | Dessiner par rapport à la position de cette instance au lieu de coordonnées d'écran absolues; optionnel |

### Dessiner une variable

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_variable` |
| **Icône** | 🔢 |
| **Catégorie** | Jeu |

Dessiner la valeur d'une variable à l'écran

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `variable` | Texte | — | Nom de la variable (self.var, global.var, ou nom simple) |

### Remplir l'écran d'une couleur

| Propriété | Valeur |
|----------|-------|
| **Nom** | `fill_color` |
| **Icône** | 🪣 |
| **Catégorie** | Jeu |

Remplir toute la zone d'affichage d'une couleur unie

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `color` | Couleur | `#000000` | Couleur hexadécimale RVB |

### Ouvrir une page web

| Propriété | Valeur |
|----------|-------|
| **Nom** | `open_webpage` |
| **Icône** | 🌐 |
| **Catégorie** | Jeu |

Ouvrir une URL dans le navigateur par défaut

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `url` | Texte | — | Adresse web à ouvrir |

### Redémarrer le jeu

| Propriété | Valeur |
|----------|-------|
| **Nom** | `restart_game` |
| **Icône** | 🔁🎮 |
| **Catégorie** | Jeu |

Redémarrer le jeu depuis la salle de départ

*Paramètres:* aucun

### Définir l'alpha

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_alpha` |
| **Icône** | 🌫️ |
| **Catégorie** | Jeu |

Définir la transparence de dessin pour les dessins suivants

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `alpha` | Nombre | `1.0` | Opacité de 0.0 (transparent) à 1.0 (opaque) |

### Définir la couleur

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_color` |
| **Icône** | 🎨 |
| **Catégorie** | Jeu |

Définir la couleur et l'alpha de dessin pour les dessins suivants

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `color` | Couleur | `#FFFFFF` | Couleur hexadécimale RVB |
| `alpha` | Nombre | `1.0` | Opacité 0.0–1.0; optionnel |

### Définir la couleur de dessin

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_draw_color` |
| **Icône** | 🎨 |
| **Catégorie** | Jeu |

Définir la couleur utilisée par les actions draw_* suivantes

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `color` | Couleur | `#000000` | Couleur hexadécimale RVB |

### Définir la police de dessin

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_draw_font` |
| **Icône** | 🔤 |
| **Catégorie** | Jeu |

Définir la police et l'alignement pour le dessin de texte suivant

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `font` | Texte | — | Nom de la police (vide = police par défaut); optionnel |
| `halign` | Choix | `left` | Alignement horizontal du texte; Choix: `left`, `center`, `right` |
| `valign` | Choix | `top` | Alignement vertical du texte; Choix: `top`, `middle`, `bottom` |

### Définir le titre de la fenêtre

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_window_caption` |
| **Icône** | 🪟 |
| **Catégorie** | Jeu |

Configurer l'affichage du score/des vies/de la santé dans le titre de la fenêtre

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `show_score` | Oui/Non | Oui | Ajouter le score actuel au titre de la fenêtre |
| `show_lives` | Oui/Non | Oui | Ajouter le nombre de vies actuel au titre de la fenêtre |
| `show_health` | Oui/Non | Non | Ajouter la valeur de santé actuelle au titre de la fenêtre |
| `caption` | Texte | — | Préfixe de titre optionnel affiché avant les compteurs; optionnel |

### Afficher les infos du jeu

| Propriété | Valeur |
|----------|-------|
| **Nom** | `show_info` |
| **Icône** | ℹ️ |
| **Catégorie** | Jeu |

Afficher l'écran d'informations du jeu

*Paramètres:* aucun

### Afficher un message

| Propriété | Valeur |
|----------|-------|
| **Nom** | `show_message` |
| **Icône** | 💬 |
| **Catégorie** | Jeu |

Afficher un message

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `message` | Texte | `Hello!` | Texte du message |

---

<a id="control"></a>
## Contrôle

### Vérifier si vide

| Propriété | Valeur |
|----------|-------|
| **Nom** | `check_empty` |
| **Icône** | 🔍 |
| **Catégorie** | Contrôle |

Vrai lorsque (x, y) est sans collision. À utiliser avec start_block/end_block pour conditionner la ou les actions suivantes, façon GM

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Texte | `self.x` | Position X à vérifier (expression acceptée, par ex. self.x + 32) |
| `y` | Texte | `self.y` | Position Y à vérifier (expression acceptée, par ex. self.y + 32) |
| `relative` | Oui/Non | Non | Traiter X/Y comme des décalages par rapport à la position de cette instance au lieu de coordonnées absolues; optionnel |
| `objects` | Choix | `solid` | Quelles instances comptent comme occupant la position; Choix: `solid`, `all` |

### Commentaire

| Propriété | Valeur |
|----------|-------|
| **Nom** | `comment` |
| **Icône** | ⚠️ |
| **Catégorie** | Contrôle |

Un commentaire dans la liste d'actions (sans effet à l'exécution)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `text` | Texte | — | Texte de commentaire libre; optionnel |

### Sinon

| Propriété | Valeur |
|----------|-------|
| **Nom** | `else_action` |
| **Icône** | ⚡ |
| **Catégorie** | Contrôle |

Marque la branche « sinon » d'une condition

*Paramètres:* aucun

### Fin de bloc

| Propriété | Valeur |
|----------|-------|
| **Nom** | `end_block` |
| **Icône** | 📁 |
| **Catégorie** | Contrôle |

Terminer un bloc d'actions

*Paramètres:* aucun

### Exécuter du code

| Propriété | Valeur |
|----------|-------|
| **Nom** | `execute_code` |
| **Icône** | 📜 |
| **Catégorie** | Contrôle |

Exécuter un bloc de code Python intégré

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `code` | Code | — | Code source Python à évaluer sur l'instance |

### Exécuter un script

| Propriété | Valeur |
|----------|-------|
| **Nom** | `execute_script` |
| **Icône** | 📜 |
| **Catégorie** | Contrôle |

Exécuter l'un des scripts du projet

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `script` | Script | — | Nom du script du projet à exécuter |
| `arg0` | Texte | — | Disponible dans le script sous argument0; optionnel |
| `arg1` | Texte | — | Disponible dans le script sous argument1; optionnel |
| `arg2` | Texte | — | Disponible dans le script sous argument2; optionnel |
| `arg3` | Texte | — | Disponible dans le script sous argument3; optionnel |
| `arg4` | Texte | — | Disponible dans le script sous argument4; optionnel |

### Quitter l'événement

| Propriété | Valeur |
|----------|-------|
| **Nom** | `exit_event` |
| **Icône** | 🚪 |
| **Catégorie** | Contrôle |

Arrêter l'exécution des actions restantes de cet événement

*Paramètres:* aucun

### Si poussée possible

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_can_push` |
| **Icône** | 📦 |
| **Catégorie** | Contrôle |

Vérifier si une caisse/un objet peut être poussé dans la direction actuelle (façon Sokoban)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `direction` | Choix | `facing` | Direction à vérifier pour la poussée; Choix: `facing` |
| `object_type` | Texte | `box` | Type d'objet poussé |
| `then_action` | Choix | `push_and_move` | Action si la poussée est possible; Choix: `push_and_move`, `none` |
| `else_action` | Choix | `stop_movement` | Action si la poussée est bloquée; Choix: `stop_movement`, `none` |

### Si collision

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_collision` |
| **Icône** | ❓💥 |
| **Catégorie** | Contrôle |

Condition : vrai si l'instance entrerait en collision au décalage (x, y)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Décalage horizontal à tester |
| `y` | Nombre | `0` | Décalage vertical à tester |
| `object` | Texte | `any` | « any », « solid », ou un nom d'objet; Choix: `any`, `solid`; optionnel |
| `not_flag` | Oui/Non | Non | Inverser le résultat; optionnel |

### Si collision à

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_collision_at` |
| **Icône** | 🎯 |
| **Catégorie** | Contrôle |

Vérifier une collision à une position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Texte | `self.x + 32` | Expression de la position X |
| `y` | Texte | `self.y` | Expression de la position Y |
| `object_type` | Choix | `any` | Type d'objet à vérifier; Choix: `any`, `solid` |
| `then_actions` | Liste d'actions | — | Actions si collision trouvée |
| `else_actions` | Liste d'actions | — | Actions si aucune collision |

### Si condition

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_condition` |
| **Icône** | ❓ |
| **Catégorie** | Contrôle |

Vérification conditionnelle avec des actions alors/sinon

*Paramètres:* aucun

### Si l'objet existe

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_object_exists` |
| **Icône** | ❓ |
| **Catégorie** | Contrôle |

Condition : vrai s'il existe au moins une instance de l'objet

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | Type d'objet à vérifier |
| `not_flag` | Oui/Non | Non | Inverser le résultat (agir quand l'objet n'existe PAS); optionnel |

### Répéter

| Propriété | Valeur |
|----------|-------|
| **Nom** | `repeat` |
| **Icône** | 🔁 |
| **Catégorie** | Contrôle |

Répéter l'action/le bloc suivant N fois

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `times` | Nombre | `10` | Nombre de répétitions |
| `actions` | Liste d'actions | — | Actions à répéter |

### Définir une variable

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_variable` |
| **Icône** | 📝 |
| **Catégorie** | Contrôle |

Définir une variable d'instance ou globale

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `variable` | Texte | — | Nom de la variable |
| `value` | Texte | `0` | Valeur (nombre, chaîne ou expression) |
| `scope` | Choix | `self` | Portée de la variable; Choix: `self`, `other`, `global` |
| `relative` | Oui/Non | Non | Ajouter à la valeur actuelle au lieu de la remplacer |

### Début de bloc

| Propriété | Valeur |
|----------|-------|
| **Nom** | `start_block` |
| **Icône** | 📂 |
| **Catégorie** | Contrôle |

Débuter un bloc d'actions (pour le regroupement)

*Paramètres:* aucun

### Tester la chance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_chance` |
| **Icône** | 🎲❓ |
| **Catégorie** | Contrôle |

Condition : vrai avec une probabilité de 1 sur « sides »

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sides` | Nombre | `6` | Une chance sur N d'être vrai |

### Tester une expression

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_expression` |
| **Icône** | ❓ |
| **Catégorie** | Contrôle |

Tester si une expression est vraie

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `expression` | Texte | — | Expression à évaluer (vrai si >= 0.5) |
| `then_actions` | Liste d'actions | — | Actions si vrai |
| `else_actions` | Liste d'actions | — | Actions si faux |

### Poser une question

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_question` |
| **Icône** | ❓💬 |
| **Catégorie** | Contrôle |

Condition : afficher une boîte de dialogue oui/non ; vrai si l'utilisateur répond oui

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `question` | Texte | `Continue?` | Question affichée au joueur |

### Tester une variable

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_variable` |
| **Icône** | ❓ |
| **Catégorie** | Contrôle |

Tester la valeur d'une variable d'instance ou globale

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `variable` | Texte | — | Nom de la variable |
| `value` | Texte | `0` | Valeur à comparer |
| `scope` | Choix | `self` | Portée de la variable; Choix: `self`, `other`, `global` |
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="grid"></a>
## Grille

### Si aligné sur la grille

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_on_grid` |
| **Icône** | ▦ |
| **Catégorie** | Grille |

Vérifier si l'objet est aligné sur la grille

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `grid_size` | Nombre | `32` | Taille de la case de grille en pixels |
| `then_actions` | Liste d'actions | — | Actions si aligné sur la grille |
| `else_actions` | Liste d'actions | — | Actions si non aligné sur la grille |

### Aligner sur la grille

| Propriété | Valeur |
|----------|-------|
| **Nom** | `snap_to_grid` |
| **Icône** | ▦ |
| **Catégorie** | Grille |

Aligner la position de l'instance sur la grille

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `grid_size` | Nombre | `32` | Taille de la case de grille en pixels |

### Arrêter si aucune touche

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_if_no_keys` |
| **Icône** | ▦ |
| **Catégorie** | Grille |

Arrêter le mouvement sur la grille quand aucune touche de déplacement n'est enfoncée (parfait pour un alignement fluide sur la grille)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `grid_size` | Nombre | `32` | Taille de la case de grille en pixels |

### Tester l'alignement sur la grille

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_alignment` |
| **Icône** | ❓▦ |
| **Catégorie** | Grille |

Condition : vrai si l'instance est alignée sur une grille

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `hsnap` | Nombre | `32` | Espacement horizontal de la grille en pixels |
| `vsnap` | Nombre | `32` | Espacement vertical de la grille en pixels |

---

<a id="views"></a>
## Vues

### Activer les vues

| Propriété | Valeur |
|----------|-------|
| **Nom** | `enable_views` |
| **Icône** | 🎥 |
| **Catégorie** | Vues |

Activer ou désactiver le système de caméra/vue de la salle (permet à un niveau de défiler lorsqu'il est plus grand que la fenêtre)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `enable` | Oui/Non | Oui | Activé = vues de caméra ; désactivé = dessiner toute la salle d'un coup |

### Définir une vue

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_view` |
| **Icône** | 🎥 |
| **Catégorie** | Vues |

Configurer une vue de caméra : quelle partie de la salle elle montre, où elle s'affiche à l'écran, et un objet à suivre

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `view` | Choix | `0` | Laquelle des 8 vues configurer; Choix: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Oui/Non | Oui | Dessiner cette vue |
| `view_x` | Nombre | `0` | Bord gauche de la région de la salle affichée |
| `view_y` | Nombre | `0` | Bord supérieur de la région de la salle affichée |
| `view_w` | Nombre | `800` | Largeur de la région de la salle affichée |
| `view_h` | Nombre | `600` | Hauteur de la région de la salle affichée |
| `port_x` | Nombre | `0` | Bord gauche à l'écran |
| `port_y` | Nombre | `0` | Bord supérieur à l'écran |
| `port_w` | Nombre | `800` | Largeur dessinée à l'écran |
| `port_h` | Nombre | `600` | Hauteur dessinée à l'écran |
| `follow` | Objet | — | Objet suivi par la caméra (vide = vue fixe); optionnel |
| `hborder` | Nombre | `32` | Bordure horizontale avant que la caméra ne défile |
| `vborder` | Nombre | `32` | Bordure verticale avant que la caméra ne défile |
| `hspeed` | Nombre | `-1` | Vitesse de défilement horizontal maximale (-1 = instantané) |
| `vspeed` | Nombre | `-1` | Vitesse de défilement vertical maximale (-1 = instantané) |

---

<a id="3d-view"></a>
## Vue 3D

### Dessiner l'ATH DOOM

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_doom_hud` |
| **Icône** | 🎯 |
| **Catégorie** | Vue 3D |

Dessiner une barre d'état inférieure façon DOOM (barre de santé + valeur, score, vies, un compteur d'objectif et une icône de visage réactive à la santé) par-dessus la vue en lancer de rayons

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Bord gauche de la barre, en pixels d'écran |
| `y` | Nombre | `-1` | Bord supérieur de la barre ; une valeur négative l'aligne automatiquement en bas de la fenêtre, sous la vue réduite; optionnel |
| `width` | Nombre | `0` | Largeur de la barre (0 = pleine largeur de la fenêtre); optionnel |
| `height` | Nombre | `42` | Hauteur de la barre ; à garder cohérente avec la bande viewport_height réservée dans enable_raycast_view; optionnel |
| `back_color` | Couleur | `#101010` | Panneau d'arrière-plan de la barre; optionnel |
| `divider_color` | Couleur | `#505050` | Bordure supérieure et fond de la barre de santé; optionnel |
| `text_color` | Couleur | `#ffffff` | Couleur de tout le texte de la barre; optionnel |
| `health_label` | Texte | `Health` | optionnel |
| `health_bar_width` | Nombre | `90` | optionnel |
| `health_bar_height` | Nombre | `14` | optionnel |
| `bar_color` | Couleur | `#20c020` | Couleur de remplissage de la barre de santé; optionnel |
| `face_sprite` | Sprite | — | Bande horizontale d'images de visage, du plus sain au moins sain (vide = pas d'icône de visage); optionnel |
| `face_frames` | Nombre | `4` | Nombre d'images de la bande de visage ; la santé y est répartie uniformément; optionnel |
| `score_label` | Texte | `Score: ` | optionnel |
| `lives_sprite` | Sprite | — | Sprite dessiné une fois par vie restante; optionnel |
| `lives_scale` | Nombre | `1.0` | optionnel |
| `objective_value` | Texte | `0` | Expression affichée après l'étiquette d'objectif (associez votre propre variable de clé/quête); optionnel |
| `objective_label` | Texte | `Keys: ` | optionnel |

### Dessiner la mini-carte

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_minimap` |
| **Icône** | 🗺️ |
| **Catégorie** | Vue 3D |

Dessiner une mini-carte orientée nord des murs de la salle en lancer de rayons, avec un repère indiquant où se trouve la caméra et dans quelle direction elle regarde

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Bord gauche de la mini-carte, en pixels d'écran |
| `y` | Nombre | `0` | Bord supérieur de la mini-carte, en pixels d'écran |
| `size` | Nombre | `120` | Largeur et hauteur du carré de la mini-carte, en pixels; optionnel |
| `back_color` | Couleur | `#101018` | Couleur du panneau derrière la carte; optionnel |
| `wall_color` | Couleur | `#8080a0` | Couleur des lignes des murs; optionnel |
| `player_color` | Couleur | `#ffd040` | Couleur du repère de caméra et de sa ligne de cap; optionnel |

### Activer la vue Raycast

| Propriété | Valeur |
|----------|-------|
| **Nom** | `enable_raycast_view` |
| **Icône** | 🕹️ |
| **Catégorie** | Vue 3D |

Afficher la salle en vue 3D à la première personne façon Doom/Wolfenstein (murs, ciel, sol) au lieu de la vue du dessus

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `enable` | Oui/Non | Oui | Activé = vue à la première personne (raycast) ; désactivé = vue du dessus normale |
| `camera_object` | Objet | — | Objet dont la position + l'angle de vue est la caméra (vide = l'objet qui exécute cette action); optionnel |
| `fov` | Nombre | `66` | Champ de vision horizontal en degrés; optionnel |
| `render_distance` | Nombre | `20` | Longueur maximale des rayons en cases de grille; optionnel |
| `cell_size` | Nombre | `32` | Taille de la case de grille en pixels (correspond à la grille de placement des murs); optionnel |
| `columns` | Nombre | `320` | Colonnes d'écran à traiter en lancer de rayons (moins = plus rapide/plus grossier); optionnel |
| `wall_color` | Couleur | `#993333` | Couleur unie des murs lorsqu'aucune texture de mur n'est définie; optionnel |
| `floor_color` | Couleur | `#464632` | Couleur unie du sol lorsqu'aucune texture de sol n'est définie; optionnel |
| `ceiling_color` | Couleur | `#87CEEB` | Couleur unie du plafond lorsqu'aucune texture de ciel/plafond n'est définie; optionnel |
| `wall_texture` | Sprite | — | Sprite pour texturer chaque mur (vide = couleur unie); optionnel |
| `sky_texture` | Sprite | — | Sprite pour un ciel panoramique au-dessus du plafond (vide = uni); optionnel |
| `floor_texture` | Sprite | — | Sprite projeté sur le sol (vide = couleur unie); optionnel |
| `ceiling_texture` | Sprite | — | Sprite projeté sur le plafond lorsqu'aucun ciel n'est défini; optionnel |
| `wall_textured` | Oui/Non | Oui | Désactivé force des couleurs de mur unies même si une texture est définie; optionnel |
| `floor_cast_res` | Nombre | `4` | Sous-échantillonnage du sol projeté (plus élevé = plus rapide + plus grossier); optionnel |
| `viewport_height` | Nombre | `0` | Réduire la vue 3D à cette hauteur en pixels (format boîte aux lettres), en réservant la bande inférieure pour une barre d'état façon DOOM (0 = pleine hauteur de la fenêtre, inchangé); optionnel |

### Définir l'angle de vue

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_facing_angle` |
| **Icône** | 🧭 |
| **Catégorie** | Vue 3D |

Définir la direction du regard de l'instance pour une caméra à lancer de rayons (première personne) — indépendante de la vitesse de déplacement

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `angle` | Nombre | `0` | Degrés (0=droite, 90=haut, 180=gauche, 270=bas) |
| `relative` | Oui/Non | Non | Ajouter à l'angle de vue actuel au lieu de le remplacer; optionnel |

---

## Voir aussi

- [Référence des Événements](Event-Reference_fr) — les événements qui déclenchent les actions
- [Guide des Préréglages](Preset-Guide_fr) — quelles de ces actions le préréglage de votre projet affiche réellement dans le sélecteur Blockly et le panneau structuré Actions
- [Vue 3D](3D-View_fr) — les actions de vue à la première personne (raycast)
- [Extensions](Extensions_fr) — comment les actions de la Vue 3D sont fournies
