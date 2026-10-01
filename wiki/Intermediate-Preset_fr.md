# Préréglage Intermédiaire

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Préréglage Débutant](Beginner-Preset_fr)*

> **Généré automatiquement** à partir de `get_intermediate()` dans `config/blockly_config.py` par `tools/gen_preset_docs.py` — ne pas modifier à la main ; relancez le générateur après avoir changé le préréglage.

> **Ce que ce préréglage restreint réellement :** ce préréglage filtre À LA FOIS la palette de blocs visuels Blockly ET les menus « Ajouter un événement »/« Ajouter une action » du panneau structuré — quel que soit l'éditeur utilisé, seuls les événements/actions listés ci-dessous apparaissent. Le préréglage d'un *projet* se règle de deux façons : **`Préférences > Édition de l'IDE`** choisit le préréglage par défaut des *nouveaux* projets (édition Débutant -> ce préréglage ; les projets existants ne sont jamais modifiés en changeant l'édition), et **`Outils > Configurer les blocs d'action...`** change le préréglage du projet *actuellement ouvert* à tout moment. L'édition par défaut de l'IDE est Débutant, donc les nouveaux projets d'une installation fraîche démarrent exactement sur cette liste. Cette liste ne couvre pas les actions d'[extension](Extensions_fr) (Vue 3D, Réseau, …) : les actions d'une extension apparaissent dans tous les préréglages, y compris celui-ci, une fois qu'elle est active pour le projet — voir la section « Quelles actions d'extension apparaissent dans la palette » de la page [Extensions](Extensions_fr).

## Aperçu

Ce préréglage active **21** types d'événements et **118** types d'actions.

---

## Événements

| Événement | Nom du bloc | Catégorie | Description |
|-------|------------|----------|-------------|
| Create | `create` | Objet | Exécuté une fois quand l'objet est créé pour la première fois |
| Destroy | `destroy` | Objet | Exécuté quand l'objet est détruit |
| Step | `step` | Objet | Exécuté à chaque image (utilisez-le pour des vérifications continues) |
| Keyboard (held) | `keyboard` | Entrée | Exécuté en continu tant qu'une touche est maintenue (pour un mouvement fluide) |
| Keyboard <No Key> | `keyboard_no_key` | Entrée | Exécuté quand aucune touche du clavier n'est actuellement enfoncée |
| Keyboard Press | `keyboard_press` | Entrée | Exécuté une fois quand une touche est enfoncée pour la première fois (pour un déplacement sur grille) |
| Collision With... | `collision` | Collision | Exécuté lors d'une collision avec un autre objet |
| Begin Step | `begin_step` | Étape | Exécuté au début de chaque image, avant les autres événements |
| End Step | `end_step` | Étape | Exécuté à la fin de chaque image, après les collisions mais avant le dessin |
| Alarm | `alarm` | Minuterie | Exécuté quand un compte à rebours d'alarme atteint zéro |
| Draw | `draw` | Dessin | Exécuté lors du dessin de l'objet (remplace le dessin automatique du sprite) |
| Draw GUI | `draw_gui` | Dessin | Dessiné par-dessus tout le reste (non affecté par la caméra/vue). À utiliser pour le HUD, le score, les vies. |
| Room End | `room_end` | Salle | Exécuté quand la salle se termine |
| Room Start | `room_start` | Salle | Exécuté quand la salle démarre (après les événements Create) |
| Game End | `game_end` | Jeu | Exécuté quand le jeu se termine |
| Game Start | `game_start` | Jeu | Exécuté quand le jeu démarre (dans la première salle uniquement) |
| Animation End | `animation_end` | Autre | Se déclenche quand l'animation du sprite atteint sa dernière image et recommence |
| Intersect Boundary | `intersect_boundary` | Autre | Exécuté quand l'instance touche le bord de la salle |
| No More Health | `no_more_health` | Autre | Exécuté quand la santé atteint 0 ou moins |
| No More Lives | `no_more_lives` | Autre | Exécuté quand les vies atteignent 0 ou moins |
| Outside Room | `outside_room` | Autre | Exécuté quand l'instance est entièrement hors de la salle |

---

## Actions

### Mouvement

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Rebondir | `bounce` | — |
| Sauter à une position | `jump_to_position` | `x`, `y`, `relative` |
| Sauter à une position aléatoire | `jump_to_random` | `snap_h`, `snap_v` |
| Sauter à la position de départ | `jump_to_start` | — |
| Déplacer sur la grille | `move_grid` | `direction`, `grid_size` |
| Se déplacer vers un point | `move_towards_point` | `x`, `y`, `speed` |
| Déplacer jusqu'au contact | `move_to_contact` | `direction`, `max_distance`, `object` |
| Inverser horizontalement | `reverse_horizontal` | — |
| Inverser verticalement | `reverse_vertical` | — |
| Définir direction et vitesse | `set_direction_speed` | `direction`, `speed` |
| Définir le frottement | `set_friction` | `friction` |
| Définir la gravité | `set_gravity` | `direction`, `gravity` |
| Définir la vitesse horizontale | `set_hspeed` | `speed` |
| Définir la vitesse verticale | `set_vspeed` | `speed` |
| Commencer à bouger (direction) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Arrêter le mouvement | `stop_movement` | — |

### Grille

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Si aligné sur la grille | `if_on_grid` | `grid_size`, `then_actions`, `else_actions` |
| Aligner sur la grille | `snap_to_grid` | `grid_size` |
| Tester l'alignement sur la grille | `test_alignment` | `hsnap`, `vsnap` |

### Instance

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Changer d'instance | `change_instance` | `object`, `perform_events` |
| Créer une instance | `create_instance` | `object`, `x`, `y`, `relative` |
| Créer une instance en mouvement | `create_moving_instance` | `object`, `x`, `y`, `speed`, `direction` |
| Créer une instance aléatoire | `create_random_instance` | `x`, `y`, `object1`, `object2`, `object3`, `object4` |
| Détruire une instance | `destroy_instance` | — |
| Détruire à une position | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Définir l'image d'animation | `set_image_index` | `frame` |
| Définir la vitesse d'animation | `set_image_speed` | `speed` |
| Définir le sprite | `set_sprite` | `sprite`, `subimage`, `speed` |
| Démarrer l'animation | `start_animation` | — |
| Arrêter l'animation | `stop_animation` | — |
| Tester le nombre d'instances | `test_instance_count` | `object`, `number`, `operation` |

### Score

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Effacer le tableau des scores | `clear_highscore` | — |
| Dessiner la barre de santé | `draw_health_bar` | `x1`, `y1`, `x2`, `y2`, `back_color`, `bar_color` |
| Dessiner les vies | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Dessiner le score | `draw_score` | `x`, `y`, `caption`, `relative` |
| Définir la santé | `set_health` | `value`, `relative` |
| Définir les vies | `set_lives` | `value`, `relative` |
| Définir le score | `set_score` | `value`, `relative` |
| Afficher le tableau des scores | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Tester la santé | `test_health` | `operation`, `value` |
| Tester les vies | `test_lives` | `value`, `operation` |
| Tester le score | `test_score` | `value`, `operation` |

### Minuterie

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Mettre la frise en pause | `pause_timeline` | — |
| Régler une alarme | `set_alarm` | `alarm_number`, `steps` |
| Définir la frise chronologique | `set_timeline` | `timeline` |
| Définir la position dans la frise | `set_timeline_position` | `position`, `relative` |
| Définir la vitesse de la frise | `set_timeline_speed` | `speed` |
| Attendre | `sleep` | `milliseconds` |
| Démarrer la frise | `start_timeline` | — |
| Arrêter la frise | `stop_timeline` | — |

### Salle

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Vérifier la salle | `check_room` | `room`, `not_flag` |
| Terminer le jeu | `game_end` | — |
| Aller à la salle | `goto_room` | `room`, `transition` |
| Si salle suivante existe | `if_next_room_exists` | `then_actions`, `else_actions` |
| Si salle précédente existe | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Salle suivante | `next_room` | — |
| Salle précédente | `previous_room` | — |
| Redémarrer la salle | `restart_room` | — |
| Définir l'arrière-plan | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |
| Définir la couleur d'arrière-plan | `set_background_color` | `color`, `show_color` |
| Définir le titre de la salle | `set_room_caption` | `caption` |
| Définir la persistance de la salle | `set_room_persistent` | `persistent` |
| Définir la vitesse de la salle | `set_room_speed` | `speed` |

### Audio

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Vérifier si un son joue | `check_sound` | `sound`, `not_flag` |
| Jouer une musique | `play_music` | `music`, `loop`, `volume` |
| Jouer un son | `play_sound` | `sound`, `volume` |
| Définir le volume | `set_volume` | `volume` |
| Arrêter la musique | `stop_music` | — |
| Arrêter un son | `stop_sound` | `sound` |

### Jeu

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Dessiner une flèche | `draw_arrow` | `x1`, `y1`, `x2`, `y2`, `tip_size` |
| Dessiner un arrière-plan | `draw_background` | `background`, `x`, `y`, `tiled` |
| Dessiner une ellipse | `draw_ellipse` | `x1`, `y1`, `x2`, `y2`, `filled` |
| Dessiner une ligne | `draw_line` | `x1`, `y1`, `x2`, `y2` |
| Dessiner du texte mis à l'échelle | `draw_scaled_text` | `text`, `x`, `y`, `xscale`, `yscale` |
| Dessiner un sprite | `draw_sprite` | `sprite`, `x`, `y`, `subimage` |
| Dessiner du texte | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Dessiner une variable | `draw_variable` | `x`, `y`, `variable` |
| Remplir l'écran d'une couleur | `fill_color` | `color` |
| Charger la partie | `load_game` | `filename` |
| Ouvrir une page web | `open_webpage` | `url` |
| Redémarrer le jeu | `restart_game` | — |
| Sauvegarder la partie | `save_game` | `filename` |
| Définir la couleur | `set_color` | `color`, `alpha` |
| Définir la couleur de dessin | `set_draw_color` | `color` |
| Définir la police de dessin | `set_draw_font` | `font`, `halign`, `valign` |
| Définir le titre de la fenêtre | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Afficher les infos du jeu | `show_info` | — |
| Afficher un message | `show_message` | `message` |
| Afficher une vidéo | `show_video` | `filename`, `fullscreen` |
| Écran d'accueil : afficher une image | `splash_show_image` | `image` |
| Écran d'accueil : afficher un texte | `splash_show_text` | `text` |

### Contrôle

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Vérifier si vide | `check_empty` | `x`, `y`, `relative`, `objects` |
| Commentaire | `comment` | `text` |
| Sinon | `else_action` | — |
| Fin de bloc | `end_block` | — |
| Exécuter du code | `execute_code` | `code` |
| Exécuter un script | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Quitter l'événement | `exit_event` | — |
| Si poussée possible | `if_can_push` | `direction`, `object_type`, `then_action`, `else_action` |
| Si collision | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Si collision à | `if_collision_at` | `x`, `y`, `object_type`, `then_actions`, `else_actions` |
| Si l'objet existe | `if_object_exists` | `object`, `not_flag` |
| Répéter | `repeat` | `times`, `actions` |
| Début de bloc | `start_block` | — |
| Tester la chance | `test_chance` | `sides` |
| Tester une expression | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Poser une question | `test_question` | `question` |
| Tester une variable | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Vues

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Activer les vues | `enable_views` | `enable` |
| Définir une vue | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### Particules

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Émettre une salve de particules | `burst_particles` | `particle_type`, `number` |
| Effacer les particules | `clear_particles` | — |
| Créer un émetteur | `create_emitter` | `x`, `y`, `width`, `height`, `shape` |
| Créer un système de particules | `create_particle_system` | `depth` |
| Créer un type de particule | `create_particle_type` | `sprite`, `size_min`, `size_max`, `size_increase`, `color`, `alpha`, `speed_min`, `speed_max`, `direction_min`, `direction_max`, `life_min`, `life_max` |
| Supprimer l'émetteur | `destroy_emitter` | — |
| Supprimer le système de particules | `destroy_particle_system` | — |
| Émettre des particules en continu | `stream_particles` | `particle_type`, `number` |

---

## Voir aussi

- [Guide des Préréglages](Preset-Guide_fr) — ce que sont les préréglages et comment en changer
- [Référence des Événements](Event-Reference_fr) — description complète de chaque événement
- [Référence Complète des Actions](Full-Action-Reference_fr) — détails complets des paramètres de chaque action
- [Préréglage Débutant](Beginner-Preset_fr) — le niveau en dessous de celui-ci
