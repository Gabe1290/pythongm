# Instance

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

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

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (25)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (16)
- [Particles](Full-Action-Reference-Particles_fr) (8)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
