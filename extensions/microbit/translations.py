#!/usr/bin/env python3
"""French text for the micro:bit's auto-generated Blockly blocks (Stage S10).

The schemas in ``actions.py`` are English-first; the Blockly canvas draws each
action as a generated block whose label, tooltip and parameter labels come from
``config/blockly_generated_block_i18n.py``. ``PLUGIN_GENERATED_BLOCK_TRANSLATIONS``
(registered by ``events/plugin_loader``) adds these to those tables, so the
extension carries its own translations and core names nothing micro:bit.

French only for now, matching the generated-block table's own scope; any other
language falls back to the English schema text. Accents are not optional
(CLAUDE.md): this is for French-speaking students.
"""

_ACTIONS_FR = {
    "microbit_show_image": (
        "Afficher une image",
        "Afficher une image sur les LED : un nom (HEART, HAPPY, SAD, YES, NO, "
        "ARROW_N, SKULL…) ou cinq lignes de chiffres de luminosité comme "
        "« 09090:99999:99999:09990:00900 ». Les affichages se mettent en file d'attente."),
    "microbit_scroll_text": (
        "Faire défiler un texte",
        "Faire défiler un texte sur l'écran LED. Mettez le texte entre guillemets "
        "(\"Bonjour\") ; sinon un tiret ou un plus est lu comme un calcul. Les "
        "lettres accentuées s'affichent en ? comme sur la vraie carte."),
    "microbit_show_number": (
        "Afficher un nombre",
        "Afficher un nombre : un chiffre reste fixe, un nombre plus long défile"),
    "microbit_set_pixel": (
        "Allumer une LED",
        "Allumer une LED tout de suite (x et y de 0 à 4, luminosité de 0 à 9)"),
    "microbit_clear_display": (
        "Effacer l'écran",
        "Éteindre toutes les LED et abandonner ce qui était en attente"),
    "microbit_set_brightness": (
        "Luminosité de l'écran",
        "Luminosité générale des LED, de 0 (éteint) à 255 (maximum)"),
    "microbit_play_tone": (
        "Jouer une note",
        "Émettre un bip à une fréquence pendant un nombre de millisecondes. "
        "Les sons se mettent en file d'attente."),
    "microbit_play_melody": (
        "Jouer une mélodie",
        "Jouer une mélodie intégrée (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, "
        "POWER_UP…) ou vos propres notes comme « C4:4 E G C5:8 R:4 » (note, "
        "octave, :durée ; R est un silence)."),
    "microbit_stop_sound": (
        "Arrêter le son",
        "Couper le haut-parleur et abandonner les sons en attente"),
    "microbit_radio_set_group": (
        "Régler le groupe radio",
        "Choisir le groupe radio (0 à 255). Seules les micro:bit du même groupe "
        "s'entendent ; chaque carte démarre dans le groupe 0."),
    "microbit_radio_send": (
        "Envoyer un message radio",
        "Envoyer un nombre ou un texte aux autres micro:bit du même groupe (pas à "
        "celle-ci). Elles reçoivent l'événement « Message radio reçu », avec la "
        "valeur dans radio_number et radio_string. Mettez le texte entre "
        "guillemets ; il est coupé à 32 caractères."),
    "microbit_read_sensor": (
        "Lire un capteur",
        "Lire un capteur de la micro:bit dans une variable de cet objet (ou une "
        "variable globale si le nom commence par « global. »)"),
    "microbit_if_button": (
        "Si bouton pressé",
        "Vrai tant que le bouton est maintenu enfoncé (A+B = les deux)"),
    "microbit_if_gesture": (
        "Si geste",
        "Vrai tant que la carte est dans ce geste ou cette position"),
    "microbit_if_tilt": (
        "Si inclinaison",
        "Comparer un axe de l'accéléromètre (milli-g, de -2048 à 2048) à une valeur"),
    "microbit_if_pixel": (
        "Si luminosité de la LED",
        "Comparer la luminosité d'une LED (0 à 9) à une valeur ; par défaut, "
        "la question est « est-elle allumée ? »"),
}

# English parameter label -> French. Labels shared with core actions keep core's
# translation (the registration never overwrites an existing entry).
_PARAMS_FR = {
    "Image": "Image",
    "Hold (ms)": "Durée d'affichage (ms)",
    "Text": "Texte",
    "Delay per column (ms)": "Délai par colonne (ms)",
    "Number": "Nombre",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "Luminosité (0-9)",
    "Brightness (0-255)": "Luminosité (0-255)",
    "Frequency (Hz)": "Fréquence (Hz)",
    "Duration (ms)": "Durée (ms)",
    "Melody": "Mélodie",
    "Tempo (bpm)": "Tempo (bpm)",
    "Group (0-255)": "Groupe (0-255)",
    "Message": "Message",
    "Sensor": "Capteur",
    "Variable": "Variable",
    "Button": "Bouton",
    "Gesture": "Geste",
    "Axis": "Axe",
    "Comparison": "Comparaison",
    "Value": "Valeur",
}

_EVENTS_FR = {
    "microbit_button_a": "Bouton A pressé",
    "microbit_button_b": "Bouton B pressé",
    "microbit_button_ab": "Boutons A+B pressés",
    "microbit_logo_touched": "Logo touché",
    "microbit_pin_0": "Broche 0 touchée",
    "microbit_pin_1": "Broche 1 touchée",
    "microbit_pin_2": "Broche 2 touchée",
    "microbit_gesture_shake": "Secousse",
    "microbit_gesture_logo_up": "Logo en haut",
    "microbit_gesture_logo_down": "Logo en bas",
    "microbit_gesture_tilt_left": "Inclinée à gauche",
    "microbit_gesture_tilt_right": "Inclinée à droite",
    "microbit_gesture_screen_up": "Écran vers le haut",
    "microbit_gesture_screen_down": "Écran vers le bas",
    "microbit_gesture_free_fall": "Chute libre",
    "microbit_gesture_2g": "Choc de 2g",
    "microbit_gesture_3g": "Choc de 3g",
    "microbit_gesture_6g": "Choc de 6g",
    "microbit_gesture_8g": "Choc de 8g",
    "microbit_loud_sound": "Bruit fort",
    "microbit_quiet_sound": "Bruit faible",
    "microbit_display_done": "Affichage terminé",
    "microbit_radio_received": "Message radio reçu",
    "microbit_sound_done": "Son terminé",
}

from . import translations_de, translations_es, translations_it, translations_pt, translations_ru, translations_uk, translations_sl, translations_ja, translations_zh

# language -> (actions {name: (label, tooltip)}, params {english: translated}, events {name: label}).
# One module per further language (translations_<lang>.py, same three tables), added here.
_LANGUAGES = {
    "fr": (_ACTIONS_FR, _PARAMS_FR, _EVENTS_FR),
    "de": (translations_de.ACTIONS, translations_de.PARAMS, translations_de.EVENTS),
    "zh": (translations_zh.ACTIONS, translations_zh.PARAMS, translations_zh.EVENTS),
    "ja": (translations_ja.ACTIONS, translations_ja.PARAMS, translations_ja.EVENTS),
    "sl": (translations_sl.ACTIONS, translations_sl.PARAMS, translations_sl.EVENTS),
    "uk": (translations_uk.ACTIONS, translations_uk.PARAMS, translations_uk.EVENTS),
    "ru": (translations_ru.ACTIONS, translations_ru.PARAMS, translations_ru.EVENTS),
    "pt": (translations_pt.ACTIONS, translations_pt.PARAMS, translations_pt.EVENTS),
    "it": (translations_it.ACTIONS, translations_it.PARAMS, translations_it.EVENTS),
    "es": (translations_es.ACTIONS, translations_es.PARAMS, translations_es.EVENTS),
}

PLUGIN_GENERATED_BLOCK_TRANSLATIONS = {
    "events": {name: {lang: events[name] for lang, (_, _, events) in _LANGUAGES.items() if name in events}
               for name in _EVENTS_FR},
    "actions": {
        name: {lang: {"display_name": actions[name][0], "description": actions[name][1]}
               for lang, (actions, _, _) in _LANGUAGES.items() if name in actions}
        for name in _ACTIONS_FR
    },
    "params": {lang: dict(params) for lang, (_, params, _) in _LANGUAGES.items()},
}
