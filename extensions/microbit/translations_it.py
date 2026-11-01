#!/usr/bin/env python3
"""Italian text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as ``translations_de.py``. Identifiers a student types stay as they are.
Accented vowels are not optional.
"""

ACTIONS = {
    "microbit_show_image": (
        "Mostra un'immagine",
        "Mostrare un'immagine sui LED: un nome (HEART, HAPPY, SAD, YES, NO, "
        "ARROW_N, SKULL…) oppure cinque righe di cifre di luminosità come "
        "«09090:99999:99999:09990:00900». Le immagini vengono messe in coda."),
    "microbit_scroll_text": (
        "Scorri un testo",
        "Far scorrere un testo sul display a LED. Metti il testo tra virgolette "
        "(\"Ciao\"); altrimenti un trattino o un più viene letto come un calcolo. Le "
        "lettere accentate appaiono come ? come sulla scheda vera."),
    "microbit_show_number": (
        "Mostra un numero",
        "Mostrare un numero: una cifra resta ferma, un numero più lungo scorre"),
    "microbit_set_pixel": (
        "Accendi un LED",
        "Accendere subito un LED (x e y da 0 a 4, luminosità da 0 a 9)"),
    "microbit_clear_display": (
        "Cancella il display",
        "Spegnere tutti i LED e scartare ciò che era in attesa"),
    "microbit_set_brightness": (
        "Luminosità del display",
        "Luminosità generale dei LED, da 0 (spento) a 255 (massimo)"),
    "microbit_play_tone": (
        "Suona una nota",
        "Emettere un segnale acustico a una frequenza per un certo numero di "
        "millisecondi. I suoni vengono messi in coda."),
    "microbit_play_melody": (
        "Suona una melodia",
        "Suonare una melodia integrata (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, "
        "POWER_UP…) oppure note tue come «C4:4 E G C5:8 R:4» (nota, "
        "ottava, :durata; R è una pausa)."),
    "microbit_stop_sound": (
        "Ferma il suono",
        "Spegnere l'altoparlante e scartare i suoni in attesa"),
    "microbit_radio_set_group": (
        "Imposta il gruppo radio",
        "Scegliere il gruppo radio (da 0 a 255). Solo le micro:bit dello stesso "
        "gruppo si sentono; ogni scheda parte dal gruppo 0."),
    "microbit_radio_send": (
        "Invia un messaggio radio",
        "Inviare un numero o un testo alle altre micro:bit dello stesso gruppo (non a "
        "questa). Ricevono l'evento «Messaggio radio ricevuto», con il valore in "
        "radio_number e radio_string. Metti il testo tra virgolette; viene "
        "troncato a 32 caratteri."),
    "microbit_read_sensor": (
        "Leggi un sensore",
        "Leggere un sensore della micro:bit in una variabile di questo oggetto (o in "
        "una variabile globale se il nome inizia con «global.»)"),
    "microbit_if_button": (
        "Se il pulsante è premuto",
        "Vero finché il pulsante resta premuto (A+B = entrambi)"),
    "microbit_if_gesture": (
        "Se c'è un gesto",
        "Vero finché la scheda si trova in questo gesto o posizione"),
    "microbit_if_tilt": (
        "Se c'è inclinazione",
        "Confrontare un asse dell'accelerometro (milli-g, da -2048 a 2048) con un valore"),
    "microbit_if_pixel": (
        "Se la luminosità del LED",
        "Confrontare la luminosità di un LED (da 0 a 9) con un valore; per impostazione "
        "predefinita la domanda è «è acceso?»"),
}

PARAMS = {
    "Image": "Immagine",
    "Hold (ms)": "Durata (ms)",
    "Text": "Testo",
    "Delay per column (ms)": "Ritardo per colonna (ms)",
    "Number": "Numero",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "Luminosità (0-9)",
    "Brightness (0-255)": "Luminosità (0-255)",
    "Frequency (Hz)": "Frequenza (Hz)",
    "Duration (ms)": "Durata (ms)",
    "Melody": "Melodia",
    "Tempo (bpm)": "Tempo (bpm)",
    "Group (0-255)": "Gruppo (0-255)",
    "Message": "Messaggio",
    "Sensor": "Sensore",
    "Variable": "Variabile",
    "Button": "Pulsante",
    "Gesture": "Gesto",
    "Axis": "Asse",
    "Comparison": "Confronto",
    "Value": "Valore",
}

EVENTS = {
    "microbit_button_a": "Pulsante A premuto",
    "microbit_button_b": "Pulsante B premuto",
    "microbit_button_ab": "Pulsanti A+B premuti",
    "microbit_logo_touched": "Logo toccato",
    "microbit_pin_0": "Pin 0 toccato",
    "microbit_pin_1": "Pin 1 toccato",
    "microbit_pin_2": "Pin 2 toccato",
    "microbit_gesture_shake": "Scossa",
    "microbit_gesture_logo_up": "Logo in alto",
    "microbit_gesture_logo_down": "Logo in basso",
    "microbit_gesture_tilt_left": "Inclinata a sinistra",
    "microbit_gesture_tilt_right": "Inclinata a destra",
    "microbit_gesture_screen_up": "Schermo verso l'alto",
    "microbit_gesture_screen_down": "Schermo verso il basso",
    "microbit_gesture_free_fall": "Caduta libera",
    "microbit_gesture_2g": "Urto da 2g",
    "microbit_gesture_3g": "Urto da 3g",
    "microbit_gesture_6g": "Urto da 6g",
    "microbit_gesture_8g": "Urto da 8g",
    "microbit_loud_sound": "Suono forte",
    "microbit_quiet_sound": "Suono debole",
    "microbit_display_done": "Visualizzazione terminata",
    "microbit_radio_received": "Messaggio radio ricevuto",
    "microbit_sound_done": "Suono terminato",
}
