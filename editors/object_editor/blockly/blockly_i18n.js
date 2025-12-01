/**
 * PyGameMaker Blockly Internationalization
 * Translations for all custom blocks
 * Based on Scratch and Blockly standard translations
 */

// Block text translations
const BLOCK_MESSAGES = {
    'fr': {
        // Event blocks
        'event_create': 'Quand créé',
        'event_create_tooltip': "S'exécute quand l'objet est créé",
        'event_step': 'À chaque étape',
        'event_step_tooltip': "S'exécute à chaque image",
        'event_draw': 'Quand dessiner',
        'event_draw_tooltip': "S'exécute pendant la phase de dessin",
        'event_destroy': 'Quand détruit',
        'event_destroy_tooltip': "S'exécute quand l'objet est détruit",
        'event_keyboard': 'Quand touche %1 pressée',
        'event_keyboard_tooltip': 'Détecte quand une touche est pressée',
        'event_keyboard_nokey': 'Clavier: Aucune touche',
        'event_keyboard_nokey_tooltip': "S'exécute quand aucune touche n'est pressée",
        'event_keyboard_anykey': "Clavier: N'importe quelle touche",
        'event_keyboard_anykey_tooltip': "S'exécute quand une touche est pressée",
        'event_keyboard_held_prefix': 'Clavier:',
        'event_keyboard_held_suffix': '(maintenue)',
        'event_keyboard_held_tooltip': "S'exécute en continu tant que la touche est maintenue",
        'event_keyboard_press_prefix': 'Touche pressée:',
        'event_keyboard_press_tooltip': "S'exécute une fois quand la touche est pressée",
        'event_keyboard_release_prefix': 'Touche relâchée:',
        'event_keyboard_release_tooltip': "S'exécute une fois quand la touche est relâchée",
        'event_mouse_prefix': 'Quand souris',
        'event_mouse_tooltip': "S'exécute lors d'événements souris",
        'event_collision_prefix': 'Quand collision avec',
        'event_collision_tooltip': "S'exécute lors d'une collision avec un autre objet",
        'event_alarm_prefix': 'Quand alarme',
        'event_alarm_suffix': 'se déclenche',
        'event_alarm_tooltip': "S'exécute quand l'alarme atteint zéro",

        // Movement blocks
        'move_set_hspeed_prefix': 'définir vitesse horizontale à',
        'move_set_hspeed': 'définir vitesse horizontale à %1',
        'move_set_hspeed_tooltip': 'Définir la vitesse horizontale (X)',
        'move_set_vspeed_prefix': 'définir vitesse verticale à',
        'move_set_vspeed': 'définir vitesse verticale à %1',
        'move_set_vspeed_tooltip': 'Définir la vitesse verticale (Y)',
        'move_stop': 'arrêter le mouvement',
        'move_stop_tooltip': 'Arrête tous les mouvements',
        'move_direction_prefix': 'Déplacer',
        'move_direction_suffix': 'à vitesse',
        'move_direction': 'déplacer en direction %1 vitesse %2',
        'move_direction_tooltip': 'Déplacer dans une direction (4 directions)',
        'move_towards_prefix': 'Déplacer vers x:',
        'move_towards_y': 'y:',
        'move_towards_speed': 'à vitesse:',
        'move_towards': 'déplacer vers x: %1 y: %2',
        'move_towards_tooltip': 'Déplacer vers un point',
        'move_snap_to_grid_prefix': 'Aligner à la grille taille',
        'move_snap_to_grid': 'aligner à la grille %1',
        'move_snap_to_grid_tooltip': 'Aligne la position à la grille',
        'move_jump_to_prefix': 'Sauter à x:',
        'move_jump_to_y': 'y:',
        'move_jump_to': 'sauter à x: %1 y: %2',
        'move_jump_to_tooltip': 'Téléportation instantanée',
        'grid_stop_if_no_keys_prefix': 'Arrêter si aucune touche (grille',
        'grid_stop_if_no_keys_suffix': ')',
        'grid_stop_if_no_keys': 'si aucune touche arrêter (grille %1)',
        'grid_stop_if_no_keys_tooltip': 'Arrête le mouvement sur grille si aucune touche',
        'grid_check_keys_and_move_prefix': 'Vérifier touches et déplacer (grille',
        'grid_check_keys_and_move_middle': ', vitesse',
        'grid_check_keys_and_move_suffix': ')',
        'grid_check_keys_and_move': 'vérifier touches et déplacer (grille %1 vitesse %2)',
        'grid_check_keys_and_move_tooltip': 'Vérifie les touches et déplace sur grille',
        'grid_if_on_grid_prefix': 'Si sur grille (taille',
        'grid_if_on_grid_suffix': ')',
        'grid_if_on_grid_do': 'faire',
        'grid_if_on_grid': 'si sur grille %1',
        'grid_if_on_grid_tooltip': 'Exécute si aligné sur la grille',
        'set_gravity_prefix': 'Définir direction gravité:',
        'set_gravity_strength': 'force:',
        'set_gravity': 'définir gravité à %1',
        'set_gravity_tooltip': 'Applique une force de gravité',
        'set_friction_prefix': 'Définir friction à',
        'set_friction': 'définir friction à %1',
        'set_friction_tooltip': 'Applique de la friction',
        'reverse_horizontal': 'Inverser mouvement horizontal',
        'reverse_horizontal_tooltip': 'Inverse la direction horizontale',
        'reverse_vertical': 'Inverser mouvement vertical',
        'reverse_vertical_tooltip': 'Inverse la direction verticale',

        // Timing blocks
        'set_alarm_prefix': 'Définir alarme',
        'set_alarm_middle': 'à',
        'set_alarm_suffix': 'étapes',
        'set_alarm': 'définir alarme %1 à %2',
        'set_alarm_tooltip': 'Définit une alarme (0-11)',

        // Drawing blocks
        'draw_text_prefix': 'Dessiner texte',
        'draw_text_x': 'à x:',
        'draw_text_y': 'y:',
        'draw_text': 'dessiner texte %1 à x: %2 y: %3',
        'draw_text_tooltip': 'Affiche du texte',
        'draw_rectangle_prefix': 'Dessiner rectangle à x:',
        'draw_rectangle_y': 'y:',
        'draw_rectangle_width': 'largeur:',
        'draw_rectangle_height': 'hauteur:',
        'draw_rectangle_color': 'couleur:',
        'draw_rectangle': 'dessiner rectangle x: %1 y: %2 largeur: %3 hauteur: %4 couleur: %5',
        'draw_rectangle_tooltip': 'Dessine un rectangle plein',
        'draw_circle_prefix': 'Dessiner cercle à x:',
        'draw_circle_y': 'y:',
        'draw_circle_radius': 'rayon:',
        'draw_circle_color': 'couleur:',
        'draw_circle': 'dessiner cercle x: %1 y: %2 rayon: %3 couleur: %4',
        'draw_circle_tooltip': 'Dessine un cercle plein',
        'set_sprite_prefix': 'Définir sprite à',
        'set_sprite': 'définir sprite à %1',
        'set_sprite_tooltip': "Change l'image du sprite",
        'set_alpha_prefix': 'Définir transparence à',
        'set_alpha_suffix': '(0-1)',
        'set_alpha': 'définir transparence à %1',
        'set_alpha_tooltip': 'Définit la transparence (0-1)',

        // Score/Lives/Health blocks
        'score_set_prefix': 'Définir score à',
        'score_set': 'définir score à %1',
        'score_set_tooltip': 'Définit la valeur du score',
        'score_add_prefix': 'Ajouter au score',
        'score_add': 'ajouter %1 au score',
        'score_add_tooltip': 'Change le score',
        'lives_set_prefix': 'Définir vies à',
        'lives_set': 'définir vies à %1',
        'lives_set_tooltip': 'Définit le nombre de vies',
        'lives_add_prefix': 'Ajouter aux vies',
        'lives_add': 'ajouter %1 aux vies',
        'lives_add_tooltip': 'Change les vies',
        'health_set_prefix': 'Définir santé à',
        'health_set': 'définir santé à %1',
        'health_set_tooltip': 'Définit la valeur de santé',
        'health_add_prefix': 'Ajouter à la santé',
        'health_add': 'ajouter %1 à la santé',
        'health_add_tooltip': 'Change la santé',
        'draw_score_prefix': 'Afficher score à x:',
        'draw_score_y': 'y:',
        'draw_score': 'afficher score à x: %1 y: %2',
        'draw_score_tooltip': 'Affiche le texte du score',
        'draw_lives_prefix': 'Afficher vies à x:',
        'draw_lives_y': 'y:',
        'draw_lives': 'afficher vies à x: %1 y: %2 sprite: %3',
        'draw_lives_tooltip': 'Affiche les icônes des vies',
        'draw_health_bar_prefix': 'Afficher barre de santé à x:',
        'draw_health_bar_y': 'y:',
        'draw_health_bar_width': 'largeur:',
        'draw_health_bar': 'afficher barre de santé x: %1 y: %2 largeur: %3 hauteur: %4',
        'draw_health_bar_tooltip': 'Affiche une barre de santé',

        // Instance blocks
        'instance_destroy': 'Détruire cette instance',
        'instance_destroy_tooltip': 'Détruit cet objet',
        'instance_destroy_other': 'Détruire autre instance',
        'instance_destroy_other_tooltip': "Détruit l'objet en collision",
        'instance_create_prefix': 'Créer',
        'instance_create_x': 'à x:',
        'instance_create_y': 'y:',
        'instance_create': 'créer instance de %1 à x: %2 y: %3',
        'instance_create_tooltip': 'Crée un nouvel objet',

        // Room blocks (using "Niveau" instead of "Salle")
        'room_goto_next': 'Aller au niveau suivant',
        'room_goto_next_tooltip': 'Va au niveau suivant',
        'room_restart': 'Redémarrer le niveau',
        'room_restart_tooltip': 'Redémarre le niveau actuel',
        'room_goto_prefix': 'Aller au niveau',
        'room_goto': 'aller au niveau %1',
        'room_goto_tooltip': 'Va à un niveau spécifique',

        // Value blocks
        'value_x': 'position x',
        'value_x_tooltip': 'Coordonnée X',
        'value_y': 'position y',
        'value_y_tooltip': 'Coordonnée Y',
        'value_hspeed': 'vitesse horizontale',
        'value_hspeed_tooltip': 'Vitesse X',
        'value_vspeed': 'vitesse verticale',
        'value_vspeed_tooltip': 'Vitesse Y',
        'value_score': 'score',
        'value_score_tooltip': 'Valeur du score',
        'value_lives': 'vies',
        'value_lives_tooltip': 'Nombre de vies',
        'value_health': 'santé',
        'value_health_tooltip': 'Valeur de santé',
        'value_mouse_x': 'souris x',
        'value_mouse_x_tooltip': 'Position X de la souris',
        'value_mouse_y': 'souris y',
        'value_mouse_y_tooltip': 'Position Y de la souris',

        // Sound blocks
        'sound_play_prefix': 'Jouer son',
        'sound_play': 'jouer son %1',
        'sound_play_tooltip': 'Joue un effet sonore',
        'music_play_prefix': 'Jouer musique',
        'music_play': 'jouer musique %1',
        'music_play_tooltip': 'Joue une musique de fond',
        'music_stop': 'Arrêter musique',
        'music_stop_tooltip': 'Arrête la musique',

        // Output blocks
        'output_message_prefix': 'Afficher message',
        'output_message': 'afficher message %1',
        'output_message_tooltip': 'Affiche une boîte de dialogue',

        // Key names
        'key_right': 'Flèche droite',
        'key_left': 'Flèche gauche',
        'key_up': 'Flèche haut',
        'key_down': 'Flèche bas',
        'key_space': 'Espace',
        'key_enter': 'Entrée',
        'key_escape': 'Échap',

        // Common terms
        'then': 'alors',
        'do': 'faire',
        'speed': 'vitesse',
        'direction': 'direction',
        'color': 'couleur',
        'grid_size': 'taille grille',

        // Math blocks
        'math_square_root': 'racine carrée',
        'math_absolute': 'valeur absolue',
        'math_random_int': 'entier aléatoire de %1 à %2',
        'math_round': 'arrondir',
        'math_floor': 'arrondir vers le bas',
        'math_ceiling': 'arrondir vers le haut',
        'math_sin': 'sinus',
        'math_cos': 'cosinus',
        'math_tan': 'tangente',

        // Logic blocks
        'logic_and': 'et',
        'logic_or': 'ou',
        'logic_not': 'non',
        'logic_true': 'vrai',
        'logic_false': 'faux',
        'logic_if': 'si',
        'logic_else': 'sinon',
        'logic_then': 'alors',
    },
    'de': {
        // Event blocks
        'event_create': 'Wenn erstellt',
        'event_create_tooltip': 'Wird ausgeführt, wenn das Objekt erstellt wird',
        'event_step': 'Jeden Schritt',
        'event_step_tooltip': 'Wird jeden Frame ausgeführt',
        'event_draw': 'Beim Zeichnen',
        'event_draw_tooltip': 'Wird während der Zeichenphase ausgeführt',
        'event_destroy': 'Wenn zerstört',
        'event_destroy_tooltip': 'Wird ausgeführt, wenn das Objekt zerstört wird',
        'event_keyboard': 'Wenn Taste %1 gedrückt',
        'event_keyboard_tooltip': 'Erkennt, wenn eine Taste gedrückt wird',
        'event_keyboard_nokey': 'Tastatur: Keine Taste',
        'event_keyboard_nokey_tooltip': 'Wird ausgeführt, wenn keine Taste gedrückt wird',
        'event_keyboard_anykey': 'Tastatur: Beliebige Taste',
        'event_keyboard_anykey_tooltip': 'Wird ausgeführt, wenn eine Taste gedrückt wird',
        'event_keyboard_held_prefix': 'Tastatur:',
        'event_keyboard_held_suffix': '(gehalten)',
        'event_keyboard_held_tooltip': 'Wird kontinuierlich ausgeführt, während die Taste gehalten wird',
        'event_keyboard_press_prefix': 'Taste gedrückt:',
        'event_keyboard_press_tooltip': 'Wird einmal ausgeführt, wenn die Taste gedrückt wird',
        'event_keyboard_release_prefix': 'Taste losgelassen:',
        'event_keyboard_release_tooltip': 'Wird einmal ausgeführt, wenn die Taste losgelassen wird',
        'event_mouse_prefix': 'Wenn Maus',
        'event_mouse_tooltip': 'Wird bei Mausereignissen ausgeführt',
        'event_collision_prefix': 'Wenn Kollision mit',
        'event_collision_tooltip': 'Wird bei Kollision mit einem anderen Objekt ausgeführt',
        'event_alarm_prefix': 'Wenn Alarm',
        'event_alarm_suffix': 'auslöst',
        'event_alarm_tooltip': 'Wird ausgeführt, wenn der Alarm Null erreicht',

        // Movement blocks
        'move_set_hspeed_prefix': 'setze horizontale Geschwindigkeit auf',
        'move_set_hspeed': 'setze horizontale Geschwindigkeit auf %1',
        'move_set_hspeed_tooltip': 'Setzt die horizontale Geschwindigkeit (X)',
        'move_set_vspeed_prefix': 'setze vertikale Geschwindigkeit auf',
        'move_set_vspeed': 'setze vertikale Geschwindigkeit auf %1',
        'move_set_vspeed_tooltip': 'Setzt die vertikale Geschwindigkeit (Y)',
        'move_stop': 'Bewegung stoppen',
        'move_stop_tooltip': 'Stoppt alle Bewegung',
        'move_direction_prefix': 'Bewege',
        'move_direction_suffix': 'mit Geschwindigkeit',
        'move_direction': 'bewege in Richtung %1 Geschwindigkeit %2',
        'move_direction_tooltip': 'Bewege in eine Richtung (4 Richtungen)',
        'move_towards_prefix': 'Bewege zu x:',
        'move_towards_y': 'y:',
        'move_towards_speed': 'mit Geschwindigkeit:',
        'move_towards': 'bewege zu x: %1 y: %2',
        'move_towards_tooltip': 'Bewege zu einem Punkt',
        'move_snap_to_grid_prefix': 'Am Raster ausrichten Größe',
        'move_snap_to_grid': 'am Raster ausrichten %1',
        'move_snap_to_grid_tooltip': 'Position am Raster ausrichten',
        'move_jump_to_prefix': 'Springe zu x:',
        'move_jump_to_y': 'y:',
        'move_jump_to': 'springe zu x: %1 y: %2',
        'move_jump_to_tooltip': 'Sofortige Bewegung',
        'grid_stop_if_no_keys_prefix': 'Stoppen wenn keine Tasten (Raster',
        'grid_stop_if_no_keys_suffix': ')',
        'grid_stop_if_no_keys': 'wenn keine Tasten stoppen (Raster %1)',
        'grid_stop_if_no_keys_tooltip': 'Stoppt Bewegung, wenn keine Pfeiltasten gedrückt werden (rasterbasiért)',
        'grid_check_keys_and_move_prefix': 'Tasten prüfen & bewegen (Raster',
        'grid_check_keys_and_move_middle': ', Geschwindigkeit',
        'grid_check_keys_and_move_suffix': ')',
        'grid_check_keys_and_move': 'prüfe Tasten und bewege (Raster %1 Geschwindigkeit %2)',
        'grid_check_keys_and_move_tooltip': 'Prüft Pfeiltasten und bewegt in Rasterschritten',
        'grid_if_on_grid_prefix': 'Wenn auf Raster (Größe',
        'grid_if_on_grid_suffix': ')',
        'grid_if_on_grid_do': 'tue',
        'grid_if_on_grid': 'wenn auf Raster %1',
        'grid_if_on_grid_tooltip': 'Führt Aktionen nur aus, wenn am Raster ausgerichtet',
        'set_gravity_prefix': 'Setze Schwerkraft Richtung:',
        'set_gravity_strength': 'Stärke:',
        'set_gravity': 'setze Schwerkraft auf %1',
        'set_gravity_tooltip': 'Wendet Schwerkraft auf diese Instanz an',
        'set_friction_prefix': 'Setze Reibung auf',
        'set_friction': 'setze Reibung auf %1',
        'set_friction_tooltip': 'Setzt Bewegungsreibung',
        'reverse_horizontal': 'Horizontale Bewegung umkehren',
        'reverse_horizontal_tooltip': 'Kehrt die horizontale Richtung um',
        'reverse_vertical': 'Vertikale Bewegung umkehren',
        'reverse_vertical_tooltip': 'Kehrt die vertikale Richtung um',

        // Timing blocks
        'set_alarm_prefix': 'Setze Alarm',
        'set_alarm_middle': 'auf',
        'set_alarm_suffix': 'Schritte',
        'set_alarm': 'setze Alarm %1 auf %2',
        'set_alarm_tooltip': 'Setzt einen Alarm (0-11)',

        // Drawing blocks
        'draw_text_prefix': 'Zeichne Text',
        'draw_text_x': 'bei x:',
        'draw_text_y': 'y:',
        'draw_text': 'zeichne Text %1 bei x: %2 y: %3',
        'draw_text_tooltip': 'Zeigt Text an',
        'draw_rectangle_prefix': 'Zeichne Rechteck bei x:',
        'draw_rectangle_y': 'y:',
        'draw_rectangle_width': 'Breite:',
        'draw_rectangle_height': 'Höhe:',
        'draw_rectangle_color': 'Farbe:',
        'draw_rectangle': 'zeichne Rechteck x: %1 y: %2 Breite: %3 Höhe: %4 Farbe: %5',
        'draw_rectangle_tooltip': 'Zeichnet ein gefülltes Rechteck',
        'draw_circle_prefix': 'Zeichne Kreis bei x:',
        'draw_circle_y': 'y:',
        'draw_circle_radius': 'Radius:',
        'draw_circle_color': 'Farbe:',
        'draw_circle': 'zeichne Kreis x: %1 y: %2 Radius: %3 Farbe: %4',
        'draw_circle_tooltip': 'Zeichnet einen gefüllten Kreis',
        'set_sprite_prefix': 'Setze Sprite auf',
        'set_sprite': 'setze Sprite auf %1',
        'set_sprite_tooltip': 'Ändert das Sprite-Bild',
        'set_alpha_prefix': 'Setze Transparenz auf',
        'set_alpha_suffix': '(0-1)',
        'set_alpha': 'setze Transparenz auf %1',
        'set_alpha_tooltip': 'Setzt Sprite-Transparenz (0=unsichtbar, 1=solide)',

        // Score/Lives/Health blocks
        'score_set_prefix': 'Setze Punkte auf',
        'score_set': 'setze Punkte auf %1',
        'score_set_tooltip': 'Setzt den Punktestand',
        'score_add_prefix': 'Zu Punkten hinzufügen',
        'score_add': 'füge %1 zu Punkten hinzu',
        'score_add_tooltip': 'Zu den Punkten hinzufügen',
        'lives_set_prefix': 'Setze Leben auf',
        'lives_set': 'setze Leben auf %1',
        'lives_set_tooltip': 'Setzt die Anzahl der Leben',
        'lives_add_prefix': 'Zu Leben hinzufügen',
        'lives_add': 'füge %1 zu Leben hinzu',
        'lives_add_tooltip': 'Zu den Leben hinzufügen (negativ zum Abziehen)',
        'health_set_prefix': 'Setze Gesundheit auf',
        'health_set': 'setze Gesundheit auf %1',
        'health_set_tooltip': 'Setzt den Gesundheitswert (0-100)',
        'health_add_prefix': 'Zu Gesundheit hinzufügen',
        'health_add': 'füge %1 zu Gesundheit hinzu',
        'health_add_tooltip': 'Zu Gesundheit hinzufügen (negativ für Schaden)',
        'draw_score_prefix': 'Zeige Punkte bei x:',
        'draw_score_y': 'y:',
        'draw_score': 'zeige Punkte bei x: %1 y: %2',
        'draw_score_tooltip': 'Zeigt den Punktestand auf dem Bildschirm',
        'draw_lives_prefix': 'Zeige Leben bei x:',
        'draw_lives_y': 'y:',
        'draw_lives': 'zeige Leben bei x: %1 y: %2 Sprite: %3',
        'draw_lives_tooltip': 'Zeigt Leben auf dem Bildschirm',
        'draw_health_bar_prefix': 'Zeige Gesundheitsbalken bei x:',
        'draw_health_bar_y': 'y:',
        'draw_health_bar_width': 'Breite:',
        'draw_health_bar': 'zeige Gesundheitsbalken x: %1 y: %2 Breite: %3 Höhe: %4',
        'draw_health_bar_tooltip': 'Zeigt einen Gesundheitsbalken',

        // Instance blocks
        'instance_destroy': 'Zerstöre diese Instanz',
        'instance_destroy_tooltip': 'Zerstört dieses Objekt',
        'instance_destroy_other': 'Zerstöre andere Instanz',
        'instance_destroy_other_tooltip': 'Zerstört das kollidierende Objekt',
        'instance_create_prefix': 'Erstelle',
        'instance_create_x': 'bei x:',
        'instance_create_y': 'y:',
        'instance_create': 'erstelle Instanz von %1 bei x: %2 y: %3',
        'instance_create_tooltip': 'Erstellt ein neues Objekt',

        // Room blocks
        'room_goto_next': 'Gehe zum nächsten Raum',
        'room_goto_next_tooltip': 'Geht zum nächsten Raum',
        'room_restart': 'Raum neu starten',
        'room_restart_tooltip': 'Startet den aktuellen Raum neu',
        'room_goto_prefix': 'Gehe zu Raum',
        'room_goto': 'gehe zu Raum %1',
        'room_goto_tooltip': 'Geht zu einem bestimmten Raum',

        // Value blocks
        'value_x': 'x Position',
        'value_x_tooltip': 'X-Koordinate',
        'value_y': 'y Position',
        'value_y_tooltip': 'Y-Koordinate',
        'value_hspeed': 'horizontale Geschwindigkeit',
        'value_hspeed_tooltip': 'X-Geschwindigkeit',
        'value_vspeed': 'vertikale Geschwindigkeit',
        'value_vspeed_tooltip': 'Y-Geschwindigkeit',
        'value_score': 'Punkte',
        'value_score_tooltip': 'Punktestand',
        'value_lives': 'Leben',
        'value_lives_tooltip': 'Anzahl Leben',
        'value_health': 'Gesundheit',
        'value_health_tooltip': 'Gesundheitswert',
        'value_mouse_x': 'Maus x',
        'value_mouse_x_tooltip': 'Maus X-Position',
        'value_mouse_y': 'Maus y',
        'value_mouse_y_tooltip': 'Maus Y-Position',

        // Sound blocks
        'sound_play_prefix': 'Spiele Sound',
        'sound_play': 'spiele Sound %1',
        'sound_play_tooltip': 'Spielt einen Soundeffekt',
        'music_play_prefix': 'Spiele Musik',
        'music_play': 'spiele Musik %1',
        'music_play_tooltip': 'Spielt Hintergrundmusik',
        'music_stop': 'Musik stoppen',
        'music_stop_tooltip': 'Stoppt Hintergrundmusik',

        // Output blocks
        'output_message_prefix': 'Zeige Nachricht',
        'output_message': 'zeige Nachricht %1',
        'output_message_tooltip': 'Zeigt eine Nachricht an',

        // Key names
        'key_right': 'Pfeil rechts',
        'key_left': 'Pfeil links',
        'key_up': 'Pfeil oben',
        'key_down': 'Pfeil unten',
        'key_space': 'Leertaste',
        'key_enter': 'Eingabe',
        'key_escape': 'Escape',

        // Common terms
        'then': 'dann',
        'do': 'tue',
        'speed': 'Geschwindigkeit',
        'direction': 'Richtung',
        'color': 'Farbe',
        'grid_size': 'Rastergröße',
    },
    'it': {
        // Event blocks
        'event_create': 'Quando creato',
        'event_create_tooltip': "Viene eseguito quando l'oggetto viene creato",
        'event_step': 'Ogni passo',
        'event_step_tooltip': 'Viene eseguito ogni frame',
        'event_draw': 'Quando disegnare',
        'event_draw_tooltip': 'Viene eseguito durante la fase di disegno',
        'event_destroy': 'Quando distrutto',
        'event_destroy_tooltip': "Viene eseguito quando l'oggetto viene distrutto",
        'event_keyboard': 'Quando tasto %1 premuto',
        'event_keyboard_tooltip': 'Rileva quando un tasto viene premuto',
        'event_keyboard_nokey': 'Tastiera: Nessun tasto',
        'event_keyboard_nokey_tooltip': 'Viene eseguito quando nessun tasto è premuto',
        'event_keyboard_anykey': 'Tastiera: Qualsiasi tasto',
        'event_keyboard_anykey_tooltip': 'Viene eseguito quando un tasto è premuto',
        'event_keyboard_held_prefix': 'Tastiera:',
        'event_keyboard_held_suffix': '(tenuto)',
        'event_keyboard_held_tooltip': 'Viene eseguito continuamente mentre il tasto è tenuto premuto',
        'event_keyboard_press_prefix': 'Tasto premuto:',
        'event_keyboard_press_tooltip': 'Viene eseguito una volta quando il tasto viene premuto',
        'event_keyboard_release_prefix': 'Tasto rilasciato:',
        'event_keyboard_release_tooltip': 'Viene eseguito una volta quando il tasto viene rilasciato',
        'event_mouse_prefix': 'Quando mouse',
        'event_mouse_tooltip': 'Viene eseguito su eventi del mouse',
        'event_collision_prefix': 'Quando collisione con',
        'event_collision_tooltip': 'Viene eseguito durante una collisione con un altro oggetto',
        'event_alarm_prefix': 'Quando allarme',
        'event_alarm_suffix': 'scatta',
        'event_alarm_tooltip': "Viene eseguito quando l'allarme raggiunge zero",

        // Movement blocks
        'move_set_hspeed_prefix': 'imposta velocità orizzontale a',
        'move_set_hspeed': 'imposta velocità orizzontale a %1',
        'move_set_hspeed_tooltip': 'Imposta la velocità orizzontale (X)',
        'move_set_vspeed_prefix': 'imposta velocità verticale a',
        'move_set_vspeed': 'imposta velocità verticale a %1',
        'move_set_vspeed_tooltip': 'Imposta la velocità verticale (Y)',
        'move_stop': 'ferma movimento',
        'move_stop_tooltip': 'Ferma tutti i movimenti',
        'move_direction_prefix': 'Muovi',
        'move_direction_suffix': 'a velocità',
        'move_direction': 'muovi in direzione %1 velocità %2',
        'move_direction_tooltip': 'Muovi in una direzione (4 direzioni)',
        'move_towards_prefix': 'Muovi verso x:',
        'move_towards_y': 'y:',
        'move_towards_speed': 'a velocità:',
        'move_towards': 'muovi verso x: %1 y: %2',
        'move_towards_tooltip': 'Muovi verso un punto',
        'move_snap_to_grid_prefix': 'Allinea alla griglia dimensione',
        'move_snap_to_grid': 'allinea alla griglia %1',
        'move_snap_to_grid_tooltip': 'Allinea la posizione alla griglia',
        'move_jump_to_prefix': 'Salta a x:',
        'move_jump_to_y': 'y:',
        'move_jump_to': 'salta a x: %1 y: %2',
        'move_jump_to_tooltip': 'Movimento istantaneo',
        'grid_stop_if_no_keys_prefix': 'Ferma se nessun tasto (griglia',
        'grid_stop_if_no_keys_suffix': ')',
        'grid_stop_if_no_keys': 'se nessun tasto ferma (griglia %1)',
        'grid_stop_if_no_keys_tooltip': 'Ferma il movimento quando nessun tasto freccia è premuto (basato su griglia)',
        'grid_check_keys_and_move_prefix': 'Controlla tasti e muovi (griglia',
        'grid_check_keys_and_move_middle': ', velocità',
        'grid_check_keys_and_move_suffix': ')',
        'grid_check_keys_and_move': 'controlla tasti e muovi (griglia %1 velocità %2)',
        'grid_check_keys_and_move_tooltip': 'Controlla i tasti freccia e muove in passi allineati alla griglia',
        'grid_if_on_grid_prefix': 'Se sulla griglia (dimensione',
        'grid_if_on_grid_suffix': ')',
        'grid_if_on_grid_do': 'fai',
        'grid_if_on_grid': 'se sulla griglia %1',
        'grid_if_on_grid_tooltip': 'Esegue azioni solo quando allineato alla griglia',
        'set_gravity_prefix': 'Imposta direzione gravità:',
        'set_gravity_strength': 'forza:',
        'set_gravity': 'imposta gravità a %1',
        'set_gravity_tooltip': 'Applica gravità a questa istanza',
        'set_friction_prefix': 'Imposta attrito a',
        'set_friction': 'imposta attrito a %1',
        'set_friction_tooltip': 'Imposta attrito del movimento',
        'reverse_horizontal': 'Inverti movimento orizzontale',
        'reverse_horizontal_tooltip': 'Inverte la direzione orizzontale',
        'reverse_vertical': 'Inverti movimento verticale',
        'reverse_vertical_tooltip': 'Inverte la direzione verticale',

        // Timing blocks
        'set_alarm_prefix': 'Imposta allarme',
        'set_alarm_middle': 'a',
        'set_alarm_suffix': 'passi',
        'set_alarm': 'imposta allarme %1 a %2',
        'set_alarm_tooltip': 'Imposta un allarme (0-11)',

        // Drawing blocks
        'draw_text_prefix': 'Disegna testo',
        'draw_text_x': 'a x:',
        'draw_text_y': 'y:',
        'draw_text': 'disegna testo %1 a x: %2 y: %3',
        'draw_text_tooltip': 'Visualizza testo',
        'draw_rectangle_prefix': 'Disegna rettangolo a x:',
        'draw_rectangle_y': 'y:',
        'draw_rectangle_width': 'larghezza:',
        'draw_rectangle_height': 'altezza:',
        'draw_rectangle_color': 'colore:',
        'draw_rectangle': 'disegna rettangolo x: %1 y: %2 larghezza: %3 altezza: %4 colore: %5',
        'draw_rectangle_tooltip': 'Disegna un rettangolo pieno',
        'draw_circle_prefix': 'Disegna cerchio a x:',
        'draw_circle_y': 'y:',
        'draw_circle_radius': 'raggio:',
        'draw_circle_color': 'colore:',
        'draw_circle': 'disegna cerchio x: %1 y: %2 raggio: %3 colore: %4',
        'draw_circle_tooltip': 'Disegna un cerchio pieno',
        'set_sprite_prefix': 'Imposta sprite a',
        'set_sprite': 'imposta sprite a %1',
        'set_sprite_tooltip': "Cambia l'immagine dello sprite",
        'set_alpha_prefix': 'Imposta trasparenza a',
        'set_alpha_suffix': '(0-1)',
        'set_alpha': 'imposta trasparenza a %1',
        'set_alpha_tooltip': 'Imposta trasparenza sprite (0=invisibile, 1=solido)',

        // Score/Lives/Health blocks
        'score_set_prefix': 'Imposta punteggio a',
        'score_set': 'imposta punteggio a %1',
        'score_set_tooltip': 'Imposta il valore del punteggio',
        'score_add_prefix': 'Aggiungi al punteggio',
        'score_add': 'aggiungi %1 al punteggio',
        'score_add_tooltip': 'Aggiungi al punteggio',
        'lives_set_prefix': 'Imposta vite a',
        'lives_set': 'imposta vite a %1',
        'lives_set_tooltip': 'Imposta il numero di vite',
        'lives_add_prefix': 'Aggiungi alle vite',
        'lives_add': 'aggiungi %1 alle vite',
        'lives_add_tooltip': 'Aggiungi alle vite (usa negativo per sottrarre)',
        'health_set_prefix': 'Imposta salute a',
        'health_set': 'imposta salute a %1',
        'health_set_tooltip': 'Imposta il valore di salute (0-100)',
        'health_add_prefix': 'Aggiungi alla salute',
        'health_add': 'aggiungi %1 alla salute',
        'health_add_tooltip': 'Aggiungi alla salute (usa negativo per danno)',
        'draw_score_prefix': 'Mostra punteggio a x:',
        'draw_score_y': 'y:',
        'draw_score': 'mostra punteggio a x: %1 y: %2',
        'draw_score_tooltip': 'Mostra il punteggio sullo schermo',
        'draw_lives_prefix': 'Mostra vite a x:',
        'draw_lives_y': 'y:',
        'draw_lives': 'mostra vite a x: %1 y: %2 sprite: %3',
        'draw_lives_tooltip': 'Mostra vite sullo schermo',
        'draw_health_bar_prefix': 'Mostra barra salute a x:',
        'draw_health_bar_y': 'y:',
        'draw_health_bar_width': 'larghezza:',
        'draw_health_bar': 'mostra barra salute x: %1 y: %2 larghezza: %3 altezza: %4',
        'draw_health_bar_tooltip': 'Mostra una barra di salute',

        // Instance blocks
        'instance_destroy': 'Distruggi questa istanza',
        'instance_destroy_tooltip': 'Distrugge questo oggetto',
        'instance_destroy_other': 'Distruggi altra istanza',
        'instance_destroy_other_tooltip': "Distrugge l'oggetto in collisione",
        'instance_create_prefix': 'Crea',
        'instance_create_x': 'a x:',
        'instance_create_y': 'y:',
        'instance_create': 'crea istanza di %1 a x: %2 y: %3',
        'instance_create_tooltip': 'Crea un nuovo oggetto',

        // Room blocks
        'room_goto_next': 'Vai alla stanza successiva',
        'room_goto_next_tooltip': 'Vai alla stanza successiva',
        'room_restart': 'Riavvia stanza',
        'room_restart_tooltip': 'Riavvia la stanza corrente',
        'room_goto_prefix': 'Vai alla stanza',
        'room_goto': 'vai alla stanza %1',
        'room_goto_tooltip': 'Vai a una stanza specifica',

        // Value blocks
        'value_x': 'posizione x',
        'value_x_tooltip': 'Coordinata X',
        'value_y': 'posizione y',
        'value_y_tooltip': 'Coordinata Y',
        'value_hspeed': 'velocità orizzontale',
        'value_hspeed_tooltip': 'Velocità X',
        'value_vspeed': 'velocità verticale',
        'value_vspeed_tooltip': 'Velocità Y',
        'value_score': 'punteggio',
        'value_score_tooltip': 'Valore del punteggio',
        'value_lives': 'vite',
        'value_lives_tooltip': 'Numero di vite',
        'value_health': 'salute',
        'value_health_tooltip': 'Valore di salute',
        'value_mouse_x': 'mouse x',
        'value_mouse_x_tooltip': 'Posizione X del mouse',
        'value_mouse_y': 'mouse y',
        'value_mouse_y_tooltip': 'Posizione Y del mouse',

        // Sound blocks
        'sound_play_prefix': 'Riproduci suono',
        'sound_play': 'riproduci suono %1',
        'sound_play_tooltip': 'Riproduce un effetto sonoro',
        'music_play_prefix': 'Riproduci musica',
        'music_play': 'riproduci musica %1',
        'music_play_tooltip': 'Riproduce musica di sottofondo',
        'music_stop': 'Ferma musica',
        'music_stop_tooltip': 'Ferma la musica',

        // Output blocks
        'output_message_prefix': 'Mostra messaggio',
        'output_message': 'mostra messaggio %1',
        'output_message_tooltip': 'Mostra un messaggio',

        // Key names
        'key_right': 'Freccia destra',
        'key_left': 'Freccia sinistra',
        'key_up': 'Freccia su',
        'key_down': 'Freccia giù',
        'key_space': 'Spazio',
        'key_enter': 'Invio',
        'key_escape': 'Esc',

        // Common terms
        'then': 'allora',
        'do': 'fai',
        'speed': 'velocità',
        'direction': 'direzione',
        'color': 'colore',
        'grid_size': 'dimensione griglia',
    }
};

/**
 * Get translated message for a block
 * @param {string} key Message key
 * @param {string} lang Language code (fr, de, it, en)
 * @returns {string} Translated message or key if not found
 */
function getBlockMessage(key, lang) {
    if (lang === 'en' || !BLOCK_MESSAGES[lang]) {
        return null; // Use default English
    }
    return BLOCK_MESSAGES[lang][key] || null;
}

// Keyboard key name translations
const KEY_NAMES = {
    'fr': {
        // Arrow keys
        'Right Arrow': 'Flèche droite',
        'Left Arrow': 'Flèche gauche',
        'Up Arrow': 'Flèche haut',
        'Down Arrow': 'Flèche bas',
        // Common keys
        'Space': 'Espace',
        'Enter': 'Entrée',
        'Escape': 'Échap',
        'Tab': 'Tab',
        'Backspace': 'Retour',
        'Delete': 'Suppr',
        // Modifier keys
        'Left Shift': 'Maj gauche',
        'Right Shift': 'Maj droite',
        'Left Ctrl': 'Ctrl gauche',
        'Right Ctrl': 'Ctrl droite',
        'Left Alt': 'Alt gauche',
        'Right Alt': 'Alt droite',
        // Navigation keys
        'Home': 'Début',
        'End': 'Fin',
        'Page Up': 'Page préc',
        'Page Down': 'Page suiv',
        'Insert': 'Insérer',
        // Numpad
        'Numpad 0': 'Pavé num 0',
        'Numpad 1': 'Pavé num 1',
        'Numpad 2': 'Pavé num 2',
        'Numpad 3': 'Pavé num 3',
        'Numpad 4': 'Pavé num 4',
        'Numpad 5': 'Pavé num 5',
        'Numpad 6': 'Pavé num 6',
        'Numpad 7': 'Pavé num 7',
        'Numpad 8': 'Pavé num 8',
        'Numpad 9': 'Pavé num 9',
        'Numpad +': 'Pavé num +',
        'Numpad -': 'Pavé num -',
        'Numpad *': 'Pavé num *',
        'Numpad /': 'Pavé num /',
        'Numpad Enter': 'Pavé num Entrée',
        'Numpad .': 'Pavé num .',
    },
    'de': {
        // Arrow keys
        'Right Arrow': 'Pfeil rechts',
        'Left Arrow': 'Pfeil links',
        'Up Arrow': 'Pfeil oben',
        'Down Arrow': 'Pfeil unten',
        // Common keys
        'Space': 'Leertaste',
        'Enter': 'Eingabe',
        'Escape': 'Escape',
        'Tab': 'Tab',
        'Backspace': 'Rücktaste',
        'Delete': 'Entf',
        // Modifier keys
        'Left Shift': 'Umschalt links',
        'Right Shift': 'Umschalt rechts',
        'Left Ctrl': 'Strg links',
        'Right Ctrl': 'Strg rechts',
        'Left Alt': 'Alt links',
        'Right Alt': 'Alt rechts',
        // Navigation keys
        'Home': 'Pos1',
        'End': 'Ende',
        'Page Up': 'Bild auf',
        'Page Down': 'Bild ab',
        'Insert': 'Einfg',
        // Numpad
        'Numpad 0': 'Num 0',
        'Numpad 1': 'Num 1',
        'Numpad 2': 'Num 2',
        'Numpad 3': 'Num 3',
        'Numpad 4': 'Num 4',
        'Numpad 5': 'Num 5',
        'Numpad 6': 'Num 6',
        'Numpad 7': 'Num 7',
        'Numpad 8': 'Num 8',
        'Numpad 9': 'Num 9',
        'Numpad +': 'Num +',
        'Numpad -': 'Num -',
        'Numpad *': 'Num *',
        'Numpad /': 'Num /',
        'Numpad Enter': 'Num Eingabe',
        'Numpad .': 'Num ,',
    },
    'it': {
        // Arrow keys
        'Right Arrow': 'Freccia destra',
        'Left Arrow': 'Freccia sinistra',
        'Up Arrow': 'Freccia su',
        'Down Arrow': 'Freccia giù',
        // Common keys
        'Space': 'Spazio',
        'Enter': 'Invio',
        'Escape': 'Esc',
        'Tab': 'Tab',
        'Backspace': 'Backspace',
        'Delete': 'Canc',
        // Modifier keys
        'Left Shift': 'Maiusc sinistro',
        'Right Shift': 'Maiusc destro',
        'Left Ctrl': 'Ctrl sinistro',
        'Right Ctrl': 'Ctrl destro',
        'Left Alt': 'Alt sinistro',
        'Right Alt': 'Alt destro',
        // Navigation keys
        'Home': 'Home',
        'End': 'Fine',
        'Page Up': 'Pag su',
        'Page Down': 'Pag giù',
        'Insert': 'Ins',
        // Numpad
        'Numpad 0': 'Num 0',
        'Numpad 1': 'Num 1',
        'Numpad 2': 'Num 2',
        'Numpad 3': 'Num 3',
        'Numpad 4': 'Num 4',
        'Numpad 5': 'Num 5',
        'Numpad 6': 'Num 6',
        'Numpad 7': 'Num 7',
        'Numpad 8': 'Num 8',
        'Numpad 9': 'Num 9',
        'Numpad +': 'Num +',
        'Numpad -': 'Num -',
        'Numpad *': 'Num *',
        'Numpad /': 'Num /',
        'Numpad Enter': 'Num Invio',
        'Numpad .': 'Num .',
    }
};

/**
 * Get translated key name
 * @param {string} key Key name in English
 * @param {string} lang Language code (fr, de, it, en)
 * @returns {string} Translated key name or original if not found
 */
function getKeyName(key, lang) {
    if (lang === 'en' || !KEY_NAMES[lang]) {
        return key; // Use default English
    }
    return KEY_NAMES[lang][key] || key;
}

/**
 * Set Blockly language
 * @param {string} lang Language code
 */
function setBlocklyLanguage(lang) {
    window.BLOCKLY_LANG = lang || 'en';
    console.log('Blockly language set to:', window.BLOCKLY_LANG);
}

// Category name translations
const CATEGORY_MESSAGES = {
    'fr': {
        'Events': 'Événements',
        'Movement': 'Mouvement',
        'Timing': 'Minuterie',
        'Drawing': 'Dessin',
        'Score/Lives/Health': 'Score/Vies/Santé',
        'Instance': 'Instance',
        'Room': 'Niveau',
        'Values': 'Valeurs',
        'Sound': 'Son',
        'Output': 'Sortie',
        'Math': 'Maths',
        'Logic': 'Logique'
    },
    'de': {
        'Events': 'Ereignisse',
        'Movement': 'Bewegung',
        'Timing': 'Zeitsteuerung',
        'Drawing': 'Zeichnen',
        'Score/Lives/Health': 'Punkte/Leben/Gesundheit',
        'Instance': 'Instanz',
        'Room': 'Raum',
        'Values': 'Werte',
        'Sound': 'Klang',
        'Output': 'Ausgabe',
        'Math': 'Mathematik',
        'Logic': 'Logik'
    },
    'it': {
        'Events': 'Eventi',
        'Movement': 'Movimento',
        'Timing': 'Temporizzazione',
        'Drawing': 'Disegno',
        'Score/Lives/Health': 'Punteggio/Vite/Salute',
        'Instance': 'Istanza',
        'Room': 'Stanza',
        'Values': 'Valori',
        'Sound': 'Suono',
        'Output': 'Uscita',
        'Math': 'Matematica',
        'Logic': 'Logica'
    },
    'uk': {
        'Events': 'Події',
        'Movement': 'Рух',
        'Timing': 'Таймінг',
        'Drawing': 'Малювання',
        'Score/Lives/Health': 'Рахунок/Життя/Здоров\'я',
        'Instance': 'Екземпляр',
        'Room': 'Кімната',
        'Values': 'Значення',
        'Sound': 'Звук',
        'Output': 'Вивід',
        'Math': 'Математика',
        'Logic': 'Логіка'
    }
};

/**
 * Get translated category name
 * @param {string} category Category name
 * @param {string} lang Language code (fr, de, it, en)
 * @returns {string} Translated category name or original if not found
 */
function getCategoryMessage(category, lang) {
    if (lang === 'en' || !CATEGORY_MESSAGES[lang]) {
        return category; // Use default English
    }
    return CATEGORY_MESSAGES[lang][category] || category;
}

// Initialize language from URL query parameter, or use English by default
(function() {
    var urlParams = new URLSearchParams(window.location.search);
    var langParam = urlParams.get('lang');
    var supportedLangs = ['fr', 'de', 'it', 'uk', 'es', 'pt', 'ru', 'zh', 'ja'];
    if (langParam && supportedLangs.indexOf(langParam) !== -1) {
        window.BLOCKLY_LANG = langParam;
        console.log('Blockly language set from URL:', window.BLOCKLY_LANG);
    } else if (typeof window.BLOCKLY_LANG === 'undefined') {
        window.BLOCKLY_LANG = 'en';
        console.log('Blockly language defaulting to English');
    }
})();

/**
 * Blockly built-in block translations
 * These override Blockly.Msg for Math, Logic, and Text blocks
 */
const BLOCKLY_MSG_TRANSLATIONS = {
    'fr': {
        // Math blocks
        "MATH_NUMBER_TOOLTIP": "Un nombre.",
        "MATH_ARITHMETIC_TOOLTIP_ADD": "Renvoie la somme des deux nombres.",
        "MATH_ARITHMETIC_TOOLTIP_MINUS": "Renvoie la différence des deux nombres.",
        "MATH_ARITHMETIC_TOOLTIP_MULTIPLY": "Renvoie le produit des deux nombres.",
        "MATH_ARITHMETIC_TOOLTIP_DIVIDE": "Renvoie le quotient des deux nombres.",
        "MATH_ARITHMETIC_TOOLTIP_POWER": "Renvoie le premier nombre élevé à la puissance du second.",
        "MATH_SINGLE_OP_ROOT": "racine carrée",
        "MATH_SINGLE_OP_ABSOLUTE": "valeur absolue",
        "MATH_SINGLE_TOOLTIP_ROOT": "Renvoie la racine carrée d'un nombre.",
        "MATH_SINGLE_TOOLTIP_ABS": "Renvoie la valeur absolue d'un nombre.",
        "MATH_SINGLE_TOOLTIP_NEG": "Renvoie l'opposé d'un nombre.",
        "MATH_SINGLE_TOOLTIP_LN": "Renvoie le logarithme naturel d'un nombre.",
        "MATH_SINGLE_TOOLTIP_LOG10": "Renvoie le logarithme base 10 d'un nombre.",
        "MATH_SINGLE_TOOLTIP_EXP": "Renvoie e élevé à la puissance d'un nombre.",
        "MATH_SINGLE_TOOLTIP_POW10": "Renvoie 10 élevé à la puissance d'un nombre.",
        "MATH_RANDOM_INT_TITLE": "entier aléatoire de %1 à %2",
        "MATH_RANDOM_INT_TOOLTIP": "Renvoie un entier aléatoire entre les deux limites spécifiées, incluses.",
        "MATH_RANDOM_FLOAT_TITLE_RANDOM": "fraction aléatoire",
        "MATH_RANDOM_FLOAT_TOOLTIP": "Renvoie une fraction aléatoire entre 0.0 (inclus) et 1.0 (exclus).",
        "MATH_ROUND_OPERATOR_ROUND": "arrondir",
        "MATH_ROUND_OPERATOR_ROUNDUP": "arrondir au supérieur",
        "MATH_ROUND_OPERATOR_ROUNDDOWN": "arrondir à l'inférieur",
        "MATH_ROUND_TOOLTIP": "Arrondir un nombre au supérieur ou à l'inférieur.",
        "MATH_MODULO_TITLE": "reste de %1 ÷ %2",
        "MATH_MODULO_TOOLTIP": "Renvoie le reste de la division des deux nombres.",
        "MATH_CONSTRAIN_TITLE": "contraindre %1 entre %2 et %3",
        "MATH_CONSTRAIN_TOOLTIP": "Contraindre un nombre à être entre les limites spécifiées (incluses).",
        "MATH_IS_EVEN": "est pair",
        "MATH_IS_ODD": "est impair",
        "MATH_IS_PRIME": "est premier",
        "MATH_IS_WHOLE": "est entier",
        "MATH_IS_POSITIVE": "est positif",
        "MATH_IS_NEGATIVE": "est négatif",
        "MATH_IS_DIVISIBLE_BY": "est divisible par",
        "MATH_IS_TOOLTIP": "Vérifie si un nombre est pair, impair, premier, entier, positif, négatif, ou s'il est divisible par un nombre. Renvoie vrai ou faux.",
        "MATH_CHANGE_TITLE": "incrémenter %1 de %2",
        "MATH_CHANGE_TOOLTIP": "Ajouter un nombre à la variable « %1 ».",

        // Logic blocks
        "LOGIC_COMPARE_TOOLTIP_EQ": "Renvoie vrai si les deux entrées sont égales.",
        "LOGIC_COMPARE_TOOLTIP_NEQ": "Renvoie vrai si les deux entrées ne sont pas égales.",
        "LOGIC_COMPARE_TOOLTIP_LT": "Renvoie vrai si la première entrée est plus petite que la seconde.",
        "LOGIC_COMPARE_TOOLTIP_LTE": "Renvoie vrai si la première entrée est plus petite ou égale à la seconde.",
        "LOGIC_COMPARE_TOOLTIP_GT": "Renvoie vrai si la première entrée est plus grande que la seconde.",
        "LOGIC_COMPARE_TOOLTIP_GTE": "Renvoie vrai si la première entrée est plus grande ou égale à la seconde.",
        "LOGIC_OPERATION_AND": "et",
        "LOGIC_OPERATION_OR": "ou",
        "LOGIC_OPERATION_TOOLTIP_AND": "Renvoie vrai si les deux entrées sont vraies.",
        "LOGIC_OPERATION_TOOLTIP_OR": "Renvoie vrai si au moins une des entrées est vraie.",
        "LOGIC_NEGATE_TITLE": "non %1",
        "LOGIC_NEGATE_TOOLTIP": "Renvoie vrai si l'entrée est fausse. Renvoie faux si l'entrée est vraie.",
        "LOGIC_BOOLEAN_TRUE": "vrai",
        "LOGIC_BOOLEAN_FALSE": "faux",
        "LOGIC_BOOLEAN_TOOLTIP": "Renvoie soit vrai soit faux.",
        "LOGIC_NULL": "nul",
        "LOGIC_NULL_TOOLTIP": "Renvoie nul.",
        "LOGIC_TERNARY_CONDITION": "test",
        "LOGIC_TERNARY_IF_TRUE": "si vrai",
        "LOGIC_TERNARY_IF_FALSE": "si faux",
        "LOGIC_TERNARY_TOOLTIP": "Vérifie la condition dans « test ». Si la condition est vraie, renvoie la valeur « si vrai » ; sinon renvoie la valeur « si faux ».",
        "CONTROLS_IF_MSG_IF": "si",
        "CONTROLS_IF_MSG_ELSEIF": "sinon si",
        "CONTROLS_IF_MSG_ELSE": "sinon",
        "CONTROLS_IF_TOOLTIP_1": "Si une valeur est vraie, alors exécuter des instructions.",
        "CONTROLS_IF_TOOLTIP_2": "Si une valeur est vraie, alors exécuter le premier bloc d'instructions. Sinon, exécuter le second bloc d'instructions.",

        // Text blocks
        "TEXT_TEXT_TOOLTIP": "Une lettre, un mot ou une ligne de texte.",
        "TEXT_JOIN_TITLE_CREATEWITH": "créer texte avec",
        "TEXT_JOIN_TOOLTIP": "Créer un texte en assemblant plusieurs éléments.",
        "TEXT_CREATE_JOIN_TITLE_JOIN": "joindre",
        "TEXT_CREATE_JOIN_TOOLTIP": "Ajouter, supprimer ou réorganiser les sections pour reconfigurer ce bloc de texte.",
        "TEXT_CREATE_JOIN_ITEM_TOOLTIP": "Ajouter un élément au texte.",
        "TEXT_APPEND_TITLE": "à %1 ajouter le texte %2",
        "TEXT_APPEND_TOOLTIP": "Ajouter du texte à la variable « %1 ».",
        "TEXT_LENGTH_TITLE": "longueur de %1",
        "TEXT_LENGTH_TOOLTIP": "Renvoie le nombre de lettres (espaces inclus) dans le texte fourni.",
        "TEXT_ISEMPTY_TITLE": "%1 est vide",
        "TEXT_ISEMPTY_TOOLTIP": "Renvoie vrai si le texte fourni est vide.",
        "TEXT_INDEXOF_TITLE": "dans le texte %1 %2 %3",
        "TEXT_INDEXOF_OPERATOR_FIRST": "trouver la première occurrence de",
        "TEXT_INDEXOF_OPERATOR_LAST": "trouver la dernière occurrence de",
        "TEXT_INDEXOF_TOOLTIP": "Renvoie la position de la première/dernière occurrence du premier texte dans le second. Renvoie %1 si le texte n'est pas trouvé.",

        // Common UI messages
        "ADD_COMMENT": "Ajouter un commentaire",
        "CLEAN_UP": "Nettoyer les blocs",
        "COLLAPSE_ALL": "Réduire les blocs",
        "COLLAPSE_BLOCK": "Réduire le bloc",
        "DELETE_ALL_BLOCKS": "Supprimer les %1 blocs ?",
        "DELETE_BLOCK": "Supprimer le bloc",
        "DELETE_X_BLOCKS": "Supprimer %1 blocs",
        "DISABLE_BLOCK": "Désactiver le bloc",
        "DUPLICATE_BLOCK": "Dupliquer",
        "ENABLE_BLOCK": "Activer le bloc",
        "EXPAND_ALL": "Développer les blocs",
        "EXPAND_BLOCK": "Développer le bloc",
        "EXTERNAL_INPUTS": "Entrées externes",
        "HELP": "Aide",
        "INLINE_INPUTS": "Entrées en ligne",
        "REDO": "Rétablir",
        "UNDO": "Annuler",
        "REMOVE_COMMENT": "Supprimer le commentaire"
    },
    'de': {
        // Math blocks
        "MATH_NUMBER_TOOLTIP": "Eine Zahl.",
        "MATH_SINGLE_OP_ROOT": "Quadratwurzel",
        "MATH_SINGLE_OP_ABSOLUTE": "Absolutwert",
        "MATH_RANDOM_INT_TITLE": "ganze Zufallszahl von %1 bis %2",
        "MATH_ROUND_OPERATOR_ROUND": "runden",
        "MATH_ROUND_OPERATOR_ROUNDUP": "aufrunden",
        "MATH_ROUND_OPERATOR_ROUNDDOWN": "abrunden",

        // Logic blocks
        "LOGIC_OPERATION_AND": "und",
        "LOGIC_OPERATION_OR": "oder",
        "LOGIC_NEGATE_TITLE": "nicht %1",
        "LOGIC_BOOLEAN_TRUE": "wahr",
        "LOGIC_BOOLEAN_FALSE": "falsch",
        "CONTROLS_IF_MSG_IF": "wenn",
        "CONTROLS_IF_MSG_ELSEIF": "sonst wenn",
        "CONTROLS_IF_MSG_ELSE": "sonst"
    },
    'it': {
        // Math blocks
        "MATH_NUMBER_TOOLTIP": "Un numero.",
        "MATH_SINGLE_OP_ROOT": "radice quadrata",
        "MATH_SINGLE_OP_ABSOLUTE": "valore assoluto",
        "MATH_RANDOM_INT_TITLE": "intero casuale da %1 a %2",
        "MATH_ROUND_OPERATOR_ROUND": "arrotonda",
        "MATH_ROUND_OPERATOR_ROUNDUP": "arrotonda per eccesso",
        "MATH_ROUND_OPERATOR_ROUNDDOWN": "arrotonda per difetto",

        // Logic blocks
        "LOGIC_OPERATION_AND": "e",
        "LOGIC_OPERATION_OR": "o",
        "LOGIC_NEGATE_TITLE": "non %1",
        "LOGIC_BOOLEAN_TRUE": "vero",
        "LOGIC_BOOLEAN_FALSE": "falso",
        "CONTROLS_IF_MSG_IF": "se",
        "CONTROLS_IF_MSG_ELSEIF": "altrimenti se",
        "CONTROLS_IF_MSG_ELSE": "altrimenti"
    },
    'uk': {
        // Math blocks
        "MATH_NUMBER_TOOLTIP": "Число.",
        "MATH_SINGLE_OP_ROOT": "квадратний корінь",
        "MATH_SINGLE_OP_ABSOLUTE": "абсолютне значення",
        "MATH_RANDOM_INT_TITLE": "випадкове ціле від %1 до %2",
        "MATH_ROUND_OPERATOR_ROUND": "округлити",
        "MATH_ROUND_OPERATOR_ROUNDUP": "округлити вгору",
        "MATH_ROUND_OPERATOR_ROUNDDOWN": "округлити вниз",
        "MATH_ARITHMETIC_TOOLTIP_ADD": "Повертає суму двох чисел.",
        "MATH_ARITHMETIC_TOOLTIP_MINUS": "Повертає різницю двох чисел.",
        "MATH_ARITHMETIC_TOOLTIP_MULTIPLY": "Повертає добуток двох чисел.",
        "MATH_ARITHMETIC_TOOLTIP_DIVIDE": "Повертає частку двох чисел.",

        // Logic blocks
        "LOGIC_OPERATION_AND": "і",
        "LOGIC_OPERATION_OR": "або",
        "LOGIC_NEGATE_TITLE": "не %1",
        "LOGIC_BOOLEAN_TRUE": "істина",
        "LOGIC_BOOLEAN_FALSE": "хибність",
        "LOGIC_OPERATION_TOOLTIP_AND": "Повертає істину, якщо обидва входи істинні.",
        "LOGIC_OPERATION_TOOLTIP_OR": "Повертає істину, якщо хоча б один з входів істинний.",
        "CONTROLS_IF_MSG_IF": "якщо",
        "CONTROLS_IF_MSG_ELSEIF": "інакше якщо",
        "CONTROLS_IF_MSG_ELSE": "інакше",

        // Common UI
        "DELETE_BLOCK": "Видалити блок",
        "DUPLICATE_BLOCK": "Дублювати",
        "ADD_COMMENT": "Додати коментар",
        "HELP": "Допомога"
    }
};

/**
 * Apply translations to Blockly.Msg for built-in blocks
 * Call this after Blockly is loaded but before workspace is created
 */
function applyBlocklyMsgTranslations(lang) {
    if (!lang || lang === 'en' || !BLOCKLY_MSG_TRANSLATIONS[lang]) {
        console.log('[Blockly i18n] Using default English for Blockly.Msg');
        return;
    }

    if (typeof Blockly === 'undefined' || !Blockly.Msg) {
        console.warn('[Blockly i18n] Blockly.Msg not available yet');
        return;
    }

    var translations = BLOCKLY_MSG_TRANSLATIONS[lang];
    var count = 0;
    for (var key in translations) {
        if (translations.hasOwnProperty(key)) {
            Blockly.Msg[key] = translations[key];
            count++;
        }
    }
    console.log('[Blockly i18n] Applied ' + count + ' translations to Blockly.Msg for language: ' + lang);
}

// Export for use in blockly_workspace.html
window.applyBlocklyMsgTranslations = applyBlocklyMsgTranslations;
