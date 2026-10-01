# Préréglage Débutant

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Préréglage Intermédiaire](Intermediate-Preset_fr)*

> **Généré automatiquement** à partir de `get_beginner()` dans `config/blockly_config.py` par `tools/gen_preset_docs.py` — ne pas modifier à la main ; relancez le générateur après avoir changé le préréglage.

> **Ce que ce préréglage restreint réellement :** ce préréglage filtre À LA FOIS la palette de blocs visuels Blockly ET les menus « Ajouter un événement »/« Ajouter une action » du panneau structuré — quel que soit l'éditeur utilisé, seuls les événements/actions listés ci-dessous apparaissent. Le préréglage d'un *projet* se règle de deux façons : **`Préférences > Édition de l'IDE`** choisit le préréglage par défaut des *nouveaux* projets (édition Débutant -> ce préréglage ; les projets existants ne sont jamais modifiés en changeant l'édition), et **`Outils > Configurer les blocs d'action...`** change le préréglage du projet *actuellement ouvert* à tout moment. L'édition par défaut de l'IDE est Débutant, donc les nouveaux projets d'une installation fraîche démarrent exactement sur cette liste. Cette liste ne couvre pas les actions d'[extension](Extensions_fr) (Vue 3D, Réseau, …) : les actions d'une extension apparaissent dans tous les préréglages, y compris celui-ci, une fois qu'elle est active pour le projet — voir la section « Quelles actions d'extension apparaissent dans la palette » de la page [Extensions](Extensions_fr).

## Aperçu

Ce préréglage active **19** types d'événements et **54** types d'actions.

---

## Événements

| Événement | Nom du bloc | Catégorie | Description |
|-------|------------|----------|-------------|
| Create | `create` | Objet | Exécuté une fois quand l'objet est créé pour la première fois |
| Step | `step` | Objet | Exécuté à chaque image (utilisez-le pour des vérifications continues) |
| Keyboard (held) | `keyboard` | Entrée | Exécuté en continu tant qu'une touche est maintenue (pour un mouvement fluide) |
| Keyboard <No Key> | `keyboard_no_key` | Entrée | Exécuté quand aucune touche du clavier n'est actuellement enfoncée |
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
| Sauter à la position de départ | `jump_to_start` | — |
| Déplacer jusqu'au contact | `move_to_contact` | `direction`, `max_distance`, `object` |
| Inverser horizontalement | `reverse_horizontal` | — |
| Inverser verticalement | `reverse_vertical` | — |
| Définir direction et vitesse | `set_direction_speed` | `direction`, `speed` |
| Définir la gravité | `set_gravity` | `direction`, `gravity` |
| Définir la vitesse horizontale | `set_hspeed` | `speed` |
| Définir la vitesse verticale | `set_vspeed` | `speed` |
| Commencer à bouger (direction) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Arrêter le mouvement | `stop_movement` | — |

### Grille

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Tester l'alignement sur la grille | `test_alignment` | `hsnap`, `vsnap` |

### Instance

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Changer d'instance | `change_instance` | `object`, `perform_events` |
| Créer une instance | `create_instance` | `object`, `x`, `y`, `relative` |
| Détruire une instance | `destroy_instance` | — |
| Détruire à une position | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Tester le nombre d'instances | `test_instance_count` | `object`, `number`, `operation` |

### Score

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Dessiner les vies | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Dessiner le score | `draw_score` | `x`, `y`, `caption`, `relative` |
| Définir les vies | `set_lives` | `value`, `relative` |
| Définir le score | `set_score` | `value`, `relative` |
| Afficher le tableau des scores | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |

### Minuterie

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Régler une alarme | `set_alarm` | `alarm_number`, `steps` |
| Attendre | `sleep` | `milliseconds` |

### Salle

| Action | Nom du bloc | Paramètres |
|--------|------------|------------|
| Terminer le jeu | `game_end` | — |
| Si salle suivante existe | `if_next_room_exists` | `then_actions`, `else_actions` |
| Si salle précédente existe | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Redémarrer la salle | `restart_room` | — |
| Définir l'arrière-plan | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |

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
| Dessiner du texte | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Redémarrer le jeu | `restart_game` | — |
| Définir la couleur de dessin | `set_draw_color` | `color` |
| Définir le titre de la fenêtre | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Afficher un message | `show_message` | `message` |

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
| Si collision | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Si l'objet existe | `if_object_exists` | `object`, `not_flag` |
| Début de bloc | `start_block` | — |
| Tester la chance | `test_chance` | `sides` |
| Tester une expression | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Tester une variable | `test_variable` | `variable`, `value`, `scope`, `operation` |

---

## Voir aussi

- [Guide des Préréglages](Preset-Guide_fr) — ce que sont les préréglages et comment en changer
- [Référence des Événements](Event-Reference_fr) — description complète de chaque événement
- [Référence Complète des Actions](Full-Action-Reference_fr) — détails complets des paramètres de chaque action
- [Préréglage Intermédiaire](Intermediate-Preset_fr) — le niveau supérieur
