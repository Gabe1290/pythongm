# Vue 3D

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

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

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (2)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (20)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
