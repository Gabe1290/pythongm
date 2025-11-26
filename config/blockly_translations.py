#!/usr/bin/env python3
"""
Blockly Block Translations
Translations for block categories, names, and descriptions
Based on Scratch and Blockly standard French translations
"""

# Category name translations
CATEGORY_TRANSLATIONS = {
    "fr": {
        "Events": "Événements",
        "Movement": "Mouvement",
        "Timing": "Minuterie",
        "Drawing": "Dessin",
        "Score/Lives/Health": "Score/Vies/Santé",
        "Instance": "Instance",
        "Room": "Salle",
        "Values": "Valeurs",
        "Sound": "Son",
        "Output": "Sortie",
    },
    "de": {
        "Events": "Ereignisse",
        "Movement": "Bewegung",
        "Timing": "Zeitsteuerung",
        "Drawing": "Zeichnen",
        "Score/Lives/Health": "Punkte/Leben/Gesundheit",
        "Instance": "Instanz",
        "Room": "Raum",
        "Values": "Werte",
        "Sound": "Klang",
        "Output": "Ausgabe",
    },
    "it": {
        "Events": "Eventi",
        "Movement": "Movimento",
        "Timing": "Temporizzazione",
        "Drawing": "Disegno",
        "Score/Lives/Health": "Punteggio/Vite/Salute",
        "Instance": "Istanza",
        "Room": "Stanza",
        "Values": "Valori",
        "Sound": "Suono",
        "Output": "Output",
    }
}

# Block name and description translations
# Format: "block_type": {"name": {...}, "description": {...}}
BLOCK_TRANSLATIONS = {
    # Events
    "event_create": {
        "name": {"fr": "Événement de création", "de": "Erstellen-Ereignis", "it": "Evento di creazione"},
        "description": {"fr": "Quand l'objet est créé", "de": "Wenn Objekt erstellt wird", "it": "Quando l'oggetto viene creato"}
    },
    "event_step": {
        "name": {"fr": "Événement étape", "de": "Schritt-Ereignis", "it": "Evento passo"},
        "description": {"fr": "Chaque image", "de": "Jeden Frame", "it": "Ogni frame"}
    },
    "event_draw": {
        "name": {"fr": "Événement de dessin", "de": "Zeichnen-Ereignis", "it": "Evento di disegno"},
        "description": {"fr": "Pendant la phase de dessin", "de": "Während der Zeichenphase", "it": "Durante la fase di disegno"}
    },
    "event_destroy": {
        "name": {"fr": "Événement de destruction", "de": "Zerstören-Ereignis", "it": "Evento di distruzione"},
        "description": {"fr": "Quand l'objet est détruit", "de": "Wenn Objekt zerstört wird", "it": "Quando l'oggetto viene distrutto"}
    },
    "event_keyboard_nokey": {
        "name": {"fr": "Aucune touche", "de": "Keine Taste", "it": "Nessun tasto"},
        "description": {"fr": "Aucune touche pressée", "de": "Keine Taste gedrückt", "it": "Nessun tasto premuto"}
    },
    "event_keyboard_anykey": {
        "name": {"fr": "N'importe quelle touche", "de": "Beliebige Taste", "it": "Qualsiasi tasto"},
        "description": {"fr": "N'importe quelle touche pressée", "de": "Beliebige Taste gedrückt", "it": "Qualsiasi tasto premuto"}
    },
    "event_keyboard_held": {
        "name": {"fr": "Clavier (maintenu)", "de": "Tastatur (gehalten)", "it": "Tastiera (tenuto)"},
        "description": {"fr": "Touche maintenue", "de": "Taste gedrückt halten", "it": "Tasto tenuto premuto"}
    },
    "event_keyboard_press": {
        "name": {"fr": "Touche pressée", "de": "Taste drücken", "it": "Tasto premuto"},
        "description": {"fr": "Touche pressée une fois", "de": "Taste einmal gedrückt", "it": "Tasto premuto una volta"}
    },
    "event_keyboard_release": {
        "name": {"fr": "Touche relâchée", "de": "Taste loslassen", "it": "Tasto rilasciato"},
        "description": {"fr": "Touche relâchée", "de": "Taste losgelassen", "it": "Tasto rilasciato"}
    },
    "event_mouse": {
        "name": {"fr": "Événements souris", "de": "Mausereignisse", "it": "Eventi mouse"},
        "description": {"fr": "Clics et mouvement de la souris", "de": "Mausklicks und Bewegung", "it": "Clic e movimento del mouse"}
    },
    "event_collision": {
        "name": {"fr": "Collision", "de": "Kollision", "it": "Collisione"},
        "description": {"fr": "Collision avec un objet", "de": "Kollision mit Objekt", "it": "Collisione con oggetto"}
    },
    "event_alarm": {
        "name": {"fr": "Événements alarme", "de": "Alarm-Ereignisse", "it": "Eventi allarme"},
        "description": {"fr": "Déclencheur d'alarme (0-11)", "de": "Alarm-Auslöser (0-11)", "it": "Trigger allarme (0-11)"}
    },

    # Movement
    "move_set_hspeed": {
        "name": {"fr": "Définir vitesse horizontale", "de": "Horizontale Geschwindigkeit setzen", "it": "Imposta velocità orizzontale"},
        "description": {"fr": "Définir la vélocité X", "de": "X-Geschwindigkeit setzen", "it": "Imposta velocità X"}
    },
    "move_set_vspeed": {
        "name": {"fr": "Définir vitesse verticale", "de": "Vertikale Geschwindigkeit setzen", "it": "Imposta velocità verticale"},
        "description": {"fr": "Définir la vélocité Y", "de": "Y-Geschwindigkeit setzen", "it": "Imposta velocità Y"}
    },
    "move_stop": {
        "name": {"fr": "Arrêter le mouvement", "de": "Bewegung stoppen", "it": "Ferma movimento"},
        "description": {"fr": "Arrêter tout mouvement", "de": "Alle Bewegung stoppen", "it": "Ferma tutti i movimenti"}
    },
    "move_direction": {
        "name": {"fr": "Déplacer direction", "de": "Richtung bewegen", "it": "Muovi direzione"},
        "description": {"fr": "Déplacer en 4 directions", "de": "In 4 Richtungen bewegen", "it": "Muovi in 4 direzioni"}
    },
    "move_towards": {
        "name": {"fr": "Déplacer vers", "de": "Bewegen zu", "it": "Muovi verso"},
        "description": {"fr": "Déplacer vers un point", "de": "Zu einem Punkt bewegen", "it": "Muovi verso un punto"}
    },
    "move_snap_to_grid": {
        "name": {"fr": "Aligner à la grille", "de": "An Raster ausrichten", "it": "Allinea alla griglia"},
        "description": {"fr": "Aligner à la grille", "de": "An Raster ausrichten", "it": "Allinea alla griglia"}
    },
    "move_jump_to": {
        "name": {"fr": "Sauter à la position", "de": "Zu Position springen", "it": "Salta alla posizione"},
        "description": {"fr": "Téléportation instantanée", "de": "Sofortiger Teleport", "it": "Teletrasporto istantaneo"}
    },
    "grid_stop_if_no_keys": {
        "name": {"fr": "Arrêter si aucune touche", "de": "Stoppen wenn keine Taste", "it": "Ferma se nessun tasto"},
        "description": {"fr": "Aide pour mouvement grille", "de": "Raster-Bewegungshilfe", "it": "Aiuto movimento griglia"}
    },
    "grid_check_keys_and_move": {
        "name": {"fr": "Vérifier touches et déplacer", "de": "Tasten prüfen und bewegen", "it": "Controlla tasti e muovi"},
        "description": {"fr": "Aide pour mouvement grille", "de": "Raster-Bewegungshilfe", "it": "Aiuto movimento griglia"}
    },
    "grid_if_on_grid": {
        "name": {"fr": "Si sur la grille", "de": "Wenn auf Raster", "it": "Se sulla griglia"},
        "description": {"fr": "Vérification alignement grille", "de": "Rasterausrichtungsprüfung", "it": "Controllo allineamento griglia"}
    },
    "set_gravity": {
        "name": {"fr": "Définir gravité", "de": "Schwerkraft setzen", "it": "Imposta gravità"},
        "description": {"fr": "Appliquer force de gravité", "de": "Schwerkraft anwenden", "it": "Applica forza di gravità"}
    },
    "set_friction": {
        "name": {"fr": "Définir friction", "de": "Reibung setzen", "it": "Imposta attrito"},
        "description": {"fr": "Appliquer friction", "de": "Reibung anwenden", "it": "Applica attrito"}
    },
    "reverse_horizontal": {
        "name": {"fr": "Inverser horizontal", "de": "Horizontal umkehren", "it": "Inverti orizzontale"},
        "description": {"fr": "Inverser direction X", "de": "X-Richtung umkehren", "it": "Inverti direzione X"}
    },
    "reverse_vertical": {
        "name": {"fr": "Inverser vertical", "de": "Vertikal umkehren", "it": "Inverti verticale"},
        "description": {"fr": "Inverser direction Y", "de": "Y-Richtung umkehren", "it": "Inverti direzione Y"}
    },

    # Timing
    "set_alarm": {
        "name": {"fr": "Définir alarme", "de": "Alarm setzen", "it": "Imposta allarme"},
        "description": {"fr": "Définir minuteur (0-11)", "de": "Timer setzen (0-11)", "it": "Imposta timer (0-11)"}
    },

    # Drawing
    "draw_text": {
        "name": {"fr": "Dessiner texte", "de": "Text zeichnen", "it": "Disegna testo"},
        "description": {"fr": "Afficher du texte", "de": "Text anzeigen", "it": "Visualizza testo"}
    },
    "draw_rectangle": {
        "name": {"fr": "Dessiner rectangle", "de": "Rechteck zeichnen", "it": "Disegna rettangolo"},
        "description": {"fr": "Dessiner rectangle plein", "de": "Gefülltes Rechteck zeichnen", "it": "Disegna rettangolo pieno"}
    },
    "draw_circle": {
        "name": {"fr": "Dessiner cercle", "de": "Kreis zeichnen", "it": "Disegna cerchio"},
        "description": {"fr": "Dessiner cercle plein", "de": "Gefüllten Kreis zeichnen", "it": "Disegna cerchio pieno"}
    },
    "set_sprite": {
        "name": {"fr": "Définir sprite", "de": "Sprite setzen", "it": "Imposta sprite"},
        "description": {"fr": "Changer l'image du sprite", "de": "Sprite-Bild ändern", "it": "Cambia immagine sprite"}
    },
    "set_alpha": {
        "name": {"fr": "Définir transparence", "de": "Transparenz setzen", "it": "Imposta trasparenza"},
        "description": {"fr": "Définir alpha (0-1)", "de": "Alpha setzen (0-1)", "it": "Imposta alpha (0-1)"}
    },

    # Score/Lives/Health
    "score_set": {
        "name": {"fr": "Définir score", "de": "Punkte setzen", "it": "Imposta punteggio"},
        "description": {"fr": "Définir valeur du score", "de": "Punktewert setzen", "it": "Imposta valore punteggio"}
    },
    "score_add": {
        "name": {"fr": "Ajouter au score", "de": "Punkte hinzufügen", "it": "Aggiungi al punteggio"},
        "description": {"fr": "Modifier le score", "de": "Punkte ändern", "it": "Modifica punteggio"}
    },
    "lives_set": {
        "name": {"fr": "Définir vies", "de": "Leben setzen", "it": "Imposta vite"},
        "description": {"fr": "Définir nombre de vies", "de": "Lebenanzahl setzen", "it": "Imposta numero di vite"}
    },
    "lives_add": {
        "name": {"fr": "Ajouter aux vies", "de": "Leben hinzufügen", "it": "Aggiungi alle vite"},
        "description": {"fr": "Modifier les vies", "de": "Leben ändern", "it": "Modifica vite"}
    },
    "health_set": {
        "name": {"fr": "Définir santé", "de": "Gesundheit setzen", "it": "Imposta salute"},
        "description": {"fr": "Définir valeur de santé", "de": "Gesundheitswert setzen", "it": "Imposta valore salute"}
    },
    "health_add": {
        "name": {"fr": "Ajouter à la santé", "de": "Gesundheit hinzufügen", "it": "Aggiungi alla salute"},
        "description": {"fr": "Modifier la santé", "de": "Gesundheit ändern", "it": "Modifica salute"}
    },
    "draw_score": {
        "name": {"fr": "Afficher score", "de": "Punkte anzeigen", "it": "Visualizza punteggio"},
        "description": {"fr": "Afficher texte du score", "de": "Punktetext anzeigen", "it": "Visualizza testo punteggio"}
    },
    "draw_lives": {
        "name": {"fr": "Afficher vies", "de": "Leben anzeigen", "it": "Visualizza vite"},
        "description": {"fr": "Afficher icônes des vies", "de": "Leben-Icons anzeigen", "it": "Visualizza icone vite"}
    },
    "draw_health_bar": {
        "name": {"fr": "Afficher barre de santé", "de": "Gesundheitsleiste anzeigen", "it": "Visualizza barra salute"},
        "description": {"fr": "Afficher barre de santé", "de": "Gesundheitsleiste anzeigen", "it": "Visualizza barra salute"}
    },

    # Instance
    "instance_destroy": {
        "name": {"fr": "Détruire instance", "de": "Instanz zerstören", "it": "Distruggi istanza"},
        "description": {"fr": "Détruire cet objet", "de": "Dieses Objekt zerstören", "it": "Distruggi questo oggetto"}
    },
    "instance_destroy_other": {
        "name": {"fr": "Détruire autre", "de": "Anderes zerstören", "it": "Distruggi altro"},
        "description": {"fr": "Détruire objet en collision", "de": "Kollidierendes Objekt zerstören", "it": "Distruggi oggetto in collisione"}
    },
    "instance_create": {
        "name": {"fr": "Créer instance", "de": "Instanz erstellen", "it": "Crea istanza"},
        "description": {"fr": "Créer nouvel objet", "de": "Neues Objekt erstellen", "it": "Crea nuovo oggetto"}
    },

    # Room
    "room_goto_next": {
        "name": {"fr": "Salle suivante", "de": "Nächster Raum", "it": "Stanza successiva"},
        "description": {"fr": "Aller à la salle suivante", "de": "Zum nächsten Raum gehen", "it": "Vai alla stanza successiva"}
    },
    "room_restart": {
        "name": {"fr": "Redémarrer salle", "de": "Raum neustarten", "it": "Riavvia stanza"},
        "description": {"fr": "Redémarrer la salle actuelle", "de": "Aktuellen Raum neustarten", "it": "Riavvia stanza corrente"}
    },
    "room_goto": {
        "name": {"fr": "Aller à la salle", "de": "Zu Raum gehen", "it": "Vai alla stanza"},
        "description": {"fr": "Aller à une salle spécifique", "de": "Zu bestimmtem Raum gehen", "it": "Vai a una stanza specifica"}
    },

    # Values
    "value_x": {
        "name": {"fr": "Position X", "de": "X-Position", "it": "Posizione X"},
        "description": {"fr": "Obtenir coordonnée X", "de": "X-Koordinate abrufen", "it": "Ottieni coordinata X"}
    },
    "value_y": {
        "name": {"fr": "Position Y", "de": "Y-Position", "it": "Posizione Y"},
        "description": {"fr": "Obtenir coordonnée Y", "de": "Y-Koordinate abrufen", "it": "Ottieni coordinata Y"}
    },
    "value_hspeed": {
        "name": {"fr": "Vitesse horizontale", "de": "Horizontale Geschwindigkeit", "it": "Velocità orizzontale"},
        "description": {"fr": "Obtenir vélocité X", "de": "X-Geschwindigkeit abrufen", "it": "Ottieni velocità X"}
    },
    "value_vspeed": {
        "name": {"fr": "Vitesse verticale", "de": "Vertikale Geschwindigkeit", "it": "Velocità verticale"},
        "description": {"fr": "Obtenir vélocité Y", "de": "Y-Geschwindigkeit abrufen", "it": "Ottieni velocità Y"}
    },
    "value_score": {
        "name": {"fr": "Score", "de": "Punkte", "it": "Punteggio"},
        "description": {"fr": "Obtenir valeur du score", "de": "Punktewert abrufen", "it": "Ottieni valore punteggio"}
    },
    "value_lives": {
        "name": {"fr": "Vies", "de": "Leben", "it": "Vite"},
        "description": {"fr": "Obtenir nombre de vies", "de": "Lebenanzahl abrufen", "it": "Ottieni numero di vite"}
    },
    "value_health": {
        "name": {"fr": "Santé", "de": "Gesundheit", "it": "Salute"},
        "description": {"fr": "Obtenir valeur de santé", "de": "Gesundheitswert abrufen", "it": "Ottieni valore salute"}
    },
    "value_mouse_x": {
        "name": {"fr": "Souris X", "de": "Maus X", "it": "Mouse X"},
        "description": {"fr": "Obtenir X de la souris", "de": "Maus-X abrufen", "it": "Ottieni X del mouse"}
    },
    "value_mouse_y": {
        "name": {"fr": "Souris Y", "de": "Maus Y", "it": "Mouse Y"},
        "description": {"fr": "Obtenir Y de la souris", "de": "Maus-Y abrufen", "it": "Ottieni Y del mouse"}
    },

    # Sound
    "sound_play": {
        "name": {"fr": "Jouer son", "de": "Sound abspielen", "it": "Riproduci suono"},
        "description": {"fr": "Jouer effet sonore", "de": "Soundeffekt abspielen", "it": "Riproduci effetto sonoro"}
    },
    "music_play": {
        "name": {"fr": "Jouer musique", "de": "Musik abspielen", "it": "Riproduci musica"},
        "description": {"fr": "Jouer musique de fond", "de": "Hintergrundmusik abspielen", "it": "Riproduci musica di sottofondo"}
    },
    "music_stop": {
        "name": {"fr": "Arrêter musique", "de": "Musik stoppen", "it": "Ferma musica"},
        "description": {"fr": "Arrêter la musique", "de": "Musik stoppen", "it": "Ferma musica"}
    },

    # Output
    "output_message": {
        "name": {"fr": "Afficher message", "de": "Nachricht anzeigen", "it": "Mostra messaggio"},
        "description": {"fr": "Afficher dialogue de message", "de": "Nachrichtendialog anzeigen", "it": "Visualizza dialogo messaggio"}
    },
}


def get_translated_category(category: str, language: str = "en") -> str:
    """Get translated category name"""
    if language == "en" or language not in CATEGORY_TRANSLATIONS:
        return category
    return CATEGORY_TRANSLATIONS[language].get(category, category)


def get_translated_block_name(block_type: str, language: str = "en") -> str:
    """Get translated block name"""
    if language == "en" or block_type not in BLOCK_TRANSLATIONS:
        return None
    return BLOCK_TRANSLATIONS[block_type]["name"].get(language)


def get_translated_block_description(block_type: str, language: str = "en") -> str:
    """Get translated block description"""
    if language == "en" or block_type not in BLOCK_TRANSLATIONS:
        return None
    return BLOCK_TRANSLATIONS[block_type]["description"].get(language)
