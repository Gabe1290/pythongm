# Vue 3D

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Apply Gravity

| Propriété | Valeur |
|----------|-------|
| **Nom** | `apply_gravity` |
| **Icône** | ⬇️ |
| **Catégorie** | Vue 3D |

Continuous falling/landing physics for the block-world camera -- bind in the Step event (not a keyboard-held event) so it runs every frame regardless of movement input. No-op unless Enable Block World View's Gravity parameter is set above 0

*Paramètres:* aucun

### Break Block

| Propriété | Valeur |
|----------|-------|
| **Nom** | `break_block` |
| **Icône** | ⛏️ |
| **Catégorie** | Vue 3D |

Remove the block the camera is looking at -- also picks it up into the calling instance's inventory if Enable Block World View's Inventory is on, and refuses if the block is protected (Set Block Protection) and the required key isn't in inventory

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `reach` | Nombre | `5` | How many cells ahead you can reach, in grid cells; optionnel |

### Draw Block World HUD

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_block_world_hud` |
| **Icône** | 🧰 |
| **Catégorie** | Vue 3D |

Draw a crosshair plus a hotbar strip (the selected slot highlighted, with a count on each slot once Inventory is on) -- call from the player/camera object's own Draw event

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `slot_size` | Nombre | `40` | Width and height of each hotbar slot, in pixels; optionnel |
| `gap` | Nombre | `6` | Space between hotbar slots, in pixels; optionnel |
| `margin_bottom` | Nombre | `16` | Space between the hotbar and the bottom of the screen; optionnel |
| `back_color` | Couleur | `#202020` | Fill colour of an unselected slot; optionnel |
| `selected_color` | Couleur | `#ffd040` | Fill colour of the currently selected slot; optionnel |
| `border_color` | Couleur | `#ffffff` | Outline colour of every slot; optionnel |
| `text_color` | Couleur | `#ffffff` | Colour of each slot's block-type label; optionnel |
| `crosshair_size` | Nombre | `12` | Width and height of the centre crosshair, in pixels; optionnel |
| `crosshair_color` | Couleur | `#ffffff` | Colour of the centre crosshair; optionnel |

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
| `mark_object` | Objet | — | Also dot every instance of this object onto the map (blank = show walls and player only); optionnel |
| `mark_color` | Couleur | `#40e0ff` | Colour of the Mark Object dots; optionnel |
| `mark_object_2` | Objet | — | A second object to dot on, in its own colour; optionnel |
| `mark_color_2` | Couleur | `#ff5050` | Colour of the Mark Object 2 dots; optionnel |

### Enable Block World View

| Propriété | Valeur |
|----------|-------|
| **Nom** | `enable_block_world_view` |
| **Icône** | 🧱 |
| **Catégorie** | Vue 3D |

Render the room as a first-person voxel view (single layer) instead of the top-down view

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `enable` | Oui/Non | Oui | On = first-person block view; off = normal top-down |
| `camera_object` | Objet | — | Objet dont la position + l'angle de vue est la caméra (vide = l'objet qui exécute cette action); optionnel |
| `z_layer` | Nombre | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); optionnel |
| `fov` | Nombre | `66` | Champ de vision horizontal en degrés; optionnel |
| `render_distance` | Nombre | `20` | Longueur maximale des rayons en cases de grille; optionnel |
| `cell_size` | Nombre | `32` | Grid cell size in pixels (match the block-placement grid); optionnel |
| `columns` | Nombre | `320` | Colonnes d'écran à traiter en lancer de rayons (moins = plus rapide/plus grossier); optionnel |
| `wall_color` | Couleur | `#8a8a8a` | Flat colour used only if Textured Blocks is off; optionnel |
| `floor_color` | Couleur | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); optionnel |
| `ceiling_color` | Couleur | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); optionnel |
| `pitch` | Nombre | `0` | Degrees to look up (+) or down (-); 0 is level; optionnel |
| `wall_textured` | Oui/Non | Oui | Off forces flat block colours even though real textures are available; optionnel |
| `top_cast_res` | Nombre | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); optionnel |
| `eye_height` | Nombre | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); optionnel |
| `gravity` | Nombre | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; optionnel |
| `inventory` | Oui/Non | Non | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; optionnel |
| `generate` | Oui/Non | Non | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; optionnel |
| `seed` | Nombre | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; optionnel |

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

### Jump

| Propriété | Valeur |
|----------|-------|
| **Nom** | `jump` |
| **Icône** | ⬆️ |
| **Catégorie** | Vue 3D |

Give the block-world camera upward velocity -- only while standing on solid ground (no double/air jumps). Needs Gravity configured (Enable Block World View) and Apply Gravity bound in the Step event, or nothing brings it back down

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `speed` | Nombre | `0.35` | Initial upward velocity, in cells/step; optionnel |

### Load Block World

| Propriété | Valeur |
|----------|-------|
| **Nom** | `load_block_world` |
| **Icône** | 📂 |
| **Catégorie** | Vue 3D |

Load a pre-authored world (blocks placed by a generator or hand-authored file) into the current room, replacing whatever blocks are there

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `data_file` | Texte | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Look Up / Down

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_look_pitch` |
| **Icône** | 🔭 |
| **Catégorie** | Vue 3D |

Tilt the block-world view up or down

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `pitch` | Nombre | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Oui/Non | Non | On = add to the current angle, for a look control you can hold down; off = set it outright; optionnel |

### Move And Collide

| Propriété | Valeur |
|----------|-------|
| **Nom** | `move_and_collide` |
| **Icône** | 🚶 |
| **Catégorie** | Vue 3D |

Move this step, checked against the block grid, with automatic footing (step up one block, drop any distance) -- the camera's z_layer follows if this is the block-world camera

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `dx` | Nombre | `0` | How far to move on x this step, in pixels |
| `dy` | Nombre | `0` | How far to move on y this step, in pixels |
| `collide` | Oui/Non | Oui | Off ignores the block grid entirely (flying/debug); optionnel |

### Place Block

| Propriété | Valeur |
|----------|-------|
| **Nom** | `place_block` |
| **Icône** | 🧱 |
| **Catégorie** | Vue 3D |

Put a block in the empty cell the camera is looking at -- unlimited unless Enable Block World View's Inventory is on, which draws from what Break Block has picked up

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `block` | Choix | `stone` | Which kind of block to place; Choix: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Nombre | `5` | How many cells ahead you can build, in grid cells; optionnel |

### Select Hotbar Slot

| Propriété | Valeur |
|----------|-------|
| **Nom** | `select_hotbar_slot` |
| **Icône** | 🔢 |
| **Catégorie** | Vue 3D |

Choose which block the hotbar has selected, for place_block to build with -- bind Place Block's Block parameter to the expression "hotbar_block" to use it

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `index` | Nombre | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Oui/Non | Non | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; optionnel |

### Set Block Protection

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_block_protection` |
| **Icône** | 🔒 |
| **Catégorie** | Vue 3D |

Require a specific block type in inventory before Break Block can remove a chosen block type -- call once per protected type, needs Enable Block World View's Inventory on or the requirement can never be satisfied

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `block_type` | Choix | `diamond_block` | Which block type becomes protected; Choix: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Choix | `gold_block` | Which block type must be in inventory to break it; Choix: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Set Block Reward

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_block_reward` |
| **Icône** | 💎 |
| **Catégorie** | Vue 3D |

Award score when Break Block successfully removes a chosen block type -- call once per rewarded type (e.g. in the room's create event, right after Enable Block World View). A mine-to-collect ore/gem block: place it in the terrain, register its reward, and breaking it awards the points automatically

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `block_type` | Choix | `diamond_block` | Which block type awards score when broken; Choix: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Nombre | `10` | Score awarded per block of this type broken |

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
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (25)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Particles](Full-Action-Reference-Particles_fr) (8)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
