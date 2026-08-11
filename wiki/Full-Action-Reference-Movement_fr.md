# Mouvement

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

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

## Autres Catégories

- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (2)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (20)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (4)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
