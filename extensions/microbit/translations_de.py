#!/usr/bin/env python3
"""German text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as the French tables in ``translations.py``: block label + tooltip per
action, the parameter labels, and the drop-down labels of its events. Identifiers a
student types (image names, ``radio_number``, ``global.``) stay as they are. Umlauts
and ß are not optional.
"""

ACTIONS = {
    "microbit_show_image": (
        "Bild anzeigen",
        "Ein Bild auf den LEDs anzeigen: ein Name (HEART, HAPPY, SAD, YES, NO, "
        "ARROW_N, SKULL…) oder fünf Zeilen mit Helligkeitsziffern wie "
        "„09090:99999:99999:09990:00900“. Anzeigen werden in eine Warteschlange gestellt."),
    "microbit_scroll_text": (
        "Text scrollen",
        "Einen Text über das LED-Display scrollen lassen. Setze den Text in "
        "Anführungszeichen (\"Hallo\"); sonst wird ein Minus oder Plus als Rechnung "
        "gelesen. Umlaute und Akzente erscheinen als ?, wie auf dem echten Board."),
    "microbit_show_number": (
        "Zahl anzeigen",
        "Eine Zahl anzeigen: eine Ziffer bleibt stehen, eine längere Zahl scrollt"),
    "microbit_set_pixel": (
        "LED einschalten",
        "Eine LED sofort einschalten (x und y von 0 bis 4, Helligkeit von 0 bis 9)"),
    "microbit_clear_display": (
        "Display löschen",
        "Alle LEDs ausschalten und alles Wartende verwerfen"),
    "microbit_set_brightness": (
        "Display-Helligkeit",
        "Gesamthelligkeit der LEDs, von 0 (aus) bis 255 (maximal)"),
    "microbit_play_tone": (
        "Ton spielen",
        "Einen Piepton mit einer Frequenz für eine Anzahl Millisekunden ausgeben. "
        "Töne werden in eine Warteschlange gestellt."),
    "microbit_play_melody": (
        "Melodie spielen",
        "Eine eingebaute Melodie spielen (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, "
        "POWER_UP…) oder eigene Noten wie „C4:4 E G C5:8 R:4“ (Note, Oktave, "
        ":Dauer; R ist eine Pause)."),
    "microbit_stop_sound": (
        "Ton stoppen",
        "Den Lautsprecher abschalten und wartende Töne verwerfen"),
    "microbit_radio_set_group": (
        "Funkgruppe festlegen",
        "Die Funkgruppe wählen (0 bis 255). Nur micro:bits in derselben Gruppe "
        "hören sich; jedes Board startet in Gruppe 0."),
    "microbit_radio_send": (
        "Funknachricht senden",
        "Eine Zahl oder einen Text an die anderen micro:bits derselben Gruppe senden "
        "(nicht an dieses). Sie erhalten das Ereignis „Funknachricht empfangen“, mit "
        "dem Wert in radio_number und radio_string. Setze den Text in "
        "Anführungszeichen; er wird auf 32 Zeichen gekürzt."),
    "microbit_read_sensor": (
        "Sensor lesen",
        "Einen Sensor des micro:bit in eine Variable dieses Objekts lesen (oder in "
        "eine globale Variable, wenn der Name mit „global.“ beginnt)"),
    "microbit_if_button": (
        "Wenn Taste gedrückt",
        "Wahr, solange die Taste gedrückt gehalten wird (A+B = beide)"),
    "microbit_if_gesture": (
        "Wenn Geste",
        "Wahr, solange sich das Board in dieser Geste oder Lage befindet"),
    "microbit_if_tilt": (
        "Wenn Neigung",
        "Eine Achse des Beschleunigungssensors (Milli-g, von -2048 bis 2048) mit einem Wert vergleichen"),
    "microbit_if_pixel": (
        "Wenn LED-Helligkeit",
        "Die Helligkeit einer LED (0 bis 9) mit einem Wert vergleichen; standardmäßig "
        "lautet die Frage „leuchtet sie?“"),
}

PARAMS = {
    "Image": "Bild",
    "Hold (ms)": "Anzeigedauer (ms)",
    "Text": "Text",
    "Delay per column (ms)": "Verzögerung pro Spalte (ms)",
    "Number": "Zahl",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "Helligkeit (0-9)",
    "Brightness (0-255)": "Helligkeit (0-255)",
    "Frequency (Hz)": "Frequenz (Hz)",
    "Duration (ms)": "Dauer (ms)",
    "Melody": "Melodie",
    "Tempo (bpm)": "Tempo (bpm)",
    "Group (0-255)": "Gruppe (0-255)",
    "Message": "Nachricht",
    "Sensor": "Sensor",
    "Variable": "Variable",
    "Button": "Taste",
    "Gesture": "Geste",
    "Axis": "Achse",
    "Comparison": "Vergleich",
    "Value": "Wert",
}

EVENTS = {
    "microbit_button_a": "Taste A gedrückt",
    "microbit_button_b": "Taste B gedrückt",
    "microbit_button_ab": "Tasten A+B gedrückt",
    "microbit_logo_touched": "Logo berührt",
    "microbit_pin_0": "Pin 0 berührt",
    "microbit_pin_1": "Pin 1 berührt",
    "microbit_pin_2": "Pin 2 berührt",
    "microbit_gesture_shake": "Schütteln",
    "microbit_gesture_logo_up": "Logo oben",
    "microbit_gesture_logo_down": "Logo unten",
    "microbit_gesture_tilt_left": "Nach links geneigt",
    "microbit_gesture_tilt_right": "Nach rechts geneigt",
    "microbit_gesture_screen_up": "Display nach oben",
    "microbit_gesture_screen_down": "Display nach unten",
    "microbit_gesture_free_fall": "Freier Fall",
    "microbit_gesture_2g": "Stoß mit 2g",
    "microbit_gesture_3g": "Stoß mit 3g",
    "microbit_gesture_6g": "Stoß mit 6g",
    "microbit_gesture_8g": "Stoß mit 8g",
    "microbit_loud_sound": "Lautes Geräusch",
    "microbit_quiet_sound": "Leises Geräusch",
    "microbit_display_done": "Anzeige beendet",
    "microbit_radio_received": "Funknachricht empfangen",
    "microbit_sound_done": "Ton beendet",
}
