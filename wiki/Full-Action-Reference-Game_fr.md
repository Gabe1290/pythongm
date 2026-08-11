# Jeu

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

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

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (2)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (4)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
