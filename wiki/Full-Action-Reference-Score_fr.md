# Score

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

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

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (21)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (14)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (3)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (18)
- [Dessin](Full-Action-Reference-Drawing_fr) (11)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (22)
- [Particules](Full-Action-Reference-Particles_fr) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_fr) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_fr) (16)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
