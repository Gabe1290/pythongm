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
        'event_keyboard_nokey': 'Quand aucune touche',
        'event_keyboard_nokey_tooltip': "S'exécute quand aucune touche n'est pressée",
        'event_keyboard_anykey': "Quand n'importe quelle touche",
        'event_keyboard_anykey_tooltip': "S'exécute quand une touche est pressée",
        'event_collision': 'Quand collision avec %1',
        'event_collision_tooltip': "Détecte la collision avec un objet",
        'event_alarm': 'Quand alarme %1',
        'event_alarm_tooltip': "S'exécute quand l'alarme se déclenche",
        'event_mouse_click': 'Quand clic souris',
        'event_mouse_click_tooltip': 'Détecte le clic de souris',

        // Movement blocks
        'move_set_hspeed': 'définir vitesse horizontale à %1',
        'move_set_hspeed_tooltip': 'Définir la vitesse horizontale (X)',
        'move_set_vspeed': 'définir vitesse verticale à %1',
        'move_set_vspeed_tooltip': 'Définir la vitesse verticale (Y)',
        'move_stop': 'arrêter le mouvement',
        'move_stop_tooltip': 'Arrête tous les mouvements',
        'move_direction': 'déplacer en direction %1 vitesse %2',
        'move_direction_tooltip': 'Déplacer dans une direction (4 directions)',
        'move_towards': 'déplacer vers x: %1 y: %2',
        'move_towards_tooltip': 'Déplacer vers un point',
        'move_snap_to_grid': 'aligner à la grille %1',
        'move_snap_to_grid_tooltip': 'Aligne la position à la grille',
        'move_jump_to': 'sauter à x: %1 y: %2',
        'move_jump_to_tooltip': 'Téléportation instantanée',
        'grid_stop_if_no_keys': 'si aucune touche arrêter (grille %1)',
        'grid_stop_if_no_keys_tooltip': 'Arrête le mouvement sur grille si aucune touche',
        'grid_check_keys_and_move': 'vérifier touches et déplacer (grille %1 vitesse %2)',
        'grid_check_keys_and_move_tooltip': 'Vérifie les touches et déplace sur grille',
        'grid_if_on_grid': 'si sur grille %1',
        'grid_if_on_grid_tooltip': 'Exécute si aligné sur la grille',
        'set_gravity': 'définir gravité à %1',
        'set_gravity_tooltip': 'Applique une force de gravité',
        'set_friction': 'définir friction à %1',
        'set_friction_tooltip': 'Applique de la friction',
        'reverse_horizontal': 'inverser horizontal',
        'reverse_horizontal_tooltip': 'Inverse la direction horizontale',
        'reverse_vertical': 'inverser vertical',
        'reverse_vertical_tooltip': 'Inverse la direction verticale',

        // Timing blocks
        'set_alarm': 'définir alarme %1 à %2',
        'set_alarm_tooltip': 'Définit une alarme (0-11)',

        // Drawing blocks
        'draw_text': 'dessiner texte %1 à x: %2 y: %3',
        'draw_text_tooltip': 'Affiche du texte',
        'draw_rectangle': 'dessiner rectangle x: %1 y: %2 largeur: %3 hauteur: %4 couleur: %5',
        'draw_rectangle_tooltip': 'Dessine un rectangle plein',
        'draw_circle': 'dessiner cercle x: %1 y: %2 rayon: %3 couleur: %4',
        'draw_circle_tooltip': 'Dessine un cercle plein',
        'set_sprite': 'définir sprite à %1',
        'set_sprite_tooltip': "Change l'image du sprite",
        'set_alpha': 'définir transparence à %1',
        'set_alpha_tooltip': 'Définit la transparence (0-1)',

        // Score/Lives/Health blocks
        'score_set': 'définir score à %1',
        'score_set_tooltip': 'Définit la valeur du score',
        'score_add': 'ajouter %1 au score',
        'score_add_tooltip': 'Change le score',
        'lives_set': 'définir vies à %1',
        'lives_set_tooltip': 'Définit le nombre de vies',
        'lives_add': 'ajouter %1 aux vies',
        'lives_add_tooltip': 'Change les vies',
        'health_set': 'définir santé à %1',
        'health_set_tooltip': 'Définit la valeur de santé',
        'health_add': 'ajouter %1 à la santé',
        'health_add_tooltip': 'Change la santé',
        'draw_score': 'afficher score à x: %1 y: %2',
        'draw_score_tooltip': 'Affiche le texte du score',
        'draw_lives': 'afficher vies à x: %1 y: %2 sprite: %3',
        'draw_lives_tooltip': 'Affiche les icônes des vies',
        'draw_health_bar': 'afficher barre de santé x: %1 y: %2 largeur: %3 hauteur: %4',
        'draw_health_bar_tooltip': 'Affiche une barre de santé',

        // Instance blocks
        'instance_destroy': 'détruire cette instance',
        'instance_destroy_tooltip': 'Détruit cet objet',
        'instance_destroy_other': 'détruire autre',
        'instance_destroy_other_tooltip': "Détruit l'objet en collision",
        'instance_create': 'créer instance de %1 à x: %2 y: %3',
        'instance_create_tooltip': 'Crée un nouvel objet',

        // Room blocks
        'room_goto_next': 'aller à la salle suivante',
        'room_goto_next_tooltip': 'Va à la salle suivante',
        'room_restart': 'redémarrer la salle',
        'room_restart_tooltip': 'Redémarre la salle actuelle',
        'room_goto': 'aller à la salle %1',
        'room_goto_tooltip': 'Va à une salle spécifique',

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
        'sound_play': 'jouer son %1',
        'sound_play_tooltip': 'Joue un effet sonore',
        'music_play': 'jouer musique %1',
        'music_play_tooltip': 'Joue une musique de fond',
        'music_stop': 'arrêter musique',
        'music_stop_tooltip': 'Arrête la musique',

        // Output blocks
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

        // Movement blocks
        'move_set_hspeed': 'setze horizontale Geschwindigkeit auf %1',
        'move_set_hspeed_tooltip': 'Setzt die horizontale Geschwindigkeit (X)',
        'move_set_vspeed': 'setze vertikale Geschwindigkeit auf %1',
        'move_set_vspeed_tooltip': 'Setzt die vertikale Geschwindigkeit (Y)',
        'move_stop': 'Bewegung stoppen',
        'move_stop_tooltip': 'Stoppt alle Bewegung',

        // Key names
        'key_right': 'Pfeil rechts',
        'key_left': 'Pfeil links',
        'key_up': 'Pfeil oben',
        'key_down': 'Pfeil unten',
        'key_space': 'Leertaste',
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

        // Movement blocks
        'move_set_hspeed': 'imposta velocità orizzontale a %1',
        'move_set_hspeed_tooltip': 'Imposta la velocità orizzontale (X)',
        'move_set_vspeed': 'imposta velocità verticale a %1',
        'move_set_vspeed_tooltip': 'Imposta la velocità verticale (Y)',
        'move_stop': 'ferma movimento',
        'move_stop_tooltip': 'Ferma tutti i movimenti',

        // Key names
        'key_right': 'Freccia destra',
        'key_left': 'Freccia sinistra',
        'key_up': 'Freccia su',
        'key_down': 'Freccia giù',
        'key_space': 'Spazio',
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
        'Room': 'Salle',
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

// Initialize with English by default
if (typeof window.BLOCKLY_LANG === 'undefined') {
    window.BLOCKLY_LANG = 'en';
}
