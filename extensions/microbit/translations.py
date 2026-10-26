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

PLUGIN_GENERATED_BLOCK_TRANSLATIONS = {
    "actions": {
        name: {"fr": {"display_name": label, "description": tooltip}}
        for name, (label, tooltip) in _ACTIONS_FR.items()
    },
    "params": {"fr": dict(_PARAMS_FR)},
}
