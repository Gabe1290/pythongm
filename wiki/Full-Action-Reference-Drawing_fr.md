# Dessin

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Dessiner une flèche

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_arrow` |
| **Icône** | ➡️ |
| **Catégorie** | Dessin |

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
| **Catégorie** | Dessin |

Dessiner une image d'arrière-plan, éventuellement répétée sur tout l'écran

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `background` | Texte | — | Nom de l'arrière-plan |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `tiled` | Oui/Non | Non | Répéter sur tout l'écran; optionnel |

### Dessiner une ellipse

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_ellipse` |
| **Icône** | 🥚 |
| **Catégorie** | Dessin |

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
| **Catégorie** | Dessin |

Dessiner une ligne entre deux points

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x1` | Nombre | `0` | X de départ |
| `y1` | Nombre | `0` | Y de départ |
| `x2` | Nombre | `100` | X de fin |
| `y2` | Nombre | `100` | Y de fin |

### Dessiner du texte mis à l'échelle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_scaled_text` |
| **Icône** | 🖍️ |
| **Catégorie** | Dessin |

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
| **Catégorie** | Dessin |

Dessiner une image de sprite à une position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite à dessiner |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `subimage` | Nombre | `0` | Index de l'image à dessiner |

### Dessiner une variable

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_variable` |
| **Icône** | 🔢 |
| **Catégorie** | Dessin |

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
| **Catégorie** | Dessin |

Remplir toute la zone d'affichage d'une couleur unie

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `color` | Couleur | `#000000` | Couleur hexadécimale RVB |

### Définir la couleur

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_color` |
| **Icône** | 🎨 |
| **Catégorie** | Dessin |

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
| **Catégorie** | Dessin |

Définir la couleur utilisée par les actions draw_* suivantes

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `color` | Couleur | `#000000` | Couleur hexadécimale RVB |

### Définir la police de dessin

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_draw_font` |
| **Icône** | 🔤 |
| **Catégorie** | Dessin |

Définir la police et l'alignement pour le dessin de texte suivant

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `font` | Texte | — | Nom de la police (vide = police par défaut); optionnel |
| `halign` | Choix | `left` | Alignement horizontal du texte; Choix: `left`, `center`, `right` |
| `valign` | Choix | `top` | Alignement vertical du texte; Choix: `top`, `middle`, `bottom` |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (21)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (6)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (14)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (3)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (18)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (22)
- [Particules](Full-Action-Reference-Particles_fr) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_fr) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_fr) (16)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
